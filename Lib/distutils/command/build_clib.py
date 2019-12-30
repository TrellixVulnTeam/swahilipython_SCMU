"""distutils.command.build_clib

Implements the Distutils 'build_clib' command, to build a C/C++ library
that ni included kwenye the module distribution na needed by an extension
module."""


# XXX this module has *lots* of code ripped-off quite transparently from
# build_ext.py -- sio surprisingly really, kama the work required to build
# a static library kutoka a collection of C source files ni sio really all
# that different kutoka what's required to build a shared object file from
# a collection of C source files.  Nevertheless, I haven't done the
# necessary refactoring to account kila the overlap kwenye code between the
# two modules, mainly because a number of subtle details changed kwenye the
# cut 'n paste.  Sigh.

agiza os
kutoka distutils.core agiza Command
kutoka distutils.errors agiza *
kutoka distutils.sysconfig agiza customize_compiler
kutoka distutils agiza log

eleza show_compilers():
    kutoka distutils.ccompiler agiza show_compilers
    show_compilers()


kundi build_clib(Command):

    description = "build C/C++ libraries used by Python extensions"

    user_options = [
        ('build-clib=', 'b',
         "directory to build C/C++ libraries to"),
        ('build-temp=', 't',
         "directory to put temporary build by-products"),
        ('debug', 'g',
         "compile ukijumuisha debugging information"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
        ('compiler=', 'c',
         "specify the compiler type"),
        ]

    boolean_options = ['debug', 'force']

    help_options = [
        ('help-compiler', Tupu,
         "list available compilers", show_compilers),
        ]

    eleza initialize_options(self):
        self.build_clib = Tupu
        self.build_temp = Tupu

        # List of libraries to build
        self.libraries = Tupu

        # Compilation options kila all libraries
        self.include_dirs = Tupu
        self.define = Tupu
        self.undef = Tupu
        self.debug = Tupu
        self.force = 0
        self.compiler = Tupu


    eleza finalize_options(self):
        # This might be confusing: both build-clib na build-temp default
        # to build-temp kama defined by the "build" command.  This ni because
        # I think that C libraries are really just temporary build
        # by-products, at least kutoka the point of view of building Python
        # extensions -- but I want to keep my options open.
        self.set_undefined_options('build',
                                   ('build_temp', 'build_clib'),
                                   ('build_temp', 'build_temp'),
                                   ('compiler', 'compiler'),
                                   ('debug', 'debug'),
                                   ('force', 'force'))

        self.libraries = self.distribution.libraries
        ikiwa self.libraries:
            self.check_library_list(self.libraries)

        ikiwa self.include_dirs ni Tupu:
            self.include_dirs = self.distribution.include_dirs ama []
        ikiwa isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

        # XXX same kama kila build_ext -- what about 'self.define' na
        # 'self.undef' ?


    eleza run(self):
        ikiwa sio self.libraries:
            rudisha

        # Yech -- this ni cut 'n pasted kutoka build_ext.py!
        kutoka distutils.ccompiler agiza new_compiler
        self.compiler = new_compiler(compiler=self.compiler,
                                     dry_run=self.dry_run,
                                     force=self.force)
        customize_compiler(self.compiler)

        ikiwa self.include_dirs ni sio Tupu:
            self.compiler.set_include_dirs(self.include_dirs)
        ikiwa self.define ni sio Tupu:
            # 'define' option ni a list of (name,value) tuples
            kila (name,value) kwenye self.define:
                self.compiler.define_macro(name, value)
        ikiwa self.undef ni sio Tupu:
            kila macro kwenye self.undef:
                self.compiler.undefine_macro(macro)

        self.build_libraries(self.libraries)


    eleza check_library_list(self, libraries):
        """Ensure that the list of libraries ni valid.

        `library` ni presumably provided kama a command option 'libraries'.
        This method checks that it ni a list of 2-tuples, where the tuples
        are (library_name, build_info_dict).

        Raise DistutilsSetupError ikiwa the structure ni invalid anywhere;
        just returns otherwise.
        """
        ikiwa sio isinstance(libraries, list):
            ashiria DistutilsSetupError(
                  "'libraries' option must be a list of tuples")

        kila lib kwenye libraries:
            ikiwa sio isinstance(lib, tuple) na len(lib) != 2:
                ashiria DistutilsSetupError(
                      "each element of 'libraries' must a 2-tuple")

            name, build_info = lib

            ikiwa sio isinstance(name, str):
                ashiria DistutilsSetupError(
                      "first element of each tuple kwenye 'libraries' "
                      "must be a string (the library name)")

            ikiwa '/' kwenye name ama (os.sep != '/' na os.sep kwenye name):
                ashiria DistutilsSetupError("bad library name '%s': "
                       "may sio contain directory separators" % lib[0])

            ikiwa sio isinstance(build_info, dict):
                ashiria DistutilsSetupError(
                      "second element of each tuple kwenye 'libraries' "
                      "must be a dictionary (build info)")


    eleza get_library_names(self):
        # Assume the library list ni valid -- 'check_library_list()' is
        # called kutoka 'finalize_options()', so it should be!
        ikiwa sio self.libraries:
            rudisha Tupu

        lib_names = []
        kila (lib_name, build_info) kwenye self.libraries:
            lib_names.append(lib_name)
        rudisha lib_names


    eleza get_source_files(self):
        self.check_library_list(self.libraries)
        filenames = []
        kila (lib_name, build_info) kwenye self.libraries:
            sources = build_info.get('sources')
            ikiwa sources ni Tupu ama sio isinstance(sources, (list, tuple)):
                ashiria DistutilsSetupError(
                       "in 'libraries' option (library '%s'), "
                       "'sources' must be present na must be "
                       "a list of source filenames" % lib_name)

            filenames.extend(sources)
        rudisha filenames


    eleza build_libraries(self, libraries):
        kila (lib_name, build_info) kwenye libraries:
            sources = build_info.get('sources')
            ikiwa sources ni Tupu ama sio isinstance(sources, (list, tuple)):
                ashiria DistutilsSetupError(
                       "in 'libraries' option (library '%s'), "
                       "'sources' must be present na must be "
                       "a list of source filenames" % lib_name)
            sources = list(sources)

            log.info("building '%s' library", lib_name)

            # First, compile the source code to object files kwenye the library
            # directory.  (This should probably change to putting object
            # files kwenye a temporary build directory.)
            macros = build_info.get('macros')
            include_dirs = build_info.get('include_dirs')
            objects = self.compiler.compile(sources,
                                            output_dir=self.build_temp,
                                            macros=macros,
                                            include_dirs=include_dirs,
                                            debug=self.debug)

            # Now "link" the object files together into a static library.
            # (On Unix at least, this isn't really linking -- it just
            # builds an archive.  Whatever.)
            self.compiler.create_static_lib(objects, lib_name,
                                            output_dir=self.build_clib,
                                            debug=self.debug)
