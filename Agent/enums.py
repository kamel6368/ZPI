"""All enums used by agent"""
from enum import Enum


class Block(Enum):
    BALL = 0
    ROLLER = 1
    CUBOID = 2
    CUBE = 3
    PYRAMID = 4
    INVALID = 5


class Color(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2
    BLUE = 3
    VIOLET = 4
    NONE = 5


class Shape(Enum):
    POINT = 0
    LINE = 1
    TRIANGLE = 2
    EQUILATERAL_TRIANGLE = 3
    ISOSCELES_TRIANGLE = 4
    SQUARE = 5
    RECTANGLE = 6
    RHOMBUS = 7
    PARALLELOGRAM = 8
    TRAPEZIUM = 9
    QUADRILATERAL = 10
    PENTAGON = 11
    HEXAGON = 12
    HEPTAGON = 13
    OCTAGON = 14
    CIRCLE = 15
    ELLIPSE = 16
    POLYGON = 17
    KITE = 18
    INVALID = 19
    NONE = 20


class MoveState(Enum):
    DISCONNECTED = 0
    IDLE = 1
    MOVING = 2
    STUCK = 3


class ColorSpace(Enum):
    BGR = 0
    HSV = 1
    HSL = 2


class Pattern(Enum):
    HORIZONTAL_LINES = 0
    VERTICAL_LINES = 1
    LEFT_INCLINED_LINES = 2
    RIGHT_INCLINED_LINES = 3
    GRID = 4
    INCLINED_GRID = 5
    NONE = 6


class Size(Enum):
    TINY = 0
    SMALL = 1
    MEDIUM = 2
    BIG = 3
    LARGE = 4
    NONE = 5
