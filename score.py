def calculate_score(findings):
    weights = {
        "CRITICAL": 10,
        "HIGH": 3, "ERROR": 3,
        "MEDIUM": 1, "WARNING": 1,
        "LOW": 0.3, "INFO": 0.3
    }
    penalty = 0
    for f in findings:
        sev = f["severity"].upper()
        penalty += weights.get(sev, 1)

    import math
    penalty = 5 * math.sqrt(penalty)   # naram scaling

    score = round(100 - penalty)
    score = max(0, min(100, score))

    if score >= 90: grade = "A"
    elif score >= 75: grade = "B"
    elif score >= 60: grade = "C"
    elif score >= 40: grade = "D"
    else: grade = "F"

    return score, grade