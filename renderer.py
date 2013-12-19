from __future__ import (print_function, division, absolute_import)


from gl import *
from glm import mat4x4


class Program(object):
    def __init__(self, id):
        self.enabled = False
        self.id = id


    def __enter__(self):
        self.enabled = True
        glUseProgram(self.id)


    def __exit__(self, type, value, traceback):
        self.enabled = False
        glUseProgram(0)


class RenderHandle(object):
    def __init__(self, program, vao, num_elements):
        self.program = program
        self.vao = vao
        self.num_elements = num_elements


def drawArrays(render_handle):
    with render_handle.program:
        glBindVertexArray(render_handle.vao)
        glDrawArrays(GL_TRIANGLES, 0, render_handle.num_elements)


