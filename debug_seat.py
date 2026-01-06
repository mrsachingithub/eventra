import sys
import os
import traceback
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import Venue, Seat
from config import Config

class SetupConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:sachin7632@127.0.0.1/eventra_db"

app = create_app(config_class=SetupConfig)

with app.app_context():
    try:
        venue = Venue.query.first()
        if venue:
            print(f"Adding 1 seat to venue {venue.id}...")
            seat = Seat(venue_id=venue.id, row_label='X', seat_number=999, seat_type='Regular', price_multiplier=1.0)
            db.session.add(seat)
            db.session.commit()
            print("Success!")
        else:
            print("No venue found.")
    except Exception:
        traceback.print_exc()
