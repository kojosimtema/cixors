import unittest
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from .. import create_app
from ..main.db import db
from ..main.models.user import User
from ..main.config.config import config_dict


class authTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()
        
        db.create_all()

    def tearDown(self):
        db.drop_all()

        self.appctx.pop()
        self.app = None
        self.client = None

    def test_create_user(self):
       data = {
           'username': 'user',
           'email': 'user@gmail.com',
           'password': 'password',
           'confirm_password': 'password'
       }
       
       response = self.client.post('/auth/signup', json=data)

       assert response.status_code == 201
       assert response.json['success'] == 1  

    def test_user_verification(self):
        #Add user manually to get verification code
        user = User(
            username = 'user',
            email = 'user@gmail.com',
            password = generate_password_hash('password'),
            verification_code = 'testV',
        )
        db.session.add(user)
        db.session.commit()
        data = {
            'verification_code': 'testV'
        }
        response = self.client.put('/auth/verify/user@gmail.com', json=data)
        assert response.status_code == 200
        assert response.json['message'] == 'You have been successfully verified'
    
    def test_user_login_success(self):
        #create and verify user with "test_user_verification function before login"
        self.test_user_verification()
       
        loginDetails = {
            'email': 'user@gmail.com',
            'password': 'password'
        }
        response = self.client.post('/auth/login', json=loginDetails)
        assert response.status_code == 200
        
    def test_user_login_fail(self):        
       #create and verify user with "test_user_verification function before login"
        self.test_user_verification()

        loginDetails = {
           'email': 'user@gmail.com',
           'password': 'U0uJJMjB'
       }

        response = self.client.post('/auth/login', json=loginDetails)

        assert response.status_code == 401
        assert response.json['message'] == 'Your credentials do not match'

    def test_user_logout(self):
        #Create a new user
        self.test_create_user()

        #Create Access Token for user
        token = create_access_token(identity=1)

        headers = {
           'Authorization': f'Bearer {token}'
       }
        
        response = self.client.post('/auth/logout', headers=headers)

        assert response.status_code == 200
        assert response.json['message'] == 'You have successfully logged out'

    
    def test_change_password(self):

        #Add an user using test_create_user function before changing user password  
       self.test_create_user()

       data = {
          'old_password': 'password',
          'new_password': 'newpassword',
          'confirm_password': 'newpassword'
       }

       token = create_access_token(identity=1)

       headers = {
           'Authorization': f'Bearer {token}'
       }
       
       response = self.client.put('/auth/change_password', json=data, headers=headers)

       assert response.status_code == 200
       assert response.json['message'] == 'Password successfuly changed'

    def test_reset_password(self):

        #create and verify user with "test_user_verification function before login"
        self.test_user_verification()

        response = self.client.put('/auth/resetpassword/user@gmail.com')

        assert response.status_code == 200
        assert response.json['message'] == 'Your password has been reset. Check your email for new password'


