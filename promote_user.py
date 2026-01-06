from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import User
import sys

app = create_app()

def promote(username, role='organizer'):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.role = role
            db.session.commit()
            print(f"Promoted {username} to {role}")
        else:
            print(f"User {username} not found")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        promote(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        promote(sys.argv[1])
