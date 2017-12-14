from math import radians, degrees
import time

from kivy.base import EventLoop
from kivy.core.window import Keyboard, Window
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.vector import Vector
from kivent_core.systems.gamesystem import GameSystem
from plyer import spatialorientation

import defs


class SneakSteeringSystem(GameSystem):
    queue_len = NumericProperty(10)

    def __init__(self, *a, **kwa):
        super(SneakSteeringSystem, self).__init__(*a, **kwa)
        self.touch = None
        self.keys_pressed = set()

        EventLoop.window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

        self.has_accel = False
        self.accel_base = None

    def set_accelerometer(self, cbox):
        active = cbox.active
        if active:
            try:
                spatialorientation.enable_listener()
                # while True:
                #     self.accel_base = spatialorientation.acceleration
                #     Logger.debug("accel base=%s", self.accel_base)
                #     if self.accel_base and self.accel_base[0] is not None:
                #         break
                self.has_accel = True
            except Exception, e:
                Logger.error("spatial not available? %s", e)
                self.has_accel = False
                cbox.active = False
        else:
            try:
                spatialorientation.disable_listener()
            except Exception:
                pass
            self.has_accel = False


    def on_key_up(self, _win, key, *_args, **_kwargs):
        code = Keyboard.keycode_to_string(Window._system_keyboard, key)
        self.keys_pressed.remove(code)

    def on_key_down(self, __win, key, *__largs, **__kwargs):
        # very dirty hack, but: we don't have any instance of keyboard anywhere, and
        # keycode_to_string should be in fact classmethod, so passing None as self is safe
        code = Keyboard.keycode_to_string(Window._system_keyboard, key)
        self.keys_pressed.add(code)

    def on_touch_up(self, __touch):
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

        entity.cymunk_physics.body.velocity = v

    def update(self, _dt):
        accel_vec = None
        if self.has_accel:
            
            azimuth, pitch, roll = spatialorientation.orientation

            Logger.debug("az, pitch, roll = %s, %s, %s", azimuth, pitch, roll)
            accel_vec = (pitch, roll)


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
