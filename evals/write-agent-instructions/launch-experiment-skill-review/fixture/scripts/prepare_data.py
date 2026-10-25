"""Tokenise raw reviews into $DATA_ROOT/reviews-v3 (run once per dataset version)."""
import os
import sys

if __name__ == "__main__":
    root = os.environ["DATA_ROOT"]
    print(f"would write to {root}/reviews-v3", file=sys.stderr)
