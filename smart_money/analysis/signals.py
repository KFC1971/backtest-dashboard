from typing import Dict, Tuple
import numpy as np


def calculate_signal_consistency(scores: Dict[str, float]) -> float:
    values = list(scores.values())
    if not values:
        return 50.0
    # Treat >55 as positive, <45 as negative, else neutral
    positives = sum(1 for v in values if v >= 55)
    negatives = sum(1 for v in values if v <= 45)
    consistency = abs(positives - negatives) / max(len(values), 1)
    return float(np.clip(consistency * 100, 0, 100))


def generate_final_signal(scores: Dict[str, float], weights: Dict[str, float]) -> Tuple[str, float, float]:
    # Center scores around 0: 50 -> 0, 0 -> -100, 100 -> +100
    centered_weighted = [((scores.get(k, 50) - 50.0) * 2.0) * weights.get(k, 0.0) for k in scores.keys()]
    weighted_score = float(sum(centered_weighted))

    consistency = calculate_signal_consistency(scores)
    confidence = min(100.0, consistency * 1.2)

    recommendation = "觀望"
    if weighted_score >= 60 and confidence >= 80:
        recommendation = "強烈買進"
    elif weighted_score >= 40 and confidence >= 70:
        recommendation = "標準買進"
    elif weighted_score >= 20 and confidence >= 60:
        recommendation = "小幅買進"
    elif weighted_score <= -60 and confidence >= 80:
        recommendation = "強烈賣出"
    elif weighted_score <= -40 and confidence >= 70:
        recommendation = "標準賣出"

    return recommendation, weighted_score, confidence
