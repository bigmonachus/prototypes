from __future__ import (print_function, division, absolute_import)


from glm import mat4x4


class Agent(object):
    '''An agent acts inside a universe. It provides a list of render handles
    at draw time. It has a tick() function that returns a new, mutated version
    of itself
    '''
    def __init__(self):
        self.render_handles = []


    def tick():
        pass


class Universe(object):
    def __init__(self, root_agent):
        self.modelview = mat4x4.identity()
        self.matstack = []
        self.head = ()
        self.root_agent = root_agent


    def push(self, mat):
        'Push current modelview and then multiply it by mat'
        self.matstack.append(self.modelview)
        self.modelview = self.modelview.mul_mat4(mat)


    def pop(self):
        self.modelview = self.matstack.pop()

