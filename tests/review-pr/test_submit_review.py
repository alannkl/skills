"""submit-review.mjs keeps comments GitHub can anchor inline and moves the rest into the review body."""
import json
import unittest

from fixtures import PR_URL, REPO, Sandbox

HEAD = "a" * 40
PULL = f"repos/{REPO}/pulls/1"
# Hunk 1: left lines 1-4, right lines 1-5 (right 2-3 added, left 2 deleted).
# Hunk 2: left lines 20-22, right lines 21-23 (right 22 added, left 21 deleted).
PATCH = "\n".join([
    "@@ -1,4 +1,5 @@",
    " one",
    "-two",
    "+TWO",
    "+extra",
    " three",
    " four",
    "@@ -20,3 +21,3 @@",
    " twenty",
    "-twentyone",
    "+TWENTYONE",
    " twentytwo",
    "\\ No newline at end of file",
])


class SubmitReviewAnchors(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.addCleanup(self.sandbox.close)
        self.sandbox.set_gh({
            "pr": {"number": 1, "url": PR_URL, "state": "OPEN", "headRefOid": HEAD},
            "viewer": "reviewer",
            f"{PULL}/reviews": [],
            f"{PULL}/files": [
                {"filename": "src/app.txt", "patch": PATCH},
                {"filename": "img.png"},
            ],
        })

    def dry_run(self, *comments):
        review = self.sandbox.root / "review.json"
        review.write_text(json.dumps({
            "commit_id": HEAD, "event": "REQUEST_CHANGES", "body": "Summary",
            "comments": [{"body": f"note {i}", **c} for i, c in enumerate(comments)],
        }))
        result = self.sandbox.node("submit-review.mjs", "1", "--in", str(review), "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any("POST" in call["args"] for call in self.sandbox.gh_calls()))
        output = json.loads(result.stdout)
        self.payload = output["payload"]
        for comment in self.payload["comments"]:
            self.assertNotIn("start_line", comment)
            self.assertNotIn("start_side", comment)
        inline = {(c["path"], c.get("start_line"), c["line"], c["side"]) for c in output["payload"]["comments"]}
        return inline, set(output["movedToBody"]), output["payload"]["body"]

    def test_anchors_follow_the_side_where_the_line_exists(self):
        """Given an added right line and a deleted left line, when submitted, then both stay inline; left 5 and right 10 fall outside their side's hunks and move to the body."""
        inline, moved, _ = self.dry_run(
            {"path": "src/app.txt", "line": 3, "side": "RIGHT"},
            {"path": "src/app.txt", "line": 2, "side": "LEFT"},
            {"path": "src/app.txt", "line": 5, "side": "LEFT"},
            {"path": "src/app.txt", "line": 10, "side": "RIGHT"},
        )
        self.assertEqual(inline, {("src/app.txt", None, 3, "RIGHT"), ("src/app.txt", None, 2, "LEFT")})
        self.assertEqual(moved, {"src/app.txt:5", "src/app.txt:10"})

    def test_second_hunk_uses_its_own_line_numbers(self):
        """Given right lines 23 and 20 around the second hunk, when submitted, then 23 stays inline and 20 moves to the body."""
        inline, moved, _ = self.dry_run(
            {"path": "src/app.txt", "line": 23, "side": "RIGHT"},
            {"path": "src/app.txt", "line": 20, "side": "RIGHT"},
        )
        self.assertEqual(inline, {("src/app.txt", None, 23, "RIGHT")})
        self.assertEqual(moved, {"src/app.txt:20"})

    def test_ranges_anchor_only_the_end_and_preserve_the_range_as_text(self):
        """Given contiguous, cross-hunk, outside-start, equal and reversed ranges with valid ends, when submitted, then each stays inline at its end with range text and no range fields."""
        for start, end in [(1, 4), (1, 22), (10, 22), (4, 4), (22, 4)]:
            with self.subTest(start=start, end=end):
                inline, moved, body = self.dry_run(
                    {"path": "src/app.txt", "start_line": start, "line": end},
                )
                self.assertEqual(inline, {("src/app.txt", None, end, "RIGHT")})
                self.assertEqual(moved, set())
                self.assertEqual(body, "Summary")
                self.assertEqual(self.payload["comments"], [{
                    "path": "src/app.txt", "line": end, "side": "RIGHT",
                    "body": f"note 0\n\nApplies to lines {start}-{end} (RIGHT).",
                }])

    def test_range_text_preserves_sides(self):
        """Given left-side and mixed-side ranges, when submitted, then each anchors its ending side and preserves both endpoint sides in its text."""
        inline, moved, body = self.dry_run(
            {"path": "src/app.txt", "start_line": 1, "line": 2, "side": "LEFT"},
            {"path": "src/app.txt", "start_line": 2, "start_side": "LEFT", "line": 4, "side": "RIGHT"},
        )
        self.assertEqual(inline, {("src/app.txt", None, 2, "LEFT"), ("src/app.txt", None, 4, "RIGHT")})
        self.assertEqual(moved, set())
        self.assertEqual(body, "Summary")
        self.assertEqual([c["body"] for c in self.payload["comments"]], [
            "note 0\n\nApplies to lines 1-2 (LEFT).",
            "note 1\n\nApplies to lines 2 (LEFT) to 4 (RIGHT).",
        ])

    def test_invalid_range_end_moves_the_finding_and_location_to_the_body(self):
        """Given a mixed-side range ending outside the diff, when submitted, then its text, path, endpoints and sides appear once in the review body."""
        inline, moved, body = self.dry_run(
            {"path": "src/app.txt", "start_line": 2, "start_side": "LEFT", "line": 10, "side": "RIGHT"},
            {"path": "src/app.txt", "line": 3, "body": "valid single line"},
        )
        self.assertEqual(inline, {("src/app.txt", None, 3, "RIGHT")})
        self.assertEqual(moved, {"src/app.txt:2 (LEFT) to 10 (RIGHT)"})
        self.assertEqual(body, "Summary\n\n### Findings outside the diff\n- `src/app.txt:2 (LEFT) to 10 (RIGHT)` note 0")
        self.assertEqual(self.payload["comments"], [{
            "path": "src/app.txt", "line": 3, "side": "RIGHT", "body": "valid single line",
        }])

    def test_files_without_a_patch_or_outside_the_pr_move_to_the_body(self):
        """Given comments on a binary file and on a file the PR does not change, when submitted, then both move to the body with their text."""
        inline, moved, body = self.dry_run(
            {"path": "img.png", "line": 1, "side": "RIGHT"},
            {"path": "other.txt", "line": 1, "side": "RIGHT"},
        )
        self.assertEqual(inline, set())
        self.assertEqual(moved, {"img.png:1", "other.txt:1"})
        self.assertIn("Summary", body)
        self.assertIn("`img.png:1` note 0", body)
        self.assertIn("`other.txt:1` note 1", body)


class SubmitReviewOutcomes(unittest.TestCase):
    def setUp(self):
        self.sandbox = Sandbox()
        self.addCleanup(self.sandbox.close)

    def submit(self, author, reviews=(), post=None):
        accepted = {"id": 7, "html_url": f"{PR_URL}#r7", "state": "COMMENTED", "commit_id": HEAD}
        self.sandbox.set_gh({
            "pr": {"number": 1, "url": PR_URL, "state": "OPEN", "headRefOid": HEAD,
                   "author": {"login": author}},
            "viewer": "reviewer",
            f"{PULL}/reviews": list(reviews),
            f"{PULL}/files": [{"filename": "src/app.txt", "patch": PATCH}],
            "post": post or {"stdout": json.dumps(accepted)},
        })
        review = self.sandbox.root / "review.json"
        review.write_text(json.dumps({
            "commit_id": HEAD, "event": "REQUEST_CHANGES", "body": "Summary",
            "comments": [{"path": "src/app.txt", "line": 3, "side": "RIGHT", "body": "F1"}],
        }))
        return self.sandbox.node("submit-review.mjs", "1", "--in", str(review))

    def posted(self):
        return [json.loads(call["stdin"]) for call in self.sandbox.gh_calls() if "POST" in call["args"]]

    def test_own_pr_request_changes_posts_a_comment_review(self):
        """Given the viewer authored the PR, when Request changes is submitted, then one Comment review is posted with the inline comment intact."""
        result = self.submit(author="reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)
        [payload] = self.posted()
        self.assertEqual(payload["event"], "COMMENT")
        self.assertEqual(payload["comments"], [{"path": "src/app.txt", "body": "F1", "line": 3, "side": "RIGHT"}])

    def test_other_authors_pr_keeps_request_changes(self):
        """Given someone else authored the PR, when Request changes is submitted, then the posted review requests changes."""
        result = self.submit(author="someone")
        self.assertEqual(result.returncode, 0, result.stderr)
        [payload] = self.posted()
        self.assertEqual(payload["event"], "REQUEST_CHANGES")

    def test_fallback_review_is_not_duplicated(self):
        """Given the viewer authored the PR and already left a Comment review on the head, when Request changes is submitted, then it exits 4 without posting."""
        existing = {"user": {"login": "reviewer"}, "state": "COMMENTED", "commit_id": HEAD,
                    "html_url": f"{PR_URL}#r6"}
        result = self.submit(author="reviewer", reviews=[existing])
        self.assertEqual(result.returncode, 4)
        self.assertEqual(self.posted(), [])

    def test_rejection_reports_githubs_reason(self):
        """Given GitHub rejects the review with a 422 and a reason, when submitted, then it exits 1 and stderr carries both the status and the reason."""
        rejection = {
            "stdout": json.dumps({"message": "Unprocessable Entity",
                                  "errors": ["Review Can not request changes on your own pull request"]}),
            "stderr": "gh: Unprocessable Entity (HTTP 422)\n",
            "exit": 1,
        }
        result = self.submit(author="someone", post=rejection)
        self.assertEqual(result.returncode, 1)
        self.assertIn("HTTP 422", result.stderr)
        self.assertIn("Review Can not request changes on your own pull request", result.stderr)


    def test_object_shaped_rejection_reports_its_fields(self):
        """Given GitHub rejects the review with an error object that has no message, when submitted, then stderr names the object's field and code."""
        rejection = {
            "stdout": json.dumps({"message": "Validation Failed",
                                  "errors": [{"resource": "PullRequestReview", "field": "body",
                                              "code": "missing_field"}]}),
            "stderr": "gh: Validation Failed (HTTP 422)\n",
            "exit": 1,
        }
        result = self.submit(author="someone", post=rejection)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("[object Object]", result.stderr)
        self.assertIn('"field":"body"', result.stderr)
        self.assertIn('"code":"missing_field"', result.stderr)

if __name__ == "__main__":
    unittest.main()
