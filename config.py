import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mediscan-super-secret-key-2026'
    
    # Storage settings
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    REPORTS_FOLDER = os.path.join(basedir, 'generated_reports')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB upload max limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm'}
    
    # Cloud Storage Bucket Settings (AWS S3 / Supabase / GCP Storage)
    CLOUD_STORAGE_ENABLED = os.environ.get('CLOUD_STORAGE_ENABLED', 'True').lower() in ('true', '1', 't')
    CLOUD_PROVIDER = os.environ.get('CLOUD_PROVIDER', 'AWS_S3_ENCRYPTED')
    CLOUD_BUCKET_NAME = os.environ.get('CLOUD_BUCKET_NAME', 'mediscan-cloud-vault')
    
    # Database Configuration: Cloud DB (Supabase / Postgres / MySQL / RDS) with SQLite local fallback
    DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('CLOUD_DB_URI')
    USE_MYSQL = os.environ.get('USE_MYSQL', 'False').lower() in ('true', '1', 't')
    
    if DATABASE_URL:
        # Fix legacy postgres:// scheme for SQLAlchemy compatibility if needed
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif USE_MYSQL:
        DB_USER = os.environ.get('DATABASE_USER', 'root')
        DB_PASS = os.environ.get('DATABASE_PASSWORD', '')
        DB_HOST = os.environ.get('DATABASE_HOST', 'localhost')
        DB_PORT = os.environ.get('DATABASE_PORT', '3306')
        DB_NAME = os.environ.get('DATABASE_NAME', 'mediscan_db')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        db_path = os.path.join(basedir, 'mediscan.db')
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI settings
    MODEL_VERSION = os.environ.get('MODEL_VERSION', 'v1.2.0-resnet50-fusion')
    
    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
