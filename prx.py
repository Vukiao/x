import requests
import sys

# Hàm tải dữ liệu từ một URL
def download_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Không thể tải từ {url}. Mã lỗi: {response.status_code}")
            return None
    except Exception as e:
        print(f"Lỗi khi tải: {e}")
        return None

# Hàm lưu dữ liệu, ghi đè nếu tệp đã tồn tại
def save_data_to_file(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
        print(f"Dữ liệu đã được lưu vào {filename}")
    except Exception as e:
        print(f"Lỗi khi lưu: {e}")

# URL của các API
url_prx = "http://103.186.101.138:1110//api/prx"
url_vn = "http://103.186.101.138:1110//api/vn"

# Kiểm tra tham số dòng lệnh
if len(sys.argv) < 2:
    print("Cách dùng: python3 api.py y|n")
    sys.exit(1)

arg = sys.argv[1].lower()

# Xử lý theo tham số
if arg == 'y':
    data = download_data(url_vn)
    if data:
        save_data_to_file(data, 'vn.txt')
elif arg == 'n':
    data = download_data(url_prx)
    if data:
        save_data_to_file(data, 'prx.txt')
else:
    print("Tham số không hợp lệ. Dùng 'y' để lấy proxy VN, 'n' để lấy proxy quốc tế.")
