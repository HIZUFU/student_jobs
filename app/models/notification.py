from app.extensions import db

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message_en = db.Column(db.String(255))
    message_de = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)