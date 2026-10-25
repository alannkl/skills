from pathlib import Path

from datasets import load_from_disk


def load_reviews(data_dir: Path, max_len: int):
    ds = load_from_disk(str(data_dir))
    return ds["train"], ds["validation"]
