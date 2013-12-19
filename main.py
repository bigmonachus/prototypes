from __future__ import (print_function, division, absolute_import)


import sys

from interface import Interface, OVRInterface


USE_OVR = False


def main():
    global USE_OVR
    import pkgutil, importlib
    game_names = [name for _, name, _ in pkgutil.iter_modules(['games'])]

    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument(
            '--ovr', action='store_true', help='Play game with Oculus Rift')
    parser.add_argument(
            '--game',
            action='store',
            help='Specify the game to run. List of games: {}'.format(game_names))

    parsed_args = parser.parse_args(sys.argv[1:])

    USE_OVR = parsed_args.ovr
    InterfaceClass = Interface
    if USE_OVR:
        InterfaceClass = OVRInterface

    # See if --game flag matches a module in the games package.
    Game = None
    if parsed_args.game in game_names:
        module = importlib.import_module('games.{}'.format(parsed_args.game))
        Game = module.new(InterfaceClass)

    if Game:
        with Game() as game:
            game.run()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
