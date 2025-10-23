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
    """Analyze email for phishing detection with detailed breakdown"""
    try:
        # Get detailed analysis from the classifier
        clf = request.app.state.text_classifier
        result = clf.analyze_email_detailed(email_data.subject, email_data.body)
        
        return result
        
    except Exception as e:
        return {
            "label": "Error",
            "confidence": 0,
            "trust_score": 0,
            "suspicious_phrases": [],
            "reason_analysis": f"Error analyzing email: {str(e)}",
            "raw_score": 0.0,
            "model": "error",
            "detailed_analysis": {
                "overall_assessment": {
                    "label": "Error",
                    "confidence": 0,
                    "risk_level": "UNKNOWN",
                    "summary": f"Analysis failed: {str(e)}"
                },
                "pattern_analysis": {},
                "technical_analysis": {},
                "recommendations": ["Contact support if this error persists"],
                "red_flags": []
            }
        }


@router.post("/media")
async def analyze_media(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
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


