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

### 🌐 Live Demo (Try it now!)

**🎭 Test the API live at: [http://51.21.190.200:80](http://51.21.190.200:80)**

- Upload a dance video and see the pose analysis in action
- No setup required - just visit the URL and start testing!

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

| Method | Endpoint | Description | Live Demo |
|--------|----------|-------------|-----------|
| `POST` | `/upload` | Upload video for pose analysis | [Try it](http://51.21.190.200:80) |
| `GET`  | `/health` | API health check | [Check Status](http://51.21.190.200:80/health) |
| `GET`  | `/` | Web upload interface | [Web UI](http://51.21.190.200:80) |

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

### 🧪 Test the Live API

```bash
# Test health endpoint
curl http://51.21.190.200:80/health

# Upload a video for analysis
curl -X POST -F "video=@your_dance_video.mp4" http://51.21.190.200:80/upload
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

## 🎬 Try It Now!

**🌟 Live Demo**: [http://51.21.190.200:80](http://51.21.190.200:80)

**Ready to analyze some dance moves? 🕺💃**

1. **Quick Test**: Visit the live demo above
2. **Local Setup**: `docker run -p 5000:5000 dancemoves:latest`
3. **Development**: Clone this repo and start coding!

### 📱 How to Use the Live Demo:
1. Visit [http://51.21.190.200:80](http://51.21.190.200:80)
2. Upload a dance video (MP4, AVI, MOV, etc.)
3. Wait for the analysis to complete
4. View the detailed pose detection results!

**Example videos to try:**
- Short dance clips (10-30 seconds work best)
- Clear view of the dancer
- Good lighting conditions