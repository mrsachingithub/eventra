import mysql.connector
import os
from app import create_app, db
from app.models import User, Venue, Seat, Event, Booking, Ticket, Payment
from config import Config

# Database Configuration
DB_HOST = "127.0.0.1"
DB_USER = "root" 
DB_PASSWORD = "sachin7632"
DB_NAME = "eventra_db"

def setup_database():
    print("--- Starting Database Setup ---")
    
    # 1. Connect to MySQL Server to create the DB
    try:
        print(f"Connecting to MySQL at {DB_HOST} as {DB_USER}...")
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        print(f"Creating database '{DB_NAME}' if it doesn't exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print("Database created/verified.")
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return

    # 2. Create Tables
    print("Initializing Flask App to create tables...")
    
    # Create a temporary config class to force the correct DB URI
    class SetupConfig(Config):
        SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pass the config class to create_app
    app = create_app(config_class=SetupConfig)
    
    with app.app_context():
        try:
            print("Creating all tables defined in models...")
            db.create_all()
            print("Tables created successfully!")
            print("Setup Complete.")
        except Exception as e:
            print(f"Error creating tables: {e}")

if __name__ == "__main__":
    setup_database()
