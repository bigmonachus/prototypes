from __future__ import (print_function, division, absolute_import)


from math import tan, atan

from glm import mat4x4


class Agent(object):
    '''An agent acts inside a universe. It provides a list of render handles
    at draw time. It has a tick() function that returns a new, mutated version
    of itself
    '''
    def get_render_handles(self):
        """Returns handles that the render module understands at draw time.
        An agent may take care of this itself, or call someone who knows
        what to do.
        (e.g. a Scene agent can do an octree search returning a list of handles)
        Returns: List of RenderHandle objects
        """
        return []


    def tick(self, dt):
        pass


class Universe(Agent):
    """The difference between a universe and an agent is subtle.
    A universe has more responsibilities.
    A universe also takes care of head movement and decides which agent render
    handles to return.
    """
    def __init__(self):
        self.modelview = mat4x4.identity()
        self.matstack = []
        self.head = ()
        self.devinfo = None
        self.program = None
        self.use_ovr = False


    def enable_ovr(self, devinfo):
        """HMDInfo Needed for self.setup_rift_persp"""
        self.devinfo = devinfo
        self.use_ovr = True


    def push(self, mat):
        'Push current modelview and then multiply it by mat'
        self.matstack.append(self.modelview)
        self.modelview = self.modelview.mul_mat4(mat)


    def pop(self):
        self.modelview = self.matstack.pop()


    def render_prelude(self):
        """Setup opengl state for this universe"""
        pass


################################################################################
# OVR
################################################################################
    def setup_rift_persp(self, eye, znear, zfar):
        if not self.use_ovr:
            return
        rift_ar = self.devinfo.HResolution / (2 * self.devinfo.VResolution)

        v_size = self.devinfo.VScreenSize
        eye_to_screen = self.devinfo.EyeToScreenDistance
        v_fov = 2 * atan(v_size / (2 * eye_to_screen))

        rift_persp = mat4x4.zero()

        t = 1 / (tan(v_fov/2))
        rift_persp.i00 = t / rift_ar
        rift_persp.i11 = t
        rift_persp.i22 = zfar / (znear - zfar)
        rift_persp.i32 = (zfar + znear) / (znear - zfar)
        rift_persp.i23 = -1

        lens_separation = self.devinfo.LensSeparationDistance
        view_center = self.devinfo.HScreenSize / 4
        eye_shift = view_center - lens_separation/2
        offset = 4 * eye_shift / self.devinfo.HScreenSize

        ipd = self.devinfo.InterpupillaryDistance

        if eye == 'right':
            translation_mat = mat4x4.translation_fff(-offset, 0, 0)
            rift_persp = translation_mat.mul_mat4(rift_persp)
            self.program.set_uniform('eye_ipd', (-ipd/2,))
        elif eye == 'left':
            translation_mat = mat4x4.translation_fff(offset, 0, 0)
            rift_persp = translation_mat.mul_mat4(rift_persp)
            self.program.set_uniform('eye_ipd', (ipd/2,))

        self.program.setup_persp(rift_persp)
