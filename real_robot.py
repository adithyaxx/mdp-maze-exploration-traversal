import math
import socket
from time import sleep

from comms import *
from robot import *
from utils import *
from constants import arduino_queue


class RealRobot(Robot):
    def __init__(self, handler):

        super().__init__(handler)
        family = socket.AF_INET
        socket_type = socket.SOCK_STREAM
        self.socket = socket.socket(family, socket_type)
        self.socket.settimeout(1)
        self.connected = False
        self.port = 1273
        self.host = ""
        self.listener = None

    def connect(self, host):
        self.host = host

        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            print("Connection established.")
            self.listener = ListenerThread(name='producer', socket=self.socket, handler=self.handler)
            self.listener.start()
            self.send('c\ns\n')
            # self.send('s')
        except socket.error as error:
            self.connected = False
            print("Unable to establish connection. ", error)

        return self.connected

    def disconnect(self):
        try:
            self.socket.shutdown(1)
            self.socket.close()
            self.connected = False
            print("Socket closed.")
        except socket.error as error:
            print("Unable to close socket. ", error)
            return False

        return True

    def send(self, msg):
        if not self.connected:
            self.connect(self.host)

        if self.connected:
            print("[Info] Sending message: ", msg)
            try:
                self.socket.sendall(str.encode(msg))
            except socket.error as error:
                print("Unable to send message. ", error)

    def get_msg(self):
        # Handle other events
        while not general_queue.empty():
            msg = general_queue.get()

            if msg[0] == DONE_TAKING_PICTURE:
                # TODO
                continue
            elif msg[:3] == START_EXPLORATION:
                self.handler.simulator.explore()
                continue
            elif msg[:3] == START_FASTEST_PATH:
                self.handler.simulator.findFP()
                continue
            elif msg[:3] == GET_MAP:
                # explored_hex, obstacles_hex = self.handler.map.create_map_descriptor()
                # json_str = "M{\"map\": [{\"length\": 300, \"explored\": \"" + explored_hex + "\", \"obstacle\": \"" + obstacles_hex + "\"}]}"
                # self.send(json_str)
                self.send_map()
                continue

        # Handle arduino events
        while arduino_queue.empty():
            sleep(0.1)

        msg = arduino_queue.get()
        return msg.split()

    def receive(self):
        msg = self.get_msg()

        # Straight line correction
        # if abs(convert_short(msg[1]) - convert_short(msg[0])) > 0:
        #     if abs(float(msg[1]) - float(msg[0])) < 3:
        #         angle = math.atan((convert_short(msg[1]) - convert_short(msg[0])) / 9)
        #
        #         if angle < 0:
        #             self.send('r' + str(int(abs(angle))) + '\n')
        #         else:
        #             self.send('l' + str(int(angle)) + '\n')
        #
        #         msg = self.get_msg()

        # Calibration
        can_calibrate = self.handler.map.find_left_wall_or_obstacle(self.x, self.y, self.handler.robot.bearing)

        if can_calibrate:
            self.send('c\ns\n')
            msg = self.get_msg()

        out = [convert_short(msg[2]),
               convert_short(msg[3]),
               convert_short(msg[4]),
               convert_short(msg[1]),
               convert_short(msg[0]),
               convert_long(msg[5])]

        print(out)

        return out

    def move(self, sense, ir, steps=1):
        self.send('f' + str(steps) + '\n')
        self.send_map()

        while arduino_queue.qsize() != steps:
            sleep(0.1)

        super().move(sense, ir, steps)

    def left(self, sense, ir):
        # rotate anticlockwise by 90 deg
        self.send('l83\n')
        self.send_map()

        while arduino_queue.qsize() < 1:
            sleep(0.1)

        super().left(sense, ir)

    def right(self, sense, ir):
        # rotate clockwise by 90 deg
        self.send('r83\n')
        self.send_map()

        while arduino_queue.qsize() < 1:
            sleep(0.1)

        super().right(sense, ir)

    def left_diag(self):
        self.send('l45\n')
        self.send_map()

        while arduino_queue.qsize() < 1:
            sleep(0.1)

        super().left_diag()

    def right_diag(self):
        self.send('r45\n')
        self.send_map()

        while arduino_queue.qsize() < 1:
            sleep(0.1)

        super().right_diag()

    def send_map(self):
        explored_hex, obstacles_hex = self.handler.map.create_map_descriptor()
        json_str = "M{\"map\": [{\"length\": 300, \"explored\": \"" + explored_hex + "\", \"obstacle\": \"" + \
                   obstacles_hex + "\"}], \"robotPosition\":[" + str(self.x) + ", " + str(
            self.y) + "," + self.convert_to_degrees() + "]}"
        self.send(json_str)

    def convert_to_degrees(self):
        if self.bearing == Bearing.NORTH:
            return '0'
        elif self.bearing == Bearing.EAST:
            return '90'
        elif self.bearing == Bearing.SOUTH:
            return '180'
        else:
            return '270'
