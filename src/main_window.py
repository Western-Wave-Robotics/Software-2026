import sys
import time

import cv2
import numpy as np
import pygame
import serial
from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # GUI Setup
        self.setWindowTitle("ROV Control and Camera Feed")
        self.resize(800, 600)

        self.layout = QVBoxLayout()

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        # Camera Setup
        self.video_label = QLabel("VIDEO STREAM")
        self.video_label.setMinimumSize(640, 480)
        self.layout.addWidget(self.video_label)

        self.camera_thread = QThread()
        self.camera_worker = CameraWorker(fps=30)

        self.camera_worker.moveToThread(self.camera_thread)

        self.camera_thread.started.connect(self.camera_worker.run)
        self.camera_worker.camera_ready.connect(self.update_frame)
        self.camera_worker.error.connect(self.handle_camera_error)

        self.camera_thread.start()

        # Controller Setup
        self.controller_label = QLabel("CONTROLLER CONNECTED")
        self.layout.addWidget(self.controller_label)

        self.controller_thread = QThread()
        self.controller_worker = ControllerWorker()

        self.controller_thread.started.connect(self.controller_worker.run)
        self.controller_worker.controller_ready.connect(self.read_controller)
        self.controller_worker.error.connect(self.handle_controller_error)

        self.controller_thread.start()

        # Arduino setup
        self.ser = None
        self.serial_btn = QPushButton("Connect to Arduino")
        self.serial_btn.clicked.connect(self.connect_serial)
        self.layout.addWidget(self.serial_btn)

    # QT Slot - Camera
    def update_frame(self, frame):
        """Display live video feed from the camera."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image)

        # Scale to fit label (keeps aspect ratio)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.video_label.setPixmap(scaled_pixmap)

    # QT Slot - Controller
    def read_controller(self, cntrl_data):
        """Send scaled motor control data to arduino"""
        print(cntrl_data)

        command = f"{int(cntrl_data["motorFL"])} {int(cntrl_data["motorFR"])} {int(cntrl_data["motorBL"])} {int(cntrl_data["motorBR"])} {int(cntrl_data["motorUPL"])} {int(cntrl_data["motorUPR"])}\n"
        self.ser.write(command.encode("utf-8"))

    def handle_camera_error(self, msg):
        self.video_label.setText(f"Camera Error:\n{msg}")

    def handle_controller_error(self, msg):
        self.controller_label.setText(f"Controller Error:\n{msg}")

    def closeEvent(self, event):
        """Release resources when the GUI is closed."""
        # Close camera thread
        self.camera_worker.stop()
        self.camera_thread.quit()
        self.camera_thread.wait()

        # Close controller thread
        self.controller_worker.stop()
        self.controller_thread.quit()
        self.controller_thread.wait()

        # others
        if self.ser:
            self.ser.close()
        pygame.quit()
        event.accept()


# Run the GUI application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
