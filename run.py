import argparse
import logging

from kociemba import solve

from src.move import MoveManager
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
        "-i",
        "--input",
        required=False,
        action="store_true",
        default=False,
        help="Whether to wait for input moves",
    )
    parser.add_argument(
        "-s",
        "--shuffle",
        required=False,
        action="store_true",
        default=False,
        help="Whether to run shuffling",
    )
    parser.add_argument(
        "-n",
        "--num-moves",
        required=False,
        type=int,
        default=10,
        help="How many moves to use for shuffling",
    )
    parser.add_argument(
        "--seed",
        required=False,
        type=int,
        default=None,
        help="Random seed",
    )
    args = parser.parse_args()
    logging.info(f"Parsed args: {vars(args)}")
    return args


def main():
    args = parse_args()

    arduino = ArduinoSerial(args.port, baudrate=args.baudrate)
    arduino.wait_for_ready()

    move_manager = MoveManager(arduino)

    if args.debug:
        return move_manager.run_random_resolving_moves(
            num_moves=args.num_moves, random_seed=args.seed
        )
    elif args.shuffle:
        return move_manager.run_random_moves(
            num_moves=args.num_moves, random_seed=args.seed
        )
    elif args.input:
        return move_manager.listen_for_input_moves()
    else:
        moves = get_solve_commands()
        return move_manager.run_moves(moves)


def get_solve_commands():
    face_to_color = {"U": "G", "R": "O", "F": "W", "D": "B", "L": "R", "B": "Y"}
    color_to_face = {v: k for k, v in face_to_color.items()}

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
    # TODO: get cube state from cameras
    cube_colors = (
        f"GGGG{face_to_color['U']}GBBB"  # up
        + f"OOOO{face_to_color['R']}OORO"  # right
        + f"YYYW{face_to_color['F']}WWWW"  # front
        + f"BBBB{face_to_color['D']}BGGG"  # down
        + f"RRRR{face_to_color['L']}RROR"  # left
        + f"YYYY{face_to_color['B']}YWWW"  # back
    )
    logging.info(f"Got cube colors: {cube_colors}")

    cube_state = "".join([color_to_face[color] for color in cube_colors])
    logging.info(f"Got cube state: {cube_state}")

    solution = solve(cube_state)
    logging.info(f"Solution: {solution}")

    commands = solution.split(" ")
    return commands


if __name__ == "__main__":
    main()
