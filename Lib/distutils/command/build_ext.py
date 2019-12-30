"""distutils.command.build_ext

Implements the Distutils 'build_ext' command, kila building extension
modules (currently limited to C extensions, should accommodate C++
extensions ASAP)."""

agiza contextlib
agiza os
agiza re
agiza sys
kutoka distutils.core agiza Command
kutoka distutils.errors agiza *
kutoka distutils.sysconfig agiza customize_compiler, get_python_version
kutoka distutils.sysconfig agiza get_config_h_filename
kutoka distutils.dep_util agiza newer_group
kutoka distutils.extension agiza Extension
kutoka distutils.util agiza get_platform
kutoka distutils agiza log

kutoka site agiza USER_BASE

# An extension name ni just a dot-separated list of Python NAMEs (ie.
# the same kama a fully-qualified module name).
extension_name_re = re.compile \
    (r'^[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_][a-zA-Z_0-9]*)*$')


eleza show_compilers ():
    kutoka distutils.ccompiler agiza show_compilers
    show_compilers()


kundi build_ext(Command):

    description = "build C/C++ extensions (compile/link to build directory)"

    # XXX thoughts on how to deal ukijumuisha complex command-line options like
    # these, i.e. how to make it so fancy_getopt can suck them off the
    # command line na make it look like setup.py defined the appropriate
    # lists of tuples of what-have-you.
    #   - each command needs a callback to process its command-line options
    #   - Command.__init__() needs access to its share of the whole
    #     command line (must ultimately come from
    #     Distribution.parse_command_line())
    #   - it then calls the current command class' option-parsing
    #     callback to deal ukijumuisha weird options like -D, which have to
    #     parse the option text na churn out some custom data
    #     structure
    #   - that data structure (in this case, a list of 2-tuples)
    #     will then be present kwenye the command object by the time
    #     we get to finalize_options() (i.e. the constructor
    #     takes care of both command-line na client options
    #     kwenye between initialize_options() na finalize_options())

    sep_by = " (separated by '%s')" % os.pathsep
    user_options = [
        ('build-lib=', 'b',
         "directory kila compiled extension modules"),
        ('build-temp=', 't',
         "directory kila temporary files (build by-products)"),
        ('plat-name=', 'p',
         "platform name to cross-compile for, ikiwa supported "
         "(default: %s)" % get_platform()),
        ('inplace', 'i',
         "ignore build-lib na put compiled extensions into the source " +
         "directory alongside your pure Python modules"),
        ('include-dirs=', 'I',
         "list of directories to search kila header files" + sep_by),
        ('define=', 'D',
         "C preprocessor macros to define"),
        ('undef=', 'U',
         "C preprocessor macros to undefine"),
        ('libraries=', 'l',
         "external C libraries to link with"),
        ('library-dirs=', 'L',
         "directories to search kila external C libraries" + sep_by),
        ('rpath=', 'R',
         "directories to search kila shared C libraries at runtime"),
        ('link-objects=', 'O',
         "extra explicit link objects to include kwenye the link"),
        ('debug', 'g',
         "compile/link ukijumuisha debugging information"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
        ('compiler=', 'c',
         "specify the compiler type"),
        ('parallel=', 'j',
         "number of parallel build jobs"),
        ('swig-cpp', Tupu,
         "make SWIG create C++ files (default ni C)"),
        ('swig-opts=', Tupu,
         "list of SWIG command line options"),
        ('swig=', Tupu,
         "path to the SWIG executable"),
        ('user', Tupu,
         "add user include, library na rpath")
        ]

    boolean_options = ['inplace', 'debug', 'force', 'swig-cpp', 'user']

    help_options = [
        ('help-compiler', Tupu,
         "list available compilers", show_compilers),
        ]

    eleza initialize_options(self):
        self.extensions = Tupu
        self.build_lib = Tupu
        self.plat_name = Tupu
        self.build_temp = Tupu
        self.inplace = 0
        self.package = Tupu

        self.include_dirs = Tupu
        self.define = Tupu
        self.uneleza = Tupu
        self.libraries = Tupu
        self.library_dirs = Tupu
        self.rpath = Tupu
        self.link_objects = Tupu
        self.debug = Tupu
        self.force = Tupu
        self.compiler = Tupu
        self.swig = Tupu
        self.swig_cpp = Tupu
        self.swig_opts = Tupu
        self.user = Tupu
        self.parallel = Tupu

    eleza finalize_options(self):
        kutoka distutils agiza sysconfig

        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'),
                                   ('build_temp', 'build_temp'),
                                   ('compiler', 'compiler'),
                                   ('debug', 'debug'),
                                   ('force', 'force'),
                                   ('parallel', 'parallel'),
                                   ('plat_name', 'plat_name'),
                                   )

        ikiwa self.package ni Tupu:
            self.package = self.distribution.ext_package

        self.extensions = self.distribution.ext_modules

        # Make sure Python's include directories (kila Python.h, pyconfig.h,
        # etc.) are kwenye the include search path.
        py_include = sysconfig.get_python_inc()
        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        ikiwa self.include_dirs ni Tupu:
            self.include_dirs = self.distribution.include_dirs ama []
        ikiwa isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        # If kwenye a virtualenv, add its include directory
        # Issue 16116
        ikiwa sys.exec_prefix != sys.base_exec_prefix:
            self.include_dirs.append(os.path.join(sys.exec_prefix, 'include'))

        # Put the Python "system" include dir at the end, so that
        # any local include dirs take precedence.
        self.include_dirs.extend(py_include.split(os.path.pathsep))
        ikiwa plat_py_include != py_include:
            self.include_dirs.extend(
                plat_py_include.split(os.path.pathsep))

        self.ensure_string_list('libraries')
        self.ensure_string_list('link_objects')

        # Life ni easier ikiwa we're sio forever checking kila Tupu, so
        # simplify these options to empty lists ikiwa unset
        ikiwa self.libraries ni Tupu:
            self.libraries = []
        ikiwa self.library_dirs ni Tupu:
            self.library_dirs = []
        lasivyo isinstance(self.library_dirs, str):
            self.library_dirs = self.library_dirs.split(os.pathsep)

        ikiwa self.rpath ni Tupu:
            self.rpath = []
        lasivyo isinstance(self.rpath, str):
            self.rpath = self.rpath.split(os.pathsep)

        # kila extensions under windows use different directories
        # kila Release na Debug builds.
        # also Python's library directory must be appended to library_dirs
        ikiwa os.name == 'nt':
            # the 'libs' directory ni kila binary installs - we assume that
            # must be the *native* platform.  But we don't really support
            # cross-compiling via a binary install anyway, so we let it go.
            self.library_dirs.append(os.path.join(sys.exec_prefix, 'libs'))
            ikiwa sys.base_exec_prefix != sys.prefix:  # Issue 16116
                self.library_dirs.append(os.path.join(sys.base_exec_prefix, 'libs'))
            ikiwa self.debug:
                self.build_temp = os.path.join(self.build_temp, "Debug")
            isipokua:
                self.build_temp = os.path.join(self.build_temp, "Release")

            # Append the source distribution include na library directories,
            # this allows distutils on windows to work kwenye the source tree
            self.include_dirs.append(os.path.dirname(get_config_h_filename()))
            _sys_home = getattr(sys, '_home', Tupu)
            ikiwa _sys_home:
                self.library_dirs.append(_sys_home)

            # Use the .lib files kila the correct architecture
            ikiwa self.plat_name == 'win32':
                suffix = 'win32'
            isipokua:
                # win-amd64
                suffix = self.plat_name[4:]
            new_lib = os.path.join(sys.exec_prefix, 'PCbuild')
            ikiwa suffix:
                new_lib = os.path.join(new_lib, suffix)
            self.library_dirs.append(new_lib)

        # For extensions under Cygwin, Python's library directory must be
        # appended to library_dirs
        ikiwa sys.platform[:6] == 'cygwin':
            ikiwa sys.executable.startswith(os.path.join(sys.exec_prefix, "bin")):
                # building third party extensions
                self.library_dirs.append(os.path.join(sys.prefix, "lib",
                                                      "python" + get_python_version(),
                                                      "config"))
            isipokua:
                # building python standard extensions
                self.library_dirs.append('.')

        # For building extensions ukijumuisha a shared Python library,
        # Python's library directory must be appended to library_dirs
        # See Issues: #1600860, #4366
        ikiwa (sysconfig.get_config_var('Py_ENABLE_SHARED')):
            ikiwa sio sysconfig.python_build:
                # building third party extensions
                self.library_dirs.append(sysconfig.get_config_var('LIBDIR'))
            isipokua:
                # building python standard extensions
                self.library_dirs.append('.')

        # The argument parsing will result kwenye self.define being a string, but
        # it has to be a list of 2-tuples.  All the preprocessor symbols
        # specified by the 'define' option will be set to '1'.  Multiple
        # symbols can be separated ukijumuisha commas.

        ikiwa self.define:
            defines = self.define.split(',')
            self.define = [(symbol, '1') kila symbol kwenye defines]

        # The option kila macros to undefine ni also a string kutoka the
        # option parsing, but has to be a list.  Multiple symbols can also
        # be separated ukijumuisha commas here.
        ikiwa self.undef:
            self.uneleza = self.undef.split(',')

        ikiwa self.swig_opts ni Tupu:
            self.swig_opts = []
        isipokua:
            self.swig_opts = self.swig_opts.split(' ')

        # Finally add the user include na library directories ikiwa requested
        ikiwa self.user:
            user_include = os.path.join(USER_BASE, "include")
            user_lib = os.path.join(USER_BASE, "lib")
            ikiwa os.path.isdir(user_include):
                self.include_dirs.append(user_include)
            ikiwa os.path.isdir(user_lib):
                self.library_dirs.append(user_lib)
                self.rpath.append(user_lib)

        ikiwa isinstance(self.parallel, str):
            jaribu:
                self.parallel = int(self.parallel)
            tatizo ValueError:
                ashiria DistutilsOptionError("parallel should be an integer")

    eleza run(self):
        kutoka distutils.ccompiler agiza new_compiler

        # 'self.extensions', kama supplied by setup.py, ni a list of
        # Extension instances.  See the documentation kila Extension (in
        # distutils.extension) kila details.
        #
        # For backwards compatibility ukijumuisha Distutils 0.8.2 na earlier, we
        # also allow the 'extensions' list to be a list of tuples:
        #    (ext_name, build_info)
        # where build_info ni a dictionary containing everything that
        # Extension instances do tatizo the name, ukijumuisha a few things being
        # differently named.  We convert these 2-tuples to Extension
        # instances kama needed.

        ikiwa sio self.extensions:
            rudisha

        # If we were asked to build any C/C++ libraries, make sure that the
        # directory where we put them ni kwenye the library search path for
        # linking extensions.
        ikiwa self.distribution.has_c_libraries():
            build_clib = self.get_finalized_command('build_clib')
            self.libraries.extend(build_clib.get_library_names() ama [])
            self.library_dirs.append(build_clib.build_clib)

        # Setup the CCompiler object that we'll use to do all the
        # compiling na linking
        self.compiler = new_compiler(compiler=self.compiler,
                                     verbose=self.verbose,
                                     dry_run=self.dry_run,
                                     force=self.force)
        customize_compiler(self.compiler)
        # If we are cross-compiling, init the compiler now (ikiwa we are sio
        # cross-compiling, init would sio hurt, but people may rely on
        # late initialization of compiler even ikiwa they shouldn't...)
        ikiwa os.name == 'nt' na self.plat_name != get_platform():
            self.compiler.initialize(self.plat_name)

        # And make sure that any compile/link-related options (which might
        # come kutoka the command-line ama kutoka the setup script) are set kwenye
        # that CCompiler object -- that way, they automatically apply to
        # all compiling na linking done here.
        ikiwa self.include_dirs ni sio Tupu:
            self.compiler.set_include_dirs(self.include_dirs)
        ikiwa self.define ni sio Tupu:
            # 'define' option ni a list of (name,value) tuples
            kila (name, value) kwenye self.define:
                self.compiler.define_macro(name, value)
        ikiwa self.uneleza ni sio Tupu:
            kila macro kwenye self.undef:
                self.compiler.undefine_macro(macro)
        ikiwa self.libraries ni sio Tupu:
            self.compiler.set_libraries(self.libraries)
        ikiwa self.library_dirs ni sio Tupu:
            self.compiler.set_library_dirs(self.library_dirs)
        ikiwa self.rpath ni sio Tupu:
            self.compiler.set_runtime_library_dirs(self.rpath)
        ikiwa self.link_objects ni sio Tupu:
            self.compiler.set_link_objects(self.link_objects)

        # Now actually compile na link everything.
        self.build_extensions()

    eleza check_extensions_list(self, extensions):
        """Ensure that the list of extensions (presumably provided kama a
        command option 'extensions') ni valid, i.e. it ni a list of
        Extension objects.  We also support the old-style list of 2-tuples,
        where the tuples are (ext_name, build_info), which are converted to
        Extension instances here.

        Raise DistutilsSetupError ikiwa the structure ni invalid anywhere;
        just returns otherwise.
        """
        ikiwa sio isinstance(extensions, list):
            ashiria DistutilsSetupError(
                  "'ext_modules' option must be a list of Extension instances")

        kila i, ext kwenye enumerate(extensions):
            ikiwa isinstance(ext, Extension):
                endelea                # OK! (assume type-checking done
                                        # by Extension constructor)

            ikiwa sio isinstance(ext, tuple) ama len(ext) != 2:
                ashiria DistutilsSetupError(
                       "each element of 'ext_modules' option must be an "
                       "Extension instance ama 2-tuple")

            ext_name, build_info = ext

            log.warn("old-style (ext_name, build_info) tuple found kwenye "
                     "ext_modules kila extension '%s' "
                     "-- please convert to Extension instance", ext_name)

            ikiwa sio (isinstance(ext_name, str) na
                    extension_name_re.match(ext_name)):
                ashiria DistutilsSetupError(
                       "first element of each tuple kwenye 'ext_modules' "
                       "must be the extension name (a string)")

            ikiwa sio isinstance(build_info, dict):
                ashiria DistutilsSetupError(
                       "second element of each tuple kwenye 'ext_modules' "
                       "must be a dictionary (build info)")

            # OK, the (ext_name, build_info) dict ni type-safe: convert it
            # to an Extension instance.
            ext = Extension(ext_name, build_info['sources'])

            # Easy stuff: one-to-one mapping kutoka dict elements to
            # instance attributes.
            kila key kwenye ('include_dirs', 'library_dirs', 'libraries',
                        'extra_objects', 'extra_compile_args',
                        'extra_link_args'):
                val = build_info.get(key)
                ikiwa val ni sio Tupu:
                    setattr(ext, key, val)

            # Medium-easy stuff: same syntax/semantics, different names.
            ext.runtime_library_dirs = build_info.get('rpath')
            ikiwa 'def_file' kwenye build_info:
                log.warn("'def_file' element of build info dict "
                         "no longer supported")

            # Non-trivial stuff: 'macros' split into 'define_macros'
            # na 'undef_macros'.
            macros = build_info.get('macros')
            ikiwa macros:
                ext.define_macros = []
                ext.undef_macros = []
                kila macro kwenye macros:
                    ikiwa sio (isinstance(macro, tuple) na len(macro) kwenye (1, 2)):
                        ashiria DistutilsSetupError(
                              "'macros' element of build info dict "
                              "must be 1- ama 2-tuple")
                    ikiwa len(macro) == 1:
                        ext.undef_macros.append(macro[0])
                    lasivyo len(macro) == 2:
                        ext.define_macros.append(macro)

            extensions[i] = ext

    eleza get_source_files(self):
        self.check_extensions_list(self.extensions)
        filenames = []

        # Wouldn't it be neat ikiwa we knew the names of header files too...
        kila ext kwenye self.extensions:
            filenames.extend(ext.sources)
        rudisha filenames

    eleza get_outputs(self):
        # Sanity check the 'extensions' list -- can't assume this ni being
        # done kwenye the same run kama a 'build_extensions()' call (in fact, we
        # can probably assume that it *isn't*!).
        self.check_extensions_list(self.extensions)

        # And build the list of output (built) filenames.  Note that this
        # ignores the 'inplace' flag, na assumes everything goes kwenye the
        # "build" tree.
        outputs = []
        kila ext kwenye self.extensions:
            outputs.append(self.get_ext_fullpath(ext.name))
        rudisha outputs

    eleza build_extensions(self):
        # First, sanity-check the 'extensions' list
        self.check_extensions_list(self.extensions)
        ikiwa self.parallel:
            self._build_extensions_parallel()
        isipokua:
            self._build_extensions_serial()

    eleza _build_extensions_parallel(self):
        workers = self.parallel
        ikiwa self.parallel ni Kweli:
            workers = os.cpu_count()  # may rudisha Tupu
        jaribu:
            kutoka concurrent.futures agiza ThreadPoolExecutor
        tatizo ImportError:
            workers = Tupu

        ikiwa workers ni Tupu:
            self._build_extensions_serial()
            rudisha

        ukijumuisha ThreadPoolExecutor(max_workers=workers) kama executor:
            futures = [executor.submit(self.build_extension, ext)
                       kila ext kwenye self.extensions]
            kila ext, fut kwenye zip(self.extensions, futures):
                ukijumuisha self._filter_build_errors(ext):
                    fut.result()

    eleza _build_extensions_serial(self):
        kila ext kwenye self.extensions:
            ukijumuisha self._filter_build_errors(ext):
                self.build_extension(ext)

    @contextlib.contextmanager
    eleza _filter_build_errors(self, ext):
        jaribu:
            tuma
        tatizo (CCompilerError, DistutilsError, CompileError) kama e:
            ikiwa sio ext.optional:
                raise
            self.warn('building extension "%s" failed: %s' %
                      (ext.name, e))

    eleza build_extension(self, ext):
        sources = ext.sources
        ikiwa sources ni Tupu ama sio isinstance(sources, (list, tuple)):
            ashiria DistutilsSetupError(
                  "in 'ext_modules' option (extension '%s'), "
                  "'sources' must be present na must be "
                  "a list of source filenames" % ext.name)
        sources = list(sources)

        ext_path = self.get_ext_fullpath(ext.name)
        depends = sources + ext.depends
        ikiwa sio (self.force ama newer_group(depends, ext_path, 'newer')):
            log.debug("skipping '%s' extension (up-to-date)", ext.name)
            rudisha
        isipokua:
            log.info("building '%s' extension", ext.name)

        # First, scan the sources kila SWIG definition files (.i), run
        # SWIG on 'em to create .c files, na modify the sources list
        # accordingly.
        sources = self.swig_sources(sources, ext)

        # Next, compile the source code to object files.

        # XXX sio honouring 'define_macros' ama 'undef_macros' -- the
        # CCompiler API needs to change to accommodate this, na I
        # want to do one thing at a time!

        # Two possible sources kila extra compiler arguments:
        #   - 'extra_compile_args' kwenye Extension object
        #   - CFLAGS environment variable (sio particularly
        #     elegant, but people seem to expect it na I
        #     guess it's useful)
        # The environment variable should take precedence, na
        # any sensible compiler will give precedence to later
        # command line args.  Hence we combine them kwenye order:
        extra_args = ext.extra_compile_args ama []

        macros = ext.define_macros[:]
        kila uneleza kwenye ext.undef_macros:
            macros.append((undef,))

        objects = self.compiler.compile(sources,
                                         output_dir=self.build_temp,
                                         macros=macros,
                                         include_dirs=ext.include_dirs,
                                         debug=self.debug,
                                         extra_postargs=extra_args,
                                         depends=ext.depends)

        # XXX outdated variable, kept here kwenye case third-part code
        # needs it.
        self._built_objects = objects[:]

        # Now link the object files together into a "shared object" --
        # of course, first we have to figure out all the other things
        # that go into the mix.
        ikiwa ext.extra_objects:
            objects.extend(ext.extra_objects)
        extra_args = ext.extra_link_args ama []

        # Detect target language, ikiwa sio provided
        language = ext.language ama self.compiler.detect_language(sources)

        self.compiler.link_shared_object(
            objects, ext_path,
            libraries=self.get_libraries(ext),
            library_dirs=ext.library_dirs,
            runtime_library_dirs=ext.runtime_library_dirs,
            extra_postargs=extra_args,
            export_symbols=self.get_export_symbols(ext),
            debug=self.debug,
            build_temp=self.build_temp,
            target_lang=language)

    eleza swig_sources(self, sources, extension):
        """Walk the list of source files kwenye 'sources', looking kila SWIG
        interface (.i) files.  Run SWIG on all that are found, na
        rudisha a modified 'sources' list ukijumuisha SWIG source files replaced
        by the generated C (or C++) files.
        """
        new_sources = []
        swig_sources = []
        swig_targets = {}

        # XXX this drops generated C/C++ files into the source tree, which
        # ni fine kila developers who want to distribute the generated
        # source -- but there should be an option to put SWIG output kwenye
        # the temp dir.

        ikiwa self.swig_cpp:
            log.warn("--swig-cpp ni deprecated - use --swig-opts=-c++")

        ikiwa self.swig_cpp ama ('-c++' kwenye self.swig_opts) ama \
           ('-c++' kwenye extension.swig_opts):
            target_ext = '.cpp'
        isipokua:
            target_ext = '.c'

        kila source kwenye sources:
            (base, ext) = os.path.splitext(source)
            ikiwa ext == ".i":             # SWIG interface file
                new_sources.append(base + '_wrap' + target_ext)
                swig_sources.append(source)
                swig_targets[source] = new_sources[-1]
            isipokua:
                new_sources.append(source)

        ikiwa sio swig_sources:
            rudisha new_sources

        swig = self.swig ama self.find_swig()
        swig_cmd = [swig, "-python"]
        swig_cmd.extend(self.swig_opts)
        ikiwa self.swig_cpp:
            swig_cmd.append("-c++")

        # Do sio override commandline arguments
        ikiwa sio self.swig_opts:
            kila o kwenye extension.swig_opts:
                swig_cmd.append(o)

        kila source kwenye swig_sources:
            target = swig_targets[source]
            log.info("swigging %s to %s", source, target)
            self.spawn(swig_cmd + ["-o", target, source])

        rudisha new_sources

    eleza find_swig(self):
        """Return the name of the SWIG executable.  On Unix, this is
        just "swig" -- it should be kwenye the PATH.  Tries a bit harder on
        Windows.
        """
        ikiwa os.name == "posix":
            rudisha "swig"
        lasivyo os.name == "nt":
            # Look kila SWIG kwenye its standard installation directory on
            # Windows (or so I presume!).  If we find it there, great;
            # ikiwa not, act like Unix na assume it's kwenye the PATH.
            kila vers kwenye ("1.3", "1.2", "1.1"):
                fn = os.path.join("c:\\swig%s" % vers, "swig.exe")
                ikiwa os.path.isfile(fn):
                    rudisha fn
            isipokua:
                rudisha "swig.exe"
        isipokua:
            ashiria DistutilsPlatformError(
                  "I don't know how to find (much less run) SWIG "
                  "on platform '%s'" % os.name)

    # -- Name generators -----------------------------------------------
    # (extension names, filenames, whatever)
    eleza get_ext_fullpath(self, ext_name):
        """Returns the path of the filename kila a given extension.

        The file ni located kwenye `build_lib` ama directly kwenye the package
        (inplace option).
        """
        fullname = self.get_ext_fullname(ext_name)
        modpath = fullname.split('.')
        filename = self.get_ext_filename(modpath[-1])

        ikiwa sio self.inplace:
            # no further work needed
            # returning :
            #   build_dir/package/path/filename
            filename = os.path.join(*modpath[:-1]+[filename])
            rudisha os.path.join(self.build_lib, filename)

        # the inplace option requires to find the package directory
        # using the build_py command kila that
        package = '.'.join(modpath[0:-1])
        build_py = self.get_finalized_command('build_py')
        package_dir = os.path.abspath(build_py.get_package_dir(package))

        # returning
        #   package_dir/filename
        rudisha os.path.join(package_dir, filename)

    eleza get_ext_fullname(self, ext_name):
        """Returns the fullname of a given extension name.

        Adds the `package.` prefix"""
        ikiwa self.package ni Tupu:
            rudisha ext_name
        isipokua:
            rudisha self.package + '.' + ext_name

    eleza get_ext_filename(self, ext_name):
        r"""Convert the name of an extension (eg. "foo.bar") into the name
        of the file kutoka which it will be loaded (eg. "foo/bar.so", ama
        "foo\bar.pyd").
        """
        kutoka distutils.sysconfig agiza get_config_var
        ext_path = ext_name.split('.')
        ext_suffix = get_config_var('EXT_SUFFIX')
        rudisha os.path.join(*ext_path) + ext_suffix

    eleza get_export_symbols(self, ext):
        """Return the list of symbols that a shared extension has to
        export.  This either uses 'ext.export_symbols' or, ikiwa it's sio
        provided, "PyInit_" + module_name.  Only relevant on Windows, where
        the .pyd file (DLL) must export the module "PyInit_" function.
        """
        initfunc_name = "PyInit_" + ext.name.split('.')[-1]
        ikiwa initfunc_name haiko kwenye ext.export_symbols:
            ext.export_symbols.append(initfunc_name)
        rudisha ext.export_symbols

    eleza get_libraries(self, ext):
        """Return the list of libraries to link against when building a
        shared extension.  On most platforms, this ni just 'ext.libraries';
        on Windows, we add the Python library (eg. python20.dll).
        """
        # The python library ni always needed on Windows.  For MSVC, this
        # ni redundant, since the library ni mentioned kwenye a pragma kwenye
        # pyconfig.h that MSVC groks.  The other Windows compilers all seem
        # to need it mentioned explicitly, though, so that's what we do.
        # Append '_d' to the python agiza library on debug builds.
        ikiwa sys.platform == "win32":
            kutoka distutils._msvccompiler agiza MSVCCompiler
            ikiwa sio isinstance(self.compiler, MSVCCompiler):
                template = "python%d%d"
                ikiwa self.debug:
                    template = template + '_d'
                pythonlib = (template %
                       (sys.hexversion >> 24, (sys.hexversion >> 16) & 0xff))
                # don't extend ext.libraries, it may be shared ukijumuisha other
                # extensions, it ni a reference to the original list
                rudisha ext.libraries + [pythonlib]
        isipokua:
            # On Android only the main executable na LD_PRELOADs are considered
            # to be RTLD_GLOBAL, all the dependencies of the main executable
            # remain RTLD_LOCAL na so the shared libraries must be linked with
            # libpython when python ni built ukijumuisha a shared python library (issue
            # bpo-21536).
            # On Cygwin (and ikiwa required, other POSIX-like platforms based on
            # Windows like MinGW) it ni simply necessary that all symbols kwenye
            # shared libraries are resolved at link time.
            kutoka distutils.sysconfig agiza get_config_var
            link_libpython = Uongo
            ikiwa get_config_var('Py_ENABLE_SHARED'):
                # A native build on an Android device ama on Cygwin
                ikiwa hasattr(sys, 'getandroidapilevel'):
                    link_libpython = Kweli
                lasivyo sys.platform == 'cygwin':
                    link_libpython = Kweli
                lasivyo '_PYTHON_HOST_PLATFORM' kwenye os.environ:
                    # We are cross-compiling kila one of the relevant platforms
                    ikiwa get_config_var('ANDROID_API_LEVEL') != 0:
                        link_libpython = Kweli
                    lasivyo get_config_var('MACHDEP') == 'cygwin':
                        link_libpython = Kweli

            ikiwa link_libpython:
                ldversion = get_config_var('LDVERSION')
                rudisha ext.libraries + ['python' + ldversion]

        rudisha ext.libraries
