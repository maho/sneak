import math

# level specific data
map_size = (800, 800)
num_stones = 3
num_rats = 2


# characters
person_speed = 400
rat_speed = 100
max_courage = 2.0

# gameplay things
freeze_time = 3
grace_time = 2
numrats_change = 1, 1.5  # on advance level, add, multipiler
numstones_change = 2, 1  # on advance level
mapsize_change = 100, 1  # on advance level

# physics
coltype_person = 1
coltype_rat = 2
coltype_stone = 3

# steering
steering_min_dist = 50
angle_step = math.radians(5)

# misc
inf = 1.0e10  # potential in place/tile of attraction/repulsion
calc_move_gradient_threshold = 0.5
