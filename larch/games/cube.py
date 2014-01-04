'''Uses all functionality provided by the classes in the interface module.
Draws a bouncing cube in perspective, desktop or vr; using a shader pipeline.
'''

from __future__ import (print_function, division, absolute_import)

from gl import *
from math import sin

import primitivelib
from interface import OVRInterface
from universe import Universe


USE_OVR = False


class HappyCube(primitivelib.Cube):
    def __init__(self):
        super(HappyCube, self).__init__()
        self.rot_vel = 0.5
        self.rotation = ((0.9, 0.7, -0.3), 0.0)
        self.translation = (0, 0, -10)
        self.cumtime = 0


    def tick(self, dt):
        self.cumtime += dt
        self.rotation = (
                self.rotation[0],
                self.rotation[1] + self.rot_vel*2*3.14*dt)
        self.translation = (
                self.translation[0],
                -5 + 9 * abs(sin(2 * self.cumtime)),
                self.translation[2],
                )


class MyUniverse(Universe):
    def __init__(self):
        super(MyUniverse, self).__init__()
        primitivelib.init_gl(USE_OVR)
        self.cube = HappyCube()
        self.program = primitivelib.PROGRAM


    def get_render_handles(self):
        # get_render_handles is implemented for all primitives in primitivelib
        self.render_prelude()
        return self.cube.get_render_handles()


    def render_prelude(self):
        glClearColor(1, 1, 1, 1)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    def tick(self, dt):
        self.cube.tick(dt)


################################################################################


def new(interface_class):
    """This is how we define a new game.
    interface_class can be a Desktop interface or a
    Rift interface, but we don't care. We just want to inherit from it.
    In this case, we do the only essential thing: Specifying a universe.
    """
    global USE_OVR
    if interface_class == OVRInterface:
        USE_OVR = True

    class SimpleGame(interface_class):
        def begin(self):
            super(SimpleGame, self).begin()
            self.universe = MyUniverse()
            if USE_OVR:
                self.universe.enable_ovr(self.devinfo)

    return SimpleGame

