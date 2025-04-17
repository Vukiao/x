import requests

# Hàm tải dữ liệu từ một URL
def download_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error: Unable to download data from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Hàm lưu dữ liệu vào tệp
def save_data_to_file(data, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
        print(f"Dữ liệu đã được lưu vào {filename}")
    except Exception as e:
        print(f"Error: {e}")

# URL của các API
url_prx = "http://103.75.183.153:1110/api/prx"
url_vn = "http://103.75.183.153:1110/api/vn"

# Hỏi người dùng có muốn tải proxy vn không
use_vn = input("Có dùng proxy VN không? (y/n): ").strip().lower()

# Tải dữ liệu từ API và lưu vào tệp tương ứng
if use_vn == 'y':
    data_vn = download_data(url_vn)
    if data_vn:
        save_data_to_file(data_vn, 'vn.txt')
elif use_vn == 'n':
    data_prx = download_data(url_prx)
    if data_prx:
        save_data_to_file(data_prx, 'prx.txt')
else:
    print("Lựa chọn không hợp lệ. Vui lòng nhập 'y' hoặc 'n'.")
