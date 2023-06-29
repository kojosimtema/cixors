import random, string
from flask_restx import Resource, Namespace, abort
from flask import request
from flask import current_app as app
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, set_access_cookies, unset_jwt_cookies
from flask_jwt_extended.exceptions import JWTExtendedException

from ..config.config import mail, limiter
from ..services.authServices import token_required
from ..models.user import User
from ..models.blocklist import Blocklist
from ..db import db
from ..namespaces import signup_model, login_model, user_model, change_password_model, user_activation_model


auth_namespace = Namespace('auth', description='Name space for authentication')


@auth_namespace.route('/signup')
class Signup(Resource):
    @auth_namespace.expect(signup_model)
    @auth_namespace.marshal_with(user_model)
    @auth_namespace.doc(description='Sign up or create a new user')
    def post(self):
        """
            Sign up a new user
        """
        data = request.get_json()
        username = data['username']
        email = data['email']
        characters = string.ascii_letters + string.digits
        verification_code = ''.join((random.choice(characters) for i in range(5)))

        if len(data['password']) > 5:
        
            if data['password'] == data['confirm_password']:
                new_user = User(
                    username = username.lower(),
                    email = email,
                    password = generate_password_hash(data.get('password')),
                    verification_code = verification_code
                )
                try:
                    new_user.save()
                except IntegrityError:
                    abort(HTTPStatus.BAD_REQUEST, message=f'Username {username} or email {email} already exit. Please try a different username and or email')
            else:
                abort(HTTPStatus.UNAUTHORIZED, message='Your passwords do not match')

            msg = Message(
                subject='Email Verification', 
                sender = 'desoftwareengineer@gmail.com', 
                recipients = [f'{email}']
            )
            msg.html = f"""
                        <div>
                            <p>Verify your email with the code below to activate your account</p>
                            <h1 style='color: darkcyan;'>{verification_code}</h1>
                        </div>
                        """
            mail.send(msg)
        else:
            abort(HTTPStatus.BAD_REQUEST, message=f'Your password should be more than 5 characters')
        
        return new_user, HTTPStatus.CREATED

@auth_namespace.route('/verify/<string:user_email>')
class VerifyUser(Resource):
    @auth_namespace.expect(user_activation_model)
    @auth_namespace.doc(
        description='Verify a new user',
        params = {
            'user_email': 'A user email'
        })
    def put(self, user_email):
        """
            New User Verification
        """
        user = User.query.filter_by(email=user_email).first()
        if user and user.is_verified is False:
            data = request.get_json()
            if data['verification_code'] == user.verification_code:
                user.is_verified = True
                user.date_verified = datetime.utcnow()
                db.session.commit()
                return {
                    'success': True,
                    'message': 'User successfully verified'
                }, HTTPStatus.OK
            else:
                return {
                    'success': False,
                    'message': 'Invalid verification code. Please try again'
                }, HTTPStatus.UNAUTHORIZED
        else:
            return{
                'success': False,
                'message': f'User with email {user_email} does not exit or is already verified'
            }, HTTPStatus.UNAUTHORIZED
        
    @auth_namespace.doc(
        description='Resend Verification code',
        params = {
            'user_email': 'A user email'
        })
    def get(self, user_email):
        """
            Resend Verification code to user
        """
        user = User.query.filter_by(email=user_email).first()
        if user and user.is_verified is False:
            characters = string.ascii_letters + string.digits
            verification_code = ''.join((random.choice(characters) for i in range(5)))

            user.verification_code = verification_code
            db.session.commit()

            msg = Message(
                subject='Email Verification', 
                sender = 'desoftwareengineer@gmail.com', 
                recipients = [f'{user_email}']
            )
            msg.html = f"""
                        <div>
                            <p>Verify your email with the code below to activate your account</p>
                            <h1 style='color: darkcyan;'>{verification_code}</h1>
                        </div>
                        """
            mail.send(msg)
            return {
                    'success': True,
                    'message': f'Please check your email "{user_email}" for new verification code'
                }, HTTPStatus.OK
        else:
            return{
                'success': False,
                'message': f'User with email "{user_email}" does not exit or is already verified'
            }, HTTPStatus.UNAUTHORIZED

        
       
@auth_namespace.route('/login')
class Login(Resource):
    @auth_namespace.expect(login_model)
    @auth_namespace.doc(description='Login a user to generate a JWT Access Token')
    def post(self):
        """
            Generate JWT for user
        """
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.is_verified and check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            response = {
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'access_token': access_token,
                'refresh_token': refresh_token
            }           
            return response, HTTPStatus.CREATED
        else:
            return {
                'success': False,
                'message': 'Your credentials do not match'
            }, HTTPStatus.UNAUTHORIZED
    
@auth_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    @auth_namespace.doc(description='Refresh a JWT Access Token')
    @token_required
    def get(self):
        """
            Refresh JWT Access Token
        """
        user = get_jwt_identity()
        access_token = create_access_token(identity=user)
        return {
            'access_token': access_token
        }, HTTPStatus.CREATED

@auth_namespace.route('/change_password')
class ChangePassword(Resource):
    @auth_namespace.expect(change_password_model)
    @auth_namespace.doc(description='Change user password. JWT is required to perform this action')
    @limiter.limit('2/day')
    @jwt_required()
    @token_required
    def put(self):
        """
            Change user password
        """
        user_id = get_jwt_identity()
        data = request.get_json()
        user = User.get_by_id(user_id)
        
        if user and check_password_hash(user.password, data['old_password']):
            if data['new_password'] == data['confirm_password']:
                user.password = generate_password_hash(data['new_password'])
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Password successfuly changed'
                }, HTTPStatus.OK
            else:
                return {
                    'success': False,
                    'message': 'your new passwords do not match'
                }, HTTPStatus.UNAUTHORIZED
        else:
            return {
                'success': False,
                'message': 'your old password is incorrect'
            }, HTTPStatus.UNAUTHORIZED
        
@auth_namespace.route('/logout')
class Logout(Resource):
    @auth_namespace.doc(description='Logout a user and block JWT')
    @jwt_required()
    @token_required
    def post(self):
        """
            Logout a user
        """
        jti = get_jwt()['jti']
        blocked = Blocklist(jti=jti)
        blocked.add_to_blocklist()
        return{
            'success': True,
            'message': 'You have successfully logged out'
        }, HTTPStatus.OK
    

@auth_namespace.route('/checkvalidtoken')
class CheckTokenValidity(Resource):
    @auth_namespace.doc(description='Check is a JWT is valid, blocked or expired')
    @jwt_required()
    @token_required
    def get(self):
        """
        Check validity of JWT
        """
        try:
            user_id = get_jwt_identity()
            jti = get_jwt()['jti']
            blockedJti = Blocklist.query.filter_by(jti=jti).first()
            if blockedJti:
                return {
                    'valid_token': False,
                    'message': 'Token is blocked. Please signin again'
                }, HTTPStatus.UNAUTHORIZED
        except Exception:
            blocked = Blocklist(jti=jti)
            blocked.add_to_blocklist()
            return {
                'valid_token': False,
                'message': 'Token has been has expired or is invalid. Please signin again'
            }, HTTPStatus.UNAUTHORIZED
        return {
            'valid_token': True,
            'message': 'Token is valid and active'
        }, HTTPStatus.OK



@auth_namespace.route('/resetpassword/<string:email>')
class ResetUserPassword(Resource):
    @auth_namespace.doc(
            description='Reset a User password',
            params={
                'email': 'User email'
            })
    def put(self, email):
        """
            Reset User password
        """
        user = User.query.filter_by(email=email).first()
        characters = string.ascii_letters + string.digits
        temporal_pass = ''.join((random.choice(characters) for i in range(8)))
          
        if user:
            user.password = generate_password_hash(temporal_pass)
            db.session.commit()
        else:
            return {
                'success': False,
                'message': 'User not found'
            }, HTTPStatus.UNAUTHORIZED
        # mail = Mail(app)
        msg = Message(
                subject='Password Reset', 
                sender = 'desoftwareengineer@gmail.com', 
                recipients = [f'{email}']
            )
        msg.html = f"""
                    <div>
                        <p>This is a reset password. Change it after loging in</p>
                        <h2 style='color: darkcyan;'>{temporal_pass}</h2>
                    </div>
                    """
        mail.send(msg)
        return {
                'success': True,
                'message': 'Your password has been reset. Check your email for new password'
        }, HTTPStatus.OK
