#!/usr/bin/env python3
"""
Simple HTTP Server for CyberGuard Backend
Uses only Python standard library - no external dependencies
"""

import json
import random
import time
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class CyberGuardHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_health_response()
        elif parsed_path.path == '/':
            self.send_root_response()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/analyze/email':
            self.handle_email_analysis()
        elif parsed_path.path == '/analyze/media':
            self.handle_media_analysis()
        else:
            self.send_error(404, "Not Found")
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def send_health_response(self):
        """Send health check response"""
        data = {
            "status": "ok",
            "message": "CyberGuard API is running in demo mode",
            "services": {
                "email_analysis": "demo_active",
                "media_analysis": "demo_active"
            }
        }
        self.send_json_response(data)
    
    def send_root_response(self):
        """Send root endpoint response"""
        data = {
            "message": "CyberGuard API - AI-Powered Security Detection",
            "version": "1.0.0",
            "status": "demo_mode",
            "endpoints": {
                "email_analysis": "/analyze/email",
                "media_analysis": "/analyze/media",
                "health": "/health"
            }
        }
        self.send_json_response(data)
    
    def handle_email_analysis(self):
        """Handle email analysis request"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON
            email_data = json.loads(post_data.decode('utf-8'))
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            
            # Analyze email
            result = self.analyze_email_demo(subject, body)
            self.send_json_response(result)
            
        except Exception as e:
            error_data = {
                "error": "Email analysis failed",
                "detail": str(e)
            }
            self.send_json_response(error_data, 500)
    
    def handle_media_analysis(self):
        """Handle media analysis request"""
        try:
            # Read multipart form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Simple file type detection from content
            file_type = "image/jpeg"  # Default
            if b'video' in post_data[:100]:
                file_type = "video/mp4"
            elif b'audio' in post_data[:100]:
                file_type = "audio/wav"
            
            # Analyze media
            result = self.analyze_media_demo(file_type, len(post_data))
            self.send_json_response(result)
            
        except Exception as e:
            error_data = {
                "error": "Media analysis failed",
                "detail": str(e)
            }
            self.send_json_response(error_data, 500)
    
    def analyze_email_demo(self, subject: str, body: str):
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
    
    def analyze_media_demo(self, file_type: str, file_size: int):
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
    
    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        return

def run_server(port=8000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CyberGuardHandler)
    
    print("🚀 Starting CyberGuard Backend Server (Demo Mode)...")
    print("=" * 50)
    print("📋 Available Endpoints:")
    print("   • Email Analysis: POST /analyze/email")
    print("   • Media Analysis: POST /analyze/media")
    print("   • Health Check: GET /health")
    print("=" * 50)
    print(f"🌐 Server running at: http://localhost:{port}")
    print("📖 This is a demo server using only Python standard library")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
