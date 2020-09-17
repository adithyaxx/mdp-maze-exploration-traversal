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
            self.send('AR,PC,s')

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
                print("[Info] Received: ", msg.decode())
                msg = msg.split()
                msg = [int(abs(float(x) // 100)) for x in msg]
                print(msg)

                # return [msg[1], msg[2], msg[3], msg[0], msg[4]]

                # For testing
                return [3, 3, 3, 0, 5]
        except socket.timeout:
            print("No message is received.")

            # For testing
            return [3, 3, 3, 0, 5]

        return []

    def move(self, steps=1):
        self.send('AR,PC,f'+str(3))

    def left(self):
        # rotate anticlockwise by 90 deg
        self.bearing = Bearing.prev_bearing(self.bearing)
        print('L90')
        self.send('AR,PC,l90')

    def right(self):
        # rotate clockwise by 90 deg
        self.bearing = Bearing.next_bearing(self.bearing)
        print('R90')
        self.send('AR,PC,r90')

    def left_diag(self):
        self.bearing = Bearing.prev_bearing_diag(self.bearing)
        print('L45')
        self.send('AR,PC,l45')

    def right_diag(self):
        self.bearing = Bearing.next_bearing_diag(self.bearing)
        print('R45')
        self.send('AR,PC,r45')
