from operator import itemgetter

from flask import Blueprint, jsonify

from grotto.auth import auth
from grotto.db import get_db

bp = Blueprint('locations', __name__, url_prefix='/locations')


@bp.route('/', methods=['GET'])
@auth.login_required
def get_all_locations():
    db = get_db()

    cursor = db.execute(
        'SELECT DISTINCT location FROM stock'
    )

    locations = []
    for item in cursor:
        locations.append({
            'text': item['location']
        })

    locations.sort(key=itemgetter('text'))

    return jsonify(locations)
