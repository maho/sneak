# pylint: disable=no-member,unused-variable,unused-import
from math import pi

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

    def init_component(self, cindex, eid, zone, args):
        if 'attraction' not in args:
            args['attraction'] = None
        if 'repulsion' not in args:
            args['repulsion'] = None
        if 'safety' not in args:
            args['safety'] = None
        if 'nomove' not in args:
            args['nomove'] = False

        super(Fear, self).init_component(cindex, eid, zone, args)
        comp = self.components[cindex]
        comp.courage = 1.0
        comp.stone_contact = False
        comp.rat_contact = False

    def on_add_system(self):
        gw = self.gameworld
        gw.phy.add_collision_handler(defs.coltype_rat,
                                                defs.coltype_stone,
                                                begin_func=self.rat_vs_stone_begin,
                                                separate_func=self.rat_vs_stone_end)

        gw.phy.add_collision_handler(defs.coltype_rat, defs.coltype_rat,
                                     begin_func=self.rat_vs_rat_begin,
                                     separate_func=self.rat_vs_rat_end)

    def arbiter2components(self, arbiter, coltype1, coltype2):
        s1, s2 = arbiter.shapes
        if s1.collision_type == coltype2:
            s1, s2 = s2, s1

        assert s1.collision_type, s2.collision_type == (coltype1, coltype2)
        e1, e2 = s1.body.data, s2.body.data

        c1, c2 = self.components[e1], self.components[e2]
        assert c1.entity_id == e1
        assert c2.entity_id == e2

        return c1, c2

    def rat_vs_rat_begin(self, _space, arbiter):
        c1, c2 = self.arbiter2components(arbiter, defs.coltype_rat, defs.coltype_rat)

        c1.rat_contact = True
        c2.rat_contact = True

        return True

    def rat_vs_rat_end(self, _space, arbiter):
        c1, c2 = self.arbiter2components(arbiter, defs.coltype_rat, defs.coltype_rat)

        c1.rat_contact = False
        c2.rat_contact = False

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

    def update(self, _dt):  # pylint: disable=too-many-locals

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
                vels += (vecs.T * c2.repulsion / dist2s / courages).T

        dvels = (vels.T / np.linalg.norm(vels, axis=1)).T * defs.rat_speed
        _angles = np.arctan2(dvels[:, 1], dvels[:, 0]) + pi / 2

        for c, e, (velx, vely), _angle in zip(comps, entities, dvels, _angles):
            if c.nomove:
                continue
            e.cymunk_physics.body.velocity = (velx, vely)
            e.rotate.r = _angle

        self.update_courages()

    def update_courages(self):
        for c in self.components:
            if c is None:
                continue
            # courage things
            if c.rat_contact:
                c.courage = min(defs.max_courage, c.courage * 1.02)
            else:
                c.courage *= 0.998


Factory.register('Fear', cls=Fear)
