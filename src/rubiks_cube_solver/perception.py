import logging
import time
from enum import Enum

import cv2

from rubiks_cube_solver.serial import ArduinoSerial


class Light(Enum):
    UPPER = "U"
    LOWER = "L"


class Status(Enum):
    OFF = "0"
    ON = "1"


class PerceptionSystem:
    def __init__(self, serial: ArduinoSerial, lower_idx: int, upper_idx: int):
        self.serial = serial
        self.light_prefix = "LIGHT:"

        self.hsv_ranges = {}
        self.lower_cap = cv2.VideoCapture(lower_idx)
        self.upper_cap = cv2.VideoCapture(upper_idx)

        if not self.lower_cap.isOpened() or not self.upper_cap.isOpened():
            raise IOError("Unable to open webcams")

    def turn_light_on(self, light: Light):
        self.send_light_command(light, Status.ON)

    def turn_light_off(self, light: Light):
        self.send_light_command(light, Status.OFF)

    def send_light_command(self, light: Light, status: Status):
        command = self.light_prefix + light.value + status.value
        self.serial.write_line(command)

        logging.info(f"Sent: {command}")

        while not self.serial.in_size() > 0:
            time.sleep(0.01)

        line = self.serial.read_line()

        logging.info(f"Received: {line}")

    def perceive_cube(self):
        pass

    def capture_images(self):
        pass

    def __del__(self):
        self.lower_cap.release()
        self.upper_cap.release()


def capture_image(camera_idx: int, delay_seconds: float = 0):
    cap = cv2.VideoCapture(camera_idx)

    if not cap.isOpened():
        raise IOError("Unable to open webcam")

    time.sleep(delay_seconds)

    ret, frame = cap.read()

    if not ret:
        raise IOError("Unable to read frame")

    cap.release()

    return frame


def rgb_to_hsv(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
