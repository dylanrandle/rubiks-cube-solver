import cv2
import numpy as np


def load_image(image_path):
    image = cv2.imread(image_path)
    return image


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


green_min = [67, 159, 119]
green_max = [88, 196, 243]

yellow_min = [87, 191, 124]
yellow_max = [95, 202, 234]

if __name__ == "__main__":
    rgb = load_image("data/images/test_capture.png")
    hsv = rgb_to_hsv(rgb)

    values = []

    def get_pixel_value(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            hsv_color = hsv[y, x]
            print(f"HSV at ({x}, {y}): {hsv_color}")
            values.append(hsv_color)

    cv2.imshow("Image", rgb)
    cv2.setMouseCallback("Image", get_pixel_value)

    wait()

    values = np.stack(values)

    values_min = np.min(values, axis=0)
    values_max = np.max(values, axis=0)
    print(f"min={values_min}, max={values_max}")

    mask = mask_by_hsv(rgb, hsv, values_min, values_max)
    cv2.imshow("Original", rgb)
    cv2.imshow("Mask", mask)

    wait()
