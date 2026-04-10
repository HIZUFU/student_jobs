from flask import request, session

def get_lang():
    lang = session.get('lang') or request.headers.get("Accept-Language", "ru")[:2]
    return lang if lang in ["ru", "en", "de"] else "ru"

def localize_vacancy(vacancy):
    lang = get_lang()
    
    if lang == "de":
        title = vacancy.title_de or vacancy.title_ru
        desc = vacancy.description_de or vacancy.description_ru
    elif lang == "en":
        title = vacancy.title_en or vacancy.title_ru
        desc = vacancy.description_en or vacancy.description_ru
    else: # 'ru'
        title = vacancy.title_ru
        desc = vacancy.description_ru

    return {
        "id": vacancy.id,
        "title": title,
        "description": desc,
        "company": vacancy.company
    }