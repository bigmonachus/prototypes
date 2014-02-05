'''
An interface opens a window, sets up a GL context and controls VR specific
viewport / multiple-rendering logic.
CONVENTIONS:
    GL_TEXTURE0: Reserved for post-processing framebuffer.
'''

from __future__ import (print_function, division, absolute_import)

import pyglet
from gl import (glClear, glViewport, glCreateProgram, glPolygonMode,
        glActiveTexture, GL_TEXTURE0,
        GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_VERTEX_SHADER,
        GL_FRAGMENT_SHADER, GL_FRONT_AND_BACK, GL_FILL)

try:
    import ovr
except ImportError:
    print('No support for ovr.')

import logger
import renderer


def get_resolution():
    return 1280, 800


class Interface(object):
    """Abstrace Interface class.
    Subclass must define in begin():
         self.universe """
    def __init__(self):
        self._gl_config = pyglet.gl.Config(
                major_version = 3,
                minor_version = 3,
                double_buffer = True,
                depth_size = 24,
                red_size = 8,
                green_size = 8,
                blue_size = 8)
        self.universe = None
        self._window = None


    def __enter__(self):
        w, h = get_resolution()

        self._window = pyglet.window.Window(w, h, config=self._gl_config)
        print('Created pyglet window. GL context version {}'.format(
            self._window.context.get_info().get_version()))
        self._setup_events()
        self.begin()
        return self


    def _setup_events(self):
        @self._window.event
        def on_draw():
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self._draw()


    def _draw(self):
        renderer.render_universe(self.universe, 'center')


    def begin(self):
        'Do setup after loading the window and setting up a GL context.'
        pyglet.clock.schedule_interval(self.tick, 0.001)


    def tick(self, dt):
        self.universe.tick(dt)


    def run(self):
        pyglet.app.run()


    def __exit__(self, t, value, traceback):
        pass


class OVRInterface(Interface):
    def __init__(self):
        super(OVRInterface, self).__init__()
        self._devs = None
        self.devices = []
        self.dm = None
        self.rendertexture = None
        self.screen_triangle_rh = None
        self.pp_program = None
        self.devinfo = None
        self.device = None

    def __enter__(self):
        ovr.System.Init(ovr.Log.ConfigureDefaultLog(ovr.LogMask_All))
        self.dm = ovr.DeviceManager.Create()
        assert self.dm
        self._devs = self.dm.EnumerateHMDDevices()
        self.devices = []
        while True:
            dev = self._devs.CreateDevice()
            if not dev:
                break
            self.devices.append(dev)
            if not self._devs.Next():
                break

        print(self.devices)
        self.device = self.devices[0]
        self.devinfo = ovr.HMDInfo()
        assert self.device.GetDeviceInfo(self.devinfo)

        ############### Search for ovr screen.
        # The only case where the default display is not what we want is some
        # linux setup where someone has more than one X display running.
        display = pyglet.window.get_platform().get_default_display()
        oculus_screen = None
        for screen in display.get_screens():
            if screen.width == 1280 and screen.height == 800:
                oculus_screen = screen
                break

        if not oculus_screen:
            logger.error("Oculus screen not found.")

        # Fulscreen oculus window.
        self._window = pyglet.window.Window(
                fullscreen = True,
                screen = oculus_screen,
                vsync = True, config = self._gl_config,
                style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS)

        self._setup_events()
        rb_width = 1280
        rb_height = 800
        self.rendertexture = renderer.RenderTexture(rb_width, rb_height)

        self.pp_program = self._build_postprocess_program()
        self.screen_triangle_rh = self._cook_screen_triangle(self.pp_program)

        self.begin()

        return self


    def _draw(self):
        with self.rendertexture:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            w, h = get_resolution()
            half = int(w/2)
            glViewport(0, 0, half, h)
            renderer.render_universe(self.universe, 'left')
            glViewport(half, 0, half, h)
            renderer.render_universe(self.universe, 'right')

        # Test: do this with our program.
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glActiveTexture(GL_TEXTURE0)
        glViewport(0, 0, w, h)
        rh = self.screen_triangle_rh
        renderer.draw_handles([self.screen_triangle_rh])
        # Test, overdraw what I want to see
        glViewport(half, 0, half, h)
        renderer.render_universe(self.universe, 'right')


    def __exit__(self, t, value, traceback):
        logger.log("OVRInterface exited succesfully.")
        del self.device
        del self.devices
        del self._devs
        del self.dm
        # TODO: This is a bug with duangle's ovr bindings.
        # ovr.System.Destroy()


    def _build_postprocess_program(self):
        vertex_src = '''
        #version 330
        in vec3 in_pos;
        in vec2 in_texcoord;

        out vec2 vs_texcoord;
        out vec3 vs_color;
        void main(void)
        {
            vs_texcoord = in_texcoord;
            gl_Position = vec4(in_pos, 1.0);
        }
        '''
        frag_src = '''
        #version 330
        in vec2 vs_texcoord;
        out vec4 out_color;

        uniform sampler2D frame;

        void main(void)
        {
            vec4 color = texture(frame, vs_texcoord);
            out_color = color;
        }
        '''
        p = renderer.Program(glCreateProgram(), 'pp_program')
        p.attach_shader(renderer.create_shader(
            vertex_src, GL_VERTEX_SHADER, 'pp_vertex'))
        p.attach_shader(renderer.create_shader(
            frag_src, GL_FRAGMENT_SHADER, 'pp_frag'))
        p.link()
        return p


    def _cook_screen_triangle(self, program):
        vertices = [
                1.0 , -1.0  ,0.0,
                -1.0 , -1.0 ,0.0,
                1.0  , 1.0  ,0.0,
                -1.0 , -1.0  ,0.0,
                -1.0 , 1.0 ,0.0,
                1.0  , 1.0  ,0.0,
                ]
        texcoords = [
                1.0 , 0.0,
                0.0 , 0.0,
                1.0 , 1.0,
                0.0 , 0.0,
                0.0 , 1.0,
                1.0 , 1.0,
                ]

        return renderer.RenderHandle.from_triangles_and_texcoords(
                program, vertices, texcoords)



