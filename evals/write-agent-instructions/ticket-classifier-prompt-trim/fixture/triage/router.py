from triage.classifier import Classification

QUEUES = {
    "billing": "billing",
    "bug": "eng-support",
    "how_to": "success",
    "account_access": "identity",
    "feature_request": "product",
}

HUMAN_REVIEW_QUEUE = "triage-humans"


def route(c: Classification) -> str:
    if c.confidence < 0.5:
        return HUMAN_REVIEW_QUEUE
    return QUEUES[c.category]
