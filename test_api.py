#!/usr/bin/env python3
"""
Test script for the Dance Pose Detection API
"""

import requests
import json
import time
import os

API_BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_api_documentation():
    """Test the API documentation endpoint"""
    print("\n🔍 Testing API documentation...")
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{API_BASE_URL}/", headers=headers)
        if response.status_code == 200:
            print("✅ API documentation retrieved")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ API documentation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API documentation error: {e}")

def test_upload_no_file():
    """Test upload endpoint without file"""
    print("\n🔍 Testing upload without file...")
    try:
        response = requests.post(f"{API_BASE_URL}/upload")
        if response.status_code == 400:
            print("✅ Correctly rejected upload without file")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Upload test error: {e}")

def test_upload_invalid_file():
    """Test upload endpoint with invalid file"""
    print("\n🔍 Testing upload with invalid file...")
    try:
        # Create a dummy text file
        with open('test.txt', 'w') as f:
            f.write("This is not a video file")
        
        with open('test.txt', 'rb') as f:
            files = {'video': f}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        os.remove('test.txt')
        
        if response.status_code == 400:
            print("✅ Correctly rejected invalid file format")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid file test error: {e}")

def test_result_not_found():
    """Test result endpoint with non-existent job ID"""
    print("\n🔍 Testing result with non-existent job ID...")
    try:
        fake_job_id = "non-existent-job-id"
        response = requests.get(f"{API_BASE_URL}/result/{fake_job_id}")
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent job")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Result test error: {e}")

def test_list_results():
    """Test listing all results"""
    print("\n🔍 Testing list results...")
    try:
        response = requests.get(f"{API_BASE_URL}/results")
        if response.status_code == 200:
            print("✅ Successfully retrieved results list")
            data = response.json()
            print(f"Total results: {data.get('total_results', 0)}")
            if data.get('results'):
                print("Recent results:")
                for result in data['results'][:3]:  # Show first 3
                    print(f"  - Job ID: {result['job_id']}")
        else:
            print(f"❌ List results failed: {response.status_code}")
    except Exception as e:
        print(f"❌ List results error: {e}")

def create_sample_video():
    """Create a simple sample video for testing (requires OpenCV)"""
    try:
        import cv2
        import numpy as np
        
        # Create a simple 5-second video with moving rectangle
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('sample_test.mp4', fourcc, 10.0, (640, 480))
        
        for i in range(50):  # 5 seconds at 10 fps
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Draw a moving rectangle
            x = int(50 + i * 10)
            y = int(200 + 50 * np.sin(i * 0.2))
            cv2.rectangle(frame, (x, y), (x+100, y+80), (0, 255, 0), -1)
            out.write(frame)
        
        out.release()
        return True
    except ImportError:
        print("⚠️  OpenCV not available, cannot create sample video")
        return False
    except Exception as e:
        print(f"⚠️  Error creating sample video: {e}")
        return False

def test_upload_sample_video():
    """Test upload with a sample video"""
    print("\n🔍 Testing upload with sample video...")
    
    # Try to create a sample video
    if not create_sample_video():
        print("⚠️  Skipping video upload test - no sample video available")
        return
    
    try:
        with open('sample_test.mp4', 'rb') as f:
            files = {'video': f}
            print("📤 Uploading sample video...")
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        # Clean up
        os.remove('sample_test.mp4')
        
        if response.status_code == 200:
            print("✅ Successfully uploaded and processed video")
            data = response.json()
            print(f"Job ID: {data.get('job_id')}")
            print("Result summary:")
            result = data.get('result', {})
            video_info = result.get('video_info', {})
            print(f"  Duration: {video_info.get('duration_seconds')}s")
            print(f"  Total frames: {video_info.get('total_frames')}")
            print(f"  Frames with poses: {video_info.get('frames_with_poses')}")
            
            # Test downloading the result
            job_id = data.get('job_id')
            if job_id:
                print(f"\n🔍 Testing result download for job {job_id}...")
                result_response = requests.get(f"{API_BASE_URL}/result/{job_id}?download=true")
                if result_response.status_code == 200:
                    print("✅ Successfully downloaded result file")
                else:
                    print(f"❌ Result download failed: {result_response.status_code}")
        else:
            print(f"❌ Video upload failed: {response.status_code}")
            print(response.json())
    except Exception as e:
        print(f"❌ Video upload test error: {e}")

def main():
    """Run all API tests"""
    print("🎭 Dance Pose Detection API - Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print("✅ API server is running")
    except Exception as e:
        print(f"❌ API server is not running: {e}")
        print("Please start the server with: python flask_api.py")
        return
    
    # Run tests
    test_health_check()
    test_api_documentation()
    test_upload_no_file()
    test_upload_invalid_file()
    test_result_not_found()
    test_list_results()
    test_upload_sample_video()
    
    print("\n" + "=" * 50)
    print("🎉 API testing complete!")
    print("\nTo test the web interface, visit: http://localhost:5000")

if __name__ == "__main__":
    main()