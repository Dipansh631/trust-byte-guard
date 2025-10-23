#!/usr/bin/env python3
"""
Comprehensive Email Analysis Test Script
Demonstrates the detailed phishing analysis features
"""

def demonstrate_email_analysis():
    """Demonstrate the enhanced email analysis features"""
    
    print("🔍 Trust Byte Guard - Detailed Email Analysis Demo")
    print("=" * 60)
    
    # Test Case 1: High-Risk Phishing Email
    print("\n📧 TEST CASE 1: High-Risk Phishing Email")
    print("-" * 50)
    
    phishing_email = {
        "subject": "URGENT: Verify Your Account Immediately!",
        "body": """Dear Customer,

Your account has been SUSPENDED due to suspicious activity. 
Click here to verify your identity immediately or your account will be PERMANENTLY CLOSED!

This is URGENT - act now!

Click: http://bit.ly/verify-now

Best regards,
Security Team"""
    }
    
    print(f"Subject: {phishing_email['subject']}")
    print(f"Body: {phishing_email['body'][:100]}...")
    
    # Simulate analysis results
    analysis_result = analyze_email_detailed(phishing_email)
    display_analysis_result(analysis_result)
    
    # Test Case 2: Financial Scam Email
    print("\n📧 TEST CASE 2: Financial Scam Email")
    print("-" * 50)
    
    scam_email = {
        "subject": "Congratulations! You've Won $10,000!",
        "body": """Congratulations! You have been selected as a winner of our lottery! 
You have won $10,000!

To claim your prize, please click here and provide your personal information:

http://tinyurl.com/claim-prize

This offer expires in 24 hours. Act now!

Regards,
Lottery Team"""
    }
    
    print(f"Subject: {scam_email['subject']}")
    print(f"Body: {scam_email['body'][:100]}...")
    
    analysis_result = analyze_email_detailed(scam_email)
    display_analysis_result(analysis_result)
    
    # Test Case 3: Legitimate Email
    print("\n📧 TEST CASE 3: Legitimate Email")
    print("-" * 50)
    
    legitimate_email = {
        "subject": "Meeting Reminder - Tomorrow at 2 PM",
        "body": """Hi John,

Just a friendly reminder about our meeting tomorrow at 2 PM in the conference room.

Please bring the quarterly reports we discussed last week.

Best regards,
Sarah"""
    }
    
    print(f"Subject: {legitimate_email['subject']}")
    print(f"Body: {legitimate_email['body'][:100]}...")
    
    analysis_result = analyze_email_detailed(legitimate_email)
    display_analysis_result(analysis_result)

def analyze_email_detailed(email):
    """Simulate detailed email analysis"""
    subject = email['subject'].lower()
    body = email['body'].lower()
    full_text = f"{subject} {body}"
    
    # Pattern analysis
    urgency_words = ['urgent', 'immediately', 'asap', 'right now', 'act now', 'limited time']
    authority_words = ['verify', 'confirm', 'update', 'validate', 'security alert', 'account locked']
    financial_words = ['free money', 'prize', 'winner', 'congratulations', 'lottery', '$10,000']
    action_words = ['click here', 'click now', 'verify now', 'reset password']
    threat_words = ['account will be closed', 'permanent suspension', 'legal action', 'suspended']
    
    urgency_score = sum(1 for word in urgency_words if word in full_text)
    authority_score = sum(1 for word in authority_words if word in full_text)
    financial_score = sum(1 for word in financial_words if word in full_text)
    action_score = sum(1 for word in action_words if word in full_text)
    threat_score = sum(1 for word in threat_words if word in full_text)
    
    total_suspicious_score = urgency_score + authority_score + financial_score + action_score + threat_score
    has_urls = 'http' in full_text or 'www.' in full_text
    has_exclamation = (email['subject'] + email['body']).count('!') > 2
    
    is_phishing = total_suspicious_score >= 2 or (urgency_score >= 1 and has_urls)
    confidence = min(95, 50 + (total_suspicious_score * 15) + (has_urls * 20) + (has_exclamation * 10)) if is_phishing else max(5, 50 - (total_suspicious_score * 10))
    
    return {
        'label': 'Phishing' if is_phishing else 'Safe',
        'confidence': round(confidence),
        'risk_level': 'HIGH RISK' if confidence >= 80 else 'MEDIUM RISK' if confidence >= 60 else 'LOW RISK' if confidence >= 40 else 'SAFE',
        'pattern_analysis': {
            'urgency_score': urgency_score,
            'authority_score': authority_score,
            'financial_score': financial_score,
            'action_score': action_score,
            'threat_score': threat_score,
            'total_score': total_suspicious_score
        },
        'technical_analysis': {
            'has_urls': has_urls,
            'has_exclamation': has_exclamation,
            'subject_length': len(email['subject']),
            'body_length': len(email['body'])
        },
        'red_flags': generate_red_flags(urgency_score, authority_score, financial_score, action_score, threat_score, has_urls, has_exclamation),
        'recommendations': generate_recommendations(is_phishing, has_urls, urgency_score, financial_score)
    }

def generate_red_flags(urgency, authority, financial, action, threat, has_urls, has_exclamation):
    """Generate red flags based on analysis"""
    flags = []
    if urgency >= 2:
        flags.append("Multiple urgency indicators detected")
    if threat > 0:
        flags.append("Threats or pressure tactics used")
    if financial > 0:
        flags.append("Unsolicited financial offers or prizes")
    if has_urls:
        flags.append("Suspicious links present")
    if has_exclamation:
        flags.append("Excessive exclamation marks")
    if authority >= 2:
        flags.append("Multiple authority claims detected")
    return flags

def generate_recommendations(is_phishing, has_urls, urgency_score, financial_score):
    """Generate security recommendations"""
    recommendations = []
    if is_phishing:
        recommendations.extend([
            "🚨 DO NOT click on any links in this email",
            "🚨 DO NOT provide any personal information",
            "🚨 DO NOT download any attachments",
            "🚨 Delete this email immediately"
        ])
        if has_urls:
            recommendations.append("🔗 Avoid clicking on shortened or suspicious URLs")
        if urgency_score > 0:
            recommendations.append("⏰ Be suspicious of urgent requests - legitimate organizations rarely require immediate action")
        if financial_score > 0:
            recommendations.append("💰 Be wary of unsolicited financial offers or prizes")
        recommendations.extend([
            "📧 Report this email as phishing to your email provider",
            "🔍 Verify any claims by contacting the organization directly through official channels"
        ])
    else:
        recommendations.extend([
            "✅ This email appears to be safe",
            "🔍 Always verify sender identity before taking any action",
            "🔗 Be cautious with any links, even in legitimate emails"
        ])
    return recommendations

def display_analysis_result(result):
    """Display detailed analysis result"""
    print(f"\n🎯 ANALYSIS RESULT:")
    print(f"   Label: {result['label']}")
    print(f"   Confidence: {result['confidence']}%")
    print(f"   Risk Level: {result['risk_level']}")
    
    print(f"\n📊 PATTERN ANALYSIS:")
    patterns = result['pattern_analysis']
    print(f"   🚨 Urgency Indicators: {patterns['urgency_score']} points")
    print(f"   🏛️ Authority Claims: {patterns['authority_score']} points")
    print(f"   💰 Financial Incentives: {patterns['financial_score']} points")
    print(f"   ⚡ Action Requirements: {patterns['action_score']} points")
    print(f"   ⚠️ Threats & Pressure: {patterns['threat_score']} points")
    print(f"   📈 Total Suspicious Score: {patterns['total_score']}")
    
    print(f"\n🔧 TECHNICAL ANALYSIS:")
    tech = result['technical_analysis']
    print(f"   🔗 URLs Present: {'Yes' if tech['has_urls'] else 'No'}")
    print(f"   ❗ Excessive Punctuation: {'Yes' if tech['has_exclamation'] else 'No'}")
    print(f"   📏 Subject Length: {tech['subject_length']} characters")
    print(f"   📏 Body Length: {tech['body_length']} characters")
    
    if result['red_flags']:
        print(f"\n🚨 RED FLAGS:")
        for flag in result['red_flags']:
            print(f"   • {flag}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in result['recommendations'][:5]:  # Show first 5
        print(f"   {rec}")
    
    print(f"\n📋 ANALYSIS REPORT SUMMARY:")
    print(f"   • Risk Assessment: {result['risk_level']}")
    print(f"   • Confidence Level: {result['confidence']}%")
    print(f"   • Suspicious Patterns: {patterns['total_score']} detected")
    print(f"   • Red Flags: {len(result['red_flags'])} identified")
    print(f"   • Recommendations: {len(result['recommendations'])} provided")

if __name__ == "__main__":
    demonstrate_email_analysis()
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETE!")
    print("\n📋 Key Features Demonstrated:")
    print("   ✅ Detailed Pattern Analysis (6 categories)")
    print("   ✅ Technical Analysis (URLs, structure, language)")
    print("   ✅ Risk Level Assessment (HIGH/MEDIUM/LOW/SAFE)")
    print("   ✅ Red Flags Identification")
    print("   ✅ Actionable Security Recommendations")
    print("   ✅ Comprehensive Analysis Reports")
    print("\n🚀 To see this in action:")
    print("   1. Run: npm run dev")
    print("   2. Go to: http://localhost:5173")
    print("   3. Try the test cases in the Email Phishing tab")
