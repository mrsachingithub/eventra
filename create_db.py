import mysql.connector
import os

def create_db():
    try:
        # Connect to MySQL server
        db = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="sachin7632"
        )
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS eventra_db")
        print("Database 'eventra_db' created or already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == '__main__':
    create_db()
