from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flasgger import Swagger

db = SQLAlchemy()
babel = Babel()
swagger = Swagger()