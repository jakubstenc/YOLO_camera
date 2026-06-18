import os
import json
import datetime
from .identity import get_camera_name

class SessionLogger:
    """
    Handles logging session metadata and YOLO statistics into a JSON sidecar file.
    """
    def __init__(self, session_id: str = None, output_dir: str = "data/pending_upload"):
        self.camera_name = get_camera_name()
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.session_id = session_id or self.start_time.strftime("%Y%m%d_%H%M%S")
        self.output_dir = output_dir
        
        os.makedirs(self.output_dir, exist_ok=True)
        self.filepath = os.path.join(self.output_dir, f"{self.session_id}_metadata.json")
        
        # Placeholder for YOLO detection statistics
        self.stats = {
            "total_frames": 0,
            "yolo_detections": 0,
            "classes_detected": {}
        }
        
        # Save initial state
        self.save()
        
    def _get_uptime(self) -> float:
        """Returns OS uptime in seconds."""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return uptime_seconds
        except Exception:
            return 0.0
            
    def update_stats(self, frames: int = 0, detections: int = 0, new_classes: dict = None):
        """Update YOLO statistics incrementally."""
        self.stats["total_frames"] += frames
        self.stats["yolo_detections"] += detections
        if new_classes:
            for cls, count in new_classes.items():
                self.stats["classes_detected"][cls] = self.stats["classes_detected"].get(cls, 0) + count
        self.save()
                
    def save(self):
        """Atomically saves the metadata to the JSON sidecar file."""
        data = {
            "camera_name": self.camera_name,
            "session_id": self.session_id,
            "start_time_iso": self.start_time.isoformat(),
            "last_update_iso": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "os_uptime_seconds": self._get_uptime(),
            "yolo_statistics": self.stats
        }
        
        # Write to temp file first to prevent corruption on sudden power loss
        temp_file = f"{self.filepath}.tmp"
        try:
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=4)
            os.rename(temp_file, self.filepath)
        except IOError as e:
            print(f"[SessionLogger] Error saving metadata: {e}")
