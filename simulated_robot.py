from robot import *


class SimulatedRobot(Robot):
    def __init__(self, handler):
        super().__init__(handler)
        self.map = handler.map
        self.handler = handler

    def get_front_middle(self):
        detect_range = config.sensor_range['front_middle']
        robot_x, robot_y = self.handler.robot.get_location()
        direction = self.handler.robot.bearing
        if direction == Bearing.SOUTH:
            sensor_location = [robot_x, robot_y + 1]
            ret = self.get_sensor_data(sensor_location, Bearing.SOUTH, detect_range)
        elif direction == Bearing.NORTH:
            sensor_location = [robot_x, robot_y - 1]
            ret = self.get_sensor_data(sensor_location, Bearing.NORTH, detect_range)
        elif direction == Bearing.EAST:
            sensor_location = [robot_x + 1, robot_y]
            ret = self.get_sensor_data(sensor_location, Bearing.EAST, detect_range)
        elif direction == Bearing.WEST:
            sensor_location = [robot_x - 1, robot_y]
            ret = self.get_sensor_data(sensor_location, Bearing.WEST, detect_range)
        else:
            print("    [ERROR] Invalid direction!", sep='; ')
            return
        # return [sensor_location, ret]
        return ret

    def get_front_left(self):
        detect_range = config.sensor_range['front_left']
        robot_x, robot_y = self.handler.robot.get_location()
        direction = self.handler.robot.bearing
        if direction == Bearing.WEST:
            sensor_location = [robot_x - 1, robot_y + 1]
            ret = self.get_sensor_data(sensor_location, Bearing.WEST, detect_range)
        elif direction == Bearing.EAST:
            sensor_location = [robot_x + 1, robot_y - 1]
            ret = self.get_sensor_data(sensor_location, Bearing.EAST, detect_range)
        elif direction == Bearing.SOUTH:
            sensor_location = [robot_x + 1, robot_y + 1]
            ret = self.get_sensor_data(sensor_location, Bearing.SOUTH, detect_range)
        elif direction == Bearing.NORTH:
            sensor_location = [robot_x - 1, robot_y - 1]
            ret = self.get_sensor_data(sensor_location, Bearing.NORTH, detect_range)
        else:
            print("    [ERROR] Invalid direction!")
            return
        # return [sensor_location, ret]
        return ret

    def get_front_right(self):
        detect_range = config.sensor_range['front_right']
        robot_x, robot_y = self.handler.robot.get_location()
        direction = self.handler.robot.bearing
        if direction == Bearing.EAST:
            sensor_location = [robot_x + 1, robot_y + 1]
            return self.get_sensor_data(sensor_location, Bearing.EAST, detect_range)
        elif direction == Bearing.WEST:
            sensor_location = [robot_x - 1, robot_y - 1]
            return self.get_sensor_data(sensor_location, Bearing.WEST, detect_range)
        elif direction == Bearing.SOUTH:
            sensor_location = [robot_x - 1, robot_y + 1]
            return self.get_sensor_data(sensor_location, Bearing.SOUTH, detect_range)
        elif direction == Bearing.NORTH:
            sensor_location = [robot_x + 1, robot_y - 1]
            return self.get_sensor_data(sensor_location, Bearing.NORTH, detect_range)
        else:
            print("    [ERROR] Invalid direction!")

    def get_left(self):
        detect_range = config.sensor_range['left']
        robot_x, robot_y = self.handler.robot.get_location()
        direction = self.handler.robot.bearing
        if direction == Bearing.NORTH:
            sensor_location = [robot_x - 1, robot_y - 1]
            return self.get_sensor_data(sensor_location, Bearing.WEST, detect_range)
        elif direction == Bearing.SOUTH:
            sensor_location = [robot_x + 1, robot_y + 1]
            return self.get_sensor_data(sensor_location, Bearing.EAST, detect_range)
        elif direction == Bearing.WEST:
            sensor_location = [robot_x - 1, robot_y + 1]
            return self.get_sensor_data(sensor_location, Bearing.SOUTH, detect_range)
        elif direction == Bearing.EAST:
            sensor_location = [robot_x + 1, robot_y - 1]
            return self.get_sensor_data(sensor_location, Bearing.NORTH, detect_range)
        else:
            print("    [ERROR] Invalid direction!")

    def get_right(self):
        detect_range = config.sensor_range['right']
        robot_x, robot_y = self.handler.robot.get_location()
        direction = self.handler.robot.bearing
        if direction == Bearing.NORTH:
            sensor_location = [robot_x + 1, robot_y]
            return self.get_sensor_data(sensor_location, Bearing.EAST, detect_range)
        elif direction == Bearing.SOUTH:
            sensor_location = [robot_x - 1, robot_y]
            return self.get_sensor_data(sensor_location, Bearing.WEST, detect_range)
        elif direction == Bearing.WEST:
            sensor_location = [robot_x, robot_y - 1]
            return self.get_sensor_data(sensor_location, Bearing.NORTH, detect_range)
        elif direction == Bearing.EAST:
            sensor_location = [robot_x, robot_y + 1]
            return self.get_sensor_data(sensor_location, Bearing.SOUTH, detect_range)
        else:
            print("    [ERROR] Invalid direction!")

    def get_sensor_data(self, location, sensor_bearing, detect_range):
        # print('detect_range:', detect_range)
        dis = 0
        if sensor_bearing == Bearing.SOUTH:
            # while (within boundary) and (block is free) and (not exceeding sensor range)
            while location[1] + dis + 1 < 20 and self.map.is_free(location[0],
                                                                  location[1] + dis + 1) and dis < detect_range:
                dis += 1
        elif sensor_bearing == Bearing.NORTH:
            while location[1] - dis - 1 >= 0 and self.map.is_free(location[0],
                                                                  location[1] - dis - 1) and dis < detect_range:
                dis += 1
        elif sensor_bearing == Bearing.EAST:
            while location[0] + dis + 1 < 15 and self.map.is_free(location[0] + dis + 1,
                                                                  location[1]) and dis < detect_range:
                dis += 1
        elif sensor_bearing == Bearing.WEST:
            while location[0] - dis - 1 >= 0 and self.map.is_free(location[0] - dis - 1,
                                                                  location[1]) and dis < detect_range:
                dis += 1

        # print("dis=", dis)

        if dis > detect_range:
            dis = -detect_range

        # print("loc=", location, "sb=", sensor_bearing, "range=", detect_range, "steps=", dis)

        return dis

    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    #     Function get_all_sensor_data
    # ----------------------------------------------------------------------
    # return:
    #     a list containing all sensor datas following get_sensor_data() format
    #     the order is as follows:
    #         front_middle,
    #         front_left,
    #         front_right,
    #         left,
    #         right
    # ----------------------------------------------------------------------
    def receive(self):
        return [self.get_front_left(),
                self.get_front_middle(),
                self.get_front_right(),
                self.get_left(),
                self.get_right()]

    # ----------------------------------------------------------------------

    # # ----------------------------------------------------------------------
    # # a thread-safe queue implementation from Phyton
    # # a testing function
    # def execute_command(self):
    #     command_queue = queue.Queue()
    #     for x in self.command_sequence:
    #         command_queue.put(x)

    #     while not command_queue.empty():
    #         next_command = command_queue.get()
    #         self.event_buffer.put(next_command)
    #         print("Command: " + next_command)
    # # ----------------------------------------------------------------------

    # def send_sendsor_data(self):
    #     last_robot_location = []
    #     last_robot_direction = ''
    #     while True:
    #         self.map_info.map_lock.acquire()
    #         print("[Map Lock] Locked by ", threading.current_thread())
    #         print("[Map Info] Location: ", self.map_info.robot_location)
    #         print("[Map Info] Direction: ", self.map_info.robot_direction)
    #         print("[Map Info] Last location: ", last_robot_location)
    #         print("[Map Info] Last direction: ", last_robot_direction)
    #         if not (self.map_info.robot_location == last_robot_location and self.map_info.robot_direction == last_robot_direction):
    #             data_to_send = SensorData(self.map_info.get_robot_location(), self.map_info.get_robot_direction(),
    #                                       {'front_middle': self.get_front_middle(),
    #                                        'front_left': self.get_front_left(),
    #                                        'front_right': self.get_front_right(),
    #                                        'left': self.get_left(),
    #                                        'right': self.get_right()})
    #             last_robot_direction = self.map_info.get_robot_direction()
    #             last_robot_location = []+self.map_info.get_robot_location()
    #             print("Robot position updated!")
    #             # self.event_buffer_lock.acquire()
    #             print("[Sensor] Sending data to buffer")
    #             self.event_buffer.put(data_to_send)
    #             print("[Buffer] size = ", self.event_buffer.qsize())
    #             # self.event_buffer_lock.release()
    #         else:
    #             print("[Sensor] Robot is not moving")
    #         self.map_info.map_lock.release()
    #         print("[Map Lock] Released by ", threading.current_thread())
    #         print('[Thread] ', threading.current_thread(), 'Giving up control')
    #         time.sleep(1)
