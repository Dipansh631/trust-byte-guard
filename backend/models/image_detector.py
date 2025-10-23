"""
Image Deepfake Detection Module
Uses DeepFace and custom models for detecting manipulated images
"""

import cv2
import numpy as np
from PIL import Image
import io
import time
from typing import Dict, List, Any, Tuple
import logging
from deepface import DeepFace
import tensorflow as tf
from tensorflow.keras.applications import Xception
from tensorflow.keras.applications.xception import preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
import mediapipe as mp

logger = logging.getLogger(__name__)

class ImageDeepfakeDetector:
    def __init__(self):
        """Initialize the image deepfake detector with multiple models"""
        self.device = "cuda" if tf.config.list_physical_devices('GPU') else "cpu"
        self.models = {}
        self.face_detection = mp.solutions.face_detection
        self.mp_face_detection = self.face_detection.FaceDetection(min_detection_confidence=0.5)
        
        # Initialize models
        self._load_models()
        
    def _load_models(self):
        """Load all deepfake detection models"""
        try:
            # Load DeepFace models
            logger.info("Loading DeepFace models...")
            self.models['deepface'] = {
                'model': DeepFace.build_model('Facenet'),
                'backends': ['opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface']
            }
            
            # Load XceptionNet for deepfake detection
            logger.info("Loading XceptionNet model...")
            self._load_xception_model()
            
            logger.info("✅ All image detection models loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading image models: {e}")
            self.models = {}
    
    def _load_xception_model(self):
        """Load and configure XceptionNet for deepfake detection"""
        try:
            # Load pre-trained Xception model
            base_model = Xception(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
            
            # Add custom classification head for deepfake detection
            x = base_model.output
            x = GlobalAveragePooling2D()(x)
            x = Dense(512, activation='relu')(x)
            x = Dense(256, activation='relu')(x)
            predictions = Dense(2, activation='softmax')(x)  # Real vs Fake
            
            self.models['xception'] = Model(inputs=base_model.input, outputs=predictions)
            
            # Note: In production, you would load pre-trained weights here
            # For now, we'll use the base model with custom logic
            
        except Exception as e:
            logger.error(f"Error loading XceptionNet: {e}")
            self.models['xception'] = None
    
    def _preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Preprocess image for model inference"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise ValueError("Invalid image format")
    
    def _detect_faces(self, image: np.ndarray) -> List[Dict]:
        """Detect faces in the image using MediaPipe"""
        try:
            results = self.mp_face_detection.process(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            faces = []
            
            if results.detections:
                h, w, _ = image.shape
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    face = {
                        'x': int(bbox.xmin * w),
                        'y': int(bbox.ymin * h),
                        'width': int(bbox.width * w),
                        'height': int(bbox.height * h),
                        'confidence': detection.score[0]
                    }
                    faces.append(face)
            
            return faces
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def _analyze_with_deepface(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image using DeepFace for authenticity"""
        try:
            # Convert numpy array to file path for DeepFace
            temp_path = "temp_image.jpg"
            cv2.imwrite(temp_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            
            # Analyze with DeepFace
            result = DeepFace.analyze(
                img_path=temp_path,
                actions=['age', 'gender', 'emotion', 'race'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            
            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Extract confidence scores
            if isinstance(result, list):
                result = result[0]
            
            # Calculate authenticity score based on consistency
            age_confidence = result.get('age', 0)
            gender_confidence = result.get('gender', 0)
            emotion_confidence = result.get('dominant_emotion', 0)
            
            # Simple heuristic: more consistent results suggest real image
            consistency_score = min(age_confidence, gender_confidence) if age_confidence and gender_confidence else 0
            
            return {
                'authenticity_score': consistency_score,
                'age': result.get('age', 'Unknown'),
                'gender': result.get('dominant_gender', 'Unknown'),
                'emotion': result.get('dominant_emotion', 'Unknown'),
                'race': result.get('dominant_race', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"DeepFace analysis error: {e}")
            return {
                'authenticity_score': 0,
                'age': 'Unknown',
                'gender': 'Unknown',
                'emotion': 'Unknown',
                'race': 'Unknown'
            }
    
    def _analyze_with_xception(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image using XceptionNet model"""
        try:
            if not self.models.get('xception'):
                return {'confidence': 0.5, 'prediction': 'Unknown'}
            
            # Resize image to model input size
            resized_image = cv2.resize(image, (299, 299))
            
            # Preprocess for Xception
            processed_image = preprocess_input(resized_image.astype(np.float32))
            processed_image = np.expand_dims(processed_image, axis=0)
            
            # Get prediction
            predictions = self.models['xception'].predict(processed_image, verbose=0)
            
            # Extract confidence scores
            real_confidence = float(predictions[0][0])
            fake_confidence = float(predictions[0][1])
            
            # Determine prediction
            prediction = 'Real' if real_confidence > fake_confidence else 'Fake'
            confidence = max(real_confidence, fake_confidence)
            
            return {
                'confidence': confidence,
                'prediction': prediction,
                'real_score': real_confidence,
                'fake_score': fake_confidence
            }
            
        except Exception as e:
            logger.error(f"XceptionNet analysis error: {e}")
            return {'confidence': 0.5, 'prediction': 'Unknown'}
    
    def _analyze_image_artifacts(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image for common deepfake artifacts"""
        try:
            artifacts = {
                'edge_inconsistencies': 0,
                'color_anomalies': 0,
                'texture_irregularities': 0,
                'frequency_anomalies': 0
            }
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # 1. Edge consistency analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            artifacts['edge_inconsistencies'] = min(edge_density * 100, 100)
            
            # 2. Color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            color_variance = np.var(hsv, axis=(0, 1))
            artifacts['color_anomalies'] = min(np.mean(color_variance) / 1000, 100)
            
            # 3. Texture analysis using Local Binary Pattern
            lbp = self._calculate_lbp(gray)
            texture_variance = np.var(lbp)
            artifacts['texture_irregularities'] = min(texture_variance / 100, 100)
            
            # 4. Frequency domain analysis
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            freq_variance = np.var(magnitude_spectrum)
            artifacts['frequency_anomalies'] = min(freq_variance / 100, 100)
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Artifact analysis error: {e}")
            return {
                'edge_inconsistencies': 0,
                'color_anomalies': 0,
                'texture_irregularities': 0,
                'frequency_anomalies': 0
            }
    
    def _calculate_lbp(self, image: np.ndarray) -> np.ndarray:
        """Calculate Local Binary Pattern for texture analysis"""
        try:
            rows, cols = image.shape
            lbp = np.zeros_like(image)
            
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    center = image[i, j]
                    binary_string = ""
                    
                    # 8-neighborhood
                    neighbors = [
                        image[i-1, j-1], image[i-1, j], image[i-1, j+1],
                        image[i, j+1], image[i+1, j+1], image[i+1, j],
                        image[i+1, j-1], image[i, j-1]
                    ]
                    
                    for neighbor in neighbors:
                        binary_string += "1" if neighbor >= center else "0"
                    
                    lbp[i, j] = int(binary_string, 2)
            
            return lbp
        except:
            return np.zeros_like(image)
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Main method to analyze image for deepfake detection"""
        start_time = time.time()
        
        try:
            # Preprocess image
            image = self._preprocess_image(image_data)
            
            # Detect faces
            faces = self._detect_faces(image)
            
            # Initialize results
            results = {
                'file_type': 'image',
                'is_deepfake': False,
                'confidence': 0.0,
                'details': {
                    'suspicious_regions': [],
                    'model_used': [],
                    'face_count': len(faces),
                    'analysis_time': 0
                }
            }
            
            if len(faces) == 0:
                results['details']['suspicious_regions'].append('No faces detected')
                results['confidence'] = 50.0  # Neutral score when no faces
                return results
            
            # Analyze with different models
            model_results = []
            
            # DeepFace analysis
            try:
                deepface_result = self._analyze_with_deepface(image)
                model_results.append({
                    'model': 'DeepFace',
                    'confidence': deepface_result['authenticity_score'] * 100,
                    'details': deepface_result
                })
                results['details']['model_used'].append('DeepFace')
            except Exception as e:
                logger.error(f"DeepFace analysis failed: {e}")
            
            # XceptionNet analysis
            try:
                xception_result = self._analyze_with_xception(image)
                if xception_result['prediction'] != 'Unknown':
                    model_results.append({
                        'model': 'XceptionNet',
                        'confidence': xception_result['confidence'] * 100,
                        'prediction': xception_result['prediction']
                    })
                    results['details']['model_used'].append('XceptionNet')
            except Exception as e:
                logger.error(f"XceptionNet analysis failed: {e}")
            
            # Artifact analysis
            try:
                artifacts = self._analyze_image_artifacts(image)
                artifact_score = np.mean(list(artifacts.values()))
                model_results.append({
                    'model': 'Artifact Analysis',
                    'confidence': artifact_score,
                    'details': artifacts
                })
                results['details']['model_used'].append('Artifact Analysis')
            except Exception as e:
                logger.error(f"Artifact analysis failed: {e}")
            
            # Combine results
            if model_results:
                # Weighted average of model results
                total_confidence = 0
                total_weight = 0
                
                for result in model_results:
                    weight = 1.0  # Equal weight for now
                    total_confidence += result['confidence'] * weight
                    total_weight += weight
                
                if total_weight > 0:
                    final_confidence = total_confidence / total_weight
                    results['confidence'] = round(final_confidence, 2)
                    results['is_deepfake'] = final_confidence > 60.0  # Threshold for deepfake
                    
                    # Add suspicious regions based on confidence
                    if final_confidence > 70:
                        results['details']['suspicious_regions'].append('High manipulation probability')
                    elif final_confidence > 50:
                        results['details']['suspicious_regions'].append('Moderate manipulation signs')
            
            # Calculate analysis time
            analysis_time = time.time() - start_time
            results['details']['analysis_time'] = round(analysis_time, 2)
            
            logger.info(f"Image analysis completed in {analysis_time:.2f}s with confidence {results['confidence']}%")
            
            return results
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {
                'file_type': 'image',
                'is_deepfake': False,
                'confidence': 0.0,
                'details': {
                    'suspicious_regions': ['Analysis failed'],
                    'model_used': ['Error'],
                    'face_count': 0,
                    'analysis_time': time.time() - start_time,
                    'error': str(e)
                }
            }
