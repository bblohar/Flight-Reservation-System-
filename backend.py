# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import heapq # For priority queue in Dijkstra's
import re    # For regular expressions (validation)
from datetime import datetime

app = Flask(__name__)
# Enable CORS for frontend to communicate. This is crucial when frontend and backend are on different ports/origins.
CORS(app) 

# --- Simulated Database (In-memory) ---
# In a real application, this would connect to a DBMS like PostgreSQL, MySQL, MongoDB, etc.

# Airports: {id: name}
AIRPORTS = {
    'DEL': 'Delhi',
    'BOM': 'Mumbai',
    'BLR': 'Bengaluru',
    'MAA': 'Chennai',
    'CCU': 'Kolkata',
    'HYD': 'Hyderabad',
    'PNQ': 'Pune',
    'AMD': 'Ahmedabad',
}

# Flights: List of dictionaries.
# Each flight represents a direct connection with distance and available seats.
# For simplicity, we'll assume flights are bidirectional for pathfinding,
# but seat management will be per-direction.
FLIGHTS = [
    {'from': 'DEL', 'to': 'BOM', 'distance': 1150, 'flight_id': 'F001', 'available_seats': 100},
    {'from': 'BOM', 'to': 'DEL', 'distance': 1150, 'flight_id': 'F001_R', 'available_seats': 100}, # Return flight
    {'from': 'DEL', 'to': 'CCU', 'distance': 1300, 'flight_id': 'F002', 'available_seats': 80},
    {'from': 'CCU', 'to': 'DEL', 'distance': 1300, 'flight_id': 'F002_R', 'available_seats': 80},
    {'from': 'BOM', 'to': 'BLR', 'distance': 850, 'flight_id': 'F003', 'available_seats': 120},
    {'from': 'BLR', 'to': 'BOM', 'distance': 850, 'flight_id': 'F003_R', 'available_seats': 120},
    {'from': 'BOM', 'to': 'HYD', 'distance': 620, 'flight_id': 'F004', 'available_seats': 90},
    {'from': 'HYD', 'to': 'BOM', 'distance': 620, 'flight_id': 'F004_R', 'available_seats': 90},
    {'from': 'BOM', 'to': 'PNQ', 'distance': 120, 'flight_id': 'F005', 'available_seats': 70},
    {'from': 'PNQ', 'to': 'BOM', 'distance': 120, 'flight_id': 'F005_R', 'available_seats': 70},
    {'from': 'BLR', 'to': 'MAA', 'distance': 350, 'flight_id': 'F006', 'available_seats': 110},
    {'from': 'MAA', 'to': 'BLR', 'distance': 350, 'flight_id': 'F006_R', 'available_seats': 110},
    {'from': 'BLR', 'to': 'HYD', 'distance': 500, 'flight_id': 'F007', 'available_seats': 95},
    {'from': 'HYD', 'to': 'BLR', 'distance': 500, 'flight_id': 'F007_R', 'available_seats': 95},
    {'from': 'MAA', 'to': 'CCU', 'distance': 1400, 'flight_id': 'F008', 'available_seats': 85},
    {'from': 'CCU', 'to': 'MAA', 'distance': 1400, 'flight_id': 'F008_R', 'available_seats': 85},
    {'from': 'CCU', 'to': 'HYD', 'distance': 1200, 'flight_id': 'F009', 'available_seats': 75},
    {'from': 'HYD', 'to': 'CCU', 'distance': 1200, 'flight_id': 'F009_R', 'available_seats': 75},
    {'from': 'HYD', 'to': 'AMD', 'distance': 900, 'flight_id': 'F010', 'available_seats': 105},
    {'from': 'AMD', 'to': 'HYD', 'distance': 900, 'flight_id': 'F010_R', 'available_seats': 105},
    {'from': 'PNQ', 'to': 'AMD', 'distance': 520, 'flight_id': 'F011', 'available_seats': 65},
    {'from': 'AMD', 'to': 'PNQ', 'distance': 520, 'flight_id': 'F011_R', 'available_seats': 65},
    {'from': 'DEL', 'to': 'AMD', 'distance': 770, 'flight_id': 'F012', 'available_seats': 115},
    {'from': 'AMD', 'to': 'DEL', 'distance': 770, 'flight_id': 'F012_R', 'available_seats': 115},
]

# Bookings: {pnr_number: booking_details}
# Added fields for more detailed traveler information
BOOKINGS = {} 

# --- Helper Functions ---

def build_graph(flights_data):
    """Builds an adjacency list graph from flight data."""
    graph = {airport_id: [] for airport_id in AIRPORTS.keys()}
    for flight in flights_data:
        # Add flight to graph if seats are available (for pathfinding)
        # For pathfinding, we only care about connectivity and distance.
        # Seat availability will be checked at booking time.
        graph[flight['from']].append({'to': flight['to'], 'distance': flight['distance'], 'flight_id': flight['flight_id']})
    return graph

def dijkstra(graph, start_node, end_node):
    """
    Implements Dijkstra's algorithm to find the shortest path.
    Returns (path, total_distance, flight_segments)
    """
    distances = {node: float('infinity') for node in graph}
    distances[start_node] = 0
    priority_queue = [(0, start_node)] # (distance, node)

    predecessors = {} # {node: (previous_node, flight_id_to_reach_node)}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor_info in graph.get(current_node, []):
            neighbor = neighbor_info['to']
            distance = neighbor_info['distance']
            flight_id = neighbor_info['flight_id']
            new_distance = current_distance + distance

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = (current_node, flight_id)
                heapq.heappush(priority_queue, (new_distance, neighbor))

    # Reconstruct path and flight segments
    path = []
    flight_segments = []
    current = end_node
    while current != start_node:
        if current not in predecessors:
            return [], float('infinity'), [] # No path found
        prev_node, flight_id = predecessors[current]
        path.insert(0, current)
        # Find the actual flight object to include in segments
        segment_flight = next((f for f in FLIGHTS if f['flight_id'] == flight_id), None)
        if segment_flight:
            flight_segments.insert(0, {'from': prev_node, 'to': current, 'flight_id': flight_id, 'distance': segment_flight['distance']})
        current = prev_node
    path.insert(0, start_node)

    return path, distances[end_node], flight_segments

# --- Validation Helper Functions ---
def is_valid_phone(phone_number):
    # Basic validation for 10 digits (can be expanded for international formats)
    return re.fullmatch(r'^\d{10}$', phone_number)

def is_valid_gmail(email):
    # Basic validation for @gmail.com
    return re.fullmatch(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email)

def is_valid_date_format(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# --- API Endpoints ---

@app.route('/airports', methods=['GET'])
def get_airports():
    """Returns a list of all available airports."""
    airport_list = [{'id': aid, 'name': aname} for aid, aname in AIRPORTS.items()]
    return jsonify(airport_list)

@app.route('/flights', methods=['GET'])
def get_flights():
    """Returns a list of all available flights (connections)."""
    return jsonify(FLIGHTS)

@app.route('/shortest_path', methods=['POST'])
def find_shortest_path():
    """
    Finds the shortest flight path between a from_airport and to_airport.
    Requires 'from_airport' and 'to_airport' in the request JSON.
    """
    data = request.get_json()
    from_airport = data.get('from_airport') # Renamed from 'source'
    to_airport = data.get('to_airport')     # Renamed from 'destination'

    if not from_airport or not to_airport:
        return jsonify({'error': 'From and To airports are required.'}), 400
    if from_airport not in AIRPORTS or to_airport not in AIRPORTS:
        return jsonify({'error': 'Invalid From or To airport ID.'}), 400
    if from_airport == to_airport:
        return jsonify({'error': 'From and To airports cannot be the same.'}), 400

    graph = build_graph(FLIGHTS)
    path, total_distance, flight_segments = dijkstra(graph, from_airport, to_airport)

    if total_distance == float('infinity'):
        return jsonify({
            'message': f'No path found between {from_airport} and {to_airport}.',
            'path': [],
            'total_distance': 0,
            'flight_segments': []
        }), 200 # Return 200 even if no path, just with empty data

    return jsonify({
        'message': 'Shortest path found!',
        'path': path,
        'total_distance': total_distance,
        'flight_segments': flight_segments
    })

@app.route('/book_flight', methods=['POST'])
def book_flight():
    """
    Books a flight.
    Requires 'passenger_name', 'email', 'gender', 'date_of_birth', 'phone_number',
    'seats', 'path', 'flight_segments', 'total_distance', 'travel_date' in JSON.
    """
    data = request.get_json()
    passenger_name = data.get('passenger_name')
    email = data.get('email')
    gender = data.get('gender') # New field
    date_of_birth = data.get('date_of_birth') # New field
    phone_number = data.get('phone_number') # New field
    seats_to_book = data.get('seats')
    path = data.get('path')
    flight_segments = data.get('flight_segments')
    total_distance = data.get('total_distance')
    travel_date = data.get('travel_date') # New field

    if not all([passenger_name, email, gender, date_of_birth, phone_number, seats_to_book, path, flight_segments, total_distance is not None, travel_date]):
        return jsonify({'error': 'Missing required booking information. Ensure all fields are provided.'}), 400
    if not isinstance(seats_to_book, int) or seats_to_book <= 0:
        return jsonify({'error': 'Number of seats must be a positive integer.'}), 400
    if not path or len(path) < 2:
        return jsonify({'error': 'Invalid flight path provided.'}), 400
    if not flight_segments or len(flight_segments) != len(path) - 1:
        return jsonify({'error': 'Invalid flight segments provided.'}), 400

    # Backend Validations
    if not is_valid_gmail(email):
        return jsonify({'error': 'Invalid email format. Please use a Gmail address.'}), 400
    if not is_valid_phone(phone_number):
        return jsonify({'error': 'Invalid phone number. Please enter a 10-digit number.'}), 400
    if gender not in ['Male', 'Female', 'Other']:
        return jsonify({'error': 'Invalid gender provided. Must be Male, Female, or Other.'}), 400
    if not is_valid_date_format(date_of_birth):
        return jsonify({'error': 'Invalid Date of Birth format. Expected YYYY-MM-DD.'}), 400
    if not is_valid_date_format(travel_date):
        return jsonify({'error': 'Invalid Travel Date format. Expected YYYY-MM-DD.'}), 400

    # Check if travel date is in the future
    try:
        travel_date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
        if travel_date_obj < datetime.now().date():
            return jsonify({'error': 'Travel date cannot be in the past.'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format for travel date.'}), 400

    # Check seat availability for all segments
    for segment in flight_segments:
        flight_id = segment['flight_id']
        flight_obj = next((f for f in FLIGHTS if f['flight_id'] == flight_id), None)
        if not flight_obj or flight_obj['available_seats'] < seats_to_book:
            return jsonify({'error': f'Not enough seats available on flight {flight_id}.'}), 400

    # Deduct seats and create booking
    pnr_number = str(uuid.uuid4())[:6].upper() # Generate a 6-character PNR
    for segment in flight_segments:
        flight_id = segment['flight_id']
        for flight_obj in FLIGHTS:
            if flight_obj['flight_id'] == flight_id:
                flight_obj['available_seats'] -= seats_to_book
                break

    booking_details = {
        'pnr_number': pnr_number, # Renamed from 'booking_id'
        'passenger_name': passenger_name,
        'email': email,
        'gender': gender,
        'date_of_birth': date_of_birth,
        'phone_number': phone_number,
        'seats': seats_to_book,
        'path': path,
        'total_distance': total_distance,
        'flight_segments': flight_segments,
        'travel_date': travel_date, # New field
        'status': 'CONFIRMED'
    }
    BOOKINGS[pnr_number] = booking_details

    return jsonify({
        'message': 'Flight booked successfully!',
        'pnr_number': pnr_number,
        'booking_details': booking_details
    }), 201

@app.route('/booking/<string:pnr_number>', methods=['GET']) # Renamed parameter
def get_booking_status(pnr_number):
    """
    Retrieves the status and details of a specific booking using PNR number.
    """
    booking = BOOKINGS.get(pnr_number.upper()) # Use PNR number as key
    if not booking:
        return jsonify({'error': 'PNR Number not found.'}), 404
    return jsonify(booking)

@app.route('/booking/<string:pnr_number>/cancel', methods=['PUT']) # Renamed parameter
def cancel_booking(pnr_number):
    """
    Cancels a specific booking and releases seats using PNR number.
    """
    pnr_number = pnr_number.upper()
    booking = BOOKINGS.get(pnr_number)
    if not booking:
        return jsonify({'error': 'PNR Number not found.'}), 404
    if booking['status'] == 'CANCELLED':
        return jsonify({'message': 'Booking is already cancelled.'}), 200

    # Release seats
    for segment in booking['flight_segments']:
        flight_id = segment['flight_id']
        for flight_obj in FLIGHTS:
            if flight_obj['flight_id'] == flight_id:
                flight_obj['available_seats'] += booking['seats']
                break

    booking['status'] = 'CANCELLED'
    return jsonify({
        'message': f'Booking with PNR {pnr_number} cancelled successfully.',
        'booking_details': booking
    })

@app.route('/booking/<string:pnr_number>/update', methods=['PUT']) # Renamed parameter
def update_booking(pnr_number):
    """
    Updates details of a specific booking using PNR number.
    Supports updating passenger name, email, gender, date_of_birth, phone_number, and travel_date.
    """
    pnr_number = pnr_number.upper()
    booking = BOOKINGS.get(pnr_number)
    if not booking:
        return jsonify({'error': 'PNR Number not found.'}), 404
    if booking['status'] == 'CANCELLED':
        return jsonify({'error': 'Cannot update a cancelled booking.'}), 400

    data = request.get_json()
    new_passenger_name = data.get('passenger_name')
    new_email = data.get('email')
    new_gender = data.get('gender')
    new_date_of_birth = data.get('date_of_birth')
    new_phone_number = data.get('phone_number')
    new_travel_date = data.get('travel_date') # New field for update

    updated = False

    if new_passenger_name is not None and new_passenger_name != booking['passenger_name']:
        booking['passenger_name'] = new_passenger_name
        updated = True
    
    if new_email is not None:
        if not is_valid_gmail(new_email):
            return jsonify({'error': 'Invalid email format for update. Please use a Gmail address.'}), 400
        if new_email != booking['email']:
            booking['email'] = new_email
            updated = True
    
    if new_gender is not None:
        if new_gender not in ['Male', 'Female', 'Other']:
            return jsonify({'error': 'Invalid gender provided for update. Must be Male, Female, or Other.'}), 400
        if new_gender != booking['gender']:
            booking['gender'] = new_gender
            updated = True
    
    if new_date_of_birth is not None:
        if not is_valid_date_format(new_date_of_birth):
            return jsonify({'error': 'Invalid Date of Birth format for update. Expected YYYY-MM-DD.'}), 400
        if new_date_of_birth != booking['date_of_birth']:
            booking['date_of_birth'] = new_date_of_birth
            updated = True
    
    if new_phone_number is not None:
        if not is_valid_phone(new_phone_number):
            return jsonify({'error': 'Invalid phone number for update. Please enter a 10-digit number.'}), 400
        if new_phone_number != booking['phone_number']:
            booking['phone_number'] = new_phone_number
            updated = True
            
    if new_travel_date is not None: # Update travel date
        if not is_valid_date_format(new_travel_date):
            return jsonify({'error': 'Invalid Travel Date format for update. Expected YYYY-MM-DD.'}), 400
        try:
            travel_date_obj = datetime.strptime(new_travel_date, '%Y-%m-%d').date()
            if travel_date_obj < datetime.now().date():
                return jsonify({'error': 'Travel date cannot be in the past.'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid date format for travel date.'}), 400
        if new_travel_date != booking['travel_date']:
            booking['travel_date'] = new_travel_date
            updated = True

    if updated:
        return jsonify({
            'message': f'Booking with PNR {pnr_number} updated successfully.',
            'booking_details': booking
        })
    else:
        return jsonify({'message': 'No changes detected or supported fields for update.'}), 200

if __name__ == '__main__':
    # To run this Flask app:
    # 1. Save it as app.py (or backend.py as you prefer)
    # 2. Install Flask and Flask-CORS: pip install Flask Flask-CORS
    # 3. Run from your terminal: python app.py
    # The app will run on http://127.0.0.1:5000/
    app.run(debug=True, port=5000)
