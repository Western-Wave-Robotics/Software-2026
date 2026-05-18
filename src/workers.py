# workers.py - Background worker threads for camera and controller input.

import time

import cv2
import numpy as np
import pygame
from PyQt6.QtCore import QObject, pyqtSignal

from src.controller_math import apply_deadzone, calculate_thrust, ramp_value, scale


class CameraWorker(QObject):
    # Signals
    camera_ready = pyqtSignal(np.ndarray)
    error = pyqtSignal(str)

    def __init__(self, fps=30):
        super().__init__()
        self.fps = fps
        self.running = True

    def run(self):
        frame_time = 1.0 / self.fps

        try:
            cap = cv2.VideoCapture(1)

            if not cap.isOpened():
                raise Exception("Camera not found")

            while self.running:
                start_time = time.time()

                ret, frame = cap.read()

                if not ret:
                    self.error.emit("Error Reading Frame")
                    break
                else:
                    self.camera_ready.emit(frame)

                # Limit fps
                elapsed = time.time() - start_time  # Elapsed time to load single frame
                time.sleep(max(0, frame_time - elapsed))  # Subtract elapsed time for stable fps

            cap.release()

        except Exception as e:
            self.error.emit(str(e))

        finally:
            if cap:
                cap.release()

    def stop(self):
        self.running = False


class ControllerWorker(QObject):
    # Signals
    status = pyqtSignal(str)
    controller_ready = pyqtSignal(dict)

    def __init__(self, poll_rate=30, ramp_rate=1000):
        super().__init__()
        self.poll_rate = poll_rate
        self.ramp_rate = ramp_rate
        self.controllers = {}
        self.cntrl_data = {}
        self.running = True
        self.prev_motor_values = {
            "motorFL": 1500,
            "motorFR": 1500,
            "motorBL": 1500,
            "motorBR": 1500,
            "motorUPL": 1500,
            "motorUPR": 1500,
        }

    def run(self):
        pygame.init()
        pygame.joystick.init()

        interval = 1 / self.poll_rate  # Time between polls in seconds

        while self.running:
            start_time = time.time()

            # Controller hotplugging
            for event in pygame.event.get():
                if event.type == pygame.JOYDEVICEADDED:
                    controller = pygame.joystick.Joystick(event.device_index)
                    self.controllers[controller.get_instance_id()] = controller
                    self.status.emit(f"Controller {controller.get_instance_id()} Connected")

                elif event.type == pygame.JOYDEVICEREMOVED:
                    del self.controllers[event.instance_id]
                    self.status.emit(f"Controller {event.instance_id} Disconnected")

            if not self.controllers:
                time.sleep(0.1)
                continue

            # Use the first connected controller
            controller = list(self.controllers.values())[0]

            # Joysticks
            left_stick_x = controller.get_axis(0)
            left_stick_y = controller.get_axis(1)
            right_stick_x = controller.get_axis(2)
            right_stick_y = controller.get_axis(3)

            # Triggers
            # left_trigger = controller.get_axis(4)
            # right_trigger = controller.get_axis(5)

            # D-pad
            # dpad_x, dpad_y = controller.get_hat(0)
            # Buttons
            # button_A = controller.get_button(0)
            # B = controller.get_button(1)
            # X = controller.get_button(2)
            # Y = controller.get_button(3)

            # Bumpers
            # LB = controller.get_button(4)
            # RB = controller.get_button(5)

            surge = apply_deadzone(-left_stick_y, deadzone=0.1)
            yaw = apply_deadzone(left_stick_x, deadzone=0.1)
            sway = apply_deadzone(right_stick_x, deadzone=0.1)
            heave = apply_deadzone(-right_stick_y, deadzone=0.1)

            motorFL, motorFR, motorBL, motorBR, motorUPL, motorUPR = calculate_thrust(
                surge, sway, yaw, heave
            )

            target_values = {
                "motorFL": scale(motorFL),
                "motorFR": scale(motorFR),
                "motorBL": scale(motorBL),
                "motorBR": scale(motorBR),
                "motorUPL": scale(motorUPL),
                "motorUPR": scale(motorUPR),
            }

            # Ramp motor values
            max_step = self.ramp_rate * interval
            for name, target_value in target_values.items():
                self.cntrl_data[name] = ramp_value(
                    self.prev_motor_values.get(name, 1500),
                    target_value,
                    max_step,
                )
                self.prev_motor_values[name] = self.cntrl_data[name]

            self.controller_ready.emit(self.cntrl_data.copy())  # Send data to main thread

            # limit polling rate (similar to fps)
            elapsed = time.time() - start_time  # Elapsed time to load single frame
            time.sleep(max(0, interval - elapsed))

    def stop(self):
        self.running = False
