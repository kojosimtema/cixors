from ..db import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    is_verified = db.Column(db.Boolean(), default=False, nullable=False)
    verification_code = db.Column(db.String())
    date_created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    date_verified = db.Column(db.DateTime())
    date_updated = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    urls = db.relationship('Url', backref='user', lazy=False)    

    def __repr__(self):
        return f'<User: {self.username}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

