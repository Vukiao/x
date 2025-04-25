#!/bin/bash

# Kiểm tra tham số dòng lệnh
if [ -z "$1" ]; then
  echo "Cách dùng: ./setup.sh [số dòng token.txt]"
  exit 1
fi

LINE_NUM=$1

# Cập nhật hệ thống và tạo thư mục làm việc
apt update -y

# Cài đặt các thư viện npm cần thiết
npm install axios hpack chalk fs https-proxy-agent http-proxy-agent async request puppeteer-extra puppeteer-extra-plugin-stealth puppeteer-extra-plugin-adblocker ua-parser-js user-agents crypto os colors random-referer puppeteer
npm install request random-referer user-agents puppeteer puppeteer-extra puppeteer-extra-plugin-stealth async colors hpack puppeteer puppeteer-extra puppeteer-extra-plugin-stealth async
sudo apt install ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils -y
# Cài đặt Python và các gói pip cần thiết
apt install python3.12-venv -y
python3 -m venv venv
source venv/bin/activate
pip install flask requests

# Cài đặt ngrok
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update
sudo apt install ngrok -y

# Chạy API ở chế độ nền
nohup python api.py > api.log 2>&1 &

# Chạy ngrok từ token.txt ở chế độ nền
if [ -f token.txt ]; then
  CMD=$(sed -n "${LINE_NUM}p" token.txt)
  if [ -n "$CMD" ]; then
    echo "Đang chạy dòng $LINE_NUM: $CMD"
    nohup bash -c "$CMD" > ngrok.log 2>&1 &

    # Gửi link ngrok qua Telegram
    echo "Đang chờ ngrok tạo link..."
    source venv/bin/activate
    python send_ngrok.py
  else
    echo "Không tìm thấy dòng $LINE_NUM trong token.txt"
  fi
else
  echo "Không tìm thấy file token.txt"
fi
