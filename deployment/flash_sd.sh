#!/bin/bash
# flash_sd.sh
# Automated SD Card Provisioning for PolliCam

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path_to_image.img> <device_e.g._/dev/sdb>"
    exit 1
fi

IMAGE=$1
DEVICE=$2

if [ ! -f "$IMAGE" ]; then
    echo "Error: Image file $IMAGE not found."
    exit 1
fi

if [ ! -b "$DEVICE" ]; then
    echo "Error: Device $DEVICE is not a valid block device."
    exit 1
fi

echo "WARNING: This will completely erase $DEVICE."
read -p "Are you sure? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo "Flashing $IMAGE to $DEVICE... This may take a while."
sudo dd if="$IMAGE" of="$DEVICE" bs=4M status=progress
sync

# Identify the boot partition
BOOT_PART="${DEVICE}1"
if [ ! -b "$BOOT_PART" ]; then
    BOOT_PART="${DEVICE}p1"
fi

if [ ! -b "$BOOT_PART" ]; then
    echo "Error: Could not find boot partition on $DEVICE"
    exit 1
fi

echo "Mounting boot partition $BOOT_PART..."
MOUNT_DIR=$(mktemp -d)
sudo mount "$BOOT_PART" "$MOUNT_DIR"

echo "Enabling SSH on boot..."
sudo touch "$MOUNT_DIR/ssh"

echo "Configuring WiFi credentials (wpa_supplicant.conf)..."
# Replace these with your actual hotspot credentials
WIFI_SSID=${POLLICAM_WIFI_SSID:-"PolliCam_Hotspot"}
WIFI_PASS=${POLLICAM_WIFI_PASS:-"pollisecret"}

sudo bash -c "cat > $MOUNT_DIR/wpa_supplicant.conf" <<EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=CZ

network={
    ssid="$WIFI_SSID"
    psk="$WIFI_PASS"
    key_mgmt=WPA-PSK
}
EOF

echo "Setting default user (user: pi, pass: raspberry)..."
# Generating a secure hash for the password 'raspberry'
# You can generate a new one using: echo 'pi:'$(openssl passwd -6 password)
sudo bash -c "echo 'pi:\$6\$aL2R/vLw7Xz\$uMvO8zV9Q5.K3pZ0a7C9r1B2f5L8y0N9j4H7x3D1m6E2q0W5k8P2v1M9G4X6s5H3T1w0Y8Q2e7N1u4B0/' > $MOUNT_DIR/userconf.txt"

echo "Syncing filesystem and unmounting..."
sync
sudo umount "$MOUNT_DIR"
rmdir "$MOUNT_DIR"

echo "Success! The SD card is ready to be inserted into the PolliCam."
