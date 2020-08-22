import config
import simulated_robot
import real_robot
from core import Core
from map import Map


class Handler:
    def __init__(self, simulator):
        self.map = Map()
        self.simulator = simulator
        self.core = Core(self)
        if config.robot_simulation:
            self.robot = simulated_robot.SimulatedRobot(self)
        else:
            self.robot = real_robot.RealRobot(self)

    def get_robot(self):
        return self.robot

    def move(self, steps=1):
        self.robot.move(steps=steps)
        self.simulator.update_map(radius=4)

    def left(self):
        self.robot.left()
        self.simulator.update_map(radius=4)

    def right(self):
        self.robot.right()
        self.simulator.update_map(radius=4)

    def get_location(self):
        self.robot.get_location()
