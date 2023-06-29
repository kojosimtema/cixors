from ..db import db
from datetime import datetime


class Url(db.Model):
    __tablename__ = 'urls'

    id = db.Column(db.Integer, primary_key=True)
    host_url = db.Column(db.String(), nullable=False)
    url_path = db.Column(db.String(7), unique=True, nullable=False)
    short_url = db.Column(db.String(), unique=True, nullable=False)
    long_url = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    qr_code = db.Column(db.String(), unique=True)
    clicks = db.Column(db.Integer(), default=0)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    date_updated = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    analytics = db.relationship('Statistic', backref='url', lazy=False)    


    def __repr__(self):
        return f'<URL: {self.short_url}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def updateClicks(self):
        self.clicks += 1
        db.session.commit()

    def addQrCode(self, qr_code):
        self.qr_code = qr_code
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

