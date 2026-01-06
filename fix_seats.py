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
    # Cleanup test seat
    Seat.query.filter_by(row_label='X', seat_number=999).delete()
    db.session.commit()

    venues = Venue.query.all()
    print(f"Found {len(venues)} venues.")
    
    for venue in venues:
        current_seats = Seat.query.filter_by(venue_id=venue.id).count()
        if current_seats == 0:
            print(f"Generating seats for Venue '{venue.name}' (ID: {venue.id}, Capacity: {venue.capacity} Type: {type(venue.capacity)})...")
            
            try:
                capacity = int(venue.capacity) if venue.capacity else 0
                if capacity <= 0:
                    print("Skipping due to invalid capacity.")
                    continue
                    
                rows = int(capacity / 10) + 1
                seat_count = 0
                created = 0
                
                # Check for existing seats again to be safe
                existing = set((s.row_label, s.seat_number) for s in Seat.query.filter_by(venue_id=venue.id).all())

                for r in range(rows):
                    row_label = chr(65 + r) # A, B, C...
                    for n in range(1, 11):
                        if seat_count >= capacity: break
                        
                        if (row_label, n) not in existing:
                            seat = Seat(venue_id=venue.id, row_label=row_label, seat_number=n)
                            db.session.add(seat)
                            created += 1
                        
                        seat_count += 1
                
                db.session.commit()
                print(f"Successfully created {created} seats for venue {venue.id}.")
            except Exception as e:
                print(f"Error creating seats for venue {venue.id}: {e}")
                traceback.print_exc()
                db.session.rollback()
        else:
            print(f"Venue '{venue.name}' (ID: {venue.id}) already has {current_seats} seats.")
