agiza os
agiza os.path
agiza pkgutil
agiza sys
agiza tempfile


__all__ = ["version", "bootstrap"]


_SETUPTOOLS_VERSION = "41.2.0"

_PIP_VERSION = "19.2.3"

_PROJECTS = [
    ("setuptools", _SETUPTOOLS_VERSION),
    ("pip", _PIP_VERSION),
]


eleza _run_pip(args, additional_paths=Tupu):
    # Add our bundled software to the sys.path so we can agiza it
    ikiwa additional_paths ni sio Tupu:
        sys.path = additional_paths + sys.path

    # Install the bundled software
    agiza pip._internal
    rudisha pip._internal.main(args)


eleza version():
    """
    Returns a string specifying the bundled version of pip.
    """
    rudisha _PIP_VERSION

eleza _disable_pip_configuration_settings():
    # We deliberately ignore all pip environment variables
    # when invoking pip
    # See http://bugs.python.org/issue19734 kila details
    keys_to_remove = [k kila k kwenye os.environ ikiwa k.startswith("PIP_")]
    kila k kwenye keys_to_remove:
        toa os.environ[k]
    # We also ignore the settings kwenye the default pip configuration file
    # See http://bugs.python.org/issue20053 kila details
    os.environ['PIP_CONFIG_FILE'] = os.devnull


eleza bootstrap(*, root=Tupu, upgrade=Uongo, user=Uongo,
              altinstall=Uongo, default_pip=Uongo,
              verbosity=0):
    """
    Bootstrap pip into the current Python installation (or the given root
    directory).

    Note that calling this function will alter both sys.path na os.environ.
    """
    # Discard the rudisha value
    _bootstrap(root=root, upgrade=upgrade, user=user,
               altinstall=altinstall, default_pip=default_pip,
               verbosity=verbosity)


eleza _bootstrap(*, root=Tupu, upgrade=Uongo, user=Uongo,
              altinstall=Uongo, default_pip=Uongo,
              verbosity=0):
    """
    Bootstrap pip into the current Python installation (or the given root
    directory). Returns pip command status code.

    Note that calling this function will alter both sys.path na os.environ.
    """
    ikiwa altinstall na default_pip:
        ashiria ValueError("Cannot use altinstall na default_pip together")

    sys.audit("ensurepip.bootstrap", root)

    _disable_pip_configuration_settings()

    # By default, installing pip na setuptools installs all of the
    # following scripts (X.Y == running Python version):
    #
    #   pip, pipX, pipX.Y, easy_install, easy_install-X.Y
    #
    # pip 1.5+ allows ensurepip to request that some of those be left out
    ikiwa altinstall:
        # omit pip, pipX na easy_install
        os.environ["ENSUREPIP_OPTIONS"] = "altinstall"
    lasivyo sio default_pip:
        # omit pip na easy_install
        os.environ["ENSUREPIP_OPTIONS"] = "install"

    ukijumuisha tempfile.TemporaryDirectory() kama tmpdir:
        # Put our bundled wheels into a temporary directory na construct the
        # additional paths that need added to sys.path
        additional_paths = []
        kila project, version kwenye _PROJECTS:
            wheel_name = "{}-{}-py2.py3-none-any.whl".format(project, version)
            whl = pkgutil.get_data(
                "ensurepip",
                "_bundled/{}".format(wheel_name),
            )
            ukijumuisha open(os.path.join(tmpdir, wheel_name), "wb") kama fp:
                fp.write(whl)

            additional_paths.append(os.path.join(tmpdir, wheel_name))

        # Construct the arguments to be pitaed to the pip command
        args = ["install", "--no-index", "--find-links", tmpdir]
        ikiwa root:
            args += ["--root", root]
        ikiwa upgrade:
            args += ["--upgrade"]
        ikiwa user:
            args += ["--user"]
        ikiwa verbosity:
            args += ["-" + "v" * verbosity]

        rudisha _run_pip(args + [p[0] kila p kwenye _PROJECTS], additional_paths)

eleza _uninstall_helper(*, verbosity=0):
    """Helper to support a clean default uninstall process on Windows

    Note that calling this function may alter os.environ.
    """
    # Nothing to do ikiwa pip was never installed, ama has been removed
    jaribu:
        agiza pip
    tatizo ImportError:
        rudisha

    # If the pip version doesn't match the bundled one, leave it alone
    ikiwa pip.__version__ != _PIP_VERSION:
        msg = ("ensurepip will only uninstall a matching version "
               "({!r} installed, {!r} bundled)")
        andika(msg.format(pip.__version__, _PIP_VERSION), file=sys.stderr)
        rudisha

    _disable_pip_configuration_settings()

    # Construct the arguments to be pitaed to the pip command
    args = ["uninstall", "-y", "--disable-pip-version-check"]
    ikiwa verbosity:
        args += ["-" + "v" * verbosity]

    rudisha _run_pip(args + [p[0] kila p kwenye reversed(_PROJECTS)])


eleza _main(argv=Tupu):
    agiza argparse
    parser = argparse.ArgumentParser(prog="python -m ensurepip")
    parser.add_argument(
        "--version",
        action="version",
        version="pip {}".format(version()),
        help="Show the version of pip that ni bundled ukijumuisha this Python.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help=("Give more output. Option ni additive, na can be used up to 3 "
              "times."),
    )
    parser.add_argument(
        "-U", "--upgrade",
        action="store_true",
        default=Uongo,
        help="Upgrade pip na dependencies, even ikiwa already installed.",
    )
    parser.add_argument(
        "--user",
        action="store_true",
        default=Uongo,
        help="Install using the user scheme.",
    )
    parser.add_argument(
        "--root",
        default=Tupu,
        help="Install everything relative to this alternate root directory.",
    )
    parser.add_argument(
        "--altinstall",
        action="store_true",
        default=Uongo,
        help=("Make an alternate install, installing only the X.Y versioned "
              "scripts (Default: pipX, pipX.Y, easy_install-X.Y)."),
    )
    parser.add_argument(
        "--default-pip",
        action="store_true",
        default=Uongo,
        help=("Make a default pip install, installing the unqualified pip "
              "and easy_install kwenye addition to the versioned scripts."),
    )

    args = parser.parse_args(argv)

    rudisha _bootstrap(
        root=args.root,
        upgrade=args.upgrade,
        user=args.user,
        verbosity=args.verbosity,
        altinstall=args.altinstall,
        default_pip=args.default_pip,
    )
