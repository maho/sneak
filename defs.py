import math

# game globals
map_size = (1000, 1000)

# characters
person_speed = 400
rat_speed = 100

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
