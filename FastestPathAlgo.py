import time
from copy import deepcopy
import config
from constants import Bearing, MOVEMENT


INFINITE_COST = 9999
MOVE_COST = 10
TURN_COST = 20
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


    def check_valid_open(self, node):
        return self.map.valid_range(node.y, node.x) and self.map.is_valid_open(node.x, node.y) and not self.map.is_virtual_wall(node.x, node.y)
        # return self.map.valid_range(node.y, node.x) and self.map.is_explored(node.x, node.y) and self.map.is_free(node.x, node.y, False) and not self.map.is_virtual_wall(node.x, node.y)


    def best_first(self):
        min_cost = INFINITE_COST
        best_node_index = -1

        for i in range(len(self.open_list)):
            # print("({} , {}): {} , {} ".format(self.open_list[i].x, self.open_list[i].y, self.open_list[i].g, self.open_list[i].h))
            f = self.open_list[i].g + self.open_list[i].h
            # print("({} , {}): g = {} h = {} f = {} dir = {}".format(self.open_list[i].x, self.open_list[i].y, self.open_list[i].g, self.open_list[i].h, f, self.open_list[i].dir))
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
        if(Bearing.prev_bearing(from_dir) == to_dir or Bearing.next_bearing(from_dir) == to_dir):
            return TURN_COST
        return  2 * TURN_COST


    def get_target_dir(self, from_node, to_node):
        if (to_node.x - from_node.x > 0):
            return Bearing.EAST
        elif (to_node.x - from_node.x < 0):
            return Bearing.WEST
        elif (to_node.y - from_node.y > 0):
            return Bearing.SOUTH
        return Bearing.NORTH


    def cost_g(self, current_dir , next_dir):
        turn_cost = self.get_turn_cost(current_dir, next_dir )
        # print("turn cost: {}".format(turn_cost))
        return MOVE_COST + turn_cost

    def create_virtual_wall(self):
        for i in range(config.map_size['height']):
            for j in range(config.map_size['width']):
                # if self.map.map_virtual[i][j] == 1:
                #     print("---- ",i , j)

                if self.map.is_physical_wall(j, i) or not self.map.is_explored(j, i):
                    self.map.set_virtual_wall_around(j, i)

        self.map.set_virtual_wall_border()

        # for i in range(config.map_size['height']):
        #     print(self.map.map_virtual[i])


    def find_fastest_path(self,  startX = 1, startY = 18, goalX = 13, goalY = 1, waypointX = 2, waypointY = 1, bearing = None):
        self.create_virtual_wall()

        if (bearing == None):
            self.curDir = self.robot.bearing
        else:
            self.curDir = bearing

        self.initial_node = Node(startX, startY, parent=None, dir=self.curDir)
        self.waypoint = Node(waypointX, waypointY, None, dir=self.curDir)
        self.destination_node = Node(goalX, goalY, None)
        self.start_node = self.initial_node
        self.goal_node = self.waypoint

        self.start_node.g = 0
        self.start_node.h = self.cost_h(self.start_node)

        self.open_list.append(self.start_node)

        path_found_wp = self.run()
        if(not path_found_wp):
            print("no path found from start to waypoint")

        else:
            self.start_node =  self.closed_list.pop(len(self.closed_list) - 1)
            self.goal_node = self.destination_node
            self.start_node.h = self.cost_h(self.start_node)
            self.open_list.clear()
            self.closed_list.clear()
            self.open_list.append(self.start_node)

            path_found_wp = self.run()

        if(not path_found_wp):
            print("no path found from waypoint to goal")

        self.temp_path = deepcopy(self.closed_list)
        self.closed_list.clear()
        self.open_list.clear()

        self.start_node = self.initial_node
        self.goal_node = self.destination_node
        self.start_node.g = 0
        self.start_node.h = self.cost_h(self.start_node)
        self.open_list.append(self.start_node)

        path_found_fp = self.run()
        if( not path_found_fp):
            print("no path found from start to goal")

        print(self.closed_list[len(self.closed_list)-1].g , self.temp_path[len(self.temp_path) - 1].g)

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
        while len(self.open_list) > 0:

            best_index = self.best_first()
            # current_node.parent = parent

            current_node = self.open_list.pop(best_index)
            self.closed_list.append(current_node)
            curDir = current_node.dir

            # if(parent != None):
            #     curDir = self.get_target_dir(parent, current_node)

            if (current_node == self.goal_node):
                print("Fastest path found")
                return True

            # print("Open: ({} , {}) g = {} h = {} f = {} dir = {}".format(current_node.x, current_node.y, current_node.g,
            #                                                              current_node.h,
            #                                                              current_node.g + current_node.h,
            #                                                              current_node.dir))

            for neighbour_position in [(0, -1), (1, 0), (0, 1), (-1, 0)]:

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
                # print("Added children: {}  {} ".format( neighbour.x, neighbour.y))

            parent = current_node

        return False


    def print_path(self, goal_node):
        node = goal_node
        self.path = []
        self.movements = []
        while node != None:
            self.map.map_virtual[node.y][node.x] = 3
            self.path.insert(0, node)
            # print(path[0].x, path[0].y, path[0].dir)
            node = node.parent
            if(node != None):
                self.get_target_movement(node.dir, self.path[0].dir)

        for y in range(config.map_size['height']):
            print((self.map.map_virtual)[y])

        print("Total cost: {}".format(goal_node.g))

        # self.path[0].dir = self.get_target_dir(self.path[0], self.path[1])
        self.path_counter = 0

        for m in self.movements:
            print(m)
        print("EXECUTING FASTEST PATH")
        self.execute_fastest_path()


    def execute_fastest_path(self):

        print(self.movements[self.path_counter])

        if(self.movements[self.path_counter] == MOVEMENT.LEFT):
            self.handler.left()
        elif(self.movements[self.path_counter] == MOVEMENT.RIGHT):
            self.handler.right()
        else:
            self.handler.move(1)
        self.path_counter += 1

        if(self.path_counter < len(self.movements) ):
            self.handler.simulator.root.after(400, self.execute_fastest_path)


    def get_target_movement(self, from_dir, to_dir):
        self.movements.insert(0, MOVEMENT.FORWARD)
        if(from_dir == Bearing.NORTH):
            self.get_target_movement_north(to_dir)
        elif (from_dir == Bearing.EAST):
            self.get_target_movement_east(to_dir)
        elif (from_dir == Bearing.SOUTH):
            self.get_target_movement_south(to_dir)
        else:
            self.get_target_movement_west(to_dir)


    def get_target_movement_north(self, to_dir):
        if(to_dir == Bearing.EAST):
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif(to_dir == Bearing.WEST):
            self.movements.insert(0, MOVEMENT.LEFT)
        elif(to_dir == Bearing.SOUTH):
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)


    def get_target_movement_east(self, to_dir):
        if (to_dir == Bearing.NORTH):
            self.movements.insert(0, MOVEMENT.LEFT)
        elif (to_dir == Bearing.SOUTH):
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif(to_dir == Bearing.WEST):
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)


    def get_target_movement_south(self, to_dir):
        if (to_dir == Bearing.EAST):
            self.movements.insert(0, MOVEMENT.LEFT)
        elif (to_dir == Bearing.WEST):
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif (to_dir == Bearing.NORTH):
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)


    def get_target_movement_west(self, to_dir):
        if (to_dir == Bearing.NORTH):
            self.movements.insert(0, MOVEMENT.RIGHT)
        elif (to_dir == Bearing.SOUTH):
            self.movements.insert(0, MOVEMENT.LEFT)
        elif (to_dir == Bearing.EAST):
            self.movements.insert(0, MOVEMENT.RIGHT)
            self.movements.insert(0, MOVEMENT.RIGHT)




