import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_conn():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "classicmodels"),
            user=os.getenv("POSTGRES_USER", "app_user"),
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
            host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
            port=os.getenv("POSTGRES_PORT", "5433")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productlines;")
        count = cursor.fetchone()[0]
        print(f"[+] Successfully connected! Number of product lines in database: {count}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[!] Connection failed: {e}")

if __name__ == "__main__":
    test_conn()
