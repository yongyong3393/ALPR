from PySide6 import QtCore, QtGui, QtWidgets

from ui.renderer import render_frame
from ui.video_view import VideoView


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
        self.image_label = VideoView()
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
        # (1) Update plate text
        if ocr_text:
            self.plate_label.setText(ocr_text)
        else:
            self.plate_label.setText("No plate detected")

        # (2) Update stream image
        qimg = render_frame(frame, box)
        self.image_label.set_frame(qimg)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
