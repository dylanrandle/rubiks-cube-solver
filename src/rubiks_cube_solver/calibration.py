import json
from collections.abc import Iterable

from rubiks_cube_solver.constants import FACES_PATH
from rubiks_cube_solver.types import Calibration, Coordinate, Face


def load_calibration() -> Calibration:
    with open(FACES_PATH) as f:
        faces: dict[str, list[dict]] = json.load(f)

    facet_coordinates: dict[Face, Iterable[Coordinate]] = {}

    for face_id, face_coordinates in faces.items():
        facet_coordinates[Face(face_id)] = [
            Coordinate(coordinate["x"], coordinate["y"])
            for coordinate in face_coordinates
        ]

    return Calibration(facet_coordinates=facet_coordinates)
