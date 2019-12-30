"""distutils.command.install

Implements the Distutils 'install' command."""

agiza sys
agiza os

kutoka distutils agiza log
kutoka distutils.core agiza Command
kutoka distutils.debug agiza DEBUG
kutoka distutils.sysconfig agiza get_config_vars
kutoka distutils.errors agiza DistutilsPlatformError
kutoka distutils.file_util agiza write_file
kutoka distutils.util agiza convert_path, subst_vars, change_root
kutoka distutils.util agiza get_platform
kutoka distutils.errors agiza DistutilsOptionError

kutoka site agiza USER_BASE
kutoka site agiza USER_SITE
HAS_USER_SITE = Kweli

WINDOWS_SCHEME = {
    'purelib': '$base/Lib/site-packages',
    'platlib': '$base/Lib/site-packages',
    'headers': '$base/Include/$dist_name',
    'scripts': '$base/Scripts',
    'data'   : '$base',
}

INSTALL_SCHEMES = {
    'unix_prefix': {
        'purelib': '$base/lib/python$py_version_short/site-packages',
        'platlib': '$platbase/lib/python$py_version_short/site-packages',
        'headers': '$base/include/python$py_version_short$abiflags/$dist_name',
        'scripts': '$base/bin',
        'data'   : '$base',
        },
    'unix_home': {
        'purelib': '$base/lib/python',
        'platlib': '$base/lib/python',
        'headers': '$base/include/python/$dist_name',
        'scripts': '$base/bin',
        'data'   : '$base',
        },
    'nt': WINDOWS_SCHEME,
    }

# user site schemes
ikiwa HAS_USER_SITE:
    INSTALL_SCHEMES['nt_user'] = {
        'purelib': '$usersite',
        'platlib': '$usersite',
        'headers': '$userbase/Python$py_version_nodot/Include/$dist_name',
        'scripts': '$userbase/Python$py_version_nodot/Scripts',
        'data'   : '$userbase',
        }

    INSTALL_SCHEMES['unix_user'] = {
        'purelib': '$usersite',
        'platlib': '$usersite',
        'headers':
            '$userbase/include/python$py_version_short$abiflags/$dist_name',
        'scripts': '$userbase/bin',
        'data'   : '$userbase',
        }

# The keys to an installation scheme; ikiwa any new types of files are to be
# installed, be sure to add an entry to every installation scheme above,
# na to SCHEME_KEYS here.
SCHEME_KEYS = ('purelib', 'platlib', 'headers', 'scripts', 'data')


kundi install(Command):

    description = "install everything kutoka build directory"

    user_options = [
        # Select installation scheme na set base director(y|ies)
        ('prefix=', Tupu,
         "installation prefix"),
        ('exec-prefix=', Tupu,
         "(Unix only) prefix kila platform-specific files"),
        ('home=', Tupu,
         "(Unix only) home directory to install under"),

        # Or, just set the base director(y|ies)
        ('install-base=', Tupu,
         "base installation directory (instead of --prefix ama --home)"),
        ('install-platbase=', Tupu,
         "base installation directory kila platform-specific files " +
         "(instead of --exec-prefix ama --home)"),
        ('root=', Tupu,
         "install everything relative to this alternate root directory"),

        # Or, explicitly set the installation scheme
        ('install-purelib=', Tupu,
         "installation directory kila pure Python module distributions"),
        ('install-platlib=', Tupu,
         "installation directory kila non-pure module distributions"),
        ('install-lib=', Tupu,
         "installation directory kila all module distributions " +
         "(overrides --install-purelib na --install-platlib)"),

        ('install-headers=', Tupu,
         "installation directory kila C/C++ headers"),
        ('install-scripts=', Tupu,
         "installation directory kila Python scripts"),
        ('install-data=', Tupu,
         "installation directory kila data files"),

        # Byte-compilation options -- see install_lib.py kila details, as
        # these are duplicated kutoka there (but only install_lib does
        # anything ukijumuisha them).
        ('compile', 'c', "compile .py to .pyc [default]"),
        ('no-compile', Tupu, "don't compile .py files"),
        ('optimize=', 'O',
         "also compile ukijumuisha optimization: -O1 kila \"python -O\", "
         "-O2 kila \"python -OO\", na -O0 to disable [default: -O0]"),

        # Miscellaneous control options
        ('force', 'f',
         "force installation (overwrite any existing files)"),
        ('skip-build', Tupu,
         "skip rebuilding everything (kila testing/debugging)"),

        # Where to install documentation (eventually!)
        #('doc-format=', Tupu, "format of documentation to generate"),
        #('install-man=', Tupu, "directory kila Unix man pages"),
        #('install-html=', Tupu, "directory kila HTML documentation"),
        #('install-info=', Tupu, "directory kila GNU info files"),

        ('record=', Tupu,
         "filename kwenye which to record list of installed files"),
        ]

    boolean_options = ['compile', 'force', 'skip-build']

    ikiwa HAS_USER_SITE:
        user_options.append(('user', Tupu,
                             "install kwenye user site-package '%s'" % USER_SITE))
        boolean_options.append('user')

    negative_opt = {'no-compile' : 'compile'}


    eleza initialize_options(self):
        """Initializes options."""
        # High-level options: these select both an installation base
        # na scheme.
        self.prefix = Tupu
        self.exec_prefix = Tupu
        self.home = Tupu
        self.user = 0

        # These select only the installation base; it's up to the user to
        # specify the installation scheme (currently, that means supplying
        # the --install-{platlib,purelib,scripts,data} options).
        self.install_base = Tupu
        self.install_platbase = Tupu
        self.root = Tupu

        # These options are the actual installation directories; ikiwa not
        # supplied by the user, they are filled kwenye using the installation
        # scheme implied by prefix/exec-prefix/home na the contents of
        # that installation scheme.
        self.install_purelib = Tupu     # kila pure module distributions
        self.install_platlib = Tupu     # non-pure (dists w/ extensions)
        self.install_headers = Tupu     # kila C/C++ headers
        self.install_lib = Tupu         # set to either purelib ama platlib
        self.install_scripts = Tupu
        self.install_data = Tupu
        self.install_userbase = USER_BASE
        self.install_usersite = USER_SITE

        self.compile = Tupu
        self.optimize = Tupu

        # Deprecated
        # These two are kila putting non-packagized distributions into their
        # own directory na creating a .pth file ikiwa it makes sense.
        # 'extra_path' comes kutoka the setup file; 'install_path_file' can
        # be turned off ikiwa it makes no sense to install a .pth file.  (But
        # better to install it uselessly than to guess wrong na not
        # install it when it's necessary na would be used!)  Currently,
        # 'install_path_file' ni always true unless some outsider meddles
        # ukijumuisha it.
        self.extra_path = Tupu
        self.install_path_file = 1

        # 'force' forces installation, even ikiwa target files are not
        # out-of-date.  'skip_build' skips running the "build" command,
        # handy ikiwa you know it's sio necessary.  'warn_dir' (which ni *not*
        # a user option, it's just there so the bdist_* commands can turn
        # it off) determines whether we warn about installing to a
        # directory haiko kwenye sys.path.
        self.force = 0
        self.skip_build = 0
        self.warn_dir = 1

        # These are only here kama a conduit kutoka the 'build' command to the
        # 'install_*' commands that do the real work.  ('build_base' isn't
        # actually used anywhere, but it might be useful kwenye future.)  They
        # are sio user options, because ikiwa the user told the install
        # command where the build directory is, that wouldn't affect the
        # build command.
        self.build_base = Tupu
        self.build_lib = Tupu

        # Not defined yet because we don't know anything about
        # documentation yet.
        #self.install_man = Tupu
        #self.install_html = Tupu
        #self.install_info = Tupu

        self.record = Tupu


    # -- Option finalizing methods -------------------------------------
    # (This ni rather more involved than kila most commands,
    # because this ni where the policy kila installing third-
    # party Python modules on various platforms given a wide
    # array of user input ni decided.  Yes, it's quite complex!)

    eleza finalize_options(self):
        """Finalizes options."""
        # This method (and its helpers, like 'finalize_unix()',
        # 'finalize_other()', na 'select_scheme()') ni where the default
        # installation directories kila modules, extension modules, na
        # anything isipokua we care to install kutoka a Python module
        # distribution.  Thus, this code makes a pretty important policy
        # statement about how third-party stuff ni added to a Python
        # installation!  Note that the actual work of installation ni done
        # by the relatively simple 'install_*' commands; they just take
        # their orders kutoka the installation directory options determined
        # here.

        # Check kila errors/inconsistencies kwenye the options; first, stuff
        # that's wrong on any platform.

        ikiwa ((self.prefix ama self.exec_prefix ama self.home) na
            (self.install_base ama self.install_platbase)):
            ashiria DistutilsOptionError(
                   "must supply either prefix/exec-prefix/home ama " +
                   "install-base/install-platbase -- sio both")

        ikiwa self.home na (self.prefix ama self.exec_prefix):
            ashiria DistutilsOptionError(
                  "must supply either home ama prefix/exec-prefix -- sio both")

        ikiwa self.user na (self.prefix ama self.exec_prefix ama self.home ama
                self.install_base ama self.install_platbase):
            ashiria DistutilsOptionError("can't combine user ukijumuisha prefix, "
                                       "exec_prefix/home, ama install_(plat)base")

        # Next, stuff that's wrong (or dubious) only on certain platforms.
        ikiwa os.name != "posix":
            ikiwa self.exec_prefix:
                self.warn("exec-prefix option ignored on this platform")
                self.exec_prefix = Tupu

        # Now the interesting logic -- so interesting that we farm it out
        # to other methods.  The goal of these methods ni to set the final
        # values kila the install_{lib,scripts,data,...}  options, using as
        # input a heady brew of prefix, exec_prefix, home, install_base,
        # install_platbase, user-supplied versions of
        # install_{purelib,platlib,lib,scripts,data,...}, na the
        # INSTALL_SCHEME dictionary above.  Phew!

        self.dump_dirs("pre-finalize_{unix,other}")

        ikiwa os.name == 'posix':
            self.finalize_unix()
        isipokua:
            self.finalize_other()

        self.dump_dirs("post-finalize_{unix,other}()")

        # Expand configuration variables, tilde, etc. kwenye self.install_base
        # na self.install_platbase -- that way, we can use $base ama
        # $platbase kwenye the other installation directories na sio worry
        # about needing recursive variable expansion (shudder).

        py_version = sys.version.split()[0]
        (prefix, exec_prefix) = get_config_vars('prefix', 'exec_prefix')
        jaribu:
            abiflags = sys.abiflags
        tatizo AttributeError:
            # sys.abiflags may sio be defined on all platforms.
            abiflags = ''
        self.config_vars = {'dist_name': self.distribution.get_name(),
                            'dist_version': self.distribution.get_version(),
                            'dist_fullname': self.distribution.get_fullname(),
                            'py_version': py_version,
                            'py_version_short': '%d.%d' % sys.version_info[:2],
                            'py_version_nodot': '%d%d' % sys.version_info[:2],
                            'sys_prefix': prefix,
                            'prefix': prefix,
                            'sys_exec_prefix': exec_prefix,
                            'exec_prefix': exec_prefix,
                            'abiflags': abiflags,
                           }

        ikiwa HAS_USER_SITE:
            self.config_vars['userbase'] = self.install_userbase
            self.config_vars['usersite'] = self.install_usersite

        self.expand_basedirs()

        self.dump_dirs("post-expand_basedirs()")

        # Now define config vars kila the base directories so we can expand
        # everything else.
        self.config_vars['base'] = self.install_base
        self.config_vars['platbase'] = self.install_platbase

        ikiwa DEBUG:
            kutoka pprint agiza pprint
            andika("config vars:")
            pandika(self.config_vars)

        # Expand "~" na configuration variables kwenye the installation
        # directories.
        self.expand_dirs()

        self.dump_dirs("post-expand_dirs()")

        # Create directories kwenye the home dir:
        ikiwa self.user:
            self.create_home_path()

        # Pick the actual directory to install all modules to: either
        # install_purelib ama install_platlib, depending on whether this
        # module distribution ni pure ama not.  Of course, ikiwa the user
        # already specified install_lib, use their selection.
        ikiwa self.install_lib ni Tupu:
            ikiwa self.distribution.ext_modules: # has extensions: non-pure
                self.install_lib = self.install_platlib
            isipokua:
                self.install_lib = self.install_purelib


        # Convert directories kutoka Unix /-separated syntax to the local
        # convention.
        self.convert_paths('lib', 'purelib', 'platlib',
                           'scripts', 'data', 'headers',
                           'userbase', 'usersite')

        # Deprecated
        # Well, we're sio actually fully completely finalized yet: we still
        # have to deal ukijumuisha 'extra_path', which ni the hack kila allowing
        # non-packagized module distributions (hello, Numerical Python!) to
        # get their own directories.
        self.handle_extra_path()
        self.install_libbase = self.install_lib # needed kila .pth file
        self.install_lib = os.path.join(self.install_lib, self.extra_dirs)

        # If a new root directory was supplied, make all the installation
        # dirs relative to it.
        ikiwa self.root ni sio Tupu:
            self.change_roots('libbase', 'lib', 'purelib', 'platlib',
                              'scripts', 'data', 'headers')

        self.dump_dirs("after prepending root")

        # Find out the build directories, ie. where to install from.
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'),
                                   ('build_lib', 'build_lib'))

        # Punt on doc directories kila now -- after all, we're punting on
        # documentation completely!

    eleza dump_dirs(self, msg):
        """Dumps the list of user options."""
        ikiwa sio DEBUG:
            return
        kutoka distutils.fancy_getopt agiza longopt_xlate
        log.debug(msg + ":")
        kila opt kwenye self.user_options:
            opt_name = opt[0]
            ikiwa opt_name[-1] == "=":
                opt_name = opt_name[0:-1]
            ikiwa opt_name kwenye self.negative_opt:
                opt_name = self.negative_opt[opt_name]
                opt_name = opt_name.translate(longopt_xlate)
                val = sio getattr(self, opt_name)
            isipokua:
                opt_name = opt_name.translate(longopt_xlate)
                val = getattr(self, opt_name)
            log.debug("  %s: %s", opt_name, val)

    eleza finalize_unix(self):
        """Finalizes options kila posix platforms."""
        ikiwa self.install_base ni sio Tupu ama self.install_platbase ni sio Tupu:
            ikiwa ((self.install_lib ni Tupu na
                 self.install_purelib ni Tupu na
                 self.install_platlib ni Tupu) ama
                self.install_headers ni Tupu ama
                self.install_scripts ni Tupu ama
                self.install_data ni Tupu):
                ashiria DistutilsOptionError(
                      "install-base ama install-platbase supplied, but "
                      "installation scheme ni incomplete")
            return

        ikiwa self.user:
            ikiwa self.install_userbase ni Tupu:
                ashiria DistutilsPlatformError(
                    "User base directory ni sio specified")
            self.install_base = self.install_platbase = self.install_userbase
            self.select_scheme("unix_user")
        lasivyo self.home ni sio Tupu:
            self.install_base = self.install_platbase = self.home
            self.select_scheme("unix_home")
        isipokua:
            ikiwa self.prefix ni Tupu:
                ikiwa self.exec_prefix ni sio Tupu:
                    ashiria DistutilsOptionError(
                          "must sio supply exec-prefix without prefix")

                self.prefix = os.path.normpath(sys.prefix)
                self.exec_prefix = os.path.normpath(sys.exec_prefix)

            isipokua:
                ikiwa self.exec_prefix ni Tupu:
                    self.exec_prefix = self.prefix

            self.install_base = self.prefix
            self.install_platbase = self.exec_prefix
            self.select_scheme("unix_prefix")

    eleza finalize_other(self):
        """Finalizes options kila non-posix platforms"""
        ikiwa self.user:
            ikiwa self.install_userbase ni Tupu:
                ashiria DistutilsPlatformError(
                    "User base directory ni sio specified")
            self.install_base = self.install_platbase = self.install_userbase
            self.select_scheme(os.name + "_user")
        lasivyo self.home ni sio Tupu:
            self.install_base = self.install_platbase = self.home
            self.select_scheme("unix_home")
        isipokua:
            ikiwa self.prefix ni Tupu:
                self.prefix = os.path.normpath(sys.prefix)

            self.install_base = self.install_platbase = self.prefix
            jaribu:
                self.select_scheme(os.name)
            tatizo KeyError:
                ashiria DistutilsPlatformError(
                      "I don't know how to install stuff on '%s'" % os.name)

    eleza select_scheme(self, name):
        """Sets the install directories by applying the install schemes."""
        # it's the caller's problem ikiwa they supply a bad name!
        scheme = INSTALL_SCHEMES[name]
        kila key kwenye SCHEME_KEYS:
            attrname = 'install_' + key
            ikiwa getattr(self, attrname) ni Tupu:
                setattr(self, attrname, scheme[key])

    eleza _expand_attrs(self, attrs):
        kila attr kwenye attrs:
            val = getattr(self, attr)
            ikiwa val ni sio Tupu:
                ikiwa os.name == 'posix' ama os.name == 'nt':
                    val = os.path.expanduser(val)
                val = subst_vars(val, self.config_vars)
                setattr(self, attr, val)

    eleza expand_basedirs(self):
        """Calls `os.path.expanduser` on install_base, install_platbase na
        root."""
        self._expand_attrs(['install_base', 'install_platbase', 'root'])

    eleza expand_dirs(self):
        """Calls `os.path.expanduser` on install dirs."""
        self._expand_attrs(['install_purelib', 'install_platlib',
                            'install_lib', 'install_headers',
                            'install_scripts', 'install_data',])

    eleza convert_paths(self, *names):
        """Call `convert_path` over `names`."""
        kila name kwenye names:
            attr = "install_" + name
            setattr(self, attr, convert_path(getattr(self, attr)))

    eleza handle_extra_path(self):
        """Set `path_file` na `extra_dirs` using `extra_path`."""
        ikiwa self.extra_path ni Tupu:
            self.extra_path = self.distribution.extra_path

        ikiwa self.extra_path ni sio Tupu:
            log.warn(
                "Distribution option extra_path ni deprecated. "
                "See issue27919 kila details."
            )
            ikiwa isinstance(self.extra_path, str):
                self.extra_path = self.extra_path.split(',')

            ikiwa len(self.extra_path) == 1:
                path_file = extra_dirs = self.extra_path[0]
            lasivyo len(self.extra_path) == 2:
                path_file, extra_dirs = self.extra_path
            isipokua:
                ashiria DistutilsOptionError(
                      "'extra_path' option must be a list, tuple, ama "
                      "comma-separated string ukijumuisha 1 ama 2 elements")

            # convert to local form kwenye case Unix notation used (as it
            # should be kwenye setup scripts)
            extra_dirs = convert_path(extra_dirs)
        isipokua:
            path_file = Tupu
            extra_dirs = ''

        # XXX should we warn ikiwa path_file na sio extra_dirs? (in which
        # case the path file would be harmless but pointless)
        self.path_file = path_file
        self.extra_dirs = extra_dirs

    eleza change_roots(self, *names):
        """Change the install directories pointed by name using root."""
        kila name kwenye names:
            attr = "install_" + name
            setattr(self, attr, change_root(self.root, getattr(self, attr)))

    eleza create_home_path(self):
        """Create directories under ~."""
        ikiwa sio self.user:
            return
        home = convert_path(os.path.expanduser("~"))
        kila name, path kwenye self.config_vars.items():
            ikiwa path.startswith(home) na sio os.path.isdir(path):
                self.debug_andika("os.makedirs('%s', 0o700)" % path)
                os.makedirs(path, 0o700)

    # -- Command execution methods -------------------------------------

    eleza run(self):
        """Runs the command."""
        # Obviously have to build before we can install
        ikiwa sio self.skip_build:
            self.run_command('build')
            # If we built kila any other platform, we can't install.
            build_plat = self.distribution.get_command_obj('build').plat_name
            # check warn_dir - it ni a clue that the 'install' ni happening
            # internally, na sio to sys.path, so we don't check the platform
            # matches what we are running.
            ikiwa self.warn_dir na build_plat != get_platform():
                ashiria DistutilsPlatformError("Can't install when "
                                             "cross-compiling")

        # Run all sub-commands (at least those that need to be run)
        kila cmd_name kwenye self.get_sub_commands():
            self.run_command(cmd_name)

        ikiwa self.path_file:
            self.create_path_file()

        # write list of installed files, ikiwa requested.
        ikiwa self.record:
            outputs = self.get_outputs()
            ikiwa self.root:               # strip any package prefix
                root_len = len(self.root)
                kila counter kwenye range(len(outputs)):
                    outputs[counter] = outputs[counter][root_len:]
            self.execute(write_file,
                         (self.record, outputs),
                         "writing list of installed files to '%s'" %
                         self.record)

        sys_path = map(os.path.normpath, sys.path)
        sys_path = map(os.path.normcase, sys_path)
        install_lib = os.path.normcase(os.path.normpath(self.install_lib))
        ikiwa (self.warn_dir na
            sio (self.path_file na self.install_path_file) na
            install_lib haiko kwenye sys_path):
            log.debug(("modules installed to '%s', which ni haiko kwenye "
                       "Python's module search path (sys.path) -- "
                       "you'll have to change the search path yourself"),
                       self.install_lib)

    eleza create_path_file(self):
        """Creates the .pth file"""
        filename = os.path.join(self.install_libbase,
                                self.path_file + ".pth")
        ikiwa self.install_path_file:
            self.execute(write_file,
                         (filename, [self.extra_dirs]),
                         "creating %s" % filename)
        isipokua:
            self.warn("path file '%s' sio created" % filename)


    # -- Reporting methods ---------------------------------------------

    eleza get_outputs(self):
        """Assembles the outputs of all the sub-commands."""
        outputs = []
        kila cmd_name kwenye self.get_sub_commands():
            cmd = self.get_finalized_command(cmd_name)
            # Add the contents of cmd.get_outputs(), ensuring
            # that outputs doesn't contain duplicate entries
            kila filename kwenye cmd.get_outputs():
                ikiwa filename haiko kwenye outputs:
                    outputs.append(filename)

        ikiwa self.path_file na self.install_path_file:
            outputs.append(os.path.join(self.install_libbase,
                                        self.path_file + ".pth"))

        rudisha outputs

    eleza get_inputs(self):
        """Returns the inputs of all the sub-commands"""
        # XXX gee, this looks familiar ;-(
        inputs = []
        kila cmd_name kwenye self.get_sub_commands():
            cmd = self.get_finalized_command(cmd_name)
            inputs.extend(cmd.get_inputs())

        rudisha inputs

    # -- Predicates kila sub-command list -------------------------------

    eleza has_lib(self):
        """Returns true ikiwa the current distribution has any Python
        modules to install."""
        rudisha (self.distribution.has_pure_modules() ama
                self.distribution.has_ext_modules())

    eleza has_headers(self):
        """Returns true ikiwa the current distribution has any headers to
        install."""
        rudisha self.distribution.has_headers()

    eleza has_scripts(self):
        """Returns true ikiwa the current distribution has any scripts to.
        install."""
        rudisha self.distribution.has_scripts()

    eleza has_data(self):
        """Returns true ikiwa the current distribution has any data to.
        install."""
        rudisha self.distribution.has_data_files()

    # 'sub_commands': a list of commands this command might have to run to
    # get its work done.  See cmd.py kila more info.
    sub_commands = [('install_lib',     has_lib),
                    ('install_headers', has_headers),
                    ('install_scripts', has_scripts),
                    ('install_data',    has_data),
                    ('install_egg_info', lambda self:Kweli),
                   ]
