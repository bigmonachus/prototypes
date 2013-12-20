from __future__ import (print_function, division, absolute_import)


from options import debug


def log(*stuff):
    if debug:
        apply(print, stuff)


def nonfatal_error(*stuff):
    apply(print, stuff)


def error(*stuff):
    apply(print, stuff)
    exit(-1)
