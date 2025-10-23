#!/usr/bin/env python3
"""
Startup script for CyberGuard Backend
Starts the FastAPI server with proper configuration
"""

import uvicorn
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting CyberGuard Backend Server...")
    print("=" * 50)
    print("📋 Available Endpoints:")
    print("   • Email Analysis: POST /analyze/email")
    print("   • Image Deepfake: POST /deepfake/image")
    print("   • Video Deepfake: POST /deepfake/video")
    print("   • Audio Deepfake: POST /deepfake/audio")
    print("   • Health Check: GET /health")
    print("   • API Docs: GET /docs")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
