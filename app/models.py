# app/models.py
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000), unique=True, nullable=False)
    password_hash = db.Column(db.String(1000), nullable=False)
    first_name = db.Column(db.String(1000), nullable=False)
    last_name = db.Column(db.String(1000), nullable=False)
    email = db.Column(db.String(1000), unique=True, nullable=False)
    sexe = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    profile_picture = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    idProduit = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    categorie = db.Column(db.String(2000), nullable=True)
    qr_code = db.Column(db.String(1000), unique=True, nullable=False)
    poids = db.Column(db.Integer, nullable=True)
    volume = db.Column(db.Integer, nullable=True)

class Possede(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quantite = db.Column(db.Integer, nullable=False)
    date_peremption = db.Column(db.Date, nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    id_utilisateur = db.Column(db.Integer, nullable=False)
    id_produit = db.Column(db.Integer, nullable=False)

class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)