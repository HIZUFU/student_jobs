from flask import Blueprint, jsonify, request

from app.extensions import db
from app.utils.localization import localize_vacancy

vacancy_bp = Blueprint("vacancy", __name__)

@vacancy_bp.route("/vacancies", methods=["GET"])
def get_vacancies():
    vacancies = Vacancy.query.all()
    result = [localize_vacancy(v) for v in vacancies]
    return jsonify(result)


@vacancy_bp.route("/vacancies", methods=["POST"])
def create_vacancy():
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