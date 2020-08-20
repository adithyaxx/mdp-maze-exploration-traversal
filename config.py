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
    north=[['images/robot/front_left.png',
           'images/robot/front_center.png',
           'images/robot/front_right.png'],
           ['images/robot/center_left.png',
           'images/robot/center_center.png',
           'images/robot/center_right.png'],
           ['images/robot/back_left.png',
           'images/robot/back_center.png',
           'images/robot/back_right.png']],
    east=[['images/robot/back_left.png',
           'images/robot/center_left.png',
           'images/robot/front_left.png'],
           ['images/robot/back_center.png',
           'images/robot/center_center.png',
           'images/robot/front_center.png'],
           ['images/robot/back_right.png',
           'images/robot/center_right.png',
           'images/robot/front_right.png']],
    south=[['images/robot/back_right.png',
           'images/robot/back_center.png',
           'images/robot/back_left.png'],
           ['images/robot/center_right.png',
           'images/robot/center_center.png',
           'images/robot/center_left.png'],
           ['images/robot/front_right.png',
           'images/robot/front_center.png',
           'images/robot/front_left.png']],
    west=[['images/robot/front_right.png',
           'images/robot/center_right.png',
           'images/robot/back_right.png'],
           ['images/robot/front_center.png',
           'images/robot/center_center.png',
           'images/robot/back_center.png'],
           ['images/robot/front_left.png',
           'images/robot/center_left.png',
           'images/robot/back_left.png']]

)