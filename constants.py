from enum import Enum

class Direction(Enum):
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"

class MOVEMENT(Enum):
    FORWARD = "F"
    LEFT = "L"
    RIGHT = "R"
    #BACKWARD = "B"