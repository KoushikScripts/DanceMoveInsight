#!/usr/bin/env python3
"""
Test runner for Dance Pose Detector

This script runs the test suite and provides detailed output
about the testing results and coverage.
"""

import subprocess
import sys
import os


def run_tests():
    """Run the test suite with detailed output"""
    
    print("="*60)
    print("DANCE POSE DETECTOR - TEST SUITE")
    print("="*60)
    
    # Check if pytest is available
    try:
        import pytest
        print("✓ Pytest found")
    except ImportError:
        print("✗ Pytest not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        print("✓ Pytest installed")
    
    # Check if required modules are available
    required_modules = ["mediapipe", "cv2", "numpy"]
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} found")
        except ImportError:
            missing_modules.append(module)
            print(f"✗ {module} not found")
    
    if missing_modules:
        print(f"\nMissing modules: {', '.join(missing_modules)}")
        print("Please install requirements: pip install -r requirements.txt")
        return 1
    
    print("\n" + "-"*60)
    print("RUNNING TESTS")
    print("-"*60)
    
    # Run tests with verbose output
    test_command = [
        sys.executable, "-m", "pytest", 
        "test_dance_pose_detector.py",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(test_command, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print("\n" + "-"*60)
        
        if result.returncode == 0:
            print("✓ ALL TESTS PASSED!")
            print("\nTest Categories Covered:")
            print("  • Pose detection accuracy")
            print("  • Keypoint extraction")
            print("  • Angle calculations")
            print("  • Video processing workflow")
            print("  • JSON output formatting")
            print("  • Error handling")
            print("  • Integration testing")
        else:
            print("✗ SOME TESTS FAILED")
            print(f"Exit code: {result.returncode}")
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def run_specific_test(test_name):
    """Run a specific test"""
    test_command = [
        sys.executable, "-m", "pytest", 
        f"test_dance_pose_detector.py::{test_name}",
        "-v"
    ]
    
    return subprocess.run(test_command).returncode


def main():
    """Main test runner"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage:")
            print("  python run_tests.py              # Run all tests")
            print("  python run_tests.py <test_name>  # Run specific test")
            print("\nAvailable test classes:")
            print("  TestDancePoseDetector")
            print("  TestIntegration")
            return 0
        else:
            # Run specific test
            test_name = sys.argv[1]
            return run_specific_test(test_name)
    
    # Run all tests
    return run_tests()


if __name__ == "__main__":
    sys.exit(main())