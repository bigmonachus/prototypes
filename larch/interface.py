'''
An interface opens a window, sets up a GL context and controls VR specific
viewport / multiple-rendering logic.
'''

from __future__ import (print_function, division, absolute_import)

import pyglet
from gl import glClear, glViewport, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
try:
    import ovr
except Exception:
    print('No support for ovr.')

import logger
import renderer

def get_resolution():
    return 1280, 800

class Interface(object):
    def __enter__(self):
        w, h = get_resolution()
        self._window = pyglet.window.Window(w, h)
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
        self.program = None  # Set this to a default, perspective projected.
        pyglet.clock.schedule_interval(self.tick, 0.001)


    def tick(self, dt):
        self.universe.tick(dt)


    def run(self):
        pyglet.app.run()


    def __exit__(self, type, value, traceback):
        pass


class OVRInterface(Interface):
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

        ovr_config = pyglet.gl.Config(double_buffer = True)

        # Simulate fullscreen by making an undecorated window right where the
        # screen is.
        self._window = pyglet.window.Window(
                fullscreen = True,
                screen = oculus_screen,
                vsync = True, config = ovr_config,
                style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS)

        self._setup_events()
        self.begin()

        return self


    def _setup_fb_target(self):
        pass


    def _draw(self):
        w, h = get_resolution()
        half = int(w/2)
        glViewport(0, 0, half, h)
        renderer.render_universe(self.universe, 'left')
        glViewport(half, 0, half, h)
        renderer.render_universe(self.universe, 'right')


    def __exit__(self, type, value, traceback):
        logger.log("OVRInterface exited succesfully.")
        del self.device
        del self.devices
        del self._devs
        del self.dm
        # TODO: This is a bug with duangle's ovr bindings.
        # ovr.System.Destroy()
