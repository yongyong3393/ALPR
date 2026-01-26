from PySide6 import QtCore, QtGui, QtWidgets

from ui.image_label import ImageLabel


class MainWindow(QtWidgets.QMainWindow):
    closed = QtCore.Signal()
    roi_finalized = QtCore.Signal(tuple)

    def __init__(self):
        super().__init__()

        # Components of the main window
        # 1. Menu bar
        # 2. Central widget with 2x2 grid layout
        #    - (1, 1): recognized plate text
        #    - (1, 2): live stream
        #    - (2, x): placeholders

        # 1. Menu bar
        self._build_menu()

        # 2. Central widget with 2x2 grid layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        grid = QtWidgets.QGridLayout(central)
        grid.setContentsMargins(12, 12, 12, 12)
        grid.setSpacing(12)

        # (1, 1): recognized plate text
        self.plate_label = QtWidgets.QLabel("No plate detected")
        self.plate_label.setAlignment(QtCore.Qt.AlignCenter)
        self.plate_label.setStyleSheet("font-size: 28px; font-weight: 600;")

        # (1, 2): live stream
        self.image_label = ImageLabel()
        self.image_label.roi_finalized.connect(self._on_roi_finalized)

        # (2, x): placeholders
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

        # 1. Source
        source_menu = menu_bar.addMenu("Source")

        self.source_webcam_action = QtGui.QAction("Webcam", self)
        self.source_rtsp_action = QtGui.QAction("RTSP", self)
        self.source_image_action = QtGui.QAction("Image File", self)

        source_menu.addAction(self.source_webcam_action)
        source_menu.addAction(self.source_rtsp_action)
        source_menu.addAction(self.source_image_action)

        # 2. Tools
        tools_menu = menu_bar.addMenu("Tools")

        self.roi_action = QtGui.QAction("ROI 설정", self)
        self.roi_action.setCheckable(True)
        self.roi_action.toggled.connect(self._toggle_roi_mode)

        tools_menu.addAction(self.roi_action)

        # 3. Record
        record_menu = menu_bar.addMenu("Record")

        self.record_entry_action = QtGui.QAction("Entry Log", self)

        record_menu.addAction(self.record_entry_action)

    # Menu Callbacks
    def _toggle_roi_mode(self, enabled: bool):
        self.image_label.set_roi_mode(enabled)
        if enabled:
            self.statusBar().showMessage("스트리밍 화면에서 드래그하여 ROI를 지정하세요.")
        else:
            self.statusBar().clearMessage()

    def _on_roi_finalized(self, roi):
        if self.roi_action.isChecked():
            self.roi_action.setChecked(False)
        self.roi_finalized.emit(roi)

    def show_frame(self, frame, box=None, ocr_text: str | None = None):
        # (1) Update plate text
        if ocr_text:
            self.plate_label.setText(ocr_text)
        else:
            self.plate_label.setText("No plate detected")

        # (2) Update stream image
        self.image_label.set_frame(frame, box)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
