#!/bin/bash
set -e

echo "======================================"
echo "    PolliCam Static IP Locker         "
echo "======================================"

# Get the current active Wi-Fi connection name
CON_NAME=$(nmcli -t -f NAME,TYPE connection show --active | grep 802-11-wireless | cut -d: -f1 | head -n 1)

# Get the current IP address
CURRENT_IP=$(hostname -I | awk '{print $1}')

# Get the default gateway (the phone's IP)
GATEWAY=$(ip route | grep default | awk '{print $3}')

if [ -z "$CON_NAME" ] || [ -z "$CURRENT_IP" ] || [ -z "$GATEWAY" ]; then
    echo "Error: Could not detect the active Wi-Fi connection or IP address."
    echo "Make sure you are connected to the hotspot."
    exit 1
fi

echo "Detected Wi-Fi Connection : $CON_NAME"
echo "Detected Current IP       : $CURRENT_IP"
echo "Detected Phone Gateway    : $GATEWAY"
echo ""
echo "Locking the IP address permanently..."

# Modify the NetworkManager connection to use static IP
sudo nmcli con mod "$CON_NAME" ipv4.addresses $CURRENT_IP/24 ipv4.gateway $GATEWAY ipv4.dns 8.8.8.8 ipv4.method manual

echo "✅ Success! The camera will now ALWAYS use: https://$CURRENT_IP:5000"
echo "You can safely bookmark this address on your phone."
echo "======================================"
