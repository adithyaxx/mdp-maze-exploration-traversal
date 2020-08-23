import config
from constants import Bearing


class Core:
    def __init__(self, handler):
        self.handler = handler
        self.map = self.handler.map

    def explore(self):
        self.periodic_check()

    def periodic_check(self):
        self.sense()
        # print('Robot bearing: ', str(self.handler.robot.bearing))
        if self.check_left():
            self.handler.left()
            self.sense()
            if self.check_front() > 0:
                self.handler.move(steps = 1)
        else:
            steps = self.check_front()

            if steps > 0:
                self.handler.move(steps=1)
                print(steps)
            else:
                self.handler.right()
                self.sense()
                if self.check_front() > 0:
                    self.handler.move(steps=1)

        # self.handler.simulator.root.after(500, self.periodic_check)

    def sense(self):
        sensor_data = self.handler.robot.receive()
        location = self.handler.robot.get_location()
        bearing = self.handler.robot.bearing

        print(sensor_data)

        if bearing == Bearing.NORTH:
            for i in range(3):
                self.update_map(location[0] + i - 1, location[1] - 1, sensor_data[i], Bearing.NORTH,
                                                     config.sensor_range['front_middle'])
            self.update_map(location[0] - 1, location[1] - 1, sensor_data[3], Bearing.WEST, config.sensor_range['left'])
            self.update_map(location[0] + 1, location[1], sensor_data[4], bearing.EAST, config.sensor_range['right'])

        elif bearing == Bearing.EAST:
            for i in range(3):
                self.update_map(location[0] + 1, location[1] + i - 1, sensor_data[i], Bearing.EAST,
                                                     config.sensor_range['front_middle'])
            self.update_map(location[0] + 1, location[1] - 1, sensor_data[3], Bearing.NORTH,
                                                 config.sensor_range['left'])
            self.update_map(location[0], location[1] + 1, sensor_data[4], bearing.SOUTH,
                                                 config.sensor_range['right'])

        elif bearing == Bearing.SOUTH:
            for i in range(3):
                self.update_map(location[0] - i + 1, location[1] + 1, sensor_data[i], Bearing.SOUTH,
                                                     config.sensor_range['front_middle'])
            self.update_map(location[0] + 1, location[1] + 1, sensor_data[3], Bearing.EAST,
                                                 config.sensor_range['left'])
            self.update_map(location[0] - 1, location[1], sensor_data[4], bearing.WEST,
                                                 config.sensor_range['right'])

        else:
            for i in range(3):
                self.update_map(location[0] - 1, location[1] - i + 1, sensor_data[i], Bearing.WEST,
                                                     config.sensor_range['front_middle'])
            self.update_map(location[0] - 1, location[1] + 1, sensor_data[3], Bearing.SOUTH,
                                                 config.sensor_range['left'])
            self.update_map(location[0], location[1] - 1, sensor_data[4], bearing.NORTH,
                                                 config.sensor_range['right'])


    def update_map(self, x, y, dis, bearing, sensor_range):

        if bearing == Bearing.NORTH:
            for i in range(dis):
                self.update_and_render(x , y - i - 1 , 1 , 0)
            if(dis < sensor_range and self.map.valid_range(y - dis - 1, x)):
                self.update_and_render(x, y - dis - 1, 1, 1)

        elif bearing == Bearing.EAST:
            for i in range(dis):
                self.update_and_render(x + i + 1 , y, 1, 0)
            if(dis < sensor_range and self.map.valid_range(y, x + dis + 1)):
                self.update_and_render(x + dis + 1, y, 1, 1)

        elif bearing == Bearing.SOUTH:
            for i in range(dis):
                self.update_and_render(x, y + i + 1, 1, 0)

            if(dis < sensor_range and self.map.valid_range(y + dis + 1, x )):
                self.update_and_render(x, y + dis + 1, 1, 1)

        else:
            for i in range(dis):
                self.update_and_render(x - i - 1, y, 1, 0)
            if(dis < sensor_range and self.map.valid_range(y, x - dis - 1)):
                self.update_and_render(x - dis - 1, y, 1, 1)

    def update_and_render(self, x , y , is_explore, is_obstacle):
        self.map.mark_explored(x , y , is_explore , is_obstacle)
        self.handler.simulator.update_cell(x , y)

    def findSP(self):
        pass

    def run(self):
        pass

    def check_left(self):
        robot_x, robot_y = self.handler.robot.get_location()

        offsets = [
            [[-1, 0, 1], [-2, -2, -2]],
            [[2, 2, 2], [-1, 0, 1]],
            [[-1, 0, 1], [2, 2, 2]],
            [[-2, -2, -2], [-1, 0, 1]]
        ]
        is_wall = [
            robot_y < 2,
            robot_x >= (config.map_size['width'] - 2),
            robot_y >= (config.map_size['height'] - 2),
            robot_x < 2
        ]

        bearing = self.handler.robot.get_left_bearing()
        offset = offsets[bearing]

        if is_wall[bearing]:
            return False

        if self.map.is_free(robot_x + offset[0][0], robot_y + offset[1][0], sim=False) and \
                self.map.is_free(robot_x + offset[0][1], robot_y + offset[1][1], sim=False) and \
                self.map.is_free(robot_x + offset[0][2], robot_y + offset[1][2], sim=False):
            return True

        # if left_bearing == Bearing.NORTH:
        #     if robot_y < 2:
        #         return False
        #
        #     if self.map.is_free(robot_y - 2, robot_x - 1) and \
        #             self.map.is_free(robot_y - 2, robot_x + 0) and \
        #             self.map.is_free(robot_y - 2, robot_x + 1):
        #         return True
        #
        #     return False
        #
        # elif left_bearing == Bearing.EAST:
        #     if robot_x > (config.map_size['width'] - 2):
        #         return False
        #
        #     if self.map.is_free(robot_y - 1, robot_x + 2) and \
        #             self.map.is_free(robot_y + 0, robot_x + 2) and \
        #             self.map.is_free(robot_y + 1, robot_x + 2):
        #         return True
        #
        #     return False
        #
        # elif left_bearing == Bearing.SOUTH:
        #     if robot_y > (config.map_size['height'] - 2):
        #         return False
        #
        #     if self.map.is_free(robot_y + 2, robot_x - 1) and \
        #             self.map.is_free(robot_y + 2, robot_x + 0) and \
        #             self.map.is_free(robot_y + 2, robot_x + 1):
        #         return True
        #
        #     return False
        #
        # elif left_bearing == Bearing.WEST:
        #     if robot_x < 2:
        #         return False
        #
        #     if self.map.is_free(robot_y - 1, robot_x - 2) and \
        #             self.map.is_free(robot_y + 0, robot_x - 2) and \
        #             self.map.is_free(robot_y + 1, robot_x - 2):
        #         return True
        #
        #     return False
        #
        # else:
        #     print("[Error] Invalid direction.")
        return False

    def check_front(self):
        sensor_data = self.handler.robot.receive()

        if (sensor_data[0] == 0) and (sensor_data[1] == 0) and (sensor_data[2] == 0):
            return 0

        return min(sensor_data[:3])
