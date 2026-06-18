import os
import time
import threading
import datetime
from core.identity import get_camera_name
from core.metadata import SessionLogger
from sync.cesnet_uploader import sync_files

def sync_worker():
    """Background thread to periodically run the CESNET uploader."""
    print("[Daemon] Sync worker thread started.")
    while True:
        try:
            sync_files()
        except Exception as e:
            print(f"[Daemon] Sync worker error: {e}")
        # Check for internet/hotspot connection and sync every 60 seconds
        time.sleep(60)

def simulate_yolo_capture(logger: SessionLogger):
    """Simulates recording video and running YOLO detections."""
    print("[Daemon] Starting YOLO capture simulation...")
    
    while True:
        # Simulate creating an image file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dummy_file = os.path.join(logger.output_dir, f"{logger.session_id}_{timestamp}.jpg")
        
        try:
            with open(dummy_file, 'w') as f:
                f.write("Simulated image data")
            print(f"[Daemon] Saved {dummy_file}")
            
            # Simulate YOLO detection updating metadata sidecar
            logger.update_stats(
                frames=1, 
                detections=1, 
                new_classes={"Apis_mellifera": 1}
            )
        except IOError as e:
            print(f"[Daemon] Error writing capture file: {e}")
            
        # Simulate a 15-second delay between captures
        time.sleep(15)
        
def main():
    camera_name = get_camera_name()
    print("=====================================")
    print("       PolliCam Field Daemon         ")
    print(f" Identity: {camera_name}")
    print("=====================================")
    
    # Start the session logger which manages the JSON sidecar
    logger = SessionLogger()
    print(f"[Daemon] Session initialized: {logger.session_id}")
    
    # Start WebDAV sync thread in the background
    sync_thread = threading.Thread(target=sync_worker, daemon=True)
    sync_thread.start()
    
    # Start the main capture loop
    try:
        simulate_yolo_capture(logger)
    except KeyboardInterrupt:
        print("\n[Daemon] KeyboardInterrupt received. Shutting down gracefully...")
        logger.save()

if __name__ == "__main__":
    main()
