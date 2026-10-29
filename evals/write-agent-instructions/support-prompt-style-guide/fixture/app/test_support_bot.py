from support_bot import SYSTEM_PROMPT


def test_prompt_keeps_refund_rule():
    assert "Never promise a refund" in SYSTEM_PROMPT
