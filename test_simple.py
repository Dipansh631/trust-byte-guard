#!/usr/bin/env python3
"""
Simple test using only standard library
"""

import urllib.request
import urllib.parse
import json

def test_connection():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing CyberGuard Frontend-Backend Connection...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        with urllib.request.urlopen(f"{base_url}/health") as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("✅ Health check passed")
                print(f"   Status: {data['status']}")
            else:
                print(f"❌ Health check failed: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test email analysis
    try:
        test_email = {
            "subject": "URGENT: Verify Your Account Now!",
            "body": "Click here immediately to verify your account or it will be suspended. This is urgent!"
        }
        
        data = json.dumps(test_email).encode('utf-8')
        req = urllib.request.Request(
            f"{base_url}/analyze/email",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                result = json.loads(response.read().decode())
                print("✅ Email analysis working")
                print(f"   Label: {result['label']}")
                print(f"   Confidence: {result['confidence']}%")
                print(f"   Suspicious phrases: {result['suspicious_phrases']}")
            else:
                print(f"❌ Email analysis failed: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Email analysis error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Frontend should now work correctly.")
    print("🌐 Backend is running at: http://localhost:8000")
    print("📱 Frontend should be running at: http://localhost:8081")
    print("\n💡 You can now:")
    print("   • Test email analysis in the frontend")
    print("   • Upload images/videos for deepfake detection")
    print("   • See real-time analysis results")
    
    return True

if __name__ == "__main__":
    test_connection()
