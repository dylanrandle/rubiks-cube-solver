import cv2
import numpy as np

colors = {
    "red": ([163, 107, 11], [180, 255, 255]),
    "blue": ([79, 155, 50], [107, 255, 255]),
    "yellow": ([17, 58, 50], [34, 255, 255]),
    "orange": ([5, 130, 50], [20, 255, 255]),
    "green": ([68, 86, 50], [89, 255, 255]),
    "white": ([0, 0, 50], [180, 37, 255]),
}


def get_rubiks_edges(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = np.zeros(hsv.shape, dtype=np.uint8)

    open_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    for color, (lower, upper) in colors.items():
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)
        color_mask = cv2.inRange(hsv, lower, upper)
        color_mask = cv2.morphologyEx(
            color_mask, cv2.MORPH_OPEN, open_kernel, iterations=1
        )
        color_mask = cv2.morphologyEx(
            color_mask, cv2.MORPH_CLOSE, close_kernel, iterations=5
        )

        color_mask = cv2.merge([color_mask, color_mask, color_mask])
        mask = cv2.bitwise_or(mask, color_mask)

    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    hsv = cv2.bitwise_and(hsv, hsv, mask=mask)

    canny = cv2.Canny(cv2.GaussianBlur(hsv, (3, 3), 0), 20, 40)

    cv2.imshow("Canny Edge", canny)


def main():
    pass


if __name__ == "__main__":
    main()
