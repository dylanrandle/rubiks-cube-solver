from dataclasses import dataclass
from enum import Enum
from typing import Iterable

import numpy as np


class Position(Enum):
    UPPER = "U"
    LOWER = "L"


class Status(Enum):
    OFF = "0"
    ON = "1"


class Color(Enum):
    RED = "R"
    GREEN = "G"
    ORANGE = "O"
    YELLOW = "Y"
    WHITE = "W"
    BLUE = "B"


class Face(Enum):
    UP = "U"
    FRONT = "F"
    LEFT = "L"
    RIGHT = "R"
    DOWN = "D"
    BACK = "B"


@dataclass
class Coordinate:
    x: int
    y: int


@dataclass
class Range:
    min: np.ndarray
    max: np.ndarray


@dataclass
class Image:
    rgb: np.ndarray
    hsv: np.ndarray


@dataclass
class Calibration:
    facet_coordinates: dict[Face, Iterable[Coordinate]]
