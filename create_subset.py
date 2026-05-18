#!/usr/bin/env python3
"""
Create a smaller YOLO dataset subset by random sampling train and val separately.

Default source paths:
  D:\datasets\anti-uav\dataset\images\train
  D:\datasets\anti-uav\dataset\labels\train
  D:\datasets\anti-uav\dataset\images\val
  D:\datasets\anti-uav\dataset\labels\val

Output structure:
  subset/images/train
  subset/labels/train
  subset/images/val
  subset/labels/val

This is intentionally simple: no clustering, no active learning, no duplicate detection.
"""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}
FRAME_STEP = 10


def sample_and_copy(image_dir: Path, label_dir: Path, out_image_dir: Path, out_label_dir: Path, count: int, seed: int) -> int:
    out_image_dir.mkdir(parents=True, exist_ok=True)
    out_label_dir.mkdir(parents=True, exist_ok=True)

    images = sorted([p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS])
    if not images:
        return 0

    selected = images[::FRAME_STEP]
    selected = selected[: min(count, len(selected))]


    copied = 0
    for img_path in selected:
        label_path = label_dir / f"{img_path.stem}.txt"
        if not label_path.exists():
            continue

        shutil.copy2(img_path, out_image_dir / img_path.name)
        shutil.copy2(label_path, out_label_dir / label_path.name)
        copied += 1

    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description="Create YOLO subset using frame skipping.")
    parser.add_argument("--train-images", default=r"D:\datasets\anti-uav\dataset\images\train")
    parser.add_argument("--train-labels", default=r"D:\datasets\anti-uav\dataset\labels\train")
    parser.add_argument("--val-images", default=r"D:\datasets\anti-uav\dataset\images\val")
    parser.add_argument("--val-labels", default=r"D:\datasets\anti-uav\dataset\labels\val")
    parser.add_argument("--out", default="subset")
    parser.add_argument("--train-count", type=int, default=34000)
    parser.add_argument("--val-count", type=int, default=6000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out_root = Path(args.out)
    train_copied = sample_and_copy(
        Path(args.train_images),
        Path(args.train_labels),
        out_root / "images" / "train",
        out_root / "labels" / "train",
        args.train_count,
        args.seed,
    )
    val_copied = sample_and_copy(
        Path(args.val_images),
        Path(args.val_labels),
        out_root / "images" / "val",
        out_root / "labels" / "val",
        args.val_count,
        args.seed + 1,
    )

    print(f"Train copied: {train_copied}")
    print(f"Val copied: {val_copied}")
    print(f"Subset created at: {out_root.resolve()}")


if __name__ == "__main__":
    main()