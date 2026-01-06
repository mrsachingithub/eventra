from flask import Blueprint, jsonify, request
from app.models import db, Booking, Ticket, Seat, Event, Payment, Venue
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import qrcode
import io
import base64
from flask import render_template

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/<int:event_id>/seats', methods=['GET'])
def get_seats(event_id):
    event = Event.query.get_or_404(event_id)
    seats = Seat.query.filter_by(venue_id=event.venue_id).all()
    
    # Get booked or locked seat IDs for this event
    # Status: Confirmed OR (Pending AND Not Expired)
    now = datetime.utcnow()
    
    booked_query = db.session.query(Ticket.seat_id).join(Booking).filter(
        Booking.event_id == event_id,
        Booking.status != 'Cancelled',
        db.or_(
            Booking.status == 'Confirmed',
            db.and_(Booking.status == 'Pending', Booking.expires_at > now)
        )
    )
    
    booked_seat_ids = {s[0] for s in booked_query.all()}

    seat_data = []
    for seat in seats:
        seat_data.append({
            "id": seat.id,
            "row": seat.row_label,
            "number": seat.seat_number,
            "type": seat.seat_type,
            "price": event.base_price * seat.price_multiplier,
            "status": "booked" if seat.id in booked_seat_ids else "available"
        })
    return jsonify(seat_data), 200

@bookings_bp.route('/lock', methods=['POST'])
@jwt_required()
def lock_tickets():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    event_id = data.get('event_id')
    seat_ids = data.get('seat_ids') # List of seat IDs
    
    if not event_id or not seat_ids:
         return jsonify({"msg": "Missing fields"}), 400

    try:
        seat_ids = [int(sid) for sid in seat_ids]
    except ValueError:
        return jsonify({"msg": "Invalid seat IDs"}), 400

    # 1. Double Booking Check (Strict)
    # Check if any seat is Confirmed OR (Pending and Active)
    now = datetime.utcnow()
    existing_tickets = Ticket.query.join(Booking).filter(
        Booking.event_id == event_id,
        Booking.status != 'Cancelled',
        Ticket.seat_id.in_(seat_ids),
        db.or_(
            Booking.status == 'Confirmed',
            db.and_(Booking.status == 'Pending', Booking.expires_at > now)
        )
    ).first()
    
    if existing_tickets:
        return jsonify({"msg": "One or more seats are already booked"}), 409

    try:
        event = Event.query.get(event_id)
        total_amount = 0
        for s_id in seat_ids:
            seat = Seat.query.get(s_id)
            total_amount += event.base_price * seat.price_multiplier

        # 2. Create Locked Booking (Pending)
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        booking = Booking(
            user_id=user_id,
            event_id=event_id,
            status='Pending',
            total_amount=total_amount,
            expires_at=expires_at
        )
        db.session.add(booking)
        db.session.flush()

        # 3. Create Reserved Tickets
        for s_id in seat_ids:
            ticket = Ticket(
                booking_id=booking.id,
                seat_id=s_id,
                unique_code=f"LOCK-{event_id}-{s_id}",
                status='Reserved'
            )
            db.session.add(ticket)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Locking failed: " + str(e)}), 500
    
    return jsonify({"msg": "Seats locked", "booking_id": booking.id, "expires_at": expires_at.isoformat()}), 201

@bookings_bp.route('/confirm', methods=['POST'])
@jwt_required()
def confirm_booking():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    booking_id = data.get('booking_id')
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != user_id:
        return jsonify({"msg": "Unauthorized"}), 403
        
    if booking.status != 'Pending':
        return jsonify({"msg": "Booking already processed or cancelled"}), 400
        
    if booking.expires_at < datetime.utcnow():
        booking.status = 'Cancelled'
        db.session.commit()
        return jsonify({"msg": "Booking expired"}), 400
        
    try:
        # Simulate Payment
        payment = Payment(
            booking_id=booking.id,
            amount=booking.total_amount,
            status='Paid',
            transaction_id=f"TXN-{int(datetime.utcnow().timestamp())}"
        )
        db.session.add(payment)
        
        # Update Booking
        booking.status = 'Confirmed'
        booking.expires_at = None # Clear expiration
        
        # Update Tickets
        tickets = Ticket.query.filter_by(booking_id=booking.id).all()
        for t in tickets:
            t.status = 'Valid'
            t.unique_code = f"EVT-{booking.event_id}-ST-{t.seat_id}-{int(datetime.utcnow().timestamp())}"
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Confirmation failed"}), 500

    return jsonify({"msg": "Booking confirmed!", "booking_id": booking.id}), 200

@bookings_bp.route('/my', methods=['GET'])
@jwt_required()
def my_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    
    result = []
    for b in bookings:
        event = Event.query.get(b.event_id)
        tickets = Ticket.query.filter_by(booking_id=b.id).all()
        seat_labels = []
        for t in tickets:
            seat = Seat.query.get(t.seat_id)
            seat_labels.append(f"{seat.row_label}{seat.seat_number}")
            
        result.append({
            "id": b.id,
            "event_title": event.title,
            "date": event.date_time.isoformat(),
            "status": b.status,
            "seats": ", ".join(seat_labels),
            "total_amount": b.total_amount
        })
        
    return jsonify(result), 200

@bookings_bp.route('/ticket/<int:booking_id>', methods=['GET'])
def view_ticket(booking_id):
    # No JWT required for public ticket validation (simulated access control via ID)
    # In production, use a signed token or random UUID
    booking = Booking.query.get_or_404(booking_id)
    event = Event.query.get(booking.event_id)
    venue = Venue.query.get(event.venue_id)
    tickets = Ticket.query.filter_by(booking_id=booking.id).all()
    
    # Enrich ticket data with seat labels
    ticket_data = []
    for t in tickets:
        seat = Seat.query.get(t.seat_id)
        t.seat_label = f"{seat.row_label}{seat.seat_number}"
    
    # Generate QR Code
    # Data format: "EVENTRA:BOOKING:<ID>"
    qr_data = f"EVENTRA:BOOKING:{booking.id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to buffer
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Use the first ticket's unique code for display
    unique_code = tickets[0].unique_code if tickets else "N/A"

    return render_template('customer/ticket_view.html', 
                           booking=booking, 
                           event=event, 
                           venue=venue, 
                           tickets=tickets,
                           qr_code=qr_b64,
                           unique_code=unique_code)
