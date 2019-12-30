"""distutils.command.install_lib

Implements the Distutils 'install_lib' command
(install all Python modules)."""

agiza os
agiza importlib.util
agiza sys

kutoka distutils.core agiza Command
kutoka distutils.errors agiza DistutilsOptionError


# Extension kila Python source files.
PYTHON_SOURCE_EXTENSION = ".py"

kundi install_lib(Command):

    description = "install all Python modules (extensions na pure Python)"

    # The byte-compilation options are a tad confusing.  Here are the
    # possible scenarios:
    #   1) no compilation at all (--no-compile --no-optimize)
    #   2) compile .pyc only (--compile --no-optimize; default)
    #   3) compile .pyc na "opt-1" .pyc (--compile --optimize)
    #   4) compile "opt-1" .pyc only (--no-compile --optimize)
    #   5) compile .pyc na "opt-2" .pyc (--compile --optimize-more)
    #   6) compile "opt-2" .pyc only (--no-compile --optimize-more)
    #
    # The UI kila this ni two options, 'compile' na 'optimize'.
    # 'compile' ni strictly boolean, na only decides whether to
    # generate .pyc files.  'optimize' ni three-way (0, 1, ama 2), na
    # decides both whether to generate .pyc files na what level of
    # optimization to use.

    user_options = [
        ('install-dir=', 'd', "directory to install to"),
        ('build-dir=','b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ('compile', 'c', "compile .py to .pyc [default]"),
        ('no-compile', Tupu, "don't compile .py files"),
        ('optimize=', 'O',
         "also compile ukijumuisha optimization: -O1 kila \"python -O\", "
         "-O2 kila \"python -OO\", na -O0 to disable [default: -O0]"),
        ('skip-build', Tupu, "skip the build steps"),
        ]

    boolean_options = ['force', 'compile', 'skip-build']
    negative_opt = {'no-compile' : 'compile'}

    eleza initialize_options(self):
        # let the 'install' command dictate our installation directory
        self.install_dir = Tupu
        self.build_dir = Tupu
        self.force = 0
        self.compile = Tupu
        self.optimize = Tupu
        self.skip_build = Tupu

    eleza finalize_options(self):
        # Get all the information we need to install pure Python modules
        # kutoka the umbrella 'install' command -- build (source) directory,
        # install (target) directory, na whether to compile .py files.
        self.set_undefined_options('install',
                                   ('build_lib', 'build_dir'),
                                   ('install_lib', 'install_dir'),
                                   ('force', 'force'),
                                   ('compile', 'compile'),
                                   ('optimize', 'optimize'),
                                   ('skip_build', 'skip_build'),
                                  )

        ikiwa self.compile ni Tupu:
            self.compile = Kweli
        ikiwa self.optimize ni Tupu:
            self.optimize = Uongo

        ikiwa sio isinstance(self.optimize, int):
            jaribu:
                self.optimize = int(self.optimize)
                ikiwa self.optimize haiko kwenye (0, 1, 2):
                    ashiria AssertionError
            tatizo (ValueError, AssertionError):
                ashiria DistutilsOptionError("optimize must be 0, 1, ama 2")

    eleza run(self):
        # Make sure we have built everything we need first
        self.build()

        # Install everything: simply dump the entire contents of the build
        # directory to the installation directory (that's the beauty of
        # having a build directory!)
        outfiles = self.install()

        # (Optionally) compile .py to .pyc
        ikiwa outfiles ni sio Tupu na self.distribution.has_pure_modules():
            self.byte_compile(outfiles)

    # -- Top-level worker functions ------------------------------------
    # (called kutoka 'run()')

    eleza build(self):
        ikiwa sio self.skip_build:
            ikiwa self.distribution.has_pure_modules():
                self.run_command('build_py')
            ikiwa self.distribution.has_ext_modules():
                self.run_command('build_ext')

    eleza install(self):
        ikiwa os.path.isdir(self.build_dir):
            outfiles = self.copy_tree(self.build_dir, self.install_dir)
        isipokua:
            self.warn("'%s' does sio exist -- no Python modules to install" %
                      self.build_dir)
            return
        rudisha outfiles

    eleza byte_compile(self, files):
        ikiwa sys.dont_write_bytecode:
            self.warn('byte-compiling ni disabled, skipping.')
            return

        kutoka distutils.util agiza byte_compile

        # Get the "--root" directory supplied to the "install" command,
        # na use it kama a prefix to strip off the purported filename
        # encoded kwenye bytecode files.  This ni far kutoka complete, but it
        # should at least generate usable bytecode kwenye RPM distributions.
        install_root = self.get_finalized_command('install').root

        ikiwa self.compile:
            byte_compile(files, optimize=0,
                         force=self.force, prefix=install_root,
                         dry_run=self.dry_run)
        ikiwa self.optimize > 0:
            byte_compile(files, optimize=self.optimize,
                         force=self.force, prefix=install_root,
                         verbose=self.verbose, dry_run=self.dry_run)


    # -- Utility methods -----------------------------------------------

    eleza _mutate_outputs(self, has_any, build_cmd, cmd_option, output_dir):
        ikiwa sio has_any:
            rudisha []

        build_cmd = self.get_finalized_command(build_cmd)
        build_files = build_cmd.get_outputs()
        build_dir = getattr(build_cmd, cmd_option)

        prefix_len = len(build_dir) + len(os.sep)
        outputs = []
        kila file kwenye build_files:
            outputs.append(os.path.join(output_dir, file[prefix_len:]))

        rudisha outputs

    eleza _bytecode_filenames(self, py_filenames):
        bytecode_files = []
        kila py_file kwenye py_filenames:
            # Since build_py handles package data installation, the
            # list of outputs can contain more than just .py files.
            # Make sure we only report bytecode kila the .py files.
            ext = os.path.splitext(os.path.normcase(py_file))[1]
            ikiwa ext != PYTHON_SOURCE_EXTENSION:
                endelea
            ikiwa self.compile:
                bytecode_files.append(importlib.util.cache_from_source(
                    py_file, optimization=''))
            ikiwa self.optimize > 0:
                bytecode_files.append(importlib.util.cache_from_source(
                    py_file, optimization=self.optimize))

        rudisha bytecode_files


    # -- External interface --------------------------------------------
    # (called by outsiders)

    eleza get_outputs(self):
        """Return the list of files that would be installed ikiwa this command
        were actually run.  Not affected by the "dry-run" flag ama whether
        modules have actually been built yet.
        """
        pure_outputs = \
            self._mutate_outputs(self.distribution.has_pure_modules(),
                                 'build_py', 'build_lib',
                                 self.install_dir)
        ikiwa self.compile:
            bytecode_outputs = self._bytecode_filenames(pure_outputs)
        isipokua:
            bytecode_outputs = []

        ext_outputs = \
            self._mutate_outputs(self.distribution.has_ext_modules(),
                                 'build_ext', 'build_lib',
                                 self.install_dir)

        rudisha pure_outputs + bytecode_outputs + ext_outputs

    eleza get_inputs(self):
        """Get the list of files that are input to this command, ie. the
        files that get installed kama they are named kwenye the build tree.
        The files kwenye this list correspond one-to-one to the output
        filenames returned by 'get_outputs()'.
        """
        inputs = []

        ikiwa self.distribution.has_pure_modules():
            build_py = self.get_finalized_command('build_py')
            inputs.extend(build_py.get_outputs())

        ikiwa self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            inputs.extend(build_ext.get_outputs())

        rudisha inputs
