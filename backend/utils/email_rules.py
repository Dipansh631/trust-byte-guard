from __future__ import annotations

import re
from typing import Dict, List


PHISHING_KEYWORDS = [
    "click here",
    "verify your account",
    "urgent",
    "limited time",
    "suspend",
    "reset your password",
    "confirm your identity",
    "act now",
    "winner",
    "congratulations",
]


URL_REGEX = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def analyze_email_rules(text: str) -> Dict[str, object]:
    lowered = text.lower()
    reasons: List[str] = []

    # Keyword checks
    keyword_hits = [kw for kw in PHISHING_KEYWORDS if kw in lowered]
    if keyword_hits:
        for kw in keyword_hits:
            reasons.append(f"Contains '{kw}'")

    # URL presence
    urls = URL_REGEX.findall(text)
    if urls:
        reasons.append("Contains URLs")

    # Urgency tone heuristic
    urgency_patterns = [
        r"act now",
        r"immediately",
        r"within\s+24\s*hours",
        r"final\s+warning",
        r"last\s+chance",
    ]
    if any(re.search(p, lowered) for p in urgency_patterns):
        reasons.append("Urgent tone detected")

    # Sender spoof hints (very naive)
    if "@" in text and any(word in lowered for word in ["support", "security", "helpdesk"]):
        reasons.append("Mentions support/security with email-like content")

    # Score calculation (simple heuristic)
    base = 10 if urls else 0
    base += min(len(keyword_hits) * 15, 45)
    base += 20 if any(re.search(p, lowered) for p in urgency_patterns) else 0
    base += 10 if "password" in lowered else 0
    confidence = max(5, min(95, base))

    verdict = (
        "Phishing Likely 🚨" if confidence >= 70 else "Suspicious ⚠️" if confidence >= 40 else "Likely Safe ✅"
    )

    return {
        "confidence": confidence,
        "verdict": verdict,
        "reasons": reasons or ["No strong phishing indicators found"],
    }


