from __future__ import (print_function, division, absolute_import)


from glm import mat4x4


class Agent(object):
    '''An agent acts inside a universe. It provides a list of render handles
    at draw time. It has a tick() function that returns a new, mutated version
    of itself
    '''
    def get_render_handles(self):
        """Returns handles that the renderer understands at draw time.
        An agent may take care of this itself, or call someone who knows
        what to do.
        (e.g. a Scene agent can do an octree search returning a list of handles)
        Returns: List of RenderHandle objects
        """
        return []


    def tick(self, dt):
        pass

