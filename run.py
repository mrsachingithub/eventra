from dotenv import load_dotenv

# Load env vars before importing app, so Config class gets them
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
