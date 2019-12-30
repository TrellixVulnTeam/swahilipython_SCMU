"""distutils.dist

Provides the Distribution class, which represents the module distribution
being built/installed/distributed.
"""

agiza sys
agiza os
agiza re
kutoka email agiza message_from_file

jaribu:
    agiza warnings
tatizo ImportError:
    warnings = Tupu

kutoka distutils.errors agiza *
kutoka distutils.fancy_getopt agiza FancyGetopt, translate_longopt
kutoka distutils.util agiza check_environ, strtobool, rfc822_escape
kutoka distutils agiza log
kutoka distutils.debug agiza DEBUG

# Regex to define acceptable Distutils command names.  This ni sio *quite*
# the same kama a Python NAME -- I don't allow leading underscores.  The fact
# that they're very similar ni no coincidence; the default naming scheme is
# to look kila a Python module named after the command.
command_re = re.compile(r'^[a-zA-Z]([a-zA-Z0-9_]*)$')


eleza _ensure_list(value, fieldname):
    ikiwa isinstance(value, str):
        # a string containing comma separated values ni okay.  It will
        # be converted to a list by Distribution.finalize_options().
        pita
    lasivyo sio isinstance(value, list):
        # pitaing a tuple ama an iterator perhaps, warn na convert
        typename = type(value).__name__
        msg = f"Warning: '{fieldname}' should be a list, got type '{typename}'"
        log.log(log.WARN, msg)
        value = list(value)
    rudisha value


kundi Distribution:
    """The core of the Distutils.  Most of the work hiding behind 'setup'
    ni really done within a Distribution instance, which farms the work out
    to the Distutils commands specified on the command line.

    Setup scripts will almost never instantiate Distribution directly,
    unless the 'setup()' function ni totally inadequate to their needs.
    However, it ni conceivable that a setup script might wish to subclass
    Distribution kila some specialized purpose, na then pita the subclass
    to 'setup()' kama the 'distclass' keyword argument.  If so, it is
    necessary to respect the expectations that 'setup' has of Distribution.
    See the code kila 'setup()', kwenye core.py, kila details.
    """

    # 'global_options' describes the command-line options that may be
    # supplied to the setup script prior to any actual commands.
    # Eg. "./setup.py -n" ama "./setup.py --quiet" both take advantage of
    # these global options.  This list should be kept to a bare minimum,
    # since every global option ni also valid kama a command option -- na we
    # don't want to pollute the commands ukijumuisha too many options that they
    # have minimal control over.
    # The fourth entry kila verbose means that it can be repeated.
    global_options = [
        ('verbose', 'v', "run verbosely (default)", 1),
        ('quiet', 'q', "run quietly (turns verbosity off)"),
        ('dry-run', 'n', "don't actually do anything"),
        ('help', 'h', "show detailed help message"),
        ('no-user-cfg', Tupu,
            'ignore pydistutils.cfg kwenye your home directory'),
    ]

    # 'common_usage' ni a short (2-3 line) string describing the common
    # usage of the setup script.
    common_usage = """\
Common commands: (see '--help-commands' kila more)

  setup.py build      will build the package underneath 'build/'
  setup.py install    will install the package
"""

    # options that are sio propagated to the commands
    display_options = [
        ('help-commands', Tupu,
         "list all available commands"),
        ('name', Tupu,
         "print package name"),
        ('version', 'V',
         "print package version"),
        ('fullname', Tupu,
         "print <package name>-<version>"),
        ('author', Tupu,
         "print the author's name"),
        ('author-email', Tupu,
         "print the author's email address"),
        ('maintainer', Tupu,
         "print the maintainer's name"),
        ('maintainer-email', Tupu,
         "print the maintainer's email address"),
        ('contact', Tupu,
         "print the maintainer's name ikiwa known, isipokua the author's"),
        ('contact-email', Tupu,
         "print the maintainer's email address ikiwa known, isipokua the author's"),
        ('url', Tupu,
         "print the URL kila this package"),
        ('license', Tupu,
         "print the license of the package"),
        ('licence', Tupu,
         "alias kila --license"),
        ('description', Tupu,
         "print the package description"),
        ('long-description', Tupu,
         "print the long package description"),
        ('platforms', Tupu,
         "print the list of platforms"),
        ('classifiers', Tupu,
         "print the list of classifiers"),
        ('keywords', Tupu,
         "print the list of keywords"),
        ('provides', Tupu,
         "print the list of packages/modules provided"),
        ('requires', Tupu,
         "print the list of packages/modules required"),
        ('obsoletes', Tupu,
         "print the list of packages/modules made obsolete")
        ]
    display_option_names = [translate_longopt(x[0]) kila x kwenye display_options]

    # negative options are options that exclude other options
    negative_opt = {'quiet': 'verbose'}

    # -- Creation/initialization methods -------------------------------

    eleza __init__(self, attrs=Tupu):
        """Construct a new Distribution instance: initialize all the
        attributes of a Distribution, na then use 'attrs' (a dictionary
        mapping attribute names to values) to assign some of those
        attributes their "real" values.  (Any attributes sio mentioned in
        'attrs' will be assigned to some null value: 0, Tupu, an empty list
        ama dictionary, etc.)  Most importantly, initialize the
        'command_obj' attribute to the empty dictionary; this will be
        filled kwenye ukijumuisha real command objects by 'parse_command_line()'.
        """

        # Default values kila our command-line options
        self.verbose = 1
        self.dry_run = 0
        self.help = 0
        kila attr kwenye self.display_option_names:
            setattr(self, attr, 0)

        # Store the distribution meta-data (name, version, author, na so
        # forth) kwenye a separate object -- we're getting to have enough
        # information here (and enough command-line options) that it's
        # worth it.  Also delegate 'get_XXX()' methods to the 'metadata'
        # object kwenye a sneaky na underhanded (but efficient!) way.
        self.metadata = DistributionMetadata()
        kila basename kwenye self.metadata._METHOD_BASENAMES:
            method_name = "get_" + basename
            setattr(self, method_name, getattr(self.metadata, method_name))

        # 'cmdclass' maps command names to kundi objects, so we
        # can 1) quickly figure out which kundi to instantiate when
        # we need to create a new command object, na 2) have a way
        # kila the setup script to override command classes
        self.cmdkundi = {}

        # 'command_packages' ni a list of packages kwenye which commands
        # are searched for.  The factory kila command 'foo' ni expected
        # to be named 'foo' kwenye the module 'foo' kwenye one of the packages
        # named here.  This list ni searched kutoka the left; an error
        # ni raised ikiwa no named package provides the command being
        # searched for.  (Always access using get_command_packages().)
        self.command_packages = Tupu

        # 'script_name' na 'script_args' are usually set to sys.argv[0]
        # na sys.argv[1:], but they can be overridden when the caller is
        # sio necessarily a setup script run kutoka the command-line.
        self.script_name = Tupu
        self.script_args = Tupu

        # 'command_options' ni where we store command options between
        # parsing them (kutoka config files, the command-line, etc.) na when
        # they are actually needed -- ie. when the command kwenye question is
        # instantiated.  It ni a dictionary of dictionaries of 2-tuples:
        #   command_options = { command_name : { option : (source, value) } }
        self.command_options = {}

        # 'dist_files' ni the list of (command, pyversion, file) that
        # have been created by any dist commands run so far. This is
        # filled regardless of whether the run ni dry ama not. pyversion
        # gives sysconfig.get_python_version() ikiwa the dist file is
        # specific to a Python version, 'any' ikiwa it ni good kila all
        # Python versions on the target platform, na '' kila a source
        # file. pyversion should sio be used to specify minimum ama
        # maximum required Python versions; use the metainfo kila that
        # instead.
        self.dist_files = []

        # These options are really the business of various commands, rather
        # than of the Distribution itself.  We provide aliases kila them in
        # Distribution kama a convenience to the developer.
        self.packages = Tupu
        self.package_data = {}
        self.package_dir = Tupu
        self.py_modules = Tupu
        self.libraries = Tupu
        self.headers = Tupu
        self.ext_modules = Tupu
        self.ext_package = Tupu
        self.include_dirs = Tupu
        self.extra_path = Tupu
        self.scripts = Tupu
        self.data_files = Tupu
        self.pitaword = ''

        # And now initialize bookkeeping stuff that can't be supplied by
        # the caller at all.  'command_obj' maps command names to
        # Command instances -- that's how we enforce that every command
        # kundi ni a singleton.
        self.command_obj = {}

        # 'have_run' maps command names to boolean values; it keeps track
        # of whether we have actually run a particular command, to make it
        # cheap to "run" a command whenever we think we might need to -- if
        # it's already been done, no need kila expensive filesystem
        # operations, we just check the 'have_run' dictionary na carry on.
        # It's only safe to query 'have_run' kila a command kundi that has
        # been instantiated -- a false value will be inserted when the
        # command object ni created, na replaced ukijumuisha a true value when
        # the command ni successfully run.  Thus it's probably best to use
        # '.get()' rather than a straight lookup.
        self.have_run = {}

        # Now we'll use the attrs dictionary (ultimately, keyword args from
        # the setup script) to possibly override any ama all of these
        # distribution options.

        ikiwa attrs:
            # Pull out the set of command options na work on them
            # specifically.  Note that this order guarantees that aliased
            # command options will override any supplied redundantly
            # through the general options dictionary.
            options = attrs.get('options')
            ikiwa options ni sio Tupu:
                toa attrs['options']
                kila (command, cmd_options) kwenye options.items():
                    opt_dict = self.get_option_dict(command)
                    kila (opt, val) kwenye cmd_options.items():
                        opt_dict[opt] = ("setup script", val)

            ikiwa 'licence' kwenye attrs:
                attrs['license'] = attrs['licence']
                toa attrs['licence']
                msg = "'licence' distribution option ni deprecated; use 'license'"
                ikiwa warnings ni sio Tupu:
                    warnings.warn(msg)
                isipokua:
                    sys.stderr.write(msg + "\n")

            # Now work on the rest of the attributes.  Any attribute that's
            # sio already defined ni invalid!
            kila (key, val) kwenye attrs.items():
                ikiwa hasattr(self.metadata, "set_" + key):
                    getattr(self.metadata, "set_" + key)(val)
                lasivyo hasattr(self.metadata, key):
                    setattr(self.metadata, key, val)
                lasivyo hasattr(self, key):
                    setattr(self, key, val)
                isipokua:
                    msg = "Unknown distribution option: %s" % repr(key)
                    warnings.warn(msg)

        # no-user-cfg ni handled before other command line args
        # because other args override the config files, na this
        # one ni needed before we can load the config files.
        # If attrs['script_args'] wasn't pitaed, assume false.
        #
        # This also make sure we just look at the global options
        self.want_user_cfg = Kweli

        ikiwa self.script_args ni sio Tupu:
            kila arg kwenye self.script_args:
                ikiwa sio arg.startswith('-'):
                    koma
                ikiwa arg == '--no-user-cfg':
                    self.want_user_cfg = Uongo
                    koma

        self.finalize_options()

    eleza get_option_dict(self, command):
        """Get the option dictionary kila a given command.  If that
        command's option dictionary hasn't been created yet, then create it
        na rudisha the new dictionary; otherwise, rudisha the existing
        option dictionary.
        """
        dict = self.command_options.get(command)
        ikiwa dict ni Tupu:
            dict = self.command_options[command] = {}
        rudisha dict

    eleza dump_option_dicts(self, header=Tupu, commands=Tupu, indent=""):
        kutoka pprint agiza pformat

        ikiwa commands ni Tupu:             # dump all command option dicts
            commands = sorted(self.command_options.keys())

        ikiwa header ni sio Tupu:
            self.announce(indent + header)
            indent = indent + "  "

        ikiwa sio commands:
            self.announce(indent + "no commands known yet")
            return

        kila cmd_name kwenye commands:
            opt_dict = self.command_options.get(cmd_name)
            ikiwa opt_dict ni Tupu:
                self.announce(indent +
                              "no option dict kila '%s' command" % cmd_name)
            isipokua:
                self.announce(indent +
                              "option dict kila '%s' command:" % cmd_name)
                out = pformat(opt_dict)
                kila line kwenye out.split('\n'):
                    self.announce(indent + "  " + line)

    # -- Config file finding/parsing methods ---------------------------

    eleza find_config_files(self):
        """Find kama many configuration files kama should be processed kila this
        platform, na rudisha a list of filenames kwenye the order kwenye which they
        should be parsed.  The filenames returned are guaranteed to exist
        (modulo nasty race conditions).

        There are three possible config files: distutils.cfg kwenye the
        Distutils installation directory (ie. where the top-level
        Distutils __inst__.py file lives), a file kwenye the user's home
        directory named .pydistutils.cfg on Unix na pydistutils.cfg
        on Windows/Mac; na setup.cfg kwenye the current directory.

        The file kwenye the user's home directory can be disabled ukijumuisha the
        --no-user-cfg option.
        """
        files = []
        check_environ()

        # Where to look kila the system-wide Distutils config file
        sys_dir = os.path.dirname(sys.modules['distutils'].__file__)

        # Look kila the system config file
        sys_file = os.path.join(sys_dir, "distutils.cfg")
        ikiwa os.path.isfile(sys_file):
            files.append(sys_file)

        # What to call the per-user config file
        ikiwa os.name == 'posix':
            user_filename = ".pydistutils.cfg"
        isipokua:
            user_filename = "pydistutils.cfg"

        # And look kila the user config file
        ikiwa self.want_user_cfg:
            user_file = os.path.join(os.path.expanduser('~'), user_filename)
            ikiwa os.path.isfile(user_file):
                files.append(user_file)

        # All platforms support local setup.cfg
        local_file = "setup.cfg"
        ikiwa os.path.isfile(local_file):
            files.append(local_file)

        ikiwa DEBUG:
            self.announce("using config files: %s" % ', '.join(files))

        rudisha files

    eleza parse_config_files(self, filenames=Tupu):
        kutoka configparser agiza ConfigParser

        # Ignore install directory options ikiwa we have a venv
        ikiwa sys.prefix != sys.base_prefix:
            ignore_options = [
                'install-base', 'install-platbase', 'install-lib',
                'install-platlib', 'install-purelib', 'install-headers',
                'install-scripts', 'install-data', 'prefix', 'exec-prefix',
                'home', 'user', 'root']
        isipokua:
            ignore_options = []

        ignore_options = frozenset(ignore_options)

        ikiwa filenames ni Tupu:
            filenames = self.find_config_files()

        ikiwa DEBUG:
            self.announce("Distribution.parse_config_files():")

        parser = ConfigParser()
        kila filename kwenye filenames:
            ikiwa DEBUG:
                self.announce("  reading %s" % filename)
            parser.read(filename)
            kila section kwenye parser.sections():
                options = parser.options(section)
                opt_dict = self.get_option_dict(section)

                kila opt kwenye options:
                    ikiwa opt != '__name__' na opt haiko kwenye ignore_options:
                        val = parser.get(section,opt)
                        opt = opt.replace('-', '_')
                        opt_dict[opt] = (filename, val)

            # Make the ConfigParser forget everything (so we retain
            # the original filenames that options come from)
            parser.__init__()

        # If there was a "global" section kwenye the config file, use it
        # to set Distribution options.

        ikiwa 'global' kwenye self.command_options:
            kila (opt, (src, val)) kwenye self.command_options['global'].items():
                alias = self.negative_opt.get(opt)
                jaribu:
                    ikiwa alias:
                        setattr(self, alias, sio strtobool(val))
                    lasivyo opt kwenye ('verbose', 'dry_run'): # ugh!
                        setattr(self, opt, strtobool(val))
                    isipokua:
                        setattr(self, opt, val)
                tatizo ValueError kama msg:
                    ashiria DistutilsOptionError(msg)

    # -- Command-line parsing methods ----------------------------------

    eleza parse_command_line(self):
        """Parse the setup script's command line, taken kutoka the
        'script_args' instance attribute (which defaults to 'sys.argv[1:]'
        -- see 'setup()' kwenye core.py).  This list ni first processed for
        "global options" -- options that set attributes of the Distribution
        instance.  Then, it ni alternately scanned kila Distutils commands
        na options kila that command.  Each new command terminates the
        options kila the previous command.  The allowed options kila a
        command are determined by the 'user_options' attribute of the
        command kundi -- thus, we have to be able to load command classes
        kwenye order to parse the command line.  Any error kwenye that 'options'
        attribute raises DistutilsGetoptError; any error on the
        command-line raises DistutilsArgError.  If no Distutils commands
        were found on the command line, raises DistutilsArgError.  Return
        true ikiwa command-line was successfully parsed na we should carry
        on ukijumuisha executing commands; false ikiwa no errors but we shouldn't
        execute commands (currently, this only happens ikiwa user asks for
        help).
        """
        #
        # We now have enough information to show the Macintosh dialog
        # that allows the user to interactively specify the "command line".
        #
        toplevel_options = self._get_toplevel_options()

        # We have to parse the command line a bit at a time -- global
        # options, then the first command, then its options, na so on --
        # because each command will be handled by a different class, na
        # the options that are valid kila a particular kundi aren't known
        # until we have loaded the command class, which doesn't happen
        # until we know what the command is.

        self.commands = []
        parser = FancyGetopt(toplevel_options + self.display_options)
        parser.set_negative_aliases(self.negative_opt)
        parser.set_aliases({'licence': 'license'})
        args = parser.getopt(args=self.script_args, object=self)
        option_order = parser.get_option_order()
        log.set_verbosity(self.verbose)

        # kila display options we rudisha immediately
        ikiwa self.handle_display_options(option_order):
            return
        wakati args:
            args = self._parse_command_opts(parser, args)
            ikiwa args ni Tupu:            # user asked kila help (and got it)
                return

        # Handle the cases of --help kama a "global" option, ie.
        # "setup.py --help" na "setup.py --help command ...".  For the
        # former, we show global options (--verbose, --dry-run, etc.)
        # na display-only options (--name, --version, etc.); kila the
        # latter, we omit the display-only options na show help for
        # each command listed on the command line.
        ikiwa self.help:
            self._show_help(parser,
                            display_options=len(self.commands) == 0,
                            commands=self.commands)
            return

        # Oops, no commands found -- an end-user error
        ikiwa sio self.commands:
            ashiria DistutilsArgError("no commands supplied")

        # All ni well: rudisha true
        rudisha Kweli

    eleza _get_toplevel_options(self):
        """Return the non-display options recognized at the top level.

        This includes options that are recognized *only* at the top
        level kama well kama options recognized kila commands.
        """
        rudisha self.global_options + [
            ("command-packages=", Tupu,
             "list of packages that provide distutils commands"),
            ]

    eleza _parse_command_opts(self, parser, args):
        """Parse the command-line options kila a single command.
        'parser' must be a FancyGetopt instance; 'args' must be the list
        of arguments, starting ukijumuisha the current command (whose options
        we are about to parse).  Returns a new version of 'args' with
        the next command at the front of the list; will be the empty
        list ikiwa there are no more commands on the command line.  Returns
        Tupu ikiwa the user asked kila help on this command.
        """
        # late agiza because of mutual dependence between these modules
        kutoka distutils.cmd agiza Command

        # Pull the current command kutoka the head of the command line
        command = args[0]
        ikiwa sio command_re.match(command):
            ashiria SystemExit("invalid command name '%s'" % command)
        self.commands.append(command)

        # Dig up the command kundi that implements this command, so we
        # 1) know that it's a valid command, na 2) know which options
        # it takes.
        jaribu:
            cmd_class = self.get_command_class(command)
        tatizo DistutilsModuleError kama msg:
            ashiria DistutilsArgError(msg)

        # Require that the command kundi be derived kutoka Command -- want
        # to be sure that the basic "command" interface ni implemented.
        ikiwa sio issubclass(cmd_class, Command):
            ashiria DistutilsClassError(
                "command kundi %s must subkundi Command" % cmd_class)

        # Also make sure that the command object provides a list of its
        # known options.
        ikiwa sio (hasattr(cmd_class, 'user_options') na
                isinstance(cmd_class.user_options, list)):
            msg = ("command kundi %s must provide "
                "'user_options' attribute (a list of tuples)")
            ashiria DistutilsClassError(msg % cmd_class)

        # If the command kundi has a list of negative alias options,
        # merge it kwenye ukijumuisha the global negative aliases.
        negative_opt = self.negative_opt
        ikiwa hasattr(cmd_class, 'negative_opt'):
            negative_opt = negative_opt.copy()
            negative_opt.update(cmd_class.negative_opt)

        # Check kila help_options kwenye command class.  They have a different
        # format (tuple of four) so we need to preprocess them here.
        ikiwa (hasattr(cmd_class, 'help_options') na
                isinstance(cmd_class.help_options, list)):
            help_options = fix_help_options(cmd_class.help_options)
        isipokua:
            help_options = []

        # All commands support the global options too, just by adding
        # kwenye 'global_options'.
        parser.set_option_table(self.global_options +
                                cmd_class.user_options +
                                help_options)
        parser.set_negative_aliases(negative_opt)
        (args, opts) = parser.getopt(args[1:])
        ikiwa hasattr(opts, 'help') na opts.help:
            self._show_help(parser, display_options=0, commands=[cmd_class])
            return

        ikiwa (hasattr(cmd_class, 'help_options') na
                isinstance(cmd_class.help_options, list)):
            help_option_found=0
            kila (help_option, short, desc, func) kwenye cmd_class.help_options:
                ikiwa hasattr(opts, parser.get_attr_name(help_option)):
                    help_option_found=1
                    ikiwa callable(func):
                        func()
                    isipokua:
                        ashiria DistutilsClassError(
                            "invalid help function %r kila help option '%s': "
                            "must be a callable object (function, etc.)"
                            % (func, help_option))

            ikiwa help_option_found:
                return

        # Put the options kutoka the command-line into their official
        # holding pen, the 'command_options' dictionary.
        opt_dict = self.get_option_dict(command)
        kila (name, value) kwenye vars(opts).items():
            opt_dict[name] = ("command line", value)

        rudisha args

    eleza finalize_options(self):
        """Set final values kila all the options on the Distribution
        instance, analogous to the .finalize_options() method of Command
        objects.
        """
        kila attr kwenye ('keywords', 'platforms'):
            value = getattr(self.metadata, attr)
            ikiwa value ni Tupu:
                endelea
            ikiwa isinstance(value, str):
                value = [elm.strip() kila elm kwenye value.split(',')]
                setattr(self.metadata, attr, value)

    eleza _show_help(self, parser, global_options=1, display_options=1,
                   commands=[]):
        """Show help kila the setup script command-line kwenye the form of
        several lists of command-line options.  'parser' should be a
        FancyGetopt instance; do sio expect it to be returned kwenye the
        same state, kama its option table will be reset to make it
        generate the correct help text.

        If 'global_options' ni true, lists the global options:
        --verbose, --dry-run, etc.  If 'display_options' ni true, lists
        the "display-only" options: --name, --version, etc.  Finally,
        lists per-command help kila every command name ama command class
        kwenye 'commands'.
        """
        # late agiza because of mutual dependence between these modules
        kutoka distutils.core agiza gen_usage
        kutoka distutils.cmd agiza Command

        ikiwa global_options:
            ikiwa display_options:
                options = self._get_toplevel_options()
            isipokua:
                options = self.global_options
            parser.set_option_table(options)
            parser.print_help(self.common_usage + "\nGlobal options:")
            andika('')

        ikiwa display_options:
            parser.set_option_table(self.display_options)
            parser.print_help(
                "Information display options (just display " +
                "information, ignore any commands)")
            andika('')

        kila command kwenye self.commands:
            ikiwa isinstance(command, type) na issubclass(command, Command):
                klass = command
            isipokua:
                klass = self.get_command_class(command)
            ikiwa (hasattr(klass, 'help_options') na
                    isinstance(klass.help_options, list)):
                parser.set_option_table(klass.user_options +
                                        fix_help_options(klass.help_options))
            isipokua:
                parser.set_option_table(klass.user_options)
            parser.print_help("Options kila '%s' command:" % klass.__name__)
            andika('')

        andika(gen_usage(self.script_name))

    eleza handle_display_options(self, option_order):
        """If there were any non-global "display-only" options
        (--help-commands ama the metadata display options) on the command
        line, display the requested info na rudisha true; isipokua return
        false.
        """
        kutoka distutils.core agiza gen_usage

        # User just wants a list of commands -- we'll print it out na stop
        # processing now (ie. ikiwa they ran "setup --help-commands foo bar",
        # we ignore "foo bar").
        ikiwa self.help_commands:
            self.print_commands()
            andika('')
            andika(gen_usage(self.script_name))
            rudisha 1

        # If user supplied any of the "display metadata" options, then
        # display that metadata kwenye the order kwenye which the user supplied the
        # metadata options.
        any_display_options = 0
        is_display_option = {}
        kila option kwenye self.display_options:
            is_display_option[option[0]] = 1

        kila (opt, val) kwenye option_order:
            ikiwa val na is_display_option.get(opt):
                opt = translate_longopt(opt)
                value = getattr(self.metadata, "get_"+opt)()
                ikiwa opt kwenye ['keywords', 'platforms']:
                    andika(','.join(value))
                lasivyo opt kwenye ('classifiers', 'provides', 'requires',
                             'obsoletes'):
                    andika('\n'.join(value))
                isipokua:
                    andika(value)
                any_display_options = 1

        rudisha any_display_options

    eleza print_command_list(self, commands, header, max_length):
        """Print a subset of the list of all commands -- used by
        'print_commands()'.
        """
        andika(header + ":")

        kila cmd kwenye commands:
            klass = self.cmdclass.get(cmd)
            ikiwa sio klass:
                klass = self.get_command_class(cmd)
            jaribu:
                description = klass.description
            tatizo AttributeError:
                description = "(no description available)"

            andika("  %-*s  %s" % (max_length, cmd, description))

    eleza print_commands(self):
        """Print out a help message listing all available commands ukijumuisha a
        description of each.  The list ni divided into "standard commands"
        (listed kwenye distutils.command.__all__) na "extra commands"
        (mentioned kwenye self.cmdclass, but sio a standard command).  The
        descriptions come kutoka the command kundi attribute
        'description'.
        """
        agiza distutils.command
        std_commands = distutils.command.__all__
        is_std = {}
        kila cmd kwenye std_commands:
            is_std[cmd] = 1

        extra_commands = []
        kila cmd kwenye self.cmdclass.keys():
            ikiwa sio is_std.get(cmd):
                extra_commands.append(cmd)

        max_length = 0
        kila cmd kwenye (std_commands + extra_commands):
            ikiwa len(cmd) > max_length:
                max_length = len(cmd)

        self.print_command_list(std_commands,
                                "Standard commands",
                                max_length)
        ikiwa extra_commands:
            andika()
            self.print_command_list(extra_commands,
                                    "Extra commands",
                                    max_length)

    eleza get_command_list(self):
        """Get a list of (command, description) tuples.
        The list ni divided into "standard commands" (listed in
        distutils.command.__all__) na "extra commands" (mentioned in
        self.cmdclass, but sio a standard command).  The descriptions come
        kutoka the command kundi attribute 'description'.
        """
        # Currently this ni only used on Mac OS, kila the Mac-only GUI
        # Distutils interface (by Jack Jansen)
        agiza distutils.command
        std_commands = distutils.command.__all__
        is_std = {}
        kila cmd kwenye std_commands:
            is_std[cmd] = 1

        extra_commands = []
        kila cmd kwenye self.cmdclass.keys():
            ikiwa sio is_std.get(cmd):
                extra_commands.append(cmd)

        rv = []
        kila cmd kwenye (std_commands + extra_commands):
            klass = self.cmdclass.get(cmd)
            ikiwa sio klass:
                klass = self.get_command_class(cmd)
            jaribu:
                description = klass.description
            tatizo AttributeError:
                description = "(no description available)"
            rv.append((cmd, description))
        rudisha rv

    # -- Command class/object methods ----------------------------------

    eleza get_command_packages(self):
        """Return a list of packages kutoka which commands are loaded."""
        pkgs = self.command_packages
        ikiwa sio isinstance(pkgs, list):
            ikiwa pkgs ni Tupu:
                pkgs = ''
            pkgs = [pkg.strip() kila pkg kwenye pkgs.split(',') ikiwa pkg != '']
            ikiwa "distutils.command" haiko kwenye pkgs:
                pkgs.insert(0, "distutils.command")
            self.command_packages = pkgs
        rudisha pkgs

    eleza get_command_class(self, command):
        """Return the kundi that implements the Distutils command named by
        'command'.  First we check the 'cmdclass' dictionary; ikiwa the
        command ni mentioned there, we fetch the kundi object kutoka the
        dictionary na rudisha it.  Otherwise we load the command module
        ("distutils.command." + command) na fetch the command kundi from
        the module.  The loaded kundi ni also stored kwenye 'cmdclass'
        to speed future calls to 'get_command_class()'.

        Raises DistutilsModuleError ikiwa the expected module could sio be
        found, ama ikiwa that module does sio define the expected class.
        """
        klass = self.cmdclass.get(command)
        ikiwa klass:
            rudisha klass

        kila pkgname kwenye self.get_command_packages():
            module_name = "%s.%s" % (pkgname, command)
            klass_name = command

            jaribu:
                __import__(module_name)
                module = sys.modules[module_name]
            tatizo ImportError:
                endelea

            jaribu:
                klass = getattr(module, klass_name)
            tatizo AttributeError:
                ashiria DistutilsModuleError(
                    "invalid command '%s' (no kundi '%s' kwenye module '%s')"
                    % (command, klass_name, module_name))

            self.cmdclass[command] = klass
            rudisha klass

        ashiria DistutilsModuleError("invalid command '%s'" % command)

    eleza get_command_obj(self, command, create=1):
        """Return the command object kila 'command'.  Normally this object
        ni cached on a previous call to 'get_command_obj()'; ikiwa no command
        object kila 'command' ni kwenye the cache, then we either create na
        rudisha it (ikiwa 'create' ni true) ama rudisha Tupu.
        """
        cmd_obj = self.command_obj.get(command)
        ikiwa sio cmd_obj na create:
            ikiwa DEBUG:
                self.announce("Distribution.get_command_obj(): "
                              "creating '%s' command object" % command)

            klass = self.get_command_class(command)
            cmd_obj = self.command_obj[command] = klass(self)
            self.have_run[command] = 0

            # Set any options that were supplied kwenye config files
            # ama on the command line.  (NB. support kila error
            # reporting ni lame here: any errors aren't reported
            # until 'finalize_options()' ni called, which means
            # we won't report the source of the error.)
            options = self.command_options.get(command)
            ikiwa options:
                self._set_command_options(cmd_obj, options)

        rudisha cmd_obj

    eleza _set_command_options(self, command_obj, option_dict=Tupu):
        """Set the options kila 'command_obj' kutoka 'option_dict'.  Basically
        this means copying elements of a dictionary ('option_dict') to
        attributes of an instance ('command').

        'command_obj' must be a Command instance.  If 'option_dict' ni not
        supplied, uses the standard option dictionary kila this command
        (kutoka 'self.command_options').
        """
        command_name = command_obj.get_command_name()
        ikiwa option_dict ni Tupu:
            option_dict = self.get_option_dict(command_name)

        ikiwa DEBUG:
            self.announce("  setting options kila '%s' command:" % command_name)
        kila (option, (source, value)) kwenye option_dict.items():
            ikiwa DEBUG:
                self.announce("    %s = %s (kutoka %s)" % (option, value,
                                                         source))
            jaribu:
                bool_opts = [translate_longopt(o)
                             kila o kwenye command_obj.boolean_options]
            tatizo AttributeError:
                bool_opts = []
            jaribu:
                neg_opt = command_obj.negative_opt
            tatizo AttributeError:
                neg_opt = {}

            jaribu:
                is_string = isinstance(value, str)
                ikiwa option kwenye neg_opt na is_string:
                    setattr(command_obj, neg_opt[option], sio strtobool(value))
                lasivyo option kwenye bool_opts na is_string:
                    setattr(command_obj, option, strtobool(value))
                lasivyo hasattr(command_obj, option):
                    setattr(command_obj, option, value)
                isipokua:
                    ashiria DistutilsOptionError(
                        "error kwenye %s: command '%s' has no such option '%s'"
                        % (source, command_name, option))
            tatizo ValueError kama msg:
                ashiria DistutilsOptionError(msg)

    eleza reinitialize_command(self, command, reinit_subcommands=0):
        """Reinitializes a command to the state it was kwenye when first
        returned by 'get_command_obj()': ie., initialized but sio yet
        finalized.  This provides the opportunity to sneak option
        values kwenye programmatically, overriding ama supplementing
        user-supplied values kutoka the config files na command line.
        You'll have to re-finalize the command object (by calling
        'finalize_options()' ama 'ensure_finalized()') before using it for
        real.

        'command' should be a command name (string) ama command object.  If
        'reinit_subcommands' ni true, also reinitializes the command's
        sub-commands, kama declared by the 'sub_commands' kundi attribute (if
        it has one).  See the "install" command kila an example.  Only
        reinitializes the sub-commands that actually matter, ie. those
        whose test predicates rudisha true.

        Returns the reinitialized command object.
        """
        kutoka distutils.cmd agiza Command
        ikiwa sio isinstance(command, Command):
            command_name = command
            command = self.get_command_obj(command_name)
        isipokua:
            command_name = command.get_command_name()

        ikiwa sio command.finalized:
            rudisha command
        command.initialize_options()
        command.finalized = 0
        self.have_run[command_name] = 0
        self._set_command_options(command)

        ikiwa reinit_subcommands:
            kila sub kwenye command.get_sub_commands():
                self.reinitialize_command(sub, reinit_subcommands)

        rudisha command

    # -- Methods that operate on the Distribution ----------------------

    eleza announce(self, msg, level=log.INFO):
        log.log(level, msg)

    eleza run_commands(self):
        """Run each command that was seen on the setup script command line.
        Uses the list of commands found na cache of command objects
        created by 'get_command_obj()'.
        """
        kila cmd kwenye self.commands:
            self.run_command(cmd)

    # -- Methods that operate on its Commands --------------------------

    eleza run_command(self, command):
        """Do whatever it takes to run a command (including nothing at all,
        ikiwa the command has already been run).  Specifically: ikiwa we have
        already created na run the command named by 'command', return
        silently without doing anything.  If the command named by 'command'
        doesn't even have a command object yet, create one.  Then invoke
        'run()' on that command object (or an existing one).
        """
        # Already been here, done that? then rudisha silently.
        ikiwa self.have_run.get(command):
            return

        log.info("running %s", command)
        cmd_obj = self.get_command_obj(command)
        cmd_obj.ensure_finalized()
        cmd_obj.run()
        self.have_run[command] = 1

    # -- Distribution query methods ------------------------------------

    eleza has_pure_modules(self):
        rudisha len(self.packages ama self.py_modules ama []) > 0

    eleza has_ext_modules(self):
        rudisha self.ext_modules na len(self.ext_modules) > 0

    eleza has_c_libraries(self):
        rudisha self.libraries na len(self.libraries) > 0

    eleza has_modules(self):
        rudisha self.has_pure_modules() ama self.has_ext_modules()

    eleza has_headers(self):
        rudisha self.headers na len(self.headers) > 0

    eleza has_scripts(self):
        rudisha self.scripts na len(self.scripts) > 0

    eleza has_data_files(self):
        rudisha self.data_files na len(self.data_files) > 0

    eleza is_pure(self):
        rudisha (self.has_pure_modules() na
                sio self.has_ext_modules() na
                sio self.has_c_libraries())

    # -- Metadata query methods ----------------------------------------

    # If you're looking kila 'get_name()', 'get_version()', na so forth,
    # they are defined kwenye a sneaky way: the constructor binds self.get_XXX
    # to self.metadata.get_XXX.  The actual code ni kwenye the
    # DistributionMetadata class, below.

kundi DistributionMetadata:
    """Dummy kundi to hold the distribution meta-data: name, version,
    author, na so forth.
    """

    _METHOD_BASENAMES = ("name", "version", "author", "author_email",
                         "maintainer", "maintainer_email", "url",
                         "license", "description", "long_description",
                         "keywords", "platforms", "fullname", "contact",
                         "contact_email", "classifiers", "download_url",
                         # PEP 314
                         "provides", "requires", "obsoletes",
                         )

    eleza __init__(self, path=Tupu):
        ikiwa path ni sio Tupu:
            self.read_pkg_file(open(path))
        isipokua:
            self.name = Tupu
            self.version = Tupu
            self.author = Tupu
            self.author_email = Tupu
            self.maintainer = Tupu
            self.maintainer_email = Tupu
            self.url = Tupu
            self.license = Tupu
            self.description = Tupu
            self.long_description = Tupu
            self.keywords = Tupu
            self.platforms = Tupu
            self.classifiers = Tupu
            self.download_url = Tupu
            # PEP 314
            self.provides = Tupu
            self.requires = Tupu
            self.obsoletes = Tupu

    eleza read_pkg_file(self, file):
        """Reads the metadata values kutoka a file object."""
        msg = message_from_file(file)

        eleza _read_field(name):
            value = msg[name]
            ikiwa value == 'UNKNOWN':
                rudisha Tupu
            rudisha value

        eleza _read_list(name):
            values = msg.get_all(name, Tupu)
            ikiwa values == []:
                rudisha Tupu
            rudisha values

        metadata_version = msg['metadata-version']
        self.name = _read_field('name')
        self.version = _read_field('version')
        self.description = _read_field('summary')
        # we are filling author only.
        self.author = _read_field('author')
        self.maintainer = Tupu
        self.author_email = _read_field('author-email')
        self.maintainer_email = Tupu
        self.url = _read_field('home-page')
        self.license = _read_field('license')

        ikiwa 'download-url' kwenye msg:
            self.download_url = _read_field('download-url')
        isipokua:
            self.download_url = Tupu

        self.long_description = _read_field('description')
        self.description = _read_field('summary')

        ikiwa 'keywords' kwenye msg:
            self.keywords = _read_field('keywords').split(',')

        self.platforms = _read_list('platform')
        self.classifiers = _read_list('classifier')

        # PEP 314 - these fields only exist kwenye 1.1
        ikiwa metadata_version == '1.1':
            self.requires = _read_list('requires')
            self.provides = _read_list('provides')
            self.obsoletes = _read_list('obsoletes')
        isipokua:
            self.requires = Tupu
            self.provides = Tupu
            self.obsoletes = Tupu

    eleza write_pkg_info(self, base_dir):
        """Write the PKG-INFO file into the release tree.
        """
        ukijumuisha open(os.path.join(base_dir, 'PKG-INFO'), 'w',
                  encoding='UTF-8') kama pkg_info:
            self.write_pkg_file(pkg_info)

    eleza write_pkg_file(self, file):
        """Write the PKG-INFO format data to a file object.
        """
        version = '1.0'
        ikiwa (self.provides ama self.requires ama self.obsoletes ama
                self.classifiers ama self.download_url):
            version = '1.1'

        file.write('Metadata-Version: %s\n' % version)
        file.write('Name: %s\n' % self.get_name())
        file.write('Version: %s\n' % self.get_version())
        file.write('Summary: %s\n' % self.get_description())
        file.write('Home-page: %s\n' % self.get_url())
        file.write('Author: %s\n' % self.get_contact())
        file.write('Author-email: %s\n' % self.get_contact_email())
        file.write('License: %s\n' % self.get_license())
        ikiwa self.download_url:
            file.write('Download-URL: %s\n' % self.download_url)

        long_desc = rfc822_escape(self.get_long_description())
        file.write('Description: %s\n' % long_desc)

        keywords = ','.join(self.get_keywords())
        ikiwa keywords:
            file.write('Keywords: %s\n' % keywords)

        self._write_list(file, 'Platform', self.get_platforms())
        self._write_list(file, 'Classifier', self.get_classifiers())

        # PEP 314
        self._write_list(file, 'Requires', self.get_requires())
        self._write_list(file, 'Provides', self.get_provides())
        self._write_list(file, 'Obsoletes', self.get_obsoletes())

    eleza _write_list(self, file, name, values):
        kila value kwenye values:
            file.write('%s: %s\n' % (name, value))

    # -- Metadata query methods ----------------------------------------

    eleza get_name(self):
        rudisha self.name ama "UNKNOWN"

    eleza get_version(self):
        rudisha self.version ama "0.0.0"

    eleza get_fullname(self):
        rudisha "%s-%s" % (self.get_name(), self.get_version())

    eleza get_author(self):
        rudisha self.author ama "UNKNOWN"

    eleza get_author_email(self):
        rudisha self.author_email ama "UNKNOWN"

    eleza get_maintainer(self):
        rudisha self.maintainer ama "UNKNOWN"

    eleza get_maintainer_email(self):
        rudisha self.maintainer_email ama "UNKNOWN"

    eleza get_contact(self):
        rudisha self.maintainer ama self.author ama "UNKNOWN"

    eleza get_contact_email(self):
        rudisha self.maintainer_email ama self.author_email ama "UNKNOWN"

    eleza get_url(self):
        rudisha self.url ama "UNKNOWN"

    eleza get_license(self):
        rudisha self.license ama "UNKNOWN"
    get_licence = get_license

    eleza get_description(self):
        rudisha self.description ama "UNKNOWN"

    eleza get_long_description(self):
        rudisha self.long_description ama "UNKNOWN"

    eleza get_keywords(self):
        rudisha self.keywords ama []

    eleza set_keywords(self, value):
        self.keywords = _ensure_list(value, 'keywords')

    eleza get_platforms(self):
        rudisha self.platforms ama ["UNKNOWN"]

    eleza set_platforms(self, value):
        self.platforms = _ensure_list(value, 'platforms')

    eleza get_classifiers(self):
        rudisha self.classifiers ama []

    eleza set_classifiers(self, value):
        self.classifiers = _ensure_list(value, 'classifiers')

    eleza get_download_url(self):
        rudisha self.download_url ama "UNKNOWN"

    # PEP 314
    eleza get_requires(self):
        rudisha self.requires ama []

    eleza set_requires(self, value):
        agiza distutils.versionpredicate
        kila v kwenye value:
            distutils.versionpredicate.VersionPredicate(v)
        self.requires = list(value)

    eleza get_provides(self):
        rudisha self.provides ama []

    eleza set_provides(self, value):
        value = [v.strip() kila v kwenye value]
        kila v kwenye value:
            agiza distutils.versionpredicate
            distutils.versionpredicate.split_provision(v)
        self.provides = value

    eleza get_obsoletes(self):
        rudisha self.obsoletes ama []

    eleza set_obsoletes(self, value):
        agiza distutils.versionpredicate
        kila v kwenye value:
            distutils.versionpredicate.VersionPredicate(v)
        self.obsoletes = list(value)

eleza fix_help_options(options):
    """Convert a 4-tuple 'help_options' list kama found kwenye various command
    classes to the 3-tuple form required by FancyGetopt.
    """
    new_options = []
    kila help_tuple kwenye options:
        new_options.append(help_tuple[0:3])
    rudisha new_options
