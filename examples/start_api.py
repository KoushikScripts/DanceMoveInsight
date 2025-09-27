#!/usr/bin/env python3
"""
Startup script for Dance Pose Detection API
"""

import os
import sys
import subprocess
import argparse

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['flask', 'mediapipe', 'cv2', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            else:
                __import__(package)
            print(f"✅ {package} found")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} missing")
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_flask.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'results', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def main():
    parser = argparse.ArgumentParser(description='Start Dance Pose Detection API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--install-deps', action='store_true', help='Install dependencies before starting')
    
    args = parser.parse_args()
    
    print("🎭 Dance Pose Detection API - Startup")
    print("=" * 50)
    
    # Check dependencies
    missing_packages = check_dependencies()
    
    if missing_packages or args.install_deps:
        if not install_dependencies():
            print("❌ Cannot start API without required dependencies")
            sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check if main files exist
    required_files = ['flask_api.py', 'dance_pose_detector.py', 'templates/upload.html']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file missing: {file}")
            sys.exit(1)
        else:
            print(f"✅ Found: {file}")
    
    print("\n" + "=" * 50)
    print("🚀 Starting Dance Pose Detection API...")
    print(f"🌐 Server will be available at: http://{args.host}:{args.port}")
    print(f"📱 Web interface: http://localhost:{args.port}")
    print(f"📚 API docs: http://localhost:{args.port} (with Accept: application/json header)")
    print("=" * 50)
    
    # Start the Flask app
    try:
        from flask_api import app
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n👋 Shutting down API server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()