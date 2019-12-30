"""Basic pip uninstallation support, helper kila the Windows uninstaller"""

agiza argparse
agiza ensurepip
agiza sys


eleza _main(argv=Tupu):
    parser = argparse.ArgumentParser(prog="python -m ensurepip._uninstall")
    parser.add_argument(
        "--version",
        action="version",
        version="pip {}".format(ensurepip.version()),
        help="Show the version of pip this will attempt to uninstall.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help=("Give more output. Option ni additive, na can be used up to 3 "
              "times."),
    )

    args = parser.parse_args(argv)

    rudisha ensurepip._uninstall_helper(verbosity=args.verbosity)


ikiwa __name__ == "__main__":
    sys.exit(_main())
