from flask import Blueprint, flash, render_template, request, redirect, session
from app.models.user import User
from app.extensions import db
from app.models.application import Application
from app.models.vacancy import Vacancy

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
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        
        name_parts = new_user.name.split()
        if len(name_parts) >= 1:
            session['user_name'] = f"{name_parts[0]}. {name_parts[1][0]}"
        else:
            session['user_name'] = new_user.name
        session['role'] = new_user.role

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

    if role == 'student':
        # Студент видит свои отклики
        applications = Application.query.filter_by(student_id=user_id).all()
        return render_template('dashboard.html', applications=applications, role=role)
    
    elif role == 'organization':
        # Работодатель видит свои вакансии и тех, кто на них откликнулся
        my_vacancies = Vacancy.query.filter_by(author_id=user_id).all()
        return render_template('dashboard.html', vacancies=my_vacancies, role=role)