#!/usr/bin/env python3
"""
Test script for enhanced email analysis functionality
"""

import requests
import json

def test_email_analysis():
    """Test the enhanced email analysis API"""
    
    # Test cases
    test_emails = [
        {
            "subject": "URGENT: Verify Your Account Immediately!",
            "body": "Dear Customer,\n\nYour account has been SUSPENDED due to suspicious activity. Click here to verify your identity immediately or your account will be PERMANENTLY CLOSED!\n\nThis is URGENT - act now!\n\nClick: http://bit.ly/verify-now\n\nBest regards,\nSecurity Team"
        },
        {
            "subject": "Congratulations! You've Won $10,000!",
            "body": "Congratulations! You have been selected as a winner of our lottery! You have won $10,000!\n\nTo claim your prize, please click here and provide your personal information:\n\nhttp://tinyurl.com/claim-prize\n\nThis offer expires in 24 hours. Act now!\n\nRegards,\nLottery Team"
        },
        {
            "subject": "Meeting Reminder - Tomorrow at 2 PM",
            "body": "Hi John,\n\nJust a friendly reminder about our meeting tomorrow at 2 PM in the conference room.\n\nPlease bring the quarterly reports we discussed last week.\n\nBest regards,\nSarah"
        }
    ]
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Enhanced Email Analysis API")
    print("=" * 50)
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n📧 Test Case {i}: {email['subject']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{base_url}/analyze/email",
                json=email,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Analysis Complete")
                print(f"   Label: {result['label']}")
                print(f"   Confidence: {result['confidence']}%")
                print(f"   Trust Score: {result['trust_score']}%")
                
                if 'detailed_analysis' in result:
                    detailed = result['detailed_analysis']
                    print(f"   Risk Level: {detailed['overall_assessment']['risk_level']}")
                    print(f"   Summary: {detailed['overall_assessment']['summary']}")
                    
                    # Show pattern analysis
                    patterns = detailed['pattern_analysis']
                    print(f"\n   📊 Pattern Analysis:")
                    for pattern_name, pattern_data in patterns.items():
                        if pattern_data['score'] > 0:
                            print(f"      {pattern_name.replace('_', ' ').title()}: {pattern_data['score']} points")
                            if pattern_data['patterns_found']:
                                print(f"         Found: {', '.join(pattern_data['patterns_found'][:3])}")
                    
                    # Show red flags
                    if detailed['red_flags']:
                        print(f"\n   🚨 Red Flags:")
                        for flag in detailed['red_flags']:
                            print(f"      • {flag}")
                    
                    # Show recommendations
                    if detailed['recommendations']:
                        print(f"\n   💡 Recommendations:")
                        for rec in detailed['recommendations'][:3]:  # Show first 3
                            print(f"      • {rec}")
                else:
                    print(f"   Reason: {result['reason_analysis']}")
                    if result['suspicious_phrases']:
                        print(f"   Suspicious Phrases: {', '.join(result['suspicious_phrases'])}")
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Backend server not running")
            print("   Please start the backend server with: python backend/app.py")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("   The enhanced email analysis provides:")
    print("   • Detailed pattern analysis (urgency, authority, financial, etc.)")
    print("   • Technical analysis (URLs, structure, language quality)")
    print("   • Specific red flags identification")
    print("   • Actionable security recommendations")
    print("   • Risk level assessment")

if __name__ == "__main__":
    test_email_analysis()
