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
    'database': os.getenv('LIBRARY_DB_NAME', 'library_db'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

if not DB_CONFIG['password']:
    raise ValueError("DB_PASSWORD not found! Check .env file")

# ... rest of code

def get_connection():

    return pymysql.connect(**DB_CONFIG)


@contextmanager
def get_db():

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

    try:
        with get_db() as db:
            db.execute("SELECT 1")
            result = db.fetchone()
            print("Database connection successful")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()