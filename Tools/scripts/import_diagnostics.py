#!/usr/bin/env python3
"""Miscellaneous diagnostics kila the agiza system"""

agiza sys
agiza argparse
kutoka pprint agiza pprint

eleza _dump_state(args):
    andika(sys.version)
    kila name kwenye args.attributes:
        andika("sys.{}:".format(name))
        pandika(getattr(sys, name))

eleza _add_dump_args(cmd):
    cmd.add_argument("attributes", metavar="ATTR", nargs="+",
                     help="sys module attribute to display")

COMMANDS = (
  ("dump", "Dump agiza state", _dump_state, _add_dump_args),
)

eleza _make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(title="Commands")
    kila name, description, implementation, add_args kwenye COMMANDS:
        cmd = sub.add_parser(name, help=description)
        cmd.set_defaults(command=implementation)
        add_args(cmd)
    rudisha parser

eleza main(args):
    parser = _make_parser()
    args = parser.parse_args(args)
    rudisha args.command(args)

ikiwa __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
