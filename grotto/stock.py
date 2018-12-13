from datetime import datetime

from flask import abort, Blueprint, g, jsonify, request

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
        'quantity': item['quantity'],
        'last_modified': item['last_modified']
    }


@bp.route('/statistics/', methods=['GET'])
@auth.login_required
def get_stock_statistics():
    db = get_db()

    cursor = db.execute(
        'SELECT quantity FROM stock'
    )

    count = 0
    entries = 0

    for item in cursor:
        count += item['quantity']
        entries += 1

    return jsonify({'count': count, 'entries': entries})


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

    if data is None or not data.keys() >= {'supplier', 'location', 'quantity'}:
        abort(400)

    db = get_db()

    now = datetime.now().strftime("%d-%m-%Y")
    user = g.current_user['username']

    last_modified = '{0} - {1}'.format(now, user)

    supplier_code = data.get('supplier_code', '')
    tidings_code = data.get('tidings_code', '')

    try:
        cursor = db.execute(
            'INSERT INTO stock (supplier_code, tidings_code, supplier, location, quantity, last_modified) VALUES (?, ?, ?, ?, ?, ?)',
            (supplier_code, tidings_code, data['supplier'], data['location'], data['quantity'], last_modified)
        )
        db.commit()
    except db.Error:
        abort(400)

    return jsonify({'message': 'Item created.', 'id': cursor.lastrowid}), 201


@bp.route('/<stock_id>/', methods=['DELETE'])
@auth.login_required
def delete_stock(stock_id):
    db = get_db()

    db.execute(
        'DELETE FROM stock WHERE id = ?', (stock_id,)
    )
    db.commit()

    return jsonify({'message': 'Item deleted.'}), 200


@bp.route('/<stock_id>/', methods=['PUT'])
@auth.login_required
def edit_stock(stock_id):
    data = request.get_json()

    if data is None or not data.keys() >= {'supplier', 'location', 'quantity'}:
        abort(400)

    db = get_db()

    now = datetime.now().strftime("%d/%m/%Y")
    user = g.current_user['username']

    last_modified = '{0} - {1}'.format(now, user)

    supplier_code = data.get('supplier_code', '')
    tidings_code = data.get('tidings_code', '')

    try:
        db.execute(
            'UPDATE stock SET supplier_code = ?, tidings_code = ?, supplier = ?, location = ?, quantity = ?, last_modified = ? WHERE id = ?',
            (supplier_code, tidings_code, data['supplier'], data['location'], data['quantity'], last_modified, stock_id)
        )
        db.commit()
        stock = db.execute(
            'SELECT * FROM stock WHERE id = ?', (stock_id,)
        ).fetchone()
    except db.Error:
        abort(400)

    return jsonify(to_dict(stock))
