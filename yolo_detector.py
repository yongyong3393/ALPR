import torch
from ultralytics import YOLO

def load_yolo(weight_path: str):
    use_gpu = torch.cuda.is_available()
    print(f"[INFO] GPU 사용 여부: {use_gpu}")

    model = YOLO(weight_path)
    print("model.names =", model.names)

    if use_gpu:
        model.to("cuda")

    return model

def detect(model, frame):
    # TODO: 
    results = model(frame)
    return results