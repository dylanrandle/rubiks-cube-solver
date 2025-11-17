import argparse
import logging
from dataclasses import dataclass
from typing import Optional

from rubiks_cube_solver.arduino import Arduino
from rubiks_cube_solver.move import get_random_moves, get_random_resolving_moves


@dataclass
class Args:
    resolve: bool
    num_moves: int
    random_seed: Optional[int] = None


def parse_args():
    parser = argparse.ArgumentParser("Rubik's cube solver")
    parser.add_argument(
        "--resolve",
        required=False,
        action="store_true",
        default=False,
        help="Whether to run auto-resolving moves",
    )
    parser.add_argument(
        "--num-moves",
        required=False,
        type=int,
        default=20,
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

    if args.resolve:
        moves = get_random_resolving_moves(
            num_moves=args.num_moves, random_seed=args.random_seed
        )
    else:
        moves = get_random_moves(num_moves=args.num_moves, random_seed=args.random_seed)

    return arduino.run_moves(moves)


if __name__ == "__main__":
    main()
