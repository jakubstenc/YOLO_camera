"""
# PolliCam Field Daemon

This script serves as the main entry point for the PolliCam edge computing device.
It manages the core lifecycle of a field deployment session, performing two primary tasks simultaneously:

1.  **Continuous Image Capture & Object Detection**: Simulates (and eventually manages)
    the capturing of images and the execution of YOLO-based inference to detect pollinators.
    It tracks real-time statistics (frames processed, detections made) and logs this data
    into a session-specific JSON metadata file.
2.  **Background Data Synchronization**: Runs a separate background thread that periodically
    checks for an internet connection (e.g., via a mobile hotspot) and uploads the locally
    collected images and JSON metadata to a remote CESNET WebDAV server for permanent storage
    and analysis.

## Key Components:
- `sync_worker()`: The daemon thread responsible for periodic file uploads.
- `simulate_yolo_capture()`: The main loop for mock camera capture and inference tracking.
- `main()`: Orchestrates the initialization, thread creation, and graceful shutdown.
"""

import os
import time
import threading
import datetime

# Import helper functions for identifying the current camera and managing metadata
from core.identity import get_camera_name
from core.metadata import SessionLogger

# Import the upload logic for sending files to the central server
from sync.cesnet_uploader import sync_files

def sync_worker():
    """
    Background thread to periodically run the CESNET uploader.
    This runs continuously in the background, independent of the main capture loop.
    """
    print("[Daemon] Sync worker thread started.")
    while True:
        try:
            # Attempt to synchronize local files with the remote CESNET server
            sync_files()
        except Exception as e:
            # Catch any errors (e.g., no internet) so the thread doesn't crash
            print(f"[Daemon] Sync worker error: {e}")
            
        # Check for internet/hotspot connection and sync every 60 seconds
        time.sleep(60)

def simulate_yolo_capture(logger: SessionLogger):
    """
    Simulates recording video and running YOLO detections.
    In a production environment, this would interface with the Pi Camera module
    and the Coral TPU / local GPU for inference.
    """
    print("[Daemon] Starting YOLO capture simulation...")
    
    while True:
        # Simulate creating an image file by generating a unique timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dummy_file = os.path.join(logger.output_dir, f"{logger.session_id}_{timestamp}.jpg")
        
        try:
            # Write a dummy file to the disk to simulate an image capture
            with open(dummy_file, 'w') as f:
                f.write("Simulated image data")
            print(f"[Daemon] Saved {dummy_file}")
            
            # Simulate YOLO detection updating the JSON metadata sidecar
            # This logs that we processed a frame and "found" a bee
            logger.update_stats(
                frames=1, 
                detections=1, 
                new_classes={"Apis_mellifera": 1}
            )
        except IOError as e:
            # Handle potential disk write errors (e.g., SD card full)
            print(f"[Daemon] Error writing capture file: {e}")
            
        # Simulate a 15-second delay between captures to prevent filling the disk too fast
        time.sleep(15)
        
def main():
    """
    Main entry point for the daemon.
    Sets up identity, initializes logging, starts the sync thread, and runs the capture loop.
    """
    # Identify which specific camera this code is running on (e.g., PolliCam_01)
    camera_name = get_camera_name()
    print("=====================================")
    print("       PolliCam Field Daemon         ")
    print(f" Identity: {camera_name}")
    print("=====================================")
    
    # Start the session logger which manages the JSON sidecar for this specific run
    logger = SessionLogger()
    print(f"[Daemon] Session initialized: {logger.session_id}")
    
    # Start WebDAV sync thread in the background as a daemon thread
    # Daemon threads automatically exit when the main program finishes
    sync_thread = threading.Thread(target=sync_worker, daemon=True)
    sync_thread.start()
    
    # Start the main capture loop in the primary thread
    try:
        simulate_yolo_capture(logger)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully to ensure metadata is flushed to disk
        print("\n[Daemon] KeyboardInterrupt received. Shutting down gracefully...")
        logger.save()

if __name__ == "__main__":
    main()
