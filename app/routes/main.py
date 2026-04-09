from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    """Главная страница со списком вакансий"""
    return render_template("index.html")

@main_bp.route("/add-vacancy")
def add_vacancy():
    """Страница с формой добавления вакансии для работодателей"""
    return render_template("add_vacancy.html")