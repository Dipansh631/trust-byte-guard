from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Routers
from backend.routers.analyze import router as analyze_router
from backend.routers.deepfake_analyze import router as deepfake_router
from backend.models.text_classifier import TextClassifier
from backend.models.deepfake_detector import DeepfakeDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="CyberGuard: AI-Powered Phishing & Deepfake Detector",
        version="1.0.0",
        description="AI-powered web application for detecting phishing emails and deepfake media (images, videos, audio)",
    )

    # CORS configuration - adjust allowed origins as needed
    allowed_origins = [
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:8080",  # Alternative port
        "http://127.0.0.1:8080",
        "http://localhost:8081",  # Another alternative port
        "http://127.0.0.1:8081",
        "http://localhost:3000",  # alternate
        "http://127.0.0.1:3000",
        "*",  # loosen for MVP; restrict in production
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Initialize ML models once and store on app state
    logger.info("🔄 Initializing AI models...")
    try:
        app.state.text_classifier = TextClassifier()
        app.state.deepfake_detector = DeepfakeDetector()
        logger.info("✅ All models initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Error initializing models: {e}")
        # Continue with basic functionality

    # Include routers
    app.include_router(analyze_router, prefix="/analyze", tags=["email-analysis"]) 
    app.include_router(deepfake_router, prefix="/deepfake", tags=["deepfake-detection"])

    @app.get("/")
    async def root():
        return {
            "message": "CyberGuard API - AI-Powered Security Detection",
            "version": "1.0.0",
            "endpoints": {
                "email_analysis": "/analyze/email",
                "image_deepfake": "/deepfake/image",
                "video_deepfake": "/deepfake/video",
                "audio_deepfake": "/deepfake/audio",
                "health": "/health"
            }
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "ok", 
            "message": "CyberGuard API is running",
            "services": {
                "email_analysis": "active",
                "deepfake_detection": "active"
            }
        }

    return app


app = create_app()


