import argparse
import logging
from dataclasses import dataclass
from typing import Optional

from rubiks_cube_solver.arduino import Arduino
from rubiks_cube_solver.move import get_random_moves, get_random_resolving_moves
from rubiks_cube_solver.perception import Perception
from rubiks_cube_solver.solver import solve


@dataclass
class Args:
    debug: bool
    shuffle: bool
    shuffle_and_resolve: bool
    listen_for_input: bool
    num_moves: int
    random_seed: Optional[int] = None


def parse_args():
    parser = argparse.ArgumentParser("Rubik's cube solver")
    parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        default=False,
        help="Whether to add debug logging",
    )
    parser.add_argument(
        "--shuffle",
        required=False,
        action="store_true",
        default=False,
        help="Whether to run shuffling moves",
    )
    parser.add_argument(
        "--shuffle-and-resolve",
        required=False,
        action="store_true",
        default=False,
        help="Whether to run auto-resolving moves",
    )
    parser.add_argument(
        "--listen-for-input",
        required=False,
        action="store_true",
        default=False,
        help="Whether to wait for input moves",
    )
    parser.add_argument(
        "--num-moves",
        required=False,
        type=int,
        default=10,
        help="How many moves to use for shuffling",
    )
    parser.add_argument(
        "--random-seed",
        required=False,
        type=int,
        default=None,
        help="Random seed",
    )
    args = parser.parse_args()
    args = Args(**vars(args))
    logging.info(f"Parsed args: {args}")
    return args


def main():
    args = parse_args()

    arduino = Arduino()
    arduino.wait_for_ready()

    perception = Perception(arduino, debug=args.debug)

    if args.shuffle:
        moves = get_random_moves(num_moves=args.num_moves, random_seed=args.random_seed)
        return arduino.run_moves(moves)

    if args.shuffle_and_resolve:
        moves = get_random_resolving_moves(
            num_moves=args.num_moves, random_seed=args.random_seed
        )
        return arduino.run_moves(moves)

    if args.listen_for_input:
        while True:
            command = input("Enter a move or press 'q' to exit: ").strip()
            if command.lower() == "q":
                exit()
            arduino.run_move(command)

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
