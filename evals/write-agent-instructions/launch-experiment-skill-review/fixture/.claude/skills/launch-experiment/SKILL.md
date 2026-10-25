---
name: launch-experiment
description: Launch a training run
---

# Launch experiment

1. Make sure the working tree is clean (`git status`) so the run is reproducible. Commit first if it isn't.
2. Copy the closest config from `configs/` to `configs/exp/<name>.yaml` and change only the fields the user asked for.
3. Start the run:

       python scripts/train.py --config configs/exp/<name>.yaml --data /home/priya/datasets/reviews-v3 --wandb-project priya-scratch

4. Paste the W&B run URL back to the user.
5. Use GPU 0 only (`CUDA_VISIBLE_DEVICES=0`); the other GPUs are reserved for eval jobs.
