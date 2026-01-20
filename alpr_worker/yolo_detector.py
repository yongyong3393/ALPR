import torch
from ultralytics import YOLO

class YoloDetector:
    def __init__(self):
        self.load_model()

    def load_model(self):
        use_gpu = torch.cuda.is_available()
        print(f"[INFO] GPU 사용 여부: {use_gpu}")
        self.model = YOLO("./yolo_weight/best.pt")
        print("model.names =", self.model.names)

        if use_gpu:
            self.model.to("cuda")

    def detect(self, frame, conf_thres: float = 0.7):
        """
        frame에서 번호판 bbox를 검출해서 list로 return.
        각 원소는 {"bbox": (x1, y1, x2, y2), "conf": float, "cls": int} 형식.
        """
        result = self.model(frame)[0]
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