# backend/database.py
import mysql.connector
from mysql.connector import pooling

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "write your own password",
    "database": "investment_advisor",
    "autocommit": True
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="investment_pool",
    pool_size=5,
    pool_reset_session=True,
    **DB_CONFIG
)

def get_connection():
    return connection_pool.get_connection()

def execute_query(query, params=None, fetch=False, fetch_one=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)  # ← buffered=True fixes unread result
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        elif fetch_one:
            result = cursor.fetchone()
            return result
        else:
            return cursor.lastrowid
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

def init_database():
    """Verify connection works"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT 1")
        cursor.fetchall()  # ← consume result
        cursor.close()
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise e