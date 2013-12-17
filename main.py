from __future__ import (print_function, division, absolute_import)

from interface import Interface, OVRInterface

import sys
import games.simple

USE_OVR = False

def main():
    global USE_OVR
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument('--ovr', action='store_true', help='Play game with Oculus Rift')
    parser.add_argument('--game', action='store',
            help='Specify the game to run. (simple)')

    parsed_args = parser.parse_args(sys.argv[1:])

    USE_OVR = parsed_args.ovr
    InterfaceClass = Interface
    if USE_OVR:
        InterfaceClass = OVRInterface

    Game = None
    if parsed_args.game == 'simple':
        Game = games.simple.new(InterfaceClass)

    if Game:
        with Game() as game:
            game.run()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
