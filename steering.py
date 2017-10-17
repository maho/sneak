from math import radians

from kivy.factory import Factory
from kivy.properties import NumericProperty
from kivy.vector import Vector
from kivent_core.systems.gamesystem import GameSystem

import defs


class SteeringSystem(GameSystem):
    queue_len = NumericProperty(10)

    def __init__(self, *a, **kwa):
        super(SteeringSystem, self).__init__(*a, **kwa)
        self.touch = None

    def on_touch_up(self, __touch):
        self.touch = None

    def on_touch_down(self, touch):
        self.touch = touch

        # self.queue.append(touch.pos)
        # self.queue = self.queue[-self.queue_len:]

        # vec = Vector(self.queue[-1]) - self.queue[0]
        # self.angle = vec.angle((0, 100))

        # self.apply_angle()

        # if vec.length2() > (self.speed_threshold**2):
        #     self.speed = 5

    @classmethod
    def apply_angle_n_run(cls, entity, vector):
        entity.rotate.r = radians(vector.angle((0, 100)))
        v = vector.normalize()*defs.person_speed

        x, y = entity.position.pos
        entity.position.pos = (x + v.x, y + v.y)

    def update(self, _dt):
        if self.touch is None:
            return
        for comp in self.components:
            if comp is None:
                continue
            eid = comp.entity_id
            e = self.gameworld.entities[eid]

            p = e.position.pos
            vec = Vector(self.touch.pos) - p
            self.apply_angle_n_run(e, vec)


Factory.register('SteeringSystem', cls=SteeringSystem)
