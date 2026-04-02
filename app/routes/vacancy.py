from deep_translator import GoogleTranslator
from flask import Blueprint, jsonify, request
from app.models.vacancy import Vacancy
from app.extensions import db
from app.utils.localization import localize_vacancy

vacancy_bp = Blueprint("vacancy", __name__)

def auto_translate(text, dest_lang):
    try:
        # Автоматически определяет исходный язык и переводит в нужный
        return GoogleTranslator(source='auto', target=dest_lang).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text # Если упало, вернем оригинал, чтобы база не пустовала
    
@vacancy_bp.route("/vacancies", methods=["GET"])
def get_vacancies():
    """
    Get a list of all vacancies
    ---
    parameters:
      - name: lang
        in: query
        type: string
        enum: ['en', 'de']
        default: 'en'
        description: Language of the content
    responses:
      200:
        description: A list of localized vacancies
        schema:
          type: array
          items:
            properties:
              id: {type: integer}
              title: {type: string}
              company: {type: string}
    """
    vacancies = Vacancy.query.all()
    result = [localize_vacancy(v) for v in vacancies]
    return jsonify(result)


@vacancy_bp.route("/vacancies", methods=["POST"])
def create_vacancy():
    data = request.get_json()

    # 1. Простейшая проверка на наличие данных
    title_raw = data.get("title")
    desc_raw = data.get("description")
    company = data.get("company")
    dept_id = data.get("department_id")

    if not title_raw or not desc_raw:
        return jsonify({"message": "Title and Description are required"}), 400

    # 2. Логика перевода (твоя "магия")
    t_en = data.get("title_en") or auto_translate(title_raw, 'en')
    t_de = data.get("title_de") or auto_translate(title_raw, 'de')
    
    d_en = data.get("description_en") or auto_translate(desc_raw, 'en')
    d_de = data.get("description_de") or auto_translate(desc_raw, 'de')

    # 3. Создание объекта
    new_vacancy = Vacancy(
        title_en=t_en,
        title_de=t_de,
        description_en=d_en,
        description_de=d_de,
        company=company,
        department_id=dept_id
    )

    # 4. Безопасное сохранение в БД
    try:
        db.session.add(new_vacancy)
        db.session.commit()
        return jsonify({"message": "Vacancy created successfully with auto-translation"}), 201
    except Exception as e:
        db.session.rollback() # Откатываем базу, если что-то пошло не так (например, нет такого dept_id)
        print(f"Database error: {e}")
        return jsonify({"message": "Database error", "error": str(e)}), 500