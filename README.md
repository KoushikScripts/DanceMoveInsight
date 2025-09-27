# 🎭 DanceMoveInsight

A Flask-based REST API for analyzing dance poses in videos using MediaPipe and OpenCV.

## ✨ Features

- **🎥 Video Upload**: Support for multiple video formats (MP4, AVI, MOV, etc.)
- **🕺 Pose Detection**: Real-time dance pose analysis using MediaPipe
- **🔌 REST API**: Clean JSON API endpoints
- **🌐 Web Interface**: Simple HTML upload interface
- **🐳 Docker Support**: Containerized deployment ready
- **💾 Result Storage**: Persistent storage of analysis results

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Run the pre-built image
docker run -p 5000:5000 dancemoves:latest

# Or build from source
docker build -t dancemoves .
docker run -p 5000:5000 dancemoves
```

### Local Development

```bash
# Install dependencies
pip install -r requirements_flask.txt

# Run the Flask app
python flask_api.py
```

Access the API at `http://localhost:5000`

## 📁 Project Structure

```
DanceMoveInsight/
├── 📄 Core Application Files
│   ├── flask_api.py              # Main Flask API server
│   ├── dance_pose_detector.py    # Pose detection logic
│   ├── config.py                 # Configuration settings
│   └── requirements_flask.txt    # Python dependencies
│
├── 🐳 Docker & Deployment
│   ├── Dockerfile                # Docker container configuration
│   └── deployment/               # Deployment scripts and configs
│       ├── aws/                  # AWS ECS deployment
│       ├── scripts/              # Deployment automation
│       └── docker-compose.yml    # Local development setup
│
├── 📚 Documentation
│   └── docs/                     # All documentation files
│       ├── API_README.md         # API documentation
│       ├── DEPLOYMENT.md         # Deployment guide
│       └── FLASK_API_SUMMARY.md  # Technical summary
│
├── 🧪 Testing
│   └── tests/                    # Test files
│       ├── test_api.py           # API endpoint tests
│       └── test_dance_pose_detector.py  # Core logic tests
│
├── 💡 Examples
│   └── examples/                 # Example usage and demos
│       ├── example_usage.py      # Usage examples
│       └── demo_json_output.py   # Output format demos
│
├── 🎨 Frontend
│   └── templates/                # HTML templates
│       └── upload.html           # Web upload interface
│
└── 📊 Results
    └── results/                  # Analysis results storage
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload video for pose analysis |
| `GET`  | `/health` | API health check |
| `GET`  | `/` | Web upload interface |

## 🕺 Detected Poses

1. **Arms Up**: Both arms raised above shoulders
2. **Arms Crossed**: Arms crossed in front of body  
3. **One Arm Up**: Single arm raised while other is down
4. **Squat**: Knees bent in squatting position
5. **Lunge**: One leg forward with bent knee, other leg back
6. **Arabesque**: One leg raised behind the body
7. **Standing**: Basic upright standing position

## 📋 Supported Formats

- **Video**: MP4, AVI, MOV, WMV, MKV, FLV, WEBM
- **Max Size**: 100MB
- **Recommended**: MP4 for best compatibility

## 🛠️ Development

```bash
# Run tests
python -m pytest tests/

# Start development server
python flask_api.py

# Run examples
python examples/example_usage.py
```

## 📖 Documentation

- **API Guide**: [`docs/API_README.md`](docs/API_README.md)
- **Deployment**: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)
- **Examples**: [`examples/`](examples/)

## 🔧 Requirements

- Python 3.8+
- OpenCV 4.8+
- MediaPipe 0.10+
- Flask 3.0+

---

**Ready to analyze some dance moves? 🕺💃**

Start with: `docker run -p 5000:5000 dancemoves:latest`