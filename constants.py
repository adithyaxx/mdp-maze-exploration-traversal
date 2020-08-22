from enum import IntEnum


class Bearing(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    @staticmethod
    def next_bearing(current_bearing):
        return Bearing((current_bearing.value + 5) % 4)

    @staticmethod
    def prev_bearing(current_bearing):
        return Bearing((current_bearing.value + 3) % 4)


class MOVEMENT(IntEnum):
    FORWARD = 0
    LEFT = 1
    RIGHT = 2
