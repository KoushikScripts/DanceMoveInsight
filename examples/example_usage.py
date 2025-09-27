#!/usr/bin/env python3
"""
Example usage of the Dance Pose Detector

This script demonstrates how to use the DancePoseDetector class
to analyze dance videos and detect standard poses.
"""

import json
import sys
from dance_pose_detector import DancePoseDetector


def main():
    """Example usage of the dance pose detector"""
    
    # Initialize the detector
    print("Initializing Dance Pose Detector...")
    detector = DancePoseDetector()
    
    # Example video file path (replace with your actual video)
    video_path = "sample_dance.mp4"
    output_path = "dance_analysis.json"
    
    print(f"Processing video: {video_path}")
    
    try:
        # Process the video
        summary = detector.process_video(video_path, output_path)
        
        # Display results
        print("\n" + "="*50)
        print("DANCE POSE ANALYSIS RESULTS")
        print("="*50)
        
        # Video information
        video_info = summary["video_info"]
        print(f"\nVideo Duration: {video_info['duration_seconds']} seconds")
        print(f"Total Frames: {video_info['total_frames']}")
        print(f"Frames with Poses: {video_info['frames_with_poses']}")
        
        # Pose summary
        print(f"\nDetected Poses:")
        pose_summary = summary["pose_summary"]
        
        if pose_summary:
            for pose_name, stats in pose_summary.items():
                print(f"  {pose_name.replace('_', ' ').title()}: {stats['count']} times ({stats['percentage']}%)")
        else:
            print("  No poses detected")
        
        # Timeline highlights
        print(f"\nTimeline Highlights:")
        timeline = summary["timeline"]
        
        if timeline:
            # Show first few detections
            for i, detection in enumerate(timeline[:5]):
                timestamp = detection["timestamp"]
                poses = ", ".join([p.replace('_', ' ').title() for p in detection["poses"]])
                print(f"  {timestamp}s: {poses}")
            
            if len(timeline) > 5:
                print(f"  ... and {len(timeline) - 5} more detections")
        else:
            print("  No pose detections in timeline")
        
        print(f"\nDetailed results saved to: {output_path}")
        
    except FileNotFoundError:
        print(f"Error: Video file '{video_path}' not found.")
        print("Please provide a valid MP4 video file.")
        return 1
    
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return 1
    
    return 0


def create_sample_video_info():
    """Display information about creating sample videos for testing"""
    print("\nTo test this script, you need an MP4 video file.")
    print("You can:")
    print("1. Record a short dance video with your phone")
    print("2. Download a sample dance video from the internet")
    print("3. Use any MP4 video with people dancing")
    print("\nRecommended video characteristics:")
    print("- Duration: 10-30 seconds")
    print("- Clear view of the dancer")
    print("- Good lighting")
    print("- Dancer should be the main subject in frame")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            create_sample_video_info()
            sys.exit(0)
    
    exit_code = main()
    
    if exit_code != 0:
        print("\nFor help creating sample videos, run:")
        print("python example_usage.py --help")
    
    sys.exit(exit_code)