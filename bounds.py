from kivy.factory import Factory
from kivy.logger import Logger
from kivent_core.systems.gamesystem import GameSystem


class Bounds(GameSystem):
    def update(self, _dt):
        mw, mh = self.gameworld.gmap.map_size

        for c in self.components:
            if c is None:
                continue
            e = self.gameworld.entities[c.entity_id]

            w, h = e.renderer.width, e.renderer.height
            nx, ny = x, y = e.position.pos

            if x < -w:
                nx = mw

            if x > mw + w:
                nx = 0

            if y < -h:
                ny = mh

            if y > mh + h:
                ny = 0

            if (x, y) != (nx, ny):
                e.cymunk_physics.body.position = (nx, ny)
                Logger.debug("set position to %s, %s", nx, ny)


Factory.register('Bounds', cls=Bounds)
