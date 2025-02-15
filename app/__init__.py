# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__)
    app = Flask(__name__)
    CORS(app)  # Cela permet à tous les domaines d'accéder à l'API

    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'

    # Configuration de la base de données PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_db_jgkv_user:9YyoKlzJNcdLJ82I9OcUpuqPhif0M9cl@dpg-cuntmudsvqrc739905v0-a.oregon-postgres.render.com/flask_db_jgkv'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_cle_secrete')


    # Charger la configuration
    if config_class is None:
        from app.config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # Permettre l'accès à tous les domaines

    # Importer et enregistrer les Blueprints
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')

    # Vous pouvez ajouter d'autres initialisations ici (ex. création de dossiers d'upload)
    return app