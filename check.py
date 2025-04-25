from flask import Flask, Response
import requests
import threading
import time
import random
import re
import os

app = Flask(__name__)

UPDATE_INTERVAL = 60

text_urls_all = [
    "https://calce.space/proxy.txt",
    "https://api.nminhniee.sbs/Nm.php",
    "http://36.50.134.20:3000/download/http",
    "http://36.50.134.20:3000/download/free-proxy-list",
    "http://36.50.134.20:3000/download/proxy-list-download",
    "http://36.50.134.20:3000/download/geonode",
    "http://36.50.134.20:3000/download/spysme",
    "http://36.50.134.20:3000/download/proxyscrape",
    "http://36.50.134.20:3000/download/vn"
]

text_urls_vn = [
    "https://calce.space/proxy.txt",
    "https://api.nminhniee.sbs/Nm.php",
    "http://36.50.134.20:3000/download/vn"
]

proxy_cache_all = []
proxy_cache_vn = []

# ======== TOOL CHECK PROXY LIVE =========

class ProxyInfo:
    def __init__(self, proxy):
        self.proxy = proxy
        self.location = None
        self.type = None
        self.response_time = None

    def determine_location(self):
        try:
            r = requests.get('https://ipinfo.io/json', proxies={"http": self.proxy, "https": self.proxy}, timeout=5)
            self.location = r.json().get("city", "Unknown")
            return True
        except:
            self.location = "Unknown"
            return False

    def determine_type(self):
        types = ["http", "https"]
        for t in types:
            try:
                r = requests.get("http://www.google.com", proxies={t: self.proxy}, timeout=5)
                if r.status_code == 200:
                    self.type = t.upper()
                    return
            except:
                pass
        self.type = "Unknown"

    def measure_response_time(self):
        try:
            r = requests.get("http://www.google.com", proxies={"http": self.proxy, "https": self.proxy}, timeout=5)
            self.response_time = r.elapsed.total_seconds()
        except:
            self.response_time = float('inf')

    def get_info(self):
        is_live = self.determine_location()
        if is_live:
            self.determine_type()
            self.measure_response_time()
        return is_live

def check_live_proxies(filename, num_threads=1500):
    output_file = "live.txt"
    if os.path.exists(output_file):
        os.remove(output_file)

    proxy_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$')
    lock = threading.Lock()

    def check_proxy_thread(proxy):
        proxy_info = ProxyInfo(proxy)
        if proxy_info.get_info() and proxy_pattern.match(proxy):
            with lock:
                with open(output_file, "a") as f:
                    f.write(proxy + "\n")

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return

    threads = []
    for proxy in proxies:
        t = threading.Thread(target=check_proxy_thread, args=(proxy,))
        t.start()
        threads.append(t)
        if len(threads) >= num_threads:
            for t in threads: t.join()
            threads = []

    for t in threads:
        t.join()

# ======== CẬP NHẬT PROXY + KIỂM TRA LIVE =========

def fetch_text_proxies(urls):
    all_lines = set()
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            lines = response.text.strip().splitlines()
            all_lines.update(line.strip() for line in lines if line.strip())
        except Exception as e:
            print(f"[!] Lỗi khi tải {url}: {e}")
    return list(all_lines)

def save_to_file(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(data))
        print(f"[+] Đã ghi file: {filename} ({len(data)} proxy)")
    except Exception as e:
        print(f"[!] Lỗi ghi file {filename}: {e}")

def update_proxies_periodically():
    global proxy_cache_all, proxy_cache_vn
    while True:
        print("[*] Đang cập nhật proxy...")
        proxy_cache_all = fetch_text_proxies(text_urls_all)
        proxy_cache_vn = fetch_text_proxies(text_urls_vn)

        save_to_file("all_proxies.txt", proxy_cache_all)
        save_to_file("vn_proxies.txt", proxy_cache_vn)

        print(f"[✓] Cập nhật xong: {len(proxy_cache_all)} (ALL), {len(proxy_cache_vn)} (VN)")
        time.sleep(UPDATE_INTERVAL)

def check_live_periodically():
    while True:
        print("[*] Đang kiểm tra proxy live...")
        check_live_proxies("vn_proxies.txt")
        print("[✓] Đã cập nhật file live.txt")
        time.sleep(30)

# ======== API ROUTES =========

@app.route('/api/prx')
def get_all_proxies():
    shuffled = proxy_cache_all[:]
    random.shuffle(shuffled)
    return Response("\n".join(shuffled), mimetype='text/plain')

@app.route('/api/vn')
def get_vn_proxies():
    shuffled = proxy_cache_vn[:]
    random.shuffle(shuffled)
    return Response("\n".join(shuffled), mimetype='text/plain')

@app.route('/api/ip')
def get_stats():
    return {
        "total_all": len(proxy_cache_all),
        "total_vn": len(proxy_cache_vn),
        "update_interval_seconds": UPDATE_INTERVAL
    }

@app.route('/api/live')
def get_live_proxies():
    try:
        with open("live.txt", "r") as f:
            lines = f.read().splitlines()
            random.shuffle(lines)
        return Response("\n".join(lines), mimetype='text/plain')
    except FileNotFoundError:
        return Response("No live proxies found.", mimetype='text/plain')

# ======== KHỞI CHẠY =========

if __name__ == '__main__':
    threading.Thread(target=update_proxies_periodically, daemon=True).start()
    threading.Thread(target=check_live_periodically, daemon=True).start()
    app.run(host='0.0.0.0', port=1110)
