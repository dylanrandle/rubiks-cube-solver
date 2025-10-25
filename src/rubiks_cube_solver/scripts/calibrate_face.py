import argparse
import json
import logging
from pathlib import Path

import cv2

from rubiks_cube_solver.constants import FACE_TO_POSITION, FACES_PATH
from rubiks_cube_solver.cv import keep_windows_open, show_image
from rubiks_cube_solver.types import (
    Coordinate,
    Face,
    Image,
    Position,
)
from rubiks_cube_solver.utils import maybe_commit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="Path to input images",
    )
    parser.add_argument(
        "-f",
        "--face",
        required=True,
        type=str,
        help="Face code (e.g. F)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists():
        raise RuntimeError("Invalid input directory")

    images: dict[Position, Image] = {}
    for pos in Position:
        img = Image(
            rgb=cv2.imread(input_dir / f"{pos}_rgb.jpg"),
            hsv=cv2.imread(input_dir / f"{pos}_hsv.jpg"),
        )
        images[pos] = img

    face = Face(args.face)

    calibrate_coordinate(face, images)


def calibrate_coordinate(face, images: dict[Position, Image]):
    logging.info("""
    Need to follow conventions used by solver:
                |************|
                |*U1**U2**U3*|
                |************|
                |*U4**U5**U6*|
                |************|
                |*U7**U8**U9*|
                |************|
    ************|************|************|************
    *L1**L2**L3*|*F1**F2**F3*|*R1**R2**R3*|*B1**B2**B3*
    ************|************|************|************
    *L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*
    ************|************|************|************
    *L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*
    ************|************|************|************
                |************|
                |*D1**D2**D3*|
                |************|
                |*D4**D5**D6*|
                |************|
                |*D7**D8**D9*|
                |************|
    """)
    logging.info(f"Calibrating face: {face}")
    coordinates: list[Coordinate] = []

    def get_coordinate(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            logging.info(f"Coordinate: ({x}, {y})")
            coordinates.append(Coordinate(x=x, y=y))

    pos = FACE_TO_POSITION[face]
    img = images[pos]

    window_id = f"Camera: {pos}"
    show_image(window_id, img.rgb, callback=get_coordinate)

    keep_windows_open(destroy=False)

    if len(coordinates) != 8:
        logging.warning(
            f"Received invalid number of coordinates ({len(coordinates)}), exiting",
        )
        return
    annotated = img.rgb.copy()

    for i, coord in enumerate(coordinates):
        start = (coord.x - 5, coord.y - 5)
        end = (coord.x + 5, coord.y + 5)

        color = (0, 0, 0)
        thickness = -1

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1

        annotated = cv2.rectangle(annotated, start, end, color, thickness)
        annotated = cv2.putText(
            annotated,
            f"{i}",
            (coord.x + 5, coord.y - 5),
            font,
            font_scale,
            color,
            5,
        )

    show_image(f"Annotated: {pos}", annotated)

    keep_windows_open(destroy=True)

    maybe_commit(lambda: save_coordinates(face, coordinates))


def save_coordinates(face: Face, coordinates: list[Coordinate]):
    if FACES_PATH.exists():
        with open(FACES_PATH) as f:
            data = json.load(f)
    else:
        data = {}

    data[face.value] = [{"x": c.x, "y": c.y} for c in coordinates]

    with open(FACES_PATH, "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    main()
