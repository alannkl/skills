"""Publish release notes to the CDN. Requires headings: ## Release <v>, ### Added, ### Fixed, ### Breaking (in order)."""
import re
import sys
import urllib.request

CDN = "https://cdn.example.com/releases"
REQUIRED = ["### Added", "### Fixed", "### Breaking"]


def check(text):
    match = re.match(r"## Release (\S+)", text)
    if not match:
        sys.exit("missing release heading")
    positions = [text.find(h) for h in REQUIRED]
    if -1 in positions or positions != sorted(positions):
        sys.exit("headings missing or out of order")
    return match.group(1)


def publish(path):
    text = open(path).read()
    version = check(text)
    request = urllib.request.Request(f"{CDN}/{version}.md", data=text.encode(), method="PUT",
                                     headers={"Content-Type": "text/markdown"})
    with urllib.request.urlopen(request) as response:
        print(f"published {version}: HTTP {response.status}")


if __name__ == "__main__":
    publish(sys.argv[1])
