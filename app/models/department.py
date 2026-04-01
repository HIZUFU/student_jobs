from app.extensions import db

class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_de = db.Column(db.String(100), nullable=False)
    
    # Связь: один отдел может иметь много вакансий
    vacancies = db.relationship('Vacancy', backref='department', lazy=True)