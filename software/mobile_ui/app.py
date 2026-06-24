import subprocess
import os
import time
import json
from flask import Flask, Response, render_template_string, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.expanduser("~/monitoring_data")
os.makedirs(BASE_DIR, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>PolliCam Kontrola</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #1e1e1e; color: #e0e0e0; margin: 0; padding: 15px; }
        h1 { font-size: 1.6rem; color: #4caf50; margin-bottom: 5px; }
        .container { max-width: 500px; margin: auto; background: #2d2d2d; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .stream-box { width: 100%; border: 2px solid #444; background: black; border-radius: 5px; overflow: hidden; margin-bottom: 15px; }
        img { width: 100%; height: auto; display: block; }
        .control-group { margin: 12px 0; text-align: left; background: #3a3a3a; padding: 10px; border-radius: 5px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; font-size: 0.9rem; color: #fff; }
        input, select { width: 100%; padding: 10px; box-sizing: border-box; background: #222; color: #fff; border: 1px solid #555; border-radius: 5px; font-size: 1rem; }
        .btn { display: block; width: 100%; padding: 15px; font-size: 1.2rem; font-weight: bold; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; text-transform: uppercase; }
        .btn-start { background: #4caf50; }
        .btn-start:active { background: #388e3c; }
        .btn-stop { background: #f44336; }
        .btn-stop:active { background: #d32f2f; }
        #status-log { font-size: 0.9rem; color: #ffeb3b; margin-top: 15px; padding: 8px; background: #222; border-radius: 3px; min-height: 20px; word-break: break-all; }
    </style>
    <script>
        window.onload = function() {
            let localIso = new Date().toISOString();
            fetch('/sync_time', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ time: localIso })
            })
            .then(res => res.json())
            .then(data => { document.getElementById('status-log').innerText = data.message; });
        };

        function startExperiment() {
            let hours = document.getElementById('duration').value;
            let interval = document.getElementById('interval').value;
            let folder = document.getElementById('folder').value;
            let prefix = document.getElementById('prefix').value;
            
            document.getElementById('status-log').innerText = "Spouštím experiment a vypínám náhled...";
            
            fetch('/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hours: hours, interval: interval, folder: folder, prefix: prefix })
            })
            .then(res => res.json())
            .then(data => { document.getElementById('status-log').innerText = data.message; });
        }

        function stopExperiment() {
            if (confirm("Zastavit monitoring a znovu načíst kameru?")) {
                document.getElementById('status-log').innerText = "Zastavuji focení...";
                fetch('/stop', { method: 'POST' })
                .then(res => res.json())
                .then(data => { 
                    document.getElementById('status-log').innerText = data.message;
                    setTimeout(() => { location.reload(); }, 1500);
                });
            }
        }
        function saveGPSMetadata() {
            let folder = document.getElementById('folder').value;
            let localIso = new Date().toISOString();
            
            document.getElementById('status-log').innerText = "Získávám GPS polohu...";
            
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    fetch('/save_metadata', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            folder: folder,
                            time: localIso,
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            accuracy: position.coords.accuracy
                        })
                    })
                    .then(res => res.json())
                    .then(data => { document.getElementById('status-log').innerText = data.message; });
                }, function(error) {
                    document.getElementById('status-log').innerText = "Chyba GPS: Povolte přístup k poloze.";
                }, { enableHighAccuracy: true });
            } else {
                document.getElementById('status-log').innerText = "GPS není podporováno.";
            }
        }
        function checkDisk() {
            fetch('/disk_space')
            .then(res => res.json())
            .then(data => { alert("Volné místo: " + data.free + " / " + data.total); });
        }

        function updateSystem() {
            if (confirm("Opravdu chcete aktualizovat systém z GitHubu?")) {
                document.getElementById('status-log').innerText = "Aktualizuji...";
                fetch('/update_system', { method: 'POST' })
                .then(res => res.json())
                .then(data => { document.getElementById('status-log').innerText = data.message; });
            }
        }

        function shutdownSystem() {
            if (confirm("Opravdu chcete bezpečně vypnout kameru?")) {
                document.getElementById('status-log').innerText = "Vypínám...";
                fetch('/shutdown', { method: 'POST' })
                .then(res => res.json())
                .then(data => { document.getElementById('status-log').innerText = data.message; });
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>PolliCam v1.6</h1>
        
        <div class="stream-box">
            <img src="/video_feed" alt="Náhled nedostupný (Probíhá focení nebo se načítá)">
        </div>
        
        <div class="control-group">
            <label for="folder">Název složky:</label>
            <input type="text" id="folder" value="pokus_01">
        </div>

        <div class="control-group">
            <label for="prefix">Předpona fotek (prefix):</label>
            <input type="text" id="prefix" value="foto">
        </div>

        <div class="control-group">
            <label for="duration">Doba monitoringu (hodiny):</label>
            <input type="number" id="duration" value="24" min="0.1" max="72" step="0.1">
        </div>

        <div class="control-group">
            <label for="interval">Interval focení (sekundy):</label>
            <select id="interval">
                <option value="2">Každé 2 sekundy</option>
                <option value="3" selected>Každé 3 sekundy</option>
                <option value="5">Každých 5 sekund</option>
                <option value="10">Každých 10 sekund</option>
            </select>
        </div>
        
        <button class="btn btn-start" onclick="startExperiment()">Spustit monitoring</button>
        <button class="btn btn-stop" onclick="stopExperiment()">Zastavit monitoring</button>
        
        <div style="margin-top: 20px;">
            <button class="btn" style="background:#ff9800; padding:10px; font-size:1rem;" onclick="saveGPSMetadata()">Uložit GPS polohu a čas</button>
            <button class="btn" style="background:#555; padding:10px; font-size:1rem;" onclick="checkDisk()">Zkontrolovat místo</button>
            <button class="btn" style="background:#007bff; padding:10px; font-size:1rem;" onclick="updateSystem()">Aktualizovat software</button>
            <button class="btn" style="background:#d32f2f; padding:10px; font-size:1rem;" onclick="shutdownSystem()">Vypnout systém</button>
        </div>
        
        <div id="status-log">Čekám na inicializaci...</div>
    </div>
</body>
</html>
"""

def generate_frames():
    cmd = [
        'rpicam-vid', '-t', '0', 
        '--inline', 
        '-n', 
        '--width', '640', '--height', '480', 
        '--framerate', '10', 
        '--codec', 'mjpeg', 
        '-o', '-'
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
    buffer = b""
    try:
        while True:
            chunk = process.stdout.read(4096)
            if not chunk: break
            buffer += chunk
            a = buffer.find(b'\xff\xd8')
            b = buffer.find(b'\xff\xd9')
            if a != -1 and b != -1 and a < b:
                jpg = buffer[a:b+2]
                buffer = buffer[b+2:]
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')
    finally:
        process.terminate()

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    os.system("pkill -9 -f rpicam-vid")
    time.sleep(0.5)
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sync_time', methods=['POST'])
def sync_time():
    data = request.get_json()
    if not data or 'time' not in data: return jsonify({"message": "Chyba času"}), 400
    try:
        subprocess.run(['sudo', 'date', '-s', data['time']], check=True)
        return jsonify({"message": "Čas úspěšně seřízen podle telefonu."})
    except Exception as e:
        return jsonify({"message": f"Chyba synchronizace: {str(e)}"}), 500

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    hours = float(data.get('hours', 24))
    interval = int(data.get('interval', 3))
    folder_name = data.get('folder', 'pokus_01').strip().replace(" ", "_")
    prefix_name = data.get('prefix', 'foto').strip().replace(" ", "_")
    
    target_dir = os.path.join(BASE_DIR, folder_name)
    os.makedirs(target_dir, exist_ok=True)
    total_seconds = int(hours * 3600)
    
    os.system("pkill -9 -f rpicam-vid")
    os.system("pkill -9 -f rpicam-jpeg")
    os.system("pkill -9 -f sleep")
    time.sleep(1)
    
    bash_script = "end=$((SECONDS + " + str(total_seconds) + ")); while [ $SECONDS -lt $end ]; do rpicam-jpeg -n -o " + target_dir + "/" + prefix_name + "_$(date +%Y%m%d_%H%M%S).jpg --width 1920 --height 1440; sync; sleep " + str(interval) + "; done"
    
    subprocess.Popen(['bash', '-c', bash_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return jsonify({"message": f"Kamera uvolněna. Focení běží! Složka: {folder_name}."})

@app.route('/stop', methods=['POST'])
def stop():
    try:
        os.system("pkill -9 -f rpicam-jpeg")
        os.system("pkill -9 -f rpicam-vid")
        os.system("pkill -9 -f sleep")
        os.system("pkill -f 'rpicam-jpeg -n -o'")
        return jsonify({"message": "Monitoring ZASTAVEN."})
    except Exception as e:
        return jsonify({"message": f"Chyba: {str(e)}"}), 500

@app.route('/save_metadata', methods=['POST'])
def save_metadata():
    data = request.get_json()
    folder_name = data.get('folder', 'pokus_01').strip().replace(" ", "_")
    target_dir = os.path.join(BASE_DIR, folder_name)
    os.makedirs(target_dir, exist_ok=True)
    
    metadata_file = os.path.join(target_dir, "metadata.json")
    metadata = {}
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        except:
            pass
            
    metadata["phone_time"] = data.get("time")
    metadata["gps_latitude"] = data.get("latitude")
    metadata["gps_longitude"] = data.get("longitude")
    metadata["gps_accuracy_meters"] = data.get("accuracy")
    
    try:
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)
        return jsonify({"message": f"GPS a čas úspěšně uloženy do složky {folder_name}!"})
    except Exception as e:
        return jsonify({"message": f"Chyba: {str(e)}"}), 500

@app.route('/disk_space', methods=['GET'])
def disk_space():
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        return jsonify({
            "total": f"{total // (2**30)} GB",
            "free": f"{free // (2**30)} GB"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_system', methods=['POST'])
def update_system():
    try:
        subprocess.Popen(['bash', os.path.expanduser('~/YOLO_camera/software/updater/sync_repo.sh')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return jsonify({"message": "Aktualizace spuštěna. Kamera se může restartovat."})
    except Exception as e:
        return jsonify({"message": f"Chyba aktualizace: {str(e)}"}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        subprocess.Popen(['sudo', 'poweroff'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return jsonify({"message": "Systém se vypíná. Počkejte 20 sekund a odpojte napájení."})
    except Exception as e:
        return jsonify({"message": f"Chyba: {str(e)}"}), 500

if __name__ == '__main__':
    time.sleep(5)
    app.run(host='0.0.0.0', port=5000, threaded=True)
