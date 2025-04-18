#!/bin/bash

# Cập nhật hệ thống
apt update -y

# Tạo thư mục và tải mã nguồn
mkdir -p z
cd z
wget https://github.com/Vukiao/x/archive/refs/heads/main.zip
unzip main.zip
cd x-main

# Cài Node.js module
npm install axios
npm install hpack
npm install chalk

# Cài Python venv và thư viện cần thiết
apt install python3.12-venv -y
python3 -m venv venv
source venv/bin/activate
pip install flask
pip install requests
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok
