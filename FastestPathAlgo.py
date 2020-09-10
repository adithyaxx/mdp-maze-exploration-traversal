import time
from copy import deepcopy
import config
from constants import Bearing, MOVEMENT


INFINITE_COST = 9999
MOVE_COST = 10
MOVE_COST_DIAG = 15
TURN_COST = 20
TURN_COST_DIAG = 10
WAYPONT_PENALTY = 1000

class Node():
    def __init__(self, x, y, parent=None, dir=None, g=INFINITE_COST, h=INFINITE_COST):
        self.parent = parent
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.dir = dir

    def __eq__(self, other):
        if other == None:
            return False
        return self.x == other.x and self.y == other.y


class FastestPathAlgo():

    def __init__(self, map, robot, handler):
        self.map = map
        self.robot = robot
        self.handler = handler
        self.open_list = []
        self.closed_list = []
        self.waypoint = None
        self.start_node = None
        self.destination_node = None
        self.goal_node = None
        self.diag = False
        self.delay = 10


    def check_valid_open(self, node):
        return self.map.valid_range(node.y, node.x) and self.map.is_valid_open(node.x, node.y) and not self.map.is_virtual_wall(node.x, node.y)


    def best_first(self):
        min_cost = INFINITE_COST
        best_node_index = -1

        for i in range(len(self.open_list)):
            f = self.open_list[i].g + self.open_list[i].h
            if(f < min_cost):
                min_cost = f
                best_node_index = i
        return best_node_index


    def cost_h(self, node):
        turn_cost = 0
        move_cost = abs(node.x - self.goal_node.x) + abs(node.y - self.goal_node.y)

        if(move_cost == 0):
            return move_cost

        if(node.x != self.goal_node.x and node.y != self.goal_node.y):
            turn_cost = TURN_COST

        return move_cost * MOVE_COST + turn_cost


    def get_turn_cost(self, from_dir, to_dir):
        if(from_dir == to_dir):
            return  0

        prev_bearing = Bearing.prev_bearing_diag(from_dir)
        next_bearing = Bearing.next_bearing_diag(from_dir)

        turn_costs = [TURN_COST_DIAG, TURN_COST, 3 * TURN_COST_DIAG, 2 * TURN_COST]

        for i in range(4):

            if prev_bearing == to_dir or next_bearing == to_dir:
                return turn_costs[i]

            prev_bearing = Bearing.prev_bearing_diag(prev_bearing)
            next_bearing = Bearing.next_bearing_diag(next_bearing)


    def get_target_dir(self, from_node, to_node):
        if self.diag:
            if to_node.x - from_node.x > 0 and to_node.y - from_node.y < 0:
                return Bearing.NORTH_EAST
            elif to_node.x - from_node.x > 0 and to_node.y - from_node.y > 0:
                return Bearing.SOUTH_EAST
            elif to_node.x - from_node.x < 0 and to_node.y - from_node.y > 0:
                return Bearing.SOUTH_WEST
            elif to_node.x - from_node.x < 0 and to_node.y - from_node.y < 0:
                return Bearing.NORTH_WEST

        if (to_node.x - from_node.x > 0):
            return Bearing.EAST
        elif (to_node.x - from_node.x < 0):
            return Bearing.WEST
        elif (to_node.y - from_node.y > 0):
            return Bearing.SOUTH
        return Bearing.NORTH


    def cost_g(self, current_dir , next_dir):
        turn_cost = self.get_turn_cost(current_dir, next_dir )
        if Bearing.is_diag_bearing(next_dir):
            return MOVE_COST_DIAG + turn_cost
        return MOVE_COST + turn_cost


    def create_virtual_wall(self):
        for i in range(config.map_size['height']):
            for j in range(config.map_size['width']):

                if self.map.is_physical_wall(j, i) or not self.map.is_explored(j, i):
                    self.map.set_virtual_wall_around(j, i)

        self.map.set_virtual_wall_border()


    def find_fastest_path(self, diag , delay, goalX, goalY, waypointX, waypointY, startX = 1, startY = config.map_size['height'] - 2):
        self.create_virtual_wall()
        self.open_list.clear()
        self.closed_list.clear()

        self.curDir = self.robot.bearing
        self.diag = diag
        self.delay = delay

        self.initial_node = Node(startX, startY, parent=None, dir=self.curDir)
        self.waypoint = Node(waypointX, waypointY, None, dir=self.curDir)
        self.destination_node = Node(goalX, goalY, None)
        self.start_node = self.initial_node
        self.goal_node = self.waypoint

        self.start_node.g = 0
        self.start_node.h = self.cost_h(self.start_node)

        self.open_list.append(self.start_node)

        path_found_wp = False
        if self.waypoint.x > 0 and self.waypoint.x < config.map_size['width']-1 and self.waypoint.y > 0 and self.waypoint.y < config.map_size['height']-1:
            path_found_wp = self.run()
            if(not path_found_wp):
                print("no path found from start to waypoint")

            else:
                self.start_node = self.closed_list.pop(len(self.closed_list) - 1)
                self.goal_node = self.destination_node
                self.start_node.h = self.cost_h(self.start_node)
                self.open_list.clear()
                self.closed_list.clear()
                self.open_list.append(self.start_node)

                path_found_wp = self.run()

                if(not path_found_wp):
                    print("no path found from waypoint to goal")
        else:
            print("Waypoints out of bound")

        self.temp_path = deepcopy(self.closed_list)
        self.closed_list.clear()
        self.open_list.clear()

        self.start_node = self.initial_node
        self.goal_node = self.destination_node
        self.start_node.g = 0
        self.start_node.h = self.cost_h(self.start_node)
        self.open_list.append(self.start_node)

        path_found_fp = self.run()
        if(not path_found_fp):
            print("no path found from start to goal")

        if path_found_wp and path_found_fp:
            if self.temp_path[len(self.temp_path) - 1].g - self.closed_list[len(self.closed_list)-1].g  > WAYPONT_PENALTY:
                self.fastest_path_goal_node = self.closed_list[len(self.closed_list)-1]
            else:
                self.fastest_path_goal_node = self.temp_path[len(self.temp_path) - 1]
        elif path_found_fp:
            self.fastest_path_goal_node = self.closed_list[len(self.closed_list) - 1]
        else:
            self.fastest_path_goal_node = self.temp_path[len(self.temp_path) - 1]

        self.print_path(self.fastest_path_goal_node)


    def run(self):

        print("Finding a fastest path from ({} , {}) to ({} , {})".format(self.start_node.x, self.start_node.y,
                                                                          self.goal_node.x, self.goal_node.y))
        start = time.time()

        while len(self.open_list) > 0:

            best_index = self.best_first()

            current_node = self.open_list.pop(best_index)
            self.closed_list.append(current_node)
            curDir = current_node.dir

            if (current_node == self.goal_node):
                end = time.time()
                print("Fastest path found in {:0.5f} second".format(end - start))
                return True

            # print("Open: ({} , {}) g = {} h = {} f = {} dir = {}".format(current_node.x, current_node.y, current_node.g,
            #                                                              current_node.h,
            #                                                              current_node.g + current_node.h,
            #                                                              current_node.dir))

            if self.diag:
                neighbour_positions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
            else:
                neighbour_positions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            for neighbour_position in neighbour_positions:

                neighbour = Node(current_node.x + neighbour_position[0], current_node.y + neighbour_position[1],
                                 current_node)
                # print("children: {}  {} ".format(neighbour.x, neighbour.y))
                if (not self.check_valid_open(neighbour)):
                    # print("Invalid children: {}  {} ".format(neighbour.x, neighbour.y))
                    continue

                if (neighbour in self.closed_list):
                    continue

                dir = self.get_target_dir(current_node, neighbour)
                if (neighbour not in self.open_list):
                    neighbour.dir = dir
                    neighbour.g = self.cost_g(dir, curDir) + current_node.g
                    # print("neighbour g: {} , parent g: {}".format( self.cost_g(current_node, neighbour, dir) , current_node.g))
                    neighbour.h = self.cost_h(neighbour)
                    self.open_list.append(neighbour)

                else:
                    g_cost = self.cost_g(dir, curDir) + current_node.g
                    h_cost = self.cost_h(neighbour)
                    f_cost = g_cost + h_cost
                    index = self.open_list.index(neighbour)
                    if (f_cost < self.open_list[index].g + self.open_list[index].h):
                        self.open_list[index].dir = dir
                        self.open_list[index].g = g_cost
                        self.open_list[index].h = h_cost
                        self.open_list[index].parent = current_node

        end = time.time()
        print("No path found in {:0.2f}".format(end - start))

        return False


    def print_path(self, goal_node):
        node = goal_node
        self.path = []
        self.movements = []
        while node != None:
            self.map.map_virtual[node.y][node.x] = 3
            self.path.insert(0, node)
            node = node.parent
            if(node != None):
                self.get_target_movement(node.dir, self.path[0].dir)

        # for y in range(config.map_size['height']):
        #     print((self.map.map_virtual)[y])

        print("Total cost: {}".format(goal_node.g))

        self.path_counter = 0

        # for m in self.movements:
        #     print(m)
        print("EXECUTING FASTEST PATH")

        self.execute_fastest_path()


    def execute_fastest_path(self):

        # print(self.movements[self.path_counter])

        if(self.movements[self.path_counter] == MOVEMENT.LEFT):
            self.handler.left()
        elif(self.movements[self.path_counter] == MOVEMENT.RIGHT):
            self.handler.right()
        elif (self.movements[self.path_counter] == MOVEMENT.LEFT_DIAG):
            self.handler.left_diag()
        elif (self.movements[self.path_counter] == MOVEMENT.RIGHT_DIAG):
            self.handler.right_diag()
        elif (self.movements[self.path_counter] == MOVEMENT.FORWARD_DIAG):
            self.handler.move_diag()
        else:
            self.handler.move(1)
        self.path_counter += 1

        if(self.path_counter < len(self.movements) ):
            self.handler.simulator.job = self.handler.simulator.root.after(self.delay, self.execute_fastest_path)


    def get_target_movement(self, from_dir, to_dir):
        if Bearing.is_diag_bearing(to_dir):
            self.movements.insert(0, MOVEMENT.FORWARD_DIAG)
        else:
            self.movements.insert(0, MOVEMENT.FORWARD)

        if from_dir == to_dir:
            return

        if from_dir == Bearing.NORTH:
            self.get_target_movement_north(to_dir)
        elif from_dir == Bearing.NORTH_EAST:
            self.get_target_movement_northeast(to_dir)
        elif from_dir == Bearing.EAST:
            self.get_target_movement_east(to_dir)
        elif from_dir == Bearing.SOUTH_EAST:
            self.get_target_movement_southeast(to_dir)
        elif from_dir == Bearing.SOUTH:
            self.get_target_movement_south(to_dir)
        elif from_dir == Bearing.SOUTH_WEST:
            self.get_target_movement_southwest(to_dir)
        elif from_dir == Bearing.WEST:
            self.get_target_movement_west(to_dir)
        else:
            self.get_target_movement_northwest(to_dir)


    def get_target_movement_north(self, to_dir):
        if to_dir == Bearing.NORTH_EAST:
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.EAST:
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif to_dir == Bearing.SOUTH_EAST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.WEST:
            self.movements.insert(0, MOVEMENT.LEFT)
        elif to_dir == Bearing.NORTH_EAST:
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.SOUTH_WEST:
            self.movements.insert(0, MOVEMENT.LEFT)
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.SOUTH:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)


    def get_target_movement_east(self, to_dir):
        if to_dir == Bearing.NORTH:
            self.movements.insert(0, MOVEMENT.LEFT)
        elif to_dir == Bearing.NORTH_EAST:
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.SOUTH_EAST:
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.SOUTH:
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif to_dir == Bearing.NORTH_EAST:
            self.movements.insert(0, MOVEMENT.LEFT)
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.SOUTH_WEST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.WEST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)


    def get_target_movement_south(self, to_dir):
        if to_dir == Bearing.EAST:
            self.movements.insert(0, MOVEMENT.LEFT)
        elif to_dir == Bearing.SOUTH_EAST:
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.SOUTH_WEST:
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.WEST:
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif to_dir == Bearing.NORTH_EAST:
            self.movements.insert(0, MOVEMENT.LEFT)
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.NORTH_WEST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.NORTH:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)


    def get_target_movement_west(self, to_dir):
        if to_dir == Bearing.NORTH:
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif to_dir == Bearing.NORTH_WEST:
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.SOUTH_WEST:
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.SOUTH:
            self.movements.insert(0, MOVEMENT.LEFT)
        elif to_dir == Bearing.NORTH_EAST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.SOUTH_EAST:
            self.movements.insert(0, MOVEMENT.LEFT)
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.EAST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)

    def get_target_movement_northeast(self, to_dir):
        if to_dir == Bearing.NORTH:
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.NORTH_WEST:
            self.movements.insert(0, MOVEMENT.LEFT)
        elif to_dir == Bearing.EAST:
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.SOUTH_EAST:
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif to_dir == Bearing.SOUTH:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.WEST:
            self.movements.insert(0, MOVEMENT.LEFT)
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.SOUTH_WEST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)

    def get_target_movement_southeast(self, to_dir):
       if to_dir == Bearing.EAST:
           self.movements.insert(0, MOVEMENT.LEFT_DIAG)
       elif to_dir == Bearing.SOUTH:
           self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
       elif to_dir == Bearing.NORTH_EAST:
           self.movements.insert(0, MOVEMENT.LEFT)
       elif to_dir == Bearing.SOUTH_WEST:
           self.movements.insert(0, MOVEMENT.RIGHT)
       elif to_dir == Bearing.NORTH:
           self.movements.insert(0, MOVEMENT.LEFT)
           self.movements.insert(0, MOVEMENT.LEFT_DIAG)
       elif to_dir == Bearing.WEST:
           self.movements.insert(0, MOVEMENT.RIGHT)
           self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
       elif to_dir == Bearing.NORTH_WEST:
           self.movements.insert(0, MOVEMENT.RIGHT)
           self.movements.insert(0, MOVEMENT.RIGHT)

    def get_target_movement_southwest(self, to_dir):
        if to_dir == Bearing.SOUTH:
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.WEST:
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.SOUTH_EAST:
            self.movements.insert(0, MOVEMENT.LEFT)
        elif to_dir == Bearing.NORTH_WEST:
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif to_dir == Bearing.EAST:
            self.movements.insert(0, MOVEMENT.LEFT)
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.NORTH:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.NORTH_EAST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)

    def get_target_movement_northwest(self, to_dir):
        if to_dir == Bearing.NORTH:
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.WEST:
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.NORTH_EAST:
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif to_dir == Bearing.SOUTH_WEST:
            self.movements.insert(0, MOVEMENT.LEFT)
        elif to_dir == Bearing.EAST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT_DIAG)
        elif to_dir == Bearing.SOUTH:
            self.movements.insert(0, MOVEMENT.LEFT)
            self.movements.insert(0, MOVEMENT.LEFT_DIAG)
        elif to_dir == Bearing.SOUTH_EAST:
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)



