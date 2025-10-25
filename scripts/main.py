import argparse
import logging

from rubiks_cube_solver.arduino import Arduino
from rubiks_cube_solver.perception import Perception
from rubiks_cube_solver.solver import solve


def parse_args():
    parser = argparse.ArgumentParser("Rubik's cube solver")
    parser.add_argument(
        "-p",
        "--port",
        required=True,
        type=str,
        help="Serial port for Arduino",
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
        "--seed",
        required=False,
        type=int,
        default=None,
        help="Random seed",
    )
    parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        default=False,
        help="Whether to add debug logging",
    )
    args = parser.parse_args()
    logging.info(f"Parsed args: {vars(args)}")
    return args


def main():
    args = parse_args()

    arduino = Arduino(args.port)
    arduino.wait_for_ready()

    perception = Perception(arduino, debug=args.debug)

    if args.shuffle:
        return arduino.run_random_moves(num_moves=args.num_moves, random_seed=args.seed)

    if args.shuffle_and_resolve:
        return arduino.run_random_resolving_moves(
            num_moves=args.num_moves,
            random_seed=args.seed,
        )

    if args.listen_for_input:
        return arduino.listen_for_input_moves()

    cube_state = perception.get_cube_state()
    logging.debug("Got cube state: {}")
    moves = solve(cube_state)
    return arduino.run_moves(moves)


if __name__ == "__main__":
    main()
