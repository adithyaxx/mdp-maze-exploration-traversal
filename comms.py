import sys
import threading
import time
import logging
import random
import socket
from constants import arduino_queue, general_queue

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

START_EXPLORATION = 'ES|'
START_FASTEST_PATH = 'FS|'
GET_MAP = 'GM|'
WAYPOINT = 'WP|'
GET_ROBOT_POS = 'GR|'
DONE_TAKING_PICTURE = 'D'


class ListenerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, socket=None, handler=None,
                 args=(), kwargs=None, verbose=None):
        super(ListenerThread, self).__init__()
        self.target = target
        self.name = name
        self.socket = socket
        self.handler = handler

    def run(self):
        while True:
            if not arduino_queue.full():
                msges = self.receive()

                try:
                    msges = msges.decode('cp1252')
                except (UnicodeDecodeError, AttributeError):
                    pass

                for msg in msges.split('\n'):
                    if msg:
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
                            explored_hex, obstacles_hex = self.handler.map.create_map_descriptor()
                            json_str = "M{\"map\": [{\"length\": 300, \"explored\": \"{}\", \"obstacle\": \"{}\"}]}".format(
                                explored_hex, obstacles_hex)
                            self.send(json_str)
                            continue
                        elif msg[:3] == WAYPOINT:
                            waypoints = msg[3:].split('|')
                            self.handler.simulator.waypoint_x.set(waypoints[0])
                            self.handler.simulator.waypoint_y.set(waypoints[1])
                            continue
                        else:
                            arduino_queue.put(msg)
                            logging.debug(
                                'Putting ' + msg + '(' + str(arduino_queue.qsize()) + ' items in queue)')
                            time.sleep(0.1)

    def receive(self):
        try:
            msg = self.socket.recv(1024)
            return msg
        except socket.timeout:
            return ""
        except OSError:
            sys.exit()

    def send(self, msg):
        print("[Info] Sending message: ", msg)
        try:
            self.socket.sendall(str.encode(msg))
        except socket.error as error:
            print("Unable to send message. ", error)
