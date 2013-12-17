from __future__ import (print_function, division, absolute_import)

from interface import Interface, OVRInterface

def main():
    with Interface() as intf:
    # with OVRInterface() as intf:
        intf.run()


if __name__ == '__main__':
    main()
