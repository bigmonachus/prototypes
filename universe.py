from __future__ import (print_function, division, absolute_import)


from glm import mat4x4


class Agent(object):
    '''An agent acts inside a universe. It provides a list of render handles
    at draw time. It has a tick() function that returns a new, mutated version
    of itself
    '''
    def __init__(self):
        pass


    def get_render_handles(self):
        """Returns handles that the renderer understands at draw time.
        An agent may take care of this itself, or call someone who knows
        what to do.
        (e.g. a Scene agent can do an octree search returning a list of handles)
        Returns: List of RenderHandle objects
        """
        return []


    def tick():
        pass


class Universe(object):
    def __init__(self, root_agent):
        self.modelview = mat4x4.identity()
        self.matstack = []
        self.head = ()
        self.root_agent = root_agent


    def tick(self):
        self.root_agent.tick()


    def push(self, mat):
        'Push current modelview and then multiply it by mat'
        self.matstack.append(self.modelview)
        self.modelview = self.modelview.mul_mat4(mat)


    def pop(self):
        self.modelview = self.matstack.pop()

