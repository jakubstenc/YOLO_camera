import os
import json

def get_hardware_serial() -> str:
    """
    Securely reads the Raspberry Pi's CPU serial number.
    Tries device tree first, then falls back to /proc/cpuinfo.
    """
    serial = "0000000000000000"
    
    # Try device tree first
    try:
        with open('/sys/firmware/devicetree/base/serial-number', 'r') as f:
            # Device tree strings are null-terminated
            serial = f.read().strip('\0').strip()
            if serial:
                return serial
    except FileNotFoundError:
        pass
        
    # Fallback to /proc/cpuinfo
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    serial = line.split(':')[1].strip()
                    break
    except FileNotFoundError:
        pass
        
    return serial

def get_camera_name(registry_path: str = "fleet_registry.json") -> str:
    """
    Reads the local fleet registry to map the hardware serial to a human-readable name.
    Returns UNKNOWN_<serial> if not found.
    """
    serial = get_hardware_serial()
    
    if os.path.exists(registry_path):
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
                # Map e.g. "000000001a2b3c4d": "PolliCam-01_Handrkov"
                return registry.get(serial, f"UNKNOWN_{serial}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Identity] Error reading {registry_path}: {e}")
            
    return f"UNKNOWN_{serial}"

if __name__ == "__main__":
    print(f"Hardware Serial: {get_hardware_serial()}")
    print(f"Camera Name: {get_camera_name()}")
