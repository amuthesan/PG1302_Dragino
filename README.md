# PG1302 LoRaWAN Basic Station Gateway Setup

This guide provides step-by-step instructions to set up the Dragino PG1302 LoRaWAN Concentrator as a Basic Station gateway on a Raspberry Pi.

## Prerequisites

- **Hardware**: Raspberry Pi 3/4/5 + Dragino PG1302 HAT.
- **OS**: Raspberry Pi OS (Bookworm 32-bit `armhf` is recommended).
- **Network**: Internet connection required.

## Step-by-Step Installation

### 1. Prepare the Raspberry Pi
Enable the SPI interface:
```bash
sudo raspi-config nonint do_spi 0
```

### 2. Install Dragino Software
Download and install the 32-bit packet forwarder (compatible with most Pi OS versions):
```bash
wget -O draginofwd-32bit.deb https://www.dragino.com/downloads/downloads/LoRa_Gateway/PG1302/software/draginofwd-32bit.deb
sudo dpkg -i draginofwd-32bit.deb
```

### 3. Register on The Things Network (TTN)
1.  **Get your Gateway EUI**:
    Run this command to see your EUI (based on the Ethernet MAC):
    ```bash
    cat /sys/class/net/eth0/address | sed 's/://g' | sed 's/\(.\{6\}\)\(.\{10\}\)/\1fffe\2/'
    ```
    *(Output example: `e45f01fffe92f30f`)*

2.  **Register Gateway**:
    - Go to the [TTN Console](https://console.cloud.thethings.network/).
    - Register a new gateway.
    - Enter the **Gateway EUI** from above.
    - Select **Basic Station** as the connection method.
    - Generate an **API Key** (LNS Key).

### 4. Configure Basic Station
Run the following commands to configure the station software.

**A. Set SPI Device and Reset Script:**
```bash
# Fix SPI device path
sudo sed -i 's|/dev/spidev1.0|/dev/spidev0.0|g' /etc/station/station.conf

# Link reset script
sudo ln -sf /usr/bin/rinit.sh /etc/station/rinit.sh
```

**B. Configure Credentials:**
Replace `<YOUR_API_KEY>` with your actual TTN API Key.

```bash
# Set LNS Server URI (Example for Europe, change 'eu1' to 'au1' or 'nam1' as needed)
echo 'wss://eu1.cloud.thethings.network:443' | sudo tee /etc/station/tc.uri

# Set CUPS Server URI
echo 'https://eu1.cloud.thethings.network:443' | sudo tee /etc/station/cups.uri

# Set API Keys
echo 'Authorization: Bearer <YOUR_API_KEY>' | sudo tee /etc/station/tc.key
echo 'Authorization: Bearer <YOUR_API_KEY>' | sudo tee /etc/station/cups.key

# Download CA Certificate
sudo wget -O /etc/station/cups.trust https://letsencrypt.org/certs/isrgrootx1.pem
sudo cp /etc/station/cups.trust /etc/station/tc.trust
```

### 5. Enable Persistence (Auto-Start)
Disable the legacy forwarder and enable the Basic Station service:
```bash
# Stop and disable conflicting service
sudo systemctl stop draginofwd
sudo systemctl disable draginofwd

# Enable and start Basic Station
sudo systemctl enable draginostation
sudo systemctl restart draginostation
```

### 6. Verify Status
Check the logs to ensure it's connected:
```bash
sudo tail -f /var/log/station.log
```
You should see messages like `[TCE:VERB] Connected to MUXS` and `Station device: spi:/dev/spidev0.0`.

---

## Troubleshooting
- **404 Not Found**: Check that your EUI in TTN matches the one in the logs.
- **Radio Busy**: Ensure `draginofwd` is stopped (`sudo systemctl stop draginofwd`).
