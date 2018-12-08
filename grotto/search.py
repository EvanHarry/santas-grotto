from flask import abort, Blueprint, current_app, g, jsonify, make_response, request

from grotto.auth import auth
from grotto.db import get_db

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('/<category>/<search_text>/', methods=['GET'])
@auth.login_required
def search_by_category_text(category, search_text):
    db = get_db()

    partial_search_text = '%{0}%'.format(search_text)
    cursor = db.execute(
        'SELECT * FROM stock WHERE {0} LIKE ?'.format(category), (partial_search_text,)
    )

    stock = []
    for item in cursor:
        stock.append({
            'id': item['id'],
            'supplier_code': item['supplier_code'],
            'tidings_code': item['tidings_code'],
            'supplier': item['supplier'],
            'location': item['location'],
            'quantity': item['quantity']
        })

    return jsonify(stock)
