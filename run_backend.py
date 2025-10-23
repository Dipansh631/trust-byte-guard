#!/usr/bin/env python3
"""
Simple Backend Server for Trust Byte Guard
Run this to test the enhanced email analysis functionality
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Trust Byte Guard: AI-Powered Phishing & Deepfake Detector",
        version="1.0.0",
        description="AI-powered web application for detecting phishing emails and deepfake media",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize ML models
    logger.info("🔄 Initializing AI models...")
    try:
        from backend.models.text_classifier import TextClassifier
        from backend.models.deepfake_detector import DeepfakeDetector
        
        app.state.text_classifier = TextClassifier()
        app.state.deepfake_detector = DeepfakeDetector()
        logger.info("✅ All models initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Error initializing models: {e}")
        logger.info("🔄 Continuing with basic functionality...")

    # Include routers
    from backend.routers.analyze import router as analyze_router
    app.include_router(analyze_router, prefix="/analyze", tags=["analysis"])

    @app.get("/")
    async def root():
        return {
            "message": "Trust Byte Guard API - AI-Powered Security Detection",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "email_analysis": "/analyze/email",
                "media_analysis": "/analyze/media",
                "health": "/health",
                "docs": "/docs"
            }
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "message": "Trust Byte Guard API is running",
            "services": {
                "email_analysis": "active",
                "media_analysis": "active"
            }
        }

    return app

if __name__ == "__main__":
    app = create_app()
    
    print("🚀 Starting Trust Byte Guard Backend Server...")
    print("=" * 50)
    print("📋 Available Endpoints:")
    print("   • Email Analysis: POST /analyze/email")
    print("   • Media Analysis: POST /analyze/media")
    print("   • Health Check: GET /health")
    print("   • API Docs: GET /docs")
    print("=" * 50)
    print("🌐 Server running at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
