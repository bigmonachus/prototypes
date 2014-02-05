from __future__ import (print_function, division, absolute_import)

import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
sys.path.insert(0, myPath + '/../larch')

import math

import glm


def test_educatemyself():
    'Just making sure things work like I think they do.'
    idt = glm.mat4x4.identity()
    idt2 = glm.mat4x4.identity()
    assert idt.equals(idt2)

    l = glm.mat3x3.look_at(glm.vec3(0,0,-1), glm.vec3(0,1,0))
    assert l.equals(glm.mat3x3.identity())

    # Test that rotation is counter-clockwise
    center = glm.vec3(0,0,-1)
    up     = glm.vec3(0,1,0)
    rot    = glm.mat3x3.rotation(math.pi / 2.0, glm.vec3(0,1,0))

    center = rot.mul_vec3(center)
    rot    = rot.mul_vec3(up)

    print(center, rot)

    l = glm.mat3x3.look_at(center, up)

    assert glm.vec3(-1,0,0).equals(l.mul_vec3(glm.vec3(0,0,-1)))


