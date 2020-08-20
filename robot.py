import config
from constants import *

class Robot:

    def __init__(self):
        self.y = config.map_size['height']-2
        self.x = 1
        self.direction = Direction.NORTH


