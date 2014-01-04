from __future__ import (print_function, division, absolute_import)


from gl import *
import glm
import re

import logger
from options import renderer_options


CURRENT_PROGRAM = -1


def draw_handles(render_handles):
    for render_handle in render_handles:
        with render_handle.program:
            glBindVertexArray(render_handle.vao)
            glDrawArrays(GL_TRIANGLES, 0, render_handle.num_elements)


def render_universe(universe, eye):
    universe.setup_rift_persp(eye, 0.1, 1000)
    draw_handles(universe.get_render_handles())


def create_shader(src, gl_type, name):
    'src is a string. gl_type is GL_VERTEX_SHADER et al.'
    s = glCreateShader(gl_type)
    glShaderSource(s, [src])
    glCompileShader(s)
    print_shader_log(s, name)
    return s


class Program(object):
    def __init__(self, idt, name):
        self.idt = idt
        self.name = name
        self.uniforms = {}


    def set_uniform(self, name, thing):
        """Currently doesn't support int uniforms"""
        if name not in self.uniforms:
            loc = glGetUniformLocation(self.idt, name)
            assert loc >= 0
            self.uniforms[name] = loc
        else:
            loc = self.uniforms[name]
        if type(thing) is glm.types.mat4x4:
            with self:
                glUniformMatrix4fv(loc, False, thing.to_c_array())
        if len(thing) == 4:
            with self:
                glUniform4fv(loc, thing)
        if len(thing) == 3:
            with self:
                glUniform3fv(loc, thing)
        if len(thing) == 1:
            with self:
                glUniform1fv(loc, thing)


    def attach_shader(self, shader):
        glAttachShader(self.idt, shader)


    def link(self):
        glLinkProgram(self.idt)
        if renderer_options.validate_programs:
            glValidateProgram(self.idt)
        print_program_log(self.idt, self.name)


    def __enter__(self):
        global CURRENT_PROGRAM
        if CURRENT_PROGRAM != self.idt:
            glUseProgram(self.idt)
            CURRENT_PROGRAM = self.idt


    def __exit__(self, t, value, traceback):
        pass


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
                glGetAttribLocation(program.idt, "in_pos"),
                glGetAttribLocation(program.idt, "in_color")
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
        return RenderHandle(program, va[0], int(len(vertices) / 3))


    @staticmethod
    def from_triangles_and_texcoords(program, vertices, texcoords):
        assert len(vertices) % 3 == 0
        has_texcoords = int(len(texcoords) / 2) == int(len(vertices) / 3)
        if not has_texcoords:
            print('warning! no texcoords')
            print(len(texcoords), len(vertices))

        va = glGenVertexArrays(1)
        vbos =  glGenBuffers(2)

        attrib_locs = [
                glGetAttribLocation(program.idt, "in_pos"),
                glGetAttribLocation(program.idt, "in_texcoord")
                ]

        glBindVertexArray(va[0])
        for i in (0, 1):
            assert attrib_locs[i] >= 0
            glBindBuffer(
                    GL_ARRAY_BUFFER, vbos[i])
            glBufferData(
                    GL_ARRAY_BUFFER, GLfloat,
                    (vertices, texcoords)[i], GL_STATIC_DRAW)
            glVertexAttribPointer(
                    attrib_locs[i], (3, 2)[i], GL_FLOAT, GL_FALSE, 0, 0)
            glEnableVertexAttribArray(i)
        return RenderHandle(program, va[0], int(len(vertices) / 3))


class RenderTexture(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        logger.log('Generating RenderTexture')

        # Create texture (RGBA8 is the convention for Larch)
        glActiveTexture(GL_TEXTURE0)
        self.color_tex = glGenTextures(1)[0]
        glBindTexture(GL_TEXTURE_2D, self.color_tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height,
                0, GL_RGBA, GL_UNSIGNED_BYTE, None)

        # Create / Bind target framebuffer
        self.fb = glGenFramebuffers(1)[0]
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)

        # Color attachment
        glFramebufferTexture2D(
                GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                self.color_tex, 0)

        # Depth attachment
        self.depth_rb = glGenRenderbuffers(1)[0]
        glBindRenderbuffer(
                GL_RENDERBUFFER, self.depth_rb)
        glRenderbufferStorage(
                GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height)
        glFramebufferRenderbuffer(
                GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER,
                self.depth_rb)

        # We cool?
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        assert status == GL_FRAMEBUFFER_COMPLETE

        # We cool...

        # Bind default framebuffer.
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


    def __enter__(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fb)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_rb)


    def __exit__(self, t, value, traceback):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindRenderbuffer(GL_RENDERBUFFER, 0)


# Got most of this from Beige: ================================
def print_shader_log(shader, name):
    shader_type = {
        0 : 'unknown shader type',
        GL_VERTEX_SHADER : 'vertex shader',
        GL_FRAGMENT_SHADER : 'fragment shader',
        GL_GEOMETRY_SHADER : 'geometry shader',
    }[glGetShaderiv(shader, GL_SHADER_TYPE)]

    judgement, logfunc = {
        GL_TRUE : ('succeeded',logger.log),
        GL_FALSE : ('FAILED',logger.nonfatal_error)
    }[glGetShaderiv(shader, GL_COMPILE_STATUS)]

    logfunc('Compilation of {0} for {1} {2}:'.format(
        shader_type, name, judgement))

    source = glGetShaderSource(shader)
    msglog = glGetShaderInfoLog(shader)
    map_source_to_log(source, msglog, logfunc)


def print_program_log(program, name):
    judgement, logfunc = {
        GL_TRUE : ('succeeded',logger.log),
        GL_FALSE : ('FAILED',logger.error)
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
    return int(m.group(1)), int(m.group(2))-1, int(m.group(3))-1

def parse_lineloc2(line):
    # ubuntu intel style
    m = re_lineno2.match(line)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))-1, 0

def parse_lineloc3(line):
    # ubuntu nvidia style
    m = re_lineno3.match(line)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))-1, 0

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
            _, lidx, chidx = location
            if linecount < MAX_NOISE:
                logfunc("")
                # print a bit of context
                for i in range(lidx-LOG_CONTEXT_PRE, lidx+LOG_CONTEXT_POST+1):
                    if (i < 0) or (i >= linelen):
                        continue
                    prefix = '! ' if i == lidx else '| '
                    logfunc(prefix + lines[i])
                    if i == lidx:
                        logfunc('--' + '-'*(chidx) + '^')
        logfunc(line)
        linecount += 1

#==========================================
