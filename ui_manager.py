import cv2

class UIManager:
    def __init__(self, window_name: str = "Webcam"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name)

    def show(self, frame, box = None, ocr_text: str | None = None):
        # Overlay text on the frame
        if box:
            x1, y1, x2, y2 = box["bbox"]
            conf = box["conf"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
    
        if ocr_text:
            cv2.putText(frame, ocr_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 255, 0), 2, cv2.LINE_AA)
        
        cv2.imshow(self.window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        return key

    def destroy(self):
        cv2.destroyAllWindows()