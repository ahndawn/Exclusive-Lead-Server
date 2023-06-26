from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String())
    reset_token = db.Column(db.String())
    reset_token_expiration = db.Column(db.String())
    is_active = db.Column(db.Boolean, default=True)
    
    def get_id(self):
        return str(self.id)