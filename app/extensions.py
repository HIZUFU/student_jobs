# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flasgger import Swagger
from flask_migrate import Migrate

db = SQLAlchemy()
babel = Babel()
swagger = Swagger()
migrate = Migrate()