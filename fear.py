# pylint: disable=no-member,unused-variable,unused-import
from functools import partial
from math import pi
from random import randint
import time

from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Keyboard, Window
from kivy.factory import Factory
from kivy.logger import Logger  # noqa: F401
from kivent_core.systems.gamesystem import GameSystem
import numpy as np

import defs

# def debug_F(f):
#     w, h = f.shape
#     from matplotlib import pyplot as plt
#     from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
#     fig = plt.figure()
#     ax = fig.gca(projection='3d')
#     ax.set_zlim(-10, 1000)
#     X = np.arange(w)
#     Y = np.arange(h)
#     X, Y = np.meshgrid(X, Y)
#     ax.plot_wireframe(X, Y, f, rstride=10, cstride=10)
#     plt.show()


class Fear(GameSystem):
    # static data
    pre_computed_fields = {}

    def __init__(self, *a, **kwa):
        super(Fear, self).__init__(*a, **kwa)

        self.cummtime = 0.0

        EventLoop.window.bind(on_key_up=self.on_key_up)

    def init_component(self, cindex, eid, zone, args):
        if 'attraction' not in args:
            args['attraction'] = None
        if 'repulsion' not in args:
            args['repulsion'] = None
        if 'safety' not in args:
            args['safety'] = None
        if 'nomove' not in args:
            args['nomove'] = False
        if 'shout' not in args:
            args['shout'] = False
        args['is_rat'] = args.get('is_rat', False)

        args['orig_data'] = None

        super(Fear, self).init_component(cindex, eid, zone, args)
        comp = self.components[cindex]
        comp.courage = 1.0
        comp.stone_contact = False
        comp.rat_contact = 0
        comp.rat_speed = randint(*defs.rat_speed)  # used only for rats
        comp.anim_changed = False
        comp.shout_time = -1

    def on_key_up(self, _win, key, *_args, **_kwargs):
        code = Keyboard.keycode_to_string(Window._system_keyboard, key)

        if code != 'a':
            return

        self.shout()

    def on_add_system(self):
        gw = self.gameworld
        gw.phy.add_collision_handler(defs.coltype_rat,
                                                defs.coltype_stone,
                                                begin_func=self.rat_vs_stone_begin,
                                                separate_func=self.rat_vs_stone_end)

        gw.phy.add_collision_handler(defs.coltype_rat, defs.coltype_rat,
                                     begin_func=self.rat_vs_rat_begin,
                                     separate_func=self.rat_vs_rat_end)

    def entity2component(self, e, static={}):
        e2c = static
        try:
            return e2c[e]
        except KeyError:
            # recalc entity to components
            for c in self.components:
                if c is None:
                    continue
                e2c[c.entity_id] = c

            return e2c[e]

    def arbiter2components(self, arbiter, coltype1, coltype2):
        s1, s2 = arbiter.shapes
        if s1.collision_type == coltype2:
            s1, s2 = s2, s1

        assert s1.collision_type, s2.collision_type == (coltype1, coltype2)
        e1, e2 = s1.body.data, s2.body.data

        c1, c2 = self.entity2component(e1), self.entity2component(e2)
        assert c1.entity_id == e1
        assert c2.entity_id == e2

        return c1, c2

    def rat_vs_rat_begin(self, _space, arbiter):
        c1, c2 = self.arbiter2components(arbiter, defs.coltype_rat, defs.coltype_rat)

        c1.rat_contact += 1
        c2.rat_contact += 1

        return False

    def rat_vs_rat_end(self, _space, arbiter):
        c1, c2 = self.arbiter2components(arbiter, defs.coltype_rat, defs.coltype_rat)

        c1.rat_contact -= 1
        c2.rat_contact -= 1

        return True

    def rat_vs_stone_begin(self, _space, arbiter):
        crat, _ign = self.arbiter2components(arbiter, 2, 3)

        crat.stone_contact = True

        return True

    def rat_vs_stone_end(self, _space, arbiter):
        crat, _ign = self.arbiter2components(arbiter, 2, 3)
        crat.stone_contact = False

    def entity(self, comp):
        if comp is None:
            return None
        return self.gameworld.entities[comp.entity_id]

    def shout(self):


        def _fn(c, _dt):
            c.attraction, c.repulsion = c.orig_data
            c.orig_data = None

        for c in self.components:
            if c is None or not c.shout:
                continue
            if c.orig_data:
                continue
            if time.time() - c.shout_time < defs.shout_delay:
                continue

            self.gameworld.sound_manager.play('shout')

            c.orig_data = (c.attraction, c.repulsion)
            c.attraction = 0
            c.repulsion += defs.shout_repulsion
            c.shout_time = time.time()

            Clock.schedule_once(partial(_fn, c), defs.shout_time)

    def numpy_rotate_matrixes(self):
        for r in [-defs.rat_turn_angle, defs.rat_turn_angle]:
            c, s = np.cos(r), np.sin(r)
            yield np.array([c, -s, s, c]).reshape(2, 2)

    def update(self, dt):  # pylint: disable=too-many-locals
        sm = self.gameworld.sound_manager
        self.cummtime += dt
        if self.cummtime < 0:
            return
        self.cummtime -= 0.1

        comps = [c for c in self.components if c and self.entity(c)]

        N = len(comps)
        vels = np.zeros(N * 2).reshape(N, 2)
        entities = [self.entity(c) for c in comps]
        poss = np.array([e.position.pos for e in entities])
        courages = np.array([c.courage for c in comps])

        for c2 in comps:
            if c2.attraction is None and c2.repulsion is None and c2.safety is None:
                continue

            e2 = self.entity(c2)

            vecs = poss - e2.position.pos

            dist2s = np.sum(vecs**2, axis=1)

            if c2.safety:
                vels -= (vecs.T * c2.safety / dist2s / courages).T

            if c2.attraction:
                vels -= (vecs.T * c2.attraction / dist2s * courages).T

            if c2.repulsion:
                vels += (vecs.T * c2.repulsion**2 / dist2s**2 / courages).T

        norms = np.linalg.norm(vels, axis=1)
        desired_angles = np.arctan2(vels[:, 1], vels[:, 0]) + pi / 2
        runornots = norms > defs.force_threshold
        real_angles = np.array([e.rotate.r for e in entities])

        anglediffs = (desired_angles - real_angles + 3 * pi) % (2 * pi) - pi
        rat_speeds = np.where(runornots, np.array([c.rat_speed for c in comps]), 0)


        # FIXME: something wrong is here, it should be >, I have some mess with angle arithmetics
        # but apparently this "wrong" works well, while "right" have strange results (rats turns in wrong direction)
        real_angles = np.where(anglediffs < 0, real_angles + defs.rat_turn_angle,
                                                real_angles - defs.rat_turn_angle)

        # real_angles = np.array([1.5*pi] * N)

        final_vels = np.vstack((-np.sin(real_angles), np.cos(real_angles))) * rat_speeds

        for c, e, angle, runornot, (vx, vy) in zip(comps, entities, real_angles, runornots,
                                                                                final_vels.T):
            if c.nomove:
                continue

            if not runornot:
                if c.is_rat:
                    e.animation.animation = 'rat-still'
                    c.anim_changed = True
                continue

            if c.anim_changed:
                e.animation.animation = 'rat'
                c.anim_changed = False
                sm.play('rat')

            body = e.cymunk_physics.body

            body.angle = angle

            body.velocity = (vx, vy)

        self.update_courages()

    def update_courages(self):
        for c in self.components:
            if c is None:
                continue
            if c.nomove:
                continue
            # courage things
            # e = self.entity(c)
            if c.rat_contact >= defs.min_contact_to_get_courage:
                c.courage = min(defs.max_courage, c.courage * 1.02)
                # e.animation.name = 'rat-red'
            else:
                c.courage *= 0.998
                # e.renderer.texture_key = 'rat'


Factory.register('Fear', cls=Fear)
