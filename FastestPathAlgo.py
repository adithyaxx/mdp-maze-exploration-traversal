import config
from constants import Bearing


INFINITE_COST = 9999
MOVE_COST = 10
TURN_COST = 20

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

    def __init__(self, map, robot, goalX = 13, goalY = 1):
        self.map = map
        self.robot = robot
        self.open_list = []
        self.closed_list = []
        self.curDir = self.robot.bearing

        self.start_node = Node(robot.x, robot.y, parent=None, dir = self.curDir)
        self.goal_node = Node(goalX, goalY, None)
        self.start_node.g = 0
        self.start_node.h = self.cost_h(self.start_node)

        self.open_list.append(self.start_node)





    def check_valid_open(self, node):
        return self.map.valid_range(node.y, node.x) and self.map.is_valid_open(node.x, node.y) and not self.map.is_virtual_wall(node.x, node.y)
        # return self.map.valid_range(node.y, node.x) and self.map.is_explored(node.x, node.y) and self.map.is_free(node.x, node.y, False) and not self.map.is_virtual_wall(node.x, node.y)


    def best_first(self):
        min_cost = INFINITE_COST
        best_node_index = -1

        for i in range(len(self.open_list)):
            # print("({} , {}): {} , {} ".format(self.open_list[i].x, self.open_list[i].y, self.open_list[i].g, self.open_list[i].h))
            f = self.open_list[i].g + self.open_list[i].h
            print("({} , {}): g = {} h = {} f = {} dir = {}".format(self.open_list[i].x, self.open_list[i].y, self.open_list[i].g, self.open_list[i].h, f, self.open_list[i].dir))
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


    def find_fastest_path(self):
        # create virtual wall
        for i in range(config.map_size['height']):
            for j in range(config.map_size['width']):
                # if self.map.map_virtual[i][j] == 1:
                #     print("---- ",i , j)

                if self.map.is_physical_wall(j, i) or not self.map.is_explored(j, i):
                    self.map.set_virtual_wall_around(j, i)

        self.map.set_virtual_wall_border()

        for i in range(config.map_size['height']):
            print(self.map.map_virtual[i])


        print("Finding a fastest path from ({} , {}) to ({} , {})".format(self.start_node.x, self.start_node.y, self.goal_node.x, self.goal_node.y))
        parent = None
        curDir = self.curDir


        while len(self.open_list) > 0:

            best_index = self.best_first()
            # current_node.parent = parent

            current_node = self.open_list.pop(best_index)
            self.closed_list.append(current_node)
            curDir = current_node.dir

            # if(parent != None):
            #     curDir = self.get_target_dir(parent, current_node)

            if(current_node == self.goal_node):
                print("Fastest path found")
                self.print_path(current_node)
                return

            print("Open: ({} , {}) g = {} h = {} f = {} dir = {}".format(current_node.x, current_node.y, current_node.g, current_node.h, current_node.g + current_node.h, current_node.dir))

            for neighbour_position in [(0, -1), (1, 0), (0, 1), (-1, 0)]:

                neighbour = Node(current_node.x + neighbour_position[0], current_node.y + neighbour_position[1],  current_node)
                # print("children: {}  {} ".format(neighbour.x, neighbour.y))
                if(not self.check_valid_open(neighbour)):
                    # print("Invalid children: {}  {} ".format(neighbour.x, neighbour.y))
                    continue

                if(neighbour in self.closed_list):
                    continue

                dir = self.get_target_dir(current_node, neighbour)
                if(neighbour not in self.open_list):
                    neighbour.dir = dir
                    neighbour.g = self.cost_g(dir, curDir) + current_node.g
                    # print("neighbour g: {} , parent g: {}".format( self.cost_g(current_node, neighbour, dir) , current_node.g))
                    neighbour.h = self.cost_h(neighbour)
                    self.open_list.append(neighbour)
                    if (neighbour.x == 3 and neighbour.y == 18):
                        print("=========="*5,self.get_turn_cost(curDir, dir))

                else:
                    g_cost = self.cost_g(dir, curDir) + current_node.g
                    h_cost = self.cost_h(neighbour)
                    f_cost = g_cost + h_cost
                    index = self.open_list.index(neighbour)
                    if(f_cost < self.open_list[index].g + self.open_list[index].h):
                        self.open_list[index].dir = dir
                        self.open_list[index].g = g_cost
                        self.open_list[index].h = h_cost
                        self.open_list[index].parent = current_node
                # print("Added children: {}  {} ".format( neighbour.x, neighbour.y))

            parent = current_node

        print("No path found")
        return None

    def print_path(self, goal_node):
        # pass
        node = goal_node
        path = []
        while node != None:
            # path.append(node)
            self.map.map_virtual[node.y][node.x] = 3
            node = node.parent

        for y in range(config.map_size['height']):
            print((self.map.map_virtual)[y])

        # for node in path:
        #     print("({}, {})\n".format(node.x, node.y))
        print("Total cost: {}".format(goal_node.g))







    # def get_target_dir_north(self, from_node, to_node):
    #     if (to_node.x - from_node.x > 0):
    #         return Bearing.EAST
    #     elif (to_node.x - from_node.x < 0):
    #         return Bearing.WEST
    #     elif (to_node.y - from_node.y > 0):
    #         return Bearing.SOUTH
    #     return Bearing.NORTH
    #
    # def get_target_dir_east(self, from_node, to_node):
    #     if (to_node.x - from_node.x > 0):
    #         return Bearing.EAST
    #     elif (to_node.x - from_node.x < 0):
    #         return Bearing.WEST
    #     elif (to_node.y - from_node.y > 0):
    #         return Bearing.EAST
    #     return Bearing.WEST
    #
    # def get_target_dir_south(self, from_node, to_node):
    #     if (to_node.x - from_node.x > 0):
    #         return Bearing.WEST
    #     elif (to_node.x - from_node.x < 0):
    #         return Bearing.EAST
    #     elif (to_node.y - from_node.y > 0):
    #         return Bearing.SOUTH
    #     return Bearing.NORTH
    #
    # def get_target_dir_west(self, from_node, to_node):
    #     if (to_node.x - from_node.x > 0):
    #         return Bearing.SOUTH
    #     elif (to_node.x - from_node.x < 0):
    #         return Bearing.NORTH
    #     elif (to_node.y - from_node.y > 0):
    #         return Bearing.WEST
    #     return Bearing.EAST
    #
    #
