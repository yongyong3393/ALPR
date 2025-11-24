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

def detect(model, frame, conf_thres: float = 0.5):
    """
    frame에서 번호판 bbox를 검출해서 list로 return.
    각 원소는 {"bbox": (x1, y1, x2, y2), "conf": float, "cls": int} 형식.
    """
    result = model(frame)[0]
    if result.boxes is None:
        return []
    
    detections = []
    for box in result.boxes:
        conf = float(box.conf)
        if conf < conf_thres:
            continue

        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        cls_id = int(box.cls[0])
        if cls_id != 0:
            continue  # 번호판 클래스가 아닌 경우 무시

        detections.append({
            "bbox": (x1, y1, x2, y2),
            "conf": conf,
            "cls": cls_id
        })
    return detections