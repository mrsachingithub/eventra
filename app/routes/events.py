from flask import Blueprint, request, jsonify
from app.models import Event, Venue, db, Seat, Booking, Ticket
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.auth import role_required
from datetime import datetime

events_bp = Blueprint('events', __name__)

# --- Venues ---

@events_bp.route('/venues', methods=['POST'])
@role_required('organizer')
def create_venue():
    data = request.get_json()
    organizer_id = int(get_jwt_identity())
    
    name = data.get('name')
    address = data.get('address')
    capacity = data.get('capacity')
    
    if not name or not address or not capacity:
        return jsonify({"msg": "Missing fields"}), 400
        
    venue = Venue(name=name, address=address, capacity=capacity, owner_id=organizer_id)
    try:
        db.session.add(venue)
        db.session.commit() # Commit first to get ID safely
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error creating venue: " + str(e)}), 500
    
    # Auto-generate seats
    try:
        rows = int(int(capacity) / 10) + 1
        seat_count = 0
        for r in range(rows):
            row_label = chr(65 + r) # A, B, C...
            for n in range(1, 11):
                if seat_count >= int(capacity): break
                seat = Seat(venue_id=venue.id, row_label=row_label, seat_number=n)
                db.session.add(seat)
                seat_count += 1
        db.session.commit()
    except Exception as e:
        # If seat creation fails, we might want to delete the venue or just log it
        print("Error creating seats:", e)
        db.session.rollback()
        return jsonify({"msg": "Venue created but seat generation failed."}), 201 # Partial success warning

    return jsonify({"msg": "Venue created", "id": venue.id}), 201

@events_bp.route('/venues', methods=['GET'])
@role_required('organizer')
def get_my_venues():
    current_user_id = int(get_jwt_identity())
    venues = Venue.query.filter_by(owner_id=current_user_id).all()
    return jsonify([{
        "id": v.id, "name": v.name, "address": v.address, "capacity": v.capacity
    } for v in venues]), 200

# --- Events ---

@events_bp.route('/', methods=['POST'])
@role_required('organizer')
def create_event():
    data = request.get_json()
    organizer_id = int(get_jwt_identity())
    
    title = data.get('title')
    description = data.get('description')
    date_time_str = data.get('date_time')
    venue_id = data.get('venue_id')
    base_price = data.get('base_price')
    
    if not title or not date_time_str or not venue_id or not base_price:
        return jsonify({"msg": "Missing fields"}), 400
        
    try:
        date_time = datetime.fromisoformat(date_time_str)
    except ValueError:
        return jsonify({"msg": "Invalid date format"}), 400

    new_event = Event(
        title=title,
        description=description,
        date_time=date_time,
        venue_id=venue_id,
        organizer_id=organizer_id,
        base_price=base_price,
        status='Active'
    )
    
    db.session.add(new_event)
    db.session.commit()
    
    return jsonify({"msg": "Event created", "id": new_event.id}), 201

@events_bp.route('/', methods=['GET'])
def get_public_events():
    events = Event.query.filter_by(status='Active').all()
    result = []
    for e in events:
        venue = Venue.query.get(e.venue_id)
        result.append({
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "date_time": e.date_time.isoformat(),
            "venue": venue.name,
            "base_price": e.base_price
        })
    return jsonify(result), 200

@events_bp.route('/organizer', methods=['GET'])
@role_required('organizer')
def get_organizer_events():
    organizer_id = int(get_jwt_identity())
    events = Event.query.filter_by(organizer_id=organizer_id).all()
    return jsonify([{
        "id": e.id,
        "title": e.title,
        "date_time": e.date_time.isoformat(),
        "status": e.status
    } for e in events]), 200

@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event_details(event_id):
    event = Event.query.get_or_404(event_id)
    venue = Venue.query.get(event.venue_id)
    return jsonify({
         "id": event.id,
         "title": event.title,
         "description": event.description,
         "date_time": event.date_time.isoformat(),
         "venue_name": venue.name,
         "venue_address": venue.address,
         "base_price": event.base_price,
         "status": event.status
    }), 200

# --- Organizer Management Endpoints ---

@events_bp.route('/<int:event_id>/bookings', methods=['GET'])
@role_required('organizer')
def get_event_bookings(event_id):
    organizer_id = int(get_jwt_identity())
    event = Event.query.get_or_404(event_id)
    
    # Security: Ensure current user owns this event
    if event.organizer_id != organizer_id:
        return jsonify({"msg": "Unauthorized"}), 403
        
    bookings = Booking.query.filter_by(event_id=event_id).order_by(Booking.created_at.desc()).all()
    
    result = []
    for b in bookings:
        user = b.user
        tickets = Ticket.query.filter_by(booking_id=b.id).all()
        seats = [f"{t.seat.row_label}{t.seat.seat_number}" for t in tickets]
        
        result.append({
            "booking_id": b.id,
            "customer_name": user.username,
            "customer_email": user.email,
            "status": b.status,
            "total_amount": b.total_amount,
            "seats": ", ".join(seats),
            "date": b.created_at.isoformat()
        })
        
    return jsonify(result), 200

@events_bp.route('/<int:event_id>/analytics', methods=['GET'])
@role_required('organizer')
def get_event_analytics(event_id):
    organizer_id = int(get_jwt_identity())
    event = Event.query.get_or_404(event_id)
    
    if event.organizer_id != organizer_id:
        return jsonify({"msg": "Unauthorized"}), 403

    # Venue Capacity
    venue = Venue.query.get(event.venue_id)
    total_capacity = venue.capacity
    
    # Sales
    # Count valid tickets (not cancelled bookings)
    sold_tickets_count = Ticket.query.join(Booking).filter(
        Booking.event_id == event_id,
        Booking.status != 'Cancelled',
        Ticket.status == 'Valid'
    ).count()
    
    revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(
        Booking.event_id == event_id,
        Booking.status != 'Cancelled'
    ).scalar() or 0.0
    
    return jsonify({
        "total_capacity": total_capacity,
        "sold_tickets": sold_tickets_count,
        "remaining_tickets": total_capacity - sold_tickets_count,
        "total_revenue": revenue
    }), 200

@events_bp.route('/<int:event_id>/status', methods=['PATCH'])
@role_required('organizer')
def update_event_status(event_id):
    organizer_id = int(get_jwt_identity())
    event = Event.query.get_or_404(event_id)
    
    if event.organizer_id != organizer_id:
        return jsonify({"msg": "Unauthorized"}), 403
        
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['Active', 'Cancelled']:
         return jsonify({"msg": "Invalid status"}), 400
         
    try:
        event.status = new_status
        db.session.commit()
        return jsonify({"msg": f"Event status updated to {new_status}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500

@events_bp.route('/organizer/stats', methods=['GET'])
@role_required('organizer')
def get_organizer_global_stats():
    organizer_id = int(get_jwt_identity())
    
    # Total Events
    total_events = Event.query.filter_by(organizer_id=organizer_id).count()
    
    # Total Revenue & Tickets (Valid only)
    # Join Event -> Booking -> Ticket (if needed, but Booking has total_amount)
    # Rev = Sum of confirmed bookings for my events
    
    # Query: Sum total_amount where event.organizer_id == me AND status != Cancelled
    revenue = db.session.query(db.func.sum(Booking.total_amount)).join(Event).filter(
        Event.organizer_id == organizer_id,
        Booking.status != 'Cancelled'
    ).scalar() or 0.0
    
    # Tickets Sold: Count tickets in valid bookings for my events
    sold_tickets = Ticket.query.join(Booking).join(Event).filter(
        Event.organizer_id == organizer_id,
        Booking.status != 'Cancelled',
        Ticket.status == 'Valid'
    ).count()
    
    return jsonify({
        "total_events": total_events,
        "total_revenue": revenue,
        "total_tickets_sold": sold_tickets
    }), 200
