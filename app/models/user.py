from app.extensions import db
from werkzeug.security import check_password_hash, generate_password_hash

student_skills = db.Table('student_skills',
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False) # student или organization
    password_hash = db.Column(db.String(256))

    student_profile = db.relationship('StudentProfile', backref='user', uselist=False)
    employer_profile = db.relationship('EmployerProfile', backref='user', uselist=False)
    
    skills = db.relationship('Skill', secondary=student_skills, backref=db.backref('students', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    group_name = db.Column(db.String(50)) # Например: НМТ-332210
    about_ru = db.Column(db.Text)
    about_en = db.Column(db.Text)
    about_de = db.Column(db.Text)

class EmployerProfile(db.Model):
    __tablename__ = 'employer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(150))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))