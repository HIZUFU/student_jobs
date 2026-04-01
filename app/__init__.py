from flask import Flask
from .config import Config
from .extensions import db
from .models.user import User
from app.extensions import db, babel, swagger
from .routes.vacancy import vacancy_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(vacancy_bp)

    db.init_app(app)
    babel.init_app(app)
    swagger.init_app(app)

    @app.route("/")
    def home():
        return "DB connected"

    return app