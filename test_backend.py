#!/usr/bin/env python3
"""
Test script to verify the backend server is working
"""

import requests
import json
import time

def test_backend_connection():
    """Test if the backend server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running!")
            return True
        else:
            print(f"❌ Backend server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running")
        print("   Please start it with: python run_backend.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def test_email_analysis():
    """Test the enhanced email analysis"""
    test_email = {
        "subject": "URGENT: Verify Your Account Immediately!",
        "body": "Dear Customer,\n\nYour account has been SUSPENDED due to suspicious activity. Click here to verify your identity immediately or your account will be PERMANENTLY CLOSED!\n\nThis is URGENT - act now!\n\nClick: http://bit.ly/verify-now\n\nBest regards,\nSecurity Team"
    }
    
    try:
        print("\n🧪 Testing Enhanced Email Analysis...")
        response = requests.post(
            "http://localhost:8000/analyze/email",
            json=test_email,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email analysis successful!")
            print(f"   Label: {result['label']}")
            print(f"   Confidence: {result['confidence']}%")
            
            if 'detailed_analysis' in result:
                detailed = result['detailed_analysis']
                print(f"   Risk Level: {detailed['overall_assessment']['risk_level']}")
                print(f"   Red Flags: {len(detailed['red_flags'])} detected")
                print(f"   Recommendations: {len(detailed['recommendations'])} provided")
                return True
            else:
                print("   ⚠️ Detailed analysis not available")
                return False
        else:
            print(f"❌ Email analysis failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing email analysis: {e}")
        return False

def main():
    print("🔍 Trust Byte Guard Backend Test")
    print("=" * 40)
    
    # Test connection
    if not test_backend_connection():
        return
    
    # Test email analysis
    if test_email_analysis():
        print("\n🎉 All tests passed! The enhanced email analysis is working correctly.")
    else:
        print("\n❌ Email analysis test failed.")

if __name__ == "__main__":
    main()