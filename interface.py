'''
An interface opens a window, sets up a GL context and controls VR specific
viewport / multiple-rendering logic.
'''

from __future__ import (print_function, division, absolute_import)

import pyglet

try:
    import ovr
except Exception:
    logger.log('No support for ovr.')

import logger
import renderer


class Interface(object):
    def __enter__(self):
        self._window = pyglet.window.Window(1280, 800)
        self._setup_events()
        self.begin()
        return self


    def _setup_events(self):
        self.event_loop = pyglet.app.EventLoop()
        @self._window.event
        def on_draw():
            # TODO: Fire rendering asynchronously.
            renderer.render_universe(self.universe, 'center')


    def begin(self):
        'Do setup after loading the window and setting up a GL context.'
        self.program = None  # Set this to a default, perspective projected.
        pyglet.clock.schedule_interval(self.tick, 0.001)


    def tick(self, dt):
        self.universe.tick()


    def run(self):
        self.event_loop.run()


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
        devinfo = ovr.HMDInfo()
        assert self.device.GetDeviceInfo(devinfo)

        screen_pos = (devinfo.DesktopX, devinfo.DesktopY)
        print(screen_pos)

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
                width = 1280, height = 800, screen = oculus_screen,
                vsync = True, config = ovr_config,
                style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
        self._window.set_location(oculus_screen.x, oculus_screen.y)

        self._setup_events()
        self.begin()

        return self


    def _setup_events(self):
        super(OVRInterface, self)._setup_events()
        @self._window.event
        def on_draw():
            print("i am complex")
            renderer.render_universe(self.universe, 'left')
            renderer.render_universe(self.universe, 'right')


    def __exit__(self, type, value, traceback):
        logger.log("OVRInterface exited succesfully.")
        del self.device
        del self.devices
        del self._devs
        del self.dm
        # TODO: This is a bug with duangle's ovr bindings.
        # ovr.System.Destroy()

