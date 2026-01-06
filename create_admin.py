from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import User

def create_admin_user():
    app = create_app()
    with app.app_context():
        username = "admin"
        email = "admin@example.com"
        password = "admin123"
        role = "admin"

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists.")
            # Optional: reset password
            # existing_user.set_password(password)
            # db.session.commit()
            # print(f"Password for '{username}' has been reset to '{password}'.")
        else:
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            print(f"Admin user created successfully.")
            print(f"Username: {username}")
            print(f"Password: {password}")

if __name__ == "__main__":
    create_admin_user()
