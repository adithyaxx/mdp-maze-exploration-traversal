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

    def left_diag(self):
        self.bearing = Bearing.prev_bearing_diag(self.bearing)

    def right_diag(self):
        self.bearing = Bearing.next_bearing_diag(self.bearing)

    def move_diag(self, steps=1):
        if self.bearing == Bearing.NORTH_EAST:
            self.x += steps
            self.y -= steps
        elif self.bearing == Bearing.SOUTH_EAST:
            self.x += steps
            self.y += steps
        elif self.bearing == Bearing.SOUTH_WEST:
            self.x -= steps
            self.y += steps
        else:
            self.x -= steps
            self.y -= steps

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

    def sense_front(self, location, bearing, sensor_data):

        sensor_offsets = [
            [[-1, 0, 1], [-1, -1, -1]],
            [[1, 1, 1], [-1, 0, 1]],
            [[1, 0, -1], [1, 1, 1]],
            [[-1, -1, -1], [1, 0, -1]]
        ]
        offset = sensor_offsets[int(bearing / 2)]

        self.handler.update_map(location[0] + offset[0][0], location[1] + offset[1][0], sensor_data[0],
                                bearing, config.sensor_range['front_left'])
        self.handler.update_map(location[0] + offset[0][1], location[1] + offset[1][1], sensor_data[1],
                                bearing, config.sensor_range['front_middle'])
        self.handler.update_map(location[0] + offset[0][2], location[1] + offset[1][2], sensor_data[2],
                                bearing, config.sensor_range['front_right'])

    # call update map for left sensor
    def sense_left(self, location, bearing, sensor_data):

        sensor_offsets = [
            [-1, -1],
            [1, -1],
            [1, 1],
            [-1, 1]
        ]
        offset = sensor_offsets[int(bearing / 2)]
        self.handler.update_map(location[0] + offset[0], location[1] + offset[1], sensor_data,
                                Bearing.prev_bearing(bearing), config.sensor_range['left'])

    # call update map for right sensor
    def sense_right(self, location, bearing, sensor_data):

        sensor_offsets = [
            [1, 0],
            [0, 1],
            [-1, 0],
            [0, -1]
        ]
        offset = sensor_offsets[int(bearing / 2)]

        self.handler.update_map(location[0] + offset[0], location[1] + offset[1], sensor_data,
                                Bearing.next_bearing(bearing), config.sensor_range['right'])

    # sense simulated sensor
    def sense(self, backtrack=0):
        sensor_data = self.receive()
        print(sensor_data)
        location = self.get_location()
        bearing = self.bearing

        self.sense_front(location, bearing, sensor_data[:3])
        self.sense_left(location, bearing, sensor_data[3])
        self.sense_right(location, bearing, sensor_data[4])

        for i in range(1, backtrack + 1):
            if bearing == Bearing.NORTH:
                x, y = location
                y += i
            elif bearing == Bearing.SOUTH:
                x, y = location
                y -= i
            elif bearing == Bearing.EAST:
                x, y = location
                x -= i
            else:
                x, y = location
                x += i

            self.set_location(x, y)
            sensor_data = self.receive()
            self.sense_front((x, y), bearing, sensor_data[:3])
            self.sense_left((x, y), bearing, sensor_data[3])
            self.sense_right((x, y), bearing, sensor_data[4])

        x, y = location
        self.set_location(x, y)

    def reset(self):
        self.y = config.map_size['height'] - 2
        self.x = 1
        self.bearing = Bearing.NORTH
