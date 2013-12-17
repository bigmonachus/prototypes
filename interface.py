from __future__ import (print_function, division, absolute_import)

import logger

import pyglet
try:
    import ovr
except Exception:
    logger.log('No support for ovr.')


class Interface(object):
    '''
    An interface wraps input/output
    '''
    def __enter__(self):
        print("ENTER")
        self.window = pyglet.window.Window(1280, 800)
        self._setup_events()
        print("Self is", self)
        return self


    def _setup_events(self):
        @self.window.event
        def on_draw():
            self.draw()


    def idle(self):
        pass


    def draw(self):
        pass


    def run(self):
        pyglet.app.run()


    def __exit__(self, type, value, traceback):
        pass


class OVRInterface(Interface):
    def __enter__(self):
        ovr.System.Init(ovr.Log.ConfigureDefaultLog(ovr.LogMask_All))
        dm = ovr.DeviceManager.Create()
        assert dm
        _devs = dm.EnumerateHMDDevices()
        self.devices = []
        while True:
            dev = _devs.CreateDevice()
            if not dev:
                break
            self.devices.append(dev)
            if not _devs.Next():
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
        self.window = pyglet.window.Window(
                width = 1280, height = 800, screen = oculus_screen,
                vsync = True, config = ovr_config,
                style = pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
        self.window.set_location(oculus_screen.x, oculus_screen.y)

        self._setup_events()

        return self


        def run(self):
            pyglet.app.run()


        def __exit__(self, type, value, traceback):
            logger.log("OVRInterface exited succesfully.")
            del self.device
            del self.devices
            ovr.System.Destroy()

