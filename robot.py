import config
from constants import *

class Robot:

    def __init__(self):
        #center of robot
        self.y = config.map_size['height']-2
        self.x = 1
        self.direction = Direction.NORTH

    #check that center of robot is not at the boarder and lies within the map
    def validate(self, x, y):
        if 0 < self.x + x < config.map_size['width']-1 and 0 < self.y + y < config.map_size['height']-1:
            return True

    #recalculate center of robot
    def move(self):
        if(self.direction == Direction.NORTH):
            if self.validate(0, -1) and self.north_free():
                self.y -= 1
        elif(self.direction == Direction.EAST):
            if self.validate(1, 0) and self.east_free():
                self.x += 1
        elif(self.direction == Direction.SOUTH):
            if self.validate(0, 1) and self.south_free():
                self.y += 1
        else:
            if self.validate(-1, 0) and self.west_free():
                self.x -= 1

    def left(self):
        #rotate anticlockwise by 90 deg
        self.direction = Direction.prev_direction(self.direction)

    def right(self):
        #rotate clockwise by 90 deg
        self.direction = Direction.next_direction(self.direction)

    # check obstacles
    def north_free(self):
        for i in range(3):
            if config.map_explored[self.y - 2][self.x - i + 1] == 1:
                return False
        return True

    def south_free(self):
        for i in range(3):
            if config.map_explored[self.y + 2][self.x - i + 1] == 1:
                return False
        return True

    def east_free(self):
        for i in range(3):
            if config.map_explored[self.y - i + 1][self.x + 2] == 1:
                return False
        return True

    def west_free(self):
        for i in range(3):
            if config.map_explored[self.y - i + 1][self.x - 2] == 1:
                return False
        return True