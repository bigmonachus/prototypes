from __future__ import (print_function, division, absolute_import)


from gl import *
import glm
import re

import logger as log
from options import renderer_options


CURRENT_PROGRAM = 0


def create_shader(src, gl_type, name):
    'src is a string. gl_type is GL_VERTEX_SHADER et al.'
    s = glCreateShader(gl_type)
    glShaderSource(s, [src])
    glCompileShader(s)
    print_shader_log(s, name)
    return s


class Program(object):
    def __init__(self, id, name):
        self.enabled = False
        self.id = id
        self.name = name
        self.uniforms = {}

    def set_uniform(self, name, thing):
        """Currently doesn't support int uniforms"""
        if name not in self.uniforms:
            loc = glGetUniformLocation(self.id, name)
            assert loc >= 0
        else:
            loc = self.uniforms[name]
        if type(thing) is glm.types.mat4x4:
            with self:
                glUniformMatrix4fv(loc, False, thing.to_c_array())
        if len(thing) == 3:
            with self:
                glUniform3fv(loc, thing)
        if len(thing) == 1:
            with self:
                glUniform1fv(loc, thing)


    def attach_shader(self, shader):
        glAttachShader(self.id, shader)


    def link(self):
        glLinkProgram(self.id)
        if renderer_options.validate_programs:
            glValidateProgram(self.id)
        print_program_log(self.id, self.name)


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
        if not has_colors:
            print('warning! no colors')
            print(len(colors), len(vertices))

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


def render_agent(agent, eye):
    draw_handles(agent.get_render_handles())


# Got most of this from Beige: ================================
def print_shader_log(shader, name):
    shader_type = {
        0 : 'unknown shader type',
        GL_VERTEX_SHADER : 'vertex shader',
        GL_FRAGMENT_SHADER : 'fragment shader',
        GL_GEOMETRY_SHADER : 'geometry shader',
    }[glGetShaderiv(shader, GL_SHADER_TYPE)]

    judgement,logfunc = {
        GL_TRUE : ('succeeded',log.log),
        GL_FALSE : ('FAILED',log.nonfatal_error)
    }[glGetShaderiv(shader, GL_COMPILE_STATUS)]

    logfunc('Compilation of {0} for {1} {2}:'.format(
        shader_type, name, judgement))

    source = glGetShaderSource(shader)
    msglog = glGetShaderInfoLog(shader)
    map_source_to_log(source, msglog, logfunc)

def print_program_log(program, name):
    judgement,logfunc = {
        GL_TRUE : ('succeeded',log.log),
        GL_FALSE : ('FAILED',log.error)
    }[glGetProgramiv(program, GL_LINK_STATUS)]

    logfunc('Compilation of program for {0} {1}:'.format(
        name, judgement))

    msglog = glGetProgramInfoLog(program)
    for line in msglog.split('\n'):
        logfunc(line)


# how much source code lines to display before shader error line
LOG_CONTEXT_PRE = 4
# how much source code lines to display after shader error line
LOG_CONTEXT_POST = 1


re_lineno = re.compile(r'^(\d+)\:(\d+)\((\d+)\)\D*')
re_lineno2 = re.compile(r'^\S+\:\s(\d+)\:(\d+)\:.*')
re_lineno3 = re.compile(r'^(\d+)\((\d+)\)\s\:.*')
re_include = re.compile(r'^include\s+"([^"]+)"')

def parse_lineloc1(line):
    # mac intel style
    m = re_lineno.match(line)
    if not m:
        return None
    return int(m.group(1)),int(m.group(2))-1,int(m.group(3))-1

def parse_lineloc2(line):
    # ubuntu intel style
    m = re_lineno2.match(line)
    if not m:
        return None
    return int(m.group(1)),int(m.group(2))-1,0

def parse_lineloc3(line):
    # ubuntu nvidia style
    m = re_lineno3.match(line)
    if not m:
        return None
    return int(m.group(1)),int(m.group(2))-1,0

def parse_include(line):
    m = re_include.match(line)
    if not m:
        return None
    return m.group(1)

# all line location parsers return shader number, line index, column index
_lineloc_parsers = [
    parse_lineloc1,
    parse_lineloc2,
    parse_lineloc3,
]
def map_source_to_log(source, msglog, logfunc):
    lines = source.split('\n')
    linelen = len(lines)
    linecount = 0
    MAX_NOISE = 5
    for line in msglog.split('\n'):
        location = None
        for locparser in _lineloc_parsers:
            location = locparser(line)
            if location:
                break
        if location:
            xno,lidx,chidx = location
            if linecount < MAX_NOISE:
                logfunc("")
                # print a bit of context
                for i in range(lidx-LOG_CONTEXT_PRE,lidx+LOG_CONTEXT_POST+1):
                    if (i < 0) or (i >= linelen):
                        continue
                    prefix = '! ' if i == lidx else '| '
                    logfunc(prefix + lines[i])
                    if i == lidx:
                        logfunc('--' + '-'*(chidx) + '^')
        logfunc(line)
        linecount += 1

#==========================================
