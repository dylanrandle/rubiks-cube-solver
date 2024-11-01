import cv2


def main():
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print("Cannot open camera")
        exit()

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
