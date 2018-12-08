from functools import wraps
import random
import string

from flask import abort, Blueprint, current_app, g, jsonify, make_response, request
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from werkzeug.security import check_password_hash

from grotto.db import get_db

auth = HTTPTokenAuth('Bearer')
bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth.verify_token
def verify_token(token):
    if token == '':
        return None

    g.current_user = verify_auth_token(token)

    return g.current_user is not None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'message': 'Unauthorized.'}), 401)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user['admin']:
            abort(401)
        return f(*args, **kwargs)

    return decorated_function


def generate_auth_token(user, expiration):
    key = current_app.config['SECRET_KEY']
    s = Serializer(key, expires_in=expiration)
    body = {
        'id': user['id'],
        'name': user['username'],
        'admin': user['admin']
    }
    return s.dumps(body).decode('ascii')


def generate_password():
    words = ['elf', 'santa', 'reindeer', 'snow']
    number = ''.join(random.choices(string.digits, k=2))
    password = ''.join(random.choice(words) + number)
    return password


def verify_auth_token(token):
    db = get_db()
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    return db.execute(
        'SELECT * FROM user WHERE id = ?', (data['id'],)
    ).fetchone()


@bp.route('/token/', methods=['POST'])
def login():
    data = request.get_json()

    if data is None or not data.keys() >= {'username', 'password'}:
        abort(400)

    db = get_db()
    error = None
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (data['username'],)
    ).fetchone()

    if user is None:
        error = {'msg': 'Incorrect username.', 'code': 404}
    elif not check_password_hash(user['password'], data['password']):
        error = {'msg': 'Incorrect password.', 'code': 401}

    if error is None:
        token = generate_auth_token(user, 86400)
        return jsonify({'token': token})
    else:
        return jsonify({'message': error['msg']}), error['code']
