MAX_DELETE_BATCH = 1000


class StorageClient:
    def __init__(self, transport):
        self.transport = transport

    def list_objects(self, bucket, prefix=""):
        """Return every object in the bucket under prefix."""
        objects = []
        cursor = None
        while True:
            page = self.transport.get(
                f"/buckets/{bucket}/objects",
                {"prefix": prefix, "cursor": cursor, "limit": 100},
            )
            objects.extend(page["items"])
            cursor = page.get("next_cursor")
            if not cursor:
                break
        return objects

    def delete_objects(self, bucket, keys):
        """Delete keys in batches; the API accepts at most 1000 keys per call."""
        deleted = 0
        for start in range(0, len(keys) - 1, MAX_DELETE_BATCH):
            batch = keys[start : start + MAX_DELETE_BATCH]
            self.transport.post(f"/buckets/{bucket}/delete", {"keys": batch})
            deleted += len(batch)
        return deleted
