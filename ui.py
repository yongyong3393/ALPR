import cv2

class UIManager:
    def __init__(self, window_name: str ="Webcam"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name)

    def show(self, frame, ocr_text: str | None = None):
        # Overlay text on the frame
        if ocr_text:
            cv2.putText(frame, ocr_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow(self.window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        return key

    def destroy(self):
        cv2.destroyAllWindows()