from flask import Blueprint, jsonify
from app.models.vacancy import Vacancy
from app.utils.localization import localize_vacancy

vacancy_bp = Blueprint("vacancy", __name__)

@vacancy_bp.route("/vacancies", methods=["GET"])
def get_vacancies():
    vacancies = Vacancy.query.all()

    result = [localize_vacancy(v) for v in vacancies]

    return jsonify(result)