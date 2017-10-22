# pylint: disable=no-member,unused-variable
from functools import reduce
from math import radians, sqrt

from kivy.factory import Factory
from kivy.logger import Logger  # noqa: F401
from kivy.properties import NumericProperty
from kivy.vector import Vector
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
    granulity = NumericProperty(6)

    # static data
    pre_computed_fields = {}

    def init_component(self, cindex, eid, zone, args):
        if 'attraction' not in args:
            args['attraction'] = 1000
        if 'repulsion' not in args:
            args['repulsion'] = 1000
        if 'nomove' not in args:
            args['nomove'] = False

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

        G = 50/self.granulity

        for i in range(-w//2, w//2):
            for j in range(-h//2, h//2):
                den2 = ((i/G)**2 + (j/G)**2)
                den = sqrt(den2)

                val = 0.0
                if repulsion and repulsion > 0:
                    if den2 == 0:
                        val += defs.inf
                    else:
                        val += repulsion / 6 / den2
                if attraction and attraction > 0:
                    if den == 0:
                        val -= defs.inf
                    else:
                        val -= attraction / 8 / den

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

    def calc_move(self, gf, p, c):
        """
            gf - global field (including field of object)
            p - position in field
            c - component
        """

        F = np.add(gf, -c.field)  # field without own field

        oi, oj = int(p[0] / self.granulity), int(p[1] / self.granulity)
        w, h = F.shape

        retx, rety = 0.0, 0.0
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                i = oi - di
                j = oj - dj
                vx, vy = self.speed_vector(di, dj)
                if not (0 < i < w and 0 < j < h):
                    val = defs.inf
                else:
                    val = F[i, j]
                retx += vx*val
                rety += vy*val
        if abs(retx) + abs(rety) < defs.calc_move_gradient_threshold:
            return (0, 0)

        return retx, rety

    def entity(self, comp):
        if comp is None:
            return None
        return self.gameworld.entities[comp.entity_id]

    def update(self, _dt):
        F = self.combined_field()

        for c in self.components:
            if c.nomove:
                continue
            e = self.entity(c)
            px, py = e.position.pos

            vx, vy = self.calc_move(F, (px, py), c)

            if abs(vx) + abs(vy) < defs.rat_speed/2:  # if no move vector
                continue

            e.rotate.r = radians(Vector((vx, vy)).angle((0, 10)))
            e.position.pos = (vx + px, vy + py)


Factory.register('Fear', cls=Fear)

if __name__ == '__main__':
    _f = np.arange(10000).reshape((100, 100))
    debug_F(_f)
