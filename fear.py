# pylint: disable=no-member,unused-variable
from functools import reduce
from math import radians, sqrt

from kivy.factory import Factory
from kivy.logger import Logger  # noqa: F401
from kivy.properties import NumericProperty
from kivy.vector import Vector as V
from kivent_core.systems.gamesystem import GameSystem
import numpy as np

import defs


def debug_F(f):
    w, h = f.shape
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_zlim(-10, 1000)
    X = np.arange(w)
    Y = np.arange(h)
    X, Y = np.meshgrid(X, Y)
    ax.plot_wireframe(X, Y, f, rstride=10, cstride=10)
    plt.show()


class Fear(GameSystem):
    granulity = NumericProperty(5)

    # static data
    pre_computed_fields = {}

    def init_component(self, cindex, eid, zone, args):
        if 'attraction' not in args:
            args['attraction'] = 1000
        if 'repulsion' not in args:
            args['repulsion'] = 1000

        super(Fear, self).init_component(cindex, eid, zone, args)
        comp = self.components[cindex]
        comp.courage = 1.0
        comp.field = self.calc_field(args['attraction'], args['repulsion'])
        comp.field_for_idx = (0, 0)

    def calc_field(self, attraction, repulsion):
        if (attraction, repulsion) in self.pre_computed_fields:
            return np.array(self.pre_computed_fields[attraction, repulsion])
        w, h = self.gameworld.gmap.size
        w //= self.granulity
        h //= self.granulity
        F = np.zeros((w, h))

        for i in range(-w//2, w//2):
            for j in range(-h//2, h//2):
                den2 = ((i/10)**2 + (j/10)**2)
                den = sqrt(den2)

                val = 0.0
                if repulsion and repulsion > 0:
                    if den2 == 0:
                        val += defs.inf
                    else:
                        val += repulsion / den2
                if attraction and attraction > 0:
                    if den == 0:
                        val -= defs.inf
                    else:
                        val -= attraction / 16 / den

                F[i, j] = val
        self.pre_computed_fields[attraction, repulsion] = F
        return F

    def roll_field_to_pos(self, comp, pos):
        """ roll field in component to position specified in pos """
        i, j = pos
        i = int(i/self.granulity)
        j = int(j/self.granulity)

        if (i, j) == comp.field_for_idx:
            return

        oi, oj = comp.field_for_idx

        comp.field = np.roll(comp.field, i-oi, axis=0)
        comp.field = np.roll(comp.field, j-oj, axis=1)

        comp.field_for_idx = (i, j)

    def combined_field(self):
        w, h = self.gameworld.gmap.size
        w //= self.granulity
        h //= self.granulity

        tosum = []

        for c in self.components:

            if not c.attraction and not c.repulsion:
                continue

            e = self.entity(c)
            p = e.position.pos

            self.roll_field_to_pos(c, p)
            tosum.append(c.field)

        F = reduce(np.add, tosum)
        return F

    @classmethod
    def speed_vector(cls, dx, dy):
        # return V(dx, dy).normalize() * defs.rat_speed
        return (dx * defs.rat_speed, dy * defs.rat_speed)

    def calc_move(self, F, p, _c):
        """
            F - field
            p - position in field
            c - component
        """
        oi, oj = int(p[0] / self.granulity), int(p[1] / self.granulity)
        w, h = F.shape

        ret = V(0.0, 0.0)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                i = oi - di
                j = oj - dj
                vx, vy = self.speed_vector(di, dj)
                if not (0 < i < w and 0 < j < h):
                    val = defs.inf
                else:
                    val = F[i, j]
                ret.x += vx*val
                ret.y += vy*val
        if ret.length2() < defs.calc_move_gradient_threshold:
            return V((0, 0))

        return ret

    def entity(self, comp):
        if comp is None:
            return None
        return self.gameworld.entities[comp.entity_id]

    def update(self, _dt):
        F = self.combined_field()

        for c in self.components:
            if c.attraction or c.repulsion:
                continue
            e = self.entity(c)
            p = e.position.pos

            vec = self.calc_move(F, p, c)

            if vec.length2() < defs.rat_speed:  # if no-move vector
                continue

            e.rotate.r = radians(vec.angle((0, 10)))
            e.position.pos = tuple(vec + e.position.pos)


Factory.register('Fear', cls=Fear)

if __name__ == '__main__':
    _f = np.arange(10000).reshape((100, 100))
    debug_F(_f)
