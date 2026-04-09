from app.extensions import db

class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    bio_en = db.Column(db.Text)
    bio_de = db.Column(db.Text)
    phone = db.Column(db.String(20))