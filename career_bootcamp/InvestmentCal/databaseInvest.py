import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('INVESTMENT_DB_NAME', 'investment_db'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}


if not DB_CONFIG['password']:
    raise ValueError("DB_PASSWORD not found in environment variables! Check your .env file.")

def get_connection():
    """Create database connection"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.Error as e:
        print(f"Database connection failed: {e}")
        raise


@contextmanager
def get_db():
    """Context manager for database operations"""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


def test_connection():
    """Test if database connection works"""
    try:
        with get_db() as db:
            db.execute("SELECT 1")
            print("✅ Database connection successful!")
            print(f"Connected to: {DB_CONFIG['database']} as {DB_CONFIG['user']}")
            return True
    except Exception as e:
        print(f" Database connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()