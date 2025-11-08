import cv2

from rubiks_cube_solver.arduino import Arduino
from rubiks_cube_solver.constants import DEBUG_PATH
from rubiks_cube_solver.perception import (
    Perception,
)
from rubiks_cube_solver.types import Position


def main():
    serial = Arduino()
    serial.wait_for_ready()

    perception = Perception(arduino=serial)

    if not DEBUG_PATH.exists():
        DEBUG_PATH.mkdir()

    for pos in Position:
        img = perception.capture_image(pos)
        cv2.imwrite(DEBUG_PATH / f"{pos}_rgb.jpg", img.rgb)
        cv2.imwrite(DEBUG_PATH / f"{pos}_hsv.jpg", img.hsv)


if __name__ == "__main__":
    main()
