from __future__ import (print_function, division, absolute_import)


import glm


def test_equality():
    'This is for my own understanding...'
    idt = glm.mat4x4.identity()
    idt2 = glm.mat4x4.identity()
    assert idt.equals(idt2)


