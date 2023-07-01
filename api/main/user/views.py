from flask_restx import Resource, Namespace, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus

from ..models.user import User
from ..config.config import cache
from ..db import db
from ..services.authServices import token_required
from ..namespaces import user_model, basic_user_model

user_namespace = Namespace('users', description='name space for users')

@user_namespace.route('/')
class GetUsers(Resource):
    @user_namespace.marshal_with(basic_user_model)
    @user_namespace.doc(description='Get all users')
    def get(self):
        """
            Get all users
        """
        return User.query.all(), HTTPStatus.OK  

@user_namespace.route('/<int:user_id>')
class GetEditUserById(Resource):

    @user_namespace.marshal_with(user_model)
    @user_namespace.doc(
        description='Get a user by ID',
        params = {
            'user_id': 'A user ID'
        }
    )
    def get(self, user_id):
        """
            Get user by id
        """
        user = User.query.get_or_404(user_id)
        return user, HTTPStatus.OK


    @user_namespace.expect(basic_user_model)
    @user_namespace.marshal_with(basic_user_model)
    @user_namespace.doc(
        description='Update a user. JWT is required to perform this action',
        params = {
            'user_id': 'A user ID'
        }
    )
    @jwt_required()
    @token_required
    def put(self, user_id):
        """
            Update user by id
        """
        current_user = get_jwt_identity()
        data = request.get_json()
        user = User.get_by_id(user_id)

        if current_user == user_id:
            try:
                user.username = data['username'].lower()
                user.email = data['email']
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                abort(
                    HTTPStatus.BAD_REQUEST, 
                    message=f"Username {data['username']} or email {data['email']} already exit. Please try a different username and or email"
                )            
        else:
            abort(
                HTTPStatus.UNAUTHORIZED, 
                message="You are not authorized to perform this action"
            ) 
        return user, HTTPStatus.OK
    
    @user_namespace.route('/<string:username>')
    class GetUserByUserName(Resource):
        @user_namespace.marshal_with(user_model)
        @user_namespace.doc(
        description='Get a user by username',
        params = {
                'username': 'A username'
            }
        )
        @cache.cached(timeout=30)
        def get(self, username):
            """
                Get User by username
            """

            user = User.query.filter_by(username=username.lower()).first()
            return user, HTTPStatus.OK

    