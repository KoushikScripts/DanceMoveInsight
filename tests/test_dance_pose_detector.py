import pytest
import numpy as np
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from dance_pose_detector import DancePoseDetector, PoseKeypoints


class TestDancePoseDetector:
    """Test suite for DancePoseDetector class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.detector = DancePoseDetector()
        
        # Create mock keypoints for different poses
        self.mock_keypoints_standing = self._create_mock_keypoints_standing()
        self.mock_keypoints_arms_up = self._create_mock_keypoints_arms_up()
        self.mock_keypoints_squat = self._create_mock_keypoints_squat()
        self.mock_keypoints_arms_crossed = self._create_mock_keypoints_arms_crossed()
    
    def _create_mock_keypoints_standing(self):
        """Create mock keypoints for standing pose"""
        # MediaPipe has 33 landmarks, we'll focus on key ones
        keypoints = [(0.5, 0.5, 0.9)] * 33  # Default position with high confidence
        
        # Set specific positions for standing pose
        keypoints[11] = (0.4, 0.3, 0.9)  # left shoulder
        keypoints[12] = (0.6, 0.3, 0.9)  # right shoulder
        keypoints[15] = (0.35, 0.5, 0.9)  # left wrist (down)
        keypoints[16] = (0.65, 0.5, 0.9)  # right wrist (down)
        keypoints[23] = (0.45, 0.6, 0.9)  # left hip
        keypoints[24] = (0.55, 0.6, 0.9)  # right hip
        keypoints[25] = (0.45, 0.8, 0.9)  # left knee
        keypoints[26] = (0.55, 0.8, 0.9)  # right knee
        keypoints[27] = (0.45, 0.95, 0.9)  # left ankle
        keypoints[28] = (0.55, 0.95, 0.9)  # right ankle
        
        return keypoints
    
    def _create_mock_keypoints_arms_up(self):
        """Create mock keypoints for arms up pose"""
        keypoints = self._create_mock_keypoints_standing().copy()
        
        # Raise both arms (wrists above shoulders)
        keypoints[15] = (0.35, 0.1, 0.9)  # left wrist (up)
        keypoints[16] = (0.65, 0.1, 0.9)  # right wrist (up)
        
        return keypoints
    
    def _create_mock_keypoints_squat(self):
        """Create mock keypoints for squat pose"""
        keypoints = self._create_mock_keypoints_standing().copy()
        
        # Bend knees for squat
        keypoints[23] = (0.45, 0.7, 0.9)  # left hip (lower)
        keypoints[24] = (0.55, 0.7, 0.9)  # right hip (lower)
        keypoints[25] = (0.45, 0.75, 0.9)  # left knee (bent)
        keypoints[26] = (0.55, 0.75, 0.9)  # right knee (bent)
        keypoints[27] = (0.45, 0.85, 0.9)  # left ankle
        keypoints[28] = (0.55, 0.85, 0.9)  # right ankle
        
        return keypoints
    
    def _create_mock_keypoints_arms_crossed(self):
        """Create mock keypoints for arms crossed pose"""
        keypoints = self._create_mock_keypoints_standing().copy()
        
        # Cross arms (left wrist on right side, right wrist on left side)
        keypoints[15] = (0.7, 0.4, 0.9)  # left wrist (right side)
        keypoints[16] = (0.3, 0.4, 0.9)  # right wrist (left side)
        
        return keypoints
    
    def test_initialization(self):
        """Test detector initialization"""
        assert self.detector.mp_pose is not None
        assert self.detector.pose is not None
        assert len(self.detector.dance_poses) == 7
        assert "arms_up" in self.detector.dance_poses
        assert "standing" in self.detector.dance_poses
    
    def test_extract_keypoints(self):
        """Test keypoint extraction from MediaPipe landmarks"""
        # Mock MediaPipe landmarks
        mock_landmarks = Mock()
        mock_landmarks.landmark = []
        
        for i in range(5):  # Create 5 mock landmarks
            landmark = Mock()
            landmark.x = i * 0.1
            landmark.y = i * 0.2
            landmark.visibility = 0.9
            mock_landmarks.landmark.append(landmark)
        
        keypoints = self.detector._extract_keypoints(mock_landmarks)
        
        assert len(keypoints) == 5
        assert keypoints[0] == (0.0, 0.0, 0.9)
        assert keypoints[4] == (0.4, 0.8, 0.9)
    
    def test_get_angle(self):
        """Test angle calculation between three points"""
        # Test right angle (90 degrees)
        p1 = (0, 1)
        p2 = (0, 0)
        p3 = (1, 0)
        angle = self.detector._get_angle(p1, p2, p3)
        assert abs(angle - 90.0) < 1.0
        
        # Test straight line (180 degrees)
        p1 = (0, 0)
        p2 = (1, 0)
        p3 = (2, 0)
        angle = self.detector._get_angle(p1, p2, p3)
        assert abs(angle - 180.0) < 1.0
    
    def test_detect_standing_pose(self):
        """Test standing pose detection"""
        result = self.detector._detect_standing(self.mock_keypoints_standing)
        assert result is True
        
        # Test with squat keypoints (should not detect standing)
        result = self.detector._detect_standing(self.mock_keypoints_squat)
        assert result is False
    
    def test_detect_arms_up_pose(self):
        """Test arms up pose detection"""
        result = self.detector._detect_arms_up(self.mock_keypoints_arms_up)
        assert result is True
        
        # Test with standing keypoints (should not detect arms up)
        result = self.detector._detect_arms_up(self.mock_keypoints_standing)
        assert result is False
    
    def test_detect_squat_pose(self):
        """Test squat pose detection"""
        result = self.detector._detect_squat(self.mock_keypoints_squat)
        assert result is True
        
        # Test with standing keypoints (should not detect squat)
        result = self.detector._detect_squat(self.mock_keypoints_standing)
        assert result is False
    
    def test_detect_arms_crossed_pose(self):
        """Test arms crossed pose detection"""
        result = self.detector._detect_arms_crossed(self.mock_keypoints_arms_crossed)
        assert result is True
        
        # Test with standing keypoints (should not detect arms crossed)
        result = self.detector._detect_arms_crossed(self.mock_keypoints_standing)
        assert result is False
    
    def test_analyze_poses(self):
        """Test pose analysis functionality"""
        pose_data = PoseKeypoints(self.mock_keypoints_arms_up, 1.0)
        detected_poses = self.detector._analyze_poses(pose_data)
        
        assert "arms_up" in detected_poses
        assert isinstance(detected_poses, list)
    
    def test_generate_summary_empty(self):
        """Test summary generation with no detections"""
        summary = self.detector._generate_summary([], 10.0, 300)
        
        assert summary["video_info"]["duration_seconds"] == 10.0
        assert summary["video_info"]["total_frames"] == 300
        assert summary["video_info"]["frames_with_poses"] == 0
        assert summary["pose_summary"] == {}
        assert summary["timeline"] == []
    
    def test_generate_summary_with_data(self):
        """Test summary generation with pose detections"""
        pose_detections = [
            {"timestamp": 1.0, "poses": ["standing", "arms_up"], "keypoints": []},
            {"timestamp": 2.0, "poses": ["standing"], "keypoints": []},
            {"timestamp": 3.0, "poses": ["squat"], "keypoints": []}
        ]
        
        summary = self.detector._generate_summary(pose_detections, 5.0, 150)
        
        assert summary["video_info"]["frames_with_poses"] == 3
        assert "standing" in summary["pose_summary"]
        assert summary["pose_summary"]["standing"]["count"] == 2
        assert summary["pose_summary"]["standing"]["percentage"] == 66.67
        assert len(summary["timeline"]) == 3
    
    @patch('cv2.VideoCapture')
    def test_process_video_file_not_found(self, mock_video_capture):
        """Test video processing with invalid file"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        with pytest.raises(ValueError, match="Could not open video file"):
            self.detector.process_video("nonexistent.mp4")
    
    @patch('cv2.VideoCapture')
    @patch('cv2.cvtColor')
    def test_process_video_success(self, mock_cvt_color, mock_video_capture):
        """Test successful video processing"""
        # Mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            0: 30.0,  # FPS
            7: 90     # Frame count
        }.get(prop, 0)
        
        # Mock frame reading
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.side_effect = [
            (True, mock_frame),
            (True, mock_frame),
            (False, None)  # End of video
        ]
        
        mock_video_capture.return_value = mock_cap
        mock_cvt_color.return_value = mock_frame
        
        # Mock MediaPipe pose processing
        with patch.object(self.detector.pose, 'process') as mock_process:
            mock_results = Mock()
            mock_results.pose_landmarks = None  # No pose detected
            mock_process.return_value = mock_results
            
            summary = self.detector.process_video("test.mp4")
            
            assert "video_info" in summary
            assert "pose_summary" in summary
            assert "timeline" in summary
    
    def test_keypoint_confidence_filtering(self):
        """Test that low confidence keypoints are filtered out"""
        # Create keypoints with low confidence
        low_confidence_keypoints = self._create_mock_keypoints_standing()
        # Set low confidence for key landmarks
        low_confidence_keypoints[11] = (0.4, 0.3, 0.3)  # left shoulder
        low_confidence_keypoints[12] = (0.6, 0.3, 0.3)  # right shoulder
        
        result = self.detector._detect_standing(low_confidence_keypoints)
        assert result is False  # Should not detect due to low confidence
    
    def test_json_output_format(self):
        """Test JSON output format and structure"""
        pose_detections = [
            {"timestamp": 1.0, "poses": ["standing"], "keypoints": []}
        ]
        
        summary = self.detector._generate_summary(pose_detections, 5.0, 150)
        
        # Test that summary can be serialized to JSON
        json_str = json.dumps(summary)
        parsed = json.loads(json_str)
        
        assert parsed == summary
        assert "video_info" in parsed
        assert "pose_summary" in parsed
        assert "timeline" in parsed


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def setup_method(self):
        self.detector = DancePoseDetector()
    
    def test_end_to_end_workflow(self):
        """Test the complete workflow with mocked video processing"""
        with patch.object(self.detector, 'process_video') as mock_process:
            expected_summary = {
                "video_info": {
                    "duration_seconds": 5.0,
                    "total_frames": 150,
                    "frames_with_poses": 3
                },
                "pose_summary": {
                    "standing": {"count": 2, "percentage": 66.67},
                    "arms_up": {"count": 1, "percentage": 33.33}
                },
                "timeline": [
                    {"timestamp": 1.0, "poses": ["standing"]},
                    {"timestamp": 2.0, "poses": ["standing", "arms_up"]},
                    {"timestamp": 3.0, "poses": ["arms_up"]}
                ]
            }
            
            mock_process.return_value = expected_summary
            
            result = self.detector.process_video("test.mp4")
            
            assert result == expected_summary
            assert "video_info" in result
            assert result["video_info"]["frames_with_poses"] > 0
    
    def test_output_file_creation(self):
        """Test that output JSON file is created correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            test_summary = {"test": "data", "video_info": {"duration_seconds": 1.0, "total_frames": 30, "frames_with_poses": 0}}
            
            # Mock video capture to return no frames (empty video)
            mock_cap = Mock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (False, None)  # No frames
            # Mock FPS and frame count properties (cv2.CAP_PROP_FPS = 5, cv2.CAP_PROP_FRAME_COUNT = 7)
            mock_cap.get.side_effect = lambda prop: 30.0 if prop == 5 else 30 if prop == 7 else 0
            
            with patch('cv2.VideoCapture', return_value=mock_cap):
                result = self.detector.process_video("test.mp4", output_path)
                
                # Check file was created and contains correct data
                assert os.path.exists(output_path)
                with open(output_path, 'r') as f:
                    saved_data = json.load(f)
                assert "video_info" in saved_data
                assert "pose_summary" in saved_data
                assert "timeline" in saved_data
        
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])