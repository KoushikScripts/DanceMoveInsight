import cv2
import mediapipe as mp
import numpy as np
import json
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PoseKeypoints:
    """Container for pose keypoints with confidence scores"""
    landmarks: List[Tuple[float, float, float]]  # (x, y, confidence)
    timestamp: float


class DancePoseDetector:
    """Detects dance poses from video using MediaPipe pose estimation"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Define standard dance poses based on body angles and positions
        self.dance_poses = {
            "arms_up": self._detect_arms_up,
            "arms_crossed": self._detect_arms_crossed,
            "one_arm_up": self._detect_one_arm_up,
            "squat": self._detect_squat,
            "lunge": self._detect_lunge,
            "arabesque": self._detect_arabesque,
            "standing": self._detect_standing
        }
    
    def process_video(self, video_path: str, output_path: str = None) -> Dict:
        """Process video and detect dance poses"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        pose_detections = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = frame_count / fps if fps > 0 else frame_count
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with MediaPipe
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Extract keypoints
                keypoints = self._extract_keypoints(results.pose_landmarks)
                pose_data = PoseKeypoints(keypoints, timestamp)
                
                # Detect dance poses
                detected_poses = self._analyze_poses(pose_data)
                
                if detected_poses:
                    pose_detections.append({
                        "timestamp": timestamp,
                        "poses": detected_poses,
                        "keypoints": keypoints
                    })
            
            frame_count += 1
        
        cap.release()
        
        # Generate summary
        summary = self._generate_summary(pose_detections, duration, total_frames)
        
        # Save to JSON if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
        
        return summary
    
    def _extract_keypoints(self, landmarks) -> List[Tuple[float, float, float]]:
        """Extract keypoints from MediaPipe landmarks"""
        keypoints = []
        for landmark in landmarks.landmark:
            keypoints.append((landmark.x, landmark.y, landmark.visibility))
        return keypoints
    
    def _analyze_poses(self, pose_data: PoseKeypoints) -> List[str]:
        """Analyze keypoints to detect dance poses"""
        detected_poses = []
        
        for pose_name, detector_func in self.dance_poses.items():
            if detector_func(pose_data.landmarks):
                detected_poses.append(pose_name)
        
        return detected_poses
    
    def _get_angle(self, p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
        """Calculate angle between three points"""
        v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
        v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        return np.degrees(angle)
    
    def _detect_arms_up(self, keypoints: List[Tuple[float, float, float]]) -> bool:
        """Detect arms raised up pose"""
        # MediaPipe pose landmarks indices
        left_shoulder = keypoints[11]
        right_shoulder = keypoints[12]
        left_elbow = keypoints[13]
        right_elbow = keypoints[14]
        left_wrist = keypoints[15]
        right_wrist = keypoints[16]
        
        # Check confidence first
        min_confidence = 0.5
        confident = all(kp[2] > min_confidence for kp in [left_shoulder, right_shoulder, left_wrist, right_wrist])
        
        if not confident:
            return False
        
        # Check if both arms are raised (wrists above shoulders)
        left_arm_up = left_wrist[1] < left_shoulder[1] - 0.1
        right_arm_up = right_wrist[1] < right_shoulder[1] - 0.1
        
        return left_arm_up and right_arm_up    

    def _detect_arms_crossed(self, keypoints: List[Tuple[float, float, float]]) -> bool:
        """Detect arms crossed pose"""
        left_wrist = keypoints[15]
        right_wrist = keypoints[16]
        left_shoulder = keypoints[11]
        right_shoulder = keypoints[12]
        
        # Check confidence first
        min_confidence = 0.5
        confident = all(kp[2] > min_confidence for kp in [left_wrist, right_wrist, left_shoulder, right_shoulder])
        
        if not confident:
            return False
        
        # Check if wrists are crossed (left wrist on right side, right wrist on left side)
        crossed = left_wrist[0] > right_shoulder[0] and right_wrist[0] < left_shoulder[0]
        
        return crossed
    
    def _detect_one_arm_up(self, keypoints: List[Tuple[float, float, float]]) -> bool:
        """Detect one arm up pose"""
        left_shoulder = keypoints[11]
        right_shoulder = keypoints[12]
        left_wrist = keypoints[15]
        right_wrist = keypoints[16]
        
        # Check confidence first
        min_confidence = 0.5
        confident = all(kp[2] > min_confidence for kp in [left_shoulder, right_shoulder, left_wrist, right_wrist])
        
        if not confident:
            return False
        
        left_arm_up = left_wrist[1] < left_shoulder[1] - 0.1
        right_arm_up = right_wrist[1] < right_shoulder[1] - 0.1
        
        # Only one arm should be up
        return (left_arm_up and not right_arm_up) or (right_arm_up and not left_arm_up)
    
    def _detect_squat(self, keypoints: List[Tuple[float, float, float]]) -> bool:
        """Detect squat pose"""
        left_hip = keypoints[23]
        right_hip = keypoints[24]
        left_knee = keypoints[25]
        right_knee = keypoints[26]
        left_ankle = keypoints[27]
        right_ankle = keypoints[28]
        
        # Check confidence first
        min_confidence = 0.5
        confident = all(kp[2] > min_confidence for kp in [left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle])
        
        if not confident:
            return False
        
        # Calculate knee angles
        left_knee_angle = self._get_angle(left_hip[:2], left_knee[:2], left_ankle[:2])
        right_knee_angle = self._get_angle(right_hip[:2], right_knee[:2], right_ankle[:2])
        
        # Squat: knees bent (angle < 140 degrees) OR hips significantly lower than standing
        hip_level = (left_hip[1] + right_hip[1]) / 2
        knee_level = (left_knee[1] + right_knee[1]) / 2
        
        # Check if hips are lower (squat position) - knees should be close to hip level
        hip_knee_ratio = abs(hip_level - knee_level)
        squat_detected = (left_knee_angle < 140 and right_knee_angle < 140) or hip_knee_ratio < 0.1
        
        return squat_detected
    
    def _detect_lunge(self, keypoints: List[Tuple[float, float, float]]) -> bool:
        """Detect lunge pose"""
        left_hip = keypoints[23]
        right_hip = keypoints[24]
        left_knee = keypoints[25]
        right_knee = keypoints[26]
        left_ankle = keypoints[27]
        right_ankle = keypoints[28]
        
        # Check confidence first
        min_confidence = 0.5
        confident = all(kp[2] > min_confidence for kp in [left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle])
        
        if not confident:
            return False
        
        # Calculate knee angles
        left_knee_angle = self._get_angle(left_hip[:2], left_knee[:2], left_ankle[:2])
        right_knee_angle = self._get_angle(right_hip[:2], right_knee[:2], right_ankle[:2])
        
        # Lunge: one knee bent significantly more than the other
        angle_diff = abs(left_knee_angle - right_knee_angle)
        lunge_detected = angle_diff > 30 and (left_knee_angle < 120 or right_knee_angle < 120)
        
        return lunge_detected
    
    def _detect_arabesque(self, keypoints: List[Tuple[float, float, float]]) -> bool:
        """Detect arabesque pose (one leg raised behind)"""
        left_hip = keypoints[23]
        right_hip = keypoints[24]
        left_knee = keypoints[25]
        right_knee = keypoints[26]
        left_ankle = keypoints[27]
        right_ankle = keypoints[28]
        
        # Check confidence first
        min_confidence = 0.5
        confident = all(kp[2] > min_confidence for kp in [left_hip, right_hip, left_ankle, right_ankle])
        
        if not confident:
            return False
        
        # Check if one leg is significantly higher than the other
        left_leg_height = left_ankle[1]
        right_leg_height = right_ankle[1]
        hip_level = (left_hip[1] + right_hip[1]) / 2
        
        # One ankle should be above hip level
        arabesque_detected = left_leg_height < hip_level - 0.1 or right_leg_height < hip_level - 0.1
        
        return arabesque_detected
    
    def _detect_standing(self, keypoints: List[Tuple[float, float, float]]) -> bool:
        """Detect basic standing pose"""
        left_shoulder = keypoints[11]
        right_shoulder = keypoints[12]
        left_hip = keypoints[23]
        right_hip = keypoints[24]
        left_knee = keypoints[25]
        right_knee = keypoints[26]
        left_ankle = keypoints[27]
        right_ankle = keypoints[28]
        
        # Check confidence first - include shoulders for overall pose stability
        min_confidence = 0.5
        confident = all(kp[2] > min_confidence for kp in [left_shoulder, right_shoulder, left_hip, right_hip, left_knee, right_knee, left_ankle, right_ankle])
        
        if not confident:
            return False
        
        # Calculate knee angles
        left_knee_angle = self._get_angle(left_hip[:2], left_knee[:2], left_ankle[:2])
        right_knee_angle = self._get_angle(right_hip[:2], right_knee[:2], right_ankle[:2])
        
        # Standing: both knees relatively straight (angle > 160 degrees) AND hips higher than knees
        hip_level = (left_hip[1] + right_hip[1]) / 2
        knee_level = (left_knee[1] + right_knee[1]) / 2
        
        # In standing position, hips should be significantly higher than knees
        hip_knee_distance = knee_level - hip_level
        standing_detected = (left_knee_angle > 160 and right_knee_angle > 160) and hip_knee_distance > 0.1
        
        return standing_detected
    
    def _generate_summary(self, pose_detections: List[Dict], duration: float, total_frames: int) -> Dict:
        """Generate summary of detected poses"""
        if not pose_detections:
            return {
                "video_info": {
                    "duration_seconds": duration,
                    "total_frames": total_frames,
                    "frames_with_poses": 0
                },
                "pose_summary": {},
                "timeline": []
            }
        
        # Count pose occurrences
        pose_counts = {}
        timeline = []
        
        for detection in pose_detections:
            timestamp = detection["timestamp"]
            poses = detection["poses"]
            
            timeline.append({
                "timestamp": round(timestamp, 2),
                "poses": poses
            })
            
            for pose in poses:
                pose_counts[pose] = pose_counts.get(pose, 0) + 1
        
        # Calculate percentages
        total_detections = len(pose_detections)
        pose_summary = {}
        
        for pose, count in pose_counts.items():
            percentage = (count / total_detections) * 100
            pose_summary[pose] = {
                "count": count,
                "percentage": round(percentage, 2)
            }
        
        return {
            "video_info": {
                "duration_seconds": round(duration, 2),
                "total_frames": total_frames,
                "frames_with_poses": total_detections
            },
            "pose_summary": pose_summary,
            "timeline": timeline
        }


def main():
    """Example usage"""
    detector = DancePoseDetector()
    
    # Example usage (uncomment when you have a video file)
    # summary = detector.process_video("dance_video.mp4", "pose_summary.json")
    # print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()