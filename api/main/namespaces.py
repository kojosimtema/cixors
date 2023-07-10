from flask_restx import fields, Model
from flask_restx import Namespace
# from .auth.views import auth_namespace
# from .user.views import user_namespace

namespaces = Namespace('namespaces', description='Namespaces')

basic_user_model = namespaces.model(
    'Basic_User', {
        'username': fields.String(required=True, description='A username'),
        'email': fields.String(required=True, description='An email')
    }
)

signup_model = namespaces.inherit(
    'Signup', basic_user_model, {  
        'password': fields.String(required=True, description='A password'),
        'confirm_password': fields.String(required=True, description='Confirm password')
    }
)
user_activation_model = namespaces.model(
    'Activate', {
        'verification_code': fields.String(required=True, description='A user verification code')
    }
)

login_model = namespaces.model(
    'Login', {
        'email': fields.String(required=True, description='An email'),
        'password': fields.String(required=True, description='A password')
    }
)

change_password_model = namespaces.model(
    'Change_Password', {
        'old_password': fields.String(required=True, description='Your old password'),
        'new_password': fields.String(required=True, description='Your new password'),
        'confirm_password': fields.String(required=True, description='Confirm new password') 
    }
)

stats_model = namespaces.model(
    'Statistics', {
        'address': fields.String(),
        'user_agent': fields.String(),
        'ip_address': fields.String()
    }
)

long_url_model = namespaces.model(
    'Long_url', {
        'long_url': fields.String(required=True, description='Long Url'),
        'host_url': fields.String(description='Hostname. Use this field for own domain or leave empty for default domain')
    }
)

short_url_model = namespaces.model(
    'Short_url', {
        'short_url': fields.String(required=True, description='Short Url')
    }
)

short_url_path_model = namespaces.model(
    'Short_url_path', {
        'url_path': fields.String(required=True, description='Short Url Path')
    }
)

basic_url_model = namespaces.model(
    'Basic_url', {
        'id': fields.Integer(),
        'short_url': fields.String(),
        'long_url': fields.String(),
        'clicks': fields.Integer()
    }
)

url_model = namespaces.inherit(
    'Url', basic_url_model, {
        'host_url': fields.String(),
        'url_path': fields.String(),
        'qr_code': fields.String(),
        'analytics': fields.List(fields.Nested(stats_model))
    }
)

user_model = namespaces.inherit(
    'User', basic_user_model, {
        'id': fields.Integer(),
        'is_verified': fields.Boolean(),
        'urls': fields.List(fields.Nested(basic_url_model))
    }
)

