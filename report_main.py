import json
import subprocess
import os
import sys
import signal
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global data storage (in-memory)
data_store = {
    "title": "ADAM",
    "name": "Waiting for Analysis...",
    "time": "--/--/-- --:--:--",
    "person_name": "Guest",
    "organization": "Service Industry",
    "total_score": 0.0,
    "audio_score": 0.0,
    "text_score": 0.0,
    "facial_score": 0.0,
    "ai_text1": "尚無分析資料。請執行分析程式。",
    "ai_text2": "...",
    "ai_text3": "...",
    "charts": []
}

# System Control Globals
system_process = None
current_config = {"camera_mode": os.getenv('CAMERA_MODE', 'SINGLE').upper()}

def load_latest_data():
    """Load data from JSON file if exists"""
    try:
        json_path = Path('static/data/analysis_result.json')
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                new_data = json.load(f)
                data_store.update(new_data)
                return True
    except Exception as e:
        print(f"Error loading data: {e}")
    return False


@app.route('/')
def report():
    """Render main report page"""
    load_latest_data()  # Refresh data on page load
    return render_template('index.html', data=data_store)


@app.route('/update', methods=['POST'])
def update_data():
    """Update data store with new values"""
    new_data = request.json
    data_store.update(new_data)
    return jsonify({"status": "success"})


@app.route('/api/report')
def api_report():
    """Return full report data as JSON"""
    load_latest_data()  # Refresh data on API call
    return jsonify(data_store)


@app.route('/api/charts')
def api_charts():
    """Return chart files metadata with existence check"""
    from pathlib import Path
    
    charts_dir = Path('static')
    charts_info = []
    
    for chart_file in data_store.get('charts', []):
        chart_path = charts_dir / chart_file
        charts_info.append({
            'filename': chart_file,
            'url': f'/static/{chart_file}',
            'exists': chart_path.exists(),
            'size': chart_path.stat().st_size if chart_path.exists() else 0
        })
    
    return jsonify({'charts': charts_info})


# --- System Control APIs ---

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """查詢系統狀態"""
    global system_process
    is_running = system_process is not None and system_process.poll() is None
    return jsonify({
        "running": is_running,
        "camera_mode": current_config["camera_mode"],
        "pid": system_process.pid if is_running else None,
        "python_path": sys.executable
    })


@app.route('/api/system/start', methods=['POST'])
def start_system():
    """啟動系統"""
    global system_process, current_config
    
    # 1. 檢查是否已經在執行
    if system_process is not None and system_process.poll() is None:
        return jsonify({"status": "error", "message": "System is already running"}), 400
        
    # 2. 取得參數
    data = request.json or {}
    mode = data.get('camera_mode', 'DUAL').upper()
    if mode not in ['SINGLE', 'DUAL']:
        return jsonify({"status": "error", "message": "Invalid mode"}), 400
        
    current_config["camera_mode"] = mode
    
    # 3. 準備環境變數
    env = os.environ.copy()
    env['CAMERA_MODE'] = mode
    env['PYTHONPATH'] = os.getcwd()
    
    try:
        # 4. 啟動 Auto_Switch_refactored.py
        cmd = [sys.executable, 'Auto_Switch_refactored.py']
        
        # Ensure logs directory exists
        Path('logs').mkdir(exist_ok=True)
        
        # Redirect output to a file for debugging
        log_file = open('logs/system_startup.log', 'w')
        
        system_process = subprocess.Popen(
            cmd,
            env=env,
            cwd=os.getcwd(),
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        
        return jsonify({
            "status": "success", 
            "message": f"System started in {mode} mode",
            "pid": system_process.pid
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """停止系統"""
    global system_process
    
    if system_process is None or system_process.poll() is not None:
        return jsonify({"status": "warning", "message": "System is not running"}), 200
        
    try:
        # 嘗試優雅結束
        system_process.terminate()
        
        # 等待一下，如果還沒死就強制結束
        try:
            system_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            system_process.kill()
            
        system_process = None
        return jsonify({"status": "success", "message": "System stopped"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
