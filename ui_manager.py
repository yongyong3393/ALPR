import cv2
from PySide6 import QtCore, QtGui, QtWidgets

class VideoLabel(QtWidgets.QLabel):
    roi_finalized = QtCore.Signal(tuple)

    def __init__(self):
        super().__init__(alignment=QtCore.Qt.AlignCenter)
        self.setStyleSheet("background-color: #111;")
        self._roi_set_mode = False
        self._roi_dragging = False
        self._roi_start = None
        self._roi_end = None
        self._roi_rect = None
        self._roi_preview = None
        self._image_size = None
        self._display_rect = None
        self._scale = None

    def set_roi_mode(self, enabled: bool):
        self._roi_set_mode = enabled
        self._roi_dragging = False
        self._roi_preview = None
        if enabled:
            self.setCursor(QtCore.Qt.CrossCursor)
        else:
            self.unsetCursor()

    def get_roi_rect(self):
        return self._roi_rect

    def set_frame(self, image: QtGui.QImage):
        img_w = image.width()
        img_h = image.height()
        label_w = self.width()
        label_h = self.height()

        if img_w <= 0 or img_h <= 0 or label_w <= 0 or label_h <= 0:
            self.setPixmap(QtGui.QPixmap.fromImage(image))
            return

        self._image_size = (img_w, img_h)
        scale = min(label_w / img_w, label_h / img_h)
        scaled_w = max(1, int(img_w * scale))
        scaled_h = max(1, int(img_h * scale))

        pixmap = QtGui.QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(
            scaled_w,
            scaled_h,
            QtCore.Qt.IgnoreAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )

        self._scale = scale
        offset_x = (label_w - scaled_w) // 2
        offset_y = (label_h - scaled_h) // 2
        self._display_rect = QtCore.QRect(offset_x, offset_y, scaled_w, scaled_h)

        roi = self._roi_preview if self._roi_dragging else self._roi_rect
        if roi:
            dx1, dy1, dx2, dy2 = self._image_rect_to_label_rect(roi)
            painter = QtGui.QPainter(scaled_pixmap)
            pen = QtGui.QPen(QtGui.QColor(255, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(dx1, dy1, dx2 - dx1, dy2 - dy1)
            painter.end()

        self.setPixmap(scaled_pixmap)

    def mousePressEvent(self, event):
        if not self._roi_set_mode or event.button() != QtCore.Qt.LeftButton:
            return super().mousePressEvent(event)

        pos = self._label_pos_to_image_pos(event.position().toPoint())
        if pos is None:
            return

        self._roi_dragging = True
        self._roi_start = pos
        self._roi_end = pos
        self._roi_preview = self._normalize_roi(self._roi_start, self._roi_end)

    def mouseMoveEvent(self, event):
        if not self._roi_dragging:
            return super().mouseMoveEvent(event)

        pos = self._label_pos_to_image_pos(event.position().toPoint())
        if pos is None:
            return

        self._roi_end = pos
        self._roi_preview = self._normalize_roi(self._roi_start, self._roi_end)

    def mouseReleaseEvent(self, event):
        if not self._roi_dragging or event.button() != QtCore.Qt.LeftButton:
            return super().mouseReleaseEvent(event)

        pos = self._label_pos_to_image_pos(event.position().toPoint())
        if pos is not None:
            self._roi_end = pos

        roi = self._normalize_roi(self._roi_start, self._roi_end)
        if roi and (roi[2] - roi[0] >= 2) and (roi[3] - roi[1] >= 2):
            self._roi_rect = roi
            self.roi_finalized.emit(roi)

        self._roi_preview = None
        self._roi_dragging = False

    def _label_pos_to_image_pos(self, pos: QtCore.QPoint):
        if self._display_rect is None or self._scale is None or self._image_size is None:
            return None
        if not self._display_rect.contains(pos):
            return None

        img_w, img_h = self._image_size
        x = pos.x() - self._display_rect.x()
        y = pos.y() - self._display_rect.y()
        img_x = int(x / self._scale)
        img_y = int(y / self._scale)
        img_x = max(0, min(img_x, img_w - 1))
        img_y = max(0, min(img_y, img_h - 1))
        return (img_x, img_y)

    def _image_rect_to_label_rect(self, roi):
        if self._scale is None:
            return (0, 0, 0, 0)
        x1, y1, x2, y2 = roi
        dx1 = int(x1 * self._scale)
        dy1 = int(y1 * self._scale)
        dx2 = int(x2 * self._scale)
        dy2 = int(y2 * self._scale)
        return (dx1, dy1, dx2, dy2)

    @staticmethod
    def _normalize_roi(start, end):
        if start is None or end is None:
            return None
        x1, y1 = start
        x2, y2 = end
        return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


class UIManager(QtWidgets.QMainWindow):
    closed = QtCore.Signal()

    def __init__(self, window_name: str = "Webcam"):
        super().__init__()
        self.setWindowTitle(window_name)
        self._build_menu()

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
        self.image_label = VideoLabel()
        self.image_label.roi_finalized.connect(self._on_roi_finalized)

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

    def _build_menu(self):
        menu_bar = self.menuBar()

        source_menu = menu_bar.addMenu("Source")
        self.source_webcam_action = QtGui.QAction("Webcam", self)
        self.source_rtsp_action = QtGui.QAction("RTSP", self)
        self.source_image_action = QtGui.QAction("Image File", self)
        source_menu.addAction(self.source_webcam_action)
        source_menu.addAction(self.source_rtsp_action)
        source_menu.addAction(self.source_image_action)

        tools_menu = menu_bar.addMenu("Tools")
        self.roi_action = QtGui.QAction("ROI 설정", self)
        self.roi_action.setCheckable(True)
        self.roi_action.toggled.connect(self._toggle_roi_mode)
        tools_menu.addAction(self.roi_action)

        record_menu = menu_bar.addMenu("Record")
        self.record_entry_action = QtGui.QAction("Entry Log", self)
        record_menu.addAction(self.record_entry_action)

    def _toggle_roi_mode(self, enabled: bool):
        self.image_label.set_roi_mode(enabled)
        if enabled:
            self.statusBar().showMessage("스트리밍 화면에서 드래그하여 ROI를 지정하세요.")
        else:
            self.statusBar().clearMessage()

    def _on_roi_finalized(self, _roi):
        if self.roi_action.isChecked():
            self.roi_action.setChecked(False)

    def get_roi_rect(self):
        return self.image_label.get_roi_rect()

    def show_frame(self, frame, box=None, ocr_text: str | None = None):
        # Overlay text on the frame
        if box:
            x1, y1, x2, y2 = box["bbox"]
            conf = box["conf"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

        # (1) Update plate text
        if ocr_text:
            self.plate_label.setText(ocr_text)
        else:
            self.plate_label.setText("No plate detected")

        # (2) Update stream image
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.image_label.set_frame(qimg)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
