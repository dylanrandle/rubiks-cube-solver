import logging

from rubiks_cube_solver.arduino import Arduino

logger = logging.getLogger(__name__)


def main():
    arduino = Arduino()
    arduino.wait_for_ready()

    try:
        while True:
            jog = input("Enter a jog command: ")
            arduino.run_jog(jog)
    except KeyboardInterrupt:
        logger.info("Shutting down")


if __name__ == "__main__":
    main()
