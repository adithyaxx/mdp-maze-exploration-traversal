from time import sleep
from tkinter import *
import tkinter.ttk as ttk
from tkinter import scrolledtext
from tkinter.filedialog import askopenfilename

import config
from comms import *
from constants import *
from handler import Handler
from map import *


class Simulator:
    def __init__(self):
        self.robot_simulation = True

        self.root = Tk()
        self.root.title("MDP Simulation")
        self.root.resizable(False, False)
        self.job = None

        self.map_start_end = PhotoImage(file=config.image_paths['red'])
        self.map_unexplored = PhotoImage(file=config.image_paths['gray'])
        self.map_obstacle_unexplored = PhotoImage(file=config.image_paths['blue'])
        self.map_free = PhotoImage(file=config.image_paths['green'])
        self.map_obstacle = PhotoImage(file=config.image_paths['pink'])

        self.handler = Handler(self)
        self.map = self.handler.map
        self.core = self.handler.core
        self.robot = self.handler.get_robot()
        self.robot_n = []
        self.robot_e = []
        self.robot_s = []
        self.robot_w = []
        for i in range(3):
            self.robot_n.append([])
            self.robot_e.append([])
            self.robot_s.append([])
            self.robot_w.append([])
            for j in range(3):
                self.robot_n[i].append(config.robot_grid['north'][i][j])
                self.robot_e[i].append(config.robot_grid['east'][i][j])
                self.robot_s[i].append(config.robot_grid['south'][i][j])
                self.robot_w[i].append(config.robot_grid['west'][i][j])

        t = Toplevel(self.root)
        t.title("Control Panel")
        t.geometry('+610+0')
        t.resizable(False, False)

        self.canvas = Canvas(self.root, width=40 * config.map_size['width'], height=40 * config.map_size['height'])
        self.canvas.pack()

        self.control_panel = ttk.Frame(t, padding=(10, 10))
        self.control_panel.grid(row=0, column=1, sticky="snew")

        control_pane_window = ttk.Panedwindow(self.control_panel, orient=VERTICAL)
        control_pane_window.grid(column=0, row=0, sticky=(N, S, E, W))
        parameter_pane = ttk.Frame(control_pane_window)
        action_pane = ttk.Frame(control_pane_window)
        # control_pane_window.add(parameter_pane, weight=4)
        # control_pane_window.add(action_pane, weight=1)
        parameter_pane.grid(column=0, row=0, sticky=(N, S, E, W))
        action_pane.grid(column=0, row=1, pady=(10, 0), sticky=(N, S, E, W))

        self.steps_per_second = StringVar()
        self.coverage_figure = StringVar()
        self.time_limit = StringVar()
        self.waypoint_x = StringVar()
        self.waypoint_y = StringVar()
        self.goal_x = StringVar()
        self.goal_y = StringVar()
        self.ip_addr = StringVar()

        explore_button = ttk.Button(action_pane, text='Explore', command=self.explore, width=30)
        explore_button.grid(column=0, row=0, sticky="ew")
        fastest_path_button = ttk.Button(action_pane, text='Fastest Path', command=self.findFP)
        fastest_path_button.grid(column=0, row=1, sticky="ew")
        move_button = ttk.Button(action_pane, text='Move', command=self.move)
        move_button.grid(column=0, row=2, sticky="ew")
        left_button = ttk.Button(action_pane, text='Left', command=self.left)
        left_button.grid(column=0, row=3, sticky="ew")
        right_button = ttk.Button(action_pane, text='Right', command=self.right)
        right_button.grid(column=0, row=4, sticky="ew")
        load_button = ttk.Button(action_pane, text='Load Map', command=self.load)
        load_button.grid(column=0, row=5, sticky="ew")
        reset_button = ttk.Button(action_pane, text='Reset', command=self.reset)
        reset_button.grid(column=0, row=6, sticky="ew")

        self.text_area = scrolledtext.ScrolledText(control_pane_window, wrap=WORD, width=35, height=10)
        self.text_area.grid(row=2, column=0, pady=(20, 10))

        step_per_second_label = ttk.Label(parameter_pane, text="Steps Per Second:")
        step_per_second_label.grid(column=0, row=0, sticky="ew")
        step_per_second_entry = ttk.Entry(parameter_pane, textvariable=self.steps_per_second, width=33)
        step_per_second_entry.grid(column=0, row=1, pady=(0, 10), sticky="ew")

        coverage_figure_label = ttk.Label(parameter_pane, text="Coverage Figure(%):")
        coverage_figure_label.grid(column=0, row=2, sticky="ew")
        coverage_figure_entry = ttk.Entry(parameter_pane, textvariable=self.coverage_figure)
        coverage_figure_entry.grid(column=0, row=3, pady=(0, 10), sticky="ew")

        time_limit_label = ttk.Label(parameter_pane, text="Time Limit(s):")
        time_limit_label.grid(column=0, row=4, sticky="ew")
        time_limit_entry = ttk.Entry(parameter_pane, textvariable=self.time_limit)
        time_limit_entry.grid(column=0, row=5, pady=(0, 10), sticky="ew")

        waypoint_label = ttk.Label(parameter_pane, text="Waypoint(x,y):")
        waypoint_label.grid(column=0, row=6, sticky="ew")
        waypoint_frame = ttk.Frame(parameter_pane)
        waypoint_x_entry = ttk.Entry(waypoint_frame, textvariable=self.waypoint_x, width=16)
        waypoint_y_entry = ttk.Entry(waypoint_frame, textvariable=self.waypoint_y, width=16)
        waypoint_frame.grid(column=0, row=7)
        waypoint_x_entry.grid(column=0, row=0, pady=(0, 10), sticky="w")
        waypoint_y_entry.grid(column=1, row=0, pady=(0, 10))

        goal_label = ttk.Label(parameter_pane, text="Goal(x,y):")
        goal_label.grid(column=0, row=8, sticky=EW)
        goal_frame = ttk.Frame(parameter_pane)
        goal_x_entry = ttk.Entry(goal_frame, textvariable=self.goal_x, width=16)
        goal_y_entry = ttk.Entry(goal_frame, textvariable=self.goal_y, width=16)
        goal_frame.grid(column=0, row=9)
        goal_x_entry.grid(column=0, row=0, pady=(0, 10), sticky=W)
        goal_y_entry.grid(column=1, row=0, pady=(0, 10))

        exploration_label = ttk.Label(parameter_pane, text="Exploration Algo:")
        exploration_label.grid(column=0, row=10, sticky=EW)
        self.exploration_dropdown = ttk.Combobox(parameter_pane, state="readonly",
                                                 values=["Left Wall Hugging", "Left Wall Hugging (Return Home)",
                                                         "Left Wall Hugging (Optimized, Return Home)",
                                                         "Image Recognition", "Image Recognition (Return Home)",
                                                         "Image Recognition (Partial, Return Home)"])
        self.exploration_dropdown.current(1)
        self.exploration_dropdown.grid(column=0, row=11, pady=(0, 10), sticky=EW)

        # self.return_home = BooleanVar()
        # return_home_checkbox = ttk.Checkbutton(parameter_pane, text="Return Home", variable=self.return_home, \
        #                                        onvalue=True, offvalue=False)
        # return_home_checkbox.grid(column=0, row=4)

        fp_algo_label = ttk.Label(parameter_pane, text="FP Algo:")
        fp_algo_label.grid(column=0, row=12, sticky=EW)
        self.fp_dropdown = ttk.Combobox(parameter_pane, state="readonly",
                                        values=["A* Search", "A* Search (With Diagonals)", "Left Wall Hugging"])
        self.fp_dropdown.current(1)
        self.fp_dropdown.grid(column=0, row=13, pady=(0, 10), sticky=EW)

        self.ip_addr.set('192.168.20.1')
        ip_addr_label = ttk.Label(parameter_pane, text="IP Address:")
        ip_addr_label.grid(column=0, row=14, sticky=EW)
        ip_addr_entry = ttk.Entry(parameter_pane, textvariable=self.ip_addr)
        ip_addr_entry.grid(column=0, row=15, pady=(0, 0), sticky=EW)

        self.connect_button = ttk.Button(parameter_pane, text='Connect', command=self.connect)
        self.connect_button.grid(column=0, row=16, pady=(0, 10), sticky=EW)

        self.coverage_figure.set(100)
        self.time_limit.set(3600)
        self.steps_per_second.set(-1)
        self.waypoint_x.set(0)
        self.waypoint_y.set(0)
        self.goal_x.set(13)
        self.goal_y.set(1)

        self.control_panel.columnconfigure(0, weight=1)
        self.control_panel.rowconfigure(0, weight=1)

        self.update_map(full=True)
        self.event_loop()
        self.root.mainloop()

    def event_loop(self):

        while not general_queue.empty():
            msg = general_queue.get()

            if msg[:3] == START_EXPLORATION:
                print('Starting exploration')
                self.explore()
                continue
            elif msg[:3] == START_FASTEST_PATH:
                self.findFP()
                continue
            elif msg[:3] == WAYPOINT:
                xy = msg.split('|')
                self.waypoint_x = int(xy[1])
                self.waypoint_y = abs(19 - int(xy[2]))
            elif msg[:3] == RESET:
                self.reset()
            elif msg[:3] == GET_MAP:
                self.robot.send_map()
                continue

        self.root.after(200, self.event_loop)

    def explore(self):
        self.core.explore(int(self.steps_per_second.get()), int(self.coverage_figure.get()),
                          int(self.time_limit.get()), self.exploration_dropdown.get())

    def findFP(self):
        self.core.findFP(int(self.steps_per_second.get()), int(self.goal_x.get()), int(self.goal_y.get()),
                         int(self.waypoint_x.get()), int(self.waypoint_y.get()), self.fp_dropdown.get())

    def update_cell(self, x, y):
        # Start & End box
        if ((0 <= y < 3) and (config.map_size['width'] - 3 <= x < config.map_size['width'])) or \
                ((config.map_size['height'] - 3 <= y < config.map_size['height']) and (0 <= x < 3)):
            color = 'gold'
        else:
            if map_is_explored[y][x] == 0:
                if map_sim[y][x] == 0:
                    color = 'gray64'
                else:
                    color = 'light pink'
            else:
                if self.map.is_free(x, y, False):
                    color = 'medium sea green'
                else:
                    color = 'red4'

        if not config.map_cells[y][x]:
            config.map_cells[y][x] = self.canvas.create_rectangle(x * 40, y * 40, x * 40 + 40, y * 40 + 40, fill=color)
            self.canvas.bind('<ButtonPress-1>', self.on_click)
        else:
            self.canvas.itemconfig(config.map_cells[y][x], fill=color)

    def on_click(self, event):
        x = event.x // 40
        y = event.y // 40

        if map_sim[y][x] == 0:
            map_sim[y][x] = 1
        else:
            map_sim[y][x] = 0
        self.update_cell(x, y)

    def put_robot(self, x, y, bearing):
        if bearing == Bearing.NORTH:
            front_coor = (x * 40 + 15, y * 40 - 10, x * 40 + 25, y * 40)
        elif bearing == Bearing.NORTH_EAST:
            front_coor = (x * 40 + 35, y * 40 - 5, x * 40 + 45, y * 40 + 5)
        elif bearing == Bearing.EAST:
            front_coor = (x * 40 + 40, y * 40 + 10, x * 40 + 50, y * 40 + 20)
        elif bearing == Bearing.SOUTH_EAST:
            front_coor = (x * 40 + 35, y * 40 + 35, x * 40 + 45, y * 40 + 45)
        elif bearing == Bearing.SOUTH:
            front_coor = (x * 40 + 15, y * 40 + 40, x * 40 + 25, y * 40 + 50)
        elif bearing == Bearing.SOUTH_WEST:
            front_coor = (x * 40 - 5, y * 40 + 35, x * 40 + 5, y * 40 + 45)
        elif bearing == Bearing.WEST:
            front_coor = (x * 40 - 10, y * 40 + 10, x * 40, y * 40 + 20)
        else:
            front_coor = (x * 40 - 5, y * 40 - 5, x * 40 + 5, y * 40 + 5)

        try:
            self.canvas.delete(self.robot_body)
            self.canvas.delete(self.robot_header)
        except:
            pass

        self.robot_body = self.canvas.create_oval(x * 40 - 20, y * 40 - 20, x * 40 + 60, y * 40 + 60,
                                                  fill="dodger blue", outline="")
        self.robot_header = self.canvas.create_oval(front_coor[0], front_coor[1], front_coor[2], front_coor[3],
                                                    fill="white", outline="")

    def update_map(self, radius=2, full=False):
        if full:
            y_range = range(config.map_size['height'])
            x_range = range(config.map_size['width'])
        else:
            y_range = range(
                max(0, self.robot.y - radius),
                min(self.robot.y + radius, config.map_size['height'] - 1) + 1
            )
            x_range = range(
                max(0, self.robot.x - radius),
                min(self.robot.x + radius, config.map_size['width'] - 1) + 1
            )

        for y in y_range:
            for x in x_range:
                try:
                    self.update_cell(x, y)
                except IndexError:
                    pass

        self.put_robot(self.robot.x, self.robot.y, self.robot.bearing)

    # Robot's movement manual control
    def move(self):
        self.handler.move(True, False)
        self.update_map()

    def left(self):
        self.handler.left(True, False)
        self.update_map()

    def right(self):
        self.handler.right(True, False)
        self.update_map()

    def reset(self):
        if self.job:
            self.root.after_cancel(self.job)
        while not arduino_queue.empty():
            arduino_queue.get()
        self.handler.reset()
        self.update_map(full=True)

    def connect(self):
        if self.connect_button.cget('text') == 'Connect':
            self.robot_simulation = False
            self.map.clear_map_for_real_exploration()
            self.update_map(full=True)
            if self.handler.connect(self.ip_addr.get()):
                self.robot = self.handler.get_robot()
                self.connect_button.config(text='Disconnect')
                return

        self.robot_simulation = True
        self.connect_button.config(text='Connect')
        self.handler.disconnect()
        self.handler = Handler(self)
        self.map = self.handler.map
        self.core = self.handler.core
        self.robot = self.handler.get_robot()

        self.reset()
        self.robot = self.handler.get_robot()

    def load(self):
        Tk().withdraw()
        filename = askopenfilename()

        f = open(filename, "r")

        self.map.decode_map_descriptor(f.readline())
        self.update_map(full=True)
