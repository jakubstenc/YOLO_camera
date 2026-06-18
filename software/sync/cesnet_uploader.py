import os
import time
import shutil
import requests
from requests.auth import HTTPBasicAuth

PENDING_DIR = "data/pending_upload"
UPLOADED_DIR = "data/uploaded"

def check_internet(test_url="https://1.1.1.1", timeout=3) -> bool:
    """Checks if there is an active internet connection."""
    try:
        requests.get(test_url, timeout=timeout)
        return True
    except requests.RequestException:
        return False

def sync_files():
    """
    Monitors data/pending_upload, uploads files via WebDAV to CESNET,
    and moves them to data/uploaded on success.
    """
    user = os.environ.get("CESNET_USER")
    password = os.environ.get("CESNET_APP_PASSWORD")
    base_url = os.environ.get("CESNET_URL")
    
    if not all([user, password, base_url]):
        print("[Uploader] Error: Missing CESNET credentials in environment variables.")
        return
        
    # Ensure WebDAV endpoint is properly formatted
    if not base_url.endswith("/"):
        base_url += "/"
    webdav_url = base_url + "remote.php/webdav/"
    
    os.makedirs(PENDING_DIR, exist_ok=True)
    os.makedirs(UPLOADED_DIR, exist_ok=True)
    
    pending_files = [f for f in os.listdir(PENDING_DIR) if os.path.isfile(os.path.join(PENDING_DIR, f))]
    
    if not pending_files:
        return # Nothing to upload
        
    if not check_internet():
        print("[Uploader] No internet connection. Skipping sync.")
        return
        
    print(f"[Uploader] Internet connection active. Found {len(pending_files)} files to sync.")
    
    for filename in pending_files:
        file_path = os.path.join(PENDING_DIR, filename)
        target_url = webdav_url + filename
        
        print(f"[Uploader] Uploading {filename}...")
        try:
            with open(file_path, 'rb') as f:
                response = requests.put(
                    target_url, 
                    auth=HTTPBasicAuth(user, password), 
                    data=f, 
                    timeout=120
                )
                
            if response.status_code == 201 or response.status_code == 204:
                print(f"[Uploader] Successfully uploaded {filename}.")
                # Safely move to uploaded
                shutil.move(file_path, os.path.join(UPLOADED_DIR, filename))
            else:
                print(f"[Uploader] Failed to upload {filename}. HTTP Status: {response.status_code}")
                print(f"[Uploader] Response: {response.text}")
                
        except requests.RequestException as e:
            print(f"[Uploader] Network error while uploading {filename}: {e}")
        except IOError as e:
            print(f"[Uploader] File IO error for {filename}: {e}")

if __name__ == "__main__":
    sync_files()
