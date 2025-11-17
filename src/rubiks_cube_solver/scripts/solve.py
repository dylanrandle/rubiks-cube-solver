import argparse
import logging

from rubiks_cube_solver.arduino import Arduino
from rubiks_cube_solver.perception import Perception
from rubiks_cube_solver.solver import solve


def parse_args():
    parser = argparse.ArgumentParser("Rubik's cube solver")
    parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        default=False,
        help="Whether to add debug logging",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.info(f"Parsed args: {args}")

    arduino = Arduino()
    arduino.wait_for_ready()

    perception = Perception(arduino, debug=args.debug)

    cube_state = perception.get_cube_state()
    logging.debug(f"Got cube state: {cube_state}")

    response = input("Solve? (y/n): ")
    if response.strip().lower() != "y":
        logging.info("Quitting")
        return

    moves = solve(cube_state)
    return arduino.run_moves(moves)


if __name__ == "__main__":
    main()
