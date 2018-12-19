from flask import abort, Blueprint, g, jsonify, request
from flask_httpauth import HTTPTokenAuth

from grotto.models import User

auth = HTTPTokenAuth('Bearer')
bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth.verify_token
def verify_token(token):
    if token == '':
        return None

    g.current_user = User.verify_auth_token(token)

    return g.current_user is not None


@bp.route('/token/', methods=['POST'])
def generate_token():
    data = request.get_json()

    if data is None or not data.keys() >= {'username', 'password'}:
        abort(400)

    user = User.query.filter_by(username=data['username']).first()

    if user is None:
        return jsonify({'message': 'User not found.'}), 404

    if not user.verify_password(data['password']):
        return jsonify({'message': 'Incorrect password.'}), 401

    token = user.generate_auth_token(expiration=86400)

    return jsonify({'token': token})
