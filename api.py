from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Paths for storage
CHEATSHEETS_DIR = 'cheatsheets'
CHEATSHEETS_META_FILE = os.path.join(CHEATSHEETS_DIR, 'metadata.json')

# Ensure the cheatsheets directory exists
os.makedirs(CHEATSHEETS_DIR, exist_ok=True)

# Load cheatsheets metadata from JSON file
def load_cheatsheets_meta():
    if os.path.exists(CHEATSHEETS_META_FILE):
        with open(CHEATSHEETS_META_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save cheatsheets metadata to JSON file
def save_cheatsheets_meta(metadata):
    with open(CHEATSHEETS_META_FILE, 'w') as file:
        json.dump(metadata, file, indent=4)

# Endpoint to upload a cheatsheet file
@app.route('/upload_cheatsheet', methods=['POST'])
def upload_cheatsheet():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected.'}), 400
    
    # Generate a unique ID for the cheatsheet
    cheatsheet_id = str(uuid.uuid4())
    
    # Save the file to the cheatsheets directory
    file_path = os.path.join(CHEATSHEETS_DIR, f'{cheatsheet_id}.txt')
    file.save(file_path)
    
    # Update metadata
    metadata = load_cheatsheets_meta()
    metadata[cheatsheet_id] = {'filename': file.filename}
    save_cheatsheets_meta(metadata)
    
    return jsonify({'status': 'success', 'message': 'File uploaded successfully.', 'id': cheatsheet_id})

# Endpoint to list all cheatsheets
@app.route('/list_cheatsheets', methods=['GET'])
def list_cheatsheets():
    metadata = load_cheatsheets_meta()
    cheatsheets = [{'id': cid, 'filename': meta['filename']} for cid, meta in metadata.items()]
    return jsonify({'cheatsheets': cheatsheets})

# Endpoint to get a cheatsheet by ID
@app.route('/get_cheatsheet/<cheatsheet_id>', methods=['GET'])
def get_cheatsheet(cheatsheet_id):
    file_path = os.path.join(CHEATSHEETS_DIR, f'{cheatsheet_id}.txt')
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'Cheatsheet not found.'}), 404
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    return jsonify({'status': 'success', 'content': content})

# Endpoint to download cheatsheet as HTML
@app.route('/download_cheatsheet_html/<cheatsheet_id>', methods=['GET'])
def download_cheatsheet_html(cheatsheet_id):
    file_path = os.path.join(CHEATSHEETS_DIR, f'{cheatsheet_id}.txt')
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'Cheatsheet not found.'}), 404
    
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Generate HTML from the content (similar to the provided template)
    html_content = f"""<html>
<head><title>Bash Cheat Sheet</title></head>
<body>
<h1>BASH CHEAT SHEET</h1>
<p>This file contains short tables of commonly used items in this shell...</p>
<pre>{content}</pre>
</body>
</html>"""
    
    # Save the HTML content to a temporary file and send it as a download
    html_file_path = os.path.join(CHEATSHEETS_DIR, f'{cheatsheet_id}.html')
    with open(html_file_path, 'w') as html_file:
        html_file.write(html_content)
    
    return send_file(html_file_path, as_attachment=True, download_name=f'{cheatsheet_id}.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
