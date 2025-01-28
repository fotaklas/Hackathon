from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import math
import os

app = Flask(__name__)
CORS(app)

# Δεδομένα στόλων
fleets = [
    {"id": 1, "location": {"lat": 37.9755, "lon": 23.7348}, "drones": 10, "name": "Fleet 1 (Σύνταγμα)"},
    {"id": 2, "location": {"lat": 37.9842, "lon": 23.7277}, "drones": 0, "name": "Fleet 2 (Ομόνοια)"},
    {"id": 3, "location": {"lat": 37.9364, "lon": 23.9475}, "drones": 5, "name": "Fleet 3 (Αεροδρόμιο)"},
    {"id": 4, "location": {"lat": 37.9420, "lon": 23.6460}, "drones": 0, "name": "Fleet 4 (Πειραιάς)"},
    {"id": 5, "location": {"lat": 38.0541, "lon": 23.8060}, "drones": 3, "name": "Fleet 5 (Μαρούσι)"},
    {"id": 6, "location": {"lat": 37.9116, "lon": 23.7221}, "drones": 2, "name": "Fleet 6 (Άλιμος)"},
]

# Υπολογισμός απόστασης (Haversine formula)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Ακτίνα της Γης σε χιλιόμετρα
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Endpoint για επιστροφή δεδομένων στόλων
@app.route('/get_fleets', methods=['GET'])
def get_fleets():
    return jsonify(fleets)

# Endpoint για αποστολή drone
@app.route('/send_drone', methods=['POST'])
def send_drone():
    data = request.json
    point_a = data.get("pointA")
    point_b = data.get("pointB")
    
    if not point_a or not point_b:
        return jsonify({"error": "Both Point A and Point B are required"}), 400

    lat_a = point_a.get('lat')
    lon_a = point_a.get('lon')
    lat_b = point_b.get('lat')
    lon_b = point_b.get('lon')

    if None in [lat_a, lon_a, lat_b, lon_b]:
        return jsonify({"error": "Latitude and Longitude of both points are required"}), 400

    nearest_fleet = None
    min_distance = float('inf')

    # Βρίσκουμε τον κοντινότερο στόλο στο Σημείο Α
    for fleet in fleets:
        if fleet['drones'] > 0:  # Ελέγχουμε για διαθέσιμα drones
            distance = calculate_distance(lat_a, lon_a, fleet['location']['lat'], fleet['location']['lon'])
            if distance < min_distance:
                min_distance = distance
                nearest_fleet = fleet

    if nearest_fleet:
        nearest_fleet['drones'] -= 1  # Μείωση drones
        return jsonify({
            "fleet": nearest_fleet,
            "route": {
                "start": {"lat": nearest_fleet['location']['lat'], "lon": nearest_fleet['location']['lon']},
                "to_pickup": {"lat": lat_a, "lon": lon_a},
                "to_dropoff": {"lat": lat_b, "lon": lon_b},
                "return_to_base": {"lat": nearest_fleet['location']['lat'], "lon": nearest_fleet['location']['lon']}
            }
        })
    else:
        return jsonify({"error": "No available fleet found"}), 404

# Endpoint για ενημέρωση στόλου όταν drone επιστρέφει
@app.route('/update_fleet', methods=['POST'])
def update_fleet():
    data = request.json
    fleet_id = data.get("fleet_id")

    if fleet_id is None:
        return jsonify({"error": "Fleet ID is required"}), 400

    # Εύρεση στόλου
    fleet = next((f for f in fleets if f["id"] == fleet_id), None)

    if not fleet:
        return jsonify({"error": "Fleet not found"}), 404

    # Αύξηση διαθέσιμων drones
    fleet['drones'] += 1
    return jsonify({"message": f"Fleet {fleet_id} updated. Available drones: {fleet['drones']}"})

# Εξυπηρέτηση του αρχείου index.html
@app.route('/')
def serve_index():
    return send_from_directory(os.getcwd(), 'index.html')

# Εκκίνηση Server
if __name__ == '__main__':
    app.run(debug=True)
