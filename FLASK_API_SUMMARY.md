# 🎭 Dance Pose Detection Flask API - Complete Setup

## ✅ What We Built

### 1. **JSON Output Format**
The API returns structured JSON with three main sections:

```json
{
  "video_info": {
    "duration_seconds": 15.5,
    "total_frames": 465,
    "frames_with_poses": 420
  },
  "pose_summary": {
    "standing": {"count": 180, "percentage": 42.86},
    "arms_up": {"count": 95, "percentage": 22.62},
    "squat": {"count": 75, "percentage": 17.86}
  },
  "timeline": [
    {"timestamp": 0.03, "poses": ["standing"]},
    {"timestamp": 0.07, "poses": ["standing", "arms_up"]}
  ]
}
```

### 2. **Flask API Server** (`flask_api.py`)
- **Video Upload**: POST `/upload` - Upload videos up to 100MB
- **Results Retrieval**: GET `/result/<job_id>` - Get analysis results
- **Web Interface**: GET `/` - HTML upload form with drag & drop
- **Health Check**: GET `/health` - Server status
- **Results List**: GET `/results` - List all processed videos

### 3. **Web Interface** (`templates/upload.html`)
- Beautiful drag & drop upload interface
- Real-time progress indication
- Visual results display with pose statistics
- Timeline viewer for pose sequences
- Download options for full JSON results

### 4. **Supporting Tools**
- **`start_api.py`**: Easy server startup with options
- **`test_api.py`**: Comprehensive API testing suite
- **`demo_json_output.py`**: JSON format demonstration
- **`API_README.md`**: Complete API documentation

## 🚀 How to Use

### Start the Server
```bash
# Activate virtual environment
source dance/bin/activate

# Start with default settings
python flask_api.py

# Or use startup script with options
python start_api.py --host 0.0.0.0 --port 5000 --debug
```

### Upload Videos
**Option 1: Web Interface**
- Open http://localhost:5000
- Drag & drop video or click to select
- View results instantly with visual statistics

**Option 2: API Endpoint**
```bash
curl -X POST -F "video=@dance.mp4" http://localhost:5000/upload
```

**Option 3: Python Requests**
```python
import requests

with open('dance_video.mp4', 'rb') as f:
    files = {'video': f}
    response = requests.post('http://localhost:5000/upload', files=files)
    result = response.json()
    print(f"Job ID: {result['job_id']}")
```

## 🎯 Detected Poses

The system can identify 7 different dance poses:

1. **Standing** - Basic upright position
2. **Arms Up** - Both arms raised above shoulders  
3. **Arms Crossed** - Arms crossed in front
4. **One Arm Up** - Single arm raised
5. **Squat** - Knees bent, lowered position
6. **Lunge** - One leg forward, one back
7. **Arabesque** - One leg raised behind

## 📊 Output Analysis

### Video Information
- **Duration**: Total video length in seconds
- **Total Frames**: Number of frames processed
- **Frames with Poses**: Frames where poses were detected

### Pose Summary
- **Count**: Number of times each pose was detected
- **Percentage**: Relative frequency of each pose

### Timeline
- **Timestamp**: Exact time when poses were detected
- **Poses**: Multiple poses can be detected simultaneously

## 🔧 Configuration

### File Limits
- **Maximum size**: 100MB per video
- **Supported formats**: MP4, AVI, MOV, MKV, WMV, FLV, WebM

### Server Settings
- **Host**: 0.0.0.0 (accessible from network)
- **Port**: 5000 (default)
- **Debug mode**: Available for development

## 🧪 Testing

### Run Test Suite
```bash
# Start server first
python flask_api.py

# In another terminal
python test_api.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:5000/health

# Upload video
curl -X POST -F "video=@test.mp4" http://localhost:5000/upload

# Get results
curl http://localhost:5000/result/your-job-id

# Download JSON
curl "http://localhost:5000/result/your-job-id?download=true" -o results.json
```

## 📁 File Structure

```
├── flask_api.py              # Main Flask application
├── dance_pose_detector.py    # Core pose detection
├── start_api.py             # Server startup script
├── test_api.py              # API test suite
├── demo_json_output.py      # JSON format demo
├── requirements_flask.txt    # Flask dependencies
├── API_README.md            # Detailed documentation
├── templates/
│   └── upload.html          # Web interface
├── uploads/                 # Temporary storage
├── results/                 # Analysis results
└── example_output.json      # Sample output format
```

## 🌟 Key Features

### For Developers
- **RESTful API**: Standard HTTP methods and status codes
- **JSON Responses**: Structured, predictable data format
- **Error Handling**: Detailed error messages and codes
- **File Validation**: Type and size checking
- **UUID Job IDs**: Unique identifiers for each analysis

### For Users
- **Drag & Drop**: Intuitive file upload
- **Visual Results**: Charts and statistics
- **Timeline View**: See pose changes over time
- **Download Options**: Get full JSON results
- **Progress Feedback**: Real-time upload/processing status

### For Production
- **Security**: File validation and secure uploads
- **Cleanup**: Automatic temporary file removal
- **Scalability**: Stateless design for horizontal scaling
- **Monitoring**: Health check endpoint
- **Documentation**: Complete API reference

## 🎉 Ready to Use!

Your Dance Pose Detection API is now complete and ready for:

1. **Development**: Test with the web interface
2. **Integration**: Use the REST API in your applications
3. **Production**: Deploy with a proper WSGI server
4. **Scaling**: Add load balancing and database storage

The system provides a complete solution for analyzing dance videos with professional-grade pose detection and user-friendly interfaces! 🕺💃