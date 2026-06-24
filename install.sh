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
echo "======================================"
echo "✅ PolliCam Installation Complete!"
echo "The web interface is now running."
echo "You can access it at: http://$(hostname).local:5000"
echo "======================================"
