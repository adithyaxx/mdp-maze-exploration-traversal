import time

import config
from fastest_path_algo import FastestPathAlgo
from visibility_graph import VisibilityGraph
from constants import Bearing, MOVEMENT
from  a_star import  A_Star

class STATUS:
    LEFT_WALL_HUGGING = "Left Wall Hugging",
    SPELUNKING1 = "Spelunking 1",
    SPELUNKING2 = "Spelunking 2",
    RETURN_HOME = "Return Home"


class Core:
    def __init__(self, handler):
        self.handler = handler
        self.map = self.handler.map
        # self.algo = VisibilityGraph(self.map, self.handler.robot, self.handler)
        self.algo = FastestPathAlgo(self.map, self.handler.robot, self.handler)
        self.steps_per_second = -1
        self.coverage = 100
        self.time_limit = 3600
        self.start = 0
        self.movements = []
        self.status = STATUS.LEFT_WALL_HUGGING


    def reset(self):
        self.status = STATUS.LEFT_WALL_HUGGING

    def explore(self, steps_per_second, coverage, time_limit, return_home):
        self.steps_per_second = steps_per_second
        self.coverage = coverage
        self.time_limit = time_limit
        self.start = time.time()
        self.return_home = return_home
        self.periodic_check()


    def periodic_check(self):
        current = time.time()
        elapsed = current - self.start

        # print(self.status)

        if elapsed >= self.time_limit or ( self.map.get_coverage() >= self.coverage and not self.return_home ) or \
                (self.return_home and self.map.get_coverage() >= self.coverage and self.handler.robot.get_location() == (1, 18)) or \
                self.status == STATUS.RETURN_HOME and self.handler.robot.get_location() == (1, 18):
                # (not self.return_home and self.handler.robot.get_location() == (1, 18) and self.handler.robot.bearing == Bearing.WEST):
            explored_hex, obstacles_hex = self.map.get_map_descriptor()
            self.handler.simulator.text_area.insert('end', explored_hex, '\n\n')
            self.handler.simulator.text_area.insert('end', obstacles_hex, '\n')
            return

        if self.handler.robot.get_location() == (1, 18) and self.handler.robot.bearing == Bearing.WEST and self.status == STATUS.LEFT_WALL_HUGGING:
            self.spelunkprep()
            self.status = STATUS.SPELUNKING1

        if self.status != STATUS.RETURN_HOME and self.handler.robot.get_location() != (1, 18) and self.map.get_coverage() >= self.coverage:
            self.go_home()

        if self.status == STATUS.LEFT_WALL_HUGGING:
            self.left_wall_hugging()
        else:
            if len(self.movements) <= 0:
                self.spelunkprep()
                if len(self.movements) <= 0:
                    self.go_home()

            self.execute_algo_move()
            if self.status == STATUS.SPELUNKING1 or self.status == STATUS.SPELUNKING2:
                self.sense()


        if self.steps_per_second == -1:
            delay = 10
        else:
            delay = 1000 // self.steps_per_second

        self.handler.simulator.job = self.handler.simulator.root.after(delay, self.periodic_check)
        # print(self.status)


    def left_wall_hugging(self):
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



    def sense(self, backtrack=0):
        self.handler.robot.sense(backtrack)

    def findFP(self, goal_x, goal_y, waypoint_x, waypoint_y, diagonal, steps_per_second):
        self.steps_per_second = steps_per_second
        if self.steps_per_second == -1:
            delay = 10
        else:
            delay = 1000 // self.steps_per_second
        # self.algo.find_fastest_path()
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


    def spelunkprep(self):
        result, dir = self.get_spelunk_target()

        if result is None:
            if self.status == STATUS.SPELUNKING1:
                print("Attempt 2: Spelunkprep")
                self.status = STATUS.SPELUNKING2
                result, dir = self.get_spelunk_target()

            if result is None:
                print("Warning: Unable to reach unexplored tile. Ending Exploration early.")
                # self.status = STATUS.RETURN_HOME
                return


        self.movements = self.algo.find_fastest_path(diag = False , delay = 0, goalX = result[0], goalY = result[1], waypointX = 0, waypointY = 0, \
                                    startX = self.handler.robot.get_location()[0], startY = self.handler.robot.get_location()[1], sim = False)
        if dir != None:
            self.add_bearing(dir)



    def get_spelunk_target(self):
        unexplored_grids = self.map.get_unexplored_grids()
        result = None
        dir = None
        while (result == None and len(unexplored_grids) > 0):
            unknown_grid = unexplored_grids.pop(0)
            # print("[CORE] Unknown grid: ", unknown_grid[0], unknown_grid[1])
            if self.status == STATUS.SPELUNKING1 or self.status == STATUS.LEFT_WALL_HUGGING:
                result = self.map.find_adjacent_free_space(unknown_grid[0], unknown_grid[1])
            else:
                try:
                    result, dir = self.map.find_adjacent_free_space_front(unknown_grid[0], unknown_grid[1])
                    self.add_bearing(dir)
                except:
                    pass
        return result, dir


    def execute_algo_move(self):

        next_move = self.movements.pop(0)
        if (next_move == MOVEMENT.LEFT):
            self.handler.left()
        elif (next_move == MOVEMENT.RIGHT):
            self.handler.right()
        elif (next_move == MOVEMENT.LEFT_DIAG):
            self.handler.left_diag()
        elif (next_move == MOVEMENT.RIGHT_DIAG):
            self.handler.right_diag()
        elif (next_move == MOVEMENT.FORWARD_DIAG):
            self.handler.move_diag()
        else:
            self.handler.move(1)

    def go_home(self):
        self.movements.clear()
        self.movements = self.algo.find_fastest_path(diag = True , delay = 0, goalX = 1, goalY = 18, waypointX = 0, waypointY = 0, \
                                    startX = self.handler.robot.get_location()[0], startY = self.handler.robot.get_location()[1], sim = False)
        # print(self.movements)
        self.status = STATUS.RETURN_HOME


    def add_bearing(self, dir):
        cur_dir = self.handler.robot.bearing
        for m in self.movements:
            if(m == MOVEMENT.LEFT):
                cur_dir = Bearing.prev_bearing(cur_dir)
            elif(m == MOVEMENT.RIGHT):
                cur_dir = Bearing.next_bearing(cur_dir)

        if cur_dir == dir:
            return

        if dir == Bearing.NORTH:
            if cur_dir == Bearing.WEST:
                self.movements.append(MOVEMENT.LEFT)
            elif cur_dir == Bearing.EAST:
                self.movements.append(MOVEMENT.RIGHT)
            else:
                self.movements.append(MOVEMENT.RIGHT)
                self.movements.append(MOVEMENT.RIGHT)

        elif dir == Bearing.SOUTH:
            if cur_dir == Bearing.WEST:
                self.movements.append(MOVEMENT.RIGHT)
            elif cur_dir == Bearing.EAST:
                self.movements.append(MOVEMENT.LEFT)
            else:
                self.movements.append(MOVEMENT.RIGHT)
                self.movements.append(MOVEMENT.RIGHT)

        elif dir == Bearing.EAST:
            if cur_dir == Bearing.NORTH:
                self.movements.append(MOVEMENT.LEFT)
            elif cur_dir == Bearing.SOUTH:
                self.movements.append(MOVEMENT.RIGHT)
            else:
                self.movements.append(MOVEMENT.RIGHT)
                self.movements.append(MOVEMENT.RIGHT)

        elif dir == Bearing.WEST:
            if cur_dir == Bearing.SOUTH:
                self.movements.append(MOVEMENT.LEFT)
            elif cur_dir == Bearing.NORTH:
                self.movements.append(MOVEMENT.RIGHT)
            else:
                self.movements.append(MOVEMENT.RIGHT)
                self.movements.append(MOVEMENT.RIGHT)

        else:
            # print(cur_dir, dir)
            print("Warning invalid direction")
        # print(self.movements)