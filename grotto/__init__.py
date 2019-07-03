__version__ = '2.0.4'

import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

cors = CORS()
db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    '''
    Create and configure the app.
    '''
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'grotto.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    '''
    Configure third party libraries
    '''
    cors.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    '''
    Add all blueprints
    '''
    from grotto import cli
    cli.init_app(app)

    from grotto.routes import auth
    app.register_blueprint(auth.bp)

    from grotto.routes import stock
    app.register_blueprint(stock.bp)

    from grotto.routes import search
    app.register_blueprint(search.bp)

    from grotto.routes import users
    app.register_blueprint(users.bp)

    '''
    API-VERSION header
    '''
    @app.after_request
    def api_version(response):
        response.headers['Access-Control-Expose-Headers'] = 'API-Version'
        response.headers['API-Version'] = __version__
        return response

    '''
    STATUS CODE handlers
    '''
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'message': 'Bad request.'}), 400

    @app.errorhandler(401)
    def unauthorised(e):
        return jsonify({'message': 'Unauthorised.'}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'message': 'Not found.'}), 404

    @app.errorhandler(405)
    def not_allowed(e):
        return jsonify({'message': 'Method not allowed.'}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'message': 'Server error.'}), 500

    return app
