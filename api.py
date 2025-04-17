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
        return jsonify({"error": "Thiếu 'host' hoặc 'time'"}), 400

    if proxy_param not in PROXY_MAP:
        return jsonify({"error": "proxy phải là 'vn' hoặc 'qte'"}), 400

    prx_flag, proxy_file = PROXY_MAP[proxy_param]

    # Bước 1: chạy prx.py
    try:
        subprocess.run(["python", "prx.py", prx_flag], capture_output=True, text=True)
    except Exception as e:
        return jsonify({"error": f"Lỗi khi chạy prx.py: {str(e)}"}), 500

    # Kiểm tra xem proxy file đã được tạo chưa
    if not os.path.exists(proxy_file):
        return jsonify({"error": f"Không tìm thấy file proxy: {proxy_file}"}), 500

    # Bước 2: chạy node với thông số cố định
    threads = "18"
    delay = "8"
    cmd = ["node", "c", "GET", host, time_param, threads, delay, proxy_file]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return jsonify({
            "status": "Đã chạy node thành công",
            "host": host,
            "proxy_file": proxy_file,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except Exception as e:
        return jsonify({"error": f"Lỗi khi chạy node: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1110)
