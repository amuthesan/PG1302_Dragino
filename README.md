# PG1302 LoRaWAN Basic Station Gateway Setup

This repository contains the tools and documentation to set up the Dragino PG1302 LoRaWAN Concentrator as a Basic Station gateway on a Raspberry Pi.

**New Feature: Web-Based Setup Interface**
We have developed a modern, web-based dashboard to automate the entire configuration process.

## Prerequisites

- **Hardware**: Raspberry Pi 3/4/5 + Dragino PG1302 HAT.
- **OS**: Raspberry Pi OS (Bookworm 32-bit `armhf` is recommended).
- **Network**: Internet connection required.

---

## 🚀 Quick Start: Web UI Setup (Recommended)

The easiest way to set up your gateway is using the **Ark Technology Web Interface**.

### 1. Deploy the Web App
Run the deployment script from your computer (Mac/Linux). You will be prompted to enter your Raspberry Pi's IP address.

```bash
# Usage: ./deploy_to_pi.sh [IP_ADDRESS]
./deploy_to_pi.sh
```
*Tip: You can find your Pi's IP address by checking your router's connected devices list or running `ping raspberrypi.local` in the terminal.*

### 2. Access the Dashboard
Once deployed, open your web browser and navigate to:

**http://<YOUR_PI_IP>:5000**
*(Example: http://192.168.1.50:5000)*

### 3. Configure via UI
1.  **System Status**: Check if the service is running.
2.  **Gateway EUI**: Copy the EUI displayed on the dashboard and register your gateway on the **The Things Network (TTN)** console.
3.  **Configuration**: Enter your **TTN API Key** and click "Configure Gateway".
4.  **Monitor**: Watch the logs and status indicators to confirm connection (Green = Connected).

**Persistence**: The Web UI and the Gateway service are configured to start automatically on boot.

---

## 🛠 Manual Installation (Fallback)

If you prefer to configure the gateway manually via the terminal, follow these steps.

### 1. Prepare the Raspberry Pi
Enable the SPI interface:
```bash
sudo raspi-config nonint do_spi 0
```

### 2. Install Dragino Software
Download and install the 32-bit packet forwarder:
```bash
wget -O draginofwd-32bit.deb https://www.dragino.com/downloads/downloads/LoRa_Gateway/PG1302/software/draginofwd-32bit.deb
sudo dpkg -i draginofwd-32bit.deb
```

### 3. Register on TTN
Get your Gateway EUI:
```bash
cat /sys/class/net/eth0/address | sed 's/://g' | sed 's/\(.\{6\}\)\(.\{10\}\)/\1fffe\2/'
```
Register this EUI on TTN and generate an API Key.

### 4. Configure Basic Station
```bash
# Fix SPI device path
sudo sed -i 's|/dev/spidev1.0|/dev/spidev0.0|g' /etc/station/station.conf

# Link reset script
sudo ln -sf /usr/bin/rinit.sh /etc/station/rinit.sh

# Configure Credentials (replace placeholders)
echo 'wss://eu1.cloud.thethings.network:443' | sudo tee /etc/station/tc.uri
echo 'https://eu1.cloud.thethings.network:443' | sudo tee /etc/station/cups.uri
echo 'Authorization: Bearer <YOUR_API_KEY>' | sudo tee /etc/station/tc.key
echo 'Authorization: Bearer <YOUR_API_KEY>' | sudo tee /etc/station/cups.key

# Download CA Certificate
sudo wget -O /etc/station/cups.trust https://letsencrypt.org/certs/isrgrootx1.pem
sudo cp /etc/station/cups.trust /etc/station/tc.trust
```

### 5. Enable Persistence
```bash
# Disable conflicting legacy service
sudo systemctl stop draginofwd
sudo systemctl disable draginofwd

# Enable station service
sudo systemctl enable draginostation
sudo systemctl restart draginostation
```

## Tools Included
- `deploy_to_pi.sh`: Automates Web UI deployment (Usage: `./deploy_to_pi.sh <IP>`).
- `ssh_pi.exp` / `scp_pi.exp`: Expect scripts for automated SSH/SCP interactions.
- `setup_gui.py`: Legacy desktop Python GUI (Tkinter).
