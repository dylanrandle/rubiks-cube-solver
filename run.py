import argparse

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
    args = parser.parse_args()
    print(f"Parsed args: {vars(args)}")
    return args


def main():
    args = parse_args()

    arduino = ArduinoSerial(args.port, baudrate=args.baudrate)
    arduino.wait_for_ready()

    # TODO: get cube state from cameras
    cube_state = "DRLUUBFBRBLURRLRUBLRDDFDLFUFUFFDBRDUBRUFLLFDDBFLUBLRBD"
    print(f"Got cube state: {cube_state}")

    solution = solve(cube_state)
    print(f"Solution: {solution}")

    commands = solution.split(" ")
    for c in commands:
        print(f"Writing command: {c}")
        arduino.write_line(c)


if __name__ == "__main__":
    main()
