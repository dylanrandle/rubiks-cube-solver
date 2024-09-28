import time

import serial


class ArduinoSerial:
    def __init__(self, port, baudrate=9600):
        self.serial = serial.Serial(port=f"/dev/tty.usbmodem{port}", baudrate=baudrate)

    def read_line(self):
        return self.serial.readline().decode().strip()

    def write_line(self, message: str):
        return self.serial.write(f"{message}\n".encode("ascii"))

    def wait_for_ready(self):
        while self.read_line() != "ARDUINO:READY":
            print("Waiting for Arduino to be ready...")
            time.sleep(1)

        print("Arduino ready")

    def available(self) -> int:
        return self.serial.in_waiting
