from __future__ import (print_function, division, absolute_import)

from gl import *

from renderer import Program, RenderHandle, create_shader
from universe import Agent, Universe

def make_simple_program():
    """A universe doesn't normally need a program of its own, but this one is
    very simple
    """
    vertex_src = '''
    #version 330
    in vec3 in_pos;
    in vec3 in_color;
    out vec3 vs_color;
    void main(void)
    {
        vs_color = in_color;
        gl_Position = vec4(in_pos, 1.0);
    }
    '''
    frag_src = '''
    #version 330
    in vec3 vs_color;
    out vec4 out_color;
    void main(void)
    {
        out_color = vec4(vs_color,1.0);
    }
    '''
    p = Program(glCreateProgram(), 'simple_program')
    p.attach_shader(create_shader(vertex_src, GL_VERTEX_SHADER, 'vertex'))
    p.attach_shader(create_shader(frag_src, GL_FRAGMENT_SHADER, 'frag'))
    p.link()
    return p


def cook_triangle():
    program = make_simple_program()

    vertices = [
            1.0 , -1.0  ,0.0,
            -1.0 , -1.0 ,0.0,
            1.0  , 1.0  ,0.0,
            ]
    colors = [
            1.0 , 0.0 , 0.0,
            0.0 , 1.0 , 0.0,
            0.0 , 0.0 , 1.0,
            ]

    return RenderHandle.from_triangles(program, vertices, colors)


class TriangleAgent(Agent):
    '''This dude doesn't do much, but when drawn, it appears to be a triangle.
    Everytime he can, he proudly proclaims his existence
    '''
    def __init__(self):
        self.render_handles = [cook_triangle()]


    def get_render_handles(self):
        return self.render_handles


    def tick(self, dt):
        print('I am a triangle!')


class SimpleUniverse(Universe):
    'Nothing happens here, created for the sake of completeness...'
    def __init__(self):
        super(SimpleUniverse, self).__init__()
        self.triangle = TriangleAgent()

    def get_render_handles(self):
        return self.triangle.get_render_handles()

    def tick(self, dt):
        self.triangle.tick(dt)


################################################################################


def new(interface_class):
    """This is how we define a new game.
    interface_class can be a Desktop interface or a
    Rift interface, but we don't care. We just want to inherit from it.
    In this case, we do the only essential thing: Specifying a universe.
    """
    class SimpleGame(interface_class):
        def begin(self):
            super(SimpleGame, self).begin()
            self.universe = SimpleUniverse()
    return SimpleGame

