from flask import abort, Blueprint, g, jsonify, request

from grotto import db
from grotto.models import User
from grotto.utils import generate_password
from grotto.routes.auth import auth
from grotto.routes.decorators import admin_required

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/', methods=['GET'])
@auth.login_required
@admin_required
def get_all_users():
    users = User.query.order_by('id')

    return jsonify([u.to_json() for u in users])


@bp.route('/', methods=['POST'])
@auth.login_required
@admin_required
def create_user():
    data = request.get_json()

    if data is None or not data.keys() >= {'username', 'admin'}:
        abort(400)

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists.'}), 400

    pwd = generate_password()
    user = User(username=data['username'], admin=data['admin'], password=pwd)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created.', 'password': pwd}), 201


@bp.route('/<user_id>/', methods=['GET'])
@auth.login_required
@admin_required
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()

    return jsonify(user.to_json()), 200


@bp.route('/<user_id>/', methods=['PUT'])
@auth.login_required
@admin_required
def update_user(user_id):
    data = request.get_json()
    user = User.query.filter_by(id=user_id).first_or_404()

    if data is None or not data.keys() >= {'username', 'admin'}:
        abort(400)

    user.admin = data['admin']
    user.username = data['username']

    db.session.commit()

    return jsonify(user.to_json()), 200


@bp.route('/<user_id>/', methods=['DELETE'])
@auth.login_required
@admin_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()

    if user.id == g.current_user.id:
        return jsonify({'message': 'Cannot delete current user.'}), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted.'}), 200
