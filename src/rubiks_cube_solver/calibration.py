import json
from collections.abc import Iterable

import numpy as np

from rubiks_cube_solver.constants import COLORS_PATH, FACES_PATH
from rubiks_cube_solver.types import Calibration, Color, Coordinate, Face, Range


def load_calibration() -> Calibration:
    with open(COLORS_PATH) as f:
        colors: dict[str, dict] = json.load(f)

    hsv_ranges: dict[Color, Range] = {}

    for color_id, color_range in colors.items():
        hsv_ranges[Color(color_id)] = Range(
            min=np.array(color_range["min"]),
            max=np.array(color_range["max"]),
        )

    with open(FACES_PATH) as f:
        faces: dict[str, list[dict]] = json.load(f)

    facet_coordinates: dict[Face, Iterable[Coordinate]] = {}

    for face_id, face_coordinates in faces.items():
        facet_coordinates[Face(face_id)] = [
            Coordinate(coordinate["x"], coordinate["y"])
            for coordinate in face_coordinates
        ]

    return Calibration(hsv_ranges=hsv_ranges, facet_coordinates=facet_coordinates)
