from flask import Blueprint, flash, render_template, request, redirect, session
from app.models.department import Department
from app.models.vacancy import Vacancy
from app.models.application import Application
from app.extensions import db
from deep_translator import GoogleTranslator
from app.models.application import ApplicationStatus

vacancy_bp = Blueprint('vacancy', __name__)

@vacancy_bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        vacancies = Vacancy.query.filter(
            (Vacancy.title_ru.ilike(f'%{search_query}%')) | 
            (Vacancy.company.ilike(f'%{search_query}%'))
        ).all()
    else:
        vacancies = Vacancy.query.all()
        
    return render_template('index.html', vacancies=vacancies, search_query=search_query)

@vacancy_bp.route('/apply/<int:vacancy_id>', methods=['GET', 'POST'])
def apply_vacancy(vacancy_id):
    if 'user_id' not in session or session.get('role') != 'student':
        flash("Только авторизованные студенты могут откликаться.", "danger")
        return redirect(f'/vacancy/{vacancy_id}')

    vacancy = Vacancy.query.get_or_404(vacancy_id)
    
    # Ищем, есть ли уже отклик (вдруг студент возвращается к черновику)
    existing_app = Application.query.filter_by(
        vacancy_id=vacancy_id, 
        student_id=session['user_id']
    ).first()

    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter', '')
        action = request.form.get('action') # Кнопка 'send' или 'draft'
        
        # 4 - Черновик, 1 - На рассмотрении
        status_id = 4 if action == 'draft' else 1 

        if existing_app:
            # Обновляем существующий черновик
            existing_app.cover_letter = cover_letter
            existing_app.status_id = status_id
        else:
            # Создаем новый отклик
            new_app = Application(
                vacancy_id=vacancy_id,
                student_id=session['user_id'],
                status_id=status_id,
                cover_letter=cover_letter
            )
            db.session.add(new_app)
            
        db.session.commit()
        
        if action == 'draft':
            flash("Отклик сохранен в черновики.", "info")
        else:
            flash("Отклик успешно отправлен работодателю!", "success")
            
        return redirect('/dashboard')
    
    return render_template('apply.html', vacancy=vacancy, existing_app=existing_app)

@vacancy_bp.route('/add', methods=['GET', 'POST'])
def add_vacancy():
    if not session.get('user_id'):
        flash("Пожалуйста, войдите в систему.", "info")
        return redirect('/login')
    
    # Проверка: Является ли он организацией?
    if session.get('role') != 'organization':
        flash("Только организации могут публиковать вакансии.", "danger")
        return redirect('/')
    
    if request.method == 'POST':
        title_ru = request.form['title']
        company = session.get('user_name')
        dept_input = request.form.get('department_id') # Получаем данные из поля департамента
        description_ru = request.form.get('description', '') # Получаем описание из формы
        
        # --- ЖЕСТКАЯ ПРОВЕРКА НА 100 СЛОВ ---
        len_description = len(description_ru)
        if len_description < 100:
            flash(f"Описание слишком короткое. Вы написали {len_description} символов, а нужно минимум 100.", "danger")
            departments = Department.query.all()
            return render_template('add_vacancy.html', departments=departments)

        # --- 1. ОБРАБОТКА И ПЕРЕВОД ДЕПАРТАМЕНТА ---
        if dept_input.isdigit():
            final_dept_id = int(dept_input)
        else:
            existing_dept = Department.query.filter_by(name_ru=dept_input).first()
            if existing_dept:
                final_dept_id = existing_dept.id
            else:
                try:
                    dept_en = GoogleTranslator(source='auto', target='en').translate(dept_input)
                    dept_de = GoogleTranslator(source='auto', target='de').translate(dept_input)
                except:
                    dept_en, dept_de = dept_input, dept_input

                new_dept = Department(name_ru=dept_input, name_en=dept_en, name_de=dept_de)
                db.session.add(new_dept)
                db.session.commit()
                final_dept_id = new_dept.id

        # --- 2. ПЕРЕВОД ВАКАНСИИ И ОПИСАНИЯ ---
        try:
            t_en = GoogleTranslator(source='auto', target='en').translate(title_ru)
            t_de = GoogleTranslator(source='auto', target='de').translate(title_ru)
            
            # Переводим длинный текст описания
            desc_en = GoogleTranslator(source='auto', target='en').translate(description_ru)
            desc_de = GoogleTranslator(source='auto', target='de').translate(description_ru)
        except:
            t_en, t_de = title_ru, title_ru
            desc_en, desc_de = description_ru, description_ru

        # --- 3. СОХРАНЕНИЕ ---
        new_vacancy = Vacancy(
            title_ru=title_ru, 
            title_en=t_en, 
            title_de=t_de, 
            description_ru=description_ru,   # Сохраняем русское описание
            description_en=desc_en,          # Сохраняем английское
            description_de=desc_de,          # Сохраняем немецкое
            company=company,
            department_id=final_dept_id,        
            author_id=session.get('user_id')    
        )
        
        db.session.add(new_vacancy)
        db.session.commit()
        flash("Вакансия успешно опубликована!", "success")
        return redirect('/')
        
    departments = Department.query.all()
    return render_template('add_vacancy.html', departments=departments)

@vacancy_bp.route('/delete/<int:id>')
def delete_vacancy(id):
    vacancy = Vacancy.query.get_or_404(id)
    db.session.delete(vacancy)
    db.session.commit()
    return redirect('/')

@vacancy_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update_vacancy(id):
    vacancy = Vacancy.query.get_or_404(id)
    if request.method == 'POST':
        if session.get('role') != 'organization':
            flash("У вас нет прав для редактирования вакансий.", "danger")
            return redirect('/')
        else:
            vacancy.title_ru = request.form.get('title')
            vacancy.company = request.form.get('company')
            
            vacancy.title_en = GoogleTranslator(source='auto', target='en').translate(vacancy.title_ru)
            vacancy.title_de = GoogleTranslator(source='auto', target='de').translate(vacancy.title_ru)

            db.session.commit()
            return redirect('/')
    return render_template('edit_vacancy.html', vacancy=vacancy)

@vacancy_bp.route('/set_lang/<lang>')
def set_lang(lang):
    # Разрешаем только те языки, которые поддерживает наш сайт
    if lang in ['ru', 'en', 'de']: 
        session['lang'] = lang
        
    # request.referrer — это магия Flask. Он возвращает URL страницы, 
    # с которой пользователь нажал на кнопку. Если его нет — кидаем на главную ('/').
    return redirect(request.referrer or '/')

@vacancy_bp.route('/vacancy/<int:id>')
def vacancy_detail(id):
    # Ищем вакансию по ID. Если её нет — Flask автоматически выдаст ошибку 404
    vacancy = Vacancy.query.get_or_404(id)
    
    # Передаем найденную вакансию в новый шаблон
    return render_template('vacancy_detail.html', vacancy=vacancy)

@vacancy_bp.route('/change_status/<int:app_id>', methods=['POST'])
def change_status(app_id):
    if session.get('role') != 'organization':
        return redirect('/')

    application = Application.query.get_or_404(app_id)
    
    # Защита: проверяем, что вакансия принадлежит этому работодателю
    if application.vacancy.author_id != session.get('user_id'):
        flash("У вас нет прав!", "danger")
        return redirect('/dashboard')

    new_status_id = request.form.get('status_id')
    if new_status_id:
        application.status_id = int(new_status_id)
        db.session.commit()
        flash("Статус кандидата обновлен.", "success")

    return redirect('/dashboard')