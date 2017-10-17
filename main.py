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

import fear, steering # noqa: E401

texture_manager.load_atlas('assets/objects.atlas')




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
