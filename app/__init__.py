from flask import Flask, request
from .config import Config
from .extensions import db, babel, swagger, migrate
from .routes.vacancy import vacancy_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    babel.init_app(app, locale_selector=lambda: request.args.get('lang') or 'en')
    swagger.init_app(app)

    from . import models 

    app.register_blueprint(vacancy_bp)

    return app