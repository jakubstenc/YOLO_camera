#!/bin/bash
set -e

echo "======================================"
echo "    PolliCam Predictable IP Locker    "
echo "======================================"

CON_NAME=$(nmcli -t -f NAME,TYPE connection show --active | grep 802-11-wireless | cut -d: -f1 | head -n 1)
CURRENT_IP=$(hostname -I | awk '{print $1}')
GATEWAY=$(ip route | grep default | awk '{print $3}')

if [ -z "$CON_NAME" ] || [ -z "$CURRENT_IP" ] || [ -z "$GATEWAY" ]; then
    echo "Error: Could not detect the active Wi-Fi connection."
    exit 1
fi

# Extract the number from the hostname (e.g. "pi1" -> 1, "pi12" -> 12)
CAM_NUM=$(hostname | tr -dc '0-9')
if [ -z "$CAM_NUM" ]; then
    CAM_NUM=100
fi

# Create a predictable IP address matching the camera number
SUBNET=$(echo $CURRENT_IP | cut -d. -f1-3)
NEW_IP="$SUBNET.$((100 + CAM_NUM))"

echo "Camera Name (Hostname)  : $(hostname)"
echo "Extracted Camera Number : $CAM_NUM"
echo "New Predictable IP      : $NEW_IP"
echo ""
echo "Locking the IP address permanently..."

sudo nmcli con mod "$CON_NAME" ipv4.addresses $NEW_IP/24 ipv4.gateway $GATEWAY ipv4.dns 8.8.8.8 ipv4.method manual
sudo nmcli con up "$CON_NAME" > /dev/null 2>&1 || true

echo ""
echo "✅ Success! The camera has been permanently assigned."
echo "Your SSH connection will likely drop now because the IP has changed."
echo "From now on, you can ALWAYS access this camera at:"
echo "https://$NEW_IP:5000"
echo "======================================"
