from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('customer/index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/events/<int:event_id>')
def event_details(event_id):
    return render_template('customer/event_details.html', event_id=event_id)

@main_bp.route('/my-bookings')
def my_bookings_page():
     return render_template('customer/my_bookings.html')

@main_bp.route('/login')
def login():
    return render_template('auth/login.html')

@main_bp.route('/register')
def register():
    return render_template('auth/register.html')

@main_bp.route('/organizer/dashboard')
def organizer_dashboard():
    return render_template('organizer/dashboard.html')

@main_bp.route('/organizer/create-venue')
def create_venue_page():
    return render_template('organizer/create_venue.html')

@main_bp.route('/organizer/create-event')
def create_event_page():
    return render_template('organizer/create_event.html')

@main_bp.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')
