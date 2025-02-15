# app/config.py
import os
from dotenv import load_dotenv
import psycopg2


load_dotenv()



class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default_cle_secrete')
    SQLALCHEMY_DATABASE_URI =os.getenv("DATABASE_URL", "postgresql://flask_db_jgkv_user:9YyoKlzJNcdLJ82I9OcUpuqPhif0M9cl@dpg-cuntmudsvqrc739905v0-a.oregon-postgres.render.com/flask_db_jgkv")    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'profile_pics')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}