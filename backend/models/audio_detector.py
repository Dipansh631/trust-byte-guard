"""
Audio Deepfake Detection Module
Analyzes audio files for deepfake detection using MFCC features and voice spoofing detection
"""

import librosa
import numpy as np
import io
import time
from typing import Dict, List, Any, Tuple
import logging
import soundfile as sf
from scipy import signal
from scipy.fft import fft, fftfreq
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AudioDeepfakeDetector:
    def __init__(self):
        """Initialize the audio deepfake detector"""
        self.sample_rate = 22050  # Standard sample rate for analysis
        self.n_mfcc = 13  # Number of MFCC coefficients
        self.n_fft = 2048
        self.hop_length = 512
        
        # Initialize models
        self._load_models()
        
    def _load_models(self):
        """Load audio analysis models"""
        try:
            # Initialize anomaly detection model for voice spoofing
            self.anomaly_detector = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Initialize scaler for feature normalization
            self.scaler = StandardScaler()
            
            logger.info("✅ Audio detection models loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading audio models: {e}")
            self.anomaly_detector = None
            self.scaler = None
    
    def _preprocess_audio(self, audio_data: bytes) -> Tuple[np.ndarray, int]:
        """Preprocess audio data for analysis"""
        try:
            # Load audio from bytes
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=self.sample_rate)
            
            # Trim silence from beginning and end
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            return audio, sr
            
        except Exception as e:
            logger.error(f"Audio preprocessing error: {e}")
            raise ValueError("Invalid audio format")
    
    def _extract_mfcc_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract MFCC features from audio"""
        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(
                y=audio,
                sr=self.sample_rate,
                n_mfcc=self.n_mfcc,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )
            
            # Calculate statistics for each MFCC coefficient
            mfcc_stats = []
            for i in range(mfccs.shape[0]):
                mfcc_stats.extend([
                    np.mean(mfccs[i]),
                    np.std(mfccs[i]),
                    np.min(mfccs[i]),
                    np.max(mfccs[i])
                ])
            
            return np.array(mfcc_stats)
            
        except Exception as e:
            logger.error(f"MFCC extraction error: {e}")
            return np.zeros(self.n_mfcc * 4)
    
    def _extract_spectral_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract spectral features from audio"""
        try:
            features = []
            
            # Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
            features.extend([
                np.mean(spectral_centroids),
                np.std(spectral_centroids)
            ])
            
            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sample_rate)[0]
            features.extend([
                np.mean(spectral_rolloff),
                np.std(spectral_rolloff)
            ])
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            features.extend([
                np.mean(zcr),
                np.std(zcr)
            ])
            
            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=self.sample_rate)[0]
            features.extend([
                np.mean(spectral_bandwidth),
                np.std(spectral_bandwidth)
            ])
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=self.sample_rate)
            features.extend([
                np.mean(chroma),
                np.std(chroma)
            ])
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Spectral feature extraction error: {e}")
            return np.zeros(10)
    
    def _extract_rhythm_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract rhythm and tempo features"""
        try:
            features = []
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=audio, sr=self.sample_rate)
            features.append(tempo)
            
            # Rhythm regularity
            onset_frames = librosa.onset.onset_detect(y=audio, sr=self.sample_rate)
            if len(onset_frames) > 1:
                onset_intervals = np.diff(onset_frames)
                rhythm_regularity = 1.0 / (np.std(onset_intervals) + 1e-6)
                features.append(rhythm_regularity)
            else:
                features.append(0.0)
            
            # Beat strength
            beat_frames = librosa.beat.beat_track(y=audio, sr=self.sample_rate)[1]
            if len(beat_frames) > 0:
                beat_strength = np.mean(librosa.beat.beat_track(y=audio, sr=self.sample_rate)[2])
                features.append(beat_strength)
            else:
                features.append(0.0)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Rhythm feature extraction error: {e}")
            return np.zeros(3)
    
    def _analyze_voice_characteristics(self, audio: np.ndarray) -> Dict[str, Any]:
        """Analyze voice characteristics for authenticity"""
        try:
            # Fundamental frequency (pitch) analysis
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio, 
                fmin=librosa.note_to_hz('C2'), 
                fmax=librosa.note_to_hz('C7')
            )
            
            # Calculate pitch statistics
            f0_clean = f0[voiced_flag]
            if len(f0_clean) > 0:
                pitch_mean = np.mean(f0_clean)
                pitch_std = np.std(f0_clean)
                pitch_range = np.max(f0_clean) - np.min(f0_clean)
            else:
                pitch_mean = pitch_std = pitch_range = 0.0
            
            # Voice quality analysis
            # Jitter (pitch variation)
            if len(f0_clean) > 1:
                jitter = np.mean(np.abs(np.diff(f0_clean))) / pitch_mean if pitch_mean > 0 else 0
            else:
                jitter = 0.0
            
            # Shimmer (amplitude variation)
            amplitude = np.abs(audio)
            if len(amplitude) > 1:
                shimmer = np.mean(np.abs(np.diff(amplitude))) / np.mean(amplitude)
            else:
                shimmer = 0.0
            
            return {
                'pitch_mean': pitch_mean,
                'pitch_std': pitch_std,
                'pitch_range': pitch_range,
                'jitter': jitter,
                'shimmer': shimmer,
                'voiced_ratio': np.mean(voiced_flag) if len(voiced_flag) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Voice characteristics analysis error: {e}")
            return {
                'pitch_mean': 0,
                'pitch_std': 0,
                'pitch_range': 0,
                'jitter': 0,
                'shimmer': 0,
                'voiced_ratio': 0
            }
    
    def _detect_voice_spoofing(self, audio: np.ndarray) -> Dict[str, Any]:
        """Detect voice spoofing using anomaly detection"""
        try:
            # Extract comprehensive features
            mfcc_features = self._extract_mfcc_features(audio)
            spectral_features = self._extract_spectral_features(audio)
            rhythm_features = self._extract_rhythm_features(audio)
            voice_chars = self._analyze_voice_characteristics(audio)
            
            # Combine all features
            all_features = np.concatenate([
                mfcc_features,
                spectral_features,
                rhythm_features,
                [
                    voice_chars['pitch_mean'],
                    voice_chars['pitch_std'],
                    voice_chars['jitter'],
                    voice_chars['shimmer'],
                    voice_chars['voiced_ratio']
                ]
            ])
            
            # Reshape for model prediction
            features_reshaped = all_features.reshape(1, -1)
            
            # Normalize features
            if self.scaler is not None:
                features_normalized = self.scaler.fit_transform(features_reshaped)
            else:
                features_normalized = features_reshaped
            
            # Detect anomalies (spoofed voices are often outliers)
            if self.anomaly_detector is not None:
                anomaly_score = self.anomaly_detector.decision_function(features_normalized)[0]
                is_anomaly = self.anomaly_detector.predict(features_normalized)[0] == -1
                
                # Convert anomaly score to confidence (0-100)
                # Higher anomaly score means more likely to be real
                confidence = max(0, min(100, (anomaly_score + 1) * 50))
            else:
                # Fallback: use feature-based heuristics
                confidence = self._calculate_heuristic_confidence(voice_chars)
                is_anomaly = confidence < 50
            
            return {
                'confidence': confidence,
                'is_spoofed': is_anomaly,
                'anomaly_score': anomaly_score if self.anomaly_detector else 0,
                'features_used': len(all_features)
            }
            
        except Exception as e:
            logger.error(f"Voice spoofing detection error: {e}")
            return {
                'confidence': 50.0,
                'is_spoofed': False,
                'anomaly_score': 0,
                'features_used': 0
            }
    
    def _calculate_heuristic_confidence(self, voice_chars: Dict[str, Any]) -> float:
        """Calculate confidence using heuristic rules"""
        try:
            confidence = 50.0  # Base confidence
            
            # Check for realistic pitch characteristics
            if 80 <= voice_chars['pitch_mean'] <= 400:  # Typical human voice range
                confidence += 10
            elif voice_chars['pitch_mean'] < 80 or voice_chars['pitch_mean'] > 400:
                confidence -= 20
            
            # Check for natural jitter and shimmer
            if 0.5 <= voice_chars['jitter'] <= 2.0:  # Natural jitter range
                confidence += 5
            elif voice_chars['jitter'] > 5.0:  # Excessive jitter
                confidence -= 15
            
            if 0.1 <= voice_chars['shimmer'] <= 0.5:  # Natural shimmer range
                confidence += 5
            elif voice_chars['shimmer'] > 1.0:  # Excessive shimmer
                confidence -= 15
            
            # Check voiced ratio (should be reasonable for speech)
            if 0.3 <= voice_chars['voiced_ratio'] <= 0.8:
                confidence += 10
            elif voice_chars['voiced_ratio'] < 0.1 or voice_chars['voiced_ratio'] > 0.9:
                confidence -= 20
            
            return max(0, min(100, confidence))
            
        except Exception as e:
            logger.error(f"Heuristic confidence calculation error: {e}")
            return 50.0
    
    def _analyze_audio_artifacts(self, audio: np.ndarray) -> Dict[str, Any]:
        """Analyze audio for common deepfake artifacts"""
        try:
            artifacts = {
                'spectral_gaps': 0,
                'unnatural_harmonics': 0,
                'compression_artifacts': 0,
                'phase_inconsistencies': 0
            }
            
            # 1. Spectral gap analysis
            stft = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)
            
            # Look for unnatural gaps in frequency spectrum
            freq_energy = np.mean(magnitude, axis=1)
            gaps = self._detect_spectral_gaps(freq_energy)
            artifacts['spectral_gaps'] = gaps
            
            # 2. Harmonic analysis
            harmonic_ratio = self._analyze_harmonics(audio)
            artifacts['unnatural_harmonics'] = harmonic_ratio
            
            # 3. Compression artifacts detection
            compression_score = self._detect_compression_artifacts(audio)
            artifacts['compression_artifacts'] = compression_score
            
            # 4. Phase consistency
            phase_score = self._analyze_phase_consistency(stft)
            artifacts['phase_inconsistencies'] = phase_score
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Audio artifact analysis error: {e}")
            return {
                'spectral_gaps': 0,
                'unnatural_harmonics': 0,
                'compression_artifacts': 0,
                'phase_inconsistencies': 0
            }
    
    def _detect_spectral_gaps(self, freq_energy: np.ndarray) -> float:
        """Detect unnatural gaps in frequency spectrum"""
        try:
            # Smooth the frequency energy
            smoothed = signal.savgol_filter(freq_energy, 5, 2)
            
            # Find gaps (local minima)
            gaps = 0
            for i in range(1, len(smoothed) - 1):
                if smoothed[i] < smoothed[i-1] and smoothed[i] < smoothed[i+1]:
                    if smoothed[i] < np.mean(smoothed) * 0.5:  # Significant drop
                        gaps += 1
            
            # Normalize by frequency bins
            return min(100, gaps / len(smoothed) * 100)
            
        except Exception as e:
            logger.error(f"Spectral gap detection error: {e}")
            return 0.0
    
    def _analyze_harmonics(self, audio: np.ndarray) -> float:
        """Analyze harmonic structure for unnatural patterns"""
        try:
            # Get fundamental frequency
            f0, voiced_flag, _ = librosa.pyin(audio, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            
            if len(f0) == 0 or np.sum(voiced_flag) == 0:
                return 0.0
            
            # Calculate harmonic-to-noise ratio
            harmonic, percussive = librosa.effects.hpss(audio)
            hnr = 10 * np.log10(np.sum(harmonic**2) / (np.sum(percussive**2) + 1e-10))
            
            # Unnatural HNR suggests manipulation
            if hnr > 20:  # Too clean
                return 80.0
            elif hnr < 5:  # Too noisy
                return 60.0
            else:
                return 20.0
                
        except Exception as e:
            logger.error(f"Harmonic analysis error: {e}")
            return 0.0
    
    def _detect_compression_artifacts(self, audio: np.ndarray) -> float:
        """Detect compression artifacts"""
        try:
            # Analyze high-frequency content
            stft = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)
            
            # High-frequency energy
            high_freq_energy = np.mean(magnitude[-len(magnitude)//4:])
            total_energy = np.mean(magnitude)
            
            # Compression often reduces high-frequency content
            hf_ratio = high_freq_energy / (total_energy + 1e-10)
            
            if hf_ratio < 0.1:  # Very low high-frequency content
                return 70.0
            elif hf_ratio < 0.2:
                return 40.0
            else:
                return 10.0
                
        except Exception as e:
            logger.error(f"Compression artifact detection error: {e}")
            return 0.0
    
    def _analyze_phase_consistency(self, stft: np.ndarray) -> float:
        """Analyze phase consistency across frequency bins"""
        try:
            phase = np.angle(stft)
            
            # Calculate phase differences between adjacent frequency bins
            phase_diffs = np.abs(np.diff(phase, axis=0))
            
            # Unwrap phase differences
            phase_diffs = np.unwrap(phase_diffs, axis=0)
            
            # Calculate phase variance
            phase_variance = np.var(phase_diffs, axis=1)
            avg_phase_variance = np.mean(phase_variance)
            
            # High phase variance suggests manipulation
            if avg_phase_variance > 2.0:
                return 80.0
            elif avg_phase_variance > 1.0:
                return 50.0
            else:
                return 20.0
                
        except Exception as e:
            logger.error(f"Phase consistency analysis error: {e}")
            return 0.0
    
    def analyze_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """Main method to analyze audio for deepfake detection"""
        start_time = time.time()
        
        try:
            # Preprocess audio
            audio, sr = self._preprocess_audio(audio_data)
            
            # Initialize results
            results = {
                'file_type': 'audio',
                'is_deepfake': False,
                'confidence': 0.0,
                'details': {
                    'suspicious_regions': [],
                    'model_used': [],
                    'duration': len(audio) / sr,
                    'analysis_time': 0
                }
            }
            
            # Analyze voice spoofing
            spoofing_analysis = self._detect_voice_spoofing(audio)
            
            # Analyze audio artifacts
            artifact_analysis = self._analyze_audio_artifacts(audio)
            
            # Analyze voice characteristics
            voice_chars = self._analyze_voice_characteristics(audio)
            
            # Combine analysis results
            spoofing_confidence = spoofing_analysis['confidence']
            artifact_score = np.mean(list(artifact_analysis.values()))
            
            # Calculate overall confidence
            # Higher artifact score means more suspicious
            overall_confidence = (spoofing_confidence + (100 - artifact_score)) / 2
            
            results['confidence'] = round(overall_confidence, 2)
            results['is_deepfake'] = overall_confidence < 40.0  # Lower confidence = more likely fake
            
            # Add suspicious regions
            if spoofing_analysis['is_spoofed']:
                results['details']['suspicious_regions'].append('Voice spoofing detected')
            
            if artifact_score > 60:
                results['details']['suspicious_regions'].append('Audio artifacts detected')
            
            if voice_chars['jitter'] > 5.0:
                results['details']['suspicious_regions'].append('Unnatural voice jitter')
            
            if voice_chars['shimmer'] > 1.0:
                results['details']['suspicious_regions'].append('Unnatural voice shimmer')
            
            if overall_confidence < 30:
                results['details']['suspicious_regions'].append('High manipulation probability')
            elif overall_confidence < 50:
                results['details']['suspicious_regions'].append('Moderate manipulation signs')
            
            # Add model information
            results['details']['model_used'] = ['Voice Spoofing Detection', 'Audio Artifact Analysis', 'Voice Characteristics']
            results['details']['spoofing_confidence'] = spoofing_confidence
            results['details']['artifact_score'] = artifact_score
            results['details']['voice_characteristics'] = voice_chars
            
            # Calculate analysis time
            analysis_time = time.time() - start_time
            results['details']['analysis_time'] = round(analysis_time, 2)
            
            logger.info(f"Audio analysis completed in {analysis_time:.2f}s with confidence {results['confidence']}%")
            
            return results
            
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            return {
                'file_type': 'audio',
                'is_deepfake': False,
                'confidence': 0.0,
                'details': {
                    'suspicious_regions': ['Analysis failed'],
                    'model_used': ['Error'],
                    'duration': 0,
                    'analysis_time': time.time() - start_time,
                    'error': str(e)
                }
            }
