from fastapi import APIRouter, UploadFile, File, Form, Request
from typing import List, Dict, Any
from pydantic import BaseModel

from backend.models.text_classifier import TextClassifier
from backend.models.deepfake_detector import DeepfakeDetector


router = APIRouter()


class EmailAnalysisRequest(BaseModel):
    subject: str
    body: str


@router.post("/email")
async def analyze_email(request: Request, email_data: EmailAnalysisRequest) -> Dict[str, Any]:
    """Analyze email for phishing detection"""
    try:
        # Combine subject and body for analysis
        full_text = f"Subject: {email_data.subject}\n\nBody: {email_data.body}"
        
        # Get ML-based analysis
        clf = request.app.state.text_classifier
        result = clf.predict_suspicion(full_text)
        
        return {
            "label": result["label"],
            "confidence": result["confidence"],
            "trust_score": result["trust_score"],
            "suspicious_phrases": result["suspicious_phrases"],
            "reason_analysis": result["reason_analysis"],
            "raw_score": result["raw_score"],
            "model": result["model"]
        }
        
    except Exception as e:
        return {
            "label": "Error",
            "confidence": 0,
            "trust_score": 0,
            "suspicious_phrases": [],
            "reason_analysis": f"Error analyzing email: {str(e)}",
            "raw_score": 0.0,
            "model": "error"
        }


@router.post("/media")
async def analyze_media(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Analyze uploaded media for deepfake detection"""
    try:
        # Read file contents
        contents = await file.read()
        
        # Get deepfake detector from app state
        detector = request.app.state.deepfake_detector
        result = detector.analyze_media(contents, file.content_type)
        
        return result
        
    except Exception as e:
        return {
            "label": "Error",
            "confidence": 0,
            "trust_score": 0,
            "reason_analysis": f"Error analyzing media: {str(e)}",
            "raw_score": 0.0,
            "model": "error"
        }


