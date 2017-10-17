from kivy.factory import Factory
from kivy.vector import Vector as V
from kivent_core.systems.gamesystem import GameSystem


class Fear(GameSystem):
    PROBE_DIST = 3
    PROBE_ANGLE_DIST = 45
    MIN_GRADIENT = 0.1

    def init_component(self, cindex, eid, zone, args):
        super(Fear, self).init_component(cindex, eid, zone, args)
        self.components[cindex].courage = 1.0

    def entity(self, comp):
        if comp is None:
            return None
        return self.gameworld.entities[comp.entity_id]

    def update(self, _dt):
        for c in self.components:
            if c is None or c.role == 'danger':
                continue
            e = self.entity(c)

            p = e.position.pos
            points = [p] + [V((self.PROBE_DIST, 0)).rotate(x) + p
                            for x in range(0, 360, self.PROBE_ANGLE_DIST)]  # noqa: E127

            results = self.field_for_points(points)

            best_point = min(results, key=results.get)
            # gradient should be steep enough
            if results[best_point] < results[p] - self.MIN_GRADIENT:
                e.position.pos = best_point

    def field_for_points(self, points):
        # get dangers
        dangers = []
        for comp in self.components:
            if comp and comp.role == 'danger':
                dangers.append(self.entity(comp).position.pos)

        ret = {}
        for p in points:
            vp = 0.0
            for d in dangers:
                dist = V(p).distance(d)
                vp += 1000/dist
            ret[tuple(p)] = vp
        return ret


Factory.register('Fear', cls=Fear)
