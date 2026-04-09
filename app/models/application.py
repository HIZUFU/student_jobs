from app.extensions import db
from datetime import datetime

class ApplicationStatus(db.Model):
    __tablename__ = 'application_statuses'
    id = db.Column(db.Integer, primary_key=True)
    status_ru = db.Column(db.String(50), nullable=False)
    status_en = db.Column(db.String(50))
    status_de = db.Column(db.String(50))

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancies.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('application_statuses.id'), nullable=False, default=1)
    
    cover_letter = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('User', backref='student_applications')
    status = db.relationship('ApplicationStatus')