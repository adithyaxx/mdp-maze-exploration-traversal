from enum import Enum

class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    @staticmethod
    def next_direction(current_direction):
        return Direction((current_direction.value + 5)% 4)

    @staticmethod
    def prev_direction(current_direction):
        return Direction((current_direction.value + 3)% 4)

class MOVEMENT(Enum):
    FORWARD = 0
    LEFT = 1
    RIGHT = 2
