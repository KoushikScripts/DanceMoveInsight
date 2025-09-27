#!/usr/bin/env python3
"""
Flask API for Dance Pose Detection
Allows video upload and returns pose analysis results
"""

import os
import uuid
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import tempfile
import shutil
from dance_pose_detector import DancePoseDetector
from config import config

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Setup logging for production
if not app.debug:
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

# Use configuration from config.py (already loaded above)

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Initialize pose detector
pose_detector = DancePoseDetector()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    """Serve the upload interface or API documentation"""
    # Check if request wants JSON (API documentation)
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            "message": "Dance Pose Detection API",
            "version": "1.0.0",
            "endpoints": {
                "GET /": "Upload interface (HTML) or API docs (JSON)",
                "POST /upload": "Upload video for pose analysis",
                "GET /result/<job_id>": "Get analysis results",
                "GET /results": "List all results",
                "GET /health": "Health check"
            },
            "supported_formats": list(ALLOWED_EXTENSIONS),
            "max_file_size": "100MB"
        })
    else:
        # Serve HTML upload interface
        return render_template('upload.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "dance-pose-detector",
        "version": "1.0.0"
    })

@app.route('/upload', methods=['POST'])
def upload_video():
    """Upload video and process for pose detection"""
    try:
        # Check if file is present
        if 'video' not in request.files:
            return jsonify({
                "error": "No video file provided",
                "message": "Please upload a video file using the 'video' field"
            }), 400
        
        file = request.files['video']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                "error": "No file selected",
                "message": "Please select a video file to upload"
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file format",
                "message": f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}",
                "uploaded_format": file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else "unknown"
            }), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        video_filename = f"{job_id}.{file_extension}"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        
        file.save(video_path)
        
        # Process video
        try:
            result_filename = f"{job_id}_result.json"
            result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
            
            # Run pose detection
            summary = pose_detector.process_video(video_path, result_path)
            
            # Clean up uploaded video file
            os.remove(video_path)
            
            return jsonify({
                "success": True,
                "job_id": job_id,
                "message": "Video processed successfully",
                "result": summary,
                "download_url": f"/result/{job_id}"
            }), 200
            
        except Exception as e:
            # Clean up files on error
            if os.path.exists(video_path):
                os.remove(video_path)
            
            return jsonify({
                "error": "Processing failed",
                "message": str(e),
                "job_id": job_id
            }), 500
    
    except RequestEntityTooLarge:
        return jsonify({
            "error": "File too large",
            "message": "Maximum file size is 100MB"
        }), 413
    
    except Exception as e:
        return jsonify({
            "error": "Upload failed",
            "message": str(e)
        }), 500

@app.route('/result/<job_id>', methods=['GET'])
def get_result(job_id):
    """Get analysis results by job ID"""
    try:
        result_filename = f"{job_id}_result.json"
        result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
        
        if not os.path.exists(result_path):
            return jsonify({
                "error": "Result not found",
                "message": f"No results found for job ID: {job_id}"
            }), 404
        
        # Check if user wants to download the file
        download = request.args.get('download', 'false').lower() == 'true'
        
        if download:
            return send_file(
                result_path,
                as_attachment=True,
                download_name=f"dance_analysis_{job_id}.json",
                mimetype='application/json'
            )
        else:
            # Return JSON content
            with open(result_path, 'r') as f:
                result_data = json.load(f)
            
            return jsonify({
                "success": True,
                "job_id": job_id,
                "result": result_data
            }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Failed to retrieve result",
            "message": str(e)
        }), 500

@app.route('/results', methods=['GET'])
def list_results():
    """List all available results"""
    try:
        results = []
        for filename in os.listdir(app.config['RESULTS_FOLDER']):
            if filename.endswith('_result.json'):
                job_id = filename.replace('_result.json', '')
                file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
                file_stats = os.stat(file_path)
                
                results.append({
                    "job_id": job_id,
                    "created_at": file_stats.st_ctime,
                    "size_bytes": file_stats.st_size,
                    "download_url": f"/result/{job_id}?download=true"
                })
        
        return jsonify({
            "success": True,
            "total_results": len(results),
            "results": sorted(results, key=lambda x: x['created_at'], reverse=True)
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Failed to list results",
            "message": str(e)
        }), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        "error": "File too large",
        "message": "Maximum file size is 100MB"
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

def cleanup_old_files():
    """Clean up old result files"""
    try:
        cutoff_date = datetime.now() - timedelta(days=app.config['RESULT_RETENTION_DAYS'])
        results_folder = app.config['RESULTS_FOLDER']
        
        if os.path.exists(results_folder):
            for filename in os.listdir(results_folder):
                file_path = os.path.join(results_folder, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        app.logger.info(f"Cleaned up old file: {filename}")
    except Exception as e:
        app.logger.error(f"Error during cleanup: {e}")

# Add security headers for production
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    if not app.debug and hasattr(app.config, 'SECURITY_HEADERS'):
        for header, value in app.config['SECURITY_HEADERS'].items():
            response.headers[header] = value
    return response

if __name__ == '__main__':
    print("🎭 Dance Pose Detection API")
    print("=" * 50)
    print("Starting Flask server...")
    print(f"Environment: {config_name}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Results folder: {app.config['RESULTS_FOLDER']}")
    print(f"Max file size: {app.config['MAX_CONTENT_LENGTH'] // (1024*1024)}MB")
    print(f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}")
    print("=" * 50)
    
    # Get host and port from environment or use defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Run the application
    app.run(host=host, port=port, debug=debug)