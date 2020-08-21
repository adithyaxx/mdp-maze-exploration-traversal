from tkinter import *
import tkinter.ttk as ttk
import config
from constants import *
from handler import Handler


class Simulator:
    def __init__(self):
        self.root = Tk()
        self.root.title("MDP Simulation")
        self.root.resizable(False, False)

        self.map_start_end = PhotoImage(file=config.image_paths['red'])
        self.map_unexplored = PhotoImage(file=config.image_paths['gray'])
        self.map_obstacle = PhotoImage(file=config.image_paths['blue'])
        self.map_safe_explored = PhotoImage(file=config.image_paths['green'])
        self.map_obstacle_explored = PhotoImage(file=config.image_paths['pink'])

        self.handler = Handler()
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
                self.robot_n[i].append(PhotoImage(file=config.robot_grid['north'][i][j]))
                self.robot_e[i].append(PhotoImage(file=config.robot_grid['east'][i][j]))
                self.robot_s[i].append(PhotoImage(file=config.robot_grid['south'][i][j]))
                self.robot_w[i].append(PhotoImage(file=config.robot_grid['west'][i][j]))

        t = Toplevel(self.root)
        t.title("Control Panel")
        t.geometry('190x360+600+28')
        t.resizable(False, False)

        self.map_panel = ttk.Frame(self.root, borderwidth=0, relief='solid')
        self.map_panel.grid(row=0, column=0, sticky="snew")

        self.control_panel = ttk.Frame(t, padding=(10, 10))
        self.control_panel.grid(row=0, column=1, sticky="snew")

        control_pane_window = ttk.Panedwindow(self.control_panel, orient=VERTICAL)
        control_pane_window.grid(column=0, row=0, sticky=(N, S, E, W))
        parameter_pane = ttk.Labelframe(control_pane_window, text='Parameters')
        action_pane = ttk.Labelframe(control_pane_window, text='Action')
        control_pane_window.add(parameter_pane, weight=4)
        control_pane_window.add(action_pane, weight=1)

        explore_button = ttk.Button(action_pane, text='Explore', width=16)
        explore_button.grid(column=0, row=0, sticky=(W, E))
        fastest_path_button = ttk.Button(action_pane, text='Fastest Path')
        fastest_path_button.grid(column=0, row=1, sticky=(W, E))
        move_button = ttk.Button(action_pane, text='Move', command=self.move)
        move_button.grid(column=0, row=2, sticky=(W, E))
        left_button = ttk.Button(action_pane, text='Left',  command=self.left)
        left_button.grid(column=0, row=3, sticky=(W, E))
        right_button = ttk.Button(action_pane, text='Right', command=self.right)
        right_button.grid(column=0, row=4, sticky=(W, E))

        step_per_second = StringVar()
        step_per_second_label = ttk.Label(parameter_pane, text="Step Per Second:")
        step_per_second_label.grid(column=0, row=0, sticky=W)
        step_per_second_entry = ttk.Entry(parameter_pane, textvariable=step_per_second)
        step_per_second_entry.grid(column=0, row=1, pady=(0, 10))

        coverage_figure = StringVar()
        coverage_figure_label = ttk.Label(parameter_pane, text="Coverage Figure(%):")
        coverage_figure_label.grid(column=0, row=2, sticky=W)
        coverage_figure_entry = ttk.Entry(parameter_pane, textvariable=coverage_figure)
        coverage_figure_entry.grid(column=0, row=3, pady=(0, 10))

        time_limit = StringVar()
        time_limit_label = ttk.Label(parameter_pane, text="Time Limit(s):")
        time_limit_label.grid(column=0, row=4, sticky=W)
        time_limit_entry = ttk.Entry(parameter_pane, textvariable=time_limit)
        time_limit_entry.grid(column=0, row=5, pady=(0, 10))

        # self.root.columnconfigure(0, weight=1)
        # self.root.rowconfigure(0, weight=1)
        self.control_panel.columnconfigure(0, weight=1)
        self.control_panel.rowconfigure(0, weight=1)

        # for i in range(10):
        #     map_pane.rowconfigure(i, weight=1)
        # for j in range(15):
        #     map_pane.columnconfigure(j, weight=1)

        # self.root.bind("<Left>", lambda e: self.left())
        # self.root.bind("<Right>", lambda e: self.right())
        # self.root.bind("<Up>", lambda e: self.move())
        # self.root.bind("<Down>", lambda e: self.back())

        for y in range(config.map_size['height']):
            for x in range(config.map_size['width']):
                if (self.robot.y - 1 <= y <= self.robot.y + 1 and
                        self.robot.x - 1 <= x <= self.robot.x + 1):
                    if y == self.robot.y and x == self.robot.x:
                        self.put_robot(x, y, self.robot.direction)
                else:
                    self.put_map(x, y)

        self.root.mainloop()

    def put_map(self, x, y):
        # Start & End box
        if ((0 <= y < 3) and (config.map_size['width'] - 3 <= x < config.map_size['width'])) or \
                ((config.map_size['height'] - 3 <= y < config.map_size['height']) and (0 <= x < 3)):
            map_image = self.map_start_end
        else:
            if config.map_explored[y][x] == 0:
                map_image = self.map_unexplored
            elif config.map_explored[y][x] == 1:
                map_image = self.map_obstacle
            elif config.map_explored[y][x] == 2:
                map_image = self.map_safe_explored
            else:
                map_image = self.map_obstacle_explored

        # Change map
        cell = Label(self.map_panel, image=map_image, borderwidth=1)
        cell.bind('<Button-1>', lambda e, i=x, j=y: self.on_click(i, j, e))
        try:
            self.map_panel[x][y].destroy()
        except Exception:
            pass
        cell.grid(column=x, row=y)
        config.map_cells[y][x] = cell

    def on_click(self, x, y, event):
        if config.map_explored[y][x] == 0:
            config.map_explored[y][x] = 1
        else:
            config.map_explored[y][x] = 0
        self.put_map(x, y)

    def put_robot(self, x, y, direction):
        if direction == Direction.NORTH:
            robot_label = self.robot_n
        elif direction == Direction.EAST:
            robot_label = self.robot_e
        elif direction == Direction.SOUTH:
            robot_label = self.robot_s
        else:
            robot_label = self.robot_w

        for i in range(3):
            for j in range(3):
                cell = Label(self.map_panel, image=robot_label[i][j], borderwidth=1)
                try:
                    self.map_panel[x-1+j][y-1+i].destroy()
                except Exception:
                    pass
                cell.grid(column=x-1+j, row=y-1+i)

    #rerender only 25 grids
    def update_map(self):
        for y in range(config.map_size['height']):
            for x in range(config.map_size['width']):
                if (self.robot.y - 2 <= y <= self.robot.y + 2 and
                        self.robot.x - 2 <= x <= self.robot.x + 2):
                    self.put_map(x, y)

        self.put_robot(self.robot.x, self.robot.y, self.robot.direction)

    #Robot's movement

    def move(self):
        self.handler.move()
        self.update_map()

    def left(self):
        self.handler.left()
        self.update_map()

    def right(self):
        self.handler.right()
        self.update_map()


# def start():
#     for i, row in enumerate(board):
#         for j, column in enumerate(row):
#             L = Label(left_frame, text='     ', bg='grey', borderwidth=0.5, relief='solid')
#             L.grid(row=i + 1, column=j)
#             L.bind('<Button-1>', lambda e, i=i, j=j: on_click(i, j, e))
#
#     n = StringVar()
#     selection = ttk.Combobox(right_frame, width=25, textvariable=n, font=("Fixed", 16))
#     selection['values'] = ('Exploration', 'Find Fastest Path')
#     selection.grid(row=0)
#
#     root.mainloop()

x = Simulator()