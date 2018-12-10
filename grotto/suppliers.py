from operator import itemgetter

from flask import Blueprint, jsonify

from grotto.auth import auth
from grotto.db import get_db

bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')


@bp.route('/', methods=['GET'])
@auth.login_required
def get_all_suppliers():
    db = get_db()

    cursor = db.execute(
        'SELECT DISTINCT supplier FROM stock'
    )

    suppliers = []
    for item in cursor:
        suppliers.append({
            'text': item['supplier']
        })

    suppliers.sort(key=itemgetter('text'))

    return jsonify(suppliers)
