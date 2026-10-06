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

    def test_ranges_need_both_ends_in_the_diff(self):
        """Given a range inside hunk 1 and a range starting between hunks, when submitted, then the first stays inline and the second moves to the body."""
        inline, moved, _ = self.dry_run(
            {"path": "src/app.txt", "start_line": 1, "line": 4, "side": "RIGHT"},
            {"path": "src/app.txt", "start_line": 10, "line": 22, "side": "RIGHT"},
        )
        self.assertEqual(inline, {("src/app.txt", 1, 4, "RIGHT")})
        self.assertEqual(moved, {"src/app.txt:10-22"})

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


if __name__ == "__main__":
    unittest.main()
