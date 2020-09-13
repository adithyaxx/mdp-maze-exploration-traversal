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

        # host = '127.0.0.1'
        port = 1273
        try:
            self.socket.connect((host, port))
        except Exception:
            print("[Error] Unable to establish connection.")
        else:
            self.connected = True
            print("[Info] Connection established.")

        return self.connected

    def send(self, msg):
        if not self.connected:
            self.connect()
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
                return
            return msg
        except socket.timeout:
            print("No message is received.")
