from __future__ import annotations

from typing import Dict, List


def analyze_media_placeholder(filename: str, content_type: str | None, data: bytes) -> Dict[str, object]:
    size_bytes = len(data)
    reasons: List[str] = []

    # Very naive heuristics for MVP placeholder
    if size_bytes < 10_000:  # <10KB often indicates low-quality or synthetic placeholder
        reasons.append("Very small file size")

    if content_type and not content_type.startswith(("image/", "video/")):
        reasons.append("Unexpected content type")

    # Confidence: bigger for anomalies
    confidence = 20
    if size_bytes < 10_000:
        confidence += 40
    if ".exe" in filename.lower() or "script" in filename.lower():
        confidence += 30
        reasons.append("Suspicious filename extension")

    confidence = max(5, min(95, confidence))

    verdict = (
        "Deepfake Likely 🚨" if confidence >= 70 else "Suspicious ⚠️" if confidence >= 40 else "Likely Authentic ✅"
    )

    return {
        "confidence": confidence,
        "verdict": verdict,
        "reasons": reasons or ["No obvious manipulation indicators from placeholder checks"],
    }


