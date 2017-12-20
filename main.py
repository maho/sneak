# pylint: disable=attribute-defined-outside-init, wrong-import-position
# import cProfile

print("BEGBODY")

import os
from random import randint
import time


# from kivy.config import Config
# Config.set('kivy', 'log_level', 'debug')
# 
from kivy.app import App  # noqa: E402
from kivy.clock import Clock  # noqa: E402
from kivy.vector import Vector  # noqa: E402
from kivy.properties import NumericProperty, ObjectProperty  # noqa: E402
from kivy.uix.widget import Widget  # noqa: E402
import kivent_cymunk # noqa:

# if "DEBUG" in os.environ:
#     Config.set('graphics', 'width', '800')
#     Config.set('graphics', 'height', '400')


# import kivent_core
from kivent_core.managers.resource_managers import texture_manager  # noqa: E402

from defedict import defedict  # noqa: E402
import defs  # noqa: E402
import fear # noqa:
import steering # noqa:

texture_manager.load_atlas('assets/objects.atlas')


class SneakGame(Widget):  # pylint: disable=too-many-instance-attributes

    levelnum = NumericProperty(0)
    arrow_tip = ObjectProperty(None, allownone=True)
    arrow_angle = NumericProperty(30)
    num_stones_left = NumericProperty(0)

    def __init__(self, **kwargs):
        super(SneakGame, self).__init__(**kwargs)
        self.gameworld.init_gameworld(
            ['renderer', 'rotate', 'position', 'steering', 'cymunk_physics',
              'fear', 'animation'],
            callback=self.init_game)

        self.points = None
        self.lives = None
        self.person_eid = None
        self.stones_in_game = set()

        self.num_rats = defs.num_rats
        self.num_stones = defs.num_stones

        self.person_anim = 'walk'

        Clock.schedule_interval(self.update, 0.05)
        Clock.schedule_interval(self.update_arrow, 0.01)

    def init_game(self):
        self.setup_states()
        self.load_sounds()
        self.load_models()
        self.advance_level(reset=True)

    def load_sounds(self):
        sm = self.gameworld.sound_manager
        sm.load_sound("rat", "snd/rat.ogg", 20)
        sm.load_sound("fail", "snd/fail.ogg", 1)
        sm.load_sound("stone", "snd/stone.ogg", 20)
        sm.load_sound("shout", "snd/shout.ogg")

    def load_models(self):
        self.load_animation('walk', 50, 50, "person-walk-%02d", 12)
        self.load_animation('grace', 50, 50, "person-grace-%02d", 6)
        self.load_animation('rat', 19, 25, "rat-%d", 9, {0:0, 1:1, 2:2, 3:3,  # noqa: E231
                                                         4:4, 5:3, 6:2, 7:1, 8:0},  # noqa: E231
                                                         frame_duration=40)
        self.load_animation('rat-still', 19, 25, "rat-%s", 1, {0: 2}, frame_duration=1000)

    def load_animation(self, animname, w, h, pattern, nframes, framemap=None, frame_duration=50):
        if not framemap:
            framemap = {x:x for x in range(nframes)}
        mm = self.gameworld.model_manager
        for x in range(nframes):
            mm.load_textured_rectangle('vertex_format_4f', w, h, pattern % framemap[x], pattern % x)

        am = self.gameworld.animation_manager

        animation_frames = [{'texture': pattern % framemap[x],
                             'model': pattern % x,
                             'duration': frame_duration} for x in range(nframes)]
        am.load_animation(animname, nframes, animation_frames)

    def advance_level(self, reset=False):
        self.levelnum += 1

        if reset:
            self.points = 0
            self.lives = 3
            self.levelnum = 0
            self.num_rats = defs.num_rats
            self.num_stones = defs.num_stones
        else:
            radd, rmult = defs.numrats_change
            stoadd, stomult = defs.numstones_change
            mapadd, mapmult = defs.mapsize_change

            self.num_rats = min(int(self.num_rats * rmult + radd), defs.numrats_limit)
            self.num_stones = int(self.num_stones * stomult + stoadd)
            # self.gamemap.map_size = [int(x * mapmult + mapadd) for x in self.gamemap.map_size] # TODO
            self.lives = min(self.lives + defs.lives_add, defs.max_lives)

        self.gameworld.state = 'levelnum'

    def on_play(self):
        self.gameworld.state = 'main'
        self.draw_some_stuff()
        self.grace_timestamp = time.time() + defs.grace_time

    def update(self, __dt):
        currtime = time.time()
        if self.person_eid is None:
            return
        ent = self.gameworld.entities[self.person_eid]

        old_anim = self.person_anim
        if self.gameworld.state == 'fail' or currtime < self.grace_timestamp:
            self.person_anim = 'grace'
        else:
            speed = ent.cymunk_physics.body.speed
            if  speed > 80:
                self.person_anim = 'walk'
            else:
                self.person_anim = None

        if self.person_anim is None:
            ent.animation.current_frame_index = 0
        elif self.person_anim != old_anim:
            ent.animation.animation = self.person_anim

    def setup_states(self):
        self.gameworld.add_state(state_name='main',
                                 systems_added=['renderer', 'cymunk_physics', 'fear', 'animation'],
                                 systems_removed=[], systems_paused=[],
                                 systems_unpaused=['renderer', 'cymunk_physics', 'fear',
                                                    'animation'],
                                 screenmanager_screen='main')

        self.gameworld.add_state(state_name='fail',
                                 systems_added=[],
                                 systems_removed=[], systems_paused=['fear', 'cymunk_physics', 'animation'],
                                 systems_unpaused=[],
                                 screenmanager_screen='main')

        self.gameworld.add_state(state_name='levelnum',
                                 systems_added=[],
                                 systems_removed=[], systems_paused=['fear', 'cymunk_physics'],
                                 systems_unpaused=[],
                                 screenmanager_screen='levelnum')

        self.gameworld.add_state(state_name='gameover',
                                 systems_added=[],
                                 systems_removed=[], systems_paused=['fear', 'cymunk_physics'],
                                 systems_unpaused=[],
                                 screenmanager_screen='gameover')

    def draw_some_stuff(self):
        # draw person
        self.gameworld.clear_entities()
        self.draw_rats()
        self.draw_stones()
        self.draw_person()
        self.init_callbacks()

    def draw_person(self):
        if self.person_anim == None:
            self.person_anim = 'grace'
        self.person_eid = self.gameworld.init_entity(
                        *defedict({
                                'renderer': {
                                    'texture': 'person-walk-00',
                                    'model_key': 'person-walk-00',
                                    'size': (50, 50),
                                },
                                'cymunk_physics': {'vel_limit': 1000,
                                                   'col_shapes': [{
                                                           'shape_type': 'circle',
                                                           'elasticity': 0.5,
                                                           'collision_type': defs.coltype_person,
                                                           'shape_info': {
                                                               'inner_radius': 0,
                                                               'outer_radius': 15,
                                                               'mass': 50,
                                                               'offset': (0, 0)
                                                           },
                                                           'friction': 1.0
                                                        }]},
                                  'fear': {'attraction': defs.person_attraction, 
                                           'repulsion': defs.person_repulsion,
                                           'nomove': True, 'shout': True},
                                'animation': {'name': self.person_anim, 'loop': True},
                             },
                             ['position', 'rotate', 'renderer', 'steering', 'fear',
                              'cymunk_physics', 'animation'])
                       )
        self.camera.entity_to_focus = self.person_eid
        assert self.camera.focus_entity

    def draw_stones(self):
        self.stones_in_game = set()
        mapw, maph = defs.map_size  # self.gamemap.map_size # TODO
        # draw stones
        for _x in range(self.num_stones):
            seid = self.gameworld.init_entity(
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
                            'position': (randint(200, mapw - 200), randint(200, maph - 200))},
                            ['position', 'rotate', 'renderer', 'fear', 'cymunk_physics'])
                           )
            self.stones_in_game.add(seid)
        self.num_stones_left = len(self.stones_in_game)

    def draw_rats(self):
        mapw, maph = defs.map_size
        # draw rats
        for _x in range(self.num_rats):
            self.gameworld.init_entity(
                        *defedict({
                            'renderer': {'texture': 'rat-0',
                                         'size': (20, 20),
                                         'copy': True},
                            'fear': {'is_rat': True},
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
                            'animation': {'name': 'rat', 'loop': 'True'},
                            'position': (randint(0, mapw), randint(0, maph))},
                            ['position', 'rotate', 'renderer', 'fear', 'cymunk_physics', 'animation'])
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
        self.gameworld.sound_manager.play('fail')

        def _fn(_dt):
            self.gameworld.state = 'main'
            self.grace_timestamp = time.time() + defs.grace_time

        Clock.schedule_once(_fn, defs.freeze_time)

        return True

    def person_vs_stone(self, _space, arbiter):
        spe, ssto = arbiter.shapes
        if spe.collision_type == defs.coltype_stone:
            spe, ssto = ssto, spe

        esto = ssto.body.data

        Clock.schedule_once(lambda dt: self.gameworld.remove_entity(esto))

        self.points += 1
        self.stones_in_game.remove(esto)
        self.num_stones_left = len(self.stones_in_game)
        self.gameworld.sound_manager.play('stone')
        if not self.stones_in_game:
            self.advance_level()

        return True

    def update_arrow(self, _dt):
        mapw, maph = defs.map_size  # self.gamemap.map_size # TODO
        cw, ch = self.camera.size
        cw = float(cw)
        ch = float(ch)

        # NOTE: lines shouldn't be parallel to OX or OY axis, otherwise segment_intersection will be false-negative
        lines = [[(50, -100), (51, ch + 100)], 
                 [(-100, ch - 50), (cw + 100, ch - 51)],
                 [(cw - 51, ch + 100), (cw - 50, -100)],
                 [(cw + 100, 51), (- 100, 50)]]

        wcx, wcy = self.camera.get_camera_center()

        arrow_tip = None

        for v1, v2 in lines:
            #line of boundary in world coordinates
            wv1 = self.camera.convert_from_screen_to_world(v1)
            wv2 = self.camera.convert_from_screen_to_world(v2)

            #line from center camera to center of stones
            ws1 = (float(wcx), float(wcy))
            ws2 = (float(mapw/2), float(maph/2))

            #intersection between them
            intersection = Vector.segment_intersection(wv1, wv2, ws1, ws2)
            if intersection:
                arrow_tip = intersection
                self.arrow_angle = (Vector(ws2) - (ws1)).angle((0, 100))
                break

        self.arrow_tip = arrow_tip


class SneakApp(App):
    #
    # def on_start(self):
    #     if "PROFILE" in os.environ:
    #         import cProfile as profmod
    #         self.profile = profmod.Profile()
    #         self.profile.enable()

    # def on_stop(self):
    #     if "PROFILE" in os.environ:
    #         self.profile.disable()
    #         self.profile.dump_stats('sneak.profile')
    pass


print("ENDBODY")

if __name__ == '__main__':
    print("BEFORE")
    # if "DEBUG" in os.environ:
    #     def debug_signal_handler(__sig, __frame):
    #         import pudb
    #         pudb.set_trace()

    #     import signal
    #     signal.signal(signal.SIGINT, debug_signal_handler)

    SneakApp().run()
    print("AFTER")
