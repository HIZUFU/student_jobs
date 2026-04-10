from app.extensions import db
from .user import User, StudentProfile, EmployerProfile
from .vacancy import Vacancy, Skill, vacancy_skills, Category
from .department import Department
from .application import Application, ApplicationStatus
from .interview import Interview
from .review import Review