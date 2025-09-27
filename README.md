# Dance Pose Detector

A Python application that uses MediaPipe and OpenCV to detect and analyze dance poses in video files. The system identifies standard dance poses like arms up, squat, arabesque, and more, providing detailed analysis in JSON format.

## Features

- **Pose Detection**: Detects 7 standard dance poses using MediaPipe pose estimation
- **Video Analysis**: Processes MP4 video files frame by frame
- **JSON Output**: Generates detailed analysis reports in JSON format
- **Timeline Tracking**: Tracks when poses occur throughout the video
- **Confidence Filtering**: Only reports poses with high confidence scores
- **Comprehensive Testing**: Includes unit tests for accuracy validation

## Detected Poses

The system can detect the following dance poses:

1. **Arms Up**: Both arms raised above shoulders
2. **Arms Crossed**: Arms crossed in front of body
3. **One Arm Up**: Single arm raised while other is down
4. **Squat**: Knees bent in squatting position
5. **Lunge**: One leg forward with bent knee, other leg back
6. **Arabesque**: One leg raised behind the body
7. **Standing**: Basic upright standing position

## Installation

1. **Clone or download the project files**

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip install mediapipe==0.10.7 opencv-python==4.8.1.78 numpy==1.24.3 pytest==7.4.3
   ```

## Usage

### Basic Usage

```python
from dance_pose_detector import DancePoseDetector

# Initialize detector
detector = DancePoseDetector()

# Process video and save results
summary = detector.process_video("dance_video.mp4", "analysis.json")

# Print summary
print(f"Detected {len(summary['pose_summary'])} different poses")
```

### Command Line Example

```bash
python example_usage.py
```

### Expected Output Format

The analysis generates a JSON file with the following structure:

```json
{
  "video_info": {
    "duration_seconds": 15.5,
    "total_frames": 465,
    "frames_with_poses": 320
  },
  "pose_summary": {
    "standing": {
      "count": 180,
      "percentage": 56.25
    },
    "arms_up": {
      "count": 85,
      "percentage": 26.56
    },
    "squat": {
      "count": 55,
      "percentage": 17.19
    }
  },
  "timeline": [
    {
      "timestamp": 0.03,
      "poses": ["standing"]
    },
    {
      "timestamp": 0.07,
      "poses": ["standing", "arms_up"]
    }
  ]
}
```

## Testing

Run the comprehensive test suite to validate pose detection accuracy:

```bash
# Run all tests
pytest test_dance_pose_detector.py -v

# Run specific test categories
pytest test_dance_pose_detector.py::TestDancePoseDetector::test_detect_standing_pose -v
pytest test_dance_pose_detector.py::TestDancePoseDetector::test_detect_arms_up_pose -v
```

### Test Coverage

The test suite includes:

- **Unit Tests**: Individual pose detection functions
- **Integration Tests**: Complete workflow testing
- **Accuracy Tests**: Keypoint detection validation
- **Output Format Tests**: JSON structure validation
- **Edge Case Tests**: Low confidence filtering, empty videos
- **Mock Testing**: Video processing without actual video files

## Video Requirements

For best results, use videos with:

- **Duration**: 10-60 seconds
- **Format**: MP4
- **Quality**: Clear view of dancer(s)
- **Lighting**: Good lighting conditions
- **Framing**: Dancer should be main subject in frame
- **Resolution**: 480p or higher recommended

## Technical Details

### Pose Detection Algorithm

1. **Frame Extraction**: Extract frames from MP4 video
2. **Pose Estimation**: Use MediaPipe to detect 33 body keypoints
3. **Angle Calculation**: Calculate joint angles for pose classification
4. **Confidence Filtering**: Only accept keypoints with >50% confidence
5. **Pose Classification**: Match keypoint patterns to standard poses
6. **Timeline Generation**: Track pose occurrences over time

### Key Components

- **DancePoseDetector**: Main class handling video processing
- **PoseKeypoints**: Data structure for pose information
- **Pose Detection Functions**: Individual detectors for each pose type
- **Summary Generation**: Creates comprehensive analysis reports

## Limitations

- Requires clear view of the dancer
- Works best with single dancer in frame
- Lighting conditions affect accuracy
- Some complex dance moves may not be detected
- Currently supports 7 basic pose types

## Extending the System

To add new pose types:

1. Create a new detection function following the pattern:
   ```python
   def _detect_new_pose(self, keypoints: List[Tuple[float, float, float]]) -> bool:
       # Implement pose detection logic
       return pose_detected and confident
   ```

2. Add to the `dance_poses` dictionary in `__init__`:
   ```python
   self.dance_poses["new_pose"] = self._detect_new_pose
   ```

3. Add corresponding unit tests

## Troubleshooting

**Video won't process**:
- Check file path and format (MP4 required)
- Ensure video file isn't corrupted
- Verify OpenCV can read the file

**No poses detected**:
- Check video lighting and quality
- Ensure dancer is clearly visible
- Try adjusting confidence thresholds

**Low accuracy**:
- Use higher quality videos
- Ensure good lighting
- Check that dancer fills significant portion of frame

## Dependencies

- **MediaPipe**: Google's pose estimation framework
- **OpenCV**: Computer vision library for video processing
- **NumPy**: Numerical computing for angle calculations
- **Pytest**: Testing framework for validation

## License

This project is provided as-is for educational and development purposes.