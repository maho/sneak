from math import radians

from kivy.app import App
from kivy.factory import Factory
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector
# import kivent_core
from kivent_core.managers.resource_managers import texture_manager
from kivent_core.systems.gamesystem import GameSystem

texture_manager.load_atlas('assets/objects.atlas')


class SteeringSystem(GameSystem):
    queue_len = NumericProperty(10)

    def __init__(self, *a, **kwa):
        super(SteeringSystem, self).__init__(*a, **kwa)
        self.queue = []
        self.angle = 0

    def on_touch_move(self, touch):
        self.queue.append(touch.pos)
        self.queue = self.queue[-self.queue_len:]

        vec = Vector(self.queue[-1]) - self.queue[0]
        self.angle = vec.angle((0, 100))

    def update(self, _dt):
        for comp in self.components:
            eid = comp.entity_id

            e = self.gameworld.entities[eid]
            e.rotate.r = radians(self.angle)


Factory.register('SteeringSystem', cls=SteeringSystem)


class VelSystem(GameSystem):
    def update(self, dt):
        pass


Factory.register('VelSystem', cls=VelSystem)


class SneakGame(Widget):
    def __init__(self, **kwargs):
        super(SneakGame, self).__init__(**kwargs)
        self.gameworld.init_gameworld(
            ['renderer', 'rotate', 'position', 'vel'],
            callback=self.init_game)

    def init_game(self):
        self.setup_states()
        self.set_state()
        self.draw_some_stuff()

    def update(self, __dt):
        self.gameworld.update(0.02)  # let's try fixed fps, to avoid physics engine mistakes

    def setup_states(self):
        self.gameworld.add_state(state_name='main',
                                 systems_added=['renderer', 'vel'],
                                 systems_removed=[], systems_paused=[],
                                 systems_unpaused=['renderer', 'vel'],
                                 screenmanager_screen='main')

    def set_state(self):
        self.gameworld.state = 'main'

    def draw_some_stuff(self):
        self.gameworld.init_entity({
                'renderer': {
                    'texture': 'person',
                    'size': (50, 50),
                    'render': True
                },
                'rotate': 0,
                'steering': {},
                'position': (100, 100),
                'vel': {'vx': 10, 'vy': 10}
            }, ['position', 'vel', 'rotate', 'renderer', 'steering'])


class SneakApp(App):
    pass


if __name__ == '__main__':
    SneakApp().run()
