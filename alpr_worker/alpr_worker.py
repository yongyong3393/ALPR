import threading
import queue

from .yolo_detector import YoloDetector
from .ocr import OCR

class ALPRWorker:
    """
    ALPR Worker combining YOLO detection and OCR.
    Interface
    - submit_frame()
    - get_latest_result()

    """

    def __init__(self):
        self.yolo_detector = YoloDetector()
        self.ocr = OCR()
        self.q = queue.Queue(maxsize=1)

        # state
        self.latest_box = None
        self.latest_text = None
        
        self._running = False
        self._thread = None
    
    def start(self):
        if self._thread is not None:
            return
        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
    
    def submit_frame(self, frame, roi=None):
        if not self._running:
            return
        payload = (frame, roi)
        try:
            self.q.put_nowait(payload)
        except queue.Full:
            try:
                self.q.get_nowait()
            except queue.Empty:
                pass
            self.q.put_nowait(payload)
    
    def get_latest_result(self):
        return self.latest_box, self.latest_text
    
    def _worker_loop(self):
        while self._running:
            try:
                payload = self.q.get(timeout=0.1)
            except queue.Empty:
                continue
            
            # 1. YOLO detection
            frame, roi = payload
            x1, y1, x2, y2 = roi
            roi_frame = frame[y1:y2 + 1, x1:x2 + 1]
            boxes = self.yolo_detector.detect(roi_frame)
            if boxes:
                boxes = [
                    {
                        **box,
                        "bbox": (
                            box["bbox"][0] + x1,
                            box["bbox"][1] + y1,
                            box["bbox"][2] + x1,
                            box["bbox"][3] + y1,
                        ),
                    }
                    for box in boxes
                ]
            if not boxes:
                self.latest_box = None
                self.latest_text = None
                continue

            # 2. Get the biggest box and crop
            best_box = max(boxes, key=lambda d: (d["bbox"][2]-d["bbox"][0]) * (d["bbox"][3]-d["bbox"][1]))
            x1, y1, x2, y2 = best_box["bbox"]
            plate_crop = frame[y1:y2, x1:x2]

            # 3. OCR
            result = self.ocr.detect(plate_crop)

            # 4. Update state
            self.latest_box, self.latest_text = best_box, result if result else None
