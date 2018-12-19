from flask import abort, Blueprint, jsonify, request

from grotto.models import Stock
from grotto.routes.auth import auth

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('/', methods=['POST'])
@auth.login_required
def search_by_category_text():
    data = request.get_json()

    if data is None or not data.keys() >= {'category', 'search_text'}:
        abort(400)

    partial_search_text = '%{0}%'.format(data['search_text'])

    attr = getattr(Stock, data['category'])
    stock = Stock.query.filter(attr.like(partial_search_text)).all()

    return jsonify([s.to_json() for s in stock]), 200
