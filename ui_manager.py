import cv2
from PySide6 import QtCore, QtGui, QtWidgets

class UIManager(QtWidgets.QMainWindow):
    closed = QtCore.Signal()

    def __init__(self, window_name: str = "Webcam"):
        super().__init__()
        self.setWindowTitle(window_name)
        self.image_label = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.image_label)
        self.resize(960, 540)

    def show_frame(self, frame, box=None, ocr_text: str | None = None):
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

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        self.image_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
