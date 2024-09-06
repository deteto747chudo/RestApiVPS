from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Path to the JSON file containing streamers
STREAMERS_FILE = 'streamers.json'

# Load streamers from JSON file
def load_streamers():
    if os.path.exists(STREAMERS_FILE):
        with open(STREAMERS_FILE, 'r') as file:
            data = json.load(file)
            return data.get('streamers', [])
    else:
        return []

# Save streamers to JSON file
def save_streamers(streamers):
    with open(STREAMERS_FILE, 'w') as file:
        json.dump({'streamers': streamers}, file, indent=4)

# Endpoint to get current streamers
@app.route('/get_streamers', methods=['GET'])
def get_streamers():
    streamers = load_streamers()
    return jsonify({'streamers': streamers})

# Endpoint to update streamers
@app.route('/update_streamers', methods=['POST'])
def update_streamers():
    data = request.json
    new_streamers = data.get('streamers', [])

    if not isinstance(new_streamers, list):
        return jsonify({'error': 'Invalid data format'}), 400

    # Load current streamers and update only non-empty new streamers
    current_streamers = load_streamers()
    updated_streamers = []

    for i in range(5):  # We expect up to 5 streamers
        if i < len(new_streamers) and new_streamers[i].strip():
            updated_streamers.append(new_streamers[i])
        elif i < len(current_streamers):
            updated_streamers.append(current_streamers[i])
        else:
            updated_streamers.append("")  # Keep empty if no replacement

    # Save updated streamers to the file
    save_streamers(updated_streamers)

    return jsonify({'message': 'Streamers updated successfully!', 'streamers': updated_streamers})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
