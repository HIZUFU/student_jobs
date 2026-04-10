from app.extensions import db
from datetime import datetime

class Interview(db.Model):
    __tablename__ = 'interviews'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    
    scheduled_for = db.Column(db.DateTime, nullable=False)
    location_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    application = db.relationship('Application', backref=db.backref('interview', uselist=False))