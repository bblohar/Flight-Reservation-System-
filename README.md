✈️ Airline Reservation System
This project implements a simple Airline Reservation System, allowing users to search for the shortest flight paths, book flights, and manage their bookings (view, cancel, and update). The system consists of a Flask-based backend API and a pure HTML/CSS/JavaScript frontend.

📚 Table of Contents
Features

Technologies Used

Setup Instructions

Backend Setup

Frontend Setup

API Endpoints

Usage

Project Structure

Future Enhancements

Contributing

License

✨ Features
✅ Airport Management: Retrieve a list of all available airports.

✈️ Flight Search: Find the shortest flight path between two airports using Dijkstra's algorithm.

🎫 Flight Booking: Book flights with passenger details, including name, email, gender, date of birth, phone number, and travel date.

🗓️ Booking Management:

🔍 Retrieve booking details using a PNR number.

❌ Cancel existing bookings, which releases seats.

✏️ Update passenger information (name, email, gender, date of birth, phone number, travel date) for confirmed bookings.

🛡️ Client-Side Validation: Robust validation for input fields (email format, phone number, dates) on the frontend.

📱 Responsive UI: A modern and responsive user interface built with Tailwind CSS.

💾 In-memory Database: Simple in-memory data storage for airports, flights, and bookings (for demonstration purposes).

🛠️ Technologies Used
Backend:

🐍 Python 3

🌐 Flask: Web framework for building the API.

🔗 Flask-CORS: For handling Cross-Origin Resource Sharing.

🆔 uuid: For generating unique PNR numbers.

📊 heapq: For implementing Dijkstra's algorithm efficiently.

📝 re: For regular expression-based validation.

⏰ datetime: For date handling and validation.

Frontend:

📄 HTML5

🎨 CSS3 (Tailwind CSS for styling)

💻 JavaScript (Vanilla JS for DOM manipulation and API calls)

⚙️ Setup Instructions
Follow these steps to get the project up and running on your local machine.

🖥️ Backend Setup
Clone the repository (if not already done):

git clone <your-repository-url>
cd <your-repository-name>

Navigate to the backend directory:
Assuming your backend.py is in the root, otherwise, adjust the path.

# If backend.py is in a 'backend' folder
# cd backend

Create a virtual environment (recommended):

python -m venv venv

Activate the virtual environment:

On Windows:

.\venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

Install the required Python packages:

pip install Flask Flask-CORS

Run the Flask backend server:

python backend.py

The backend server will typically run on http://127.0.0.1:5000/. Keep this terminal window open.

🌐 Frontend Setup
The frontend is a static HTML file (fronted.html). You can open it directly in your web browser.

Open fronted.html:
Navigate to the fronted.html file in your file explorer and open it with your preferred web browser (e.g., Chrome, Firefox).

Important: Ensure the backend server is running before opening the frontend, as the frontend will try to communicate with the backend API.

🔗 API Endpoints
The backend API provides the following endpoints:

GET /airports: Get a list of all available airports.

GET /flights: Get a list of all available direct flights.

POST /shortest_path: Find the shortest path between two airports.

Request Body:

{
    "from_airport": "DEL",
    "to_airport": "BOM"
}

POST /book_flight: Book a new flight.

Request Body:

{
    "passenger_name": "John Doe",
    "email": "john.doe@gmail.com",
    "gender": "Male",
    "date_of_birth": "1990-01-15",
    "phone_number": "9876543210",
    "seats": 1,
    "path": ["DEL", "BOM"],
    "flight_segments": [{"from": "DEL", "to": "BOM", "flight_id": "F001", "distance": 1150}],
    "total_distance": 1150,
    "travel_date": "2025-12-25"
}

GET /booking/<pnr_number>: Retrieve details of a specific booking.

PUT /booking/<pnr_number>/cancel: Cancel a booking.

PUT /booking/<pnr_number>/update: Update details of a booking.

Request Body (example, send only fields to update):

{
    "passenger_name": "Jane Doe",
    "email": "jane.doe@gmail.com",
    "phone_number": "1234567890",
    "travel_date": "2026-01-01"
}

🚀 Usage
Search & Book Tab:

✈️ Select your "From" and "To" airports from the dropdowns.

🔍 Click "Find Shortest Flight" to see the optimal route and total distance.

➡️ If a path is found, click "Proceed to Booking".

📝 Fill in your passenger details, number of seats, and travel date.

✅ Click "Confirm Booking". A PNR number will be generated and displayed.

My Bookings Tab:

🔢 Enter your PNR number (from a previous booking).

👀 Click "Check Status" to view your booking details.

🔄 If the booking is confirmed, you will see options to "Cancel Booking" or "Update Booking".

Cancel Booking: 🚫 Click this button, confirm the action, and the booking status will change to "CANCELLED", releasing the seats.

Update Booking: ✍️ Click "Update Booking" to reveal a form. Modify the desired fields (name, email, gender, date of birth, phone number, travel date) and click "Apply Update".

📂 Project Structure
.
├── backend.py        # Flask backend application
├── fronted.html      # Frontend HTML, CSS, and JavaScript
├── 1693154256046.jpeg # Project banner image
└── download.jpeg     # Flight banner image used in frontend

✨ Future Enhancements
🗄️ Database Integration: Replace the in-memory database with a persistent database (e.g., PostgreSQL, MySQL, MongoDB) for real-world data storage.

🔐 User Authentication: Implement user registration and login for secure access to bookings.

💳 Payment Gateway Integration: Add a payment system for actual flight purchases.

➕ Advanced Search Filters: Allow searching by date, time, direct flights only, etc.

🖥️ Admin Panel: Create an interface for administrators to manage flights, airports, and bookings.

🐛 Error Handling Improvements: More granular error messages and graceful degradation.

🧪 Testing: Implement unit and integration tests for both frontend and backend.

☁️ Deployment: Set up deployment to cloud platforms (e.g., Heroku, AWS, Google Cloud).

🤝 Contributing
Contributions are welcome! Please follow these steps:

🍴 Fork the repository.

🌿 Create a new branch (git checkout -b feature/your-feature-name).

✏️ Make your changes.

💾 Commit your changes (git commit -m 'Add new feature').

⬆️ Push to the branch (git push origin feature/your-feature-name).

➡️ Open a Pull Request.
