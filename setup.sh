#!/bin/bash

set -e

echo "[*] Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip openssh-client openssl


echo "[*] Installing Python packages..."
pip install flask paramiko

echo "[*] Generating RSA SSH key for honeypot..."
KEY_PATH="server.key"
if [ ! -f "$KEY_PATH" ]; then
    ssh-keygen -t rsa -b 2048 -m PEM -f "$KEY_PATH" -N "" <<< y >/dev/null 2>&1
    echo "[+] SSH key generated at $KEY_PATH"
else
    echo "[!] Key already exists: $KEY_PATH"
fi


