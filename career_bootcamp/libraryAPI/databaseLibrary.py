import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '00709710@Mysql',
    'database': 'library_db',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}


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