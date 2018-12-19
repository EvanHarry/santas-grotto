from flask import abort, g
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user.admin:
            abort(401)
        return f(*args, **kwargs)

    return decorated_function
