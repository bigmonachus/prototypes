from __future__ import (print_function, division, absolute_import)


from gl import *
from glm import mat4x4

from interface import get_resolution
from render import Program, create_shader, RenderHandle
from universe import Agent, Universe


PROGRAM = None  # Lazily created when the first agent needs it.
ASPECT_RATIO = 1.0


def init_gl(with_ovr):
    global ASPECT_RATIO
    w, h = get_resolution()
    if not with_ovr:
        ASPECT_RATIO = w / h
    else:
        ASPECT_RATIO = int(w/2) / h
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


class Primitive(Agent):
    def __init__(self):
        super(Primitive, self).__init__()
        self.rotation = ((0, 1, 0), 0.0)
        self.translation = (0, 0, 0)
        self.render_handle = None

        global PROGRAM
        if not PROGRAM:
            PROGRAM = PrimitiveProgram()


    def get_render_handles(self):
        PROGRAM.set_uniform('transform.axis', self.rotation[0])
        PROGRAM.set_uniform('transform.angle', (self.rotation[1],))
        PROGRAM.set_uniform('transform.translation', self.translation)
        return [self.render_handle]


class Cube(Primitive):
    def __init__(self):
        super(Cube, self).__init__()
        self.rotation = ((0, 1, 0), 0.0)
        self.translation = (0, 0, 0)
        self._build_rhandle()


    def _build_rhandle(self):
        u = 1.0

        # Repeating vertices because too lazy to render indexed arrays.
        vertices = [
                -u , -u  ,u,   # 1
                -u , u ,u,     # 2
                u  , -u  ,u,   # 3

                u  , -u  ,u,   # 3
                -u , u , u,     # 2
                u  , u  ,u,    # 4

                u  , -u  , u,   # 3
                u  , u  , u,    # 4
                u  , -u  , -u,  # 6

                u  , -u  , -u,  # 6
                u  , u  , u,    # 4
                u  , u  , -u,   # 5

                u  , u  , -u,   # 5
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
                  [[0.5 , 0.1 , 0.5] for _ in xrange(36)]
                for item in sublist]

        self.render_handle = RenderHandle.from_triangles(
                PROGRAM, vertices, colors)


class PrimitiveUniverse(Universe):
    def __init__(self, hmdinfo):
        '''devinfo is an instance of HMDInfo or None. OVR setup
        is decided based on that.
        '''
        super(PrimitiveUniverse, self).__init__()
        global PROGRAM
        use_ovr = not hmdinfo is None

        init_gl(use_ovr)
        if PROGRAM is None:
            PROGRAM = PrimitiveProgram()
        self.program = PROGRAM
        self.primitives = []

        if use_ovr:
            self.hmdinfo = hmdinfo
    
    
    def attach_primitive(self, p):
        self.primitives.append(p)
    
    
    def get_render_handles(self):
        rhs = []
        for p in self.primitives:
            rhs.extend(p.get_render_handles())
        return rhs
    

    def tick(self, dt):
        for p in self.primitives:
            p.tick(dt)
    

    def render_prelude(self, eye):
        Universe.render_prelude(self, eye)
        glClearColor(1, 1, 1, 1)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        

class PrimitiveProgram(Program):
    def __init__(self):
        super(PrimitiveProgram, self).__init__(
                glCreateProgram(), 'primitive_program')
        rotation_src = '''
        mat4 rotation_matrix(vec3 p_axis, float angle)
        {
            vec3 axis = normalize(p_axis);
            float s = sin(angle);
            float c = cos(angle);
            float oc = 1.0 - c;

            return mat4(
            oc * axis.x * axis.x + c       , oc * axis.x * axis.y - axis.z * s ,
                oc * axis.z * axis.x + axis.y * s , 0.0   ,
            oc * axis.x * axis.y + axis.z * s , oc * axis.y * axis.y + c      ,
                oc * axis.y * axis.z - axis.x * s , 0.0   ,
            oc * axis.z * axis.x - axis.y * s,oc * axis.y * axis.z + axis.x * s,
                oc * axis.z * axis.z + c          , 0.0   ,
            0.0                               , 0.0                            ,
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
        uniform float eye_ipd;
        uniform float persp_offset;

        uniform mat4 persp;

        mat4 rotation_matrix(vec3 p_axis, float angle);

        void main(void)
        {
            vs_color = in_color;
            vec3 translation = transform.translation;

            mat4 vt = mat4(
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                eye_ipd, 0.0, 0.0, 1.0);

            mat4 translate = mat4(
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                translation.x, translation.y, translation.z, 1.0);

            mat4 view = translate *
                rotation_matrix(transform.axis, transform.angle);

            vec4 view_vec = vt * view * vec4(in_pos, 1.0);

            gl_Position = persp * view_vec;
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
        self.attach_shader(
                create_shader(rotation_src, GL_VERTEX_SHADER, 'rotation'))
        self.attach_shader(
                create_shader(vertex_src, GL_VERTEX_SHADER, 'vertex'))
        self.attach_shader(
                create_shader(frag_src, GL_FRAGMENT_SHADER, 'frag'))
        self.link()
        # Setup a default perspective matrix.
        self.set_uniform('persp',
                         mat4x4.perspective(75.0, ASPECT_RATIO, 0.001, 100))
