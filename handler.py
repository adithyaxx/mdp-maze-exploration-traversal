import config
import simulated_robot
import real_robot
from core import Core
from map import Map
from constants import Bearing


class Handler:
    def __init__(self, simulator):
        self.map = Map()
        self.simulator = simulator
        if config.robot_simulation:
            self.robot = simulated_robot.SimulatedRobot(self)
        else:
            self.robot = real_robot.RealRobot(self)
        self.core = Core(self)

    def get_robot(self):
        return self.robot

    def move(self, steps=1):
        self.robot.move(steps=steps)
        self.simulator.update_map(radius=3)

    def left(self):
        self.robot.left()
        self.simulator.update_map(radius=3)

    def right(self):
        self.robot.right()
        self.simulator.update_map(radius=3)

    def reset(self):
        self.robot.reset()
        self.map.reset()

    def get_location(self):
        self.robot.get_location()

    # call update and rerender for every grids detected by the sensor
    def update_map(self, x, y, dis, bearing, sensor_range):
        if bearing == Bearing.NORTH:
            for i in range(dis):
                self.update_and_render(x, y - i - 1, 1, 0)
            if (dis < sensor_range and self.map.valid_range(y - dis - 1, x)):
                self.update_and_render(x, y - dis - 1, 1, 1)

        elif bearing == Bearing.EAST:
            for i in range(dis):
                self.update_and_render(x + i + 1, y, 1, 0)
            if (dis < sensor_range and self.map.valid_range(y, x + dis + 1)):
                self.update_and_render(x + dis + 1, y, 1, 1)

        elif bearing == Bearing.SOUTH:
            for i in range(dis):
                self.update_and_render(x, y + i + 1, 1, 0)

            if (dis < sensor_range and self.map.valid_range(y + dis + 1, x)):
                self.update_and_render(x, y + dis + 1, 1, 1)

        else:
            for i in range(dis):
                self.update_and_render(x - i - 1, y, 1, 0)
            if (dis < sensor_range and self.map.valid_range(y, x - dis - 1)):
                self.update_and_render(x - dis - 1, y, 1, 1)

    # update map_is_explored and virtual map and call the simulator to rerender the cell
    def update_and_render(self, x, y, is_explore, is_obstacle):
        self.map.mark_explored(x, y, is_explore, is_obstacle)
        self.simulator.update_cell(x, y)
