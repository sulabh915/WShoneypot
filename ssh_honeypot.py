# ssh_honeypot.py
import logging
from logging.handlers import RotatingFileHandler
import socket
import paramiko
import threading
import time
import argparse
import configparser
from datetime import datetime
import os

# ------------------------
# Load configuration safely
# ------------------------
config = configparser.ConfigParser()
config.read('config.ini')

# Provide default fallback values even if section is missing
if 'honeypot' not in config:
    config['honeypot'] = {}

SSH_BANNER = config['honeypot'].get('ssh_banner', "SSH-2.0-MySSHServer_1.0")
HOST_KEY_PATH = config['honeypot'].get('host_key_path', "server.key")
LOG_FILE_FUNNEL = config['honeypot'].get('log_file_funnel', "audits.log")
LOG_FILE_CREDS = config['honeypot'].get('log_file_creds', "cmd_audits.log")
HOST = config['honeypot'].get('host', '0.0.0.0')
PORT = int(config['honeypot'].get('port', 2223))
USERNAME = config['honeypot'].get('username', 'username')
PASSWORD = config['honeypot'].get('password', 'password')

# ------------------------
# Logging Setup
# ------------------------
logging_format = logging.Formatter('%(asctime)s - %(message)s')

funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler(LOG_FILE_FUNNEL, maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler(LOG_FILE_CREDS, maxBytes=2000, backupCount=5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)

# ------------------------
# Load Host Key
# ------------------------
if not os.path.exists(HOST_KEY_PATH):
    raise FileNotFoundError(f"Host key file not found: {HOST_KEY_PATH}")
host_key = paramiko.RSAKey(filename=HOST_KEY_PATH)

# ------------------------
# Emulated Shell
# ------------------------

def emulated_shell(channel, client_ip):
    prompt = b'corporate-jumpbox2$ '
    channel.send(prompt)
    command = b""
    while True:
        char = channel.recv(1)
        if not char:
            break

        command += char
        channel.send(char)

        if char == b'\r':
            cmd = command.strip()
            decoded_cmd = cmd.decode(errors='ignore')
            creds_logger.info(f"{client_ip} executed: {decoded_cmd}")

            if cmd == b'exit':
                channel.send(b'\r\nGoodbye!\r\n')
                break
            elif cmd == b'pwd':
                response = b'/usr/local\r\n'
            elif cmd == b'whoami':
                response = b'corpuser1\r\n'
            elif cmd == b'ls':
                response = b'jumpbox1.conf\r\n'
            elif cmd == b'cat jumpbox1.conf':
                response = b'Go to test.com\r\n'
            elif cmd == b'uname -a':
                response = b'Linux corpbox 5.15.0-76-generic #83-Ubuntu SMP x86_64\r\n'
            elif cmd == b'id':
                response = b'uid=1000(corpuser1) gid=1000(corpuser1) groups=1000(corpuser1)\r\n'
            else:
                response = b'bash: ' + cmd + b': command not found\r\n'

            channel.send(b'\r\n' + response + prompt)
            command = b""

# ------------------------
# SSH Server Class
# ------------------------

class Server(paramiko.ServerInterface):
    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        time.sleep(1)  # Delay to slow down brute-force
        funnel_logger.info(f"[{self.client_ip}] Login attempt: {username}/{password}")
        if self.input_username and self.input_password:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            return paramiko.AUTH_FAILED
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        return True

# ------------------------
# Handle Client Connection
# ------------------------

def client_handle(client, addr, username, password):
    client_ip = addr[0]
    print(f"{client_ip} connected.")
    transport = None
    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        transport.add_server_key(host_key)
        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        transport.start_server(server=server)

        channel = transport.accept(100)
        if channel is None:
            print("No channel opened.")
            return

        banner = "Welcome to Ubuntu 22.04 LTS \r\n\r\n"
        channel.send(banner.encode())
        emulated_shell(channel, client_ip)

    except Exception as error:
        funnel_logger.exception(f"[{client_ip}] Error: {error}")

    finally:
        if transport:
            try:
                transport.close()
            except Exception as error:
                funnel_logger.exception(f"[{client_ip}] Transport close error: {error}")
        client.close()

# ------------------------
# Start SSH Honeypot
# ------------------------

def honeypot(address, port, username, password):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((address, port))
    sock.listen(100)
    print(f"[+] SSH Honeypot listening on {address}:{port}")

    while True:
        try:
            client, addr = sock.accept()
            thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            thread.start()
        except Exception as error:
            funnel_logger.exception(f"Connection error: {error}")

# ------------------------
# Entry Point
# ------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSH Honeypot")
    parser.add_argument('--host', default=HOST)
    parser.add_argument('--port', type=int, default=PORT)
    parser.add_argument('--username', default=USERNAME)
    parser.add_argument('--password', default=PASSWORD)
    args = parser.parse_args()

    honeypot(args.host, args.port, args.username, args.password)
