
from fastest_path_algo import FastestPathAlgo
from exploration_algo import ExplorationAlgo


class Core:
    def __init__(self, handler):
        self.handler = handler
        self.map = self.handler.map
        self.path_finder = FastestPathAlgo(self.map, self.handler.robot, self.handler)
        self.explorer = ExplorationAlgo(self.handler, self.path_finder)

    def reset(self):
        self.explorer.reset()


    def explore(self, steps_per_second, coverage, time_limit, exploration_algo):
        is_return_home = 'Return Home' in exploration_algo

        if steps_per_second == -1:
            delay = 10
        else:
            delay = 1000 // steps_per_second

        if 'Image Recognition' in exploration_algo:
            self.explorer.set_status(do_img_rec=True)
        else:
            if 'Optimized' in exploration_algo:
                self.explorer.set_optimized(True)
            else:
                self.explorer.set_optimized(False)
            self.explorer.set_status(do_img_rec=False)
        self.explorer.sense()
        self.explorer.explore(delay, steps_per_second, coverage, time_limit, is_return_home)


    def findFP(self, steps_per_second, goal_x, goal_y, waypoint_x, waypoint_y, diagonal):
        is_diagonal = "Diagonal" in diagonal

        if steps_per_second == -1:
            delay = 10
        else:
            delay = 1000 // steps_per_second
        self.path_finder.find_fastest_path(diag=is_diagonal, delay=delay, goalX=goal_x, goalY=goal_y, waypointX=waypoint_x,
                                    waypointY=waypoint_y)
