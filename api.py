from flask import Flask, request, jsonify
import subprocess
import os
import signal

app = Flask(__name__)

PROXY_MAP = {
    "vn": ("y", "vn.txt"),
    "all": ("n", "prx.txt")
}

@app.route('/api', methods=['GET'])
def run_api():
    host = request.args.get('host')
    time_param = request.args.get('time')
    proxy_param = request.args.get('proxy', 'vn').lower()

    if not host or not time_param:
        return jsonify({"error": "Missing 'host' or 'time' parameter"}), 400

    if proxy_param not in PROXY_MAP:
        return jsonify({"error": "Invalid 'proxy' value, must be 'vn' or 'all'"}), 400

    prx_flag, proxy_file = PROXY_MAP[proxy_param]

    try:
        subprocess.run(["python3", "prx.py", prx_flag], capture_output=True, text=True)
    except Exception as e:
        return jsonify({"error": f"Error running prx.py: {str(e)}"}), 500

    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Proxy file not found: {proxy_file}"}), 500

    threads = "18"
    delay = "8"
    cmd = ["node", "c", "GET", host, time_param, threads, delay, proxy_file]

    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        return jsonify({
            "status": "Node script started in background",
            "host": host,
            "proxy_file": proxy_file
        })
    except Exception as e:
        return jsonify({"error": f"Error running node script: {str(e)}"}), 500

@app.route('/api/stop', methods=['GET'])
def stop_node_processes():
    try:
        subprocess.run(["pkill", "-f", "node c GET"], check=True)
        return jsonify({"status": "Stopped all running node scripts"})
    except subprocess.CalledProcessError:
        return jsonify({"status": "No node processes found or already stopped"})
    except Exception as e:
        return jsonify({"error": f"Error stopping node scripts: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1110)
