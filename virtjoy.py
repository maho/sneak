# from kivy.clock import Clock
from kivy.lang import Builder
# from kivy.logger import Logger
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector

from plyer import vibrator

Builder.load_string("""
<VirtualJoystick>:
    canvas:
        Color:
            rgba: 1, 0, 0, 0.3
        Ellipse:
            pos: self.center[0] - self.radius, self.center[1] - self.radius
            size: self.radius * 2, self.radius * 2
        Color:
            rgba: 0.5, 0.5, 0.0, 1.0
        Line:
            width: 8
            points: [self.center, self.touch]
        Color:
            rgba: 0.0, 0.5, 0.5, 0.4
        Ellipse:
            pos: self.center[0] - 15, self.center[1] - 15
            size: 30, 30
        Ellipse:
            pos: self.touch[0] - 15, self.touch[1] - 15
            size: 30, 30
""")


class VirtualJoystick(Widget):

    touch = ObjectProperty([-1999, -1999])
    radius = NumericProperty(10)

    def __init__(self, *args, **kwargs):
        super(VirtualJoystick, self).__init__(*args, **kwargs)
        self.touch = self.center[:]
        self.bind(size=self.update)
        self.bind(pos=self.update)

        # Clock.schedule_once(self.bind_update_pos)
        self.vec = Vector((0, 0))
        self.joystick_active = False

    def disable_joystick(self):
        self.pos = (-1000, -1000)
        self.joystick_active = False
        self.vec = Vector((0, 0))

    def update(self, *__args):
        self.radius = min(self.size[0], self.size[1]) / 2
        self.touch = self.center[:]

    # def bind_update_pos(self, _dt):
    #     if not self.parent:
    #         Clock.schedule_once(self.bind_update_pos)
    #         return
    #     self.parent.bind(size=self.update_pos)

    def update_pos(self, *_args):
        self.center_y = self.parent.center_y
        self.center_x = self.parent.width - self.width - 100

    def on_touch_up(self, touch):
        if "vjtouch" not in touch.ud:
            return
        self.touch = self.center[:]
        self.disable()

    def on_touch_down(self, touch):
        self.center = touch.pos
        self.joystick_active = True
        touch.ud["vjtouch"] = True

    def on_touch_move(self, touch):
        if "vjtouch" not in touch.ud:
            return
        vec = Vector(touch.pos) - Vector(self.center)

        vlen = vec.length()

        if vlen > self.radius:
            vec = vec.normalize() * self.radius

        stripsize = 0.2
        try:
            if vlen < self.radius * stripsize or \
               self.radius * (1.0 + stripsize) > vlen > self.radius:
                vibrator.vibrate(0.005)
        except NotImplementedError:
            pass

        self.touch = Vector(self.center) + vec

        self.vec = vec / self.radius
