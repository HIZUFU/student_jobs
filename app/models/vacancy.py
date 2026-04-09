from app.extensions import db

vacancy_skills = db.Table('vacancy_skills',
    db.Column('vacancy_id', db.Integer, db.ForeignKey('vacancies.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True)
)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name_ru = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    name_de = db.Column(db.String(100))
    vacancies = db.relationship('Vacancy', backref='category', lazy=True)

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class Vacancy(db.Model):
    __tablename__ = 'vacancies'
    id = db.Column(db.Integer, primary_key=True)
    
    title_ru = db.Column(db.String(150), nullable=False)
    title_en = db.Column(db.String(150))
    title_de = db.Column(db.String(150))
    
    description_ru = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text)
    description_de = db.Column(db.Text)
    
    company = db.Column(db.String(150), nullable=False)
    
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    skills = db.relationship('Skill', secondary=vacancy_skills, backref=db.backref('vacancies', lazy='dynamic'))
    applications = db.relationship('Application', backref='vacancy', lazy=True)