import logging
import time
from enum import Enum

import cv2
import numpy as np

from rubiks_cube_solver.serial import ArduinoSerial


class Light(Enum):
    UPPER = "U"
    LOWER = "L"


class Status(Enum):
    OFF = "0"
    ON = "1"


class PerceptionSystem:
    def __init__(self, serial: ArduinoSerial, lower_idx: int, upper_idx: int):
        self.serial = serial
        self.light_prefix = "LIGHT:"

        self.hsv_ranges = {}
        self.lower_cap = cv2.VideoCapture(lower_idx)
        self.upper_cap = cv2.VideoCapture(upper_idx)

        if not self.lower_cap.isOpened() or not self.upper_cap.isOpened():
            raise IOError("Unable to open webcams")

    def turn_light_on(self, light: Light):
        self.send_light_command(light, Status.ON)

    def turn_light_off(self, light: Light):
        self.send_light_command(light, Status.OFF)

    def send_light_command(self, light: Light, status: Status):
        command = self.light_prefix + light.value + status.value
        self.serial.write_line(command)

        logging.info(f"Sent: {command}")

        while not self.serial.in_size() > 0:
            time.sleep(0.01)

        line = self.serial.read_line()

        logging.info(f"Received: {line}")

    def perceive_cube(self):
        pass

    def capture_images(self):
        pass

    def __del__(self):
        self.lower_cap.release()
        self.upper_cap.release()


def load_image(image_path):
    image = cv2.imread(image_path)
    return image


def capture_image(camera_idx: int, delay_seconds: float = 0):
    cap = cv2.VideoCapture(camera_idx)

    if not cap.isOpened():
        raise IOError("Unable to open webcam")

    time.sleep(delay_seconds)

    ret, frame = cap.read()

    if not ret:
        raise IOError("Unable to read frame")

    cap.release()

    return frame


def rgb_to_hsv(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)


def wait():
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def mask_by_hsv(rgb_img, hsv_img, lower_hsv, upper_hsv, mask_color=(0, 0, 0)):
    lower_bound = np.array(lower_hsv)
    upper_bound = np.array(upper_hsv)

    mask = cv2.inRange(hsv_img, lower_bound, upper_bound)

    masked_img = rgb_img.copy()
    masked_img[mask > 0] = mask_color

    return masked_img


LOWER_ID = 0
UPPER_ID = 1

green_min = [40, 126, 123]
green_max = [72, 198, 240]

yellow_min = [78, 77, 180]
yellow_max = [89, 171, 242]


def find_hsv_ranges():
    # rgb = load_image("data/images/test_capture_emeet_light_autoexposure.png")
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


def trigger_lights():
    serial = ArduinoSerial(31201)
    serial.wait_for_ready()

    perception = PerceptionSystem(serial, 0, 1)

    while True:
        perception.turn_light_on(Light.LOWER)
        time.sleep(1)
        perception.turn_light_off(Light.LOWER)
        time.sleep(1)


if __name__ == "__main__":
    trigger_lights()
