#!/bin/bash

# Configuration
PI_USER="pi"
PI_PASS="raspberry"
REMOTE_DIR="/home/pi/dragino_web_setup"

# Get IP from argument or prompt
if [ -z "$1" ]; then
    read -p "Enter Raspberry Pi IP Address: " PI_IP
else
    PI_IP=$1
fi

if [ -z "$PI_IP" ]; then
    echo "Error: IP Address is required."
    exit 1
fi

echo "Deploying to $PI_USER@$PI_IP..."

# 1. Create remote directory
./ssh_pi.exp $PI_IP $PI_USER $PI_PASS "mkdir -p $REMOTE_DIR/templates $REMOTE_DIR/static"

# 2. Copy files using SCP (Reliable transfer)
echo "Copying app.py..."
./scp_pi.exp $PI_IP $PI_USER $PI_PASS "app.py" "$REMOTE_DIR/"

echo "Copying templates..."
./scp_pi.exp $PI_IP $PI_USER $PI_PASS "templates/index.html" "$REMOTE_DIR/templates/"

echo "Copying static files (Logo)..."
./scp_pi.exp $PI_IP $PI_USER $PI_PASS "static/logo.png" "$REMOTE_DIR/static/"
# Ensure permissions are correct
./ssh_pi.exp $PI_IP $PI_USER $PI_PASS "chmod -R 755 $REMOTE_DIR/static"

# 3. Install Flask
echo "Installing Flask on Pi..."
./ssh_pi.exp $PI_IP $PI_USER $PI_PASS "sudo apt-get install -y python3-flask || sudo pip3 install flask"

# 4. Install and Start Service
echo "Installing Systemd Service..."
./scp_pi.exp $PI_IP $PI_USER $PI_PASS "ark-gateway-ui.service" "/tmp/"
./ssh_pi.exp $PI_IP $PI_USER $PI_PASS "sudo mv /tmp/ark-gateway-ui.service /etc/systemd/system/ark-gateway-ui.service"
./ssh_pi.exp $PI_IP $PI_USER $PI_PASS "sudo systemctl daemon-reload"
./ssh_pi.exp $PI_IP $PI_USER $PI_PASS "sudo systemctl enable ark-gateway-ui.service"
./ssh_pi.exp $PI_IP $PI_USER $PI_PASS "sudo systemctl restart ark-gateway-ui.service"

echo "Deployment Complete!"
echo "Access the UI at: http://$PI_IP:5000"
