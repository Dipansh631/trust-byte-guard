#!/usr/bin/env python3
"""
Simple test script to verify the CyberGuard backend is working
"""

import requests
import json
import time

def test_backend():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing CyberGuard Backend API...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test email analysis endpoint
    try:
        print("\n2. Testing email analysis endpoint...")
        test_email = {
            "subject": "URGENT: Verify Your Account Now!",
            "body": "Click here immediately to verify your account or it will be suspended. This is urgent!"
        }
        
        response = requests.post(
            f"{base_url}/analyze/email",
            headers={"Content-Type": "application/json"},
            json=test_email
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email analysis passed")
            print(f"   Label: {result.get('label', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}%")
            print(f"   Trust Score: {result.get('trust_score', 'N/A')}%")
            print(f"   Suspicious Phrases: {result.get('suspicious_phrases', [])}")
        else:
            print(f"❌ Email analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Email analysis error: {e}")
    
    # Test media analysis endpoint (with a simple test)
    try:
        print("\n3. Testing media analysis endpoint...")
        # Create a simple test image (1x1 pixel PNG)
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {'file': ('test.png', test_image_data, 'image/png')}
        response = requests.post(f"{base_url}/analyze/media", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Media analysis passed")
            print(f"   Label: {result.get('label', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}%")
            print(f"   Trust Score: {result.get('trust_score', 'N/A')}%")
        else:
            print(f"❌ Media analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Media analysis error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")
    return True

if __name__ == "__main__":
    # Wait a moment for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    test_backend()
