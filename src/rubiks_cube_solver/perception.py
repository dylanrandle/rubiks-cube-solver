import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable

import cv2
import numpy as np

from rubiks_cube_solver.serial import ArduinoSerial


class Position(Enum):
    UPPER = "U"
    LOWER = "L"


class Status(Enum):
    OFF = "0"
    ON = "1"


class Color(Enum):
    RED = "R"
    GREEN = "G"
    ORANGE = "O"
    YELLOW = "Y"
    WHITE = "W"
    BLUE = "B"


class Face(Enum):
    UP = "U"
    FRONT = "F"
    LEFT = "L"
    RIGHT = "R"
    DOWN = "D"
    BACK = "B"


@dataclass
class Coordinate:
    x: int
    y: int


@dataclass
class Range:
    min: np.ndarray
    max: np.ndarray


@dataclass
class Image:
    rgb: np.ndarray
    hsv: np.ndarray


class PerceptionSystem:
    def __init__(self, serial: ArduinoSerial):
        self.serial = serial

        self.position_to_camera_idx: Dict[Position, int] = {
            Position.LOWER: 1,
            Position.UPPER: 2,
        }

        self.light_prefix = "LIGHT:"
        self.facet_coordinates = FACET_COORDINATES
        self.hsv_ranges = HSV_RANGES
        self.position_to_faces: Dict[Position, Iterable[Face]] = {
            Position.UPPER: [Face.UP, Face.LEFT, Face.FRONT],
            Position.LOWER: [Face.RIGHT, Face.BACK, Face.DOWN],
        }
        self.color_to_face = {
            Color.GREEN: Face.UP,
            Color.ORANGE: Face.RIGHT,
            Color.WHITE: Face.FRONT,
            Color.BLUE: Face.DOWN,
            Color.RED: Face.LEFT,
            Color.YELLOW: Face.BACK,
        }
        self.color_neighborhood = 5

    def turn_light_on(self, position: Position):
        self.send_light_command(position, Status.ON)

    def turn_light_off(self, position: Position):
        self.send_light_command(position, Status.OFF)

    def send_light_command(self, position: Position, status: Status):
        command = self.light_prefix + position.value + status.value
        return self.serial.write_line_and_wait_for_response(command)

    def capture_image(self, position: Position):
        self.turn_light_on(position)
        rgb = get_rgb(self.position_to_camera_idx[position])
        self.turn_light_off(position)
        return Image(rgb=rgb, hsv=rgb_to_hsv(rgb))

    def get_face_colors(self, face: Face, image: Image):
        coordinates = self.facet_coordinates[face]
        colors: Iterable[Color] = []
        for coordinate in coordinates:
            pixel_hsv = image.hsv[
                coordinate.y - self.color_neighborhood : coordinate.y
                + self.color_neighborhood,
                coordinate.x - self.color_neighborhood : coordinate.x
                + self.color_neighborhood,
            ].mean(axis=(0, 1))
            color = pixel_hsv_to_color(pixel_hsv)
            colors.append(color)
            logging.debug(f"{face=}, {coordinate=}, {pixel_hsv=}, {color=}")
        return colors

    def get_cube_colors(self):
        cube_colors: Dict[Face, Iterable[Color]] = {}
        for position in [Position.LOWER, Position.UPPER]:
            image = self.capture_image(position)
            for face in self.position_to_faces[position]:
                cube_colors[face] = self.get_face_colors(face, image)

        return cube_colors

    def get_cube_state(self):
        # need to add center face itself
        # need to return order expected by solver:
        # U1, U2, U3, U4, U5, U6, U7, U8, U9,
        # R1, R2, R3, R4, R5, R6, R7, R8, R9,
        # F1, F2, F3, F4, F5, F6, F7, F8, F9,
        # D1, D2, D3, D4, D5, D6, D7, D8, D9,
        # L1, L2, L3, L4, L5, L6, L7, L8, L9,
        # B1, B2, B3, B4, B5, B6, B7, B8, B9.
        cube_colors = self.get_cube_colors()
        cube_state: Iterable[Face] = []
        for face in [Face.UP, Face.RIGHT, Face.FRONT, Face.DOWN, Face.LEFT, Face.BACK]:
            for i in range(9):
                if i == 4:
                    cube_state.append(face)
                else:
                    cube_state.append(self.color_to_face[cube_colors[face][i]])

        return "".join([state.value for state in cube_state])


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


def pixel_hsv_to_color(pixel_hsv: np.ndarray):
    for color, range in HSV_RANGES.items():
        if np.all((range.min <= pixel_hsv) & (pixel_hsv <= range.max)):
            return color
    raise RuntimeError(f"Unable to find a color match for {pixel_hsv=}")


# Need to follow conventions used by solver:
#             |************|
#             |*U1**U2**U3*|
#             |************|
#             |*U4**U5**U6*|
#             |************|
#             |*U7**U8**U9*|
#             |************|
# ************|************|************|************
# *L1**L2**L3*|*F1**F2**F3*|*R1**R2**R3*|*B1**B2**B3*
# ************|************|************|************
# *L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*
# ************|************|************|************
# *L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*
# ************|************|************|************
#             |************|
#             |*D1**D2**D3*|
#             |************|
#             |*D4**D5**D6*|
#             |************|
#             |*D7**D8**D9*|
#             |************|
FACET_COORDINATES: Dict[Face, Iterable[Coordinate]] = {
    Face.BACK: [
        Coordinate(1040, 145),
        Coordinate(1200, 270),
        Coordinate(1379, 469),
        Coordinate(1031, 307),
        Coordinate(1366, 562),
        Coordinate(1010, 498),
        Coordinate(1224, 642),
        Coordinate(1395, 754),
    ],
    Face.LEFT: [
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
    ],
    Face.RIGHT: [
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
    ],
    Face.FRONT: [
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
    ],
    Face.UP: [
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
    ],
    Face.DOWN: [
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
        # Coordinate(),
    ],
}

HSV_RANGES: Dict[Color, Range] = {
    Color.GREEN: Range(min=np.array([40, 126, 123]), max=np.array([72, 198, 240])),
    Color.RED: Range(min=np.array([]), max=np.array([])),
    Color.WHITE: Range(min=np.array([]), max=np.array([])),
    Color.BLUE: Range(min=np.array([]), max=np.array([])),
    Color.YELLOW: Range(min=np.array([78, 77, 180]), max=np.array([89, 171, 242])),
    Color.ORANGE: Range(min=np.array([]), max=np.array([])),
}
