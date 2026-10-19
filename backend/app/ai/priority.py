import re

PRIORITY_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "urgent": 4,
}

URGENT_PATTERNS = [
    r"\bservice is completely down\b",
    r"\bproduction outage\b",
    r"\bsecurity breach\b",
    r"\baccount compromised\b",
    r"\bunauthorized access\b",
    r"\bcritical outage\b",
]

HIGH_PATTERNS = [
    r"\bmultiple users\b",
    r"\bunable to work\b",
    r"\bpayment failed\b",
    r"\bcharged twice\b",
    r"\bdata loss\b",
    r"\bkeeps crashing\b",
    r"\bdeadline today\b",
]

LOW_PATTERNS = [
    r"\bfeature request\b",
    r"\bgeneral question\b",
    r"\bhow do i\b",
    r"\binformation about\b",
]


def recommend_priority(title: str, description: str) -> dict:
    """Recommend a priority using explainable keyword rules."""
    text = f"{title} {description}".lower()
    reasons = []

    if any(re.search(pattern, text) for pattern in URGENT_PATTERNS):
        priority = "urgent"
        reasons.append(
            "The text contains a phrase associated with a possible "
            "outage or security incident."
        )
    elif any(re.search(pattern, text) for pattern in HIGH_PATTERNS):
        priority = "high"
        reasons.append(
            "The text contains a phrase associated with significant "
            "service or payment impact."
        )
    elif any(re.search(pattern, text) for pattern in LOW_PATTERNS):
        priority = "low"
        reasons.append(
            "The text appears to describe a general question or feature request."
        )
    else:
        priority = "medium"
        reasons.append(
            "No configured high- or urgent-impact phrase was detected; "
            "manual review may change this recommendation."
        )

    return {
        "recommended_priority": priority,
        "method": "keyword_rules",
        "reasons": reasons,
        "requires_human_review": True,
        "notice": (
            "This is a heuristic recommendation, not a prediction of actual "
            "business impact. Review the ticket before changing its priority."
        ),
    }
