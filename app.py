import os
import subprocess
import logging
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def run_command(command):
    """Runs a shell command and returns output/error."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/eui', methods=['GET'])
def get_eui():
    """Retrieves the Gateway EUI."""
    cmd = "cat /sys/class/net/eth0/address | sed 's/://g' | sed 's/\\(.\\{6\\}\\)\\(.\\{6\\}\\)/\\1fffe\\2/'"
    success, output = run_command(cmd)
    if success:
        return jsonify({'success': True, 'eui': output})
    return jsonify({'success': False, 'error': output}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Checks the service status and TTN connection."""
    success, output = run_command("systemctl is-active draginostation")
    service_status = "running" if success and output == "active" else "stopped"
    
    # Get last 50 lines of logs to ensure we catch the connection message
    if os.path.exists("/var/log/station.log"):
        _, logs = run_command("tail -n 50 /var/log/station.log")
    else:
        logs = "Log file not found. Service might not be running yet."
    
    # Determine TTN Connection Status
    ttn_status = "disconnected"
    if service_status == "running":
        if "Connected to MUXS" in logs:
            ttn_status = "connected"
        elif "Connecting to INFOS" in logs or "Starting TC engine" in logs:
            ttn_status = "connecting"
        elif "FAIL TO CONNECT BOARD" in logs:
            ttn_status = "hardware_error"
    
    return jsonify({
        'status': service_status,
        'ttn_status': ttn_status,
        'logs': logs
    })

@app.route('/api/configure', methods=['POST'])
def configure():
    """Configures the gateway."""
    data = request.json
    lns_uri = data.get('lns_uri')
    cups_uri = data.get('cups_uri')
    lns_key = data.get('lns_key', '').strip()
    cups_key = data.get('cups_key', '').strip()

    # Sanitize keys (remove "Authorization: Bearer " if user pasted it)
    if lns_key.lower().startswith("authorization: bearer "):
        lns_key = lns_key.split(" ", 2)[2]
    if cups_key.lower().startswith("authorization: bearer "):
        cups_key = cups_key.split(" ", 2)[2]

    if not all([lns_uri, cups_uri, lns_key, cups_key]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    commands = [
        # Enable SPI
        "raspi-config nonint do_spi 0",
        # Install Software (Idempotent-ish)
        "rm -f /tmp/draginofwd.deb && wget -O /tmp/draginofwd.deb https://www.dragino.com/downloads/downloads/LoRa_Gateway/PG1302/software/draginofwd-32bit.deb && dpkg -i /tmp/draginofwd.deb",
        # Fix SPI
        "sed -i 's|/dev/spidev1.0|/dev/spidev0.0|g' /etc/station/station.conf",
        # Link Reset
        "ln -sf /usr/bin/rinit.sh /etc/station/rinit.sh",
        # Fix Binary Name (Package installs station_sx1302 but service expects station)
        "ln -sf /usr/bin/station_sx1302 /usr/bin/station",
        # Config Keys
        f"echo '{lns_uri}' > /etc/station/tc.uri",
        f"echo '{cups_uri}' > /etc/station/cups.uri",
        f"echo 'Authorization: Bearer {lns_key}' > /etc/station/tc.key",
        f"echo 'Authorization: Bearer {cups_key}' > /etc/station/cups.key",
        # Certs
        # Certs
        "wget -O /etc/station/cups.trust https://letsencrypt.org/certs/isrgrootx1.pem",
        "cp /etc/station/cups.trust /etc/station/tc.trust",
        "chmod 644 /etc/station/cups.trust /etc/station/tc.trust",
        # Persistence
        "systemctl stop draginofwd || true",
        "systemctl disable draginofwd || true",
        "systemctl enable draginostation",
        "systemctl restart draginostation"
    ]

    try:
        for cmd in commands:
            app.logger.info(f"Executing: {cmd}")
            success, output = run_command(cmd)
            if not success:
                raise Exception(f"Command failed: {cmd}\nError: {output}")
        
        return jsonify({'success': True, 'message': 'Configuration completed successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible from network
    app.run(host='0.0.0.0', port=5000, debug=True)
