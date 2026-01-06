from flask import Blueprint, jsonify
from app.models import User, Event, Booking, db
from app.routes.auth import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_stats():
    try:
        user_count = User.query.count()
        event_count = Event.query.count()
        
        # Calculate total revenue from non-cancelled bookings
        # We use func.sum for efficiency
        revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(Booking.status != 'Cancelled').scalar() or 0
        
        return jsonify({
            "users": user_count,
            "events": event_count,
            "revenue": round(revenue, 2)
        }), 200
    except Exception as e:
        print(e)
        return jsonify({"msg": "Error fetching stats"}), 500

# --- User Management ---

@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_all_users():
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role,
        "created_at": u.created_at.isoformat()
    } for u in users]), 200

@admin_bp.route('/users/<int:user_id>/role', methods=['PATCH'])
@role_required('admin')
def update_user_role(user_id):
    from flask import request
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in ['customer', 'organizer', 'admin']:
        return jsonify({"msg": "Invalid role"}), 400
        
    user = User.query.get_or_404(user_id)
    user.role = new_role
    
    try:
        db.session.commit()
        return jsonify({"msg": f"User role updated to {new_role}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500

# --- Event Oversight ---

@admin_bp.route('/events', methods=['GET'])
@role_required('admin')
def get_all_events():
    events = Event.query.all()
    result = []
    
    for e in events:
        organizer = User.query.get(e.organizer_id)
        # Calculate revenue for this event
        revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(
            Booking.event_id == e.id,
            Booking.status != 'Cancelled'
        ).scalar() or 0.0
        
        result.append({
            "id": e.id,
            "title": e.title,
            "organizer": organizer.username if organizer else "Unknown",
            "date": e.date_time.isoformat(),
            "status": e.status,
            "revenue": revenue
        })
        
    return jsonify(result), 200

@admin_bp.route('/events/<int:event_id>/status', methods=['PATCH'])
@role_required('admin')
def update_event_status_admin(event_id):
    from flask import request
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['Active', 'Cancelled', 'Suspended']:
         return jsonify({"msg": "Invalid status"}), 400
         
    event = Event.query.get_or_404(event_id)
    event.status = new_status
    
    try:
        db.session.commit()
        return jsonify({"msg": f"Event status updated to {new_status}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500
