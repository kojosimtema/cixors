import jwt
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_restx import abort
from functools import wraps
from http import HTTPStatus

from ..models.blocklist import Blocklist
from ..models.user import User


#THIS IS A DECORATOR TO ENSURE USERS ARE LOGGED IN
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            user = get_jwt_identity()
            current_user = User.get_by_id(user)
            if current_user:
                jti = get_jwt()['jti']
                blocked = Blocklist.query.filter_by(jti = jti).first()
                if blocked:
                    # return {
                    #     'success': False,
                    #     'message': 'You are not signed in'
                    # }, HTTPStatus.UNAUTHORIZED
                    abort(HTTPStatus.UNAUTHORIZED, message='You are not signed in')
            else:
                # return {
                #         'success': False,
                #         'message': 'You are not signed in'
                #     }, HTTPStatus.UNAUTHORIZED
                abort(HTTPStatus.UNAUTHORIZED, message='You are not signed in')
        except jwt.ExpiredSignatureError:
            # return {
            #     'success': False,
            #     'message': 'Your token has expired, Please sign in again'
            # }, HTTPStatus.UNAUTHORIZED
            abort(HTTPStatus.UNAUTHORIZED, message='Token has expired. Please sign in')
        except jwt.InvalidSignatureError:
            # return {
            #     'success': False,
            #     'message': 'Invalid token, Please sign in again'
            # }, HTTPStatus.UNAUTHORIZED
            abort(500, message='Invalid token')
        except jwt.InvalidTokenError:
            # return {
            #     'success': False,
            #     'message': 'Invalid token, Please sign in again'
            # }, HTTPStatus.UNAUTHORIZED
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, message='Invalid token')
          
        # except Exception as e:
        #     # return {
        #     #     'success': False,
        #     #     'message': 'An exception occured. Please login again'
        #     # }, HTTPStatus.UNAUTHORIZED
        #     abort(HTTPStatus.UNAUTHORIZED, message='An exception occured. Please login again')
            
        return f(*args, **kwargs)
    return decorated


    