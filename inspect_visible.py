from pathlib import Path
import json

ROOT = Path("Anti-UAV-RGBT")
splits = ["train", "val", "test"]

image_exts = [".jpg", ".jpeg", ".png", ".bmp"]

grand_total = 0

for split in splits:
    split_path = ROOT / split

    if not split_path.exists():
        print(f"{split} not found")
        continue

    print("=" * 60)
    print(f"Inspecting {split.upper()}")
    print("=" * 60)

    split_total = 0
    sequence_count = 0

    for seq_path in sorted(split_path.iterdir()):
        if not seq_path.is_dir():
            continue

        visible_path = seq_path / "visible"
        json_path = seq_path / "visible.json"

        if not visible_path.exists():
            print(f"❌ {seq_path.name}: no visible folder")
            continue

        images = []
        for ext in image_exts:
            images.extend(list(visible_path.glob(f"*{ext}")))

        images = sorted(images)
        image_count = len(images)

        exist_count = "N/A"
        gt_count = "N/A"

        if json_path.exists():
            with open(json_path, "r") as f:
                data = json.load(f)

            exist = data.get("exist", [])
            gt_rect = data.get("gt_rect", [])

            exist_count = sum(1 for x in exist if x == 1)
            gt_count = len(gt_rect)

        print(
            f"{seq_path.name} | "
            f"images: {image_count} | "
            f"exist=1: {exist_count} | "
            f"gt_rect: {gt_count}"
        )

        split_total += image_count
        sequence_count += 1

    print()
    print(f"{split.upper()} sequences: {sequence_count}")
    print(f"{split.upper()} total visible images: {split_total}")
    print()

    grand_total += split_total

print("=" * 60)
print(f"ALL visible images total: {grand_total}")
print("=" * 60)