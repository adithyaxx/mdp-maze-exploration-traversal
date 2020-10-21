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
            logging.info("Connection established.")
            self.listener = ListenerThread(name='producer', socket=self.socket, handler=self.handler)
            self.listener.start()
            self.send('c\ns\n')
            # self.send('s')
        except socket.error as error:
            self.connected = False
            logging.info("Unable to establish connection. " + str(error))

        return self.connected


    def disconnect(self):
        try:
            self.socket.shutdown(1)
            self.socket.close()
            self.connected = False
            logging.info("Socket closed.")
        except socket.error as error:
            logging.info("Unable to close socket. " + str(error))
            return False

        return True

    def send(self, msg):
        # for x in range(config.map_size['height']):
        #     logging.debug(map_virtual_w[x])

        if not self.connected:
            self.connect(self.host)

        if self.connected:
            logging.debug("[Info] Sending message: " + str(msg))
            try:
                self.socket.sendall(str.encode(msg))
            except socket.error as error:
                logging.info("Unable to send message. " + str(error))

    def get_msg(self):
        # Handle other events
        # while not general_queue.empty():
        #     msg = general_queue.get()
        #
        #     if msg[0] == DONE_TAKING_PICTURE:
        #         # TODO
        #         continue
        #     elif msg[:3] == START_EXPLORATION:
        #         self.handler.simulator.explore()
        #         continue
        #     elif msg[:3] == START_FASTEST_PATH:
        #         self.handler.simulator.findFP()
        #         continue
        #     elif msg[:3] == GET_MAP:
        #         # explored_hex, obstacles_hex = self.handler.map.create_map_descriptor()
        #         # json_str = "M{\"map\": [{\"length\": 300, \"explored\": \"" + explored_hex + "\", \"obstacle\": \"" + obstacles_hex + "\"}]}"
        #         # self.send(json_str)
        #         self.send_map()
        #         continue

        # Handle arduino events
        while arduino_queue.empty():
            sleep(0.05)

        msg = arduino_queue.get()
        return msg.split()

    def receive(self):
        msg = self.get_msg()

        # Straight line correction
        # if abs(convert_short(msg[1]) - convert_short(msg[0])) > 0:
        #     if abs(float(msg[1]) - float(msg[0])) < 3:
        #         angle = math.atan((convert_short(msg[1]) - convert_short(msg[0])) / 9)
        #         angle = math.degrees(angle)
        #
        #         if angle < 0:
        #             self.send('r' + str(int(abs(angle))) + '\n')
        #         else:
        #             self.send('l' + str(int(angle)) + '\n')
        #
        #         logging.debug('Straight line correction')
        #
        #         msg = self.get_msg()

        out = [convert_short(msg[2]),
               convert_short(msg[3]),
               convert_short(msg[4]),
               convert_short(msg[1]),
               convert_short(msg[0]),
               convert_long(msg[5])]

        return out

    def move(self, sense, ir, steps=1):
        # Calibration
        can_calibrate = self.handler.map.find_left_wall_or_obstacle(self.x, self.y, self.handler.robot.bearing)

        if can_calibrate:
            self.send('c\nf' + str(steps) + '\n')
        else:
            self.send('f' + str(steps) + '\n')

        self.send_map()

        if sense:
            while arduino_queue.qsize() < 1:
                sleep(0.1)

        super().move(sense, ir=False, steps=steps)
        if ir:
            self.take_image()

    def move_diag(self, steps=1):
        self.send('f' + str(steps) + '\n')
        self.send_map()
        super().move_diag(steps)

    def left(self, sense, ir):
        # rotate anticlockwise by 90 deg
        if ir:
            self.take_image(before_turn=True)

        self.send('l83\n')
        self.send_map()

        if sense:
            while arduino_queue.qsize() < 1:
                sleep(0.1)

        super().left(sense, ir=False)
        if ir:
            self.take_image()

    def right(self, sense, ir):
        # rotate clockwise by 90 deg
        if ir:
            self.take_image(before_turn=True)

        can_calibrate = self.handler.map.find_left_wall_or_obstacle(self.x, self.y, self.handler.robot.bearing)

        if can_calibrate:
            self.send('c\nr83\n')
        else:
            self.send('r83\n')
        self.send_map()

        if sense:
            while arduino_queue.qsize() < 1:
                sleep(0.1)

        super().right(sense, ir=False)
        if ir:
            self.take_image()

    def left_diag(self):
        self.send('l33\n')
        self.send_map()

        while arduino_queue.qsize() < 1:
            sleep(0.1)

        super().left_diag()

    def right_diag(self):
        self.send('r33\n')
        self.send_map()

        while arduino_queue.qsize() < 1:
            sleep(0.1)

        super().right_diag()

    def send_map(self):
        explored_hex, obstacles_hex = self.handler.map.create_map_descriptor()
        json_str = "M{\"map\": [{\"length\": 300, \"explored\": \"" + explored_hex + "\", \"obstacle\": \"" + \
                   obstacles_hex + "\"}], \"robotPosition\":[" + str(self.x) + ", " + str(
            self.y) + "," + self.convert_to_degrees() + "]}\n"
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

    def execute_fastest_path(self, movements):
        forward = 0
        forward_diag = 0
        agg_movements = ['g']

        for movement in movements:
            if movement == MOVEMENT.FORWARD:
                forward += 1
            elif movement == MOVEMENT.FORWARD_DIAG:
                forward_diag += 1
            else:
                if forward > 0:
                    agg_movements.append('f{:0>2d}'.format(forward))
                    forward = 0

                if forward_diag > 0:
                    agg_movements.append('h{:0>2d}'.format(forward_diag))
                    forward_diag = 0

                if movement == MOVEMENT.LEFT_DIAG:
                    agg_movements.append('l33')
                elif movement == MOVEMENT.RIGHT_DIAG:
                    agg_movements.append('r33')
                elif movement == MOVEMENT.LEFT:
                    agg_movements.append('l83')
                else:
                    agg_movements.append('r83')

        if forward > 0:
            agg_movements.append('f{:0>2d}'.format(forward))
        elif forward_diag > 0:
            agg_movements.append('h{:0>2d}'.format(forward_diag))

        agg_movements.append('\n')

        self.send(''.join(agg_movements))
        self.send_map()

        # super().execute_fastest_path(movements)
        return

    def take_image(self, before_turn=False):
        # logging.debug('Take image')
        try:
            first, second, third = super().take_image(before_turn)
            bearing = self.bearing
            if bearing == Bearing.NORTH:
                bearing = 'N'
            elif bearing == Bearing.EAST:
                bearing = 'E'
            elif bearing == Bearing.SOUTH:
                bearing = 'S'
            else:
                bearing = 'W'
            self.send('P[{},{}|{},{}|{},{}|{}]\n'.format(first[0], first[1], second[0], second[1], third[0], third[1], bearing))
        except:
            logging.debug("No obstacle. Don't worry")

    def calibrate(self):
        self.send('c\nc\n')
        super().calibrate()

    def signal_exploration_ended(self):
        self.send('N\n')