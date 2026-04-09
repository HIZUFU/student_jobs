from app import create_app
from app.extensions import db
from app.models.application import ApplicationStatus

app = create_app()

with app.app_context():
    required_statuses = [
        {'id': 1, 'status_ru': 'На рассмотрении', 'status_en': 'Pending', 'status_de': 'In Bearbeitung'},
        {'id': 2, 'status_ru': 'Принято', 'status_en': 'Accepted', 'status_de': 'Akzeptiert'},
        {'id': 3, 'status_ru': 'Отказ', 'status_en': 'Rejected', 'status_de': 'Abgelehnt'},
        {'id': 4, 'status_ru': 'Черновик', 'status_en': 'Draft', 'status_de': 'Entwurf'}
    ]

    added = False
    for s_data in required_statuses:
        existing_status = ApplicationStatus.query.get(s_data['id'])
        if not existing_status:
            new_status = ApplicationStatus(**s_data)
            db.session.add(new_status)
            added = True
            print(f"Добавлен статус: {s_data['status_ru']}")

    if added:
        db.session.commit()
        print("База статусов успешно обновлена!")
    else:
        print("Все 4 статуса уже существуют в базе. Ничего не изменено.")