from flask import Flask, session, request 
from .extensions import db
from .routes.vacancy import vacancy_bp
from .routes.auth import auth_bp
from .translations import translations 
from flasgger import Swagger
from .routes.api import api_bp
from .routes.application import application_bp

from .models.user import User
from .models.vacancy import Vacancy, Skill, vacancy_skills
from .models.department import Department
from .models.application import Application, Message

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'super-secret-key-for-dev'
    
    db.init_app(app)
    
    app.register_blueprint(vacancy_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(application_bp)

    Swagger(app)

    @app.context_processor
    def inject_translator():
        def translate(key):
            lang = session.get('lang', 'ru')
            return translations.get(lang, translations['ru']).get(key, key)
            
        def get_db_lang(obj, field_base):
            if obj is None:
                return ""
            lang = session.get('lang', 'ru')
            attr_name = f"{field_base}_{lang}"
            return getattr(obj, attr_name, getattr(obj, f"{field_base}_ru", ""))

        return dict(t=translate, get_db_lang=get_db_lang)

    @app.before_request
    def detect_language():
        lang_param = request.args.get('lang')
        if lang_param in ['ru', 'en', 'de']:
            session['lang'] = lang_param
            return

        if 'lang' in session:
            return

        best_match = request.accept_languages.best_match(['ru', 'en', 'de'])
        if best_match:
            session['lang'] = best_match
        else:
            session['lang'] = 'ru'

    with app.app_context():
        db.create_all()

    return app