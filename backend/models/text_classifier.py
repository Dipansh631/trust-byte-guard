from __future__ import annotations

from typing import Dict, Any, List
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
        
        # Common suspicious phrases for highlighting
        self.suspicious_phrases = [
            "urgent", "verify", "click", "account locked", "suspended", "immediately",
            "act now", "limited time", "congratulations", "winner", "prize", "free money",
            "reset password", "verify identity", "unlock account", "security alert",
            "confirm your account", "update your information", "expires soon",
            "click here", "verify now", "urgent action", "account verification"
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

    def _extract_suspicious_phrases(self, text: str) -> List[str]:
        """Extract suspicious phrases from the text"""
        found_phrases = []
        text_lower = text.lower()
        
        for phrase in self.suspicious_phrases:
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


