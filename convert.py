import os
import cv2
import json
import shutil

DATASET_PATH = "Anti-UAV-RGBT"
OUTPUT_PATH = "dataset"

splits = ["train", "val", "test"]
for split in splits:
    os.makedirs(os.path.join(OUTPUT_PATH, f"images/{split}"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_PATH, f"labels/{split}"), exist_ok=True)


def process_split(split_name):
    split_folder = os.path.join(DATASET_PATH, split_name)
    img_out = os.path.join(OUTPUT_PATH, f"images/{split_name}")
    lbl_out = os.path.join(OUTPUT_PATH, f"labels/{split_name}")

    if not os.path.exists(split_folder):
        print(f"Skipping {split_name}: folder not found")
        return 0

    count = 0

    for seq in sorted(os.listdir(split_folder)):
        seq_path = os.path.join(split_folder, seq)
        if not os.path.isdir(seq_path):
            continue

        visible_dir = os.path.join(seq_path, "visible")
        json_path = os.path.join(seq_path, "visible.json")

        if not os.path.exists(visible_dir) or not os.path.exists(json_path):
            print(f"  Skipping {seq}: missing visible/ or visible.json")
            continue

        with open(json_path, "r") as f:
            data = json.load(f)

        gt_rect = data.get("gt_rect", [])
        exist = data.get("exist", [])

        if not gt_rect or not exist:
            print(f"  Skipping {seq}: empty annotations")
            continue

        images = sorted([
            f for f in os.listdir(visible_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
        ])

        seq_count = 0

        for frame_id, img_file in enumerate(images):
            if frame_id >= len(gt_rect):
                break

            if exist[frame_id] != 1:
                continue

            src = os.path.join(visible_dir, img_file)
            img = cv2.imread(src)
            if img is None:
                continue

            H, W = img.shape[:2]
            x, y, w, h = gt_rect[frame_id]

            x_center = (x + w / 2) / W
            y_center = (y + h / 2) / H
            w_norm   = w / W
            h_norm   = h / H

            out_name = f"{seq}_{frame_id:04d}"
            shutil.copy2(src, os.path.join(img_out, out_name + ".jpg"))

            with open(os.path.join(lbl_out, out_name + ".txt"), "w") as f:
                f.write(f"0 {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n")

            seq_count += 1
            count += 1

        if seq_count > 0:
            print(f"  {seq}: {seq_count} frames")

    return count


print("Converting Anti-UAV-RGBT to YOLO format...\n")

total = 0
for split in splits:
    print(f"[{split.upper()}]")
    n = process_split(split)
    print(f"  => {n} images\n")
    total += n

data_yaml = f"""path: {os.path.abspath(OUTPUT_PATH)}
train: images/train
val: images/val
test: images/test

nc: 1
names: ['drone']
"""

with open(os.path.join(OUTPUT_PATH, "data.yaml"), "w") as f:
    f.write(data_yaml)

print(f"Done. Total images: {total}")
print(f"data.yaml saved to: {os.path.abspath(OUTPUT_PATH)}")
