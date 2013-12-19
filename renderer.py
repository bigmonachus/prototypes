from __future__ import (print_function, division, absolute_import)


from gl import *

from options import renderer_options


CURRENT_PROGRAM = 0


def create_shader(src, gl_type):
    'src is a string. gl_type is GL_VERTEX_SHADER et al.'
    s = glCreateShader(gl_type)
    glShaderSource(s, [src])
    glCompileShader(s)
    return s


class Program(object):
    def __init__(self, id):
        self.enabled = False
        self.id = id


    def attach_shader(self, shader):
        glAttachShader(self.id, shader)


    def link(self):
        glLinkProgram(self.id)
        if renderer_options.validate_programs:
            glValidateProgram(self.id)


    def __enter__(self):
        global CURRENT_PROGRAM
        self.enabled = True
        if CURRENT_PROGRAM != self.id:
            glUseProgram(self.id)
        CURRENT_PROGRAM = self.id


    def __exit__(self, type, value, traceback):
        self.enabled = False


class RenderHandle(object):
    def __init__(self, program, vao, num_elements):
        self.program = program
        self.vao = vao
        self.num_elements = num_elements


    @staticmethod
    def from_triangles(program, vertices, colors):
        assert len(vertices) % 3 == 0
        has_colors = len(colors) == len(vertices)

        va = glGenVertexArrays(1)
        vbos =  glGenBuffers(2)

        attrib_locs = [
                glGetAttribLocation(program.id, "in_pos"),
                glGetAttribLocation(program.id, "in_color")
                ]

        glBindVertexArray(va[0])
        for i in (0, 1):
            if attrib_locs[i] >= 0:
                glBindBuffer(
                        GL_ARRAY_BUFFER, vbos[i])
                glBufferData(
                        GL_ARRAY_BUFFER, GLfloat,
                        (vertices, colors)[i], GL_STATIC_DRAW)
                glVertexAttribPointer(
                        attrib_locs[i], 3, GL_FLOAT, GL_FALSE, 0, 0)
                glEnableVertexAttribArray(i)
        import math
        return RenderHandle(program, va[0], int(len(vertices) / 3))


def draw_handles(render_handles):
    for render_handle in render_handles:
        with render_handle.program:
            glBindVertexArray(render_handle.vao)
            glDrawArrays(GL_TRIANGLES, 0, render_handle.num_elements)


def render_universe(universe, eye):
    draw_handles(universe.root_agent.render_handles)
