#!/bin/bash
set -e

echo "======================================"
echo "    PolliCam Access Point Config      "
echo "======================================"

# The SSID will be "PolliCam-" followed by the camera number
CAM_NUM=$(hostname | tr -dc '0-9')
if [ -z "$CAM_NUM" ]; then
    CAM_NUM="X"
fi
SSID="PolliCam-${CAM_NUM}"
PASSWORD="pollicam_field"

echo "Configuring the camera to broadcast its own Wi-Fi network..."
echo "Network Name (SSID) : $SSID"
echo "Password            : $PASSWORD"
echo "Camera IP Address   : 192.168.4.1"

# Delete any existing hotspot profile
sudo nmcli con delete Hotspot > /dev/null 2>&1 || true

# Create the new AP profile
sudo nmcli con add type wifi ifname wlan0 con-name Hotspot autoconnect yes ssid "$SSID" > /dev/null
sudo nmcli con modify Hotspot 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared > /dev/null
sudo nmcli con modify Hotspot wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PASSWORD" > /dev/null
sudo nmcli con modify Hotspot ipv4.addresses 192.168.4.1/24 > /dev/null

echo "Bringing up the hotspot..."
sudo nmcli con up Hotspot > /dev/null 2>&1 || true

echo ""
echo "✅ Success! The camera is now broadcasting."
echo "Your SSH connection will drop shortly."
echo "Connect your phone to Wi-Fi: $SSID"
echo "And go to: https://192.168.4.1:5000"
echo "======================================"
