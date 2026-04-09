from app.extensions import db

vacancy_skills = db.Table('vacancy_skills',
    db.Column('vacancy_id', db.Integer, db.ForeignKey('vacancies.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True)
)