from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

from grotto import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=100), unique=True)
    password_hash = db.Column(db.String(length=200))
    admin = db.Column(db.Boolean(), default=False)

    def __init__(self, username, password, **kwargs):
        self.username = username
        self.password = password
        self.admin = kwargs.get('admin', False)

    @property
    def password(self):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        key = current_app.config['SECRET_KEY']
        print(key)

        s = Serializer(key, expires_in=expiration)

        body = self.to_json()

        return s.dumps(body).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'admin': self.admin
        }

    def __repr__(self):
        return '<User {0}>'.format(self.username)
