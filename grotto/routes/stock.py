from datetime import datetime
from operator import itemgetter

from flask import abort, Blueprint, g, jsonify, request

from grotto import db
from grotto.models import Stock
from grotto.routes.auth import auth

bp = Blueprint('stock', __name__, url_prefix='/stock')


@bp.route('/', methods=['GET'])
@auth.login_required
def get_all_stock():
    stock = Stock.query.order_by('id')

    return jsonify([s.to_json() for s in stock])


@bp.route('/', methods=['POST'])
@auth.login_required
def create_stock():
    data = request.get_json()

    if data is None or not data.keys() >= {'supplier', 'location', 'quantity'}:
        abort(400)

    supplier_code = data.get('supplier_code', '')
    tidings_code = data.get('tidings_code', '')

    stock = Stock(data['supplier'], data['location'], data['quantity'], supplier_code, tidings_code)

    db.session.add(stock)
    db.session.commit()

    return jsonify({'message': 'Stock created.', 'id': stock.id}), 201


@bp.route('/<stock_id>/', methods=['GET'])
@auth.login_required
def get_stock(stock_id):
    stock = Stock.query.filter_by(id=stock_id).first_or_404()

    return jsonify(stock.to_json()), 200


@bp.route('/<stock_id>/', methods=['PUT'])
@auth.login_required
def update_stock(stock_id):
    data = request.get_json()
    stock = Stock.query.filter_by(id=stock_id).first_or_404()

    if data is None or not data.keys() >= {'supplier', 'location', 'quantity'}:
        abort(400)

    now = datetime.now().strftime("%d/%m/%Y")
    user = g.current_user.username

    stock.supplier = data['supplier']
    stock.location = data['location']
    stock.quantity = data['quantity']
    stock.supplier_code = data.get('supplier_code', '')
    stock.tidings_code = data.get('tidings_code', '')
    stock.last_modified = '{0} - {1}'.format(now, user)

    db.session.commit()

    return jsonify(stock.to_json()), 200


@bp.route('/<stock_id>/', methods=['DELETE'])
@auth.login_required
def delete_stock(stock_id):
    stock = Stock.query.filter_by(id=stock_id).first_or_404()

    db.session.delete(stock)
    db.session.commit()

    return jsonify({'message': 'Stock deleted.'}), 200


@bp.route('/statistics/', methods=['GET'])
@auth.login_required
def stock_statistics():
    stock = Stock.query.with_entities(Stock.quantity)

    count = 0
    entries = 0

    for i in stock:
        count += i[0]
        entries += 1

    return jsonify({'count': count, 'entries': entries}), 200


@bp.route('/locations/', methods=['GET'])
@auth.login_required
def get_stock_locations():
    raw_locations = Stock.query.with_entities(Stock.location).distinct()
    locations = [{'text': i[0]} for i in raw_locations]

    locations.sort(key=itemgetter('text'))

    return jsonify(locations), 200


@bp.route('/suppliers/', methods=['GET'])
@auth.login_required
def get_stock_suppliers():
    raw_suppliers = Stock.query.with_entities(Stock.supplier).distinct()
    suppliers = [{'text': i[0]} for i in raw_suppliers]

    suppliers.sort(key=itemgetter('text'))

    return jsonify(suppliers), 200
