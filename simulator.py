from tkinter import *
import tkinter.ttk as ttk
from tkinter import scrolledtext

import config
from constants import *
from handler import Handler


class Simulator:
    def __init__(self):
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
        action_pane.grid(column=0, row=1, pady=(20, 0), sticky=(N, S, E, W))

        self.steps_per_second = StringVar()
        self.coverage_figure = StringVar()
        self.time_limit = StringVar()
        self.waypoint_x = StringVar()
        self.waypoint_y = StringVar()
        self.goal_x = StringVar()
        self.goal_y = StringVar()

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
        reset_button = ttk.Button(action_pane, text='Reset', command=self.reset)
        reset_button.grid(column=0, row=5, sticky="ew")

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
        waypoint_x_entry = ttk.Entry(parameter_pane, textvariable=self.waypoint_x)
        waypoint_y_entry = ttk.Entry(parameter_pane, textvariable=self.waypoint_y)
        waypoint_x_entry.grid(column=0, row=7, pady=(0, 0), sticky="ew")
        waypoint_y_entry.grid(column=0, row=8, pady=(0, 10), sticky="ew")

        goal_label = ttk.Label(parameter_pane, text="Goal(x,y):")
        goal_label.grid(column=0, row=9, sticky=EW)
        goal_x_entry = ttk.Entry(parameter_pane, textvariable=self.goal_x)
        goal_y_entry = ttk.Entry(parameter_pane, textvariable=self.goal_y)
        goal_x_entry.grid(column=0, row=10, pady=(0, 0), sticky=EW)
        goal_y_entry.grid(column=0, row=11, pady=(0, 0), sticky=EW)

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
        self.root.mainloop()

    def explore(self):
        self.core.explore(int(self.steps_per_second.get()), int(self.coverage_figure.get()),
                          int(self.time_limit.get()))

    def findFP(self):
        self.core.findFP(int(self.goal_x.get()), int(self.goal_y.get()),
                         int(self.waypoint_x.get()), int(self.waypoint_y.get()))

    def update_cell(self, x, y):
        # Start & End box
        if ((0 <= y < 3) and (config.map_size['width'] - 3 <= x < config.map_size['width'])) or \
                ((config.map_size['height'] - 3 <= y < config.map_size['height']) and (0 <= x < 3)):
            color = 'gold'
        else:
            if self.map.map_is_explored[y][x] == 0:
                if self.map.map_sim[y][x] == 0:
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

        if self.map.map_sim[y][x] == 0:
            self.map.map_sim[y][x] = 1
        else:
            self.map.map_sim[y][x] = 0
        self.update_cell(x, y)

    def put_robot(self, x, y, bearing):
        if bearing == Bearing.NORTH:
            robot_color = self.robot_n
        elif bearing == Bearing.EAST:
            robot_color = self.robot_e
        elif bearing == Bearing.SOUTH:
            robot_color = self.robot_s
        else:
            robot_color = self.robot_w

        for i in range(3):
            for j in range(3):
                if not config.map_cells[y - 1 + i][x - 1 + j]:
                    config.map_cells[y - 1 + i][x - 1 + j] = self.canvas.create_rectangle((x - 1 + j) * 40,
                                                                                          (y - 1 + i) * 40,
                                                                                          ((x - 1 + j) * 40) + 40,
                                                                                          ((y - 1 + i) * 40) + 40,
                                                                                          fill=robot_color[i][j])
                else:
                    self.canvas.itemconfig(config.map_cells[y - 1 + i][x - 1 + j], fill=robot_color[i][j])

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
                self.update_cell(x, y)

        self.put_robot(self.robot.x, self.robot.y, self.robot.bearing)

    # Robot's movement manual control
    def move(self):
        self.handler.move()
        self.update_map()

    def left(self):
        self.handler.left()
        self.update_map()

    def right(self):
        self.handler.right()
        self.update_map()

    def reset(self):
        if self.job:
            self.root.after_cancel(self.job)
        self.handler.reset()
        self.update_map(full=True)
