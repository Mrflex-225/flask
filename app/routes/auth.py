# app/routes/auth.py
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from jwt import encode
import datetime, os

from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    sexe = request.form.get('sexe')
    age = request.form.get('age')

    if not username or not password or not first_name or not last_name or not email:
        return jsonify({'message': 'Tous les champs requis ne sont pas fournis'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Nom d\'utilisateur déjà pris!'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email déjà utilisé!'}), 400

    profile_picture = None
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            profile_picture = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(profile_picture)

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        password_hash=hashed_password,
        first_name=first_name,
        last_name=last_name,
        email=email,
        sexe=sexe,
        age=age,
        profile_picture=profile_picture
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Inscription réussie!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'Nom d\'utilisateur non trouvé!'}), 404

    if not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Mot de passe incorrect!'}), 401

    token = encode({
        'username': username,
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token, 'user_id': user.id, 'message': 'Connexion réussie'}), 200

@auth_bp.route('/user_profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = db.session.get(User, user_id)
    if user:
        profile_picture_url = f"http://192.168.1.111:5000/api/user_profile_picture/{os.path.basename(user.profile_picture)}" if user.profile_picture else None
        return jsonify({
            'username': user.username,
            'profile_picture': profile_picture_url
        })
    else:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404

@auth_bp.route('/user_profile_picture/<filename>', methods=['GET'])
def get_profile_picture(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)