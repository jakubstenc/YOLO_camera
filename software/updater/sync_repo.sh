#!/bin/bash
# sync_repo.sh
# PolliCam OTA Update Script

REPO_DIR="/home/pi/YOLO_camera"

if [ ! -d "$REPO_DIR" ]; then
    echo "[OTA] Error: Repository directory $REPO_DIR not found."
    exit 1
fi

cd "$REPO_DIR" || exit 1

echo "[OTA] Checking for internet connection..."
ping -c 1 8.8.8.8 > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[OTA] No internet connection. Aborting update."
    exit 1
fi

echo "[OTA] Fetching latest changes from GitHub..."
git fetch origin main

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u} 2>/dev/null || git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "[OTA] System is up to date."
else
    echo "[OTA] Updates found. Applying..."
    # Stash any local changes to prevent merge conflicts
    git stash
    git pull origin main
    
    echo "[OTA] Restarting PolliCam services..."
    # Restart the daemon and mobile UI if they are running as systemd services
    sudo systemctl restart pollicam-daemon.service || true
    sudo systemctl restart pollicam-ui.service || true
    
    echo "[OTA] Update complete!"
fi
