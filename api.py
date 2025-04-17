from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

PROXY_MAP = {
    "vn": ("y", "vn.txt"),
    "qte": ("n", "prx.txt")
}

@app.route('/api', methods=['GET'])
def run_api():
    host = request.args.get('host')
    time_param = request.args.get('time')
    proxy_param = request.args.get('proxy', 'vn').lower()

    if not host or not time_param:
        return jsonify({"error": "Thieu 'host' hoac 'time'"}), 400

    if proxy_param not in PROXY_MAP:
        return jsonify({"error": "proxy phai la 'vn' hoac 'qte'"}), 400

    prx_flag, proxy_file = PROXY_MAP[proxy_param]

    # Bước 1: chạy prx.py
    try:
        subprocess.run(["python3", "prx.py", prx_flag], capture_output=True, text=True)
    except Exception as e:
        return jsonify({"error": f"Loi khi chay prx.py: {str(e)}"}), 500

    # Kiểm tra file proxy có tồn tại không
    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Khong tim thay file proxy: {proxy_file}"}), 500

    # Bước 2: chạy node ở chế độ nền
    threads = "18"
    delay = "8"
    cmd = ["node", "c", "GET", host, time_param, threads, delay, proxy_file]

    try:
        subprocess.Popen(cmd)
        return jsonify({
            "status": "Da khoi chay api thanh cong",
            "host": host,
            "proxy_file": proxy_file
        })
    except Exception as e:
        return jsonify({"error": f"Lỗi khi chạy node (nền): {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1110)
