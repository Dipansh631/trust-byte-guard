"""
Video Deepfake Detection Module
Analyzes video files for deepfake detection using frame extraction and temporal analysis
"""

import cv2
import numpy as np
from PIL import Image
import io
import time
from typing import Dict, List, Any, Tuple
import logging
from .image_detector import ImageDeepfakeDetector
import mediapipe as mp

logger = logging.getLogger(__name__)

class VideoDeepfakeDetector:
    def __init__(self):
        """Initialize the video deepfake detector"""
        self.image_detector = ImageDeepfakeDetector()
        self.face_detection = mp.solutions.face_detection
        self.mp_face_detection = self.face_detection.FaceDetection(min_detection_confidence=0.5)
        
    def _extract_frames(self, video_data: bytes, max_frames: int = 30) -> List[np.ndarray]:
        """Extract frames from video data for analysis"""
        try:
            # Create a temporary file-like object
            video_stream = io.BytesIO(video_data)
            
            # Use OpenCV to read video
            cap = cv2.VideoCapture()
            cap.open(video_stream)
            
            frames = []
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate frame sampling rate
            if total_frames > max_frames:
                sample_rate = total_frames // max_frames
            else:
                sample_rate = 1
            
            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames based on sample rate
                if frame_count % sample_rate == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                
                frame_count += 1
            
            cap.release()
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting video frames: {e}")
            return []
    
    def _analyze_temporal_consistency(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze temporal consistency across video frames"""
        try:
            if len(frames) < 2:
                return {'temporal_score': 0, 'inconsistencies': []}
            
            inconsistencies = []
            temporal_scores = []
            
            # Analyze consecutive frame pairs
            for i in range(len(frames) - 1):
                frame1 = frames[i]
                frame2 = frames[i + 1]
                
                # Calculate optical flow
                flow = self._calculate_optical_flow(frame1, frame2)
                
                # Analyze motion consistency
                motion_consistency = self._analyze_motion_consistency(flow)
                temporal_scores.append(motion_consistency)
                
                if motion_consistency < 0.5:  # Threshold for inconsistency
                    inconsistencies.append(f'Frame {i}-{i+1}: Motion inconsistency')
            
            # Analyze face consistency across frames
            face_consistency = self._analyze_face_consistency(frames)
            temporal_scores.append(face_consistency)
            
            if face_consistency < 0.6:
                inconsistencies.append('Face consistency issues detected')
            
            # Calculate overall temporal score
            avg_temporal_score = np.mean(temporal_scores) if temporal_scores else 0
            
            return {
                'temporal_score': avg_temporal_score,
                'inconsistencies': inconsistencies,
                'frame_count': len(frames)
            }
            
        except Exception as e:
            logger.error(f"Temporal analysis error: {e}")
            return {'temporal_score': 0, 'inconsistencies': ['Analysis failed']}
    
    def _calculate_optical_flow(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """Calculate optical flow between two frames"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
            
            # Calculate optical flow using Lucas-Kanade method
            flow = cv2.calcOpticalFlowPyrLK(
                gray1, gray2, 
                None, None,
                winSize=(15, 15),
                maxLevel=2,
                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
            )
            
            return flow[0] if flow[0] is not None else np.array([])
            
        except Exception as e:
            logger.error(f"Optical flow calculation error: {e}")
            return np.array([])
    
    def _analyze_motion_consistency(self, flow: np.ndarray) -> float:
        """Analyze motion consistency from optical flow"""
        try:
            if len(flow) == 0:
                return 0.0
            
            # Calculate motion magnitude
            motion_magnitude = np.linalg.norm(flow, axis=1)
            
            # Calculate motion direction consistency
            motion_direction = np.arctan2(flow[:, 1], flow[:, 0])
            
            # Check for sudden direction changes (sign of manipulation)
            direction_changes = np.abs(np.diff(motion_direction))
            direction_changes = np.minimum(direction_changes, 2 * np.pi - direction_changes)
            
            # High direction changes suggest manipulation
            consistency_score = 1.0 - np.mean(direction_changes) / np.pi
            
            return max(0.0, min(1.0, consistency_score))
            
        except Exception as e:
            logger.error(f"Motion consistency analysis error: {e}")
            return 0.0
    
    def _analyze_face_consistency(self, frames: List[np.ndarray]) -> float:
        """Analyze face consistency across frames"""
        try:
            if len(frames) < 2:
                return 0.0
            
            face_landmarks = []
            
            # Extract face landmarks for each frame
            for frame in frames:
                landmarks = self._extract_face_landmarks(frame)
                if landmarks:
                    face_landmarks.append(landmarks)
            
            if len(face_landmarks) < 2:
                return 0.0
            
            # Calculate consistency between consecutive face landmarks
            consistency_scores = []
            
            for i in range(len(face_landmarks) - 1):
                landmarks1 = face_landmarks[i]
                landmarks2 = face_landmarks[i + 1]
                
                # Calculate landmark distance
                if len(landmarks1) == len(landmarks2):
                    distances = np.linalg.norm(landmarks1 - landmarks2, axis=1)
                    avg_distance = np.mean(distances)
                    
                    # Normalize distance (lower is more consistent)
                    consistency = max(0.0, 1.0 - avg_distance / 50.0)  # Threshold of 50 pixels
                    consistency_scores.append(consistency)
            
            return np.mean(consistency_scores) if consistency_scores else 0.0
            
        except Exception as e:
            logger.error(f"Face consistency analysis error: {e}")
            return 0.0
    
    def _extract_face_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """Extract face landmarks using MediaPipe"""
        try:
            results = self.mp_face_detection.process(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
            if results.detections:
                # Get the first detected face
                detection = results.detections[0]
                bbox = detection.location_data.relative_bounding_box
                
                h, w, _ = frame.shape
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Extract face region
                face_region = frame[y:y+height, x:x+width]
                
                if face_region.size > 0:
                    # Resize to standard size for landmark extraction
                    face_resized = cv2.resize(face_region, (224, 224))
                    
                    # Simple landmark extraction (in practice, use more sophisticated methods)
                    # For now, return corner points of the face region
                    landmarks = np.array([
                        [x, y],  # Top-left
                        [x + width, y],  # Top-right
                        [x, y + height],  # Bottom-left
                        [x + width, y + height]  # Bottom-right
                    ])
                    
                    return landmarks
            
            return np.array([])
            
        except Exception as e:
            logger.error(f"Face landmark extraction error: {e}")
            return np.array([])
    
    def _analyze_lip_sync(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze lip-sync consistency (placeholder for advanced analysis)"""
        try:
            # This is a simplified version - in practice, you'd use more sophisticated methods
            lip_sync_scores = []
            
            for frame in frames:
                # Extract mouth region (simplified)
                mouth_region = self._extract_mouth_region(frame)
                if mouth_region is not None:
                    # Analyze mouth movement consistency
                    score = self._analyze_mouth_movement(mouth_region)
                    lip_sync_scores.append(score)
            
            avg_lip_sync = np.mean(lip_sync_scores) if lip_sync_scores else 0.5
            
            return {
                'lip_sync_score': avg_lip_sync,
                'is_consistent': avg_lip_sync > 0.6
            }
            
        except Exception as e:
            logger.error(f"Lip-sync analysis error: {e}")
            return {'lip_sync_score': 0.5, 'is_consistent': True}
    
    def _extract_mouth_region(self, frame: np.ndarray) -> np.ndarray:
        """Extract mouth region from face"""
        try:
            # Use face detection to find mouth region
            results = self.mp_face_detection.process(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
            if results.detections:
                detection = results.detections[0]
                bbox = detection.location_data.relative_bounding_box
                
                h, w, _ = frame.shape
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Estimate mouth region (bottom half of face)
                mouth_y = y + int(height * 0.6)
                mouth_height = int(height * 0.4)
                
                mouth_region = frame[mouth_y:mouth_y+mouth_height, x:x+width]
                return mouth_region
            
            return None
            
        except Exception as e:
            logger.error(f"Mouth region extraction error: {e}")
            return None
    
    def _analyze_mouth_movement(self, mouth_region: np.ndarray) -> float:
        """Analyze mouth movement consistency"""
        try:
            if mouth_region is None or mouth_region.size == 0:
                return 0.5
            
            # Convert to grayscale
            gray = cv2.cvtColor(mouth_region, cv2.COLOR_RGB2GRAY)
            
            # Calculate edge density (more edges = more movement)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Normalize to 0-1 range
            return min(1.0, edge_density * 10)
            
        except Exception as e:
            logger.error(f"Mouth movement analysis error: {e}")
            return 0.5
    
    def analyze_video(self, video_data: bytes) -> Dict[str, Any]:
        """Main method to analyze video for deepfake detection"""
        start_time = time.time()
        
        try:
            # Extract frames from video
            frames = self._extract_frames(video_data)
            
            if not frames:
                return {
                    'file_type': 'video',
                    'is_deepfake': False,
                    'confidence': 0.0,
                    'details': {
                        'suspicious_regions': ['No frames extracted'],
                        'model_used': ['Error'],
                        'frame_count': 0,
                        'analysis_time': time.time() - start_time
                    }
                }
            
            # Initialize results
            results = {
                'file_type': 'video',
                'is_deepfake': False,
                'confidence': 0.0,
                'details': {
                    'suspicious_regions': [],
                    'model_used': [],
                    'frame_count': len(frames),
                    'analysis_time': 0
                }
            }
            
            # Analyze individual frames
            frame_results = []
            for i, frame in enumerate(frames):
                try:
                    # Convert frame to bytes for image detector
                    frame_pil = Image.fromarray(frame)
                    frame_bytes = io.BytesIO()
                    frame_pil.save(frame_bytes, format='JPEG')
                    frame_bytes = frame_bytes.getvalue()
                    
                    # Analyze frame
                    frame_result = self.image_detector.analyze_image(frame_bytes)
                    frame_results.append(frame_result)
                    
                except Exception as e:
                    logger.error(f"Frame {i} analysis error: {e}")
                    continue
            
            # Analyze temporal consistency
            temporal_analysis = self._analyze_temporal_consistency(frames)
            
            # Analyze lip-sync
            lip_sync_analysis = self._analyze_lip_sync(frames)
            
            # Combine frame analysis results
            if frame_results:
                frame_confidences = [r['confidence'] for r in frame_results if 'confidence' in r]
                avg_frame_confidence = np.mean(frame_confidences) if frame_confidences else 50.0
            else:
                avg_frame_confidence = 50.0
            
            # Calculate overall confidence
            temporal_score = temporal_analysis['temporal_score'] * 100
            lip_sync_score = lip_sync_analysis['lip_sync_score'] * 100
            
            # Weighted combination
            overall_confidence = (
                avg_frame_confidence * 0.4 +  # Frame analysis
                temporal_score * 0.3 +        # Temporal consistency
                lip_sync_score * 0.3          # Lip-sync analysis
            )
            
            results['confidence'] = round(overall_confidence, 2)
            results['is_deepfake'] = overall_confidence > 60.0
            
            # Add suspicious regions
            if temporal_analysis['inconsistencies']:
                results['details']['suspicious_regions'].extend(temporal_analysis['inconsistencies'])
            
            if not lip_sync_analysis['is_consistent']:
                results['details']['suspicious_regions'].append('Lip-sync inconsistency')
            
            if overall_confidence > 70:
                results['details']['suspicious_regions'].append('High manipulation probability')
            elif overall_confidence > 50:
                results['details']['suspicious_regions'].append('Moderate manipulation signs')
            
            # Add model information
            results['details']['model_used'] = ['Frame Analysis', 'Temporal Analysis', 'Lip-sync Analysis']
            results['details']['temporal_score'] = temporal_score
            results['details']['lip_sync_score'] = lip_sync_score
            
            # Calculate analysis time
            analysis_time = time.time() - start_time
            results['details']['analysis_time'] = round(analysis_time, 2)
            
            logger.info(f"Video analysis completed in {analysis_time:.2f}s with confidence {results['confidence']}%")
            
            return results
            
        except Exception as e:
            logger.error(f"Video analysis error: {e}")
            return {
                'file_type': 'video',
                'is_deepfake': False,
                'confidence': 0.0,
                'details': {
                    'suspicious_regions': ['Analysis failed'],
                    'model_used': ['Error'],
                    'frame_count': 0,
                    'analysis_time': time.time() - start_time,
                    'error': str(e)
                }
            }
