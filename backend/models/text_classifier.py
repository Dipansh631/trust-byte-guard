from __future__ import annotations

from typing import Dict, Any, List, Tuple
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np


class TextClassifier:
    def __init__(self):
        # Load the Hugging Face BERT model for phishing detection
        self.model_name = "mrm8488/bert-tiny-finetuned-phishing"
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_model()
        
        # Comprehensive suspicious phrases categorized by type
        self.suspicious_patterns = {
            "urgency": [
                "urgent", "immediately", "asap", "right now", "act now", "limited time",
                "expires soon", "deadline", "hurry", "quick", "instant", "emergency"
            ],
            "authority": [
                "verify", "confirm", "update", "validate", "authenticate", "authorize",
                "security alert", "account locked", "suspended", "compromised", "breach"
            ],
            "financial": [
                "free money", "prize", "winner", "congratulations", "lottery", "inheritance",
                "tax refund", "payment", "billing", "invoice", "overdue", "charge"
            ],
            "action_required": [
                "click here", "click now", "verify now", "reset password", "unlock account",
                "download", "install", "update now", "confirm identity", "reactivate"
            ],
            "social_engineering": [
                "trusted", "official", "secure", "protected", "guaranteed", "certified",
                "legitimate", "authorized", "verified", "approved", "safe"
            ],
            "threats": [
                "account will be closed", "permanent suspension", "legal action", "fines",
                "penalties", "consequences", "violation", "terminated", "blocked"
            ]
        }
        
        # Additional patterns for analysis
        self.url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'[a-zA-Z0-9.-]+\.(?:com|org|net|info|biz|co|uk|us|ca|au|de|fr|it|es|jp|cn|in|ru|br|mx|ar|cl|pe|ve|co|ec|uy|py|bo|gf|sr|gy|fk|gs|tc|vg|ai|ag|bb|bs|bz|dm|gd|gy|jm|kn|lc|ms|sr|tt|vc|ws)'
        ]
        
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ]

    def _load_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ Loaded BERT model: {self.model_name}")
        except Exception as e:
            print(f"❌ Error loading BERT model: {e}")
            print("Falling back to simple rule-based detection")
            self.model = None
            self.tokenizer = None

    def _analyze_suspicious_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze text for suspicious patterns and categorize them"""
        text_lower = text.lower()
        analysis = {
            "urgency_score": 0,
            "authority_score": 0,
            "financial_score": 0,
            "action_required_score": 0,
            "social_engineering_score": 0,
            "threats_score": 0,
            "found_patterns": {},
            "total_suspicious_score": 0
        }
        
        # Analyze each category
        for category, patterns in self.suspicious_patterns.items():
            found_patterns = []
            score = 0
            
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    found_patterns.append(pattern)
                    score += 1
            
            analysis[f"{category}_score"] = score
            analysis["found_patterns"][category] = found_patterns
        
        # Calculate total suspicious score
        analysis["total_suspicious_score"] = sum([
            analysis["urgency_score"],
            analysis["authority_score"], 
            analysis["financial_score"],
            analysis["action_required_score"],
            analysis["social_engineering_score"],
            analysis["threats_score"]
        ])
        
        return analysis

    def _analyze_urls_and_links(self, text: str) -> Dict[str, Any]:
        """Analyze URLs and links in the text"""
        analysis = {
            "urls_found": [],
            "suspicious_urls": [],
            "url_count": 0,
            "suspicious_domains": [],
            "shortened_urls": []
        }
        
        # Find all URLs
        for pattern in self.url_patterns:
            urls = re.findall(pattern, text, re.IGNORECASE)
            analysis["urls_found"].extend(urls)
        
        analysis["url_count"] = len(analysis["urls_found"])
        
        # Analyze URLs for suspicious characteristics
        suspicious_domains = [
            "bit.ly", "tinyurl.com", "short.link", "goo.gl", "t.co", "ow.ly",
            "is.gd", "v.gd", "shorturl.at", "rebrand.ly", "cutt.ly"
        ]
        
        for url in analysis["urls_found"]:
            url_lower = url.lower()
            
            # Check for shortened URLs
            for short_domain in suspicious_domains:
                if short_domain in url_lower:
                    analysis["shortened_urls"].append(url)
                    analysis["suspicious_urls"].append(url)
                    break
            
            # Check for suspicious patterns in URLs
            if any(suspicious in url_lower for suspicious in ["verify", "confirm", "update", "security", "account"]):
                analysis["suspicious_urls"].append(url)
        
        return analysis

    def _analyze_email_structure(self, subject: str, body: str) -> Dict[str, Any]:
        """Analyze email structure and formatting"""
        analysis = {
            "subject_length": len(subject),
            "body_length": len(body),
            "excessive_punctuation": 0,
            "all_caps_words": [],
            "exclamation_count": 0,
            "question_count": 0,
            "suspicious_formatting": []
        }
        
        # Analyze punctuation
        analysis["exclamation_count"] = subject.count("!") + body.count("!")
        analysis["question_count"] = subject.count("?") + body.count("?")
        
        if analysis["exclamation_count"] > 3:
            analysis["excessive_punctuation"] = analysis["exclamation_count"]
            analysis["suspicious_formatting"].append("Excessive exclamation marks")
        
        # Find all caps words
        words = re.findall(r'\b[A-Z]{3,}\b', subject + " " + body)
        analysis["all_caps_words"] = [word for word in words if len(word) > 2]
        
        if len(analysis["all_caps_words"]) > 2:
            analysis["suspicious_formatting"].append("Excessive use of capital letters")
        
        # Check for suspicious subject patterns
        subject_lower = subject.lower()
        if any(word in subject_lower for word in ["urgent", "important", "action required", "security alert"]):
            analysis["suspicious_formatting"].append("Urgent/alert language in subject")
        
        return analysis

    def _analyze_grammar_and_language(self, text: str) -> Dict[str, Any]:
        """Analyze grammar and language patterns"""
        analysis = {
            "grammar_errors": [],
            "suspicious_language": [],
            "spelling_errors": [],
            "language_quality_score": 0
        }
        
        # Common phishing grammar patterns
        grammar_patterns = [
            (r'\b(?:is|are|was|were)\s+(?:urgent|important|critical)\s+(?:that|to)\b', "Urgent language pattern"),
            (r'\b(?:please|kindly)\s+(?:verify|confirm|update|click)\b', "Polite urgency pattern"),
            (r'\b(?:your|you)\s+(?:account|profile|information)\s+(?:has|have)\s+(?:been|is)\s+(?:locked|suspended|compromised)\b', "Account status threat"),
            (r'\b(?:click|visit)\s+(?:here|below|this)\s+(?:link|button|to)\b', "Action instruction pattern"),
            (r'\b(?:failure|fail)\s+(?:to|in)\s+(?:verify|confirm|update)\b', "Failure threat pattern")
        ]
        
        for pattern, description in grammar_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                analysis["suspicious_language"].append(description)
        
        # Calculate language quality score
        analysis["language_quality_score"] = max(0, 100 - len(analysis["suspicious_language"]) * 20)
        
        return analysis

    def _generate_detailed_analysis(self, subject: str, body: str, label: str, confidence: int, pattern_analysis: Dict, url_analysis: Dict, structure_analysis: Dict, language_analysis: Dict) -> Dict[str, Any]:
        """Generate comprehensive detailed analysis"""
        
        detailed_analysis = {
            "overall_assessment": {
                "label": label,
                "confidence": confidence,
                "risk_level": self._get_risk_level(confidence),
                "summary": self._generate_summary(label, confidence, pattern_analysis)
            },
            "pattern_analysis": {
                "urgency_indicators": {
                    "score": pattern_analysis["urgency_score"],
                    "patterns_found": pattern_analysis["found_patterns"].get("urgency", []),
                    "explanation": "High urgency language is commonly used in phishing emails to pressure victims into quick action."
                },
                "authority_claims": {
                    "score": pattern_analysis["authority_score"],
                    "patterns_found": pattern_analysis["found_patterns"].get("authority", []),
                    "explanation": "Phishing emails often impersonate legitimate authorities or institutions."
                },
                "financial_incentives": {
                    "score": pattern_analysis["financial_score"],
                    "patterns_found": pattern_analysis["found_patterns"].get("financial", []),
                    "explanation": "Offers of money, prizes, or financial benefits are common phishing tactics."
                },
                "action_requirements": {
                    "score": pattern_analysis["action_required_score"],
                    "patterns_found": pattern_analysis["found_patterns"].get("action_required", []),
                    "explanation": "Phishing emails typically require immediate action from the victim."
                },
                "social_engineering": {
                    "score": pattern_analysis["social_engineering_score"],
                    "patterns_found": pattern_analysis["found_patterns"].get("social_engineering", []),
                    "explanation": "Trust-building language is used to make phishing attempts appear legitimate."
                },
                "threats_and_pressure": {
                    "score": pattern_analysis["threats_score"],
                    "patterns_found": pattern_analysis["found_patterns"].get("threats", []),
                    "explanation": "Threats of account closure or legal action are common phishing tactics."
                }
            },
            "technical_analysis": {
                "urls_and_links": {
                    "total_urls": url_analysis["url_count"],
                    "suspicious_urls": url_analysis["suspicious_urls"],
                    "shortened_urls": url_analysis["shortened_urls"],
                    "explanation": "Suspicious or shortened URLs are often used to hide malicious destinations."
                },
                "email_structure": {
                    "subject_length": structure_analysis["subject_length"],
                    "body_length": structure_analysis["body_length"],
                    "excessive_punctuation": structure_analysis["excessive_punctuation"],
                    "all_caps_words": structure_analysis["all_caps_words"],
                    "suspicious_formatting": structure_analysis["suspicious_formatting"],
                    "explanation": "Unusual formatting, excessive punctuation, or all-caps text can indicate phishing."
                },
                "language_quality": {
                    "suspicious_patterns": language_analysis["suspicious_language"],
                    "quality_score": language_analysis["language_quality_score"],
                    "explanation": "Poor grammar, unusual language patterns, or suspicious phrasing can indicate phishing."
                }
            },
            "recommendations": self._generate_recommendations(label, confidence, pattern_analysis, url_analysis),
            "red_flags": self._identify_red_flags(pattern_analysis, url_analysis, structure_analysis, language_analysis)
        }
        
        return detailed_analysis

    def _get_risk_level(self, confidence: int) -> str:
        """Determine risk level based on confidence score"""
        if confidence >= 80:
            return "HIGH RISK"
        elif confidence >= 60:
            return "MEDIUM RISK"
        elif confidence >= 40:
            return "LOW RISK"
        else:
            return "SAFE"

    def _generate_summary(self, label: str, confidence: int, pattern_analysis: Dict) -> str:
        """Generate a comprehensive summary of the analysis"""
        if label == "Phishing":
            total_score = pattern_analysis["total_suspicious_score"]
            if confidence >= 80:
                return f"This email shows STRONG indicators of phishing with {total_score} suspicious patterns detected. The high confidence score ({confidence}%) suggests this is very likely a phishing attempt."
            elif confidence >= 60:
                return f"This email shows MODERATE indicators of phishing with {total_score} suspicious patterns detected. The confidence score ({confidence}%) suggests this could be a phishing attempt."
            else:
                return f"This email shows WEAK indicators of phishing with {total_score} suspicious patterns detected. The low confidence score ({confidence}%) suggests this might be a phishing attempt."
        else:
            return f"This email appears to be legitimate with minimal suspicious patterns detected. The confidence score ({confidence}%) suggests this is likely a safe email."

    def _generate_recommendations(self, label: str, confidence: int, pattern_analysis: Dict, url_analysis: Dict) -> List[str]:
        """Generate security recommendations based on analysis"""
        recommendations = []
        
        if label == "Phishing":
            recommendations.append("🚨 DO NOT click on any links in this email")
            recommendations.append("🚨 DO NOT provide any personal information")
            recommendations.append("🚨 DO NOT download any attachments")
            recommendations.append("🚨 Delete this email immediately")
            
            if url_analysis["suspicious_urls"]:
                recommendations.append("🔗 Avoid clicking on shortened or suspicious URLs")
            
            if pattern_analysis["urgency_score"] > 0:
                recommendations.append("⏰ Be suspicious of urgent requests - legitimate organizations rarely require immediate action")
            
            if pattern_analysis["financial_score"] > 0:
                recommendations.append("💰 Be wary of unsolicited financial offers or prizes")
            
            recommendations.append("📧 Report this email as phishing to your email provider")
            recommendations.append("🔍 Verify any claims by contacting the organization directly through official channels")
        else:
            recommendations.append("✅ This email appears to be safe")
            recommendations.append("🔍 Always verify sender identity before taking any action")
            recommendations.append("🔗 Be cautious with any links, even in legitimate emails")
        
        return recommendations

    def _identify_red_flags(self, pattern_analysis: Dict, url_analysis: Dict, structure_analysis: Dict, language_analysis: Dict) -> List[str]:
        """Identify specific red flags in the email"""
        red_flags = []
        
        # Pattern-based red flags
        if pattern_analysis["urgency_score"] >= 3:
            red_flags.append("Multiple urgency indicators detected")
        
        if pattern_analysis["threats_score"] > 0:
            red_flags.append("Threats or pressure tactics used")
        
        if pattern_analysis["financial_score"] > 0:
            red_flags.append("Unsolicited financial offers or prizes")
        
        # URL-based red flags
        if url_analysis["shortened_urls"]:
            red_flags.append("Shortened URLs present (common in phishing)")
        
        if url_analysis["url_count"] > 3:
            red_flags.append("Excessive number of links")
        
        # Structure-based red flags
        if structure_analysis["excessive_punctuation"] > 3:
            red_flags.append("Excessive exclamation marks")
        
        if len(structure_analysis["all_caps_words"]) > 2:
            red_flags.append("Excessive use of capital letters")
        
        # Language-based red flags
        if language_analysis["language_quality_score"] < 60:
            red_flags.append("Poor language quality or suspicious phrasing")
        
        return red_flags

    def predict_suspicion(self, text: str) -> Dict[str, Any]:
        if self.model is None or self.tokenizer is None:
            # Fallback to simple rule-based detection
            return self._fallback_detection(text)
        
        try:
            # Prepare input for BERT model
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            ).to(self.device)
            
            # Get model prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Extract probabilities
            probabilities = predictions.cpu().numpy()[0]
            
            # Assuming the model has labels: [0: legitimate, 1: phishing]
            # We need to check the actual model configuration
            phishing_prob = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])
            legitimate_prob = float(probabilities[0]) if len(probabilities) > 1 else float(probabilities[1])
            
            # Determine label and confidence
            if phishing_prob > legitimate_prob:
                label = "Phishing"
                confidence = phishing_prob
            else:
                label = "Safe"
                confidence = legitimate_prob
            
            # Convert to 0-100 scale
            confidence_percent = int(round(confidence * 100))
            trust_score = confidence_percent
            
            # Extract suspicious phrases
            suspicious_phrases = self._extract_suspicious_phrases(text)
            
            # Generate reason analysis
            reason_analysis = self._generate_reason_analysis(label, confidence_percent, suspicious_phrases)
            
            return {
                "label": label,
                "confidence": confidence_percent,
                "trust_score": trust_score,
                "suspicious_phrases": suspicious_phrases,
                "reason_analysis": reason_analysis,
                "raw_score": float(confidence),
                "model": "bert-tiny-finetuned-phishing"
            }
            
        except Exception as e:
            print(f"Error in BERT prediction: {e}")
            return self._fallback_detection(text)

    def analyze_email_detailed(self, subject: str, body: str) -> Dict[str, Any]:
        """Perform comprehensive email analysis with detailed breakdown"""
        try:
            # Combine subject and body for analysis
            full_text = f"Subject: {subject}\n\nBody: {body}"
            
            # Get basic prediction
            basic_result = self.predict_suspicion(full_text)
            
            # Perform detailed analysis
            pattern_analysis = self._analyze_suspicious_patterns(full_text)
            url_analysis = self._analyze_urls_and_links(full_text)
            structure_analysis = self._analyze_email_structure(subject, body)
            language_analysis = self._analyze_grammar_and_language(full_text)
            
            # Generate detailed analysis
            detailed_analysis = self._generate_detailed_analysis(
                subject, body, basic_result["label"], basic_result["confidence"],
                pattern_analysis, url_analysis, structure_analysis, language_analysis
            )
            
            # Combine basic result with detailed analysis
            result = {
                "label": basic_result["label"],
                "confidence": basic_result["confidence"],
                "trust_score": basic_result["trust_score"],
                "suspicious_phrases": basic_result["suspicious_phrases"],
                "reason_analysis": basic_result["reason_analysis"],
                "raw_score": basic_result["raw_score"],
                "model": basic_result["model"],
                "detailed_analysis": detailed_analysis
            }
            
            return result
            
        except Exception as e:
            print(f"Error in detailed email analysis: {e}")
            return self._fallback_detection(f"Subject: {subject}\n\nBody: {body}")

    def _extract_suspicious_phrases(self, text: str) -> List[str]:
        """Extract suspicious phrases from the text"""
        found_phrases = []
        text_lower = text.lower()
        
        # Flatten all patterns from all categories
        all_patterns = []
        for patterns in self.suspicious_patterns.values():
            all_patterns.extend(patterns)
        
        for phrase in all_patterns:
            if phrase.lower() in text_lower:
                found_phrases.append(phrase)
        
        return found_phrases

    def _generate_reason_analysis(self, label: str, confidence: float, suspicious_phrases: List[str]) -> str:
        """Generate human-readable explanation for the analysis"""
        if label == "Phishing":
            if confidence > 80:
                reason = "High confidence phishing detection. "
            elif confidence > 60:
                reason = "Moderate confidence phishing detection. "
            else:
                reason = "Low confidence phishing detection. "
            
            if suspicious_phrases:
                reason += f"Detected suspicious phrases: {', '.join(suspicious_phrases[:3])}. "
            
            reason += "This email contains characteristics commonly found in phishing attempts."
        else:
            reason = "Email appears to be legitimate. "
            if confidence < 30:
                reason += "No suspicious patterns detected."
            else:
                reason += "Some minor suspicious elements present but not enough to classify as phishing."
        
        return reason

    def _fallback_detection(self, text: str) -> Dict[str, Any]:
        """Fallback rule-based detection when BERT model fails"""
        text_lower = text.lower()
        
        # Simple scoring based on suspicious keywords
        suspicious_keywords = [
            "urgent", "verify", "click", "account", "suspended", "immediately",
            "congratulations", "winner", "prize", "free", "reset", "password",
            "security", "alert", "confirm", "update", "expires", "limited"
        ]
        
        score = 0
        found_phrases = []
        
        for keyword in suspicious_keywords:
            if keyword in text_lower:
                score += 10
                found_phrases.append(keyword)
        
        # Additional checks
        if "http" in text_lower or "www." in text_lower:
            score += 15
            found_phrases.append("suspicious link")
        
        if "!" in text and text.count("!") > 2:
            score += 10
            found_phrases.append("excessive punctuation")
        
        # Normalize score to 0-100
        confidence = min(score, 100)
        
        if confidence >= 50:
            label = "Phishing"
        else:
            label = "Safe"
        
        trust_score = confidence
        reason_analysis = self._generate_reason_analysis(label, confidence, found_phrases)
        
        return {
            "label": label,
            "confidence": confidence,
            "trust_score": trust_score,
            "suspicious_phrases": found_phrases,
            "reason_analysis": reason_analysis,
            "raw_score": confidence / 100.0,
            "model": "rule-based-fallback"
        }


