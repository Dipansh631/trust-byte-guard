# Trust Byte Guard - Quick Start Guide

## 🚀 Running the Project

### Option 1: Frontend Only (Demo Mode)
If you just want to test the enhanced email analysis features:

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Start the frontend:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   - Go to `http://localhost:5173`
   - The app will automatically use demo mode when the backend isn't available
   - You'll see detailed phishing analysis with pattern breakdown, red flags, and recommendations

### Option 2: Full Stack (Backend + Frontend)
For the complete AI-powered analysis:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the backend server:**
   ```bash
   python run_backend.py
   ```

3. **Start the frontend (in a new terminal):**
   ```bash
   npm install
   npm run dev
   ```

4. **Test the enhanced analysis:**
   - Go to `http://localhost:5173`
   - Try analyzing emails with suspicious content
   - See detailed breakdowns of why emails are flagged as phishing

## 🧪 Testing the Enhanced Email Analysis

### Test Cases to Try:

**High-Risk Phishing Email:**
```
Subject: URGENT: Verify Your Account Immediately!
Body: Dear Customer, Your account has been SUSPENDED due to suspicious activity. Click here to verify your identity immediately or your account will be PERMANENTLY CLOSED! This is URGENT - act now! Click: http://bit.ly/verify-now
```

**Financial Scam Email:**
```
Subject: Congratulations! You've Won $10,000!
Body: Congratulations! You have been selected as a winner of our lottery! You have won $10,000! To claim your prize, please click here and provide your personal information: http://tinyurl.com/claim-prize This offer expires in 24 hours. Act now!
```

**Legitimate Email:**
```
Subject: Meeting Reminder - Tomorrow at 2 PM
Body: Hi John, Just a friendly reminder about our meeting tomorrow at 2 PM in the conference room. Please bring the quarterly reports we discussed last week. Best regards, Sarah
```

## 🎯 Enhanced Features

### Detailed Pattern Analysis:
- **🚨 Urgency Indicators**: Detects urgent language and pressure tactics
- **🏛️ Authority Claims**: Identifies impersonation attempts
- **💰 Financial Incentives**: Spots money/prize offers
- **⚡ Action Requirements**: Finds immediate action requests
- **🎭 Social Engineering**: Detects trust-building language
- **⚠️ Threats & Pressure**: Identifies threats and consequences

### Technical Analysis:
- **🔗 URL Analysis**: Detects suspicious and shortened links
- **📧 Email Structure**: Analyzes formatting and punctuation
- **📝 Language Quality**: Evaluates grammar and phrasing

### Security Features:
- **🚨 Red Flags**: Specific warning indicators
- **💡 Recommendations**: Actionable security advice
- **📊 Risk Assessment**: Visual risk level indicators

## 🔧 Troubleshooting

### Backend Connection Issues:
- If you see "Backend Server Not Running" messages, the app will automatically switch to demo mode
- Demo mode provides realistic analysis based on email content patterns
- To use the full AI analysis, start the backend server with `python run_backend.py`

### Python Environment Issues:
- Make sure you have Python 3.8+ installed
- Install dependencies with `pip install -r requirements.txt`
- If you encounter module errors, try using a virtual environment

## 📊 What You'll See

The enhanced email analysis now shows:

1. **Overall Assessment** with risk level and summary
2. **Pattern Analysis** with detailed breakdowns of each category
3. **Technical Analysis** of URLs, structure, and language
4. **Red Flags** highlighting specific concerns
5. **Recommendations** with actionable security advice

This provides users with comprehensive, educational, and actionable information about email threats!
