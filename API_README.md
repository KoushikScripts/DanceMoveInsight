# 🎭 Dance Pose Detection API

A Flask-based REST API for analyzing dance poses in videos using MediaPipe pose estimation.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Activate your virtual environment
source dance/bin/activate

# Install dependencies
pip install -r requirements_flask.txt
```

### 2. Start the API Server
```bash
# Simple start
python flask_api.py

# Or use the startup script with options
python start_api.py --host 0.0.0.0 --port 5000 --debug
```

### 3. Access the API
- **Web Interface**: http://localhost:5000
- **API Documentation**: http://localhost:5000 (with `Accept: application/json` header)
- **Health Check**: http://localhost:5000/health

## 📋 API Endpoints

### `GET /`
- **Web Interface**: Returns HTML upload form
- **API Docs**: Returns JSON documentation (with `Accept: application/json` header)

### `POST /upload`
Upload a video file for pose analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `video` (video file)

**Response:**
```json
{
  "success": true,
  "job_id": "uuid-string",
  "message": "Video processed successfully",
  "result": {
    "video_info": {
      "duration_seconds": 15.5,
      "total_frames": 465,
      "frames_with_poses": 420
    },
    "pose_summary": {
      "standing": {"count": 180, "percentage": 42.86},
      "arms_up": {"count": 95, "percentage": 22.62}
    },
    "timeline": [
      {"timestamp": 0.03, "poses": ["standing"]},
      {"timestamp": 0.07, "poses": ["standing", "arms_up"]}
    ]
  },
  "download_url": "/result/uuid-string"
}
```

### `GET /result/<job_id>`
Get analysis results by job ID.

**Query Parameters:**
- `download=true`: Download as JSON file

**Response:**
```json
{
  "success": true,
  "job_id": "uuid-string",
  "result": { /* analysis results */ }
}
```

### `GET /results`
List all available analysis results.

**Response:**
```json
{
  "success": true,
  "total_results": 5,
  "results": [
    {
      "job_id": "uuid-string",
      "created_at": 1640995200,
      "size_bytes": 2048,
      "download_url": "/result/uuid-string?download=true"
    }
  ]
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "dance-pose-detector",
  "version": "1.0.0"
}
```

## 🎯 Detected Poses

The API can detect the following dance poses:

1. **Standing** - Basic upright standing position
2. **Arms Up** - Both arms raised above shoulders
3. **Arms Crossed** - Arms crossed in front of body
4. **One Arm Up** - Single arm raised
5. **Squat** - Knees bent, lowered position
6. **Lunge** - One leg forward, one back
7. **Arabesque** - One leg raised behind

## 📊 JSON Output Format

The analysis results include:

### Video Information
- `duration_seconds`: Video length in seconds
- `total_frames`: Total number of frames processed
- `frames_with_poses`: Number of frames where poses were detected

### Pose Summary
For each detected pose:
- `count`: Number of times the pose was detected
- `percentage`: Percentage of total detections

### Timeline
Chronological list of pose detections:
- `timestamp`: Time in seconds when pose was detected
- `poses`: Array of pose names detected at that timestamp

## 🔧 Configuration

### File Limits
- **Max file size**: 100MB
- **Supported formats**: MP4, AVI, MOV, MKV, WMV, FLV, WebM

### Directories
- `uploads/`: Temporary storage for uploaded videos (auto-cleaned)
- `results/`: Persistent storage for analysis results
- `templates/`: HTML templates for web interface

## 🧪 Testing

### Run API Tests
```bash
# Start the API server first
python flask_api.py

# In another terminal, run tests
python test_api.py
```

### Manual Testing with cURL

**Upload a video:**
```bash
curl -X POST -F "video=@your_video.mp4" http://localhost:5000/upload
```

**Get results:**
```bash
curl http://localhost:5000/result/your-job-id
```

**Download results:**
```bash
curl "http://localhost:5000/result/your-job-id?download=true" -o results.json
```

## 🌐 Web Interface Features

The HTML interface provides:

- **Drag & Drop Upload**: Drag video files directly onto the upload area
- **File Validation**: Checks file format and size before upload
- **Progress Indication**: Visual feedback during processing
- **Results Visualization**: 
  - Video information summary
  - Pose detection statistics with percentages
  - Interactive timeline viewer
  - Download options for full results

## 🚨 Error Handling

The API provides detailed error responses:

### Common Error Codes
- `400`: Bad request (invalid file, missing parameters)
- `404`: Resource not found (invalid job ID)
- `413`: File too large (exceeds 100MB limit)
- `500`: Internal server error (processing failure)

### Error Response Format
```json
{
  "error": "Error Type",
  "message": "Detailed error description",
  "job_id": "uuid-string" // if applicable
}
```

## 🔒 Security Considerations

- File uploads are validated for type and size
- Uploaded files are automatically cleaned up after processing
- Secure filename handling prevents directory traversal
- Results are stored with UUID-based filenames

## 📈 Performance Notes

- Processing time depends on video length and complexity
- Typical processing: ~1-2x video duration
- Memory usage scales with video resolution
- Results are cached for future retrieval

## 🛠️ Development

### Project Structure
```
├── flask_api.py              # Main Flask application
├── dance_pose_detector.py    # Core pose detection logic
├── start_api.py             # Startup script with options
├── test_api.py              # API test suite
├── requirements_flask.txt    # Python dependencies
├── templates/
│   └── upload.html          # Web interface
├── uploads/                 # Temporary upload storage
└── results/                 # Analysis results storage
```

### Adding New Poses

To add new pose detection:

1. Add detection method to `DancePoseDetector` class
2. Register in `dance_poses` dictionary
3. Update API documentation
4. Add tests for new pose

### Customizing the Web Interface

Edit `templates/upload.html` to modify:
- Styling and layout
- Upload behavior
- Results visualization
- Additional features

## 📞 Support

For issues or questions:
1. Check the health endpoint: `/health`
2. Review error messages in API responses
3. Check server logs for detailed error information
4. Verify file format and size requirements