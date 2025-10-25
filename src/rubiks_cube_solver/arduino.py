import logging
import time
from collections.abc import Iterable

import serial

from rubiks_cube_solver.constants import ARDUINO_BAUDRATE
from rubiks_cube_solver.move import (
    get_random_moves,
    get_random_resolving_moves,
)
from rubiks_cube_solver.types import Position, Status
from rubiks_cube_solver.utils import timer


class Arduino:
    def __init__(self, port):
        self.serial = serial.Serial(port=port, baudrate=ARDUINO_BAUDRATE)
        self.move_prefix = "MOVE:"
        self.light_prefix = "LIGHT:"

    @timer
    def write_line_and_wait_for_response(self, message: str):
        self.write_line(message)

        logging.debug(f"Sent: {message}")

        while not self.in_size() > 0:
            time.sleep(0.01)

        line = self.read_line()

        logging.debug(f"Received: {line}")

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

    def run_move(self, move: str):
        return self.write_line_and_wait_for_response(self.move_prefix + move)

    def run_moves(self, moves: Iterable[str]):
        for move in moves:
            self.run_move(move)

    def listen_for_input_moves(self):
        while True:
            command = input("Enter a move or press 'q' to exit: ").strip()
            if command.lower() == "q":
                exit()
            self.run_move(command)

    def run_random_moves(self, num_moves: int, random_seed: int = None):
        moves = get_random_moves(num_moves=num_moves, random_seed=random_seed)
        self.run_moves(moves)

    def run_random_resolving_moves(self, num_moves: int, random_seed: int = None):
        moves = get_random_resolving_moves(num_moves=num_moves, random_seed=random_seed)
        self.run_moves(moves)

    def turn_light_on(self, position: Position):
        self.send_light_command(position, Status.ON)

    def turn_light_off(self, position: Position):
        self.send_light_command(position, Status.OFF)

    def send_light_command(self, position: Position, status: Status):
        command = self.light_prefix + position.value + status.value
        return self.write_line_and_wait_for_response(command)
