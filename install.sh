#!/bin/bash
set -e

echo "======================================"
echo "    PolliCam Auto-Installer v1.0      "
echo "======================================"

# 1. Update and install dependencies
echo ""
echo "[1/4] Installing system dependencies..."
sudo apt update
sudo apt install git python3-pip python3-venv -y

# 2. Clone the repository
echo ""
echo "[2/4] Downloading PolliCam software..."
if [ -d "$HOME/YOLO_camera" ]; then
    echo "Directory YOLO_camera already exists. Pulling latest changes..."
    cd $HOME/YOLO_camera
    git reset --hard
    git pull
else
    cd $HOME
    git clone https://github.com/jakubstenc/YOLO_camera.git
fi

# 3. Install Python dependencies
echo ""
echo "[3/4] Installing Python requirements..."
cd $HOME/YOLO_camera/software
pip3 install -r requirements.txt --break-system-packages

# 4. Set up the Systemd Service
echo ""
echo "[4/4] Configuring automatic boot service..."
sudo cp $HOME/YOLO_camera/software/pollicam-ui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pollicam-ui.service
sudo systemctl restart pollicam-ui.service

echo ""
echo "[5/5] Optimizing system for maximum battery life..."
sudo systemctl disable bluetooth.service || true
sudo systemctl disable hciuart.service || true

CONFIG_FILE="/boot/firmware/config.txt"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="/boot/config.txt"
fi

if ! grep -q "dtoverlay=disable-bt" "$CONFIG_FILE"; then
    echo "dtoverlay=disable-bt" | sudo tee -a "$CONFIG_FILE"
fi

if ! grep -q "dtparam=act_led_trigger=none" "$CONFIG_FILE"; then
    echo "dtparam=act_led_trigger=none" | sudo tee -a "$CONFIG_FILE"
    echo "dtparam=act_led_activelow=off" | sudo tee -a "$CONFIG_FILE"
fi

if ! grep -q "dtparam=audio=off" "$CONFIG_FILE"; then
    echo "dtparam=audio=off" | sudo tee -a "$CONFIG_FILE"
fi

# Disable HDMI chip power to save ~25mA
if ! grep -q "vcgencmd display_power 0" /etc/rc.local; then
    # Insert before 'exit 0' in rc.local
    sudo sed -i -e '$i \/usr/bin/vcgencmd display_power 0\n' /etc/rc.local || true
fi

echo ""
echo "======================================"
echo "✅ PolliCam Installation Complete!"
echo "The web interface is now running."
echo "You can access it at: https://$(hostname).local:5000"
echo "Note: The Raspberry Pi may need a quick reboot to apply the battery-saving settings."
echo "======================================"
