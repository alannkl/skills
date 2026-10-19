from app.parse import parse_reply


def test_parse_reply():
    reply = '{"summary": "Agreed the launch date.", "actions": [{"owner": null, "task": "Book the room"}], "confidence": 0.8}'
    assert parse_reply(reply)["actions"] == [(None, "Book the room")]
