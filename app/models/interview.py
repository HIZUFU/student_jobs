from app.extensions import db

class Interview(db.Model):
    __tablename__ = "interviews"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    scheduled_at = db.Column(db.DateTime, nullable=False)
    meeting_link = db.Column(db.String(255)) # Ссылка на BBB по заданию