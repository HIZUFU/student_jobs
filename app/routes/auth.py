from flask import Blueprint, flash, render_template, request, redirect, session
from app.models.user import User
from app.extensions import db
from app.models.application import Application
from app.models.vacancy import Vacancy
from app.models.user import User, StudentProfile, EmployerProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['company_name'] = user.employer_profile.company_name if user.role == 'organization' else None
            session['role'] = user.role
            flash("Вы успешно вошли!", "success")
            return redirect('/')
        else:
            flash("Неверный email или пароль.", "danger")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Вы вышли из системы.", "info")
    return redirect('/')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        
        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует.", "danger")
            return render_template('register.html')
        new_user = User(name=username, email=email, role=role)
        new_user.set_password(password)

        if role == 'organization':
            company_name = request.form.get('company_name', 'Без названия')
            new_user.employer_profile = EmployerProfile(company_name=company_name)
        else:
            new_user.student_profile = StudentProfile(
                university="",
                group_name=""
            )

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['role'] = new_user.role
        
        name_parts = new_user.name.split()
        if len(name_parts) >= 2:
            session['user_name'] = f"{name_parts[0]} {name_parts[1][0]}."
        else:
            session['user_name'] = new_user.name

        flash("Добро пожаловать!", "success")
        return redirect('/')
        
    return render_template('register.html')

@auth_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в систему.", "warning")
        return redirect('/login')

    user_id = session['user_id']
    role = session.get('role')
    user = User.query.get(user_id)

    if role == 'student':
        applications = Application.query.filter_by(student_id=user_id).all()
        invitations = [app for app in applications if app.status_id == 2]
        
        return render_template('dashboard.html', 
                               applications=applications, 
                               invitations=invitations, 
                               role=role, 
                               user=user)
    
    elif role == 'organization':
        my_vacancies = Vacancy.query.filter_by(author_id=user_id).all()
        return render_template('dashboard.html', vacancies=my_vacancies, role=role, user=user)
    
@auth_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        if user.role == 'student':
            # Получаем объект профиля
            profile = user.student_profile
            
            # Сохраняем ВУЗ и другие поля из формы
            profile.university = request.form.get('university')
            profile.group_name = request.form.get('group_name')
            profile.phone = request.form.get('phone')
            profile.address = request.form.get('address')
            profile.experience = request.form.get('experience')
            profile.desired_employment_type = request.form.get('employment_type')
        
        elif user.role == 'organization':
            # Логика для организации (название, ИНН и т.д.)
            profile = user.employer_profile
            profile.company_name = request.form.get('company_name')
            profile.inn = request.form.get('inn')
            # ... остальные поля ...

        db.session.commit()
        flash("Профиль успешно обновлен!", "success")
        return redirect('/dashboard')

    return render_template('edit_profile.html', user=user)