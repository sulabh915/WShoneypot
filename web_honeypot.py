# web_honeypot.py

import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for

# Set up logging format
logging_format = logging.Formatter('%(asctime)s %(message)s')

# HTTP logger
funnel_logger = logging.getLogger('HTTP Logger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('http_audits.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

def web_honeypot(input_username='admin', input_password='password'):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('wp-admin.html')

    @app.route('/wp-admin-login', methods=['POST'])
    def login():
        username = request.form['username']
        password = request.form['password']
        ip_address = request.remote_addr

        funnel_logger.info(f'Client IP: {ip_address} | Username: {username} | Password: {password}')

        if username == input_username and password == input_password:
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password. Please try again."

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    return app

def run_web_honeypot(port=5000, input_username='admin', input_password='password'):
    honeypot_app = web_honeypot(input_username, input_password)
    honeypot_app.run(debug=True, port=port, host="0.0.0.0")
    return honeypot_app

if __name__ == "__main__":
    run_web_honeypot(port=5000, input_username='admin', input_password='password')

