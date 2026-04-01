from flask import Blueprint, jsonify, request
from app.models.vacancy import Vacancy
from app.extensions import db
from app.utils.localization import localize_vacancy

vacancy_bp = Blueprint("vacancy", __name__)

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
    """
    Create a new vacancy with translations
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Vacancy
          required:
            - title_en
            - title_de
            - company
          properties:
            title_en:
              type: string
              example: "Python Developer Intern"
            title_de:
              type: string
              example: "Python-Entwickler Praktikant"
            description_en:
              type: string
              example: "Work with FastAPI and Postgres"
            description_de:
              type: string
              example: "Arbeiten Sie mit FastAPI und Postgres"
            company:
              type: string
              example: "RTF Lab"
    responses:
      201:
        description: Vacancy created successfully
    """
    data = request.get_json()

    new_vacancy = Vacancy(
        title_en=data.get("title_en"),
        title_de=data.get("title_de"),
        description_en=data.get("description_en"),
        description_de=data.get("description_de"),
        company=data.get("company")
    )

    db.session.add(new_vacancy)
    db.session.commit()

    return jsonify({"message": "Vacancy created"}), 201