from ..db import db
from datetime import datetime


class Blocklist(db.Model):
    __tablename__ = 'blocklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(), nullable=False)
    date_blocked = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<jti: {self.jti}>'
    
    def add_to_blocklist(self):
        db.session.add(self)
        db.session.commit()

    