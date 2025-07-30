import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable
import json
from pathlib import Path

import cv2
import numpy as np

from rubiks_cube_solver.serial import ArduinoSerial
from rubiks_cube_solver.utils import timer


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
    def __init__(
        self,
        serial: ArduinoSerial,
        debug: bool = False,
        camera_delay_seconds: float = 0.5,
    ):
        self.serial = serial

        self.debug = debug
        self.debug_path = Path("debug")
        if self.debug and not self.debug_path.exists():
            self.debug_path.mkdir()

        self.calibration = load_calibration()

        self.camera_delay_seconds = camera_delay_seconds
        self.position_to_camera_idx: Dict[Position, int] = {
            Position.LOWER: 0,
            Position.UPPER: 2,
        }

        self.position_to_camera_capture: Dict[Position, cv2.VideoCapure] = {}
        for pos, idx in self.position_to_camera_idx.items():
            cap = cv2.VideoCapture(idx)
            if not cap.isOpened():
                raise IOError(f"Unable to open webcam {pos} @ {idx}")
            self.position_to_camera_capture[pos] = cap

        self.light_prefix = "LIGHT:"
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

    @timer
    def capture_image(self, position: Position):
        self.turn_light_on(position)
        try:
            rgb = get_rgb(
                self.position_to_camera_capture[position],
                delay_seconds=self.camera_delay_seconds,
            )
        except Exception as e:
            raise e
        finally:
            self.turn_light_off(position)
        return Image(rgb=rgb, hsv=rgb_to_hsv(rgb))

    def get_face_colors(self, face: Face, image: Image):
        coordinates = self.calibration.facet_coordinates[face]
        colors: Iterable[Color] = []
        for coordinate in coordinates:
            pixel_hsv = image.hsv[
                coordinate.y - self.color_neighborhood : coordinate.y
                + self.color_neighborhood,
                coordinate.x - self.color_neighborhood : coordinate.x
                + self.color_neighborhood,
            ].mean(axis=(0, 1))
            color = self.pixel_hsv_to_color(pixel_hsv)
            colors.append(color)
            logging.debug(f"{face=}, {coordinate=}, {pixel_hsv=}, {color=}")

        if self.debug:
            self.log_face_colors(face, coordinates, colors, image)

        return colors

    def pixel_hsv_to_color(self, pixel_hsv: np.ndarray):
        for color, range in self.calibration.hsv_ranges.items():
            if np.all((range.min <= pixel_hsv) & (pixel_hsv <= range.max)):
                return color

        logging.warning(
            f"Unable to find exact color match: {pixel_hsv=}, falling back to nearest"
        )

        closest_color = None
        closest_distance = np.inf
        for color, range in self.calibration.hsv_ranges.items():
            distance = np.min(
                [
                    np.sum(np.abs(pixel_hsv - range.min)),
                    np.sum(np.abs(pixel_hsv - range.max)),
                ]
            )
            if distance < closest_distance:
                closest_color = color
                closest_distance = distance
        return closest_color

    def log_face_colors(
        self,
        face: Face,
        coordinates: Iterable[Coordinate],
        colors: Iterable[Color],
        img: Image,
    ):
        annotated = img.rgb.copy()
        for coordinate, color in zip(coordinates, colors):
            start = (coordinate.x - 5, coordinate.y - 5)
            end = (coordinate.x + 5, coordinate.y + 5)
            draw_color = (0, 0, 0)
            annotated = cv2.rectangle(annotated, start, end, draw_color, -1)
            annotated = cv2.putText(
                annotated,
                color.value,
                (coordinate.x + 5, coordinate.y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                draw_color,
                5,
            )

        cv2.imwrite(self.debug_path / f"debug_face_{face.value}.jpg", annotated)

    def get_cube_colors(self):
        cube_colors: Dict[Face, Iterable[Color]] = {}
        for position in [Position.LOWER, Position.UPPER]:
            image = self.capture_image(position)
            for face in self.position_to_faces[position]:
                cube_colors[face] = self.get_face_colors(face, image)

        return cube_colors

    def get_cube_state(self):
        cube_colors = self.get_cube_colors()
        cube_state: Iterable[Face] = []
        # need to return order expected by solver:
        # U1, U2, U3, U4, U5, U6, U7, U8, U9,
        # R1, R2, R3, R4, R5, R6, R7, R8, R9,
        # F1, F2, F3, F4, F5, F6, F7, F8, F9,
        # D1, D2, D3, D4, D5, D6, D7, D8, D9,
        # L1, L2, L3, L4, L5, L6, L7, L8, L9,
        # B1, B2, B3, B4, B5, B6, B7, B8, B9.
        for face in [Face.UP, Face.RIGHT, Face.FRONT, Face.DOWN, Face.LEFT, Face.BACK]:
            for i, color in enumerate(cube_colors[face]):
                cube_state.append(self.color_to_face[color])
                if i == 3:
                    # add center facelet
                    cube_state.append(face)

        return "".join([state.value for state in cube_state])

    def __del__(self):
        for cap in self.position_to_camera_capture.values():
            cap.release()


def get_rgb(cap: cv2.VideoCapture, delay_seconds: float = 0):
    time.sleep(delay_seconds)

    ret, frame = cap.read()

    if not ret:
        raise IOError("Unable to read frame")

    return frame


def rgb_to_hsv(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)


@dataclass
class Calibration:
    hsv_ranges: Dict[Color, Range]
    facet_coordinates: Dict[Face, Iterable[Coordinate]]


CALIBRATION_PATH = Path(__file__).parent.parent.parent / "data" / "calibration.json"


def load_calibration() -> Calibration:
    with open(CALIBRATION_PATH, "r") as f:
        data: Dict[str, Dict] = json.load(f)

    hsv_ranges: Dict[Color, Range] = {}

    for color_id, color_range in data["colors"].items():
        hsv_ranges[Color(color_id)] = Range(
            min=np.array(color_range["min"]), max=np.array(color_range["max"])
        )

    facet_coordinates: Dict[Face, Iterable[Coordinate]] = {}

    for face_id, face_coordinates in data["coordinates"].items():
        facet_coordinates[Face(face_id)] = [
            Coordinate(coordinate["x"], coordinate["y"])
            for coordinate in face_coordinates
        ]

    return Calibration(hsv_ranges=hsv_ranges, facet_coordinates=facet_coordinates)
