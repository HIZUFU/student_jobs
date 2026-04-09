from flask import Blueprint, jsonify, request
from app.models.vacancy import Vacancy

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/vacancies', methods=['GET'])
def get_vacancies():
    """
    Получение списка вакансий с учетом языка
    ---
    parameters:
      - name: lang
        in: query
        type: string
        required: false
        default: ru
        description: Язык ответа (ru, en, de)
    responses:
      200:
        description: Список вакансий
    """
    lang = request.args.get('lang', 'ru')
    vacancies = Vacancy.query.all()
    
    result = []
    for v in vacancies:
        title = getattr(v, f'title_{lang}', v.title_ru) or v.title_ru
        desc = getattr(v, f'description_{lang}', v.description_ru) or v.description_ru
        
        result.append({
            'id': v.id,
            'title': title,
            'description': desc,
            'company': v.company
        })
        
    return jsonify(result)