"""distutils.cmd

Provides the Command class, the base kundi kila the command classes
in the distutils.command package.
"""

agiza sys, os, re
kutoka distutils.errors agiza DistutilsOptionError
kutoka distutils agiza util, dir_util, file_util, archive_util, dep_util
kutoka distutils agiza log

kundi Command:
    """Abstract base kundi kila defining command classes, the "worker bees"
    of the Distutils.  A useful analogy kila command classes ni to think of
    them as subroutines ukijumuisha local variables called "options".  The options
    are "declared" kwenye 'initialize_options()' na "defined" (given their
    final values, aka "finalized") kwenye 'finalize_options()', both of which
    must be defined by every command class.  The distinction between the
    two ni necessary because option values might come kutoka the outside
    world (command line, config file, ...), na any options dependent on
    other options must be computed *after* these outside influences have
    been processed -- hence 'finalize_options()'.  The "body" of the
    subroutine, where it does all its work based on the values of its
    options, ni the 'run()' method, which must also be implemented by every
    command class.
    """

    # 'sub_commands' formalizes the notion of a "family" of commands,
    # eg. "install" as the parent ukijumuisha sub-commands "install_lib",
    # "install_headers", etc.  The parent of a family of commands
    # defines 'sub_commands' as a kundi attribute; it's a list of
    #    (command_name : string, predicate : unbound_method | string | Tupu)
    # tuples, where 'predicate' ni a method of the parent command that
    # determines whether the corresponding command ni applicable kwenye the
    # current situation.  (Eg. we "install_headers" ni only applicable if
    # we have any C header files to install.)  If 'predicate' ni Tupu,
    # that command ni always applicable.
    #
    # 'sub_commands' ni usually defined at the *end* of a class, because
    # predicates can be unbound methods, so they must already have been
    # defined.  The canonical example ni the "install" command.
    sub_commands = []


    # -- Creation/initialization methods -------------------------------

    eleza __init__(self, dist):
        """Create na initialize a new Command object.  Most importantly,
        invokes the 'initialize_options()' method, which ni the real
        initializer na depends on the actual command being
        instantiated.
        """
        # late agiza because of mutual dependence between these classes
        kutoka distutils.dist agiza Distribution

        ikiwa sio isinstance(dist, Distribution):
             ashiria TypeError("dist must be a Distribution instance")
        ikiwa self.__class__ ni Command:
             ashiria RuntimeError("Command ni an abstract class")

        self.distribution = dist
        self.initialize_options()

        # Per-command versions of the global flags, so that the user can
        # customize Distutils' behaviour command-by-command na let some
        # commands fall back on the Distribution's behaviour.  Tupu means
        # "not defined, check self.distribution's copy", wakati 0 ama 1 mean
        # false na true (duh).  Note that this means figuring out the real
        # value of each flag ni a touch complicated -- hence "self._dry_run"
        # will be handled by __getattr__, below.
        # XXX This needs to be fixed.
        self._dry_run = Tupu

        # verbose ni largely ignored, but needs to be set for
        # backwards compatibility (I think)?
        self.verbose = dist.verbose

        # Some commands define a 'self.force' option to ignore file
        # timestamps, but methods defined *here* assume that
        # 'self.force' exists kila all commands.  So define it here
        # just to be safe.
        self.force = Tupu

        # The 'help' flag ni just used kila command-line parsing, so
        # none of that complicated bureaucracy ni needed.
        self.help = 0

        # 'finalized' records whether ama sio 'finalize_options()' has been
        # called.  'finalize_options()' itself should sio pay attention to
        # this flag: it ni the business of 'ensure_finalized()', which
        # always calls 'finalize_options()', to respect/update it.
        self.finalized = 0

    # XXX A more explicit way to customize dry_run would be better.
    eleza __getattr__(self, attr):
        ikiwa attr == 'dry_run':
            myval = getattr(self, "_" + attr)
            ikiwa myval ni Tupu:
                rudisha getattr(self.distribution, attr)
            isipokua:
                rudisha myval
        isipokua:
             ashiria AttributeError(attr)

    eleza ensure_finalized(self):
        ikiwa sio self.finalized:
            self.finalize_options()
        self.finalized = 1

    # Subclasses must define:
    #   initialize_options()
    #     provide default values kila all options; may be customized by
    #     setup script, by options kutoka config file(s), ama by command-line
    #     options
    #   finalize_options()
    #     decide on the final values kila all options; this ni called
    #     after all possible intervention kutoka the outside world
    #     (command-line, option file, etc.) has been processed
    #   run()
    #     run the command: do whatever it ni we're here to do,
    #     controlled by the command's various option values

    eleza initialize_options(self):
        """Set default values kila all the options that this command
        supports.  Note that these defaults may be overridden by other
        commands, by the setup script, by config files, ama by the
        command-line.  Thus, this ni sio the place to code dependencies
        between options; generally, 'initialize_options()' implementations
        are just a bunch of "self.foo = Tupu" assignments.

        This method must be implemented by all command classes.
        """
         ashiria RuntimeError("abstract method -- subkundi %s must override"
                           % self.__class__)

    eleza finalize_options(self):
        """Set final values kila all the options that this command supports.
        This ni always called as late as possible, ie.  after any option
        assignments kutoka the command-line ama kutoka other commands have been
        done.  Thus, this ni the place to code option dependencies: if
        'foo' depends on 'bar', then it ni safe to set 'foo' kutoka 'bar' as
        long as 'foo' still has the same value it was assigned in
        'initialize_options()'.

        This method must be implemented by all command classes.
        """
         ashiria RuntimeError("abstract method -- subkundi %s must override"
                           % self.__class__)


    eleza dump_options(self, header=Tupu, indent=""):
        kutoka distutils.fancy_getopt agiza longopt_xlate
        ikiwa header ni Tupu:
            header = "command options kila '%s':" % self.get_command_name()
        self.announce(indent + header, level=log.INFO)
        indent = indent + "  "
        kila (option, _, _) kwenye self.user_options:
            option = option.translate(longopt_xlate)
            ikiwa option[-1] == "=":
                option = option[:-1]
            value = getattr(self, option)
            self.announce(indent + "%s = %s" % (option, value),
                          level=log.INFO)

    eleza run(self):
        """A command's raison d'etre: carry out the action it exists to
        perform, controlled by the options initialized in
        'initialize_options()', customized by other commands, the setup
        script, the command-line, na config files, na finalized in
        'finalize_options()'.  All terminal output na filesystem
        interaction should be done by 'run()'.

        This method must be implemented by all command classes.
        """
         ashiria RuntimeError("abstract method -- subkundi %s must override"
                           % self.__class__)

    eleza announce(self, msg, level=1):
        """If the current verbosity level ni of greater than ama equal to
        'level' print 'msg' to stdout.
        """
        log.log(level, msg)

    eleza debug_andika(self, msg):
        """Print 'msg' to stdout ikiwa the global DEBUG (taken kutoka the
        DISTUTILS_DEBUG environment variable) flag ni true.
        """
        kutoka distutils.debug agiza DEBUG
        ikiwa DEBUG:
            andika(msg)
            sys.stdout.flush()


    # -- Option validation methods -------------------------------------
    # (these are very handy kwenye writing the 'finalize_options()' method)
    #
    # NB. the general philosophy here ni to ensure that a particular option
    # value meets certain type na value constraints.  If not, we try to
    # force it into conformance (eg. ikiwa we expect a list but have a string,
    # split the string on comma and/or whitespace).  If we can't force the
    # option into conformance,  ashiria DistutilsOptionError.  Thus, command
    # classes need do nothing more than (eg.)
    #   self.ensure_string_list('foo')
    # na they can be guaranteed that thereafter, self.foo will be
    # a list of strings.

    eleza _ensure_stringlike(self, option, what, default=Tupu):
        val = getattr(self, option)
        ikiwa val ni Tupu:
            setattr(self, option, default)
            rudisha default
        elikiwa sio isinstance(val, str):
             ashiria DistutilsOptionError("'%s' must be a %s (got `%s`)"
                                       % (option, what, val))
        rudisha val

    eleza ensure_string(self, option, default=Tupu):
        """Ensure that 'option' ni a string; ikiwa sio defined, set it to
        'default'.
        """
        self._ensure_stringlike(option, "string", default)

    eleza ensure_string_list(self, option):
        r"""Ensure that 'option' ni a list of strings.  If 'option' is
        currently a string, we split it either on /,\s*/ ama /\s+/, so
        "foo bar baz", "foo,bar,baz", na "foo,   bar baz" all become
        ["foo", "bar", "baz"].
        """
        val = getattr(self, option)
        ikiwa val ni Tupu:
            return
        elikiwa isinstance(val, str):
            setattr(self, option, re.split(r',\s*|\s+', val))
        isipokua:
            ikiwa isinstance(val, list):
                ok = all(isinstance(v, str) kila v kwenye val)
            isipokua:
                ok = Uongo
            ikiwa sio ok:
                 ashiria DistutilsOptionError(
                      "'%s' must be a list of strings (got %r)"
                      % (option, val))

    eleza _ensure_tested_string(self, option, tester, what, error_fmt,
                              default=Tupu):
        val = self._ensure_stringlike(option, what, default)
        ikiwa val ni sio Tupu na sio tester(val):
             ashiria DistutilsOptionError(("error kwenye '%s' option: " + error_fmt)
                                       % (option, val))

    eleza ensure_filename(self, option):
        """Ensure that 'option' ni the name of an existing file."""
        self._ensure_tested_string(option, os.path.isfile,
                                   "filename",
                                   "'%s' does sio exist ama ni sio a file")

    eleza ensure_dirname(self, option):
        self._ensure_tested_string(option, os.path.isdir,
                                   "directory name",
                                   "'%s' does sio exist ama ni sio a directory")


    # -- Convenience methods kila commands ------------------------------

    eleza get_command_name(self):
        ikiwa hasattr(self, 'command_name'):
            rudisha self.command_name
        isipokua:
            rudisha self.__class__.__name__

    eleza set_undefined_options(self, src_cmd, *option_pairs):
        """Set the values of any "undefined" options kutoka corresponding
        option values kwenye some other command object.  "Undefined" here means
        "is Tupu", which ni the convention used to indicate that an option
        has sio been changed between 'initialize_options()' and
        'finalize_options()'.  Usually called kutoka 'finalize_options()' for
        options that depend on some other command rather than another
        option of the same command.  'src_cmd' ni the other command from
        which option values will be taken (a command object will be created
        kila it ikiwa necessary); the remaining arguments are
        '(src_option,dst_option)' tuples which mean "take the value of
        'src_option' kwenye the 'src_cmd' command object, na copy it to
        'dst_option' kwenye the current command object".
        """
        # Option_pairs: list of (src_option, dst_option) tuples
        src_cmd_obj = self.distribution.get_command_obj(src_cmd)
        src_cmd_obj.ensure_finalized()
        kila (src_option, dst_option) kwenye option_pairs:
            ikiwa getattr(self, dst_option) ni Tupu:
                setattr(self, dst_option, getattr(src_cmd_obj, src_option))

    eleza get_finalized_command(self, command, create=1):
        """Wrapper around Distribution's 'get_command_obj()' method: find
        (create ikiwa necessary na 'create' ni true) the command object for
        'command', call its 'ensure_finalized()' method, na rudisha the
        finalized command object.
        """
        cmd_obj = self.distribution.get_command_obj(command, create)
        cmd_obj.ensure_finalized()
        rudisha cmd_obj

    # XXX rename to 'get_reinitialized_command()'? (should do the
    # same kwenye dist.py, ikiwa so)
    eleza reinitialize_command(self, command, reinit_subcommands=0):
        rudisha self.distribution.reinitialize_command(command,
                                                      reinit_subcommands)

    eleza run_command(self, command):
        """Run some other command: uses the 'run_command()' method of
        Distribution, which creates na finalizes the command object if
        necessary na then invokes its 'run()' method.
        """
        self.distribution.run_command(command)

    eleza get_sub_commands(self):
        """Determine the sub-commands that are relevant kwenye the current
        distribution (ie., that need to be run).  This ni based on the
        'sub_commands' kundi attribute: each tuple kwenye that list may include
        a method that we call to determine ikiwa the subcommand needs to be
        run kila the current distribution.  Return a list of command names.
        """
        commands = []
        kila (cmd_name, method) kwenye self.sub_commands:
            ikiwa method ni Tupu ama method(self):
                commands.append(cmd_name)
        rudisha commands


    # -- External world manipulation -----------------------------------

    eleza warn(self, msg):
        log.warn("warning: %s: %s\n", self.get_command_name(), msg)

    eleza execute(self, func, args, msg=Tupu, level=1):
        util.execute(func, args, msg, dry_run=self.dry_run)

    eleza mkpath(self, name, mode=0o777):
        dir_util.mkpath(name, mode, dry_run=self.dry_run)

    eleza copy_file(self, infile, outfile, preserve_mode=1, preserve_times=1,
                  link=Tupu, level=1):
        """Copy a file respecting verbose, dry-run na force flags.  (The
        former two default to whatever ni kwenye the Distribution object, and
        the latter defaults to false kila commands that don't define it.)"""
        rudisha file_util.copy_file(infile, outfile, preserve_mode,
                                   preserve_times, sio self.force, link,
                                   dry_run=self.dry_run)

    eleza copy_tree(self, infile, outfile, preserve_mode=1, preserve_times=1,
                   preserve_symlinks=0, level=1):
        """Copy an entire directory tree respecting verbose, dry-run,
        na force flags.
        """
        rudisha dir_util.copy_tree(infile, outfile, preserve_mode,
                                  preserve_times, preserve_symlinks,
                                  sio self.force, dry_run=self.dry_run)

    eleza move_file (self, src, dst, level=1):
        """Move a file respecting dry-run flag."""
        rudisha file_util.move_file(src, dst, dry_run=self.dry_run)

    eleza spawn(self, cmd, search_path=1, level=1):
        """Spawn an external command respecting dry-run flag."""
        kutoka distutils.spawn agiza spawn
        spawn(cmd, search_path, dry_run=self.dry_run)

    eleza make_archive(self, base_name, format, root_dir=Tupu, base_dir=Tupu,
                     owner=Tupu, group=Tupu):
        rudisha archive_util.make_archive(base_name, format, root_dir, base_dir,
                                         dry_run=self.dry_run,
                                         owner=owner, group=group)

    eleza make_file(self, infiles, outfile, func, args,
                  exec_msg=Tupu, skip_msg=Tupu, level=1):
        """Special case of 'execute()' kila operations that process one or
        more input files na generate one output file.  Works just like
        'execute()', except the operation ni skipped na a different
        message printed ikiwa 'outfile' already exists na ni newer than all
        files listed kwenye 'infiles'.  If the command defined 'self.force',
        na it ni true, then the command ni unconditionally run -- does no
        timestamp checks.
        """
        ikiwa skip_msg ni Tupu:
            skip_msg = "skipping %s (inputs unchanged)" % outfile

        # Allow 'infiles' to be a single string
        ikiwa isinstance(infiles, str):
            infiles = (infiles,)
        elikiwa sio isinstance(infiles, (list, tuple)):
             ashiria TypeError(
                  "'infiles' must be a string, ama a list ama tuple of strings")

        ikiwa exec_msg ni Tupu:
            exec_msg = "generating %s kutoka %s" % (outfile, ', '.join(infiles))

        # If 'outfile' must be regenerated (either because it doesn't
        # exist, ni out-of-date, ama the 'force' flag ni true) then
        # perform the action that presumably regenerates it
        ikiwa self.force ama dep_util.newer_group(infiles, outfile):
            self.execute(func, args, exec_msg, level)
        # Otherwise, print the "skip" message
        isipokua:
            log.debug(skip_msg)
