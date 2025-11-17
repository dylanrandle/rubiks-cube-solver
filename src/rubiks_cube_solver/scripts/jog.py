import sys
import termios
import tty

from rubiks_cube_solver.arduino import Arduino


def main():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    arduino = Arduino()
    arduino.wait_for_ready()

    def print_raw(*values: object):
        """Helper to achieve similar print behavior in raw mode"""
        print(
            *values,
            end="\r\n",
            flush=True,
        )

    try:
        tty.setraw(sys.stdin.fileno())

        current_axis = None
        axes = ["F", "R", "L", "U", "D", "B"]

        print_raw(f"Select axis: {axes} (or 'q' to quit)")

        while True:
            key = sys.stdin.read(1)

            if key == "\x03":
                break

            if key == "\x1b":
                key_rest = sys.stdin.read(2)
                # Handle potential partial reads (e.g., user just pressing ESC)
                if not key_rest:
                    continue
                key += key_rest

            if current_axis is None:
                upper_key = key.upper()
                if upper_key in axes:
                    current_axis = upper_key
                    print_raw(
                        f"Axis {current_axis} selected. Use LEFT/RIGHT arrows to move.",
                    )
                    print_raw("Press 's' for new axis or 'q' to quit.")
                elif key == "q":
                    break
                else:
                    print_raw("Invalid selection")

            else:
                if key == "\x1b[D":  # Left arrow
                    print_raw(f"Axis {current_axis} -> LEFT")
                    arduino.run_jog(current_axis + "'")
                elif key == "\x1b[C":  # Right arrow
                    print_raw(f"Axis {current_axis} -> RIGHT")
                    arduino.run_jog(current_axis)
                elif key == "s":
                    current_axis = None
                    print_raw(f"Select axis: {axes} (or 'q' to quit)")
                elif key == "q":
                    break

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("Goodbye")


if __name__ == "__main__":
    main()
