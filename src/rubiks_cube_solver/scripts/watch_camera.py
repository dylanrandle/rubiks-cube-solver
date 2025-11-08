import argparse
import logging

import cv2

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--camera-index", type=int, required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    cap = cv2.VideoCapture(args.camera_index)

    if not cap.isOpened():
        logger.error("Could not open camera")
        exit()

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                logger.error("Failed to capture image.")
                break

            cv2.imshow("Live Camera Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
