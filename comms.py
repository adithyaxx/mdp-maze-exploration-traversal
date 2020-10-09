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
RESET = 'RS|'
DONE_TAKING_PICTURE = 'D'
STOP_IR = 'I'

ANDROID_CMDS = [
    START_EXPLORATION,
    START_FASTEST_PATH,
    GET_MAP,
    WAYPOINT,
    RESET
]


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
                        if msg == any(ANDROID_CMDS):
                            general_queue.put(msg)
                            logging.debug(
                                'Putting ' + msg + '(' + str(general_queue.qsize()) + ' items in queue)')
                        else:
                            arduino_queue.put(msg)
                            logging.debug(
                                'Putting ' + msg + '(' + str(arduino_queue.qsize()) + ' items in queue)')
                        time.sleep(0.05)

    def receive(self):
        try:
            msg = self.socket.recv(1024)
            return msg
        except socket.timeout:
            return ""
        except OSError:
            logging.debug('OS Error.')
            sys.exit()

    def send(self, msg):
        print("[Info] Sending message: ", msg)
        try:
            self.socket.sendall(str.encode(msg))
        except socket.error as error:
            print("Unable to send message. ", error)
