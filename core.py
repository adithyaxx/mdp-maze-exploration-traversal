import time

import config
from FastestPathAlgo import FastestPathAlgo
from constants import Bearing


class Core:
    def __init__(self, handler):
        self.handler = handler
        self.map = self.handler.map
        self.algo = FastestPathAlgo(self.map, self.handler.robot, self.handler)
        self.steps_per_second = -1
        self.coverage = 100
        self.time_limit = 3600
        self.start = 0

    def explore(self, steps_per_second, coverage, time_limit):
        self.steps_per_second = steps_per_second
        self.coverage = coverage
        self.time_limit = time_limit
        self.start = time.time()
        self.periodic_check()

    def periodic_check(self):
        current = time.time()
        elapsed = current - self.start

        if elapsed >= self.time_limit or self.map.get_coverage() >= self.coverage:
            explored_hex, obstacles_hex = self.map.get_map_descriptor()
            self.handler.simulator.text_area.insert('end', explored_hex, '\n\n')
            self.handler.simulator.text_area.insert('end', obstacles_hex, '\n')
            return

        if self.handler.robot.get_location() == (1, 18) and self.handler.robot.bearing == Bearing.WEST:
            self.handler.right()
            explored_hex, obstacles_hex = self.map.get_map_descriptor()
            self.handler.simulator.text_area.insert('end', explored_hex + '\n\n')
            self.handler.simulator.text_area.insert('end', obstacles_hex + '\n\n')
            return

        self.sense()
        # Turn left and move forward if left is free
        if self.check_left():
            self.handler.left()
            self.sense()
            steps = self.check_front()
            if steps > 0:
                self.handler.move(steps=1)
        else:
            steps = self.check_front()

            # Move forward if front is free
            if steps > 0:
                # Move forward by 1 step only if front left is free
                # if self.check_top_left():
                #     self.handler.move(steps=1)
                # else:
                #     self.handler.move(steps=steps)
                #     self.sense(steps - 1)
                #     self.handler.simulator.update_map(radius=5)

                self.handler.move(steps=1)
            else:
                self.handler.right()
                self.sense()
                steps = self.check_front()
                if steps > 0:
                    self.handler.move(steps=1)

        if self.steps_per_second == -1:
            delay = 10
        else:
            delay = 1000 // self.steps_per_second

        self.handler.simulator.job = self.handler.simulator.root.after(delay, self.periodic_check)

    def sense(self, backtrack=0):
        self.handler.robot.sense(backtrack)

    def findFP(self, goal_x, goal_y, waypoint_x, waypoint_y, diagonal):
        if self.steps_per_second == -1:
            delay = 10
        else:
            delay = 1000 // self.steps_per_second
        self.algo.find_fastest_path(diag= diagonal, delay = delay, goalX=goal_x, goalY=goal_y, waypointX=waypoint_x, waypointY=waypoint_y)

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
        offset = offsets[int(bearing/2)]

        if is_wall[int(bearing/2)]:
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

    def check_top_left(self):
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
        offset = offsets[int(bearing/2)]

        if is_wall[int(bearing/2)]:
            return False

        if self.map.is_free(robot_x + offset[0][2], robot_y + offset[1][2], sim=False):
            return True

        return False

    def check_front(self):
        sensor_data = self.handler.robot.receive()

        if (sensor_data[0] == 0) and (sensor_data[1] == 0) and (sensor_data[2] == 0):
            return 0

        return min(sensor_data[:3])
