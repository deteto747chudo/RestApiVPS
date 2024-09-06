from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import subprocess
import signal
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Path to the JSON file containing streamers
STREAMERS_FILE = 'streamers.json'
PROCESS_NAME = 'mainsetup.py'
process = None  # Global variable to store the subprocess

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

# Start the mainsetup.py process
def start_process():
    global process
    if process is None or process.poll() is not None:
        process = subprocess.Popen(['python3', PROCESS_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {'status': 'success', 'message': 'Process started.'}
    return {'status': 'error', 'message': 'Process is already running.'}

# Stop the mainsetup.py process
def stop_process():
    global process
    if process is not None:
        process.terminate()  # Send terminate signal
        process.wait()  # Wait for the process to terminate
        process = None
        return {'status': 'success', 'message': 'Process stopped.'}
    return {'status': 'error', 'message': 'Process is not running.'}

# Restart the mainsetup.py process
def restart_process():
    stop_result = stop_process()
    if stop_result['status'] == 'success':
        start_result = start_process()
        return start_result
    return stop_result

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

# Endpoint to start the mainsetup.py process
@app.route('/start', methods=['POST'])
def start():
    return jsonify(start_process())

# Endpoint to stop the mainsetup.py process
@app.route('/stop', methods=['POST'])
def stop():
    return jsonify(stop_process())

# Endpoint to restart the mainsetup.py process
@app.route('/restart', methods=['POST'])
def restart():
    return jsonify(restart_process())

# Endpoint to get the status of the mainsetup.py process
@app.route('/status', methods=['GET'])
def status():
    global process
    if process is None:
        return jsonify({'status': 'not running'})
    elif process.poll() is None:
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
