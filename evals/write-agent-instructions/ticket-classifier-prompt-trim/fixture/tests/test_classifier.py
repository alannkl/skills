from triage.classifier import parse_response


def test_parse_valid():
    c = parse_response('{"category": "bug", "urgency": "high", "confidence": 0.9}')
    assert (c.category, c.urgency, c.confidence) == ("bug", "high", 0.9)


def test_unknown_category_falls_back_to_other():
    c = parse_response('{"category": "sales", "urgency": "low", "confidence": 0.7}')
    assert c.category == "other"
