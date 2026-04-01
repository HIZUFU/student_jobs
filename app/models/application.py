from app.extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancies.id'), nullable=False)
    status = db.Column(db.String(50), default="Pending") # Pending, Accepted, Rejected
    cover_letter = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)