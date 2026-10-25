# reviews-sentiment

Sentiment classifier for product reviews.

## Data

Datasets live on the shared volume at `$DATA_ROOT` (set in everyone's shell profile on the GPU box). Current version: `reviews-v3`. Build a new version with `python scripts/prepare_data.py`.

## Training

    python -m src.train --config configs/base.yaml

Runs log to the shared W&B project `reviews-sentiment`.

The GPU box has 4 GPUs; GPU 0 is for training, 1-3 run the nightly eval jobs.
