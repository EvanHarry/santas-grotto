__version__ = '1.0.14'

import os

from flask import Flask, jsonify
from flask_cors import CORS


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'grotto.sqlite'),
    )

    cors = CORS()
    cors.init_app(app)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import search
    app.register_blueprint(search.bp)

    from . import stock
    app.register_blueprint(stock.bp)

    from . import suppliers
    app.register_blueprint(suppliers.bp)

    from . import users
    app.register_blueprint(users.bp)

    @app.after_request
    def api_version(response):
        response.headers['Access-Control-Expose-Headers'] = 'API-Version'
        response.headers['API-Version'] = __version__
        return response

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'message': 'Bad request.'}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'message': 'Not found.'}), 404

    @app.errorhandler(405)
    def not_allowed(e):
        return jsonify({'message': 'Method not allowed.'}), 405

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
