import time

from rubiks_cube_solver.perception import Light, PerceptionSystem
from rubiks_cube_solver.serial import ArduinoSerial


def trigger_lights():
    serial = ArduinoSerial(31201)
    serial.wait_for_ready()

    perception = PerceptionSystem(serial, 0, 1)

    while True:
        perception.turn_light_on(Light.LOWER)
        time.sleep(1)
        perception.turn_light_off(Light.LOWER)
        time.sleep(1)


if __name__ == "__main__":
    trigger_lights()
