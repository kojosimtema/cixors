import unittest
from flask_jwt_extended import create_access_token
from .. import create_app
from ..main.db import db
from ..main.models.user import User
from ..main.config.config import config_dict


class usersTestCase(unittest.TestCase):
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

    def test_get_all_users(self):
        response = self.client.get('/users/')
        assert response.status_code == 200
        assert response.json == []

    def test_get_user_by_id(self):
        #Create a User
        # authTestCase.test_create_user(self)
        user_data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'password': 'password',
            'confirm_password': 'password'
        }
        self.client.post('/auth/signup', json=user_data)

        response = self.client.get('/users/1')
        assert response.status_code == 200
        assert response.json['email'] == 'user@gmail.com'

    def test_get_user_by_username(self):
        #Create a User
        # authTestCase.test_create_user(self)
        user_data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'password': 'password',
            'confirm_password': 'password'
        }
        self.client.post('/auth/signup', json=user_data)
        
        response = self.client.get('/users/user')
        assert response.status_code == 200

    def test_update_user_by_id(self):
        #Create a User
        # authTestCase.test_create_user(self)
        user_data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'password': 'password',
            'confirm_password': 'password'
        }
        self.client.post('/auth/signup', json=user_data)
        
        data={
            'email': 'newemail@gmail.com',
            'username': 'newuser'
        }
        token = create_access_token(identity=1)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = self.client.put('/users/1', json=data, headers=headers)
        assert response.status_code == 200
        assert response.json['username'] == 'newuser'