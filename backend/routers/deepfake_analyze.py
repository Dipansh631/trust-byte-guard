"""
Deepfake Analysis API Routes
Provides endpoints for image, video, and audio deepfake detection
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import logging
from ..models.image_detector import ImageDeepfakeDetector
from ..models.video_detector import VideoDeepfakeDetector
from ..models.audio_detector import AudioDeepfakeDetector

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize detectors
image_detector = ImageDeepfakeDetector()
video_detector = VideoDeepfakeDetector()
audio_detector = AudioDeepfakeDetector()

@router.post("/image")
async def analyze_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze uploaded image for deepfake detection
    
    Args:
        file: Image file (JPG, PNG, etc.)
        
    Returns:
        JSON response with deepfake analysis results
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an image file (JPG, PNG, etc.)"
            )
        
        # Validate file size (max 20MB)
        if file.size and file.size > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Please upload an image smaller than 20MB."
            )
        
        # Read file contents
        contents = await file.read()
        
        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        logger.info(f"Analyzing image: {file.filename} ({len(contents)} bytes)")
        
        # Analyze image
        result = image_detector.analyze_image(contents)
        
        # Add file information
        result['file_info'] = {
            'filename': file.filename,
            'content_type': file.content_type,
            'size_bytes': len(contents)
        }
        
        logger.info(f"Image analysis completed: {result['confidence']}% confidence, is_deepfake: {result['is_deepfake']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {str(e)}"
        )

@router.post("/video")
async def analyze_video(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze uploaded video for deepfake detection
    
    Args:
        file: Video file (MP4, AVI, MOV, etc.)
        
    Returns:
        JSON response with deepfake analysis results
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload a video file (MP4, AVI, MOV, etc.)"
            )
        
        # Validate file size (max 100MB)
        if file.size and file.size > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Please upload a video smaller than 100MB."
            )
        
        # Read file contents
        contents = await file.read()
        
        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        logger.info(f"Analyzing video: {file.filename} ({len(contents)} bytes)")
        
        # Analyze video
        result = video_detector.analyze_video(contents)
        
        # Add file information
        result['file_info'] = {
            'filename': file.filename,
            'content_type': file.content_type,
            'size_bytes': len(contents)
        }
        
        logger.info(f"Video analysis completed: {result['confidence']}% confidence, is_deepfake: {result['is_deepfake']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Video analysis failed: {str(e)}"
        )

@router.post("/audio")
async def analyze_audio(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyze uploaded audio for deepfake detection
    
    Args:
        file: Audio file (WAV, MP3, M4A, etc.)
        
    Returns:
        JSON response with deepfake analysis results
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an audio file (WAV, MP3, M4A, etc.)"
            )
        
        # Validate file size (max 50MB)
        if file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Please upload an audio file smaller than 50MB."
            )
        
        # Read file contents
        contents = await file.read()
        
        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        logger.info(f"Analyzing audio: {file.filename} ({len(contents)} bytes)")
        
        # Analyze audio
        result = audio_detector.analyze_audio(contents)
        
        # Add file information
        result['file_info'] = {
            'filename': file.filename,
            'content_type': file.content_type,
            'size_bytes': len(contents)
        }
        
        logger.info(f"Audio analysis completed: {result['confidence']}% confidence, is_deepfake: {result['is_deepfake']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio analysis failed: {str(e)}"
        )

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for deepfake detection services
    
    Returns:
        JSON response with service status
    """
    try:
        # Check if all detectors are initialized
        status = {
            "status": "healthy",
            "services": {
                "image_detection": image_detector is not None,
                "video_detection": video_detector is not None,
                "audio_detection": audio_detector is not None
            },
            "models_loaded": {
                "image_models": len(image_detector.models) if image_detector else 0,
                "video_models": "Frame Analysis, Temporal Analysis, Lip-sync Analysis",
                "audio_models": "Voice Spoofing Detection, Audio Artifact Analysis"
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
