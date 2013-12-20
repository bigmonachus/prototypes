'''Uses all functionality provided by the classes in the interface module.
Draws a bouncing cube in perspective, desktop or vr; using a shader pipeline.
'''

from __future__ import (print_function, division, absolute_import)

from gl import *
from glm import mat4x4, vec3

from interface import Interface
from renderer import Program, RenderHandle, create_shader, draw_handles
from universe import Agent, Universe

def make_persp_program():
    """A universe doesn't normally need a program of its own, but this one is
    very simple
    """
    rotation_src = '''
    mat4 rotation_matrix(vec3 p_axis, float angle)
    {
        vec3 axis = normalize(p_axis);
        float s = sin(angle);
        float c = cos(angle);
        float oc = 1.0 - c;

        return mat4(
        oc * axis.x * axis.x + c          , oc * axis.x * axis.y - axis.z * s ,
            oc * axis.z * axis.x + axis.y * s , 0.0   ,
        oc * axis.x * axis.y + axis.z * s , oc * axis.y * axis.y + c          ,
            oc * axis.y * axis.z - axis.x * s , 0.0   ,
        oc * axis.z * axis.x - axis.y * s , oc * axis.y * axis.z + axis.x * s ,
            oc * axis.z * axis.z + c          , 0.0   ,
        0.0                               , 0.0                               ,
            0.0                               , 1.0);
    }
    '''
    vertex_src = '''
    #version 330
    in vec3 in_pos;
    in vec3 in_color;

    out vec3 vs_color;

    struct Transform {
        vec3 axis;
        float angle;
        vec3 translation;
    };
    uniform Transform transform;

    uniform mat4 persp;

    mat4 rotation_matrix(vec3 p_axis, float angle);

    void main(void)
    {
        vs_color = in_color;
        gl_Position = persp * ((rotation_matrix(transform.axis, transform.angle) *
            vec4(in_pos,1.0)) + vec4(transform.translation, 0.0));
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
    p = Program(glCreateProgram(), 'simple_persp')
    p.attach_shader(create_shader(rotation_src, GL_VERTEX_SHADER, 'rotation'))
    p.attach_shader(create_shader(vertex_src, GL_VERTEX_SHADER, 'vertex'))
    p.attach_shader(create_shader(frag_src, GL_FRAGMENT_SHADER, 'frag'))
    p.link()

    #TODO: aspect ratio should be gotten from somewhere else
    persp_mat = mat4x4.perspective(75.0, 1280/800, 0.001, 10)

    p.set_uniform('persp', persp_mat)
    p.set_uniform('transform.axis', (1,0,0))
    p.set_uniform('transform.angle', (1.0, ))
    p.set_uniform('transform.translation', (0,0,-10))


    return p


def cook_cube():
    program = make_persp_program()

    u = 1.0

    # Repeating vertices because too lazy right now to render indexed arrays.
    vertices = [
            -u , -u  ,u,   # 1
            -u , u ,u,     # 2
            u  , -u  ,u,   # 3

            u  , -u  ,u,   # 3
            -u , u ,u,     # 2
            u  , u  ,u,    # 4

            u  , -u  ,u,   # 3
            u  , u  ,u,    # 4
            u  , -u  ,-u,  # 6

            u  , -u  ,-u,  # 6
            u  , u  ,u,    # 4
            u  , u  ,-u,   # 5

            u  , u  ,-u,   # 5
            -u  , u, -u,   # 8
            u  , -u  ,-u,  # 6

            u  , -u  ,-u,  # 6
            -u  , u, -u,   # 8
            -u  , -u  ,-u, # 7

            -u  , -u  ,-u, # 7
            -u  , u, -u,   # 8
            -u , u ,u,     # 2

            -u , u ,u,     # 2
            -u , -u  ,u,   # 1
            -u  , -u  ,-u, # 7

            -u  , -u  ,-u, # 7
            u  , -u  ,u,   # 3
            u  , -u  ,-u,  # 6

            u  , -u  ,u,   # 3
            -u  , -u  ,-u, # 7
            -u , -u  ,u,   # 1

            -u  , u, -u,   # 8
            u  , u  ,u,    # 4
            -u , u ,u,     # 2

            -u  , u, -u,   # 8
            u  , u  ,-u,   # 5
            u  , u  ,u,    # 4
            ]

    colors = [item for sublist in
            [[0.5 , 0.1 , 0.5] for n in xrange(36)] for item in sublist]

    return RenderHandle.from_triangles(program, vertices, colors)


class CubeAgent(Agent):
    def __init__(self):
        self.render_handles = [cook_cube()]


    def get_render_handles(self):
        return self.render_handles


    def tick(self, dt):
        pass


class SimpleUniverse(Universe):
    'Nothing happens here, created for the sake of completeness...'
    pass


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
            self.universe = SimpleUniverse(CubeAgent())
    return SimpleGame

