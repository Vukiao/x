import requests
import time

# Thay thế bằng token và chat_id của bạn
TELEGRAM_BOT_TOKEN = '7991506659:AAG6y7T88mJflcQZw8EYETLAPwqVdnyPaG8'
CHAT_ID = 'YOUR_CHAT_ID'

def get_ngrok_url():
    try:
        tunnels = requests.get('http://localhost:4040/api/tunnels').json()
        for tunnel in tunnels['tunnels']:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
    except Exception as e:
        print(f"Lỗi khi lấy URL ngrok: {e}")
    return None

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message}
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Lỗi khi gửi tin nhắn: {response.text}")
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn: {e}")

# Đợi ngrok khởi động và lấy URL
for _ in range(10):
    url = get_ngrok_url()
    if url:
        send_telegram_message(f'Ngrok URL: {url}')
        break
    time.sleep(2)
else:
    print("Không thể lấy URL ngrok sau nhiều lần thử.")
