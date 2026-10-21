from app.http import HTTPError

MAX_ATTEMPTS = 3


class ProfileClient:
    def __init__(self, transport):
        self.transport = transport

    def update_display_name(self, user_id, name):
        """Set the display name with optimistic concurrency.

        The profile API rejects a write with 412 when the ETag is stale, so
        re-read the profile and write again.
        """
        for attempt in range(MAX_ATTEMPTS):
            profile = self.transport.get(f"/profiles/{user_id}")
            try:
                return self.transport.put(
                    f"/profiles/{user_id}",
                    {**profile["body"], "display_name": name},
                    headers={"If-Match": profile["etag"]},
                )
            except HTTPError as exc:
                if exc.status != 412 or attempt == MAX_ATTEMPTS - 1:
                    raise
