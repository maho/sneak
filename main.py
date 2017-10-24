# pylint: disable=attribute-defined-outside-init
import cProfile
import os
from random import randint

from kivy.app import App
from kivy.uix.widget import Widget
# import kivent_core
from kivent_core.managers.resource_managers import texture_manager

from defedict import defedict
import defs

texture_manager.load_atlas('assets/objects.atlas')


class SneakGame(Widget):
    def __init__(self, **kwargs):
        super(SneakGame, self).__init__(**kwargs)
        self.gameworld.init_gameworld(
            ['renderer', 'rotate', 'position', 'steering', 'cymunk_physics', 'fear'],
            callback=self.init_game)

    def init_game(self):
        self.setup_states()
        self.set_state()
        self.draw_some_stuff()

    # def update(self, __dt):
    #     self.gameworld.update(0.02)  # let's try fixed fps, to avoid physics engine mistakes

    def setup_states(self):
        self.gameworld.add_state(state_name='main',
                                 systems_added=['renderer', 'cymunk_physics'],
                                 systems_removed=[], systems_paused=[],
                                 systems_unpaused=['renderer', 'cymunk_physics'],
                                 screenmanager_screen='main')

    def set_state(self):
        self.gameworld.state = 'main'

    def draw_some_stuff(self):
        # draw person
        self.draw_person()
        self.draw_stones()
        self.draw_rats()

    def draw_person(self):
        self.gameworld.init_entity(
                        *defedict({
                                'renderer': {
                                    'texture': 'person',
                                    'size': (50, 50)
                                },
                                'cymunk_physics': {'vel_limit': 10,
                                                   'col_shapes': [{
                                                           'shape_type': 'circle',
                                                           'elasticity': 0.5,
                                                           'collision_type': defs.coltype_person,
                                                           'shape_info': {
                                                               'inner_radius': 0,
                                                               'outer_radius': 50,
                                                               'mass': 50,
                                                               'offset': (0, 0)
                                                           },
                                                           'friction': 1.0
                                                        }]},
                                'fear': {'attraction': 1000, 'nomove': True},
                             },
                             ['position', 'rotate', 'renderer', 'steering', 'fear',
                              'cymunk_physics'])
                       )

    def draw_stones(self):
        mapw, maph = self.gamemap.size
        # draw stones
        for _x in range(3):
            self.gameworld.init_entity(
                        *defedict({
                            'renderer': {'texture': 'stone',
                                         'size': (60, 60)},
                            'fear': {'nomove': True, 'safety': 1000},
                            'cymunk_physics': {'mass': 0,
                                               'col_shapes': [{
                                                       'shape_type': 'circle',
                                                       'elasticity': 0.5,
                                                       'collision_type': defs.coltype_stone,
                                                       'shape_info': {
                                                           'inner_radius': 0,
                                                           'outer_radius': 50,
                                                           'mass': 50,
                                                           'offset': (0, 0)
                                                       },
                                                       'friction': 1.0
                                                    }]},
                            'position': (randint(0, mapw), randint(0, maph))},
                            ['position', 'rotate', 'renderer', 'fear', 'cymunk_physics'])
                           )

    def draw_rats(self):
        mapw, maph = self.gamemap.size
        # draw rats
        for _x in range(100):
            self.gameworld.init_entity(
                        *defedict({
                            'renderer': {'texture': 'rat',
                                         'size': (20, 20)},
                            'fear': {},
                            'cymunk_physics': {'col_shapes': [{
                                                       'shape_type': 'circle',
                                                       'elasticity': 0.5,
                                                       'collision_type': defs.coltype_rat,
                                                       'shape_info': {
                                                           'inner_radius': 0,
                                                           'outer_radius': 15,
                                                           'mass': 50,
                                                           'offset': (0, 0)
                                                       },
                                                       'friction': 1.0
                                                    }]},
                            'position': (randint(0, mapw), randint(0, maph))},
                            ['position', 'rotate', 'renderer', 'fear', 'cymunk_physics'])
                           )


class SneakApp(App):
    def on_start(self):
        if "PROFILE" in os.environ:
            self.profile = cProfile.Profile()
            self.profile.enable()

    def on_stop(self):
        if "PROFILE" in os.environ:
            self.profile.disable()
            self.profile.dump_stats('sneak.profile')


if __name__ == '__main__':
    if "DEBUG" in os.environ:
        def debug_signal_handler(__sig, __frame):
            import pudb
            pudb.set_trace()

        import signal
        signal.signal(signal.SIGINT, debug_signal_handler)

    SneakApp().run()
