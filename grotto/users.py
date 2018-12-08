from random import SystemRandom
from string import ascii_letters, digits

from flask import abort, Blueprint, g, jsonify, request
from werkzeug.security import generate_password_hash

from grotto.auth import admin_required, auth
from grotto.db import get_db

bp = Blueprint('users', __name__, url_prefix='/users')


def to_dict(item):
    return {
        'id': item['id'],
        'username': item['username'],
        'admin': item['admin']
    }


@bp.route('/', methods=['GET'])
@auth.login_required
@admin_required
def get_all_users():
    db = get_db()

    cursor = db.execute(
        'SELECT * FROM user'
    )

    users = []
    for item in cursor:
        users.append(to_dict(item))

    return jsonify(users)


@bp.route('/', methods=['POST'])
@auth.login_required
@admin_required
def create_new_user():
    data = request.get_json()

    if data is None or not data.keys() >= {'username', 'admin'}:
        abort(400)

    db = get_db()
    pwd = ''.join(SystemRandom().choice(ascii_letters + digits) for _ in range(8))

    print('Username: {0}, Password: {1}'.format(data['username'], pwd))

    try:
        cursor = db.execute(
            'INSERT INTO user (username, password, admin) VALUES (?, ?, ?)',
            (data['username'], generate_password_hash(pwd), data['admin'])
        )
        db.commit()
    except db.Error:
        abort(400)

    return jsonify({'message': 'User created.', 'password': pwd}), 201


@bp.route('/<user_id>/', methods=['DELETE'])
@auth.login_required
@admin_required
def delete_user(user_id):
    db = get_db()

    if int(user_id) == g.current_user['id']:
        abort(400)

    try:
        cursor = db.execute(
            'DELETE FROM user WHERE id = ?', (user_id,)
        )
        db.commit()
    except db.Error:
        abort(400)

    return jsonify({'message': 'User deleted.'}), 200


@bp.route('/<user_id>/', methods=['PUT'])
@auth.login_required
@admin_required
def edit_user(user_id):
    data = request.get_json()

    if data is None or not data.keys() >= {'username', 'admin'}:
        abort(400)

    db = get_db()

    try:
        cursor = db.execute(
            'UPDATE user SET username = ?, admin = ? WHERE id = ?',
            (data['username'], data['admin'], user_id)
        )
        db.commit()
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
    except db.Error:
        abort(400)

    return jsonify(to_dict(user))
