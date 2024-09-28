import time

from arduino import ArduinoSerial


def main():
    arduino = ArduinoSerial(port=101)
    arduino.wait_for_ready()

    commands = ["L2", "R'"]
    for c in commands:
        print(f"Writing command: {c}")
        num_written = arduino.write_line(c)
        print(f"Wrote bytes: {num_written}")

    time.sleep(1)

    while arduino.available() > 0:
        print(arduino.read_line())


if __name__ == "__main__":
    main()
