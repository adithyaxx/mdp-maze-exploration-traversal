import socket
from robot import *
from utils import *


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

    def connect(self, host):
        self.host = host

        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            print("Connection established.")
            self.send('c')
            self.send('s')
        except socket.error as error:
            self.connected = False
            print("Unable to establish connection. ", error)

        return self.connected

    def disconnect(self):
        try:
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

    def receive(self):
        try:
            msg = self.socket.recv(1024)
            if msg:
                print("Received values: ", msg.decode('cp1252'))
                msg = msg.split()

                out = [convert_short(msg[2]),
                       convert_short(msg[3]),
                       convert_short(msg[4]),
                       convert_short(msg[1]),
                       convert_long(msg[5])]

                print(out)

                return out
        except socket.timeout:
            print("No message is received.")
            self.send('s')
            return self.receive()

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
