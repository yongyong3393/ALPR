import cv2

class VideoStream:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)

    def is_opened(self) -> bool:
        return self.cap.isOpened()

    def read(self):
        """return (ok, frame)"""
        return self.cap.read()

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
