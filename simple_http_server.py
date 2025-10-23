#!/usr/bin/env python3
"""
Simple HTTP Server for CyberGuard Backend
Uses only Python standard library - no external dependencies
"""

import json
import random
import time
import base64
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from datetime import datetime

# Global storage for reports (in production, use a database)
REPORTS_STORAGE = {}

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
        elif parsed_path.path == '/reports':
            self.handle_get_reports()
        elif parsed_path.path.startswith('/reports/'):
            report_id = parsed_path.path.split('/')[-1]
            self.handle_get_report(report_id)
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/analyze/email':
            self.handle_email_analysis()
        elif parsed_path.path == '/analyze/media':
            self.handle_media_analysis()
        elif parsed_path.path == '/reports':
            self.handle_create_report()
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
        """Demo email analysis function with detailed breakdown"""
        # Enhanced analysis categories
        suspicious_keywords = {
            'urgency': ['urgent', 'immediately', 'asap', 'expires', 'limited time', 'act now'],
            'authority': ['verify', 'confirm', 'update', 'security', 'alert', 'suspended'],
            'financial': ['winner', 'prize', 'free', 'congratulations', 'money', 'cash'],
            'action': ['click', 'download', 'reset', 'password', 'account', 'login']
        }
        
        text = f"{subject} {body}".lower()
        
        # Analyze each category
        category_scores = {}
        found_phrases = []
        
        for category, keywords in suspicious_keywords.items():
            category_found = [word for word in keywords if word in text]
            if category_found:
                found_phrases.extend(category_found)
                category_scores[category] = len(category_found) * 20
        
        # Additional analysis
        domain_analysis = self.analyze_domain(subject, body)
        link_analysis = self.analyze_links(body)
        grammar_analysis = self.analyze_grammar(subject, body)
        
        # Calculate overall confidence
        base_confidence = sum(category_scores.values()) / len(suspicious_keywords)
        confidence = min(95, base_confidence + domain_analysis['score'] + link_analysis['score'] + grammar_analysis['score'])
        
        is_phishing = confidence > 50
        
        # Generate detailed reasons
        reasons = {
            "suspicious_keywords": {
                "score": base_confidence,
                "details": category_scores,
                "found_phrases": found_phrases[:5]  # Limit to 5 most relevant
            },
            "domain_analysis": domain_analysis,
            "link_analysis": link_analysis,
            "grammar_analysis": grammar_analysis
        }
        
        # Score breakdown for visualization
        score_breakdown = {
            "keyword_analysis": base_confidence,
            "domain_reputation": domain_analysis['score'],
            "link_safety": link_analysis['score'],
            "grammar_quality": grammar_analysis['score'],
            "overall_confidence": confidence
        }
        
        return {
            "result": "phishing" if is_phishing else "safe",
            "confidence": round(confidence, 1),
            "reasons": reasons,
            "score_breakdown": score_breakdown,
            "label": "Phishing" if is_phishing else "Safe",
            "trust_score": round(100 - confidence, 1),
            "suspicious_phrases": found_phrases[:5],
            "reason_analysis": f"{'High' if confidence > 70 else 'Moderate' if confidence > 40 else 'Low'} confidence {'phishing' if is_phishing else 'legitimate'} detection. {'Detected suspicious phrases: ' + ', '.join(found_phrases[:3]) + '.' if found_phrases else 'No suspicious patterns detected.'}",
            "raw_score": confidence / 100.0,
            "model": "demo-enhanced-analysis"
        }
    
    def analyze_domain(self, subject: str, body: str):
        """Analyze domain-related suspicious patterns"""
        text = f"{subject} {body}".lower()
        
        suspicious_domains = ['bit.ly', 'tinyurl', 'goo.gl', 't.co']
        domain_score = 0
        details = []
        
        for domain in suspicious_domains:
            if domain in text:
                domain_score += 25
                details.append(f"Shortened URL detected: {domain}")
        
        # Check for suspicious email patterns
        if '@' in text and any(susp in text for susp in ['noreply', 'no-reply', 'support']):
            domain_score += 15
            details.append("Generic sender address detected")
        
        return {
            "score": min(30, domain_score),
            "details": details,
            "risk_level": "high" if domain_score > 20 else "medium" if domain_score > 10 else "low"
        }
    
    def analyze_links(self, body: str):
        """Analyze links in email body"""
        link_score = 0
        details = []
        
        # Count links
        link_count = body.lower().count('http')
        if link_count > 2:
            link_score += 20
            details.append(f"Multiple links detected ({link_count})")
        
        # Check for suspicious link patterns
        suspicious_patterns = ['click here', 'download now', 'verify account']
        for pattern in suspicious_patterns:
            if pattern in body.lower():
                link_score += 15
                details.append(f"Suspicious link text: '{pattern}'")
        
        return {
            "score": min(25, link_score),
            "details": details,
            "link_count": link_count,
            "risk_level": "high" if link_score > 15 else "medium" if link_score > 8 else "low"
        }
    
    def analyze_grammar(self, subject: str, body: str):
        """Analyze grammar and language patterns"""
        grammar_score = 0
        details = []
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in subject if c.isupper()) / len(subject) if subject else 0
        if caps_ratio > 0.3:
            grammar_score += 15
            details.append("Excessive capitalization in subject")
        
        # Check for spelling errors (simplified)
        common_errors = ['recieve', 'seperate', 'occured', 'definately']
        for error in common_errors:
            if error in body.lower():
                grammar_score += 10
                details.append(f"Spelling error detected: '{error}'")
        
        # Check for urgency language
        urgency_words = ['urgent', 'immediately', 'asap', 'expires']
        urgency_count = sum(1 for word in urgency_words if word in body.lower())
        if urgency_count > 1:
            grammar_score += 12
            details.append("Multiple urgency indicators")
        
        return {
            "score": min(20, grammar_score),
            "details": details,
            "caps_ratio": caps_ratio,
            "risk_level": "high" if grammar_score > 12 else "medium" if grammar_score > 6 else "low"
        }
    
    def analyze_media_demo(self, file_type: str, file_size: int):
        """Demo media analysis function with detailed breakdown"""
        is_video = file_type.startswith('video/')
        is_audio = file_type.startswith('audio/')
        is_image = file_type.startswith('image/')
        
        # Generate detailed analysis based on media type
        if is_video:
            analysis = self.analyze_video_demo(file_size)
        elif is_audio:
            analysis = self.analyze_audio_demo(file_size)
        else:
            analysis = self.analyze_image_demo(file_size)
        
        return {
            "result": "deepfake" if analysis['is_deepfake'] else "real",
            "confidence": analysis['confidence'],
            "reasons": analysis['reasons'],
            "score_breakdown": analysis['score_breakdown'],
            "label": "AI-Generated" if analysis['is_deepfake'] else "Human-Created",
            "ai_generated": analysis['is_deepfake'],
            "trust_score": round(100 - analysis['confidence'], 1),
            "reason_analysis": analysis['reason_analysis'],
            "raw_score": analysis['confidence'] / 100.0,
            "model": "demo-enhanced-analysis",
            "file_type": "video" if is_video else "audio" if is_audio else "image",
            "frames_analyzed": analysis.get('frames_analyzed'),
            "duration": analysis.get('duration')
        }
    
    def analyze_image_demo(self, file_size: int):
        """Analyze image for deepfake characteristics"""
        # Simulate different analysis categories
        face_analysis = {
            "score": random.randint(20, 80),
            "details": ["Face detection successful", "Facial landmarks detected"],
            "anomalies": ["Minor texture inconsistencies"] if random.random() > 0.7 else []
        }
        
        texture_analysis = {
            "score": random.randint(15, 75),
            "details": ["Texture analysis completed", "Color consistency checked"],
            "anomalies": ["Slight color artifacts"] if random.random() > 0.6 else []
        }
        
        metadata_analysis = {
            "score": random.randint(10, 60),
            "details": ["EXIF data analyzed", "Creation timestamp verified"],
            "anomalies": ["Metadata inconsistencies"] if random.random() > 0.8 else []
        }
        
        # Calculate overall confidence
        confidence = (face_analysis['score'] + texture_analysis['score'] + metadata_analysis['score']) / 3
        is_deepfake = confidence > 60
        
        reasons = {
            "face_analysis": face_analysis,
            "texture_analysis": texture_analysis,
            "metadata_analysis": metadata_analysis
        }
        
        score_breakdown = {
            "face_consistency": face_analysis['score'],
            "texture_quality": texture_analysis['score'],
            "metadata_integrity": metadata_analysis['score'],
            "overall_confidence": confidence
        }
        
        return {
            "is_deepfake": is_deepfake,
            "confidence": round(confidence, 1),
            "reasons": reasons,
            "score_breakdown": score_breakdown,
            "reason_analysis": f"{'High' if confidence > 70 else 'Moderate' if confidence > 40 else 'Low'} confidence {'AI-generated' if is_deepfake else 'human-created'} detection. {'This media appears to be artificially generated using AI technology.' if is_deepfake else 'This media appears to be created by humans without AI manipulation.'}",
            "frames_analyzed": None,
            "duration": None
        }
    
    def analyze_video_demo(self, file_size: int):
        """Analyze video for deepfake characteristics"""
        frames_analyzed = random.randint(15, 45)
        
        temporal_analysis = {
            "score": random.randint(25, 85),
            "details": [f"Analyzed {frames_analyzed} frames", "Temporal consistency checked"],
            "anomalies": ["Frame-to-frame inconsistencies"] if random.random() > 0.6 else []
        }
        
        lip_sync_analysis = {
            "score": random.randint(20, 80),
            "details": ["Lip-sync analysis completed", "Audio-visual alignment checked"],
            "anomalies": ["Lip-sync mismatches detected"] if random.random() > 0.7 else []
        }
        
        motion_analysis = {
            "score": random.randint(15, 75),
            "details": ["Motion tracking completed", "Natural movement patterns analyzed"],
            "anomalies": ["Unnatural motion patterns"] if random.random() > 0.5 else []
        }
        
        confidence = (temporal_analysis['score'] + lip_sync_analysis['score'] + motion_analysis['score']) / 3
        is_deepfake = confidence > 55
        
        reasons = {
            "temporal_analysis": temporal_analysis,
            "lip_sync_analysis": lip_sync_analysis,
            "motion_analysis": motion_analysis
        }
        
        score_breakdown = {
            "temporal_consistency": temporal_analysis['score'],
            "lip_sync_accuracy": lip_sync_analysis['score'],
            "motion_naturalness": motion_analysis['score'],
            "overall_confidence": confidence
        }
        
        return {
            "is_deepfake": is_deepfake,
            "confidence": round(confidence, 1),
            "reasons": reasons,
            "score_breakdown": score_breakdown,
            "reason_analysis": f"{'High' if confidence > 70 else 'Moderate' if confidence > 40 else 'Low'} confidence {'AI-generated' if is_deepfake else 'human-created'} detection. {'This video appears to be artificially generated using AI technology with temporal inconsistencies.' if is_deepfake else 'This video appears to be created by humans without AI manipulation.'}",
            "frames_analyzed": frames_analyzed,
            "duration": round(random.uniform(3.0, 12.0), 1)
        }
    
    def analyze_audio_demo(self, file_size: int):
        """Analyze audio for deepfake characteristics"""
        duration = round(random.uniform(2.0, 8.0), 1)
        
        voice_analysis = {
            "score": random.randint(20, 85),
            "details": ["Voice characteristics analyzed", "Spectral analysis completed"],
            "anomalies": ["Voice spoofing indicators"] if random.random() > 0.6 else []
        }
        
        audio_quality_analysis = {
            "score": random.randint(15, 80),
            "details": ["Audio quality assessment", "Background noise analysis"],
            "anomalies": ["Audio artifacts detected"] if random.random() > 0.7 else []
        }
        
        frequency_analysis = {
            "score": random.randint(25, 75),
            "details": ["Frequency spectrum analyzed", "Harmonic patterns checked"],
            "anomalies": ["Unnatural frequency patterns"] if random.random() > 0.5 else []
        }
        
        confidence = (voice_analysis['score'] + audio_quality_analysis['score'] + frequency_analysis['score']) / 3
        is_deepfake = confidence > 50
        
        reasons = {
            "voice_analysis": voice_analysis,
            "audio_quality_analysis": audio_quality_analysis,
            "frequency_analysis": frequency_analysis
        }
        
        score_breakdown = {
            "voice_authenticity": voice_analysis['score'],
            "audio_quality": audio_quality_analysis['score'],
            "frequency_naturalness": frequency_analysis['score'],
            "overall_confidence": confidence
        }
        
        return {
            "is_deepfake": is_deepfake,
            "confidence": round(confidence, 1),
            "reasons": reasons,
            "score_breakdown": score_breakdown,
            "reason_analysis": f"{'High' if confidence > 70 else 'Moderate' if confidence > 40 else 'Low'} confidence {'AI-generated' if is_deepfake else 'human-created'} detection. {'This audio appears to be artificially generated using AI voice synthesis technology.' if is_deepfake else 'This audio appears to be created by humans without AI voice manipulation.'}",
            "frames_analyzed": None,
            "duration": duration
        }
    
    def handle_create_report(self):
        """Handle creating a new report"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            report_data = json.loads(post_data.decode('utf-8'))
            
            # Generate unique report ID
            report_id = str(uuid.uuid4())
            
            # Store report
            REPORTS_STORAGE[report_id] = {
                "id": report_id,
                "timestamp": datetime.now().isoformat(),
                "type": report_data.get('type', 'unknown'),
                "analysis_data": report_data.get('analysis_data', {}),
                "user_notes": report_data.get('user_notes', '')
            }
            
            self.send_json_response({
                "success": True,
                "report_id": report_id,
                "message": "Report created successfully"
            })
            
        except Exception as e:
            error_data = {
                "error": "Report creation failed",
                "detail": str(e)
            }
            self.send_json_response(error_data, 500)
    
    def handle_get_reports(self):
        """Handle getting all reports"""
        try:
            reports = list(REPORTS_STORAGE.values())
            # Sort by timestamp (newest first)
            reports.sort(key=lambda x: x['timestamp'], reverse=True)
            
            self.send_json_response({
                "success": True,
                "reports": reports,
                "count": len(reports)
            })
            
        except Exception as e:
            error_data = {
                "error": "Failed to retrieve reports",
                "detail": str(e)
            }
            self.send_json_response(error_data, 500)
    
    def handle_get_report(self, report_id):
        """Handle getting a specific report"""
        try:
            if report_id not in REPORTS_STORAGE:
                self.send_json_response({
                    "error": "Report not found"
                }, 404)
                return
            
            report = REPORTS_STORAGE[report_id]
            self.send_json_response({
                "success": True,
                "report": report
            })
            
        except Exception as e:
            error_data = {
                "error": "Failed to retrieve report",
                "detail": str(e)
            }
            self.send_json_response(error_data, 500)
    
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
    print("   • Create Report: POST /reports")
    print("   • Get Reports: GET /reports")
    print("   • Get Report: GET /reports/{id}")
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
