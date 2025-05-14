import argparse
import logging

from rubiks_cube_solver.solver import solve
from rubiks_cube_solver.move import MoveManager
from rubiks_cube_solver.perception import PerceptionSystem
from rubiks_cube_solver.serial import ArduinoSerial


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

    serial = ArduinoSerial(args.port, baudrate=args.baudrate)
    serial.wait_for_ready()

    move_manager = MoveManager(serial)
    perception = PerceptionSystem(serial)

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
        cube_state = perception.get_cube_state()
        moves = solve(cube_state)
        return move_manager.run_moves(moves)


if __name__ == "__main__":
    main()
