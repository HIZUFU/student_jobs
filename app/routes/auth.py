from flask import Blueprint, current_app, request, jsonify
from app.models.user import User
from app.extensions import db
import werkzeug.security

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"message": "Email and password are required"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User with this email already exists"}), 400

    new_user = User(
        name=data.get('username'), 
        email=data['email'],
        role=data.get('role', 'student')
    )
    
    new_user.set_password(data['password'])

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": "User created and logged in",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "role": new_user.role
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Database error: {e}")
        return jsonify({"message": "Registration failed", "error": str(e)}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing credentials"}), 400
    
    user = User.query.filter_by(email=data.get('email')).first()

    if user and werkzeug.security.check_password_hash(user.password_hash, data.get('password')):
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id, 
                "name": user.name,
                "role": user.role
            }
        }), 200
    
    return jsonify({"message": "Invalid email or password"}), 401