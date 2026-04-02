from app.extensions import db



class Vacancy(db.Model):
    __tablename__ = "vacancies"

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    title_en = db.Column(db.String(200), nullable=False)
    title_de = db.Column(db.String(200), nullable=False)

    description_en = db.Column(db.Text, nullable=False)
    description_de = db.Column(db.Text, nullable=False)

    company = db.Column(db.String(150), nullable=False)

