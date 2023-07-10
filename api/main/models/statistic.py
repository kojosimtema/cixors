from ..db import db
from datetime import datetime


class Statistic(db.Model):
    __tablename__ = 'statistics'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    country = db.Column(db.String(), nullable=False)
    user_agent = db.Column(db.String(), nullable=False)
    ip_address = db.Column(db.String(), nullable=False)
    url_id = db.Column(db.Integer(), db.ForeignKey('urls.id'))
    date_created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    date_updated = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Statistic: {self.id}>'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

