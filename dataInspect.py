import os
import cv2
import numpy as np
from tqdm import tqdm

IMAGE_DIR = r"D:\datasets\anti-uav\dataset\images\train"
LABEL_DIR = r"D:\datasets\anti-uav\dataset\labels\train"

missing_labels = 0
empty_labels = 0
bad_images = 0
bad_boxes = 0
total_boxes = 0

box_widths = []
box_heights = []

images = os.listdir(IMAGE_DIR)

for img_name in tqdm(images):

    img_path = os.path.join(IMAGE_DIR, img_name)

    # corresponding label
    label_name = os.path.splitext(img_name)[0] + ".txt"
    label_path = os.path.join(LABEL_DIR, label_name)

    # -------------------------
    # check image
    # -------------------------
    img = cv2.imread(img_path)

    if img is None:
        bad_images += 1
        continue

    h, w = img.shape[:2]

    # -------------------------
    # check label existence
    # -------------------------
    if not os.path.exists(label_path):
        missing_labels += 1
        continue

    # -------------------------
    # check empty label
    # -------------------------
    with open(label_path, "r") as f:
        lines = f.readlines()

    if len(lines) == 0:
        empty_labels += 1
        continue

    # -------------------------
    # validate boxes
    # -------------------------
    for line in lines:

        parts = line.strip().split()

        if len(parts) != 5:
            bad_boxes += 1
            continue

        cls, xc, yc, bw, bh = map(float, parts)

        total_boxes += 1

        # YOLO values must be 0-1
        if not (0 <= xc <= 1 and
                0 <= yc <= 1 and
                0 <= bw <= 1 and
                0 <= bh <= 1):
            bad_boxes += 1

        box_widths.append(bw * w)
        box_heights.append(bh * h)

# -------------------------
# final report
# -------------------------
print("\n========== DATASET REPORT ==========")

print(f"Total Images      : {len(images)}")
print(f"Bad Images        : {bad_images}")
print(f"Missing Labels    : {missing_labels}")
print(f"Empty Labels      : {empty_labels}")
print(f"Bad Boxes         : {bad_boxes}")
print(f"Total Boxes       : {total_boxes}")

if len(box_widths) > 0:
    print("\n===== BBOX STATS =====")
    print(f"Avg Box Width  : {np.mean(box_widths):.2f}px")
    print(f"Avg Box Height : {np.mean(box_heights):.2f}px")
    print(f"Min Width      : {np.min(box_widths):.2f}px")
    print(f"Min Height     : {np.min(box_heights):.2f}px")

