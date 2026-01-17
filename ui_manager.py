import cv2
from PySide6 import QtCore, QtGui, QtWidgets

class UIManager(QtWidgets.QMainWindow):
    closed = QtCore.Signal()

    def __init__(self, window_name: str = "Webcam"):
        super().__init__()
        self.setWindowTitle(window_name)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        grid = QtWidgets.QGridLayout(central)
        grid.setContentsMargins(12, 12, 12, 12)
        grid.setSpacing(12)

        # (1) Top-left: recognized plate text
        self.plate_label = QtWidgets.QLabel("No plate detected")
        self.plate_label.setAlignment(QtCore.Qt.AlignCenter)
        self.plate_label.setStyleSheet("font-size: 28px; font-weight: 600;")

        # (2) Top-right: live stream
        self.image_label = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #111;")

        # Bottom placeholders
        self.placeholder_left = QtWidgets.QLabel()
        self.placeholder_left.setStyleSheet("background-color: #3a3a3a;")
        self.placeholder_right = QtWidgets.QLabel()
        self.placeholder_right.setStyleSheet("background-color: #3a3a3a;")

        grid.addWidget(self.plate_label, 0, 0)
        grid.addWidget(self.image_label, 0, 1)
        grid.addWidget(self.placeholder_left, 1, 0)
        grid.addWidget(self.placeholder_right, 1, 1)

        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self.resize(1600, 900)

    def show_frame(self, frame, box=None, ocr_text: str | None = None):
        # Overlay text on the frame
        if box:
            x1, y1, x2, y2 = box["bbox"]
            conf = box["conf"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

        if ocr_text:
            self.plate_label.setText(ocr_text)
        else:
            self.plate_label.setText("No plate detected")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        self.image_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
