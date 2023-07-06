import os
from decouple import config
from datetime import timedelta
from flask_caching import Cache
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


cache = Cache()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
# limiter = Limiter(
#     key_func=get_remote_address, 
#     storage_uri="redis://localhost:6379",
#     # storage_options={"socket_connect_timeout": 30},
#     # strategy="fixed-window", # or "moving-window"
# )
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = 'static/images/qrCodes'

#FOR POSTGRES DB
uri = os.getenv('DATABASE_URL') #or other relevant config var
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)


class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=120)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=120)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', 'jwt_secret')
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAIL_SERVER = config('MAIL_SERVER')
    MAIL_PORT = config('MAIL_PORT')
    MAIL_USERNAME = config('MAIL_USERNAME')
    MAIL_PASSWORD = config('MAIL_PASSWORD')
    MAIL_USE_TLS = config('MAIL_USE_TLS', False, cast=bool)
    MAIL_USE_SSL = config('MAIL_USE_SSL', True, cast=bool)
    CACHE_DEFAULT_TIMEOUT = config('CACHE_DEFAULT_TIMEOUT', 30, cast=int)
    
    
class DevConfig(Config):
    DEBUG = config('DEBUG', True, cast=bool)
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATION = False
    CACHE_TYPE = config('CACHE_TYPE', 'SimpleCache')
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(BASE_DIR, 'db.sqlite3')
    SQLALCHEMY_DATABASE_URI = 'postgresql://cixors_database_user:2N21VdPNnabrxPYayGMYzOICS0mOzaa8@dpg-cieq12dgkuvlk1hu7p70-a.oregon-postgres.render.com/cixors_database'
    

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATION = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://' #THIS USES SQL MEMORY DATABASE INSTEAD OF CREATING A NEW ONE
    
class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = config('DEBUG', False, cast=bool)
    CACHE_TYPE = config('CACHE_TYPE', 'RedisCache')
    CACHE_REDIS_HOST = config('CACHE_REDIS_HOST')
    CACHE_REDIS_PORT = config('CACHE_REDIS_PORT')
    CACHE_REDIS_URL = config('CACHE_REDIS_URL')
    RATELIMIT_STORAGE_URI = config('RATELIMIT_STORAGE_URI')
    # pass


config_dict = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'test': TestConfig
}