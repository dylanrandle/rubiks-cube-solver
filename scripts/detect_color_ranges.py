import logging

import cv2
import numpy as np

from rubiks_cube_solver.perception import capture_image, rgb_to_hsv

LOWER_ID = 0
UPPER_ID = 1

green_min = [40, 126, 123]
green_max = [72, 198, 240]

yellow_min = [78, 77, 180]
yellow_max = [89, 171, 242]


def find_hsv_ranges():
    rgb = capture_image(2, delay_seconds=0)
    hsv = rgb_to_hsv(rgb)

    values = []

    def get_pixel_value(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            hsv_color = hsv[y, x]
            logging.info(f"HSV at ({x}, {y}): {hsv_color}")
            values.append(hsv_color)

    cv2.imshow("Image", rgb)
    cv2.setMouseCallback("Image", get_pixel_value)

    wait()

    values = np.stack(values)

    values_min = np.min(values, axis=0)
    values_max = np.max(values, axis=0)
    logging.info(f"min={values_min}, max={values_max}")

    mask = mask_by_hsv(rgb, hsv, values_min, values_max)
    cv2.imshow("Original", rgb)
    cv2.imshow("Mask", mask)

    wait()


def mask_by_hsv(rgb_img, hsv_img, lower_hsv, upper_hsv, mask_color=(0, 0, 0)):
    lower_bound = np.array(lower_hsv)
    upper_bound = np.array(upper_hsv)

    mask = cv2.inRange(hsv_img, lower_bound, upper_bound)

    masked_img = rgb_img.copy()
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
