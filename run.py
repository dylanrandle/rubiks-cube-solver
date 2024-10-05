import argparse
import time

import numpy as np
from kociemba import solve

from src.arduino import ArduinoSerial


def parse_args():
    parser = argparse.ArgumentParser("Rubik's cube solver")
    parser.add_argument(
        "-p", "--port", required=True, type=str, help="Serial port for Arduino"
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        required=False,
        type=int,
        default=9600,
        help="Baudrate for serial communication",
    )
    parser.add_argument(
        "-d",
        "--debug",
        required=False,
        action="store_true",
        default=False,
        help="Whether to run random debug moves",
    )
    parser.add_argument(
        "-s",
        "--shuffle",
        required=False,
        action="store_true",
        default=False,
        help="Whether to run shuffling",
    )
    args = parser.parse_args()
    print(f"Parsed args: {vars(args)}")
    return args


def main():
    args = parse_args()

    arduino = ArduinoSerial(args.port, baudrate=args.baudrate)
    arduino.wait_for_ready()

    if args.debug:
        commands = get_random_self_resolving_commands()
    elif args.shuffle:
        commands = get_random_commands()
    else:
        commands = get_solve_commands()

    for c in commands:
        print(f"Writing command: {c}")
        arduino.write_line(c)
        time.sleep(0.1)

    while True:
        print(arduino.read_line())
        time.sleep(0.1)


def get_solve_commands():
    face_to_color = {"U": "G", "R": "O", "F": "W", "D": "B", "L": "R", "B": "Y"}
    color_to_face = {v: k for k, v in face_to_color.items()}

    # TODO: get cube state from cameras
    #             |************|
    #             |*U1**U2**U3*|
    #             |************|
    #             |*U4**U5**U6*|
    #             |************|
    #             |*U7**U8**U9*|
    #             |************|
    # ************|************|************|************
    # *L1**L2**L3*|*F1**F2**F3*|*R1**R2**R3*|*B1**B2**B3*
    # ************|************|************|************
    # *L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*
    # ************|************|************|************
    # *L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*
    # ************|************|************|************
    #             |************|
    #             |*D1**D2**D3*|
    #             |************|
    #             |*D4**D5**D6*|
    #             |************|
    #             |*D7**D8**D9*|
    #             |************|
    # U1, U2, U3, U4, U5, U6, U7, U8, U9,
    # R1, R2, R3, R4, R5, R6, R7, R8, R9,
    # F1, F2, F3, F4, F5, F6, F7, F8, F9,
    # D1, D2, D3, D4, D5, D6, D7, D8, D9,
    # L1, L2, L3, L4, L5, L6, L7, L8, L9,
    # B1, B2, B3, B4, B5, B6, B7, B8, B9.
    cube_colors = (
        f"YGBY{face_to_color["U"]}WRGB"  # up
        + f"RORR{face_to_color["R"]}OBRY"  # right
        + f"GYWY{face_to_color["F"]}GWRO"  # front
        + f"GBWB{face_to_color["D"]}WGBO"  # down
        + f"GOWO{face_to_color["L"]}ROYO"  # left
        + f"YWRG{face_to_color["B"]}BBWY"  # back
    )
    print(f"Got cube colors: {cube_colors}")

    cube_state = "".join([color_to_face[color] for color in cube_colors])
    print(f"Got cube state: {cube_state}")

    solution = solve(cube_state)
    print(f"Solution: {solution}")
    commands = solution.split(" ")
    return commands


def get_random_commands(num_moves=20, random_seed=None):
    if random_seed:
        np.random.seed(random_seed)
    faces = np.random.choice(["L", "F", "R", "D", "U", "B"], size=num_moves)
    counts = np.random.choice(["", "2"], size=num_moves)
    inverted = np.random.choice(["", "'"], size=num_moves)

    commands = [f"{f}{c}{i}" for f, c, i in zip(faces, counts, inverted)]
    return commands


def invert_command(command: str):
    if command.endswith("'"):
        return command[:-1]
    return command + "'"


def get_random_self_resolving_commands(**kwargs):
    commands = get_random_commands(**kwargs)
    commands = commands + list(reversed([invert_command(c) for c in commands]))
    return commands


if __name__ == "__main__":
    main()
