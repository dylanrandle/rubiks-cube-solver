import time
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np

from rubiks_cube_solver.serial import ArduinoSerial


class Position(Enum):
    UPPER = "U"
    LOWER = "L"


class Status(Enum):
    OFF = "0"
    ON = "1"


@dataclass
class Image:
    rgb: np.ndarray
    hsv: np.ndarray


class PerceptionSystem:
    def __init__(self, serial: ArduinoSerial):
        self.serial = serial
        self.light_prefix = "LIGHT:"

        self.hsv_ranges = {}
        self.position_to_idx = {
            Position.LOWER: 0,
            Position.UPPER: 1,
        }

    def turn_light_on(self, position: Position):
        self.send_light_command(position, Status.ON)

    def turn_light_off(self, position: Position):
        self.send_light_command(position, Status.OFF)

    def send_light_command(self, position: Position, status: Status):
        command = self.light_prefix + position.value + status.value
        return self.serial.write_line_and_wait_for_response(command)

    def capture_image(self, position: Position):
        self.turn_light_on(position)
        rgb = get_rgb(self.position_to_idx[position])
        self.turn_light_off(position)
        return Image(rgb=rgb, hsv=rgb_to_hsv(rgb))


def get_rgb(camera_idx: int, delay_seconds: float = 0):
    cap = cv2.VideoCapture(camera_idx)

    if not cap.isOpened():
        raise IOError(f"Unable to open webcam {camera_idx}")

    time.sleep(delay_seconds)

    ret, frame = cap.read()

    if not ret:
        raise IOError(f"Unable to read frame {camera_idx}")

    cap.release()

    return frame


def rgb_to_hsv(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
