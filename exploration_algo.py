import time

import config
from constants import Bearing, MOVEMENT
from map import *


class STATUS:
    LEFT_WALL_HUGGING = "Left Wall Hugging",
    SPELUNKING = "Spelunking",  # use front sensors
    RETURN_HOME = "Return Home",
    IMAGE_REC = "Image Rec"  # left wall hugging for image rec


"""
x: unexplored grid
o: robot target
SPELUNKING 
 _ _ _ _ _ _ _ _ _ _
|_|_|_|_|_|_|_|_|_|_|
|_|_|_|_|o|o|o|_|_|_|
|_|_|_|o|_|_|_|o|_|_|
|_|_|_|o|_|x|_|o|_|_|
|_|_|_|o|_|_|_|o|_|_|
|_|_|_|_|o|o|o|_|_|_|
|_|_|_|_|_|_|_|_|_|_|
"""


class ExplorationAlgo:
    def __init__(self, handler, path_finder):
        self.handler = handler
        self.map = self.handler.map
        self.path_finder = path_finder
        self.steps_per_second = -1
        self.coverage = 100
        self.time_limit = 3600
        self.start = 0
        self.movements = []
        self.status = STATUS.LEFT_WALL_HUGGING
        self.do_img_rec = False
        self.start_pos = (0, 0)
        self.max_move = 999
        self.start_pos = (0, 0)
        self.optimized = True

    def reset(self):
        self.status = STATUS.LEFT_WALL_HUGGING
        self.movements.clear()
        self.start_pos = (0, 0)
        # for i in range(config.map_size['height']):
        #     for j in range(config.map_size['width']):
        #         self.map_img_rec[i][j] = 0

    def explore(self, delay, steps_per_second, coverage, time_limit, return_home, perform_fp=False):
        self.delay = delay
        self.steps_per_second = steps_per_second
        self.coverage = coverage
        self.time_limit = time_limit
        self.start = time.time()
        self.return_home = return_home
        self.perform_fp = perform_fp
        self.periodic_check()

    def periodic_check(self):
        current = time.time()
        elapsed = current - self.start

        if self.perform_fp:
            if self.handler.robot.x == 13 and self.handler.robot.y == 1:
                return
        else:
            if elapsed >= self.time_limit or (
                    self.status != STATUS.IMAGE_REC and self.map.get_coverage() >= self.coverage and \
                    (not self.return_home or (self.return_home and self.handler.robot.get_location() == (1, 18)))) or \
                    (self.status == STATUS.RETURN_HOME and self.handler.robot.get_location() == (1, 18)) or \
                    (self.status == STATUS.IMAGE_REC and sum(sum(self.handler.robot.map_img_rec, [])) == config.map_size[
                        'height'] *
                     config.map_size['width'] and \
                     list(self.handler.robot.get_location()) == list(self.start_pos) and not self.return_home):
                if self.return_home and self.handler.robot.get_location() == (1, 18):
                    self.reach_start()
                explored_hex, obstacles_hex = self.map.create_map_descriptor()
                self.handler.simulator.text_area.insert('end', explored_hex, '\n\n')
                self.handler.simulator.text_area.insert('end', obstacles_hex, '\n')
                # for p in self.map_img_rec:
                #     print(p)
                return

        # print(self.status,self.handler.robot.get_location(),  self.start_pos)
        if self.status == STATUS.IMAGE_REC:
            if (self.handler.robot.get_location() == (1, 18) and self.handler.robot.bearing == Bearing.WEST) or \
                    list(self.handler.robot.get_location()) == list(self.start_pos):
                # print("restarting")
                self.get_image_rec_target()
                self.spelunkprep()
                if self.temp_pos == None:
                    print("Image Rec completed. Going Home")
                    self.go_home()
            elif self.start_pos == (-1, -1) and len(self.movements) == 0:
                self.update_start_pos()

        #  if exploration is still incomplete after left wall hugging, try explore unknown grids using spenlunking
        elif self.status == STATUS.LEFT_WALL_HUGGING and self.handler.robot.get_location() == (
                1, 18) and self.handler.robot.bearing == Bearing.WEST:
            self.status = STATUS.SPELUNKING
            self.movements.clear()
            self.spelunkprep()

        #  send robot back to the start when exploration coverage reached
        elif self.map.get_coverage() >= self.coverage and self.return_home and self.handler.robot.get_location() != (
                1, 18) and \
                self.status != STATUS.RETURN_HOME:
            self.go_home()

        if self.status == STATUS.IMAGE_REC:
            self.left_wall_hugging()

        elif self.status == STATUS.LEFT_WALL_HUGGING:
            self.left_wall_hugging()
        else:
            if len(self.movements) <= 0:
                print("here")
                self.spelunkprep()
                if len(self.movements) <= 0:
                    if self.return_home:
                        self.go_home()

            if self.status == STATUS.SPELUNKING:
                self.move_and_sense()
            else:
                # print("Current Status: ", self.status)
                # for i in self.handler.robot.map_img_rec:
                #     print(i)
                self.move_and_sense(sense=True)

        self.handler.simulator.job = self.handler.simulator.root.after(self.delay, self.periodic_check)

    def left_wall_hugging(self):
        # self.sense()
        if len(self.movements) > 0:
            self.move_and_sense()
            return

        left_front, left_middle, left_back = self.check_left()
        if not left_front:
            steps = self.check_front()
            if steps > 0:
                for _ in range(min(steps, self.max_move)):
                    self.movements.append(MOVEMENT.FORWARD)
            else:
                self.movements.append(MOVEMENT.RIGHT)
        else:
            if left_middle and left_back:
                self.movements.append(MOVEMENT.LEFT)
                self.movements.append(MOVEMENT.FORWARD)
            else:
                steps = self.check_front()
                if steps > 0:
                    if not left_middle:
                        self.movements.append(MOVEMENT.FORWARD)
                    self.movements.append(MOVEMENT.FORWARD)
                else:
                    self.movements.append(MOVEMENT.RIGHT)
        self.move_and_sense()

    def move_and_sense(self, sense=True):
        ir = (self.status == STATUS.IMAGE_REC)
        if self.optimized:
            num_move = 1

            robot_x, robot_y = self.handler.robot.get_location()
            robot_bearing = self.handler.robot.bearing

            if self.movements[0] == MOVEMENT.FORWARD:
                if self.status == STATUS.IMAGE_REC:
                    robot_x, robot_y = self.simulate_move(robot_x, robot_y, robot_bearing)
                if [robot_x, robot_y] != list(self.start_pos) and len(self.movements) > 1 and self.movements[
                    1] == MOVEMENT.FORWARD:
                    num_move += 1
                    if self.status == STATUS.IMAGE_REC:
                        robot_x, robot_y = self.simulate_move(robot_x, robot_y, robot_bearing)
                    if [robot_x, robot_y] != list(self.start_pos) and len(self.movements) > 2 and self.movements[
                        2] == MOVEMENT.FORWARD:
                        num_move += 1

            self.execute_algo_move(num_move=num_move, sense=sense, ir=ir)
            # for _ in range(num_move):
            #     self.execute_algo_move()
            #     if sense:
            #         self.sense()
        else:
            self.execute_algo_move(num_move=1, sense=sense, ir=ir)
            # if sense:
            #     self.sense()
        # if self.status == STATUS.IMAGE_REC:
        #     self.take_image()

    # def take_image(self):
    #     robot_x, robot_y = self.handler.robot.get_location()
    #     robot_bearing = self.handler.robot.bearing
    #     for i in range(3):
    #         for j in range(3):
    #             if self.map.valid_range(robot_y + i - 1, robot_x + j - 1):
    #                 self.map_img_rec[robot_y + i - 1][robot_x + j - 1] = 1
    #     if robot_x < 2 and robot_bearing == Bearing.NORTH:
    #         return
    #     if robot_y < 2 and robot_bearing == Bearing.EAST:
    #         return
    #     if robot_x > config.map_size['width'] - 3 and robot_bearing == Bearing.SOUTH:
    #         return
    #     if robot_y > config.map_size['height'] - 3 and robot_bearing == Bearing.WEST:
    #         return
    #
    #     img_target = [
    #         [[robot_x - 2, robot_y - 1], [robot_x - 2, robot_y], [robot_x - 2, robot_y + 1]],
    #         [[robot_x + 1, robot_y - 2], [robot_x, robot_y - 2], [robot_x - 1, robot_y - 2]],
    #         [[robot_x + 2, robot_y + 1], [robot_x + 2, robot_y], [robot_x + 2, robot_y - 1]],
    #         [[robot_x - 1, robot_y + 2], [robot_x, robot_y + 2], [robot_x + 1, robot_y + 2]]
    #     ]
    #     img_pos = img_target[int(robot_bearing // 2)]
    #
    #     if self.map.valid_range(img_pos[1][1], img_pos[1][0]) and (
    #             self.map.is_obstacle(img_pos[0][0], img_pos[0][1], False) or \
    #             self.map.is_obstacle(img_pos[1][0], img_pos[1][1], False) or self.map.is_obstacle(img_pos[2][0],
    #                                                                                               img_pos[2][1],
    #                                                                                               False)):
    #         # print(robot_bearing)
    #         print("[EXPLORATION] Image taken at {}, {}".format(img_pos[0][0], img_pos[0][1]))  # take photo command
    #         print("[EXPLORATION] Image taken at {}, {}".format(img_pos[1][0], img_pos[1][1]))  # take photo command
    #         print("[EXPLORATION] Image taken at {}, {}".format(img_pos[2][0], img_pos[2][1]))  # take photo command
    #         self.map_img_rec[img_pos[0][1]][img_pos[0][0]] = 1
    #         self.map_img_rec[img_pos[1][1]][img_pos[1][0]] = 1
    #         self.map_img_rec[img_pos[2][1]][img_pos[2][0]] = 1

    def sense(self, backtrack=0):
        # print("[EXPLORATION] sense")
        self.handler.robot.sense(backtrack)
        # if self.status == STATUS.IMAGE_REC:
        #     self.take_image()

    def check_left(self):
        robot_x, robot_y = self.handler.robot.get_location()

        offsets = [
            [[1, 0, -1], [-2, -2, -2]],
            [[2, 2, 2], [1, 0, -1]],
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
        offset = offsets[int(bearing / 2)]

        if is_wall[int(bearing / 2)]:
            return 0, 0, 0

        return self.map.is_free(robot_x + offset[0][0], robot_y + offset[1][0], sim=False), \
               self.map.is_free(robot_x + offset[0][1], robot_y + offset[1][1], sim=False), \
               self.map.is_free(robot_x + offset[0][2], robot_y + offset[1][2], sim=False)

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
        offset = offsets[int(bearing / 2)]

        if is_wall[int(bearing / 2)]:
            return False

        if self.map.is_free(robot_x + offset[0][2], robot_y + offset[1][2], sim=False):
            return True

        return False

    def check_front(self):
        sensor_data = self.handler.robot.check_front()

        if (sensor_data[0] == 0) and (sensor_data[1] == 0) and (sensor_data[2] == 0):
            return 0

        return min(sensor_data[:3])

    def spelunkprep(self):
        if self.status == STATUS.IMAGE_REC:
            result, dir = self.get_image_rec_target()
            print("Getting image rec target")
            print("Target: ", result)
            self.start_pos = (-1, -1)
            self.temp_pos = result
            # print("new start pos" ,self.temp_pos)
        else:
            result, dir = self.get_spelunk_target()

        if result is None:
            print("Warning: Unable to reach unexplored tile. Ending Exploration early.")
            for i in self.handler.robot.map_img_rec:
                print(i)

            return
        self.movements = self.path_finder.find_fastest_path(diag=False, delay=0, goalX=result[0], goalY=result[1],
                                                            waypointX=0,
                                                            waypointY=0,
                                                            startX=self.handler.robot.get_location()[0],
                                                            startY=self.handler.robot.get_location()[1], sim=False)
        if self.status == STATUS.IMAGE_REC:
            dir = Bearing.next_bearing(dir)

        self.add_bearing(dir)

    def get_image_rec_target(self):
        try:
            explored = []
            unexplored = []
            result = None
            dir = None
            for i in range(config.map_size['height']):
                for j in range(config.map_size['width']):
                    if self.handler.robot.map_img_rec[config.map_size['height'] - i - 1][j] == 0:
                        if self.map.is_explored(j, config.map_size['height'] - i - 1) == 1:
                            if self.map.is_obstacle(j, config.map_size['height'] - i - 1, sim=False):
                                explored.append((j, config.map_size['height'] - i - 1))
                                print((j, config.map_size['height'] - i - 1))
                        else:
                            unexplored.append((j, config.map_size['height'] - i - 1))
                            print((j, config.map_size['height'] - i - 1))

            while result == None and len(explored) > 0:
                obs = explored.pop(0)
                try:
                    result, dir = self.map.find_adjacent_free_space_front(obs[0], obs[1])
                except:
                    print("No explored target for image rec")
            print("Explored results: ", result)

            while result == None and len(unexplored) > 0:
                obs = unexplored.pop(0)
                try:
                    result, dir = self.map.find_adjacent_free_space_front(obs[0], obs[1])
                except:
                    print("No unexplored target for image rec")
            print("Unexplored results: ", result)

            # for p in self.map_img_rec:
            #     print(p)
            # print("\n")
            return result, dir
        except IndexError:
            pass

    def get_spelunk_target(self):
        unexplored_grids = self.map.get_unexplored_grids()
        result = None
        dir = None
        while result == None and len(unexplored_grids) > 0:
            unknown_grid = unexplored_grids.pop(0)
            # print("[CORE] Unknown grid: ", unknown_grid[0], unknown_grid[1])
            try:
                result, dir = self.map.find_adjacent_free_space_front(unknown_grid[0], unknown_grid[1])
                self.add_bearing(dir)
            except:
                pass
        return result, dir

    def execute_algo_move(self, sense, ir, num_move=1):
        try:
            for _ in range(num_move):
                next_move = self.movements.pop(0)

            if (next_move == MOVEMENT.LEFT):
                self.handler.left(sense, ir)
            elif (next_move == MOVEMENT.RIGHT):
                self.handler.right(sense, ir)
            elif (next_move == MOVEMENT.LEFT_DIAG):
                self.handler.left_diag()
            elif (next_move == MOVEMENT.RIGHT_DIAG):
                self.handler.right_diag()
            elif (next_move == MOVEMENT.FORWARD_DIAG):
                self.handler.move_diag()
            else:
                self.handler.move(sense=sense, ir=ir, steps=num_move)
        except:
            print("IR no obstacle in the middle")

    def go_home(self):

        self.movements.clear()
        self.movements = self.path_finder.find_fastest_path(diag=False, delay=0, goalX=1, goalY=18, waypointX=0,
                                                            waypointY=0, \
                                                            startX=self.handler.robot.get_location()[0],
                                                            startY=self.handler.robot.get_location()[1], sim=False)
        print("Going Home from {}, len movements: {}".format(self.handler.robot.get_location(), len(self.movements)))
        self.status = STATUS.RETURN_HOME

    def add_bearing(self, dir):
        cur_dir = self.handler.robot.bearing
        for m in self.movements:
            if (m == MOVEMENT.LEFT):
                cur_dir = Bearing.prev_bearing(cur_dir)
            elif (m == MOVEMENT.RIGHT):
                cur_dir = Bearing.next_bearing(cur_dir)

        if cur_dir == dir:
            return

        if cur_dir == Bearing.NORTH:
            if dir == Bearing.WEST:
                self.movements.append(MOVEMENT.LEFT)
            elif dir == Bearing.EAST:
                self.movements.append(MOVEMENT.RIGHT)
            else:
                self.movements.append(MOVEMENT.RIGHT)
                self.movements.append(MOVEMENT.RIGHT)

        elif cur_dir == Bearing.SOUTH:
            if dir == Bearing.WEST:
                self.movements.append(MOVEMENT.RIGHT)
            elif dir == Bearing.EAST:
                self.movements.append(MOVEMENT.LEFT)
            else:
                self.movements.append(MOVEMENT.RIGHT)
                self.movements.append(MOVEMENT.RIGHT)

        elif cur_dir == Bearing.EAST:
            if dir == Bearing.NORTH:
                self.movements.append(MOVEMENT.LEFT)
            elif dir == Bearing.SOUTH:
                self.movements.append(MOVEMENT.RIGHT)
            else:
                self.movements.append(MOVEMENT.RIGHT)
                self.movements.append(MOVEMENT.RIGHT)

        elif cur_dir == Bearing.WEST:
            if dir == Bearing.SOUTH:
                self.movements.append(MOVEMENT.LEFT)
            elif dir == Bearing.NORTH:
                self.movements.append(MOVEMENT.RIGHT)
            else:
                self.movements.append(MOVEMENT.RIGHT)
                self.movements.append(MOVEMENT.RIGHT)

        else:
            print("Warning invalid direction")

    def set_status(self, do_img_rec):
        if do_img_rec:
            self.status = STATUS.IMAGE_REC
            self.max_move = 3
            self.set_optimized(False)
            # self.set_optimized(True)
        else:
            self.status = STATUS.LEFT_WALL_HUGGING
            self.max_move = 999

    def update_start_pos(self):
        self.start_pos = self.temp_pos

    def set_optimized(self, opt):
        self.optimized = opt

    def simulate_move(self, robot_x, robot_y, robot_bearing):
        if robot_bearing == Bearing.NORTH:
            robot_y -= 1
        elif robot_bearing == Bearing.EAST:
            robot_x += 1
        elif robot_bearing == Bearing.SOUTH:
            robot_y += 1
        else:
            robot_x -= 1
        return robot_x, robot_y

    # def simulate_left(self, bearing):
    #     return Bearing.prev_bearing(bearing)
    #
    # def simulate_right(self, bearing):
    #     return Bearing.next_bearing(bearing)
    #

    # def get_unexplored_grids(self):
    #     robot_x, robot_y = self.handler.robot.get_location()
    #     unexplored_grids = []
    #     for i in range(config.map_size['height']):
    #         for k in range(robot_x - i, robot_x + i, 1):
    #              for j in range(robot_y - i, robot_y + i):
    #                 if (self.map.valid_range(j, k) and self.map.map_is_explored[j][k] == 0):
    #                     unexplored_grids.append((k, j))
    #     return unexplored_grids

    def reach_start(self):
        robot_bearing = self.handler.robot.bearing
        if robot_bearing == Bearing.NORTH:
            return
        elif robot_bearing == Bearing.EAST:
            self.movements.append(MOVEMENT.LEFT)
        elif robot_bearing == Bearing.SOUTH:
            self.movements.append(MOVEMENT.RIGHT)
            self.movements.append(MOVEMENT.RIGHT)
        elif robot_bearing == Bearing.WEST:
            self.movements.append(MOVEMENT.RIGHT)
        elif robot_bearing == Bearing.NORTH_EAST:
            self.movements.append(MOVEMENT.LEFT_DIAG)
        elif robot_bearing == Bearing.SOUTH_EAST:
            self.movements.append(MOVEMENT.LEFT_DIAG)
            self.movements.append(MOVEMENT.LEFT)
        elif robot_bearing == Bearing.SOUTH_WEST:
            self.movements.append(MOVEMENT.RIGHT_DIAG)
            self.movements.append(MOVEMENT.RIGHT)
        elif robot_bearing == Bearing.NORTH_WEST:
            self.movements.append(MOVEMENT.RIGHT_DIAG)
        else:
            print("[EXPLORATION] Reached start: invalid direction")

        for _ in range(len(self.movements)):
            self.execute_algo_move(sense=False, ir=False, num_move=1)
