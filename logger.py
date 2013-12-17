from __future__ import (print_function, division, absolute_import)

def log(*stuff):
    apply(print, stuff)

def error(*stuff):
    apply(print, stuff)
    exit(-1)
