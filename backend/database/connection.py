import mysql.connector
from config import config

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=config.DB_PORT
    )

def init_db():
    """Just test the connection - no table creation"""
    try:
        conn = get_db_connection()
        print("✅ Database connection successful - using existing tables")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise e