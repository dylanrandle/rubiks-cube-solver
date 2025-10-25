import logging
from typing import Iterable

import cv2
import numpy as np

from rubiks_cube_solver.arduino import Arduino
from rubiks_cube_solver.calibration import load_calibration
from rubiks_cube_solver.constants import (
    COLOR_NEIGHBORHOOD,
    COLOR_TO_FACE,
    DEBUG_PATH,
    POSITION_TO_CAMERA_IDX,
    POSITION_TO_FACES,
    ROTATED_FACET_IDX_TO_COORDINATE_IDX,
)
from rubiks_cube_solver.cv import get_rgb, rgb_to_hsv
from rubiks_cube_solver.types import (
    Color,
    Coordinate,
    Face,
    Image,
    Position,
)
from rubiks_cube_solver.utils import timer


class Perception:
    def __init__(
        self,
        arduino: Arduino,
        debug: bool = False,
    ):
        self.arduino = arduino
        self.debug = debug

        if self.debug and not DEBUG_PATH.exists():
            DEBUG_PATH.mkdir(parents=True, exist_ok=True)

        self.calibration = load_calibration()

    @timer
    def capture_image(self, position: Position):
        self.arduino.turn_light_on(position)
        try:
            rgb = get_rgb(POSITION_TO_CAMERA_IDX[position])
        except Exception as e:
            raise e
        finally:
            self.arduino.turn_light_off(position)
        return Image(rgb=rgb, hsv=rgb_to_hsv(rgb))

    def get_face_colors(self, position: Position, face: Face, image: Image):
        coordinates = self.calibration.facet_coordinates[face]

        colors = self.get_image_colors(image, coordinates)

        if self.debug:
            self.log_face_colors(face, coordinates, colors, image)

        self.arduino.run_move(f"{face.value}2")
        image_rotated = self.capture_image(position)
        self.arduino.run_move(f"{face.value}2'")

        colors_rotated = self.get_image_colors(image_rotated, coordinates)

        if self.debug:
            self.log_face_colors(
                face, coordinates, colors_rotated, image_rotated, suffix="_rotated"
            )

        for facet_idx, coordinate_idx in ROTATED_FACET_IDX_TO_COORDINATE_IDX[
            face
        ].items():
            colors[facet_idx] = colors_rotated[coordinate_idx]

        return colors

    def get_image_colors(self, image: Image, coordinates: Iterable[Coordinate]):
        colors: Iterable[Color] = []
        for coordinate in coordinates:
            pixel_hsv = image.hsv[
                coordinate.y - COLOR_NEIGHBORHOOD : coordinate.y + COLOR_NEIGHBORHOOD,
                coordinate.x - COLOR_NEIGHBORHOOD : coordinate.x + COLOR_NEIGHBORHOOD,
            ].mean(axis=(0, 1))
            color = self.pixel_hsv_to_color(pixel_hsv)
            colors.append(color)
        return colors

    def pixel_hsv_to_color(self, pixel_hsv: np.ndarray):
        for color, range in self.calibration.hsv_ranges.items():
            if np.all((range.min <= pixel_hsv) & (pixel_hsv <= range.max)):
                return color

        closest_color = None
        closest_distance = np.inf
        for color, range in self.calibration.hsv_ranges.items():
            distance = np.min(
                [
                    np.mean((pixel_hsv - range.min) ** 2),
                    np.mean((pixel_hsv - range.max) ** 2),
                ],
            )
            if distance < closest_distance:
                closest_color = color
                closest_distance = distance

        logging.warning(
            f"Unable to find exact color match: {pixel_hsv=}, {closest_color=}, {closest_distance=}",
        )
        return closest_color

    def log_face_colors(
        self,
        face: Face,
        coordinates: Iterable[Coordinate],
        colors: Iterable[Color],
        img: Image,
        suffix: str = "",
    ):
        annotated = img.rgb.copy()
        for coordinate, color in zip(coordinates, colors, strict=False):
            start = (
                coordinate.x - COLOR_NEIGHBORHOOD,
                coordinate.y - COLOR_NEIGHBORHOOD,
            )
            end = (
                coordinate.x + COLOR_NEIGHBORHOOD,
                coordinate.y + COLOR_NEIGHBORHOOD,
            )
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

        cv2.imwrite(DEBUG_PATH / f"debug_face_{face.value}{suffix}.jpg", annotated)

    def get_cube_colors(self):
        cube_colors: dict[Face, Iterable[Color]] = {}
        for position in [Position.LOWER, Position.UPPER]:
            image = self.capture_image(position)
            for face in POSITION_TO_FACES[position]:
                cube_colors[face] = self.get_face_colors(position, face, image)
                logging.debug(f"{face=}, {cube_colors[face]=}")

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
                cube_state.append(COLOR_TO_FACE[color])
                if i == 3:
                    # add center facelet
                    cube_state.append(face)

        return "".join([state.value for state in cube_state])
