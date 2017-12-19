import math

# level specific data
map_size = (1000, 1000)
num_stones = 5
num_rats = 400


# characters
person_speed = 360
rat_speed = (90, 140)
rat_turn_angle = math.radians(18)
max_courage = 4.0
min_contact_to_get_courage = 2

# gameplay things
freeze_time = 3
grace_time = 2
numrats_change = 5, 1.35  # on advance level, add, multipiler
numrats_limit = 400
numstones_change = 1, 1  # on advance level
mapsize_change = 200, 1  # on advance level
lives_add = 2
max_lives = 6

# physics
coltype_person = 1
coltype_rat = 2
coltype_stone = 3

force_threshold = 1.5
shout_repulsion = 20000
shout_time = 2.8

# steering
angle_step = math.radians(7)
full_speed_accel = math.pi / 16

# misc
inf = 1.0e10  # potential in place/tile of attraction/repulsion
