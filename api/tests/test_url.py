import unittest
from flask_jwt_extended import create_access_token

from .. import create_app
from ..main.db import db
from ..main.models.user import User
from ..main.config.config import config_dict


class urlTestCase(unittest.TestCase):
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

    def test_generate_url(self):
        #add new user
        user_data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'password': 'password',
            'confirm_password': 'password'
        }
        self.client.post('/auth/signup', json=user_data)

        token = create_access_token(identity=1)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        data = {
            'long_url': 'https://medium.com/geekculture/how-to-avoid-file-name-collisions-in-pytest-295f770bdec3',
            'host_url': 'sc/'
        }
        response = self.client.post('/scx/', json=data, headers=headers)
        assert response.status_code == 201
        # assert response.json['short_url'] == 'sc/'
    
    def test_get_all_url(self):
        #add new user
        user_data = {
            'username': 'user',
            'email': 'user@gmail.com',
            'password': 'password',
            'confirm_password': 'password'
        }
        self.client.post('/auth/signup', json=user_data)

        token = create_access_token(identity=1)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = self.client.get('/scx/', headers=headers)
        assert response.status_code == 200

    def test_get_url_by_id(self):
        #Generate short URL
        self.test_generate_url()

        response = self.client.get('/scx/1')
        assert response.status_code == 200

    def test_edit_url(self):
        #Generate short URL
        self.test_generate_url()

        token = create_access_token(identity=1)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        data = {
            'url_path': 'test'
        }
        response = self.client.put('/scx/1', json=data, headers=headers)
        assert response.status_code == 200
        assert response.json['message'] == 'You have successfully customized your url'

    def test_get_url_by_url_path(self):  
        #Edit URL path name to 'test'
        self.test_edit_url()

        #Get URL with path name 'test'
        response = self.client.get(f'/scx/test')
        assert response.status_code == 200

    def test_delete_url(self):
        #Generate short URL
        self.test_generate_url()

        token = create_access_token(identity=1)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = self.client.delete('/scx/1', headers=headers)
        assert response.status_code == 200
        assert response.json['message'] == 'Url successfully deleted'

    def test_get_url_by_user_id(self):
        #Generate short URL
        self.test_generate_url()

        response = self.client.get('/scx/user/1')
        assert response.status_code == 200

    def test_get_user_specific_url(self):
        #Edit URL path name to 'test'
        self.test_edit_url()

        token = create_access_token(identity=1)
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = self.client.get('/scx/test/1', headers=headers)
        assert response.status_code == 200

    def test_generate_qrcode(self):
        #Edit URL path name to 'test'
        self.test_edit_url()
        token = create_access_token(identity=1)
        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.put('/scx/test/qrcode', headers=headers)
        assert response.status_code == 200