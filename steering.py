# pylint: disable=protected-access
from math import radians, degrees

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
        self.touch_base = None
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
                while True:
                    x, y, z = spatialorientation.orientation
                    if x and y and z:
                        break
                self.has_accel = True
            except (Exception) as e:  # pylint: disable=broad-except
                Logger.error("spatial not available? %s", e)
                self.has_accel = False
                cbox.active = False
        else:
            try:
                spatialorientation.disable_listener()
            except Exception:  # pylint: disable=broad-except
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
        self.touch_base = None
        self.touch = None

    def on_touch_down(self, touch):
        self.touch_base = touch.pos

    def on_touch_move(self, touch):
        self.touch = touch.pos

    def apply_run(self, entity, vector=None, full_speed_len=None):  # pylint: disable=no-self-use
        if vector:
            if full_speed_len:
                vlen = vector.length()
                speed = min(vlen / full_speed_len * defs.person_speed, defs.person_speed)
            else:
                speed = defs.person_speed
            v = vector.normalize() * speed
            entity.cymunk_physics.body.angle = radians(vector.angle((0, 1)))
        else:
            v = Vector((0, defs.person_speed)).rotate(degrees(entity.cymunk_physics.body.angle))

        entity.cymunk_physics.body.velocity = v

    def update(self, _dt):
        accel_vec = None
        if self.has_accel:
            _azimuth, pitch, roll = spatialorientation.orientation
            accel_vec = (-pitch, roll)

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
                self.apply_run(e)

            if accel_vec:
                vec = Vector(accel_vec)
                self.apply_run(e, vec, full_speed_len=defs.full_speed_accel)
            elif self.touch and self.touch_base:
                fx, fy = self.touch_base
                tx, ty = self.touch
                vec = Vector((tx - fx, ty - fy))
                self.apply_run(e, vec, full_speed_len=defs.full_speed_touchvec)


Factory.register('SneakSteeringSystem', cls=SneakSteeringSystem)
