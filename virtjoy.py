from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector

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
        self.vec = Vector((0, 0))

    def update(self, *__args):
        self.radius = min(self.size[0], self.size[1]) / 2
        self.touch = self.center[:]
        Logger.debug("self.touch = %s", self.touch)

    def on_touch_up(self, __touch):
        self.touch = self.center[:]
        Logger.debug("self.touch = %s", self.touch)

    def on_touch_down(self, touch):
        self.on_touch_move(touch)

    def on_touch_move(self, touch):
        vec = Vector(touch.pos) - Vector(self.center)
        if vec.length2() > self.radius**2:
            vec = vec.normalize() * self.radius

        self.touch = Vector(self.center) + vec
        Logger.debug("self.touch = %s", self.touch)

        self.vec = vec / self.radius
