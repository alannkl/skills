"""Publish release notes. Requires headings: ## Release <v>, ### Added, ### Fixed, ### Breaking (in order)."""
import re, sys
REQUIRED = ["### Added", "### Fixed", "### Breaking"]
def check(text):
    if not re.match(r"## Release \S+", text):
        sys.exit("missing release heading")
    positions = [text.find(h) for h in REQUIRED]
    if -1 in positions or positions != sorted(positions):
        sys.exit("headings missing or out of order")
if __name__ == "__main__":
    check(open(sys.argv[1]).read())
