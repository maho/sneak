import math

# level specific data
map_size = (1000, 1000)
num_stones = 1
num_rats = 10


# characters
person_speed = 400
rat_speed = 120
max_courage = 4.0

# gameplay things
freeze_time = 3
grace_time = 2
numrats_change = 10, 1.1  # on advance level, add, multipiler
numstones_change = 1, 1  # on advance level
mapsize_change = 200, 1  # on advance level
lives_add = 2
max_lives = 6
shout_range = 300

# physics
coltype_person = 1
coltype_rat = 2
coltype_stone = 3

force_threshold = 3

# steering
steering_min_dist = 50
angle_step = math.radians(6)

# misc
inf = 1.0e10  # potential in place/tile of attraction/repulsion
