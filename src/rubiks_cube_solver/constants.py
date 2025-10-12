from collections.abc import Iterable
from pathlib import Path

from rubiks_cube_solver.types import Color, Face, Position

ROOT_PATH = Path(__file__).parent.parent.parent
COLORS_PATH = ROOT_PATH / "data" / "colors.json"
FACES_PATH = ROOT_PATH / "data" / "faces.json"

POSITION_TO_CAMERA_IDX: dict[Position, int] = {
    Position.LOWER: 0,
    Position.UPPER: 2,
}

POSITION_TO_FACES: dict[Position, Iterable[Face]] = {
    Position.UPPER: [Face.UP, Face.LEFT, Face.FRONT],
    Position.LOWER: [Face.RIGHT, Face.BACK, Face.DOWN],
}

FACE_TO_POSITION: dict[Face, Position] = {}
for pos, faces in POSITION_TO_FACES.items():
    for face in faces:
        FACE_TO_POSITION[face] = pos

COLOR_TO_FACE: dict[Color, Face] = {
    Color.GREEN: Face.UP,
    Color.ORANGE: Face.RIGHT,
    Color.WHITE: Face.FRONT,
    Color.BLUE: Face.DOWN,
    Color.RED: Face.LEFT,
    Color.YELLOW: Face.BACK,
}

# Contains coordinate indices for facets
# that we perceive after 180 degree rotation
ROTATED_FACET_IDX_TO_COORDINATE_IDX = {
    Face.FRONT: {
        4: 3,
        6: 1,
        7: 0,
    },
    Face.LEFT: {
        3: 4,
        5: 2,
        6: 1,
    },
    Face.UP: {
        1: 6,
        2: 5,
        4: 3,
    },
    Face.RIGHT: {
        0: 7,
        1: 6,
        3: 4,
    },
    Face.BACK: {
        1: 6,
        2: 5,
        4: 3,
    },
    Face.DOWN: {
        0: 7,
        1: 6,
        3: 4,
    },
}
