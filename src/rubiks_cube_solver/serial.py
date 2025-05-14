import logging
import time

import serial

from rubiks_cube_solver.utils import timer


class ArduinoSerial:
    def __init__(self, port, baudrate=9600):
        self.serial = serial.Serial(port=f"/dev/tty.usbmodem{port}", baudrate=baudrate)

    @timer
    def write_line_and_wait_for_response(self, message: str):
        self.write_line(message)

        logging.info(f"Sent: {message}")

        while not self.in_size() > 0:
            time.sleep(0.01)

        line = self.read_line()

        logging.info(f"Received: {line}")

        return line

    def wait_for_ready(self):
        while self.read_line() != "STATUS:READY":
            logging.info("Waiting for Arduino to be ready...")
            time.sleep(1)

        logging.info("Arduino ready")

    def read_line(self):
        return self.serial.readline().decode().strip()

    def write_line(self, message: str):
        return self.serial.write(f"{message}\n".encode("ascii"))

    def in_size(self) -> int:
        return self.serial.in_waiting

    def out_size(self) -> int:
        return self.serial.out_waiting
