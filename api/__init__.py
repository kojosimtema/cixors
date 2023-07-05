from flask import Flask
from flask_cors import CORS, cross_origin
from flask_restx import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import NotFound, MethodNotAllowed, TooManyRequests

from .main.db import db
from .main.url.views import url_namespace
from .main.auth.views import auth_namespace
from .main.user.views import user_namespace
from .main.namespaces import namespaces
from .main.models.url import Url
from .main.models.user import User
from .main.models.blocklist import Blocklist
from .main.models.statistic import Statistic
from .main.config.config import config_dict, cache, mail, limiter



def create_app(config = config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app,
         origins=['https://cixors.onrender.com', 'http://localhost:3000'],
         supports_credentials=True
    )
    # CORS(app, origins=['http://localhost:3000'])

    #initiate cache instance
    cache.init_app(app)

    #initiate mail instance
    mail.init_app(app)

    limiter.init_app(app)
    

    jwt = JWTManager(app)
    jwt.user_lookup_loader

    db.init_app(app)
    migrate = Migrate(app, db)

    authorization = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'headers',
            'name': 'Authorization',
            'description': 'Add a JWT token to the header with ** Bearer &lt; JWT &gt; ** to get authorized'
        }
    }
    
    api = Api(app,
        title='CIXORS',
        description='A URL shortener with RESTX API service',
        authorizations=authorization,
        security='Bearer Auth'
    )

    api.add_namespace(auth_namespace)
    api.add_namespace(user_namespace)
    api.add_namespace(url_namespace)
    api.add_namespace(namespaces)

    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404

    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}, 405
    
    @api.errorhandler(TooManyRequests)
    def ratelimit_handler(error):
        return {"error": "You have a exceeded your limit for the day. Please try again later"}, 429


    @app.shell_context_processor
    def make_shell_context():

        return {
            'db': db,
            'User': User,
            'Url': Url,
            'Statistic': Statistic,
            'Blocklist': Blocklist
        } 

    return app