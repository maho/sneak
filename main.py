# pylint: disable=attribute-defined-outside-init, wrong-import-position
import cProfile
import os
from random import randint
import time


from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.widget import Widget

if "DEBUG" in os.environ:
    from kivy.config import Config
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '400')

# import kivent_core
from kivent_core.managers.resource_managers import texture_manager  # noqa: E402

from defedict import defedict  # noqa: E402
import defs  # noqa: E402

texture_manager.load_atlas('assets/objects.atlas')


class SneakGame(Widget):
    def __init__(self, **kwargs):
        super(SneakGame, self).__init__(**kwargs)
        self.gameworld.init_gameworld(
            ['renderer', 'rotate', 'position', 'steering', 'cymunk_physics',
              'fear', 'bounds'],
            callback=self.init_game)

        self.points = None
        self.lives = None
        self.person_eid = None
        self.grace_timestamp = time.time() + defs.grace_time
        Clock.schedule_interval(self.update, 0.05)

    def init_game(self):
        self.setup_states()
        self.on_play()

    def on_play(self):
        self.set_state()
        self.draw_some_stuff()

    def update(self, __dt):
        currtime = time.time()
        if self.person_eid is None:
            return

        ent = self.gameworld.entities[self.person_eid]
        if self.gameworld.state == 'fail' or currtime < self.grace_timestamp:
            idx = int(currtime * 20) % 10
            Logger.debug("in freeze time idx=%s", idx)
            ent.renderer.texture_key = "person-grace-%s" % idx
        elif ent.renderer.texture_key != 'person':
            ent.renderer.texture_key = 'person'

    def setup_states(self):
        self.gameworld.add_state(state_name='main',
                                 systems_added=['renderer', 'cymunk_physics', 'fear'],
                                 systems_removed=[], systems_paused=[],
                                 systems_unpaused=['renderer', 'cymunk_physics', 'fear'],
                                 screenmanager_screen='main')

        self.gameworld.add_state(state_name='fail',
                                 systems_added=[],
                                 systems_removed=[], systems_paused=['fear', 'cymunk_physics'],
                                 systems_unpaused=[],
                                 screenmanager_screen='main')

        self.gameworld.add_state(state_name='gameover',
                                 systems_added=[],
                                 systems_removed=[], systems_paused=['fear', 'cymunk_physics'],
                                 systems_unpaused=[],
                                 screenmanager_screen='gameover')

    def set_state(self):
        self.gameworld.state = 'main'

    def draw_some_stuff(self):
        # draw person
        self.gameworld.clear_entities()
        self.draw_stones()
        self.draw_rats()
        self.draw_person()
        self.init_callbacks()
        self.set_data()

    def set_data(self):
        self.points = 0
        self.lives = 4

    def draw_person(self):
        self.person_eid = self.gameworld.init_entity(
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
                                                               'outer_radius': 20,
                                                               'mass': 50,
                                                               'offset': (0, 0)
                                                           },
                                                           'friction': 1.0
                                                        }]},
                                'fear': {'attraction': 1000, 'nomove': True},
                             },
                             ['position', 'rotate', 'renderer', 'steering', 'fear',
                              'cymunk_physics', 'bounds'])
                       )
        self.camera.entity_to_focus = self.person_eid
        assert self.camera.focus_entity

    def draw_stones(self):
        mapw, maph = self.gamemap.map_size
        # draw stones
        for _x in range(defs.num_stones):
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
                                                           'outer_radius': 20,
                                                           'mass': 50,
                                                           'offset': (0, 0)
                                                       },
                                                       'friction': 1.0
                                                    }]},
                            'position': (randint(0, mapw), randint(0, maph))},
                            ['position', 'rotate', 'renderer', 'fear', 'cymunk_physics'])
                           )

    def draw_rats(self):
        mapw, maph = self.gamemap.map_size
        # draw rats
        for _x in range(defs.num_rats):
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
                            'position': (randint(0, mapw), randint(0, maph)),
                            'bounds': {'padding': 3.0}},
                            ['position', 'rotate', 'renderer', 'fear', 'cymunk_physics', 'bounds'])
                           )

    def init_callbacks(self):
        gw = self.gameworld
        gw.phy.add_collision_handler(defs.coltype_person,
                                                defs.coltype_stone,
                                                begin_func=self.person_vs_stone)

        gw.phy.add_collision_handler(defs.coltype_person,
                                                defs.coltype_rat,
                                                begin_func=self.person_vs_rat)

    def person_vs_rat(self, _space, _arbiter):

        if time.time() < self.grace_timestamp:
            return False

        self.lives -= 1

        if self.lives < 0:
            self.gameworld.state = 'gameover'
            return

        self.gameworld.state = 'fail'

        def _fn(_dt):
            self.gameworld.state = 'main'
            self.grace_timestamp = time.time() + defs.grace_time

        Clock.schedule_once(_fn, defs.freeze_time)

        return True

    def person_vs_stone(self, _space, arbiter):
        spe, ssto = arbiter.shapes
        if spe.collision_type == defs.coltype_stone:
            spe, ssto = ssto, spe

        sto = ssto.body.data

        Clock.schedule_once(lambda dt: self.gameworld.remove_entity(sto))

        self.points += 1

        return True


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
