# pylint: disable=attribute-defined-outside-init
import cProfile
import os
from random import randint

from kivy.app import App
from kivy.uix.widget import Widget
# import kivent_core
from kivent_core.managers.resource_managers import texture_manager

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
                'fear': {'attraction': None}
            }, ['position', 'rotate', 'renderer', 'steering', 'fear'])

        # draw rats
        mapw, maph = self.gamemap.size
        for _x in range(100):
            self.gameworld.init_entity({
                'renderer': {'texture': 'rat',
                             'size':  (20, 20),
                             'render': True},
                'rotate': 0,
                'fear': {'attraction': None, 'repulsion': None},
                'position': (randint(0, mapw), randint(0, maph))},
                ['position', 'rotate', 'renderer', 'fear'])


class SneakApp(App):
    def on_start(self):
        self.profile = cProfile.Profile()
        self.profile.enable()
        pass

    def on_stop(self):
        self.profile.disable()
        self.profile.dump_stats('sneak.profile')
        pass


if __name__ == '__main__':
    if "DEBUG" in os.environ:
        def debug_signal_handler(__sig, __frame):
            import pudb
            pudb.set_trace()

        import signal
        signal.signal(signal.SIGINT, debug_signal_handler)

    SneakApp().run()
