from ultralytics import YOLO

model = YOLO("runs/drone_yolo11n/weights/best.pt")

results = model.predict(
    source="test.jpg",
    imgsz=640,
    conf=0.25,
    save=True
)

print("Prediction done!")