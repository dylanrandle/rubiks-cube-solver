import logging

import cv2
import numpy as np

from rubiks_cube_solver.types import Image


def show_image(window_id: str, rgb: np.ndarray, callback=None):
    cv2.namedWindow(window_id, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_id, rgb.shape[1] // 2, rgb.shape[0] // 2)
    cv2.imshow(window_id, rgb)
    if callback:
        cv2.setMouseCallback(window_id, callback)


def keep_windows_open(destroy=True):
    logging.info("Press `q` in the window to continue")
    cv2.waitKey(0)
    if destroy:
        cv2.destroyAllWindows()


def get_rgb(idx: int):
    cap = cv2.VideoCapture(idx)

    if not cap.isOpened():
        raise OSError(f"Unable to open webcam: {idx}")

    ret, frame = cap.read()

    cap.release()

    if not ret:
        raise OSError("Unable to read frame")

    return frame


def rgb_to_hsv(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)


def mask_by_hsv(img: Image, lower_hsv, upper_hsv, mask_color=(0, 0, 0)):
    lower_bound = np.array(lower_hsv)
    upper_bound = np.array(upper_hsv)

    mask = cv2.inRange(img.hsv, lower_bound, upper_bound)

    masked_img = img.rgb.copy()
    masked_img[mask > 0] = mask_color

    return masked_img
