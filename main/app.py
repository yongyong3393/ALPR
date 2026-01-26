import sys
from PySide6 import QtCore, QtWidgets

from alpr_worker.alpr_worker import ALPRWorker
from source.video_stream import VideoStream
from main.app_state import AppState
from ui.main_window import MainWindow


class App:
    def __init__(self):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        self.state = AppState()

        # 1. Load ALPR worker (YOLO + OCR)
        self.alpr_worker = ALPRWorker()
        self.alpr_worker.start()

        # 2. Load webcam stream
        self.stream = VideoStream()

        # 3. Load UI manager
        self.ui_manager = MainWindow()
        self.ui_manager.closed.connect(self.stop)

        # main loop state
        self.frame_idx = 0
        self.N = 60  # Process every N frames
        self._running = False

        self.timer = QtCore.QTimer()
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._on_timer)

        self.qt_app.aboutToQuit.connect(self.stop)

    def start(self):
        self._running = True
        self.ui_manager.showMaximized()
        self.timer.start()
        return self.qt_app.exec()

    def stop(self):
        if not self._running:
            return
        self._running = False
        self.timer.stop()
        self.alpr_worker.stop()
        self.stream.release()
        if self.ui_manager.isVisible():
            self.ui_manager.close()

    def _on_timer(self):
        if not self._running:
            return

        ok, frame = self.stream.read()
        if not ok:
            print("[ERROR] Cannot read a frame from webcam")
            self.stop()
            return

        # ALPR every N frames
        self.frame_idx += 1
        if self.frame_idx % self.N == 0:
            roi = self.ui_manager.get_roi_rect()
            if roi is None:
                h, w = frame.shape[:2]
                roi = (0, 0, w - 1, h - 1)
            self.state.roi_rect = roi
            self.alpr_worker.submit_frame(frame, roi)

        # Get latest OCR results
        last_box, last_text = self.alpr_worker.get_latest_result()

        # Visualize results on UI
        self.ui_manager.show_frame(frame, last_box, last_text)


def main():
    app = App()
    return app.start()


if __name__ == "__main__":
    raise SystemExit(main())
