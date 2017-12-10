from math import radians, degrees
import time

from kivy.base import EventLoop
from kivy.core.window import Keyboard, Window
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.vector import Vector
from kivent_core.systems.gamesystem import GameSystem
from plyer import accelerometer

import defs


class SneakSteeringSystem(GameSystem):
    queue_len = NumericProperty(10)

    def __init__(self, *a, **kwa):
        super(SneakSteeringSystem, self).__init__(*a, **kwa)
        self.touch = None
        self.keys_pressed = set()

        EventLoop.window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

        self.has_accel = True
        self.accel_base = None
        try:
            accelerometer.enable()
        except plyer.NotImplementedError:
            self.has_accel = False

    def init_component(self, cindex, eid, zone, args):
        super(SneakSteeringSystem, self).init_component(cindex, eid, zone, args)
        comp = self.components[cindex]

    def on_key_up(self, _win, key, *_args, **_kwargs):
        code = Keyboard.keycode_to_string(Window._system_keyboard, key)
        self.keys_pressed.remove(code)

    def on_key_down(self, __win, key, *__largs, **__kwargs):
        # very dirty hack, but: we don't have any instance of keyboard anywhere, and
        # keycode_to_string should be in fact classmethod, so passing None as self is safe
        code = Keyboard.keycode_to_string(Window._system_keyboard, key)
        self.keys_pressed.add(code)

    def on_touch_up(self, __touch):
        Logger.debug("on_touch_up, touch=%s", __touch)
        self.touch = None

    def on_touch_down(self, touch):
        self.touch = touch

    def apply_run(self, comp, entity, vector=None):
        if vector and vector.length2() < defs.steering_min_dist**2:
            return

        if vector:
            v = vector.normalize() * defs.person_speed
            entity.cymunk_physics.body.angle = radians(vector.angle((0, 1)))
        else:
            v = Vector((0, defs.person_speed)).rotate(degrees(entity.cymunk_physics.body.angle))

        Logger.debug("new_velocity = %0.2f, %0.2f", v.x, v.y)

        entity.cymunk_physics.body.velocity = v

    def update_accel_base(self):
        if not self.has_accel:
            return
        try:
            if not self.accel_base:
                x, y, z = accelerometer.acceleration[:3]
                if None in [x, y, z]:
                    return
                self.accel_base = x, y, z
        except Exception:
            Logger.error("no accel avail?")
            self.has_accel = False


    def update(self, _dt):

        self.update_accel_base()
       
        accel_vec = None
        if self.has_accel and self.accel_base:
            
            x, y, z = accelerometer.acceleration[:3]
            bx, by, bz = self.accel_base
            x -= bx
            y -= by
            z -= bz

            accel_vec = (y, -x)


        for comp in self.components:
            if comp is None:
                continue
            eid = comp.entity_id
            e = self.gameworld.entities[eid]
            body = e.cymunk_physics.body

            if 'left' in self.keys_pressed:
                body.angle += defs.angle_step
            if 'right' in self.keys_pressed:
                body.angle -= defs.angle_step
            if 'up' in self.keys_pressed:
                self.apply_run(comp, e)

            if accel_vec:
                vec = Vector(accel_vec)
                Logger.debug("accel_vec = %0.2f, %0.2f", vec.x, vec.y)
                self.apply_run(comp, e, vec)
            elif self.touch:
                p = e.position.pos
                tpos = self.camera.convert_from_screen_to_world(self.touch.pos)
                vec = Vector(tpos) - p
                self.apply_run(comp, e, vec)



Factory.register('SneakSteeringSystem', cls=SneakSteeringSystem)
