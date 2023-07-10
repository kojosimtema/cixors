import random, string, requests, uuid, os

from datetime import datetime
from flask_restx import Resource, Namespace, abort
from flask import request, current_app, redirect, url_for, send_from_directory
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException, InternalServerError

from ..db import db
from ..config.config import cache, limiter
from ..services.urlServices import generateQrCode
from ..services.authServices import token_required
from ..models.user import User
from ..models.url import Url
from ..models.statistic import Statistic
from ..namespaces import long_url_model, short_url_model, short_url_path_model, url_model


url_namespace = Namespace('scx', description='Namespace for URLs')

@url_namespace.route('/')
class GetAddUrl(Resource):
    @url_namespace.marshal_list_with(url_model)
    @url_namespace.doc(description='Get all URLs.')
    # @cache.cached()
    def get(self):
        """
            Get All URLs
        """
        return Url.query.all(), HTTPStatus.OK
    
    @url_namespace.expect(long_url_model)
    @url_namespace.marshal_with(short_url_model)
    @url_namespace.doc(description='Generate a Short URL. JWT is required to perform this action')
    @limiter.limit('40/day')
    @jwt_required()
    # @token_required
    def post(self):
        """
            Generate short URL
        """
        user_id = get_jwt_identity()
        current_user = User.get_by_id(user_id)
        data = request.get_json()
        url_exit = Url.query.filter_by(long_url = data.get('long_url')).filter_by(user_id=user_id).first()

        if url_exit:
            abort(HTTPStatus.CONFLICT, message=f'You already have a short URL for this resource {url_exit.short_url}. Please try a different resource')
        else: 
            try:
                valid_url = requests.get(data.get('long_url'))
                if valid_url.status_code == HTTPStatus.OK:
                    
                    characters = string.ascii_letters + string.digits
                    hostname = data.get('host_url')
                    url_path = ''.join((random.choice(characters) for i in range(7)))
                    
                    if hostname:
                        short_url = ''.join((hostname, url_path))
                        new_url = Url(
                            host_url = hostname,
                            url_path = url_path,
                            short_url = short_url,
                            long_url = data.get('long_url')
                        )
                        new_url.user = current_user
                        try:
                            new_url.save()
                        except IntegrityError:
                            db.session.rollback()
                            return redirect(url_for('self.post'))
                        except SQLAlchemyError:
                            db.session.rollback()
                            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='An error occured whiles adding Url')
                        return new_url, HTTPStatus.CREATED
                    else:
                        default_host = request.base_url
                        short_url = ''.join((default_host, url_path))
                        new_url = Url(
                            host_url = default_host,
                            url_path = url_path,
                            short_url = short_url,
                            long_url = data.get('long_url')
                        )
                        new_url.user = current_user
                        try:
                            new_url.save()
                        except IntegrityError:
                            db.session.rollback()
                            return redirect(url_for('self.post'))
                        except SQLAlchemyError:
                            db.session.rollback()
                            abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='An error occured whiles adding Url')
                        return new_url, HTTPStatus.CREATED
                else:
                    abort(valid_url.status_code, message='URL not found. It might be broken or invalid')
            except FileNotFoundError:
                abort(HTTPStatus.NOT_FOUND, message='URL not found. It might be broken or invalid')
            except Exception:
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message='URL not found. It might be broken or invalid')
            
                    
                
            
    @url_namespace.route('/<url_path>')
    class GetEditDeleteUrlByPath(Resource):

        @url_namespace.marshal_with(long_url_model)
        @url_namespace.doc(
            description='Get a long URL using the short URL path excluding the hostname or host url',
            params = {
                'url_path': 'Short URL path without hostname'
                }
            )
        @cache.cached()
        @limiter.limit('1/3 second')
        def get(self, url_path):
            """
                Get long URL by short URL path
            """
            url = Url.query.filter_by(url_path = url_path).first()
            
            r_a = request.remote_addr
            remote_ip = request.headers.get("X-Forwarded-For", r_a)
            user_agent = str(request.user_agent)
            # serviceurl = f'http://www.geoplugin.net/json.gp?ip='

            # response = requests.get(f'http://ip-api.com/json/{user_agent}').json()
            if remote_ip == '127.0.0.1':
                response = requests.get('http://ip-api.com/json').json()
                user_ip = response['query']
            else:
                response = requests.get(f'http://ip-api.com/json/{remote_ip}').json()
                user_ip = remote_ip
            city = response['city']
            country = response['country']
            address = f'{city}, {country}'
            
            print(f"this is Remote Address {r_a}")
            print(f"this is Request Header {user_ip}")
            print(f"this is user agent {user_agent}")
            print(f'this is response {response}')
            

            if url:
                url_stats = Statistic.query.filter_by(url_id=url.id).filter_by(user_agent=user_agent).filter_by(ip_address=user_ip).filter_by(address=address).first()

                if not url_stats:
                    new_stats = Statistic(
                            address = address,
                            city = city,
                            country = country,
                            user_agent = user_agent,
                            ip_address = user_ip
                        )
                    new_stats.url = url
                    new_stats.save()

                url.updateClicks()

            return url, HTTPStatus.OK
        
@url_namespace.route('/<int:url_id>')
class GetEditDeleteUrlById(Resource):
    @url_namespace.marshal_with(url_model)
    @url_namespace.doc(
        description='Get URL details by URL ID',
        params = {
            'url_id': 'A URL ID'
        }
    )
    @cache.cached()
    def get(self, url_id):
        """
            Get URL by ID
        """
        return Url.get_by_id(url_id), HTTPStatus.OK

    @jwt_required()
    @url_namespace.expect(short_url_path_model)
    @url_namespace.doc(
        description='Edit Your Short URL by ID. JWT is required to perform this action',
        params = {
            'url_id': 'A URL ID'
        }
    )
    # @token_required
    def put(self, url_id):
        """
            Edit URL by ID
        """
       
        data = request.get_json()
        user_id = get_jwt_identity()
        url = Url.query.filter_by(id = url_id).first()
        
        if url.user_id == user_id:
            url.url_path = data.get('url_path')
            url.short_url = url.host_url + data.get('url_path')
            url.date_updated = datetime.utcnow()
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                abort(HTTPStatus.BAD_REQUEST, message='This short Url is already in use. Please try a different one')
            return {
                'success': True,
                'message': 'You have successfully customized your url',
                'new_url': url.short_url
            }, HTTPStatus.OK
        else:
            return {
                'success': False,
                'message': 'You are not authorized to peform this action'
            }, HTTPStatus.UNAUTHORIZED
            # abort(HTTPStatus.UNAUTHORIZED, message='You are not authorized to peform this action')

    @jwt_required()
    @url_namespace.doc(
        description='Delete a URL by ID. JWT is required to perform this action',
        params = {
            'url_id': 'A URL ID'
        }
    )
    def delete(self, url_id):
        """
            Delete URL by ID
        """
        user_id = get_jwt_identity()
        url = Url.get_by_id(url_id)
        if url and url.user_id == user_id:
            url_stats = Statistic.query.filter_by(url_id=url_id).all()
            
            for stats in url_stats:
                stats.delete()
            url.delete()
            return {
                'success': True,
                'message': 'Url successfully deleted'
            }, HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND, message='Url not found')

@url_namespace.route('/user/<int:user_id>')
class GetUrlByUserId(Resource):

    @url_namespace.marshal_with(url_model)
    @url_namespace.doc(
        description='Get all URLs a of user by the User ID',
        params = {
            'user_id': 'A User ID'
        }
    )
    # @cache.cached(timeout=30)
    def get(self, user_id):
        """
            Get URLs by User ID
        """
        user_url = Url.query.filter_by(user_id = user_id).order_by(Url.clicks.desc()).all()
        return user_url, HTTPStatus.OK
    
@url_namespace.route('/<url_path>/<user_id>')
class GetUserSpecificUrl(Resource):
    @jwt_required()
    @url_namespace.marshal_with(url_model)
    @url_namespace.doc(
        description='Get a specific URL by User ID and the Short URL path. JWT is required to perform this action',
        params = {
            'url_path': 'A Short URL path excluding hostname',
            'user_id': 'A User ID'
        }
    )
    @cache.cached()
    def get(self, url_path, user_id):
        """
            Get URL by path and user ID
        """
        url = Url.query.filter_by(user_id = user_id).filter_by(url_path = url_path).first()
        return url, HTTPStatus.OK

@url_namespace.route('/<url_path>/qrcode')
class GenerateQrCode(Resource):
    @url_namespace.doc(
        description='Generate a QRCode for your URL using the short URL path excluding the hostname',
        params = {
            'url_path': 'A Short URL path excluding hostname'
        }
    )
    @limiter.limit('60/day')
    @jwt_required()
    def put(self, url_path):
        """
            Generate QRCode for URL
        """
        user_id = get_jwt_identity()
        url = Url.query.filter_by(url_path = url_path).first()
        host = request.host

        if url and url.user_id == user_id:
            qrcode = generateQrCode(url.short_url)
            file_name = 'qr' + str(uuid.uuid4().time_low) + '.png'
            host_name = request.host_url

            #This path is where the images will be saved
            upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)

            #this path will serve as an endpoint for retrieving images i.e the 'ServeImage endpoint'
            file_path = f'{host_name}scx/qrcode/{file_name}'

            qrcode.save(upload_path)
            url.qr_code = file_path
            url.date_updated = datetime.utcnow()
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                abort(400, message='File name already exits. Please try again')
            return {
                'success': True,
                'qrcode': file_path,
                'file_name': file_name
            }, HTTPStatus.OK
        else:
            return {
                'success': False,
                'message': 'URL not found'
            }, HTTPStatus.NOT_FOUND
        
@url_namespace.route('/qrcode/<path:filename>')
class ServeImage(Resource):
    @url_namespace.doc(
        description='Get QRCode by filename',
        params = {
            'filename': 'A QRCode name'
        }
    )
    def get(self, filename):
        """
            Get QRCode by name
        """
        
        #as_attachment makes it possible to download the file
        return send_from_directory(f"../{current_app.config['UPLOAD_FOLDER']}", filename, as_attachment=True)
