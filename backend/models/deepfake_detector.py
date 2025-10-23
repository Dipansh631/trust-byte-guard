from __future__ import annotations

from typing import Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image
import io
import torch
import torch.nn as nn
import torchvision.transforms as transforms


class SimpleCNN(nn.Module):
    """Simple CNN for deepfake detection"""
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128 * 32 * 32, 512)
        self.fc2 = nn.Linear(512, 2)  # 2 classes: real, fake
        self.dropout = nn.Dropout(0.5)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.pool(self.relu(self.conv3(x)))
        x = x.view(-1, 128 * 32 * 32)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x


class DeepfakeDetector:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the deepfake detection model"""
        try:
            # For now, we'll use a placeholder model
            # In production, you would load a pre-trained deepfake detection model
            self.model = SimpleCNN()
            self.model.to(self.device)
            self.model.eval()
            print("✅ Deepfake detector initialized (placeholder model)")
        except Exception as e:
            print(f"❌ Error initializing deepfake model: {e}")
            self.model = None

    def _extract_frames_from_video(self, video_data: bytes) -> list:
        """Extract frames from video data"""
        try:
            # Create a temporary file-like object
            video_stream = io.BytesIO(video_data)
            
            # Use OpenCV to read video
            cap = cv2.VideoCapture()
            cap.open(video_stream)
            
            frames = []
            frame_count = 0
            max_frames = 10  # Limit to 10 frames for analysis
            
            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
                frame_count += 1
            
            cap.release()
            return frames
            
        except Exception as e:
            print(f"Error extracting video frames: {e}")
            return []

    def _analyze_image_features(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze image features for deepfake detection"""
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(image)
            
            # Apply transformations
            input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            if self.model is not None:
                with torch.no_grad():
                    outputs = self.model(input_tensor)
                    probabilities = torch.nn.functional.softmax(outputs, dim=1)
                    fake_prob = float(probabilities[0][1])  # Probability of being fake
                    real_prob = float(probabilities[0][0])  # Probability of being real
            else:
                # Fallback to rule-based analysis
                fake_prob, real_prob = self._rule_based_analysis(image)
            
            return {
                "fake_probability": fake_prob,
                "real_probability": real_prob,
                "confidence": max(fake_prob, real_prob)
            }
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return {"fake_probability": 0.5, "real_probability": 0.5, "confidence": 0.5}

    def _rule_based_analysis(self, image: np.ndarray) -> Tuple[float, float]:
        """Rule-based analysis for deepfake detection"""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Calculate various features
            features = {}
            
            # 1. Edge density analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            features['edge_density'] = edge_density
            
            # 2. Frequency domain analysis
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            features['frequency_variance'] = np.var(magnitude_spectrum)
            
            # 3. Color distribution analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            color_variance = np.var(hsv, axis=(0, 1))
            features['color_variance'] = np.mean(color_variance)
            
            # 4. Texture analysis using Local Binary Pattern
            lbp = self._calculate_lbp(gray)
            features['texture_uniformity'] = np.var(lbp)
            
            # Simple scoring based on features
            score = 0
            
            # High edge density might indicate manipulation
            if edge_density > 0.1:
                score += 0.2
            
            # Unusual frequency patterns
            if features['frequency_variance'] > 10:
                score += 0.2
            
            # Unusual color patterns
            if features['color_variance'] > 1000:
                score += 0.2
            
            # Texture inconsistencies
            if features['texture_uniformity'] > 50:
                score += 0.2
            
            # Additional checks
            if self._detect_face_artifacts(image):
                score += 0.2
            
            # Normalize score
            fake_prob = min(score, 1.0)
            real_prob = 1.0 - fake_prob
            
            return fake_prob, real_prob
            
        except Exception as e:
            print(f"Error in rule-based analysis: {e}")
            return 0.5, 0.5

    def _calculate_lbp(self, image: np.ndarray) -> np.ndarray:
        """Calculate Local Binary Pattern for texture analysis"""
        try:
            # Simple LBP implementation
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

    def _detect_face_artifacts(self, image: np.ndarray) -> bool:
        """Detect potential face manipulation artifacts"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Use Haar cascade for face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return False
            
            # Analyze the first detected face
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            
            # Check for unusual patterns in the face region
            face_edges = cv2.Canny(face_roi, 50, 150)
            edge_density = np.sum(face_edges > 0) / (face_edges.shape[0] * face_edges.shape[1])
            
            # High edge density in face region might indicate manipulation
            return edge_density > 0.15
            
        except:
            return False

    def analyze_media(self, file_data: bytes, content_type: str) -> Dict[str, Any]:
        """Analyze uploaded media for deepfake detection"""
        try:
            if content_type.startswith('image/'):
                return self._analyze_image(file_data)
            elif content_type.startswith('video/'):
                return self._analyze_video(file_data)
            else:
                return {
                    "label": "Unsupported",
                    "confidence": 0,
                    "trust_score": 0,
                    "reason_analysis": "Unsupported file type. Please upload an image or video file.",
                    "model": "unsupported"
                }
        except Exception as e:
            return {
                "label": "Error",
                "confidence": 0,
                "trust_score": 0,
                "reason_analysis": f"Error analyzing media: {str(e)}",
                "model": "error"
            }

    def _analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze a single image"""
        try:
            # Convert bytes to numpy array
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Analyze image features
            features = self._analyze_image_features(image_array)
            
            fake_prob = features["fake_probability"]
            real_prob = features["real_probability"]
            confidence = features["confidence"]
            
            # Determine label
            if fake_prob > real_prob:
                label = "Deepfake"
                confidence_percent = int(round(fake_prob * 100))
            else:
                label = "Real"
                confidence_percent = int(round(real_prob * 100))
            
            trust_score = confidence_percent
            
            # Generate reason analysis
            reason_analysis = self._generate_reason_analysis(label, confidence_percent, fake_prob)
            
            return {
                "label": label,
                "confidence": confidence_percent,
                "trust_score": trust_score,
                "reason_analysis": reason_analysis,
                "raw_score": float(confidence),
                "model": "deepfake-detector"
            }
            
        except Exception as e:
            return {
                "label": "Error",
                "confidence": 0,
                "trust_score": 0,
                "reason_analysis": f"Error processing image: {str(e)}",
                "model": "error"
            }

    def _analyze_video(self, video_data: bytes) -> Dict[str, Any]:
        """Analyze video for deepfake detection"""
        try:
            # Extract frames from video
            frames = self._extract_frames_from_video(video_data)
            
            if not frames:
                return {
                    "label": "Error",
                    "confidence": 0,
                    "trust_score": 0,
                    "reason_analysis": "Could not extract frames from video",
                    "model": "error"
                }
            
            # Analyze each frame
            frame_results = []
            for frame in frames:
                features = self._analyze_image_features(frame)
                frame_results.append(features)
            
            # Aggregate results
            avg_fake_prob = np.mean([r["fake_probability"] for r in frame_results])
            avg_real_prob = np.mean([r["real_probability"] for r in frame_results])
            avg_confidence = np.mean([r["confidence"] for r in frame_results])
            
            # Determine label
            if avg_fake_prob > avg_real_prob:
                label = "Deepfake"
                confidence_percent = int(round(avg_fake_prob * 100))
            else:
                label = "Real"
                confidence_percent = int(round(avg_real_prob * 100))
            
            trust_score = confidence_percent
            
            # Generate reason analysis
            reason_analysis = self._generate_reason_analysis(label, confidence_percent, avg_fake_prob)
            reason_analysis += f" Analyzed {len(frames)} frames from the video."
            
            return {
                "label": label,
                "confidence": confidence_percent,
                "trust_score": trust_score,
                "reason_analysis": reason_analysis,
                "raw_score": float(avg_confidence),
                "model": "deepfake-detector-video",
                "frames_analyzed": len(frames)
            }
            
        except Exception as e:
            return {
                "label": "Error",
                "confidence": 0,
                "trust_score": 0,
                "reason_analysis": f"Error processing video: {str(e)}",
                "model": "error"
            }

    def _generate_reason_analysis(self, label: str, confidence: int, fake_prob: float) -> str:
        """Generate human-readable explanation for deepfake analysis"""
        if label == "Deepfake":
            if confidence > 80:
                reason = "High confidence deepfake detection. "
            elif confidence > 60:
                reason = "Moderate confidence deepfake detection. "
            else:
                reason = "Low confidence deepfake detection. "
            
            reason += "The media shows characteristics commonly associated with AI-generated or manipulated content."
        else:
            reason = "Media appears to be authentic. "
            if confidence < 70:
                reason += "Some minor inconsistencies detected but not enough to classify as deepfake."
            else:
                reason += "No significant signs of manipulation detected."
        
        return reason
