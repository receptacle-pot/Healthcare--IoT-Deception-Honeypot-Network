
from flask import Flask, render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sklearn.ensemble import IsolationForest
import pandas as pd
import random
import threading
import socket
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attacks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Attack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100))
    attack_type = db.Column(db.String(100))
    severity = db.Column(db.String(50))
    ai_result = db.Column(db.String(50))
    target_device = db.Column(db.String(100))
    time = db.Column(db.DateTime, default=datetime.utcnow)

fake_devices = [
    {"device":"MRI Scanner","ip":"192.168.1.10","status":"Active"},
    {"device":"ECG Monitor","ip":"192.168.1.20","status":"Active"},
    {"device":"Smart Infusion Pump","ip":"192.168.1.30","status":"Idle"},
    {"device":"Patient Monitor","ip":"192.168.1.40","status":"Active"}
]

attack_types = [
    "Port Scan",
    "Brute Force",
    "SQL Injection",
    "Malware Upload",
    "DDoS Attempt"
]

ips = [
    "45.22.11.3",
    "103.44.22.19",
    "182.76.11.90",
    "88.12.67.44"
]

def ai_detect():
    sample = {
        'packets':[10,12,11,300,450,9,8,400],
        'requests':[4,5,6,220,300,5,4,250]
    }

    df = pd.DataFrame(sample)

    model = IsolationForest(contamination=0.25, random_state=42)
    df['result'] = model.fit_predict(df)

    if -1 in df['result'].values:
        return "Suspicious"

    return "Normal"

@app.route('/')
def home():

    attacks = Attack.query.order_by(Attack.time.desc()).all()

    total_attacks = len(attacks)

    attack_stats = {}

    for a in attacks:
        attack_stats[a.attack_type] = attack_stats.get(a.attack_type,0)+1

    return render_template(
        'index.html',
        attacks=attacks,
        devices=fake_devices,
        total_attacks=total_attacks,
        attack_stats=attack_stats
    )

@app.route('/generate')
def generate_attack():

    attack = Attack(
        ip=random.choice(ips),
        attack_type=random.choice(attack_types),
        severity=random.choice(["Low","Medium","High","Critical"]),
        ai_result=ai_detect(),
        target_device=random.choice(fake_devices)['device']
    )

    db.session.add(attack)
    db.session.commit()

    return redirect('/')

@app.route('/api/stats')
def api_stats():

    attacks = Attack.query.all()

    stats = {}

    for a in attacks:
        stats[a.attack_type] = stats.get(a.attack_type,0)+1

    return jsonify(stats)

def honeypot_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind(("0.0.0.0",2222))
        server.listen(5)

        while True:

            client, addr = server.accept()

            time.sleep(random.uniform(1,3))

            banner = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\n"
            client.send(banner.encode())

            with app.app_context():

                attack = Attack(
                    ip=addr[0],
                    attack_type="SSH Honeypot Connection",
                    severity="Medium",
                    ai_result="Suspicious",
                    target_device="SSH Medical Gateway"
                )

                db.session.add(attack)
                db.session.commit()

            client.close()

    except Exception as e:
        print("Honeypot Error:",e)

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    threading.Thread(target=honeypot_server, daemon=True).start()

    app.run(host='0.0.0.0',port=5000,debug=True)
