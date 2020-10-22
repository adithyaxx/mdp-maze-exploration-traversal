import time

import config
import numpy as np
from constants import Bearing, MOVEMENT
from map import *
import logging

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
        self.time_limit = 360
        self.start = 0
        self.movements = []
        self.status = STATUS.LEFT_WALL_HUGGING
        # self.do_img_rec = False
        self.start_pos = (0, 0)
        self.max_move = 999
        self.start_pos = (0, 0)
        self.optimized = True
        self.ir_completed = False
        self.start_time = 0
        self.partial_ir = False
        self.completed_partial_exploration = False
        self.consecutive_left_turn = 0

    def reset(self):
        self.handler.robot.update_map = True
        self.status = STATUS.LEFT_WALL_HUGGING
        self.movements.clear()
        self.start_pos = (0, 0)
        self.ir_completed = False
        self.partial_ir = False
        self.count = 0
        self.consecutive_left_turn = 0
        self.completed_partial_exploration = False
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
        # logging.debug("[Exploration] Periodic Check")
        current = time.time()
        elapsed = current - self.start

        if self.map.get_coverage() >= self.coverage and self.handler.robot.update_map:
            self.handler.robot.update_map = False
        if self.perform_fp:
            if self.handler.robot.x == 13 and self.handler.robot.y == 1:
                return
        else:
            # logging.debug("Elapsed: ", elapsed)
            if elapsed >= self.time_limit or \
 \
                    (self.status != STATUS.IMAGE_REC and self.map.get_coverage() >= self.coverage and (
                            not self.return_home or (
                            self.return_home and self.handler.robot.get_location() == (1, 18)))) or \
 \
                    (self.status == STATUS.RETURN_HOME and self.handler.robot.get_location() == (1, 18)) or \
 \
                    (self.status == STATUS.IMAGE_REC and sum(sum(self.handler.robot.map_img_rec, [])) ==
                     config.map_size[
                         'height'] *
                     config.map_size['width'] and
                     list(self.handler.robot.get_location()) == list(self.start_pos) and not self.return_home):
                explored_hex, obstacles_hex = self.map.create_map_descriptor()
                self.handler.simulator.text_area.insert('end', explored_hex, '\n\n')
                self.handler.simulator.text_area.insert('end', obstacles_hex, '\n')
                if self.status == STATUS.IMAGE_REC:
                    self.handler.robot.signal_exploration_ended()
                if self.return_home and self.handler.robot.get_location() == (1, 18):
                    # time.sleep(7)
                    self.reach_start()
                self.handler.robot.calibrate()
                return

        # if self.count == 300:
        #     self.stop_ir()
        # self.count += 1
        # logging.debug("Status: ", self.status, self.count)

        if self.status == STATUS.IMAGE_REC:
            if self.ir_completed or elapsed >= 360:
                self.handler.robot.signal_exploration_ended()
                # m = np.multiply(map_partial_explored, map_is_explored) == map_partial_explored
                if self.completed_partial_exploration:
                    self.status = STATUS.SPELUNKING
                else:
                    self.status = STATUS.LEFT_WALL_HUGGING

            elif self.partial_ir and self.handler.robot.get_location() == (
                    1, 18) and self.handler.robot.bearing == Bearing.WEST:
                self.status = STATUS.SPELUNKING
                # self.do_img_rec = False
                logging.debug("Image rec to spelunk")

            elif (self.handler.robot.get_location() == (1, 18) and self.handler.robot.bearing == Bearing.WEST) or \
                    list(self.handler.robot.get_location()) == list(self.start_pos):
                # logging.debug("restarting")
                # self.get_image_rec_target()
                self.spelunkprep()
                if self.temp_pos == None:
                    logging.debug("Image Rec completed. Going Home")
                    self.handler.robot.signal_exploration_ended()
                    self.go_home()
            elif self.start_pos == (-1, -1) and len(self.movements) == 0:
                self.update_start_pos()
                self.left_wall_hugging()
                # self.ir_spelunk_delay = True
                # logging.debug("updating start pos, ", self.temp_pos)

        #  if exploration is still incomplete after left wall hugging, try explore unknown grids using spelunking
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
                self.spelunkprep()
                if len(self.movements) <= 0:
                    if self.return_home:
                        self.go_home()

            if self.status == STATUS.SPELUNKING:
                self.move_and_sense()
            else:
                # logging.debug("Current Status: ", self.status)
                # for i in self.handler.robot.map_img_rec:
                #     logging.debug(i)
                self.move_and_sense(sense=True)

        self.handler.simulator.job = self.handler.simulator.root.after(self.delay, self.periodic_check)

    def left_wall_hugging(self):
        logging.debug("Consecutive left turn: " + str(self.consecutive_left_turn))
        if len(self.movements) > 0:
            self.move_and_sense()
            return

        elif self.consecutive_left_turn == 2:
            logging.debug("Error recovery")
            self.error_recovery()
            return

        left_front, left_middle, left_back = self.check_left()
        # if left_front and left_middle and left_back and not self.completed_partial_exploration:
        #     if self.left_obstacle():
        #         steps = self.check_front()
        #         if steps > 0:
        #             self.movements.append(MOVEMENT.FORWARD)
        #             self.move_and_sense()
        #         else:
        #             self.movements.append(MOVEMENT.LEFT)
        #             self.move_and_sense()
        #             steps = self.check_front()
        #             if steps > 0:
        #                 for _ in range(min(steps, 3)):
        #                     self.movements.append(MOVEMENT.FORWARD)
        #             self.movements.append(MOVEMENT.RIGHT)
        #     else:
        #         self.movements.append(MOVEMENT.LEFT)
        #         self.move_and_sense()
        #         steps = self.check_front()
        #         if steps > 0:
        #             for _ in range(min(steps, 3)):
        #                 self.movements.append(MOVEMENT.FORWARD)
        #     return

        if not left_front:
            self.consecutive_left_turn = 0
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
                self.consecutive_left_turn += 1

            else:
                self.consecutive_left_turn = 0
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
        else:
            self.execute_algo_move(num_move=1, sense=sense, ir=ir)

    def sense(self, backtrack=0):
        # logging.debug("[EXPLORATION] sense")
        self.handler.robot.sense(backtrack)

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
        if self.max_move > 1:
            self.max_move = 1
        if self.status == STATUS.IMAGE_REC:
            result, dir = self.get_image_rec_target()
            logging.debug("Getting image rec target")
            logging.debug("Target: " + str(result))
            self.start_pos = (-1, -1)
            self.temp_pos = result
            # logging.debug("new start pos" ,self.temp_pos)
        else:
            result, dir = self.get_spelunk_target()

        if result is None:
            logging.debug("Warning: Unable to reach unexplored tile. Ending Exploration early.")
            # for i in self.handler.robot.map_img_rec:
            #     logging.debug(i)

            return
        self.movements = self.path_finder.find_fastest_path(diag=False, delay=0, goalX=result[0], goalY=result[1],
                                                            waypointX=0,
                                                            waypointY=0,
                                                            startX=self.handler.robot.get_location()[0],
                                                            startY=self.handler.robot.get_location()[1], sim=False)
        if self.status == STATUS.IMAGE_REC:
            # logging.debug("old dir: ",dir)
            dir = Bearing.next_bearing(dir)
            # logging.debug("new dir: ",dir)
        self.add_bearing(dir)

    def get_image_rec_target(self):
        self.completed_partial_exploration = True
        try:
            explored = []
            unexplored = []
            result = None
            dir = None

            robot_x, robot_y = self.handler.robot.get_location()
            for i in range(config.map_size['height']):
                for k in range(robot_x - i, robot_x + i, 1):
                    for j in range(robot_y - i, robot_y + i):
                        if self.map.valid_range(j, k):
                            if j<3 or k<3:
                                continue
                            if self.handler.robot.map_img_rec[j][k] == 0:
                                if self.map.is_explored(k, j) == 1:
                                    if self.map.is_obstacle(k, j, sim=False):
                                        explored.append((k, j))
                                        # logging.debug((j, config.map_size['height'] - i - 1))
                                else:
                                    unexplored.append((k, j))
                                    # logging.debug((j, config.map_size['height'] - i - 1))

            while result == None and len(explored) > 0:
                obs = explored.pop(0)
                try:
                    result, dir = self.map.find_adjacent_free_space_front(obs[0], obs[1], ir=True)
                except:
                    logging.debug("No explored target for image rec")
            # logging.debug("Explored results: ", result)

            while result == None and len(unexplored) > 0:
                obs = unexplored.pop(0)
                try:
                    result, dir = self.map.find_adjacent_free_space_front(obs[0], obs[1], ir=True)
                except:
                    pass
                    logging.debug("No unexplored target for image rec")
            # logging.debug("Unexplored results: ", result)

            return result, dir
        except IndexError:
            pass

    def get_spelunk_target(self):
        unexplored_grids = self.map.get_unexplored_grids()
        result = None
        dir = None
        while result == None and len(unexplored_grids) > 0:
            unknown_grid = unexplored_grids.pop(0)
            # logging.debug("[CORE] Unknown grid: ", unknown_grid[0], unknown_grid[1])
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
            logging.debug("IR no obstacle in the middle")

    def go_home(self):
        self.handler.robot.update_map = False
        self.movements.clear()
        self.movements = self.path_finder.find_fastest_path(diag=False, delay=0, goalX=1, goalY=18, waypointX=2,
                                                            waypointY=18, \
                                                            startX=self.handler.robot.get_location()[0],
                                                            startY=self.handler.robot.get_location()[1], sim=False)
        logging.debug("Going Home from {}, len movements: {}".format(self.handler.robot.get_location(), len(self.movements)))
        self.status = STATUS.RETURN_HOME

    def add_bearing(self, dir):
        cur_dir = self.handler.robot.bearing
        if self.movements!= None and len(self.movements) > 0:
            for m in self.movements:
                if (m == MOVEMENT.LEFT):
                    cur_dir = Bearing.prev_bearing(cur_dir)
                elif (m == MOVEMENT.RIGHT):
                    cur_dir = Bearing.next_bearing(cur_dir)
        else:
            self.movements = []

        # logging.debug("cur dir: ", cur_dir, " dir: ", dir)
        if cur_dir == dir:
            return
        if dir == Bearing.next_bearing(cur_dir):
            self.movements.append(MOVEMENT.RIGHT)
        elif dir == Bearing.next_bearing(cur_dir):
            self.movements.append(MOVEMENT.LEFT)
        elif dir == Bearing.next_bearing(Bearing.next_bearing(cur_dir)):
            self.movements.append(MOVEMENT.RIGHT)
            self.movements.append(MOVEMENT.RIGHT)

        # if cur_dir == Bearing.NORTH:
        #     if dir == Bearing.WEST:
        #         self.movements.append(MOVEMENT.LEFT)
        #     elif dir == Bearing.EAST:
        #         self.movements.append(MOVEMENT.RIGHT)
        #     else:
        #         self.movements.append(MOVEMENT.RIGHT)
        #         self.movements.append(MOVEMENT.RIGHT)
        #
        # elif cur_dir == Bearing.SOUTH:
        #     if dir == Bearing.WEST:
        #         self.movements.append(MOVEMENT.RIGHT)
        #     elif dir == Bearing.EAST:
        #         self.movements.append(MOVEMENT.LEFT)
        #     else:
        #         self.movements.append(MOVEMENT.RIGHT)
        #         self.movements.append(MOVEMENT.RIGHT)
        #
        # elif cur_dir == Bearing.EAST:
        #     if dir == Bearing.NORTH:
        #         self.movements.append(MOVEMENT.LEFT)
        #     elif dir == Bearing.SOUTH:
        #         self.movements.append(MOVEMENT.RIGHT)
        #     else:
        #         self.movements.append(MOVEMENT.RIGHT)
        #         self.movements.append(MOVEMENT.RIGHT)
        #
        # elif cur_dir == Bearing.WEST:
        #     if dir == Bearing.SOUTH:
        #         self.movements.append(MOVEMENT.LEFT)
        #     elif dir == Bearing.NORTH:
        #         self.movements.append(MOVEMENT.RIGHT)
        #     else:
        #         self.movements.append(MOVEMENT.RIGHT)
        #         self.movements.append(MOVEMENT.RIGHT)

        else:
            logging.debug("Warning invalid direction")

    def set_status(self, do_img_rec, partial_ir):
        if do_img_rec:
            self.status = STATUS.IMAGE_REC
            self.max_move = 3
            self.set_optimized(False)
            if partial_ir:
                self.partial_ir = True
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
            logging.debug("[EXPLORATION] Reached start: invalid direction")

        for _ in range(len(self.movements)):
            self.execute_algo_move(sense=False, ir=False, num_move=1)

    def stop_ir(self):
        logging.debug("[EXPLORATION] IR completed. Changing status...")
        self.ir_completed = True

    def left_obstacle(self):
        robot_x, robot_y = self.handler.robot.get_location()
        robot_bearing = self.handler.robot.bearing
        left_bottom = [
            [0, 1],
            [-1, 0],
            [0, -1],
            [1, 0]
        ]
        offsets = [
            [-1, 0],
            [0, -1],
            [1, 0],
            [0, 1]
        ]
        offset = offsets[int(robot_bearing / 2)]
        pos = left_bottom[int(robot_bearing / 2)]
        for i in range(2,4):
            if self.map.valid_range(robot_y + pos[1] + offset[1]*i, robot_x + pos[0] + offset[0]*i):
                if self.map.is_explored(robot_x + pos[0] + offset[0]*i, robot_y + pos[1] + offset[1]*i):
                    if not self.map.is_free(robot_x + pos[0] + offset[0]*i, robot_y + pos[1] + offset[1]*i, sim=False):
                        logging.debug(f'{robot_x + pos[0] + offset[0]*i}, {robot_y + pos[1] + offset[1]*i} is free')
                        return True
                else:
                    logging.debug(f'{robot_x + pos[0] + offset[0] * i}, {robot_y + pos[1] + offset[1] * i} not explored')
                    return False
            else:
                logging.debug(f'{robot_x + pos[0] + offset[0] * i}, {robot_y + pos[1] + offset[1] * i} is not valide range')
                return False
        logging.debug(f'{robot_x + pos[0] + offset[0] * i}, {robot_y + pos[1] + offset[1] * i} is free')
        return False

    def error_recovery(self):
        self.movements.append(MOVEMENT.RIGHT)
        self.movements.append(MOVEMENT.RIGHT)
        # prev_loc = self.handler.robot.revert_loop()
        # self.movements = self.path_finder.find_fastest_path(diag=False, delay=0, goalX=prev_loc[0][0], goalY=prev_loc[0][1], waypointX=0,
        #                                                     waypointY=0, \
        #                                                     startX=self.handler.robot.get_location()[0],
        #                                                     startY=self.handler.robot.get_location()[1], sim=False)
        #
        # self.consecutive_left_turn = 0
        # self.add_bearing(prev_loc[1])
        # while self.movements!=None and len(self.movements)>0:
        #     self.move_and_sense()
        #     self.handler.robot.pop_prev_loc()




