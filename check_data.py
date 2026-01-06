import sys
import os
sys.path.append(os.getcwd())

from app import create_app, db
from app.models import User, Venue, Seat, Event
from config import Config

class SetupConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Hardcode DB URI as seen in database_setup.py
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:sachin7632@127.0.0.1/eventra_db"

app = create_app(config_class=SetupConfig)

with app.app_context():
    print(f"Users: {User.query.count()}")
    print(f"Venues: {Venue.query.count()}")
    print(f"Seats: {Seat.query.count()}")
    print(f"Events: {Event.query.count()}")
    
    events = Event.query.all()
    for e in events:
        seat_count = Seat.query.filter_by(venue_id=e.venue_id).count()
        print(f"Event '{e.title}' (ID: {e.id}) - Venue ID: {e.venue_id} - Seats: {seat_count}")
