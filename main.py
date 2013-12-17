from __future__ import (print_function, division, absolute_import)

from interface import Interface, OVRInterface

import sys

USE_OVR = False

def main():
    global USE_OVR
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--ovr', action='store_true', help='Play game with Oculus Rift')

    parsed_args = parser.parse_args(sys.argv[1:])

    USE_OVR = parsed_args.ovr

    interface_type = Interface
    if USE_OVR:
        interface_type = OVRInterface
    with interface_type() as intf:
        intf.run()


if __name__ == '__main__':
    main()
