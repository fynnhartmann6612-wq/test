from flask import Flask, request
import requests
import json

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1531275791600455920/eqjzGUGNuyHBs9awFBnwWJwV-HLZ_lgNtygrbi_jcUnU8BHiKWhLNh3bnaoM3TA2Nov5"

def get_public_ip():
    try:
        resp = requests.get('https://api.ipify.org?format=json', timeout=5)
        return resp.json()['ip']
    except:
        try:
            resp = requests.get('https://api.ipapi.co/json/', timeout=5)
            return resp.json().get('ip', 'unknown')
        except:
            return 'unable_to_fetch'

def send_to_discord(ip):
    payload = {"content": f"IP: {ip}"}
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        return r.status_code == 204
    except:
        return False

@app.route('/')
def log_ip():
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if visitor_ip and ',' in visitor_ip:
        visitor_ip = visitor_ip.split(',')[0].strip()
    send_to_discord(visitor_ip)
    return "Logged", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
