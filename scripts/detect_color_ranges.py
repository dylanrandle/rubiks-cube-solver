import logging

import cv2
import numpy as np

from rubiks_cube_solver.perception import (
    Image,
    PerceptionSystem,
    Position,
)
from rubiks_cube_solver.serial import ArduinoSerial

LOWER_ID = 0
UPPER_ID = 1

green_min = [40, 126, 123]
green_max = [72, 198, 240]

yellow_min = [78, 77, 180]
yellow_max = [89, 171, 242]


def find_hsv_ranges():
    serial = ArduinoSerial(31201)
    serial.wait_for_ready()

    perception = PerceptionSystem(serial=serial)
    img = perception.capture_image(Position.LOWER)

    values = []

    def get_pixel_value(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            hsv_color = img.hsv[y, x]
            logging.info(f"HSV at ({x}, {y}): {hsv_color}")
            values.append(hsv_color)

    cv2.imshow("Image", img.rgb)
    cv2.setMouseCallback("Image", get_pixel_value)

    wait()

    values = np.stack(values)

    values_min = np.min(values, axis=0)
    values_max = np.max(values, axis=0)
    logging.info(f"min={values_min}, max={values_max}")

    mask = mask_by_hsv(img, values_min, values_max)
    cv2.imshow("Original", img.rgb)
    cv2.imshow("Mask", mask)

    wait()


def mask_by_hsv(img: Image, lower_hsv, upper_hsv, mask_color=(0, 0, 0)):
    lower_bound = np.array(lower_hsv)
    upper_bound = np.array(upper_hsv)

    mask = cv2.inRange(img.hsv, lower_bound, upper_bound)

    masked_img = img.rgb.copy()
    masked_img[mask > 0] = mask_color

    return masked_img


def wait():
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def load_image(image_path):
    image = cv2.imread(image_path)
    return image


if __name__ == "__main__":
    find_hsv_ranges()
