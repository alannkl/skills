"""Fine-tune a sentiment classifier on product reviews."""
import argparse
import os
from pathlib import Path

import torch
import wandb
import yaml

from src.data import load_reviews
from src.model import build_model


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--data-dir", type=Path, default=Path(os.environ.get("DATA_ROOT", "/data")) / "reviews-v3")
    p.add_argument("--wandb-project", default="reviews-sentiment")
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = yaml.safe_load(args.config.read_text())
    torch.manual_seed(args.seed)
    run = wandb.init(project=args.wandb_project, config=cfg)
    print(f"wandb run: {run.url}", flush=True)
    train_ds, val_ds = load_reviews(args.data_dir, cfg["max_len"])
    model = build_model(cfg).cuda()
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"])
    for epoch in range(cfg["epochs"]):
        model.train()
        for batch in torch.utils.data.DataLoader(train_ds, batch_size=cfg["batch_size"], shuffle=True):
            loss = model(**{k: v.cuda() for k, v in batch.items()}).loss
            loss.backward()
            opt.step()
            opt.zero_grad()
        wandb.log({"epoch": epoch, "loss": loss.item()})


if __name__ == "__main__":
    main()
