from kivy.factory import Factory
from kivy.logger import Logger
from kivent_core.systems.gamesystem import GameSystem


class Bounds(GameSystem):
    def update(self, _dt):
        mw, mh = self.gameworld.gmap.map_size

        for c in self.components:
            if c is None:
                continue

            padding = getattr(c, "padding", 1.0)

            e = self.gameworld.entities[c.entity_id]

            w, h = e.renderer.width, e.renderer.height
            nx, ny = x, y = e.position.pos

            if x < padding * w:
                nx = mw - (padding + 1.) * w

            if x > mw - padding * w:
                nx = (padding + 1.) * w

            if y < padding * h:
                ny = mh - (padding + 1.) * h

            if y > mh - padding * h:
                ny = (padding + 1.) * h

            if (x, y) != (nx, ny):
                e.cymunk_physics.body.position = (nx, ny)
                Logger.debug("set position to %s, %s", nx, ny)


Factory.register('Bounds', cls=Bounds)
