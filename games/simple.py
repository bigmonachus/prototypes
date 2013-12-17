'''Uses all functionality provided by the classes in the interface module.
Draws a bouncing cube in perspective, desktop or vr; using a shader pipeline.
'''

from __future__ import (print_function, division)

from interface import Interface

from pyglet.gl import *
import pyglet.graphics as gr

def new(interface_class):
    class SimpleGame(interface_class):
        def draw(self, eye):
            glClearColor(1,1,1,1)
            glClear(GL_COLOR_BUFFER_BIT)
            print(eye)

    return SimpleGame
