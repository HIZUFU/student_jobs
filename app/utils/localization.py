from flask import request

def get_lang():
    lang = request.headers.get("Accept-Language", "en")
    return lang if lang in ["en", "de"] else "en"


def localize_vacancy(vacancy):
    lang = get_lang()

    if lang == "de":
        return {
            "id": vacancy.id,
            "title": vacancy.title_de,
            "description": vacancy.description_de,
            "company": vacancy.company
        }

    return {
        "id": vacancy.id,
        "title": vacancy.title_en,
        "description": vacancy.description_en,
        "company": vacancy.company
    }