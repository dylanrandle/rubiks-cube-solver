from typing import Iterable
from kociemba import solve as _solve


def solve(cube_state: str) -> Iterable[str]:
    solution = _solve(cube_state)
    if not isinstance(solution, str):
        raise Exception("Unable to solve cube")
    return solution.split(" ")
