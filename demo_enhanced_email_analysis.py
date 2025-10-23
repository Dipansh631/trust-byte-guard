#!/usr/bin/env python3
"""
Enhanced Email Analysis Demo
Demonstrates the comprehensive email phishing detection with detailed analysis
"""

import json
from datetime import datetime

def demo_enhanced_email_analysis():
    """Demonstrate the enhanced email analysis features"""
    
    print("🔍 Enhanced Email Analysis Demo")
    print("=" * 50)
    print()
    
    # Sample phishing email
    phishing_email = {
        "subject": "URGENT: Your account will be suspended in 24 hours!",
        "body": """
Dear Valued Customer,

We have detected suspicious activity on your account. Your account will be SUSPENDED within 24 hours unless you verify your identity immediately.

CLICK HERE NOW: http://bit.ly/verify-account-now

This is your FINAL WARNING! Do not ignore this message or you will lose access to your account permanently.

Act now or face the consequences!

Best regards,
Security Team
        """.strip()
    }
    
    # Sample legitimate email
    legitimate_email = {
        "subject": "Monthly Newsletter - December 2024",
        "body": """
Hello,

Thank you for subscribing to our monthly newsletter. Here are the highlights from December 2024:

1. New product launches
2. Industry updates
3. Customer success stories

You can unsubscribe at any time by clicking the link below.

Best regards,
Marketing Team
        """.strip()
    }
    
    print("📧 Sample Phishing Email Analysis")
    print("-" * 40)
    analyze_email_demo(phishing_email, "Phishing")
    
    print("\n" + "=" * 50)
    print()
    
    print("📧 Sample Legitimate Email Analysis")
    print("-" * 40)
    analyze_email_demo(legitimate_email, "Legitimate")

def analyze_email_demo(email_data, expected_label):
    """Simulate email analysis with detailed breakdown"""
    
    subject = email_data["subject"]
    body = email_data["body"]
    
    print(f"Subject: {subject}")
    print(f"Body: {body[:100]}...")
    print()
    
    # Simulate detailed analysis results
    if expected_label == "Phishing":
        detailed_analysis = {
            "overall_assessment": {
                "label": "Phishing",
                "confidence": 87,
                "risk_level": "High",
                "summary": "This email exhibits multiple characteristics of phishing attempts, including urgency tactics, authority claims, and suspicious URLs."
            },
            "pattern_analysis": {
                "urgency_indicators": {
                    "score": 95,
                    "patterns_found": ["URGENT", "24 hours", "FINAL WARNING", "Act now"],
                    "explanation": "High urgency language designed to create panic and force immediate action"
                },
                "authority_claims": {
                    "score": 80,
                    "patterns_found": ["Security Team", "account suspension", "suspicious activity"],
                    "explanation": "Claims authority without proper verification mechanisms"
                },
                "financial_incentives": {
                    "score": 60,
                    "patterns_found": ["account suspension", "lose access"],
                    "explanation": "Threatens financial loss to pressure user action"
                },
                "action_requirements": {
                    "score": 90,
                    "patterns_found": ["CLICK HERE NOW", "verify your identity immediately"],
                    "explanation": "Demands immediate action without proper context"
                },
                "social_engineering": {
                    "score": 85,
                    "patterns_found": ["Valued Customer", "suspicious activity detected"],
                    "explanation": "Uses social engineering to create false sense of urgency"
                },
                "threats_and_pressure": {
                    "score": 95,
                    "patterns_found": ["face the consequences", "FINAL WARNING", "permanently"],
                    "explanation": "Uses threats and pressure tactics to force compliance"
                }
            },
            "technical_analysis": {
                "urls_and_links": {
                    "total_urls": 1,
                    "suspicious_urls": ["http://bit.ly/verify-account-now"],
                    "shortened_urls": ["http://bit.ly/verify-account-now"],
                    "explanation": "Contains shortened URL that could redirect to malicious site"
                },
                "email_structure": {
                    "subject_length": 45,
                    "body_length": 420,
                    "excessive_punctuation": 8,
                    "all_caps_words": ["URGENT", "SUSPENDED", "CLICK HERE NOW", "FINAL WARNING"],
                    "suspicious_formatting": ["Excessive exclamation marks", "All caps words", "Urgency formatting"],
                    "explanation": "Poor email structure with excessive punctuation and formatting"
                },
                "language_quality": {
                    "suspicious_patterns": ["Urgency language", "Threats", "Poor grammar"],
                    "quality_score": 35,
                    "explanation": "Low language quality with multiple suspicious patterns"
                }
            },
            "recommendations": [
                "Do not click on any links in this email",
                "Verify the sender through official channels",
                "Report this email to your IT security team",
                "Never provide personal information via email links"
            ],
            "red_flags": [
                "Urgent language demanding immediate action",
                "Threats of account suspension",
                "Suspicious shortened URL",
                "Poor grammar and excessive punctuation",
                "Claims of suspicious activity without proper context"
            ]
        }
    else:
        detailed_analysis = {
            "overall_assessment": {
                "label": "Legitimate",
                "confidence": 92,
                "risk_level": "Low",
                "summary": "This email appears to be a legitimate newsletter with no suspicious patterns detected."
            },
            "pattern_analysis": {
                "urgency_indicators": {
                    "score": 5,
                    "patterns_found": [],
                    "explanation": "No urgency language detected"
                },
                "authority_claims": {
                    "score": 10,
                    "patterns_found": ["Marketing Team"],
                    "explanation": "Appropriate authority claim for newsletter content"
                },
                "financial_incentives": {
                    "score": 0,
                    "patterns_found": [],
                    "explanation": "No financial incentives or threats detected"
                },
                "action_requirements": {
                    "score": 15,
                    "patterns_found": ["unsubscribe"],
                    "explanation": "Optional action with clear unsubscribe option"
                },
                "social_engineering": {
                    "score": 5,
                    "patterns_found": [],
                    "explanation": "No social engineering tactics detected"
                },
                "threats_and_pressure": {
                    "score": 0,
                    "patterns_found": [],
                    "explanation": "No threats or pressure tactics detected"
                }
            },
            "technical_analysis": {
                "urls_and_links": {
                    "total_urls": 1,
                    "suspicious_urls": [],
                    "shortened_urls": [],
                    "explanation": "No suspicious URLs detected"
                },
                "email_structure": {
                    "subject_length": 35,
                    "body_length": 280,
                    "excessive_punctuation": 0,
                    "all_caps_words": [],
                    "suspicious_formatting": [],
                    "explanation": "Well-structured email with appropriate formatting"
                },
                "language_quality": {
                    "suspicious_patterns": [],
                    "quality_score": 95,
                    "explanation": "High language quality with professional tone"
                }
            },
            "recommendations": [
                "This email appears safe to read",
                "Verify sender if you have concerns",
                "Use unsubscribe link if no longer interested"
            ],
            "red_flags": []
        }
    
    # Display analysis results
    print("🔍 DETAILED ANALYSIS REPORT")
    print("=" * 30)
    
    print(f"📊 Classification: {detailed_analysis['overall_assessment']['label']}")
    print(f"🎯 Confidence: {detailed_analysis['overall_assessment']['confidence']}%")
    print(f"⚠️  Risk Level: {detailed_analysis['overall_assessment']['risk_level']}")
    print(f"📝 Summary: {detailed_analysis['overall_assessment']['summary']}")
    print()
    
    print("🧠 ANALYSIS THEORY & METHODOLOGY")
    print("-" * 35)
    print("Our AI analyzes emails using:")
    print("• Pattern Recognition: Identifies common phishing techniques")
    print("• Technical Analysis: Examines URLs, structure, and language quality")
    print("• Behavioral Analysis: Detects social engineering tactics")
    print("• Risk Assessment: Calculates overall threat level")
    print()
    
    print("📈 PATTERN ANALYSIS BREAKDOWN")
    print("-" * 30)
    for pattern_type, analysis in detailed_analysis['pattern_analysis'].items():
        print(f"• {pattern_type.replace('_', ' ').title()}: {analysis['score']}%")
        if analysis['patterns_found']:
            print(f"  Patterns: {', '.join(analysis['patterns_found'][:3])}")
        print(f"  Explanation: {analysis['explanation']}")
        print()
    
    print("🔧 TECHNICAL ANALYSIS")
    print("-" * 20)
    tech = detailed_analysis['technical_analysis']
    print(f"• URLs Found: {tech['urls_and_links']['total_urls']}")
    print(f"• Suspicious URLs: {len(tech['urls_and_links']['suspicious_urls'])}")
    print(f"• Language Quality: {tech['language_quality']['quality_score']}%")
    print(f"• Excessive Punctuation: {tech['email_structure']['excessive_punctuation']}")
    print()
    
    if detailed_analysis['red_flags']:
        print("🚨 RED FLAGS DETECTED")
        print("-" * 20)
        for i, flag in enumerate(detailed_analysis['red_flags'], 1):
            print(f"{i}. {flag}")
        print()
    
    print("💡 SECURITY RECOMMENDATIONS")
    print("-" * 25)
    for i, rec in enumerate(detailed_analysis['recommendations'], 1):
        print(f"{i}. {rec}")
    print()
    
    print("📋 ANALYSIS REPORT SUMMARY")
    print("-" * 25)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Email Type: {expected_label}")
    print(f"Confidence Level: {detailed_analysis['overall_assessment']['confidence']}%")
    print(f"Risk Assessment: {detailed_analysis['overall_assessment']['risk_level']}")
    print(f"Red Flags: {len(detailed_analysis['red_flags'])}")
    print(f"Recommendations: {len(detailed_analysis['recommendations'])}")

if __name__ == "__main__":
    demo_enhanced_email_analysis()
