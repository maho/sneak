import math
import os

# level specific data
map_size = (1000, 1000)
num_stones = 5
num_rats = 2


# characters
person_speed = 360
rat_speed = [90, 140]
rat_speed_incr = 1, 1.1
rat_turn_angle = math.radians(18)
max_courage = 5.5
min_contact_to_get_courage = 1

# gameplay things
freeze_time = 1
grace_time = 2
numrats_change = 3, 1.1  # on advance level, add, multipiler
numrats_limit = 200
numstones_change = 1, 1  # on advance level
mapsize_change = 200, 1  # on advance level
initial_lives = 3
lives_add = 1
max_lives = 4

# physics
coltype_person = 1
coltype_rat = 2
coltype_stone = 3

force_threshold = 5
person_attraction = 1000
person_repulsion = 2700
shout_repulsion = 20000
shout_time = 2.4
shout_delay = 5

# steering
angle_step = math.radians(7)
full_speed_accel = math.pi / 16
full_speed_touchvec = 100

# misc
inf = 1.0e10  # potential in place/tile of attraction/repulsion


if "DEBUG" in os.environ:
    num_rats = 10
    #force_threshold = 2
    initial_lives = 1

