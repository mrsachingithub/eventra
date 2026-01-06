# Eventra - Event Ticket Booking System

Eventra is a modern, full-featured web application for managing and booking event tickets. It provides a seamless experience for customers to discover and book events, organizers to manage their listings and track analytics, and administrators to oversee the entire platform.

## 🌟 Features

### 👤 Customer
- **Browse Events**: View upcoming events with details like date, venue, and pricing.
- **Seat Selection**: Interactive seat map to view availability and select specific seats.
- **Secure Booking**: Two-step booking process with seat locking to prevent double bookings.
- **Booking History**: View past and upcoming bookings with QR code placeholders.
- **Responsive UI**: A premium, dark-themed interface that works across devices.

### 🎭 Event Organizer
- **Dashboard**: Centralized hub to manage events and venues.
- **Create Venues**: Add new venues with capacity and location details.
- **Create Events**: Schedule events, set prices, and link them to venues.
- **Analytics**: Real-time insights on ticket sales, revenue, and capacity utilization per event.
- **Event Management**: Cancel or reactivate events as needed.
- **Global Stats**: Overview of total events, total tickets sold, and total revenue across all events.

### 🛡️ Admin
- **System Dashboard**: High-level view of total users, events, and platform revenue.
- **User Management**: View all users and manage roles (promote to Organizer/Admin, demote to Customer).
- **Event Oversight**: Monitor all events and suspend those violating policies.
- **Platform Control**: Ensure the integrity and quality of the marketplace.

## 🛠️ Technology Stack
- **Backend**: Python (Flask), SQLAlchemy (SQLite)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: SQLite (Development)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd event-ticket-system
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Setup**
    Create a `.env` file in the root directory (or rename `.env.example` if available) and add:
    ```ini
    SECRET_KEY=your_secret_key_here
    JWT_SECRET_KEY=your_jwt_secret_key_here
    DATABASE_URL=sqlite:///site.db
    ```

5.  **Initialize Database**
    Run the setup script to create tables and seed initial data (if configured):
    ```bash
    python database_setup.py
    ```

### Running the Application

1.  **Start the Server**
    ```bash
    python run.py
    ```

2.  **Access the App**
    Open your browser and navigate to `http://localhost:5000`.

## 📂 Project Structure

```
event-ticket-system/
├── app/
│   ├── models.py           # Database models
│   ├── routes/             # API and page routes
│   ├── static/             # CSS, JS, Images
│   └── templates/          # HTML templates
├── instance/               # SQLite database file
├── database_setup.py       # Database initialization script
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

---
© 2026 Eventra. All rights reserved.

## ☁️ Deployment (Render)

This project includes configuration for one-click deployment on Render.

1.  **Push to GitHub/GitLab**: Ensure your code is in a remote repository.
2.  **Create Blueprint**:
    - Go to your Render Dashboard.
    - Click **New +** and select **Blueprint**.
    - Connect your repository.
    - Render will automatically detect `render.yaml` and prompt you to apply the configuration.
3.  **Approve**: Click "Apply" to start the deployment. Render will build the app and create the database automatically.

