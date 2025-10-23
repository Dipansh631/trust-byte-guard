#!/usr/bin/env python3
"""
Simple CyberGuard Backend Server
Minimal FastAPI server for demo purposes
"""

import json
import random
import time
from typing import Dict, Any
import io
from PIL import Image
import base64

try:
    from fastapi import FastAPI, UploadFile, File, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    print("FastAPI not available, creating mock server...")
    FASTAPI_AVAILABLE = False

class EmailAnalysisRequest(BaseModel):
    subject: str
    body: str

def create_mock_app():
    """Create a mock app when FastAPI is not available"""
    class MockApp:
        def __init__(self):
            self.routes = {}
        
        def post(self, path):
            def decorator(func):
                self.routes[path] = func
                return func
            return decorator
        
        def get(self, path):
            def decorator(func):
                self.routes[path] = func
                return func
            return decorator
        
        def add_middleware(self, *args, **kwargs):
            pass
        
        def include_router(self, *args, **kwargs):
            pass
    
    return MockApp()

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="CyberGuard: AI-Powered Phishing & Deepfake Detector",
        version="1.0.0",
        description="AI-powered web application for detecting phishing emails and deepfake media",
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app = create_mock_app()

def analyze_email_demo(subject: str, body: str) -> Dict[str, Any]:
    """Demo email analysis function"""
    # Simple rule-based analysis
    suspicious_keywords = [
        'urgent', 'verify', 'click', 'account', 'suspended', 'immediately',
        'congratulations', 'winner', 'prize', 'free', 'reset', 'password',
        'security', 'alert', 'confirm', 'update', 'expires', 'limited'
    ]
    
    text = f"{subject} {body}".lower()
    found_phrases = [word for word in suspicious_keywords if word in text]
    
    # Calculate confidence based on suspicious phrases
    confidence = min(90, len(found_phrases) * 15 + random.randint(0, 20))
    
    is_phishing = confidence > 50
    
    return {
        "label": "Phishing" if is_phishing else "Safe",
        "confidence": confidence,
        "trust_score": confidence,
        "suspicious_phrases": found_phrases,
        "reason_analysis": f"{'High' if confidence > 70 else 'Moderate' if confidence > 40 else 'Low'} confidence {'phishing' if is_phishing else 'legitimate'} detection. {'Detected suspicious phrases: ' + ', '.join(found_phrases[:3]) + '.' if found_phrases else 'No suspicious patterns detected.'}",
        "raw_score": confidence / 100.0,
        "model": "demo-rule-based"
    }

def analyze_media_demo(file_type: str, file_size: int) -> Dict[str, Any]:
    """Demo media analysis function"""
    # Simulate analysis based on file characteristics
    is_video = file_type.startswith('video/')
    is_audio = file_type.startswith('audio/')
    
    # Random confidence with some bias based on file type
    base_confidence = random.randint(20, 80)
    
    # Add some "intelligence" based on file size
    if file_size > 10 * 1024 * 1024:  # Large files might be more suspicious
        base_confidence += 10
    
    confidence = min(95, base_confidence)
    is_deepfake = confidence > 60
    
    suspicious_regions = []
    if is_deepfake:
        if is_video:
            suspicious_regions.extend(['temporal inconsistency', 'lip-sync mismatch'])
        elif is_audio:
            suspicious_regions.extend(['voice spoofing', 'audio artifacts'])
        else:
            suspicious_regions.extend(['face manipulation', 'texture anomalies'])
    
    return {
        "file_type": "video" if is_video else "audio" if is_audio else "image",
        "is_deepfake": is_deepfake,
        "confidence": confidence,
        "details": {
            "suspicious_regions": suspicious_regions,
            "model_used": ["Demo Analysis", "Rule-based Detection"],
            "analysis_time": round(random.uniform(1.0, 3.0), 2),
            "frame_count": random.randint(10, 30) if is_video else None,
            "duration": round(random.uniform(2.0, 10.0), 1) if is_audio else None
        }
    }

if FASTAPI_AVAILABLE:
    @app.get("/")
    async def root():
        return {
            "message": "CyberGuard API - AI-Powered Security Detection",
            "version": "1.0.0",
            "status": "demo_mode",
            "endpoints": {
                "email_analysis": "/analyze/email",
                "media_analysis": "/analyze/media",
                "health": "/health"
            }
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "message": "CyberGuard API is running in demo mode",
            "services": {
                "email_analysis": "demo_active",
                "media_analysis": "demo_active"
            }
        }
    
    @app.post("/analyze/email")
    async def analyze_email(email_data: EmailAnalysisRequest):
        """Analyze email for phishing detection"""
        try:
            result = analyze_email_demo(email_data.subject, email_data.body)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/analyze/media")
    async def analyze_media(file: UploadFile = File(...)):
        """Analyze media for deepfake detection"""
        try:
            # Read file contents
            contents = await file.read()
            
            if not contents:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            
            # Analyze media
            result = analyze_media_demo(file.content_type, len(contents))
            
            # Add file information
            result['file_info'] = {
                'filename': file.filename,
                'content_type': file.content_type,
                'size_bytes': len(contents)
            }
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

def run_server():
    """Run the server"""
    if FASTAPI_AVAILABLE:
        import uvicorn
        print("🚀 Starting CyberGuard Backend Server (Demo Mode)...")
        print("=" * 50)
        print("📋 Available Endpoints:")
        print("   • Email Analysis: POST /analyze/email")
        print("   • Media Analysis: POST /analyze/media")
        print("   • Health Check: GET /health")
        print("   • API Docs: GET /docs")
        print("=" * 50)
        print("🌐 Server running at: http://localhost:8000")
        print("📖 API Documentation: http://localhost:8000/docs")
        
        try:
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
    else:
        print("❌ FastAPI not available. Please install with: pip install fastapi uvicorn")
        print("   Or run the frontend in demo mode without backend.")

if __name__ == "__main__":
    run_server()
