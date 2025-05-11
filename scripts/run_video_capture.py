import cv2


def main():
    capture = cv2.VideoCapture(1)
    if not capture.isOpened():
        print("Cannot open camera")
        exit()

    params = [
        cv2.CAP_PROP_AUTO_EXPOSURE,
        cv2.CAP_PROP_EXPOSURE,
    ]

    for p in params:
        print(p, capture.get(p))

    while True:
        ret, frame = capture.read()
        if not ret:
            print("Error reading image, quitting")
            break

        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
