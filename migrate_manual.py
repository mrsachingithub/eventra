from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column exists
        with db.engine.connect() as conn:
            # SQLite specific check (assuming standard setup, but could be Postgres on Render, checking local which is likely SQLite or Postgres)
            # Generic add column
            conn.execute(text("ALTER TABLE bookings ADD COLUMN expires_at TIMESTAMP"))
            conn.commit()
            print("Added expires_at column")
    except Exception as e:
        print(f"Migration might have failed or column exists: {e}")
