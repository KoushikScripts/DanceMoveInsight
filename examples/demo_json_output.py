#!/usr/bin/env python3
"""
Demo script showing the JSON output format of the Dance Pose Detector
"""

import json
from dance_pose_detector import DancePoseDetector

def create_mock_pose_detections():
    """Create mock pose detection data for demonstration"""
    return [
        {
            "timestamp": 0.03,
            "poses": ["standing"],
            "keypoints": [(0.5, 0.3, 0.9)] * 33  # Mock keypoints
        },
        {
            "timestamp": 0.07,
            "poses": ["standing", "arms_up"],
            "keypoints": [(0.5, 0.3, 0.9)] * 33
        },
        {
            "timestamp": 0.10,
            "poses": ["arms_up"],
            "keypoints": [(0.5, 0.3, 0.9)] * 33
        },
        {
            "timestamp": 2.15,
            "poses": ["squat"],
            "keypoints": [(0.5, 0.3, 0.9)] * 33
        },
        {
            "timestamp": 5.42,
            "poses": ["arms_crossed"],
            "keypoints": [(0.5, 0.3, 0.9)] * 33
        },
        {
            "timestamp": 8.73,
            "poses": ["one_arm_up"],
            "keypoints": [(0.5, 0.3, 0.9)] * 33
        },
        {
            "timestamp": 12.18,
            "poses": ["standing"],
            "keypoints": [(0.5, 0.3, 0.9)] * 33
        }
    ]

def main():
    """Demonstrate the JSON output format"""
    print("🎭 Dance Pose Detector - JSON Output Format Demo")
    print("=" * 60)
    
    # Create detector instance
    detector = DancePoseDetector()
    
    # Create mock data
    mock_detections = create_mock_pose_detections()
    duration = 15.5
    total_frames = 465
    
    # Generate summary using the actual method
    summary = detector._generate_summary(mock_detections, duration, total_frames)
    
    print("📊 Example JSON Output:")
    print("-" * 30)
    print(json.dumps(summary, indent=2))
    
    print("\n" + "=" * 60)
    print("📋 JSON Structure Explanation:")
    print("-" * 30)
    
    print("\n🎬 video_info:")
    print("  • duration_seconds: Total video length in seconds")
    print("  • total_frames: Number of frames processed")
    print("  • frames_with_poses: Frames where poses were detected")
    
    print("\n🎯 pose_summary:")
    print("  • For each detected pose type:")
    print("    - count: Number of detections")
    print("    - percentage: Percentage of total detections")
    
    print("\n⏰ timeline:")
    print("  • Chronological list of pose detections:")
    print("    - timestamp: Time in seconds")
    print("    - poses: Array of pose names detected")
    
    print("\n🎭 Available Pose Types:")
    print("-" * 30)
    pose_descriptions = {
        "standing": "Basic upright standing position",
        "arms_up": "Both arms raised above shoulders",
        "arms_crossed": "Arms crossed in front of body",
        "one_arm_up": "Single arm raised",
        "squat": "Knees bent, lowered position",
        "lunge": "One leg forward, one back",
        "arabesque": "One leg raised behind"
    }
    
    for pose, description in pose_descriptions.items():
        print(f"  • {pose}: {description}")
    
    print("\n" + "=" * 60)
    print("🚀 Usage Examples:")
    print("-" * 30)
    
    print("\n📤 Flask API Upload:")
    print("curl -X POST -F 'video=@dance.mp4' http://localhost:5000/upload")
    
    print("\n📥 Get Results:")
    print("curl http://localhost:5000/result/your-job-id")
    
    print("\n💾 Download JSON:")
    print("curl 'http://localhost:5000/result/your-job-id?download=true' -o results.json")
    
    print("\n🌐 Web Interface:")
    print("Open http://localhost:5000 in your browser")
    
    print("\n" + "=" * 60)
    print("✨ Ready to analyze your dance videos!")

if __name__ == "__main__":
    main()