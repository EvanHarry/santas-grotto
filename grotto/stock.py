from flask import abort, Blueprint, jsonify, request

from grotto.auth import auth
from grotto.db import get_db

bp = Blueprint('stock', __name__, url_prefix='/stock')


def to_dict(item):
    return {
        'id': item['id'],
        'supplier_code': item['supplier_code'],
        'tidings_code': item['tidings_code'],
        'supplier': item['supplier'],
        'location': item['location'],
        'quantity': item['quantity']
    }


@bp.route('/', methods=['GET'])
@auth.login_required
def get_all_stock():
    db = get_db()

    cursor = db.execute(
        'SELECT * FROM stock'
    )

    stock = []
    for item in cursor:
        stock.append(to_dict(item))

    return jsonify(stock)


@bp.route('/', methods=['POST'])
@auth.login_required
def create_new_stock():
    data = request.get_json()

    if data is None or not data.keys() >= {'supplier_code', 'tidings_code', 'supplier', 'location', 'quantity'}:
        abort(400)

    db = get_db()

    try:
        cursor = db.execute(
            'INSERT INTO stock (supplier_code, tidings_code, supplier, location, quantity) VALUES (?, ?, ?, ?, ?)',
            (data['supplier_code'], data['tidings_code'], data['supplier'], data['location'], data['quantity'])
        )
        db.commit()
    except db.Error:
        abort(400)

    return jsonify({'message': 'Item created.', 'id': cursor.lastrowid}), 201


@bp.route('/<stock_id>/', methods=['DELETE'])
@auth.login_required
def delete_stock(stock_id):
    db = get_db()

    cursor = db.execute(
        'DELETE FROM stock WHERE id = ?', (stock_id,)
    )
    db.commit()

    return jsonify({'message': 'Item deleted.'}), 200


@bp.route('/<stock_id>/', methods=['PUT'])
@auth.login_required
def edit_stock(stock_id):
    data = request.get_json()

    if data is None or not data.keys() >= {'supplier_code', 'tidings_code', 'supplier', 'location', 'quantity'}:
        abort(400)

    db = get_db()

    try:
        cursor = db.execute(
            'UPDATE stock SET supplier_code = ?, tidings_code = ?, supplier = ?, location = ?, quantity = ? WHERE id = ?',
            (data['supplier_code'], data['tidings_code'], data['supplier'], data['location'], data['quantity'], stock_id)
        )
        db.commit()
        stock = db.execute(
            'SELECT * FROM stock WHERE id = ?', (stock_id,)
        ).fetchone()
    except db.Error:
        abort(400)

    return jsonify(to_dict(stock))
