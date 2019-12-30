"""distutils.command.build

Implements the Distutils 'build' command."""

agiza sys, os
kutoka distutils.core agiza Command
kutoka distutils.errors agiza DistutilsOptionError
kutoka distutils.util agiza get_platform


eleza show_compilers():
    kutoka distutils.ccompiler agiza show_compilers
    show_compilers()


kundi build(Command):

    description = "build everything needed to install"

    user_options = [
        ('build-base=', 'b',
         "base directory kila build library"),
        ('build-purelib=', Tupu,
         "build directory kila platform-neutral distributions"),
        ('build-platlib=', Tupu,
         "build directory kila platform-specific distributions"),
        ('build-lib=', Tupu,
         "build directory kila all distribution (defaults to either " +
         "build-purelib ama build-platlib"),
        ('build-scripts=', Tupu,
         "build directory kila scripts"),
        ('build-temp=', 't',
         "temporary build directory"),
        ('plat-name=', 'p',
         "platform name to build for, ikiwa supported "
         "(default: %s)" % get_platform()),
        ('compiler=', 'c',
         "specify the compiler type"),
        ('parallel=', 'j',
         "number of parallel build jobs"),
        ('debug', 'g',
         "compile extensions na libraries ukijumuisha debugging information"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
        ('executable=', 'e',
         "specify final destination interpreter path (build.py)"),
        ]

    boolean_options = ['debug', 'force']

    help_options = [
        ('help-compiler', Tupu,
         "list available compilers", show_compilers),
        ]

    eleza initialize_options(self):
        self.build_base = 'build'
        # these are decided only after 'build_base' has its final value
        # (unless overridden by the user ama client)
        self.build_purelib = Tupu
        self.build_platlib = Tupu
        self.build_lib = Tupu
        self.build_temp = Tupu
        self.build_scripts = Tupu
        self.compiler = Tupu
        self.plat_name = Tupu
        self.debug = Tupu
        self.force = 0
        self.executable = Tupu
        self.parallel = Tupu

    eleza finalize_options(self):
        ikiwa self.plat_name ni Tupu:
            self.plat_name = get_platform()
        isipokua:
            # plat-name only supported kila windows (other platforms are
            # supported via ./configure flags, ikiwa at all).  Avoid misleading
            # other platforms.
            ikiwa os.name != 'nt':
                 ashiria DistutilsOptionError(
                            "--plat-name only supported on Windows (try "
                            "using './configure --help' on your platform)")

        plat_specifier = ".%s-%d.%d" % (self.plat_name, *sys.version_info[:2])

        # Make it so Python 2.x na Python 2.x ukijumuisha --with-pydebug don't
        # share the same build directories. Doing so confuses the build
        # process kila C modules
        ikiwa hasattr(sys, 'gettotalrefcount'):
            plat_specifier += '-pydebug'

        # 'build_purelib' na 'build_platlib' just default to 'lib' and
        # 'lib.<plat>' under the base build directory.  We only use one of
        # them kila a given distribution, though --
        ikiwa self.build_purelib ni Tupu:
            self.build_purelib = os.path.join(self.build_base, 'lib')
        ikiwa self.build_platlib ni Tupu:
            self.build_platlib = os.path.join(self.build_base,
                                              'lib' + plat_specifier)

        # 'build_lib' ni the actual directory that we will use kila this
        # particular module distribution -- ikiwa user didn't supply it, pick
        # one of 'build_purelib' ama 'build_platlib'.
        ikiwa self.build_lib ni Tupu:
            ikiwa self.distribution.ext_modules:
                self.build_lib = self.build_platlib
            isipokua:
                self.build_lib = self.build_purelib

        # 'build_temp' -- temporary directory kila compiler turds,
        # "build/temp.<plat>"
        ikiwa self.build_temp ni Tupu:
            self.build_temp = os.path.join(self.build_base,
                                           'temp' + plat_specifier)
        ikiwa self.build_scripts ni Tupu:
            self.build_scripts = os.path.join(self.build_base,
                                              'scripts-%d.%d' % sys.version_info[:2])

        ikiwa self.executable ni Tupu na sys.executable:
            self.executable = os.path.normpath(sys.executable)

        ikiwa isinstance(self.parallel, str):
            jaribu:
                self.parallel = int(self.parallel)
            except ValueError:
                 ashiria DistutilsOptionError("parallel should be an integer")

    eleza run(self):
        # Run all relevant sub-commands.  This will be some subset of:
        #  - build_py      - pure Python modules
        #  - build_clib    - standalone C libraries
        #  - build_ext     - Python extensions
        #  - build_scripts - (Python) scripts
        kila cmd_name kwenye self.get_sub_commands():
            self.run_command(cmd_name)


    # -- Predicates kila the sub-command list ---------------------------

    eleza has_pure_modules(self):
        rudisha self.distribution.has_pure_modules()

    eleza has_c_libraries(self):
        rudisha self.distribution.has_c_libraries()

    eleza has_ext_modules(self):
        rudisha self.distribution.has_ext_modules()

    eleza has_scripts(self):
        rudisha self.distribution.has_scripts()


    sub_commands = [('build_py',      has_pure_modules),
                    ('build_clib',    has_c_libraries),
                    ('build_ext',     has_ext_modules),
                    ('build_scripts', has_scripts),
                   ]
