from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import random

# Import local modules
import database as db
import model
import route_optimizer as router

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app) # Enable CORS for all routes

# Define base data during initialization if empty
INITIAL_LOCATIONS = [
    "Downtown Plaza", "Central Park", "Main Street Station",
    "University Campus", "City Mall", "Tech Park",
    "Residential Area A", "Residential Area B", "Hospital Zone",
    "Market Square"
]

with app.app_context():
    db.init_db()
    bins = db.get_all_bins()
    if not bins:
        print("Initializing default bins...")
        for loc in INITIAL_LOCATIONS:
            # Random initial fill level
            db.insert_bin(loc, round(random.uniform(10.0, 60.0), 2))

# ====================
# STATIC FILE ROUTES
# ====================

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_file(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return "Not Found", 404

# ====================
# API ENDPOINTS
# ====================

@app.route('/get_bins', methods=['GET'])
def get_bins():
    bins = db.get_all_bins()
    # Let's attach predictions as well for the dashboard
    predictions = {p['bin_id']: p['predicted_overflow'] for p in db.get_all_predictions()}
    
    for b in bins:
        b['predicted_overflow'] = predictions.get(b['id'], 0)
        
    return jsonify(bins)

@app.route('/add_bin', methods=['POST'])
def add_bin():
    data = request.json
    if not data or 'location' not in data or 'fill_level' not in data:
        return jsonify({"error": "Missing location or fill_level"}), 400
        
    bin_id = db.insert_bin(data['location'], data['fill_level'])
    return jsonify({"message": "Bin added", "bin_id": bin_id}), 201

@app.route('/update_bin', methods=['POST'])
def update_bin_route():
    data = request.json
    if not data or 'bin_id' not in data or 'fill_level' not in data:
        return jsonify({"error": "Missing bin_id or fill_level"}), 400
        
    db.update_bin(data['bin_id'], data['fill_level'])
    
    # When updating, also run prediction and save it
    prediction = model.predict_overflow(data['bin_id'], data['fill_level'])
    db.insert_prediction(data['bin_id'], prediction)
    
    return jsonify({
        "message": "Bin updated", 
        "prediction": prediction,
        "is_overflow": data['fill_level'] > 80.0
    }), 200

@app.route('/predict_overflow', methods=['POST'])
def predict_overflow_route():
    data = request.json
    if not data or 'bin_id' not in data or 'fill_level' not in data:
        return jsonify({"error": "Missing bin_id or fill_level"}), 400
        
    prediction = model.predict_overflow(data['bin_id'], data['fill_level'])
    return jsonify({"bin_id": data['bin_id'], "predicted_overflow": prediction})

@app.route('/optimize_route', methods=['GET'])
def optimize_route_api():
    bins = db.get_all_bins()
    # Filter bins that need collection (> 80%)
    bins_to_collect = [b for b in bins if b['fill_level'] > 80.0]
    
    if not bins_to_collect:
        return jsonify({"message": "No bins require collection.", "route": []})
        
    # Start node is assuming node 1 is depot
    result = router.optimize_route(bins_to_collect, start_node=1)
    
    # Enhance route coordinates for frontend display
    enhanced_route = []
    for node_id in result['route']:
        bin_data = next((b for b in bins if b['id'] == node_id), None)
        if bin_data:
            enhanced_route.append({
                "id": bin_data['id'],
                "location": bin_data['location'],
                "fill_level": bin_data['fill_level']
            })
        elif node_id == 1:
            # Depot case if no bin is at node 1
            enhanced_route.append({"id": 1, "location": "Depot", "fill_level": 0})
            
    return jsonify({
        "route_ids": result['route'],
        "stops": enhanced_route,
        "total_distance": result['total_distance']
    })

if __name__ == '__main__':
    # Initialize DB if not exists
    if not os.path.exists(db.DB_PATH):
        db.init_db()
    app.run(host='0.0.0.0', debug=True, port=5000)
