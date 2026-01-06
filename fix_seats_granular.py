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
    venues = Venue.query.all()
    for venue in venues:
        current_seats = Seat.query.filter_by(venue_id=venue.id).count()
        if current_seats == 0:
            print(f"Generating seats for Venue '{venue.name}' (ID: {venue.id})...")
            
            capacity = int(venue.capacity) if venue.capacity else 0
            if capacity <= 0: continue
            
            rows = int(capacity / 10) + 1
            seat_count = 0
            
            for r in range(rows):
                row_label = chr(65 + r)
                for n in range(1, 11):
                    if seat_count >= capacity: break
                    
                    try:
                        seat = Seat(venue_id=venue.id, row_label=row_label, seat_number=n)
                        db.session.add(seat)
                        db.session.commit()
                        print(f"Added {row_label}{n}")
                    except Exception as e:
                        print(f"Failed to add {row_label}{n}: {e}")
                        db.session.rollback()
                        
                    seat_count += 1
