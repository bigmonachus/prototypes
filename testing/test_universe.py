from __future__ import (print_function, division, absolute_import)


import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
sys.path.insert(0, myPath + '/../larch')

from glm import mat4x4

from larch import universe


def test_modelviewinit():
    u = universe.Universe()
    u.modelview.equals(mat4x4.identity())


def test_modelpushpop():
    u = universe.Universe()
    assert u.matstack == []
    u.push(mat4x4.scale_f(2))
    expected = mat4x4.identity().mul_mat4(mat4x4.scale_f(2))
    print(expected)
    print(u.modelview)
    assert u.modelview.equals(expected)
    assert len(u.matstack) == 1
    assert u.matstack[0].equals(mat4x4.identity())
    u.pop()
    assert u.modelview.equals(mat4x4.identity())
    assert u.matstack == []
