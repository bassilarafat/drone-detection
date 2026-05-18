from ultralytics import YOLO

def main():

    model = YOLO("yolo11s.pt")

    model.train(
        data="dataset/data.yaml",
        epochs=30,
        imgsz=640,
        batch=16,
        device=0,
        workers=0,
        cache=True,
        project="runs",
        name="anti_uav_yolo11s",
        exist_ok=True,

        # small object settings
        mosaic=1.0,
        close_mosaic=5,
        scale=0.5,
        fliplr=0.5,
        flipud=0.0,
        degrees=0.0
    )

if __name__ == "__main__":
    main()