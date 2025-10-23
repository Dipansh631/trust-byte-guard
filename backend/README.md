# CyberGuard Backend - AI-Powered Deepfake Detection

A comprehensive FastAPI backend for detecting deepfakes in images, videos, and audio files, plus phishing email detection.

## 🚀 Features

### Deepfake Detection
- **Image Analysis**: Uses DeepFace, XceptionNet, and artifact analysis
- **Video Analysis**: Frame extraction, temporal consistency, lip-sync analysis
- **Audio Analysis**: Voice spoofing detection, MFCC features, audio artifacts

### Email Security
- **Phishing Detection**: BERT-based model with suspicious phrase highlighting
- **Rule-based Analysis**: Additional security checks and validation

## 📋 API Endpoints

### Deepfake Detection
- `POST /deepfake/image` - Analyze images for deepfakes
- `POST /deepfake/video` - Analyze videos for deepfakes  
- `POST /deepfake/audio` - Analyze audio for deepfakes
- `GET /deepfake/health` - Check deepfake detection services

### Email Analysis
- `POST /analyze/email` - Analyze emails for phishing
- `POST /analyze/media` - Legacy media analysis endpoint

### General
- `GET /` - API information and available endpoints
- `GET /health` - Overall API health check
- `GET /docs` - Interactive API documentation

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**:
   ```bash
   python start_backend.py
   ```
   
   Or directly:
   ```bash
   cd backend
   python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access API Documentation**:
   - Open http://localhost:8000/docs for interactive API docs
   - Open http://localhost:8000/redoc for alternative documentation

## 📊 Response Format

### Image/Video/Audio Analysis Response
```json
{
  "file_type": "image|video|audio",
  "is_deepfake": true|false,
  "confidence": 85.7,
  "details": {
    "suspicious_regions": ["face", "lip-sync mismatch"],
    "model_used": ["DeepFace", "XceptionNet", "Artifact Analysis"],
    "analysis_time": 2.34,
    "face_count": 1,
    "frame_count": 30,
    "duration": 5.2
  },
  "file_info": {
    "filename": "test.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 1024000
  }
}
```

### Email Analysis Response
```json
{
  "label": "Phishing|Safe",
  "confidence": 92,
  "trust_score": 92,
  "suspicious_phrases": ["urgent", "click here", "verify"],
  "reason_analysis": "High confidence phishing detection...",
  "raw_score": 0.92,
  "model": "bert-tiny-finetuned-phishing"
}
```

## 🔧 Technical Details

### Image Detection Models
- **DeepFace**: Face analysis and authenticity scoring
- **XceptionNet**: Deep learning-based deepfake detection
- **Artifact Analysis**: Edge, color, texture, and frequency analysis

### Video Detection Features
- **Frame Extraction**: Automatic sampling of video frames
- **Temporal Analysis**: Optical flow and motion consistency
- **Lip-sync Analysis**: Mouth movement and synchronization
- **Face Consistency**: Landmark tracking across frames

### Audio Detection Features
- **MFCC Features**: Mel-frequency cepstral coefficients
- **Voice Spoofing**: Anomaly detection for synthetic voices
- **Spectral Analysis**: Frequency domain artifact detection
- **Voice Characteristics**: Pitch, jitter, shimmer analysis

### Email Detection Features
- **BERT Model**: `mrm8488/bert-tiny-finetuned-phishing`
- **Suspicious Phrase Detection**: Keyword and pattern matching
- **Rule-based Analysis**: Additional security heuristics

## 📁 Project Structure

```
backend/
├── models/
│   ├── image_detector.py      # Image deepfake detection
│   ├── video_detector.py      # Video deepfake detection
│   ├── audio_detector.py      # Audio deepfake detection
│   ├── text_classifier.py     # Email phishing detection
│   └── deepfake_detector.py   # Legacy deepfake detector
├── routers/
│   ├── analyze.py             # Email analysis endpoints
│   └── deepfake_analyze.py    # Deepfake detection endpoints
├── utils/                      # Utility functions
├── app.py                     # FastAPI application
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_deepfake_backend.py
```

This will test all endpoints with sample data and verify functionality.

## ⚙️ Configuration

### Environment Variables
- `CUDA_VISIBLE_DEVICES`: GPU configuration for ML models
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Model Configuration
- Models are automatically downloaded on first use
- Fallback to rule-based analysis if models fail to load
- Configurable confidence thresholds in each detector

## 🚨 Error Handling

- **File Validation**: Type, size, and format checking
- **Model Fallbacks**: Graceful degradation when models fail
- **Comprehensive Logging**: Detailed error tracking and debugging
- **HTTP Status Codes**: Proper REST API error responses

## 📈 Performance

- **Async Processing**: Non-blocking file uploads and analysis
- **Model Caching**: Pre-loaded models for faster inference
- **Batch Processing**: Efficient frame and audio analysis
- **Memory Management**: Optimized for large file processing

## 🔒 Security

- **File Size Limits**: Configurable upload limits
- **Content Validation**: Strict file type checking
- **CORS Configuration**: Configurable cross-origin policies
- **Input Sanitization**: Safe handling of user uploads

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the test files for usage examples
3. Check the logs for detailed error information
4. Open an issue on GitHub

---

**CyberGuard Backend** - Protecting digital content with AI-powered analysis 🛡️
