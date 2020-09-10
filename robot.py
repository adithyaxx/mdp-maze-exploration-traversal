import config
from constants import *


class Robot:
    def __init__(self, handler):
        # center of robot
        self.y = config.map_size['height'] - 2
        self.x = 1
        self.bearing = Bearing.NORTH
        self.map = handler.map

    # check that center of robot is not at the border and lies within the map
    def validate(self, x, y):
        if 0 < self.x + x < config.map_size['width'] - 1 and 0 < self.y + y < config.map_size['height'] - 1:
            return True

    # recalculate center of robot
    def move(self, steps=1):
        if self.bearing == Bearing.NORTH:
            if self.validate(0, -steps) and self.north_is_free():
                self.y -= steps
        elif self.bearing == Bearing.EAST:
            if self.validate(steps, 0) and self.east_is_free():
                self.x += steps
        elif self.bearing == Bearing.SOUTH:
            if self.validate(0, steps) and self.south_is_free():
                self.y += steps
        else:
            if self.validate(-steps, 0) and self.west_is_free():
                self.x -= steps

    def left(self):
        # rotate anticlockwise by 90 deg
        self.bearing = Bearing.prev_bearing(self.bearing)

    def right(self):
        # rotate clockwise by 90 deg
        self.bearing = Bearing.next_bearing(self.bearing)

    # check obstacles
    def north_is_free(self):
        for i in range(3):
            if self.map.map_virtual[self.y - 2][self.x - i + 1] == 1:
                return False
        return True

    def south_is_free(self):
        for i in range(3):
            if self.map.map_virtual[self.y + 2][self.x - i + 1] == 1:
                return False
        return True

    def east_is_free(self):
        for i in range(3):
            if self.map.map_virtual[self.y - i + 1][self.x + 2] == 1:
                return False
        return True

    def west_is_free(self):
        for i in range(3):
            if self.map.map_virtual[self.y - i + 1][self.x - 2] == 1:
                return False
        return True

    def get_location(self):
        return self.x, self.y

    def set_location(self, x, y):
        self.x = x
        self.y = y

    def get_right_bearing(self):
        return Bearing.next_bearing(self.bearing)

    def get_left_bearing(self):
        return Bearing.prev_bearing(self.bearing)

    def get_back_bearing(self):
        return Bearing.next_bearing(Bearing.next_bearing(self.bearing))

    def receive(self):
        raise NotImplementedError

    def reset(self):
        self.y = config.map_size['height'] - 2
        self.x = 1
        self.bearing = Bearing.NORTH
