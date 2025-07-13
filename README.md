# Flask Keylogger Web Interface

A comprehensive web-based keylogger application built with Python and Flask, providing secure remote monitoring and analysis capabilities. This tool captures keystrokes using the `pynput` library, stores them as structured JSON logs, and offers both web interface and REST API endpoints for interaction.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Log File Format](#log-file-format)
- [Analytics](#analytics)
- [Security Considerations](#security-considerations)
- [Legal Disclaimer](#legal-disclaimer)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality
- **Remote Control**: Start and stop keylogging sessions via web interface or REST API
- **Real-time Monitoring**: View keystroke logs as they are captured
- **Text Reconstruction**: Intelligent reconstruction of typed text from raw keystrokes
- **Session Management**: List, view, and download previous keylogging sessions
- **Analytics Dashboard**: Comprehensive statistics including word frequency, typing patterns, and session metrics

### Technical Features
- **JSON-based Storage**: Structured log format with timestamp and key type classification
- **Graceful Shutdown**: Clean termination handling with proper resource cleanup
- **Cross-platform Support**: Compatible with Windows, macOS, and Linux
- **RESTful API**: Complete API endpoints for programmatic integration

## Prerequisites

- **Python**: Version 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Permissions**: Administrative privileges may be required for keystroke capture

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/flask-keylogger.git
cd flask-keylogger
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install flask pynput
```

## Project Structure

```
flask-keylogger/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── templates/
│   └── index.html           # Web interface template
├── static/                  # CSS, JS, and other static files
│   ├── css/
│   ├── js/
│   └── images/
├── keylogs/                 # Auto-generated log storage directory
└── tests/                   # Unit and integration tests
```

## Usage

### Starting the Application

1. **Run the Flask server**:
   ```bash
   python app.py
   ```

2. **Access the web interface**:
   ```
   http://localhost:5000
   ```

3. **Start keylogging**:
   - Click "Start Keylogger" in the web interface, or
   - Send a POST request to `/start` endpoint

### Configuration

The application can be configured by modifying the following variables in `app.py`:

```python
# Server configuration
HOST = '127.0.0.1'
PORT = 5000
DEBUG = False

# Logging configuration
LOG_DIRECTORY = 'keylogs'
LOG_FORMAT = 'session_%Y%m%d_%H%M%S.json'
```

## API Documentation

### Authentication
Currently, the API does not require authentication. For production use, implement proper authentication mechanisms.

### Endpoints

| Endpoint | Method | Description | Response Format |
|----------|--------|-------------|-----------------|
| `/` | GET | Web interface homepage | HTML |
| `/start` | POST | Start keylogger session | JSON |
| `/stop` | POST | Stop active keylogger session | JSON |
| `/status` | GET | Get current keylogger status | JSON |
| `/files` | GET | List all saved keylog files | JSON |
| `/view/<filename>` | GET | View and analyze specific keylog file | JSON |
| `/download/<filename>` | GET | Download keylog file | File |

### Example API Responses

**Start Keylogger**:
```json
{
  "status": "success",
  "message": "Keylogger started",
  "session_id": "session_20250713_134500",
  "timestamp": "2025-07-13T13:45:00Z"
}
```

**Get Status**:
```json
{
  "active": true,
  "session_id": "session_20250713_134500",
  "start_time": "2025-07-13T13:45:00Z",
  "keys_captured": 1247
}
```

## Log File Format

Each keystroke is stored as a JSON line with the following structure:

```json
{
  "timestamp": "2025-07-13T13:45:00.123456Z",
  "key": "a",
  "type": "character",
  "session_id": "session_20250713_134500"
}
```

### Key Types
- **character**: Regular alphanumeric characters
- **special**: Special keys (Enter, Space, Tab, etc.)
- **modifier**: Modifier keys (Ctrl, Alt, Shift, etc.)
- **function**: Function keys (F1-F12)

## Analytics

The analytics engine provides comprehensive insights:

### Text Reconstruction
- Intelligent handling of backspace and delete operations
- Proper spacing and line break reconstruction
- Support for special character combinations

### Statistical Analysis
- **Typing Metrics**: WPM, accuracy, session duration
- **Key Frequency**: Most used keys and key combinations
- **Word Analysis**: Word frequency, average word length
- **Pattern Recognition**: Typing patterns and common mistakes

### Example Analytics Output

```json
{
  "session_summary": {
    "total_keys": 1247,
    "duration_minutes": 15.5,
    "words_per_minute": 45.2,
    "characters_per_minute": 226
  },
  "reconstructed_text": "The quick brown fox jumps over the lazy dog.",
  "key_statistics": {
    "most_frequent_keys": ["e", "t", "a", "o", "i"],
    "special_key_count": 89,
    "backspace_count": 23
  },
  "word_analysis": {
    "total_words": 312,
    "unique_words": 156,
    "average_word_length": 4.8,
    "most_common_words": ["the", "and", "to", "a", "in"]
  }
}
```

## Security Considerations

### Important Security Notes
- **Network Security**: The application runs on localhost by default. Avoid exposing it to external networks without proper security measures.
- **Data Encryption**: Consider encrypting log files for sensitive environments.
- **Access Control**: Implement authentication and authorization for production deployments.
- **Log Retention**: Establish policies for log retention and secure deletion.

### Recommended Security Practices
1. Use HTTPS in production environments
2. Implement rate limiting for API endpoints
3. Add input validation and sanitization
4. Use secure session management
5. Regular security audits and updates

## Legal Disclaimer

**⚠️ IMPORTANT LEGAL NOTICE**

This software is provided for **educational and authorized testing purposes only**. Users are solely responsible for ensuring compliance with all applicable laws and regulations.

### Legal Requirements
- **Explicit Consent**: Obtain explicit written consent from all users before deployment
- **Legal Compliance**: Ensure compliance with local privacy and surveillance laws
- **Data Protection**: Follow applicable data protection regulations (GDPR, CCPA, etc.)
- **Workplace Policies**: Verify compliance with organizational policies and employment laws

### Prohibited Uses
- Unauthorized monitoring of individuals
- Deployment without proper legal authorization
- Collection of sensitive personal information without consent
- Any use that violates privacy rights or applicable laws

**The developers assume no responsibility for misuse of this software.**

## Contributing

We welcome contributions to improve this project. Please follow these guidelines:

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Add unit tests for new features
- Update documentation as needed

### Reporting Issues
Please use the GitHub issue tracker to report bugs or request features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Version**: 1.0.0  
**Last Updated**: July 13, 2025  
**Maintained by**: [Your Name/Organization]

For support and questions, please open an issue on GitHub or contact [your-email@example.com].