map_size = dict(
    height=20,
    width=15
)

# ----------------------------------------------------------------------
#   Map Legend:
#   0 - unexplored
#   1 - unexplored, obstacle
#   2 - explored, safe
#   3 - explored, obstacle
# ----------------------------------------------------------------------

empty_map = \
    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

map_explored = \
    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
     [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
     [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
     [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
map_cells = [[None for _ in range(map_size['width'])] for _ in range(map_size['height'])]

image_paths = dict(
    blue='images/blue.gif',
    gray='images/gray.gif',
    green='images/green.gif',
    light_blue='images/light_blue.gif',
    light_green='images/light_green.gif',
    pink='images/pink.gif',
    red='images/red.gif',
    yellow='images/yellow.gif'
)

robot_grid = dict(
    north=[['images/robot/north/front_left.png',
           'images/robot/north/front_center.png',
           'images/robot/north/front_right.png'],
           ['images/robot/north/center_left.png',
           'images/robot/north/center_center.png',
           'images/robot/north/center_right.png'],
           ['images/robot/north/back_left.png',
           'images/robot/north/back_center.png',
           'images/robot/north/back_right.png']],
    east=[['images/robot/east/1.png',
           'images/robot/east/2.png',
           'images/robot/east/3.png'],
           ['images/robot/east/4.png',
           'images/robot/east/5.png',
           'images/robot/east/6.png'],
           ['images/robot/east/7.png',
           'images/robot/east/8.png',
           'images/robot/east/9.png']],
    south=[['images/robot/south/1.png',
           'images/robot/south/2.png',
           'images/robot/south/3.png'],
          ['images/robot/south/4.png',
           'images/robot/south/5.png',
           'images/robot/south/6.png'],
          ['images/robot/south/7.png',
           'images/robot/south/8.png',
           'images/robot/south/9.png']],
    west=[['images/robot/west/1.png',
           'images/robot/west/2.png',
           'images/robot/west/3.png'],
           ['images/robot/west/4.png',
           'images/robot/west/5.png',
           'images/robot/west/6.png'],
           ['images/robot/west/7.png',
           'images/robot/west/8.png',
           'images/robot/west/9.png']],

)

# TODO: Distinguish between start , goal and obstacle. Robot cannot enter start/goal now because the areas are marked as wall