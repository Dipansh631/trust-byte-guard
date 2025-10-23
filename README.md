# Trust Byte Guard 🛡️

**AI-Powered Phishing & Deepfake Detection Platform**

Trust Byte Guard is a comprehensive security platform that uses advanced AI and machine learning to detect phishing emails and deepfake media (images, videos, audio). Built with FastAPI backend and React frontend, it provides real-time analysis with detailed confidence scores and explanations.

## 🚀 Features

### 📧 Email Phishing Detection
- **BERT-based Analysis**: Uses fine-tuned BERT model for sophisticated phishing detection
- **Rule-based Fallback**: Comprehensive keyword and pattern analysis
- **Suspicious Phrase Detection**: Identifies common phishing indicators
- **Confidence Scoring**: Provides detailed confidence levels and explanations

### 🖼️ Deepfake Detection
- **Multi-modal Analysis**: Supports images, videos, and audio files
- **Advanced Computer Vision**: Uses DeepFace, MediaPipe, and custom CNN models
- **Temporal Analysis**: Analyzes video frame consistency and lip-sync
- **Audio Artifact Detection**: Identifies voice spoofing and audio manipulation
- **Real-time Processing**: Fast analysis with detailed results

### 🎯 Key Capabilities
- **Real-time Analysis**: Instant detection and analysis
- **Detailed Reports**: Comprehensive analysis with confidence scores
- **Multiple Models**: Ensemble approach for higher accuracy
- **User-friendly Interface**: Modern, responsive web interface
- **API Access**: RESTful API for integration with other systems

## 🏗️ Architecture

### Backend (Python/FastAPI)
```
backend/
├── app.py                 # Main FastAPI application
├── models/               # AI/ML models
│   ├── text_classifier.py    # Email phishing detection
│   ├── deepfake_detector.py # General deepfake detection
│   ├── image_detector.py    # Image-specific analysis
│   ├── video_detector.py    # Video-specific analysis
│   └── audio_detector.py   # Audio-specific analysis
├── routers/              # API endpoints
│   ├── analyze.py           # Email analysis routes
│   └── deepfake_analyze.py  # Media analysis routes
└── utils/                # Utility functions
```

### Frontend (React/TypeScript)
```
src/
├── components/           # React components
│   ├── EmailAnalyzer.tsx    # Email analysis interface
│   ├── DeepfakeDetector.tsx # Media analysis interface
│   ├── AnalysisResults.tsx  # Results display
│   └── ui/                  # Reusable UI components
├── pages/               # Page components
└── hooks/               # Custom React hooks
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dipansh631/trust-byte-guard.git
   cd trust-byte-guard
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend server**
   ```bash
   # Option 1: Full backend with all models
   python backend/app.py
   
   # Option 2: Simple demo backend
   python simple_backend.py
   ```

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   npm install
   ```

2. **Start the development server**
   ```bash
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📚 API Documentation

### Email Analysis
```http
POST /analyze/email
Content-Type: application/json

{
  "subject": "Urgent: Verify Your Account",
  "body": "Click here to verify your account immediately..."
}
```

### Media Analysis
```http
POST /deepfake/image
Content-Type: multipart/form-data

[Upload image file]
```

```http
POST /deepfake/video
Content-Type: multipart/form-data

[Upload video file]
```

```http
POST /deepfake/audio
Content-Type: multipart/form-data

[Upload audio file]
```

### Response Format
```json
{
  "label": "Phishing" | "Safe" | "Deepfake" | "Real",
  "confidence": 85,
  "trust_score": 85,
  "suspicious_phrases": ["urgent", "verify", "click"],
  "reason_analysis": "High confidence phishing detection...",
  "raw_score": 0.85,
  "model": "bert-tiny-finetuned-phishing"
}
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Model Configuration
MODEL_CACHE_DIR=./models
MAX_FILE_SIZE_MB=100

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
python -m pytest backend/tests/

# Run specific test files
python test_backend.py
python test_deepfake_backend.py
```

### Frontend Tests
```bash
npm run test
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker build -t trust-byte-guard .
docker run -p 8000:8000 trust-byte-guard
```

### Production Deployment
1. **Backend**: Deploy to cloud platforms (AWS, GCP, Azure)
2. **Frontend**: Build and deploy to CDN or static hosting
3. **Database**: Configure persistent storage for model caching

## 📊 Performance

- **Email Analysis**: ~200ms average response time
- **Image Analysis**: ~2-5 seconds depending on complexity
- **Video Analysis**: ~10-30 seconds for 30-second clips
- **Audio Analysis**: ~3-8 seconds for 30-second audio

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugging Face**: For pre-trained BERT models
- **DeepFace**: For face analysis capabilities
- **MediaPipe**: For media processing pipeline
- **OpenCV**: For computer vision operations
- **Librosa**: For audio analysis

## 📞 Support

For support, email dipansh631@gmail.com or create an issue in the GitHub repository.

## 🔮 Roadmap

- [ ] Real-time video stream analysis
- [ ] Mobile app development
- [ ] Advanced ensemble models
- [ ] Cloud-based model serving
- [ ] Integration with email clients
- [ ] Browser extension for real-time protection

---

**Trust Byte Guard** - Protecting digital trust through AI-powered detection 🛡️