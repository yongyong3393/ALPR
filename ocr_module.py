import threading
import queue
from paddleocr import PaddleOCR

class OCRWorker:
    """
    main methods:
    - submit_frame()
    - get_latest_text()
    """

    def __init__(self, lang: str = "korean", device: str = "cpu", queue_size: int = 1):
        self.ocr = PaddleOCR(lang=lang, device=device)
        self.q = queue.Queue(maxsize=queue_size)
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
    
    def submit_frame(self, frame):
        if not self._running:
            return
        if self.q.full():
            self.q.get()
        self.q.put(frame)

    def get_latest_text(self):
        return self.latest_text

    def _worker_loop(self):
        while self._running:
            try:
                frame_for_ocr = self.q.get(timeout=0.1)
            except queue.Empty:
                continue

            result = self.ocr.predict(input=frame_for_ocr)
            if not result:
                self.latest_text = None
                continue
            rec_texts = result[0].get("rec_texts", [])
            if rec_texts:
                # TODO: 문자열 처리 로직 수정. 현재는 여러 줄이면 이어 붙이는 로직만 추가
                self.latest_text = "".join(rec_texts)
            else:
                self.latest_text = None