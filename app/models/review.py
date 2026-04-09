from app.extensions import db

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Оцениваемый
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))      # Автор
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)