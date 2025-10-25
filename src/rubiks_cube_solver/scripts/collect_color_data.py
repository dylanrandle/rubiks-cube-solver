import argparse
import json
import logging
from pathlib import Path

import cv2
import numpy as np

from rubiks_cube_solver.constants import COLOR_NEIGHBORHOOD, COLORS_PATH
from rubiks_cube_solver.cv import keep_windows_open, mask_by_hsv, show_image
from rubiks_cube_solver.types import (
    Color,
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
        "-c",
        "--color",
        required=True,
        type=str,
        help="Color code (e.g. R)",
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

    color = Color(args.color)

    collect_color_data(color, images)


def collect_color_data(color: Color, images: dict[Position, Image]):
    pixels_hsv = []
    logging.info(f"Collecting data for {color=}")

    def mouse_callback(img: Image):
        def get_pixel_value(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                hsv_color = img.hsv[
                    y - COLOR_NEIGHBORHOOD : y + COLOR_NEIGHBORHOOD,
                    x - COLOR_NEIGHBORHOOD : x + COLOR_NEIGHBORHOOD,
                ].mean(axis=(0, 1))
                logging.debug(f"HSV at ({x}, {y}): {hsv_color}")
                pixels_hsv.append(hsv_color)

        return get_pixel_value

    for pos in Position:
        img = images[pos]
        window_id = f"Camera: {pos}"
        show_image(window_id, img.rgb, callback=mouse_callback(img))

    keep_windows_open(destroy=False)

    if len(pixels_hsv) == 0:
        logging.warning("Did not receive any selected pixels, exiting")
        return

    hsv_min = np.min(pixels_hsv, axis=0)
    hsv_max = np.max(pixels_hsv, axis=0)

    logging.info(f"Color: {color} | min: {hsv_min} | max: {hsv_max}")

    for pos in Position:
        img = images[pos]
        mask = mask_by_hsv(img, hsv_min, hsv_max)
        window_id = f"Masked: {pos}"
        show_image(window_id, mask)

    keep_windows_open(destroy=True)

    maybe_commit(lambda: save_colors(color, pixels_hsv))


def save_colors(color: Color, pixels_hsv: list[np.ndarray]):
    if COLORS_PATH.exists():
        with open(COLORS_PATH) as f:
            data = json.load(f)
    else:
        data = {}

    curr_list: list = data.get(color.value, [])
    assert isinstance(curr_list, list), "Expected to receive list type for color data"
    curr_list += [arr.tolist() for arr in pixels_hsv]

    data[color.value] = curr_list

    with open(COLORS_PATH, "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    main()
