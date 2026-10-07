"""Review helpers route every API request to the supported github.com service."""
import json
import unittest

from fixtures import PR_URL, REPO, Sandbox

HEAD = "a" * 40
PULL = f"repos/{REPO}/pulls/1"
PR = {"number": 1, "url": PR_URL, "state": "OPEN", "headRefOid": HEAD}


def connection(nodes, cursor=None):
    return {"nodes": nodes, "pageInfo": {"hasNextPage": cursor is not None, "endCursor": cursor}}


class ApiHost(unittest.TestCase):
    def test_read_pr_collects_rest_and_graphql_from_github_com(self):
        """Given a github.com PR and unset or overridden GH_HOST, when read, then viewer, REST pages, GraphQL threads and replies come from github.com with complete coverage."""
        for host in [None, "127.0.0.1:9"]:
            with self.subTest(host=host):
                sandbox = Sandbox()
                self.addCleanup(sandbox.close)
                sandbox.env.pop("GH_HOST", None)
                if host:
                    sandbox.env["GH_HOST"] = host
                sandbox.set_gh({
                    "pr": PR, "viewer": "reviewer",
                    f"repos/{REPO}/issues/1/comments?per_page=100&page=1": [
                        {"id": i, "body": f"discussion {i}"} for i in range(100)
                    ],
                    f"repos/{REPO}/issues/1/comments?per_page=100&page=2": [{"id": 100}],
                    f"{PULL}/reviews": [{"id": 7, "body": "review"}],
                    "graphql": [
                        {"data": {"repository": {"pullRequest": {"reviewThreads": connection([
                            {"id": "thread", "comments": connection([{"id": "first"}], "reply-cursor")},
                        ], "thread-cursor")}}}},
                        {"data": {"node": {"comments": connection([{"id": "reply"}])}}},
                        {"data": {"repository": {"pullRequest": {"reviewThreads": connection([
                            {"id": "second-thread", "comments": connection([{"id": "second"}])},
                        ])}}}},
                    ],
                })
                output = sandbox.root / "read.json"
                result = sandbox.node("read-pr.mjs", PR_URL, "--out", str(output))
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(output.read_text())
                self.assertEqual(data["viewer"], "reviewer")
                self.assertEqual(data["failures"], [])
                self.assertEqual([c["id"] for c in data["discussion"]["items"]], list(range(101)))
                self.assertEqual(data["discussion"]["pages"], 2)
                self.assertEqual([r["id"] for r in data["reviews"]["items"]], [7])
                self.assertEqual(data["threads"]["pages"], 3)
                self.assertEqual([[c["id"] for c in t["comments"]] for t in data["threads"]["items"]], [["first", "reply"], ["second"]])
                self.assertFalse(any("--method" in c["args"] for c in sandbox.gh_calls()))

    def test_submit_review_reads_and_posts_to_github_com(self):
        """Given a github.com PR and unset or overridden GH_HOST, when submitted, then viewer, review and diff lookups and the single review POST all use github.com."""
        for host in [None, "127.0.0.1:9"]:
            with self.subTest(host=host):
                sandbox = Sandbox()
                self.addCleanup(sandbox.close)
                sandbox.env.pop("GH_HOST", None)
                if host:
                    sandbox.env["GH_HOST"] = host
                sandbox.set_gh({
                    "pr": PR, "viewer": "reviewer", f"{PULL}/reviews": [],
                    f"{PULL}/files": [{"filename": "a.txt", "patch": "@@ -1 +1 @@\n-old\n+new"}],
                    "post": {"stdout": json.dumps({"id": 7, "state": "CHANGES_REQUESTED", "html_url": f"{PR_URL}#r7", "commit_id": HEAD})},
                })
                review = sandbox.root / "review.json"
                review.write_text(json.dumps({
                    "commit_id": HEAD, "event": "REQUEST_CHANGES", "body": "Summary",
                    "comments": [{"path": "a.txt", "body": "F1", "start_line": 1, "line": 1}],
                }))
                result = sandbox.node("submit-review.mjs", PR_URL, "--in", str(review))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["url"], f"{PR_URL}#r7")
                [posted] = [json.loads(c["stdin"]) for c in sandbox.gh_calls() if "POST" in c["args"]]
                self.assertEqual(posted, {
                    "commit_id": HEAD, "event": "REQUEST_CHANGES", "body": "Summary",
                    "comments": [{"path": "a.txt", "body": "F1\n\nApplies to lines 1-1 (RIGHT).", "line": 1, "side": "RIGHT"}],
                })
