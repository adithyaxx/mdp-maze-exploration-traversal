from robot import Robot
import config

class Handler:

    def __init__(self):
        self.robot = Robot()

    def get_robot(self):
        return self.robot

    def move(self):
        self.robot.move()

    def left(self):
        self.robot.left()

    def right(self):
        self.robot.right()
