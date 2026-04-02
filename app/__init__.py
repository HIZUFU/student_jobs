from flask import Flask, request
from .config import Config
from .extensions import db, babel, swagger, migrate
from .routes.vacancy import vacancy_bp
from .routes.main import main_bp
from .routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=lambda: request.args.get('lang') or 'en')
    swagger.init_app(app)

    # Регистрация моделей для миграций
    from . import models 

    # Регистрация блюпринтов
    app.register_blueprint(main_bp)      # Главная страница (/)
    app.register_blueprint(vacancy_bp, url_prefix='/api')  # API для вакансий (/api/vacancies)
    app.register_blueprint(auth_bp, url_prefix='/api')

    return app