from flask import Blueprint, jsonify, request
from app.models.vacancy import Vacancy
from app.models.user import User
from app.models.department import Department
from app.models.application import Application

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/vacancies', methods=['GET'])
def get_vacancies():
    """
    Финальный эндпоинт: полный список вакансий со всеми метаданными
    """
    lang = request.args.get('lang', 'ru')
    vacancies = Vacancy.query.all()
    
    result = []
    for v in vacancies:
        result.append({
            'id': v.id,
            'title': getattr(v, f'title_{lang}', v.title_ru) or v.title_ru,
            'description': getattr(v, f'description_{lang}', v.description_ru) or v.description_ru,
            'company': {
                'name': v.company,
                'author_id': v.author_id,
                # Подтягиваем доп. инфо из профиля работодателя, если есть
                'website': v.author.employer_profile.website if v.author.employer_profile else None
            },
            'compensation': {
                'from': v.salary_from,
                'to': v.salary_to,
                'currency': 'RUB',
                'is_negotiable': not (v.salary_from or v.salary_to)
            },
            'conditions': {
                'employment_type': v.employment_type,
                'is_internship': v.is_internship,
                'remote_work': getattr(v, 'remote_allowed', False) # Если добавлял такое поле
            },
            'category': {
                'id': v.department.id if v.department else None,
                'name': getattr(v.department, f'name_{lang}', v.department.name_ru) if v.department else None
            },
            'stats': {
                'total_applications': len(v.applications)
            },
            'published_at': v.created_at.isoformat() if v.created_at else None
        })
        
    return jsonify(result)

@api_bp.route('/stats', methods=['GET'])
def get_global_stats():
    """
    Дополнительный эндпоинт для дашборда (общее кол-во вакансий и студентов)
    """
    return jsonify({
        'total_vacancies': Vacancy.query.count(),
        'total_students': User.query.filter_by(role='student').count(),
        'total_applications': Application.query.count()
    })