from math import radians, cos, sin
from random import randint

from kivy.app import App
from kivy.factory import Factory
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector
# import kivent_core
from kivent_core.managers.resource_managers import texture_manager
from kivent_core.systems.gamesystem import GameSystem

import fear

texture_manager.load_atlas('assets/objects.atlas')


class SteeringSystem(GameSystem):
    queue_len = NumericProperty(10)
    speed_threshold = NumericProperty(20)

    def __init__(self, *a, **kwa):
        super(SteeringSystem, self).__init__(*a, **kwa)
        self.queue = []
        self.angle = 0
        self.speed = 0

    def on_touch_move(self, touch):
        self.queue.append(touch.pos)
        self.queue = self.queue[-self.queue_len:]

        vec = Vector(self.queue[-1]) - self.queue[0]
        self.angle = vec.angle((0, 100))

        self.apply_angle()

        if vec.length2() > (self.speed_threshold**2):
            self.speed = 5

    def apply_angle(self):
        for comp in self.components:
            eid = comp.entity_id

            e = self.gameworld.entities[eid]
            e.rotate.r = radians(self.angle)

    def apply_run(self, e):
        vx, vy = - self.speed * sin(radians(self.angle)), self.speed * cos(radians(self.angle))
        x, y = e.position.pos
        e.position.pos = (x + vx, y + vy)

    def update(self, _dt):
        for comp in self.components:
            eid = comp.entity_id
            e = self.gameworld.entities[eid]
            self.apply_run(e)
        self.speed /= 2


Factory.register('SteeringSystem', cls=SteeringSystem)


class SneakGame(Widget):
    def __init__(self, **kwargs):
        super(SneakGame, self).__init__(**kwargs)
        self.gameworld.init_gameworld(
            ['renderer', 'rotate', 'position', 'steering', 'fear'],
            callback=self.init_game)

    def init_game(self):
        self.setup_states()
        self.set_state()
        self.draw_some_stuff()

    def update(self, __dt):
        self.gameworld.update(0.02)  # let's try fixed fps, to avoid physics engine mistakes

    def setup_states(self):
        self.gameworld.add_state(state_name='main',
                                 systems_added=['renderer'],
                                 systems_removed=[], systems_paused=[],
                                 systems_unpaused=['renderer'],
                                 screenmanager_screen='main')

    def set_state(self):
        self.gameworld.state = 'main'

    def draw_some_stuff(self):
        # draw person
        self.gameworld.init_entity({
                'renderer': {
                    'texture': 'person',
                    'size': (50, 50),
                    'render': True
                },
                'rotate': 0,
                'steering': {},
                'position': (100, 100),
                'fear': {'role': 'danger'}
            }, ['position', 'rotate', 'renderer', 'steering', 'fear'])

        # draw rats
        mapw, maph = self.gamemap.size
        for _x in range(20):
            self.gameworld.init_entity({
                'renderer': {'texture': 'rat',
                             'size':  (20, 20),
                             'render': True},
                'rotate': 0,
                'fear': {'role': 'victim'},
                'position': (randint(0, mapw), randint(0, maph))},
                ['position', 'rotate', 'renderer', 'fear'])


class SneakApp(App):
    pass


if __name__ == '__main__':
    SneakApp().run()
