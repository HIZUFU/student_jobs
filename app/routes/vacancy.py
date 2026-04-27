from flask import Blueprint, flash, render_template, request, redirect, session
from app.models.department import Department
from app.models.vacancy import Vacancy
from app.models.application import Application
from app.extensions import db
from deep_translator import GoogleTranslator

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
    
    existing_app = Application.query.filter_by(
        vacancy_id=vacancy_id, 
        student_id=session['user_id']
    ).first()

    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter', '')
        action = request.form.get('action')
        
        status_id = 4 if action == 'draft' else 1 

        if existing_app:
            if existing_app.status_id != 4 and action == 'send':
                flash("Вы уже отправили отклик на эту вакансию.", "warning")
                return redirect('/dashboard')
                
            existing_app.cover_letter = cover_letter
            existing_app.status_id = status_id
        else:
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
    
    if session.get('role') != 'organization':
        flash("Только организации могут публиковать вакансии.", "danger")
        return redirect('/')
    
    if request.method == 'POST':
        title_ru = request.form['title']
        company = session.get('company_name') or session.get('user_name') # Берем название компании из сессии
        
        salary_from_raw = request.form.get('salary_from')
        salary_to_raw = request.form.get('salary_to')
        employment_type = request.form.get('employment_type', '')
        is_internship = True if request.form.get('is_internship') == 'yes' else False
        salary_from = int(salary_from_raw) if salary_from_raw and salary_from_raw.isdigit() else None
        salary_to = int(salary_to_raw) if salary_to_raw and salary_to_raw.isdigit() else None
        
        dept_input = request.form.get('department_id')
        if not dept_input:
            flash("Пожалуйста, выберите кафедру или направление.", "danger")
            departments = Department.query.all()
            return render_template('add_vacancy.html', departments=departments)

        description_ru = request.form.get('description', '')
        len_description = len(description_ru)
        if len_description < 100:
            flash(f"Описание слишком короткое. Вы написали {len_description} символов, а нужно минимум 100.", "danger")
            departments = Department.query.all()
            return render_template('add_vacancy.html', departments=departments)

        if str(dept_input).isdigit():
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

        try:
            t_en = GoogleTranslator(source='auto', target='en').translate(title_ru)
            t_de = GoogleTranslator(source='auto', target='de').translate(title_ru)
            desc_en = GoogleTranslator(source='auto', target='en').translate(description_ru)
            desc_de = GoogleTranslator(source='auto', target='de').translate(description_ru)
        except:
            t_en, t_de = title_ru, title_ru
            desc_en, desc_de = description_ru, description_ru

        new_vacancy = Vacancy(
            title_ru=title_ru, 
            title_en=t_en, 
            title_de=t_de, 
            description_ru=description_ru,
            description_en=desc_en,
            description_de=desc_de,
            company=company,
            department_id=final_dept_id,
            author_id=session.get('user_id'),
            salary_from=salary_from,
            salary_to=salary_to,
            employment_type=employment_type,
            is_internship=is_internship
        )
        
        db.session.add(new_vacancy)
        db.session.commit()
        flash("Вакансия успешно опубликована!", "success")
        return redirect('/')
        
    departments = Department.query.all()
    return render_template('add_vacancy.html', departments=departments)

@vacancy_bp.route('/delete/<int:id>')
def delete_vacancy(id):
    if session.get('role') != 'organization':
        flash("У вас нет прав для удаления вакансий.", "danger")
        return redirect('/')
        
    vacancy = Vacancy.query.get_or_404(id)
    if vacancy.author_id != session.get('user_id'):
        flash("Вы не можете удалить чужую вакансию.", "danger")
        return redirect('/')

    # Сначала удаляем все отклики
    Application.query.filter_by(vacancy_id=id).delete()

    db.session.delete(vacancy)
    db.session.commit()
    
    flash("Вакансия удалена.", "success")
    return redirect('/')

@vacancy_bp.route('/update/<int:id>', methods=['GET', 'POST'])
def update_vacancy(id):
    vacancy = Vacancy.query.get_or_404(id)
    
    # 1. ЗАЩИТА: Блокируем доступ к странице редактирования чужим пользователям
    if 'user_id' not in session or session.get('role') != 'organization':
        flash("У вас нет прав для редактирования вакансий.", "danger")
        return redirect('/')
        
    if vacancy.author_id != session.get('user_id'):
        flash("Вы не можете редактировать чужую вакансию.", "danger")
        return redirect(f'/vacancy/{id}')

    # 2. ОБРАБОТКА ДАННЫХ ПРИ СОХРАНЕНИИ
    if request.method == 'POST':
        title_ru = request.form.get('title')
        description_ru = request.form.get('description')
        dept_input = request.form.get('department_id')
        
        # Обновляем Кафедру/Направление
        if dept_input:
            if str(dept_input).isdigit():
                vacancy.department_id = int(dept_input)
            else:
                existing_dept = Department.query.filter_by(name_ru=dept_input).first()
                if existing_dept:
                    vacancy.department_id = existing_dept.id
                else:
                    try:
                        dept_en = GoogleTranslator(source='auto', target='en').translate(dept_input)
                        dept_de = GoogleTranslator(source='auto', target='de').translate(dept_input)
                    except:
                        dept_en, dept_de = dept_input, dept_input

                    new_dept = Department(name_ru=dept_input, name_en=dept_en, name_de=dept_de)
                    db.session.add(new_dept)
                    db.session.commit()
                    vacancy.department_id = new_dept.id

        # Обновляем Название и переводим
        if title_ru:
            vacancy.title_ru = title_ru
            try:
                vacancy.title_en = GoogleTranslator(source='auto', target='en').translate(title_ru)
                vacancy.title_de = GoogleTranslator(source='auto', target='de').translate(title_ru)
            except:
                pass

        # Обновляем Описание и переводим
        if description_ru:
            vacancy.description_ru = description_ru
            try:
                vacancy.description_en = GoogleTranslator(source='auto', target='en').translate(description_ru)
                vacancy.description_de = GoogleTranslator(source='auto', target='de').translate(description_ru)
            except:
                pass

        db.session.commit()
        flash("Вакансия успешно обновлена.", "success")
        return redirect(f'/vacancy/{vacancy.id}') # После успеха отправляем обратно на карточку вакансии
        
    # Загружаем список всех кафедр, чтобы форма работала корректно
    departments = Department.query.all()
    return render_template('edit_vacancy.html', vacancy=vacancy, departments=departments)

@vacancy_bp.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['ru', 'en', 'de']: 
        session['lang'] = lang
    return redirect(request.referrer or '/')

@vacancy_bp.route('/vacancy/<int:id>')
def vacancy_detail(id):
    vacancy = Vacancy.query.get_or_404(id)
    return render_template('vacancy_detail.html', vacancy=vacancy)