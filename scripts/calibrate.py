import argparse
import logging
from typing import Callable, Dict, List
import json
from pathlib import Path

import cv2
import numpy as np

from rubiks_cube_solver.perception import (
    Color,
    Coordinate,
    Face,
    Image,
    PerceptionSystem,
    Position,
)
from rubiks_cube_solver.serial import ArduinoSerial


CALIBRATION_PATH = Path(__file__).parent.parent / "data" / "calibration.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", required=True, type=str, help="Port to arduino")
    parser.add_argument(
        "-m",
        "--mode",
        required=True,
        choices={"colors", "coordinates"},
        help="Calibration modality",
    )
    args = parser.parse_args()

    serial = ArduinoSerial(args.port)
    serial.wait_for_ready()

    perception = PerceptionSystem(serial=serial)

    images: Dict[Position, Image] = {}
    for pos in Position:
        img = perception.capture_image(pos)
        images[pos] = img

    if args.mode == "colors":
        calibrate_colors(images)
    elif args.mode == "coordinates":
        calibrate_coordinates(images)
    else:
        raise RuntimeError(f"Unrecognized mode: {args.mode}")


def calibrate_colors(images: Dict[Position, Image]):
    for color in Color:
        pixels_hsv = []
        logging.info(f"Calibrating {color}")

        def mouse_callback(img: Image):
            def get_pixel_value(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    hsv_color = img.hsv[y, x]
                    logging.debug(f"HSV at ({x}, {y}): {hsv_color}")
                    pixels_hsv.append(hsv_color)

            return get_pixel_value

        for pos in Position:
            img = images[pos]
            window_id = f"Camera: {pos}"
            show_image(window_id, img.rgb, callback=mouse_callback(img))

        wait(destroy=False)

        if len(pixels_hsv) == 0:
            logging.warning("Did not receive any selected pixels, skipping")
            continue

        hsv_min = np.min(pixels_hsv, axis=0)
        hsv_max = np.max(pixels_hsv, axis=0)

        logging.info(f"Color: {color} | min: {hsv_min} | max: {hsv_max}")

        for pos in Position:
            img = images[pos]
            mask = mask_by_hsv(img, hsv_min, hsv_max)
            window_id = f"Masked: {pos}"
            show_image(window_id, mask)

        wait(destroy=True)

        maybe_commit(lambda: save_color(color, hsv_min, hsv_max))


def calibrate_coordinates(images: Dict[Position, Image]):
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
    for face in Face:
        logging.info(f"Calibrating face: {face}")
        coordinates: List[Coordinate] = []

        def get_coordinate(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                logging.debug(f"Coordinate: ({x}, {y})")
                coordinates.append(Coordinate(x=x, y=y))

        pos = Position(input("Select position (U, L): ").strip().upper())
        img = images[pos]

        window_id = f"Camera: {pos}"
        show_image(window_id, img.rgb, callback=get_coordinate)

        wait(destroy=False)

        if len(coordinates) != 8:
            logging.warning(
                f"Received invalid number of coordinates ({len(coordinates)}), skipping"
            )
            continue

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

        wait(destroy=True)

        maybe_commit(lambda: save_coordinates(face, coordinates))


def save_color(color: Color, hsv_min: np.ndarray, hsv_max: np.ndarray):
    with open(CALIBRATION_PATH, "r") as f:
        data = json.load(f)

    data["colors"][color.value] = {
        "min": hsv_min.tolist(),
        "max": hsv_max.tolist(),
    }

    with open(CALIBRATION_PATH, "w") as f:
        json.dump(data, f)


def save_coordinates(face: Face, coordinates: List[Coordinate]):
    with open(CALIBRATION_PATH, "r") as f:
        data = json.load(f)

    data["coordinates"][face.value] = [{"x": c.x, "y": c.y} for c in coordinates]

    with open(CALIBRATION_PATH, "w") as f:
        json.dump(data, f)


def mask_by_hsv(img: Image, lower_hsv, upper_hsv, mask_color=(0, 0, 0)):
    lower_bound = np.array(lower_hsv)
    upper_bound = np.array(upper_hsv)

    mask = cv2.inRange(img.hsv, lower_bound, upper_bound)

    masked_img = img.rgb.copy()
    masked_img[mask > 0] = mask_color

    return masked_img


def wait(destroy=True):
    logging.info("Press `q` in the window to continue")
    cv2.waitKey(0)
    if destroy:
        cv2.destroyAllWindows()


def show_image(window_id: str, rgb: np.ndarray, callback=None):
    cv2.namedWindow(window_id, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_id, rgb.shape[1] // 2, rgb.shape[0] // 2)
    cv2.imshow(window_id, rgb)
    if callback:
        cv2.setMouseCallback(window_id, callback)


def maybe_commit(callable: Callable):
    logging.info("Commit? (y/n)")
    response = input().strip().lower()
    if response == "y":
        callable()
    else:
        logging.info("Not saving results")


if __name__ == "__main__":
    main()
