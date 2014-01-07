'''Uses all functionality provided by the classes in the interface module.
Draws a bouncing cube in perspective, desktop or vr; using a shader pipeline.
'''

from __future__ import (print_function, division, absolute_import)

from gl import *

import primitive


class HappyCube(primitive.Cube):
    def __init__(self):
        super(HappyCube, self).__init__()
        self.rot_vel = 0.1
        self.rotation = ((0.9, 0.7, -0.3), 0.0)
        self.translation = (0, 0, -3)
        self.cumtime = 0


    def tick(self, dt):
        self.cumtime += dt
        self.rotation = (
                self.rotation[0],
                self.rotation[1] + self.rot_vel*2*3.14*dt)


class HappyUniverse(primitive.PrimitiveUniverse):
    def render_prelude(self):
        super(HappyUniverse, self).render_prelude()
        glLineWidth(2.0)


def new(interface_class):
    """This is how we define a new game.
    interface_class can be a Desktop interface or a
    Rift interface, but we don't care. We just want to inherit from it.
    In this case, we do the only essential thing: Specifying a universe.
    """
    class SimpleGame(interface_class):
        def begin(self):
            super(SimpleGame, self).begin()
            self.universe = HappyUniverse(self.hmdinfo)
            self.universe.attach_primitive(HappyCube())

    return SimpleGame

