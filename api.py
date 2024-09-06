from flask import Flask, request, jsonify
import subprocess
import psutil
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def run_script(command):
    script_path = './run_script.sh'
    try:
        subprocess.run([script_path, command], check=True)
        return {'status': 'success', 'message': f'{command.capitalize()} command executed.'}
    except subprocess.CalledProcessError as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/start', methods=['POST'])
def start_process():
    return jsonify(run_script('start'))

@app.route('/stop', methods=['POST'])
def stop_process():
    return jsonify(run_script('stop'))

@app.route('/restart', methods=['POST'])
def restart_process():
    return jsonify(run_script('restart'))

@app.route('/status', methods=['GET'])
def status():
    # Check if processes are running
    status = {
        'mainsetup.py': any(
            p.name() == 'python3' and 'mainsetup.py' in p.cmdline() for p in psutil.process_iter()
        ),
        'flask': any(
            p.name() == 'python3' and 'api.py' in p.cmdline() for p in psutil.process_iter()
        ),
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
