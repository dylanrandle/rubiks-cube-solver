from typing import Iterable

import numpy as np

from rubiks_cube_solver.serial import ArduinoSerial


class MoveManager:
    def __init__(self, serial: ArduinoSerial):
        self.serial = serial
        self.prefix = "MOVE:"

    def run_move(self, move: str):
        return self.serial.write_line_and_wait_for_response(self.prefix + move)

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


def get_random_moves(num_moves: int, random_seed: int = None):
    if random_seed:
        np.random.seed(random_seed)

    faces = {"L", "F", "R", "D", "U", "B"}
    counts = ["", "2"]
    inversions = ["", "'"]

    commands, last_face = [], ""
    for _ in range(num_moves):
        # we make sure not to repeat the same face in consecutive moves
        face = np.random.choice(list(sorted(faces.difference(last_face))))
        count = np.random.choice(counts)
        inverted = np.random.choice(inversions)
        commands.append(f"{face}{count}{inverted}")
        last_face = face

    return commands


def invert_moves(move: str):
    if move.endswith("'"):
        return move[:-1]
    return move + "'"


def get_random_resolving_moves(num_moves: int, random_seed: int = None):
    commands = get_random_moves(num_moves=num_moves, random_seed=random_seed)
    commands = commands + list(reversed([invert_moves(c) for c in commands]))
    return commands
