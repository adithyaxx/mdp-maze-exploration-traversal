import socket
from robot import *


class RealRobot(Robot):
    # def __init__(self, map):
    #
    #     super().__init__(map)
    #     family = socket.AF_INET
    #     socket_type = socket.SOCK_STREAM
    #     self.socket = socket.socket(family, socket_type)
    #     self.socket.settimeout(1)
    #     self.connected = False
    #     self.connect()
    #
    # def connect(self):
    #     host = '192.168.12.12'
    #     port = 8008
    #     try:
    #         self.socket.connect((host, port))
    #     except Exception:
    #         print("[Error] Unable to establish connection.")
    #     else:
    #         self.connected = True
    #         print("[Info] Connection established.")
    #
    # def send(self, msg):
    #     if not self.connected:
    #         self.connect()
    #     if self.connected:
    #         print("[Info] Sending message: ", msg)
    #         try:
    #             self.socket.sendall(str.encode(msg))
    #         except Exception:
    #             print("[Error] Unable to send message. Connection loss.")
    #             # self.connected = False
    #
    # def receive(self):
    #     if not self.connected:
    #         self.connect()
    #     if self.connected:
    #         try:
    #             msg = self.socket.recv(1024)
    #             if msg:
    #                 msg_decoded = msg.decode()
    #                 print("[Info] Received: ", msg_decoded)
    #                 sensor_data_in_str = msg.split(',')
    #                 sensor_data = []
    #                 for data in sensor_data_in_str:
    #                     sensor_data.append(int(data))
    #                 return sensor_data
    #         except socket.timeout:
    #             print("[Info] No message received.")
    #     # else:
    #     #     print("[Error] Unable to receive message. Connection loss.")
    def __init__(self, handler):

        super().__init__(handler)
        family = socket.AF_INET
        socket_type = socket.SOCK_STREAM
        self.socket = socket.socket(family, socket_type)
        self.socket.settimeout(1)
        self.connected = False
        # self.connect()

    def convert_long(self, distance):
        distance = float(distance)

        if (0 <= distance and distance <= 9):
            return 0
        elif (9 < distance and distance <= 21):
            return 1
        elif (21 < distance and distance <= 32):
            return 2
        elif (32 < distance and distance <= 44):
            return 3
        elif (44 < distance and distance <= 54):
            return 4
        elif (54 < distance and distance <= 61):
            return 5
        return 6

    def convert_short(self, distance):
        distance = float(distance)

        if (0 <= distance and distance <= 10):
            return 0
        elif (10 < distance and distance <= 19):
            return 1
        elif (19 < distance and distance <= 29):
            return 2
        return 3

    def connect(self, host):

        self.host = host
        port = 1273
        try:
            self.socket.connect((host, port))
        except Exception:
            print("[Error] Unable to establish connection.")
            return False
        else:
            self.connected = True
            print("[Info] Connection established.")
            self.send('c')
            self.send('s')

        return self.connected

    def send(self, msg):
        if not self.connected:
            self.connect(self.host)
        if self.connected:
            print("[Info] Sending message: ", msg)
            try:
                self.socket.sendall(str.encode(msg))
            except Exception:
                print("[Error] Unable to send message. Connection loss.")
                # self.connected = False

    def receive(self):
        try:
            msg = self.socket.recv(1024)
            if msg:
                print("[Info] Received: ", msg.decode('cp1252'))
                msg = msg.split()

                # msg = [int(abs(float(x) // 100)) for x in msg]

                out = [self.convert_short(msg[2]),
                        self.convert_short(msg[3]),
                        self.convert_short(msg[4]),
                        self.convert_short(msg[1]),
                        self.convert_long(msg[5])]

                print(out)

                return out

                # For testing
                # return [3, 3, 3, 0, 5]
        except socket.timeout:
            print("No message is received.")
            self.send('s')
            return self.receive()
            # For testing
            # return [3, 3, 3, 0, 5]

        return []

    def move(self, steps=1):
        print('f' + str(steps))
        self.send('f' + str(steps))

    def left(self):
        # rotate anticlockwise by 90 deg
        self.bearing = Bearing.prev_bearing(self.bearing)
        print('L90')
        self.send('l90')

    def right(self):
        # rotate clockwise by 90 deg
        self.bearing = Bearing.next_bearing(self.bearing)
        print('R90')
        self.send('r90')
        # self.send('c')

    def left_diag(self):
        self.bearing = Bearing.prev_bearing_diag(self.bearing)
        print('L45')
        self.send('l45')

    def right_diag(self):
        self.bearing = Bearing.next_bearing_diag(self.bearing)
        print('R45')
        self.send('r45')
