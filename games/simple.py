'''Uses all functionality provided by the classes in the interface module.
Draws a bouncing cube in perspective, desktop or vr; using a shader pipeline.
'''

from __future__ import (print_function, division, absolute_import)

from gl import *

from interface import Interface
from renderer import Program, RenderHandle, drawArrays
from universe import Agent, Universe


def cook():
    vertex_src = '''
    #version 330
    in vec3 in_pos;
    in vec3 in_color;
    out vec3 vs_color;
    void main(void)
    {
        vs_color = in_color;
        gl_Position = vec4(in_pos.x, in_pos.y, 0.0, 1.0);
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
    vs = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vs, [vertex_src])
    glCompileShader(vs)

    fs = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fs, [frag_src])
    glCompileShader(fs)

    p = glCreateProgram()
    glAttachShader(p, vs)
    glAttachShader(p, fs)
    glLinkProgram(p)

    glValidateProgram(p)
    ########################

    print('number of active attributes: ', glGetProgramiv(p, GL_ACTIVE_ATTRIBUTES))
    vertices = [
            1.0 , -1.0  ,
            -1.0 , -1.0 ,
            1.0  , 1.0  ,
            ]
    colors = [
            1.0 , 0.0 , 0.0,
            0.0 , 1.0 , 0.0,
            0.0 , 0.0 , 1.0,
            ]

    va = glGenVertexArrays(1)
    vbos =  glGenBuffers(2)

    attrib_locs = [
            glGetAttribLocation(p, "in_pos"),
            glGetAttribLocation(p, "in_color")
            ]
    print(attrib_locs)

    glBindVertexArray(va[0])
    for i in (0, 1):
        if attrib_locs[i] >= 0:
            glBindBuffer(GL_ARRAY_BUFFER, vbos[i])
            glBufferData(GL_ARRAY_BUFFER, GLfloat, (vertices, colors)[i], GL_STATIC_DRAW)
            glVertexAttribPointer(attrib_locs[i], (2, 3)[i], GL_FLOAT, GL_FALSE, 0, 0)
            glEnableVertexAttribArray(i)

    return RenderHandle(Program(p), va[0], 3)


def new(interface_class):
    class SimpleGame(interface_class):
        def begin(self):
            interface_class.begin(self)
            self.handle = cook()
            self.agent = Agent()
            self.universe = Universe(self.agent)

        def draw(self, eye):
            glClearColor(1,1,1,1)
            glClear(GL_COLOR_BUFFER_BIT)
            print(eye)
            drawArrays(self.handle)

    return SimpleGame
