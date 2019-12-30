"""distutils.core

The only module that needs to be imported to use the Distutils; provides
the 'setup' function (which ni to be called kutoka the setup script).  Also
indirectly provides the Distribution na Command classes, although they are
really defined kwenye distutils.dist na distutils.cmd.
"""

agiza os
agiza sys

kutoka distutils.debug agiza DEBUG
kutoka distutils.errors agiza *

# Mainly agiza these so setup scripts can "kutoka distutils.core import" them.
kutoka distutils.dist agiza Distribution
kutoka distutils.cmd agiza Command
kutoka distutils.config agiza PyPIRCCommand
kutoka distutils.extension agiza Extension

# This ni a barebones help message generated displayed when the user
# runs the setup script ukijumuisha no arguments at all.  More useful help
# ni generated ukijumuisha various --help options: global help, list commands,
# na per-command help.
USAGE = """\
usage: %(script)s [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]
   or: %(script)s --help [cmd1 cmd2 ...]
   or: %(script)s --help-commands
   or: %(script)s cmd --help
"""

eleza gen_usage (script_name):
    script = os.path.basename(script_name)
    rudisha USAGE % vars()


# Some mild magic to control the behaviour of 'setup()' kutoka 'run_setup()'.
_setup_stop_after = Tupu
_setup_distribution = Tupu

# Legal keyword arguments kila the setup() function
setup_keywords = ('distclass', 'script_name', 'script_args', 'options',
                  'name', 'version', 'author', 'author_email',
                  'maintainer', 'maintainer_email', 'url', 'license',
                  'description', 'long_description', 'keywords',
                  'platforms', 'classifiers', 'download_url',
                  'requires', 'provides', 'obsoletes',
                  )

# Legal keyword arguments kila the Extension constructor
extension_keywords = ('name', 'sources', 'include_dirs',
                      'define_macros', 'undef_macros',
                      'library_dirs', 'libraries', 'runtime_library_dirs',
                      'extra_objects', 'extra_compile_args', 'extra_link_args',
                      'swig_opts', 'export_symbols', 'depends', 'language')

eleza setup (**attrs):
    """The gateway to the Distutils: do everything your setup script needs
    to do, kwenye a highly flexible na user-driven way.  Briefly: create a
    Distribution instance; find na parse config files; parse the command
    line; run each Distutils command found there, customized by the options
    supplied to 'setup()' (as keyword arguments), kwenye config files, na on
    the command line.

    The Distribution instance might be an instance of a kundi supplied via
    the 'distclass' keyword argument to 'setup'; ikiwa no such kundi is
    supplied, then the Distribution kundi (in dist.py) ni instantiated.
    All other arguments to 'setup' (tatizo kila 'cmdclass') are used to set
    attributes of the Distribution instance.

    The 'cmdclass' argument, ikiwa supplied, ni a dictionary mapping command
    names to command classes.  Each command encountered on the command line
    will be turned into a command class, which ni kwenye turn instantiated; any
    kundi found kwenye 'cmdclass' ni used kwenye place of the default, which is
    (kila command 'foo_bar') kundi 'foo_bar' kwenye module
    'distutils.command.foo_bar'.  The command kundi must provide a
    'user_options' attribute which ni a list of option specifiers for
    'distutils.fancy_getopt'.  Any command-line options between the current
    na the next command are used to set attributes of the current command
    object.

    When the entire command-line has been successfully parsed, calls the
    'run()' method on each command object kwenye turn.  This method will be
    driven entirely by the Distribution object (which each command object
    has a reference to, thanks to its constructor), na the
    command-specific options that became attributes of each command
    object.
    """

    global _setup_stop_after, _setup_distribution

    # Determine the distribution kundi -- either caller-supplied ama
    # our Distribution (see below).
    klass = attrs.get('distclass')
    ikiwa klass:
        toa attrs['distclass']
    isipokua:
        klass = Distribution

    ikiwa 'script_name' haiko kwenye attrs:
        attrs['script_name'] = os.path.basename(sys.argv[0])
    ikiwa 'script_args'  haiko kwenye attrs:
        attrs['script_args'] = sys.argv[1:]

    # Create the Distribution instance, using the remaining arguments
    # (ie. everything tatizo distclass) to initialize it
    jaribu:
        _setup_distribution = dist = klass(attrs)
    tatizo DistutilsSetupError kama msg:
        ikiwa 'name' haiko kwenye attrs:
            ashiria SystemExit("error kwenye setup command: %s" % msg)
        isipokua:
            ashiria SystemExit("error kwenye %s setup command: %s" % \
                  (attrs['name'], msg))

    ikiwa _setup_stop_after == "init":
        rudisha dist

    # Find na parse the config file(s): they will override options from
    # the setup script, but be overridden by the command line.
    dist.parse_config_files()

    ikiwa DEBUG:
        andika("options (after parsing config files):")
        dist.dump_option_dicts()

    ikiwa _setup_stop_after == "config":
        rudisha dist

    # Parse the command line na override config files; any
    # command-line errors are the end user's fault, so turn them into
    # SystemExit to suppress tracebacks.
    jaribu:
        ok = dist.parse_command_line()
    tatizo DistutilsArgError kama msg:
        ashiria SystemExit(gen_usage(dist.script_name) + "\nerror: %s" % msg)

    ikiwa DEBUG:
        andika("options (after parsing command line):")
        dist.dump_option_dicts()

    ikiwa _setup_stop_after == "commandline":
        rudisha dist

    # And finally, run all the commands found on the command line.
    ikiwa ok:
        jaribu:
            dist.run_commands()
        tatizo KeyboardInterrupt:
            ashiria SystemExit("interrupted")
        tatizo OSError kama exc:
            ikiwa DEBUG:
                sys.stderr.write("error: %s\n" % (exc,))
                raise
            isipokua:
                ashiria SystemExit("error: %s" % (exc,))

        tatizo (DistutilsError,
                CCompilerError) kama msg:
            ikiwa DEBUG:
                raise
            isipokua:
                ashiria SystemExit("error: " + str(msg))

    rudisha dist

# setup ()


eleza run_setup (script_name, script_args=Tupu, stop_after="run"):
    """Run a setup script kwenye a somewhat controlled environment, na
    rudisha the Distribution instance that drives things.  This ni useful
    ikiwa you need to find out the distribution meta-data (pitaed as
    keyword args kutoka 'script' to 'setup()', ama the contents of the
    config files ama command-line.

    'script_name' ni a file that will be read na run ukijumuisha 'exec()';
    'sys.argv[0]' will be replaced ukijumuisha 'script' kila the duration of the
    call.  'script_args' ni a list of strings; ikiwa supplied,
    'sys.argv[1:]' will be replaced by 'script_args' kila the duration of
    the call.

    'stop_after' tells 'setup()' when to stop processing; possible
    values:
      init
        stop after the Distribution instance has been created na
        populated ukijumuisha the keyword arguments to 'setup()'
      config
        stop after config files have been parsed (and their data
        stored kwenye the Distribution instance)
      commandline
        stop after the command-line ('sys.argv[1:]' ama 'script_args')
        have been parsed (and the data stored kwenye the Distribution)
      run [default]
        stop after all commands have been run (the same kama ikiwa 'setup()'
        had been called kwenye the usual way

    Returns the Distribution instance, which provides all information
    used to drive the Distutils.
    """
    ikiwa stop_after haiko kwenye ('init', 'config', 'commandline', 'run'):
        ashiria ValueError("invalid value kila 'stop_after': %r" % (stop_after,))

    global _setup_stop_after, _setup_distribution
    _setup_stop_after = stop_after

    save_argv = sys.argv.copy()
    g = {'__file__': script_name}
    jaribu:
        jaribu:
            sys.argv[0] = script_name
            ikiwa script_args ni sio Tupu:
                sys.argv[1:] = script_args
            ukijumuisha open(script_name, 'rb') kama f:
                exec(f.read(), g)
        mwishowe:
            sys.argv = save_argv
            _setup_stop_after = Tupu
    tatizo SystemExit:
        # Hmm, should we do something ikiwa exiting ukijumuisha a non-zero code
        # (ie. error)?
        pita

    ikiwa _setup_distribution ni Tupu:
        ashiria RuntimeError(("'distutils.core.setup()' was never called -- "
               "perhaps '%s' ni sio a Distutils setup script?") % \
              script_name)

    # I wonder ikiwa the setup script's namespace -- g na l -- would be of
    # any interest to callers?
    #print "_setup_distribution:", _setup_distribution
    rudisha _setup_distribution

# run_setup ()
