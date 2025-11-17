import logging

from rubiks_cube_solver.arduino import Arduino

logger = logging.getLogger(__name__)


def main():
    arduino = Arduino()
    arduino.wait_for_ready()

    try:
        while True:
            move = input("Enter a move command: ")
            arduino.run_move(move)
    except KeyboardInterrupt:
        logger.info("Shutting down")


if __name__ == "__main__":
    main()
