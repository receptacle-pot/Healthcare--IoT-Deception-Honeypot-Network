DEVICE_PROFILE = {
    "name": "MediVitals VX-1200",
    "vendor": "Northstar Biomedical",
    "firmware": "VXOS 2.3.4",
    "location": "ICU-West-3",
    "services": ["ssh", "telnet", "http", "mqtt", "dicom"],
}


FAKE_FILES = {
    "/etc/issue": "MediVitals VXOS 2.3.4\n",
    "/etc/passwd": "root:x:0:0:root:/root:/bin/sh\nservice:x:100:100:Service:/srv:/bin/sh\n",
    "/proc/cpuinfo": "Processor\t: ARMv7 Processor rev 5\nHardware\t: VX-1200 telemetry board\n",
    "/var/log/device.log": "SpO2 sensor recalibrated\nLead II signal quality nominal\n",
}


SHELL_RESPONSES = {
    "help": "diagnostics  status  netstat  reboot  update  cat  uname  ifconfig\n",
    "id": "uid=0(root) gid=0(root) groups=0(root)\n",
    "whoami": "root\n",
    "uname -a": "Linux medivitals-vx1200 4.4.0-vx #7 armv7l GNU/Linux\n",
    "ifconfig": "eth0 Link encap:Ethernet  inet addr:10.42.7.31  Mask:255.255.255.0\n",
    "ip addr": "2: eth0: inet 10.42.7.31/24 brd 10.42.7.255 scope global eth0\n",
    "netstat": "tcp 0 0 0.0.0.0:23 0.0.0.0:* LISTEN\ntcp 0 0 0.0.0.0:80 0.0.0.0:* LISTEN\n",
    "status": "HR=78 SpO2=98 NIBP=118/76 TEMP=36.8C BATTERY=AC\n",
    "diagnostics": "SELFTEST PASS\nECG PASS\nSPO2 PASS\nNIBP PASS\n",
}

