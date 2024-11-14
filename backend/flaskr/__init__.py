import flaskr.models

from flask import Flask, jsonify
from config import DevelopmentConfig
from flaskr.extensions import db, jwt, api, cors, migrate

from flaskr.controllers.user_controller import bp as user_controller
from flaskr.controllers.auth_controller import bp as auth_controller
from flaskr.controllers.category_controller import bp as category_controller


def create_app(testing_config=None):
    app = Flask(__name__)

    if testing_config is None:
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(testing_config)

    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    api.init_app(app)
    cors.init_app(app)

    # Enregistrer les blueprints
    app.register_blueprint(user_controller, url_prefix="/api")
    app.register_blueprint(auth_controller, url_prefix="/api")
    app.register_blueprint(category_controller, url_prefix="/api")

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'status': 401,
            'sub_status': 42,
            'message': 'The token has expired'
        }), 401

    # Ajouter une route de santé
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'}), 200

    return app