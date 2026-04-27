from flask import Blueprint, flash, render_template, request, redirect, session, url_for
from app.models.application import Application, Message
from app.models.vacancy import Vacancy
from app.extensions import db
from sqlalchemy import or_

application_bp = Blueprint('application', __name__)

@application_bp.route('/messages')
@application_bp.route('/messages/<int:active_app_id>')
def all_messages(active_app_id=None):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    role = session.get('role')

    if role == 'student':
        apps = Application.query.filter_by(student_id=user_id).order_by(Application.created_at.desc()).all()
    else:
        apps = Application.query.join(Vacancy).filter(Vacancy.author_id == user_id).order_by(Application.created_at.desc()).all()

    active_chat = None
    if active_app_id:
        active_chat = Application.query.get_or_404(active_app_id)
        if active_chat.student_id != user_id and active_chat.vacancy.author_id != user_id:
            flash("Доступ запрещен", "danger")
            return redirect(url_for('application.all_messages'))

    return render_template('messages_hub.html', apps=apps, active_chat=active_chat)

@application_bp.route('/application/<int:app_id>')
def application_detail(app_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    application = Application.query.get_or_404(app_id)
    user_id = session['user_id']
    role = session.get('role')
    
    is_author = application.vacancy.author_id == user_id
    is_student = application.student_id == user_id

    if not (is_author or is_student):
        flash("У вас нет прав для просмотра этого отклика.", "danger")
        return redirect(url_for('auth.dashboard'))

    return render_template('application_detail.html', app=application, role=role)


@application_bp.route('/change_status/<int:app_id>', methods=['POST'])
def change_status(app_id):
    if session.get('role') != 'organization':
        return redirect('/')

    application = Application.query.get_or_404(app_id)
    if application.vacancy.author_id != session.get('user_id'):
        flash("У вас нет прав!", "danger")
        return redirect(url_for('auth.dashboard'))

    new_status_id = request.form.get('status_id')
    if new_status_id:
        application.status_id = int(new_status_id)
        
        if application.status_id == 2:
            application.interview_time = request.form.get('interview_time')
            application.interview_place = request.form.get('interview_place')
        else:
            application.interview_time = None
            application.interview_place = None
            
        db.session.commit()
        flash("Статус кандидата обновлен.", "success")

    return redirect(request.referrer or url_for('application.application_detail', app_id=app_id))

@application_bp.route('/application/<int:app_id>/message', methods=['POST'])
def send_message(app_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    application = Application.query.get_or_404(app_id)
    user_id = session['user_id']

    if application.student_id != user_id and application.vacancy.author_id != user_id:
        flash("У вас нет прав!", "danger")
        return redirect(url_for('auth.dashboard'))

    text = request.form.get('message_text')
    
    if text and text.strip():
        new_msg = Message(
            application_id=app_id,
            sender_id=user_id,
            text=text.strip()
        )
        db.session.add(new_msg)
        db.session.commit()

    if request.form.get('redirect_to') == 'messenger':
        return redirect(url_for('application.all_messages', active_app_id=app_id))
    
    return redirect(url_for('application.application_detail', app_id=app_id))