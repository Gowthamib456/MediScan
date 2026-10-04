"""
Database Setup & Connectivity Verification Script for MediScan.
Tests MySQL database connection via SQLAlchemy/PyMySQL, creates the database
if it does not exist, and pings the engine connection.
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

import sqlalchemy
from config import config

def test_database_connection():
    env_mode = os.getenv('FLASK_ENV', 'development')
    app_config = config.get(env_mode, config['default'])
    
    db_user = app_config.DB_USER
    db_password = app_config.DB_PASSWORD
    db_host = app_config.DB_HOST
    db_port = app_config.DB_PORT
    db_name = app_config.DB_NAME
    
    print("\n--------------------------------------------------")
    print("  MediScan MySQL Database Diagnostic & Setup Test  ")
    print("--------------------------------------------------")
    print(f"Target Host : {db_host}:{db_port}")
    print(f"Target DB   : {db_name}")
    print(f"User        : {db_user}")

    # 1. Connect to MySQL server root instance (without specifying target DB)
    server_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}"
    print(f"\nAttempting server connection to {db_host}:{db_port}...")
    
    try:
        server_engine = sqlalchemy.create_engine(server_uri)
        with server_engine.connect() as conn:
            conn.execute(sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
            print(f"SUCCESS: Server connected. Database `{db_name}` verified/created.")
    except Exception as e:
        print(f"WARNING: Server connection failed: {str(e)}")
        print("Note: If MySQL authentication differs, ensure root/password settings match in `.env`.")

    # 2. Test direct connection to target database URI
    target_uri = app_config.SQLALCHEMY_DATABASE_URI
    print(f"\nTesting SQLAlchemy engine URI: {target_uri} ...")
    try:
        engine = sqlalchemy.create_engine(target_uri)
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT VERSION()")).fetchone()
            print(f"SUCCESS: Connected to database `{db_name}`!")
            print(f"MySQL Version: {result[0]}")
            return True
    except Exception as e:
        print(f"ERROR: Target database connection failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_database_connection()
    sys.exit(0 if success else 1)
