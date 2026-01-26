import cv2


class BaseStream:
    def is_opened(self) -> bool:
        raise NotImplementedError

    def read(self):
        """return (ok, frame)"""
        raise NotImplementedError

    def release(self):
        raise NotImplementedError


class VideoCaptureStream(BaseStream):
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)

    def is_opened(self) -> bool:
        return self.cap.isOpened()

    def read(self):
        return self.cap.read()

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class WebcamStream(VideoCaptureStream):
    def __init__(self, src=0):
        super().__init__(src)


class RTSPStream(VideoCaptureStream):
    def __init__(self, url: str):
        super().__init__(url)


class ImageStream(BaseStream):
    def __init__(self, path: str):
        self.path = path
        self.image = cv2.imread(path)

    def is_opened(self) -> bool:
        return self.image is not None

    def read(self):
        if self.image is None:
            return False, None
        return True, self.image.copy()

    def release(self):
        self.image = None


VideoStream = WebcamStream
