import argparse
from typing import Dict
from pathlib import Path

import cv2

from rubiks_cube_solver.perception import (
    Image,
    PerceptionSystem,
    Position,
)
from rubiks_cube_solver.serial import ArduinoSerial


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", required=True, type=str, help="Port to arduino")
    parser.add_argument(
        "-o", "--output", required=True, type=str, help="Output directory"
    )
    args = parser.parse_args()

    serial = ArduinoSerial(args.port)
    serial.wait_for_ready()

    perception = PerceptionSystem(serial=serial)

    output_dir = Path(args.output)
    if not output_dir.exists():
        output_dir.mkdir()

    images: Dict[Position, Image] = {}
    for pos in Position:
        img = perception.capture_image(pos)
        images[pos] = img
        cv2.imwrite(output_dir / f"{pos}_rgb.jpg", img.rgb)
        cv2.imwrite(output_dir / f"{pos}_hsv.jpg", img.hsv)


if __name__ == "__main__":
    main()
