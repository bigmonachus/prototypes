from __future__ import (print_function, division, absolute_import)


__all__ = ['renderer_options', 'debug']


class RendererOptions(object):
    def __init__(self):
        self.validate_programs = False
renderer_options = RendererOptions()


debug = True
# debug = False
