# app/models.py
from app import db
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta

class User(db.Model):
    """Table for users"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    bucketlists = db.relationship('Bucketlist', order_by='Bucketlist.id', cascade="all, delete-orphan")

    def __init__(self, email, password):
        #Initialize user with email and password
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode

    def password_is_valid(self, password):
        """Checks the password agaist it's hash to validate the user's password"""
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database"""
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """Generates the access token"""
        try:
            #Setup a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=5),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            #Create the byte string token using payload and SECRET key
            jwt_string = jwt.encode(payload, current_app.config.get('SECRET'), algorithm='HS256')
            return jwt_string

        except exception as e:
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the authorization header"""
        try:
            #Try to decode the token using SECRET variable
            payload = jwt.decode(token, currnt_app.config.get('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            #The token is expired, return an error string
            return "Expired token. Please login to get a new token."
        except jwt.InvalidTokenError:
            return "Invalid token. Please register or login."



class Bucketlist(db.Model):
    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, name, created_by):
        self.name = name
        self.created_by = created_by

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        return Bucketlist.query.filter_by(created_by=user_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucketlist: {}>".format(self.name)

