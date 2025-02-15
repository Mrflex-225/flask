from jwt import encode
import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
import os
from dotenv import load_dotenv


load_dotenv()  # Charge les variables d'environnement depuis .env

app = Flask(__name__)

# Configuration de la base de donnees PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/flask_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from dotenv import load_dotenv

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_cle_secrete')

db = SQLAlchemy(app)
# Créer la base de données et les tables si nécessaire
with app.app_context():
    db.create_all()  # Crée toutes les tables définies par les modèles
    print("Les tables ont été créées avec succès.")

# Modèle d'utilisateur pour la base de donnees
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000), unique=True, nullable=False)
    password_hash = db.Column(db.String(1000), nullable=False)
    first_name = db.Column(db.String(1000), nullable=False)
    last_name = db.Column(db.String(1000), nullable=False)
    email = db.Column(db.String(1000), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Creer les tables dans la base de donnees
@app.before_request
def create_tables():
    db.create_all()


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Aucune donnée JSON reçue'}), 400
    print(data)  # Cela affichera les données dans le terminal de Flask

    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')

    # Verifie si l'utilisateur existe deja
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Nom d\'utilisateur deja pris!'}), 400

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({'message': 'Email deja utilise!'}), 400

    # Hashage du mot de passe
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Creer un nouvel utilisateur dans la base de donnees
    new_user = User(
        username=username, 
        password_hash=password,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Inscription reussie!'}), 201

@app.route('/api/test_db_connection', methods=['GET'])
def test_db_connection():
    try:
        # Essayer une requête simple
        result = db.session.execute('SELECT 1')
        return jsonify({'message': 'Connexion à la base de données réussie!'})
    except Exception as e:
        return jsonify({'message': f'Erreur de connexion à la base de données : {str(e)}'}), 500



@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    print(f"Tentative de connexion pour l'utilisateur: {username}")  # Log

    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"Utilisateur non trouvé: {username}")  # Log
        return jsonify({'message': 'Nom d\'utilisateur non trouvé!'}), 404

    # Vérification simple du mot de passe
    if password == user.password_hash:  # Comparaison directe
        # Génération du token JWT
        token = encode({
            'username': username,
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        print(f"Token généré pour l'utilisateur {username}: {token[:20]}...")  # Log (ne pas afficher le token complet pour des raisons de sécurité)
        
        # Retourne le token dans la réponse
        return jsonify({'token': token, 'message': 'Connexion réussie'}), 200
    else:
        print(f"Mot de passe incorrect pour l'utilisateur: {username}")  # Log
        return jsonify({'message': 'Mot de passe incorrect!'}), 401


# Exemple de route protegee (requiert un token)
@app.route('/api/protected', methods=['GET'])
def protected_route():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token manquant!'}), 403

    try:
        token = token.split(" ")[1]  # Recupère le token après "Bearer "
        # Decodage du token et verification
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        current_user = data['username']
        return jsonify({'message': f'Bienvenue {current_user}, vous avez accès a cette route protegee!'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Le token a expire!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token invalide!'}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
