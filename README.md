
# WShoneypot System (SSH + Web WordPress Clone)

A stealthy and extensible Python honeypot for mimicking both SSH shells and WordPress login portals, designed for security research, attacker deception, and credential collection.

## Features

🔐 SSH Honeypot

- Simulates a Linux-like shell on port 2223
- Captures and logs brute-force login attempts (username, password, IP)
- Responds to typical shell commands like ls, pwd, whoami, cat, etc.
- Utilizes the paramiko library for SSH server simulation


🌐 HTTP WordPress Honeypot

- Frontend emulates WordPress login page (/wp-admin)
- Redirects successful logins to a fake dashboard
- Records username, password, and IP address of attacker
- Built using Flask and HTML templates


📁 Logging System

- Logs are stored in the log/ directory using rotating file handlers
- http_audits.log: logs web form credentials
- audits.log: logs SSH login attempts
- cmd_audits.log: logs SSH shell commands
- Timestamped entries for forensic tracking


⚙️ Unified CLI Tool

- Choose between SSH or HTTP honeypot via CLI flags
- Configurable address, port, username, and password
- Generates RSA key file server.key automatically if missing
## Setup

Install my-project with npm

```bash
chmod +x setup_honeypot.sh
./setup_honeypot.sh
```
This will:

- Install required Python libraries
- Create and activate a virtual environment
- Generate an RSA key for SSH honeypot
## Usage/Examples
Launch SSH Honeypot:
```javascript
python3 main.py -s -a 0.0.0.0 -p 2223 -u root -w toor
```
Launch HTTP Honeypot:
```bash
python3 main.py -wh -a 0.0.0.0 -p 5000
```

Default login: admin / deeboodah

## 🗂️ Project Structure
```bash
.
├── main.py                 # CLI interface
├── ssh_honeypot.py         # SSH honeypot backend
├── web_honeypot.py         # HTTP honeypot with WordPress clone
├── templates/              # Flask templates
│   ├── wp-admin.html
│   └── dashboard.html
├── server.key              # RSA private key (auto-generated)
├── setup_honeypot.sh       # Setup installer script
├── config.ini              # Optional configuration overrides
└── log/                    # Logging output files
```
## ⚠️ Legal Disclaimer
This honeypot is intended strictly for educational and research purposes in controlled environments. Do not deploy publicly without legal permission.
