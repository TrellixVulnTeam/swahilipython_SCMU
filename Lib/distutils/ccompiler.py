"""distutils.ccompiler

Contains CCompiler, an abstract base kundi that defines the interface
kila the Distutils compiler abstraction model."""

agiza sys, os, re
kutoka distutils.errors agiza *
kutoka distutils.spawn agiza spawn
kutoka distutils.file_util agiza move_file
kutoka distutils.dir_util agiza mkpath
kutoka distutils.dep_util agiza newer_pairwise, newer_group
kutoka distutils.util agiza split_quoted, execute
kutoka distutils agiza log

kundi CCompiler:
    """Abstract base kundi to define the interface that must be implemented
    by real compiler classes.  Also has some utility methods used by
    several compiler classes.

    The basic idea behind a compiler abstraction kundi ni that each
    instance can be used kila all the compile/link steps kwenye building a
    single project.  Thus, attributes common to all of those compile na
    link steps -- include directories, macros to define, libraries to link
    against, etc. -- are attributes of the compiler instance.  To allow for
    variability kwenye how individual files are treated, most of those
    attributes may be varied on a per-compilation ama per-link basis.
    """

    # 'compiler_type' ni a kundi attribute that identifies this class.  It
    # keeps code that wants to know what kind of compiler it's dealing with
    # kutoka having to agiza all possible compiler classes just to do an
    # 'isinstance'.  In concrete CCompiler subclasses, 'compiler_type'
    # should really, really be one of the keys of the 'compiler_class'
    # dictionary (see below -- used by the 'new_compiler()' factory
    # function) -- authors of new compiler interface classes are
    # responsible kila updating 'compiler_class'!
    compiler_type = Tupu

    # XXX things sio handled by this compiler abstraction model:
    #   * client can't provide additional options kila a compiler,
    #     e.g. warning, optimization, debugging flags.  Perhaps this
    #     should be the domain of concrete compiler abstraction classes
    #     (UnixCCompiler, MSVCCompiler, etc.) -- ama perhaps the base
    #     kundi should have methods kila the common ones.
    #   * can't completely override the include ama library searchg
    #     path, ie. no "cc -I -Idir1 -Idir2" ama "cc -L -Ldir1 -Ldir2".
    #     I'm sio sure how widely supported this ni even by Unix
    #     compilers, much less on other platforms.  And I'm even less
    #     sure how useful it is; maybe kila cross-compiling, but
    #     support kila that ni a ways off.  (And anyways, cross
    #     compilers probably have a dedicated binary ukijumuisha the
    #     right paths compiled in.  I hope.)
    #   * can't do really freaky things ukijumuisha the library list/library
    #     dirs, e.g. "-Ldir1 -lfoo -Ldir2 -lfoo" to link against
    #     different versions of libfoo.a kwenye different locations.  I
    #     think this ni useless without the ability to null out the
    #     library search path anyways.


    # Subclasses that rely on the standard filename generation methods
    # implemented below should override these; see the comment near
    # those methods ('object_filenames()' et. al.) kila details:
    src_extensions = Tupu               # list of strings
    obj_extension = Tupu                # string
    static_lib_extension = Tupu
    shared_lib_extension = Tupu         # string
    static_lib_format = Tupu            # format string
    shared_lib_format = Tupu            # prob. same kama static_lib_format
    exe_extension = Tupu                # string

    # Default language settings. language_map ni used to detect a source
    # file ama Extension target language, checking source filenames.
    # language_order ni used to detect the language precedence, when deciding
    # what language to use when mixing source types. For example, ikiwa some
    # extension has two files ukijumuisha ".c" extension, na one ukijumuisha ".cpp", it
    # ni still linked kama c++.
    language_map = {".c"   : "c",
                    ".cc"  : "c++",
                    ".cpp" : "c++",
                    ".cxx" : "c++",
                    ".m"   : "objc",
                   }
    language_order = ["c++", "objc", "c"]

    eleza __init__(self, verbose=0, dry_run=0, force=0):
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose

        # 'output_dir': a common output directory kila object, library,
        # shared object, na shared library files
        self.output_dir = Tupu

        # 'macros': a list of macro definitions (or undefinitions).  A
        # macro definition ni a 2-tuple (name, value), where the value is
        # either a string ama Tupu (no explicit value).  A macro
        # undefinition ni a 1-tuple (name,).
        self.macros = []

        # 'include_dirs': a list of directories to search kila include files
        self.include_dirs = []

        # 'libraries': a list of libraries to include kwenye any link
        # (library names, sio filenames: eg. "foo" sio "libfoo.a")
        self.libraries = []

        # 'library_dirs': a list of directories to search kila libraries
        self.library_dirs = []

        # 'runtime_library_dirs': a list of directories to search for
        # shared libraries/objects at runtime
        self.runtime_library_dirs = []

        # 'objects': a list of object files (or similar, such kama explicitly
        # named library files) to include on any link
        self.objects = []

        kila key kwenye self.executables.keys():
            self.set_executable(key, self.executables[key])

    eleza set_executables(self, **kwargs):
        """Define the executables (and options kila them) that will be run
        to perform the various stages of compilation.  The exact set of
        executables that may be specified here depends on the compiler
        kundi (via the 'executables' kundi attribute), but most will have:
          compiler      the C/C++ compiler
          linker_so     linker used to create shared objects na libraries
          linker_exe    linker used to create binary executables
          archiver      static library creator

        On platforms ukijumuisha a command-line (Unix, DOS/Windows), each of these
        ni a string that will be split into executable name na (optional)
        list of arguments.  (Splitting the string ni done similarly to how
        Unix shells operate: words are delimited by spaces, but quotes na
        backslashes can override this.  See
        'distutils.util.split_quoted()'.)
        """

        # Note that some CCompiler implementation classes will define class
        # attributes 'cpp', 'cc', etc. ukijumuisha hard-coded executable names;
        # this ni appropriate when a compiler kundi ni kila exactly one
        # compiler/OS combination (eg. MSVCCompiler).  Other compiler
        # classes (UnixCCompiler, kwenye particular) are driven by information
        # discovered at run-time, since there are many different ways to do
        # basically the same things ukijumuisha Unix C compilers.

        kila key kwenye kwargs:
            ikiwa key haiko kwenye self.executables:
                ashiria ValueError("unknown executable '%s' kila kundi %s" %
                      (key, self.__class__.__name__))
            self.set_executable(key, kwargs[key])

    eleza set_executable(self, key, value):
        ikiwa isinstance(value, str):
            setattr(self, key, split_quoted(value))
        isipokua:
            setattr(self, key, value)

    eleza _find_macro(self, name):
        i = 0
        kila defn kwenye self.macros:
            ikiwa defn[0] == name:
                rudisha i
            i += 1
        rudisha Tupu

    eleza _check_macro_definitions(self, definitions):
        """Ensures that every element of 'definitions' ni a valid macro
        definition, ie. either (name,value) 2-tuple ama a (name,) tuple.  Do
        nothing ikiwa all definitions are OK, ashiria TypeError otherwise.
        """
        kila defn kwenye definitions:
            ikiwa sio (isinstance(defn, tuple) na
                    (len(defn) kwenye (1, 2) na
                      (isinstance (defn[1], str) ama defn[1] ni Tupu)) na
                    isinstance (defn[0], str)):
                ashiria TypeError(("invalid macro definition '%s': " % defn) + \
                      "must be tuple (string,), (string, string), ama " + \
                      "(string, Tupu)")


    # -- Bookkeeping methods -------------------------------------------

    eleza define_macro(self, name, value=Tupu):
        """Define a preprocessor macro kila all compilations driven by this
        compiler object.  The optional parameter 'value' should be a
        string; ikiwa it ni sio supplied, then the macro will be defined
        without an explicit value na the exact outcome depends on the
        compiler used (XXX true? does ANSI say anything about this?)
        """
        # Delete kutoka the list of macro definitions/undefinitions if
        # already there (so that this one will take precedence).
        i = self._find_macro (name)
        ikiwa i ni sio Tupu:
            toa self.macros[i]

        self.macros.append((name, value))

    eleza undefine_macro(self, name):
        """Undefine a preprocessor macro kila all compilations driven by
        this compiler object.  If the same macro ni defined by
        'define_macro()' na undefined by 'undefine_macro()' the last call
        takes precedence (including multiple redefinitions ama
        undefinitions).  If the macro ni redefined/undefined on a
        per-compilation basis (ie. kwenye the call to 'compile()'), then that
        takes precedence.
        """
        # Delete kutoka the list of macro definitions/undefinitions if
        # already there (so that this one will take precedence).
        i = self._find_macro (name)
        ikiwa i ni sio Tupu:
            toa self.macros[i]

        undefn = (name,)
        self.macros.append(undefn)

    eleza add_include_dir(self, dir):
        """Add 'dir' to the list of directories that will be searched for
        header files.  The compiler ni instructed to search directories kwenye
        the order kwenye which they are supplied by successive calls to
        'add_include_dir()'.
        """
        self.include_dirs.append(dir)

    eleza set_include_dirs(self, dirs):
        """Set the list of directories that will be searched to 'dirs' (a
        list of strings).  Overrides any preceding calls to
        'add_include_dir()'; subsequence calls to 'add_include_dir()' add
        to the list pitaed to 'set_include_dirs()'.  This does sio affect
        any list of standard include directories that the compiler may
        search by default.
        """
        self.include_dirs = dirs[:]

    eleza add_library(self, libname):
        """Add 'libname' to the list of libraries that will be included kwenye
        all links driven by this compiler object.  Note that 'libname'
        should *not* be the name of a file containing a library, but the
        name of the library itself: the actual filename will be inferred by
        the linker, the compiler, ama the compiler kundi (depending on the
        platform).

        The linker will be instructed to link against libraries kwenye the
        order they were supplied to 'add_library()' and/or
        'set_libraries()'.  It ni perfectly valid to duplicate library
        names; the linker will be instructed to link against libraries as
        many times kama they are mentioned.
        """
        self.libraries.append(libname)

    eleza set_libraries(self, libnames):
        """Set the list of libraries to be included kwenye all links driven by
        this compiler object to 'libnames' (a list of strings).  This does
        sio affect any standard system libraries that the linker may
        include by default.
        """
        self.libraries = libnames[:]

    eleza add_library_dir(self, dir):
        """Add 'dir' to the list of directories that will be searched for
        libraries specified to 'add_library()' na 'set_libraries()'.  The
        linker will be instructed to search kila libraries kwenye the order they
        are supplied to 'add_library_dir()' and/or 'set_library_dirs()'.
        """
        self.library_dirs.append(dir)

    eleza set_library_dirs(self, dirs):
        """Set the list of library search directories to 'dirs' (a list of
        strings).  This does sio affect any standard library search path
        that the linker may search by default.
        """
        self.library_dirs = dirs[:]

    eleza add_runtime_library_dir(self, dir):
        """Add 'dir' to the list of directories that will be searched for
        shared libraries at runtime.
        """
        self.runtime_library_dirs.append(dir)

    eleza set_runtime_library_dirs(self, dirs):
        """Set the list of directories to search kila shared libraries at
        runtime to 'dirs' (a list of strings).  This does sio affect any
        standard search path that the runtime linker may search by
        default.
        """
        self.runtime_library_dirs = dirs[:]

    eleza add_link_object(self, object):
        """Add 'object' to the list of object files (or analogues, such as
        explicitly named library files ama the output of "resource
        compilers") to be included kwenye every link driven by this compiler
        object.
        """
        self.objects.append(object)

    eleza set_link_objects(self, objects):
        """Set the list of object files (or analogues) to be included kwenye
        every link to 'objects'.  This does sio affect any standard object
        files that the linker may include by default (such kama system
        libraries).
        """
        self.objects = objects[:]


    # -- Private utility methods --------------------------------------
    # (here kila the convenience of subclasses)

    # Helper method to prep compiler kwenye subkundi compile() methods

    eleza _setup_compile(self, outdir, macros, incdirs, sources, depends,
                       extra):
        """Process arguments na decide which source files to compile."""
        ikiwa outdir ni Tupu:
            outdir = self.output_dir
        lasivyo sio isinstance(outdir, str):
            ashiria TypeError("'output_dir' must be a string ama Tupu")

        ikiwa macros ni Tupu:
            macros = self.macros
        lasivyo isinstance(macros, list):
            macros = macros + (self.macros ama [])
        isipokua:
            ashiria TypeError("'macros' (ikiwa supplied) must be a list of tuples")

        ikiwa incdirs ni Tupu:
            incdirs = self.include_dirs
        lasivyo isinstance(incdirs, (list, tuple)):
            incdirs = list(incdirs) + (self.include_dirs ama [])
        isipokua:
            ashiria TypeError(
                  "'include_dirs' (ikiwa supplied) must be a list of strings")

        ikiwa extra ni Tupu:
            extra = []

        # Get the list of expected output (object) files
        objects = self.object_filenames(sources, strip_dir=0,
                                        output_dir=outdir)
        assert len(objects) == len(sources)

        pp_opts = gen_preprocess_options(macros, incdirs)

        build = {}
        kila i kwenye range(len(sources)):
            src = sources[i]
            obj = objects[i]
            ext = os.path.splitext(src)[1]
            self.mkpath(os.path.dirname(obj))
            build[obj] = (src, ext)

        rudisha macros, objects, extra, pp_opts, build

    eleza _get_cc_args(self, pp_opts, debug, before):
        # works kila unixccompiler, cygwinccompiler
        cc_args = pp_opts + ['-c']
        ikiwa debug:
            cc_args[:0] = ['-g']
        ikiwa before:
            cc_args[:0] = before
        rudisha cc_args

    eleza _fix_compile_args(self, output_dir, macros, include_dirs):
        """Typecheck na fix-up some of the arguments to the 'compile()'
        method, na rudisha fixed-up values.  Specifically: ikiwa 'output_dir'
        ni Tupu, replaces it ukijumuisha 'self.output_dir'; ensures that 'macros'
        ni a list, na augments it ukijumuisha 'self.macros'; ensures that
        'include_dirs' ni a list, na augments it ukijumuisha 'self.include_dirs'.
        Guarantees that the returned values are of the correct type,
        i.e. kila 'output_dir' either string ama Tupu, na kila 'macros' na
        'include_dirs' either list ama Tupu.
        """
        ikiwa output_dir ni Tupu:
            output_dir = self.output_dir
        lasivyo sio isinstance(output_dir, str):
            ashiria TypeError("'output_dir' must be a string ama Tupu")

        ikiwa macros ni Tupu:
            macros = self.macros
        lasivyo isinstance(macros, list):
            macros = macros + (self.macros ama [])
        isipokua:
            ashiria TypeError("'macros' (ikiwa supplied) must be a list of tuples")

        ikiwa include_dirs ni Tupu:
            include_dirs = self.include_dirs
        lasivyo isinstance(include_dirs, (list, tuple)):
            include_dirs = list(include_dirs) + (self.include_dirs ama [])
        isipokua:
            ashiria TypeError(
                  "'include_dirs' (ikiwa supplied) must be a list of strings")

        rudisha output_dir, macros, include_dirs

    eleza _prep_compile(self, sources, output_dir, depends=Tupu):
        """Decide which souce files must be recompiled.

        Determine the list of object files corresponding to 'sources',
        na figure out which ones really need to be recompiled.
        Return a list of all object files na a dictionary telling
        which source files can be skipped.
        """
        # Get the list of expected output (object) files
        objects = self.object_filenames(sources, output_dir=output_dir)
        assert len(objects) == len(sources)

        # Return an empty dict kila the "which source files can be skipped"
        # rudisha value to preserve API compatibility.
        rudisha objects, {}

    eleza _fix_object_args(self, objects, output_dir):
        """Typecheck na fix up some arguments supplied to various methods.
        Specifically: ensure that 'objects' ni a list; ikiwa output_dir is
        Tupu, replace ukijumuisha self.output_dir.  Return fixed versions of
        'objects' na 'output_dir'.
        """
        ikiwa sio isinstance(objects, (list, tuple)):
            ashiria TypeError("'objects' must be a list ama tuple of strings")
        objects = list(objects)

        ikiwa output_dir ni Tupu:
            output_dir = self.output_dir
        lasivyo sio isinstance(output_dir, str):
            ashiria TypeError("'output_dir' must be a string ama Tupu")

        rudisha (objects, output_dir)

    eleza _fix_lib_args(self, libraries, library_dirs, runtime_library_dirs):
        """Typecheck na fix up some of the arguments supplied to the
        'link_*' methods.  Specifically: ensure that all arguments are
        lists, na augment them ukijumuisha their permanent versions
        (eg. 'self.libraries' augments 'libraries').  Return a tuple with
        fixed versions of all arguments.
        """
        ikiwa libraries ni Tupu:
            libraries = self.libraries
        lasivyo isinstance(libraries, (list, tuple)):
            libraries = list (libraries) + (self.libraries ama [])
        isipokua:
            ashiria TypeError(
                  "'libraries' (ikiwa supplied) must be a list of strings")

        ikiwa library_dirs ni Tupu:
            library_dirs = self.library_dirs
        lasivyo isinstance(library_dirs, (list, tuple)):
            library_dirs = list (library_dirs) + (self.library_dirs ama [])
        isipokua:
            ashiria TypeError(
                  "'library_dirs' (ikiwa supplied) must be a list of strings")

        ikiwa runtime_library_dirs ni Tupu:
            runtime_library_dirs = self.runtime_library_dirs
        lasivyo isinstance(runtime_library_dirs, (list, tuple)):
            runtime_library_dirs = (list(runtime_library_dirs) +
                                    (self.runtime_library_dirs ama []))
        isipokua:
            ashiria TypeError("'runtime_library_dirs' (ikiwa supplied) "
                            "must be a list of strings")

        rudisha (libraries, library_dirs, runtime_library_dirs)

    eleza _need_link(self, objects, output_file):
        """Return true ikiwa we need to relink the files listed kwenye 'objects'
        to recreate 'output_file'.
        """
        ikiwa self.force:
            rudisha Kweli
        isipokua:
            ikiwa self.dry_run:
                newer = newer_group (objects, output_file, missing='newer')
            isipokua:
                newer = newer_group (objects, output_file)
            rudisha newer

    eleza detect_language(self, sources):
        """Detect the language of a given file, ama list of files. Uses
        language_map, na language_order to do the job.
        """
        ikiwa sio isinstance(sources, list):
            sources = [sources]
        lang = Tupu
        index = len(self.language_order)
        kila source kwenye sources:
            base, ext = os.path.splitext(source)
            extlang = self.language_map.get(ext)
            jaribu:
                extindex = self.language_order.index(extlang)
                ikiwa extindex < index:
                    lang = extlang
                    index = extindex
            tatizo ValueError:
                pita
        rudisha lang


    # -- Worker methods ------------------------------------------------
    # (must be implemented by subclasses)

    eleza preprocess(self, source, output_file=Tupu, macros=Tupu,
                   include_dirs=Tupu, extra_preargs=Tupu, extra_postargs=Tupu):
        """Preprocess a single C/C++ source file, named kwenye 'source'.
        Output will be written to file named 'output_file', ama stdout if
        'output_file' sio supplied.  'macros' ni a list of macro
        definitions kama kila 'compile()', which will augment the macros set
        ukijumuisha 'define_macro()' na 'undefine_macro()'.  'include_dirs' ni a
        list of directory names that will be added to the default list.

        Raises PreprocessError on failure.
        """
        pita

    eleza compile(self, sources, output_dir=Tupu, macros=Tupu,
                include_dirs=Tupu, debug=0, extra_preargs=Tupu,
                extra_postargs=Tupu, depends=Tupu):
        """Compile one ama more source files.

        'sources' must be a list of filenames, most likely C/C++
        files, but kwenye reality anything that can be handled by a
        particular compiler na compiler kundi (eg. MSVCCompiler can
        handle resource files kwenye 'sources').  Return a list of object
        filenames, one per source filename kwenye 'sources'.  Depending on
        the implementation, sio all source files will necessarily be
        compiled, but all corresponding object filenames will be
        returned.

        If 'output_dir' ni given, object files will be put under it, while
        retaining their original path component.  That is, "foo/bar.c"
        normally compiles to "foo/bar.o" (kila a Unix implementation); if
        'output_dir' ni "build", then it would compile to
        "build/foo/bar.o".

        'macros', ikiwa given, must be a list of macro definitions.  A macro
        definition ni either a (name, value) 2-tuple ama a (name,) 1-tuple.
        The former defines a macro; ikiwa the value ni Tupu, the macro is
        defined without an explicit value.  The 1-tuple case undefines a
        macro.  Later definitions/redefinitions/ undefinitions take
        precedence.

        'include_dirs', ikiwa given, must be a list of strings, the
        directories to add to the default include file search path kila this
        compilation only.

        'debug' ni a boolean; ikiwa true, the compiler will be instructed to
        output debug symbols kwenye (or alongside) the object file(s).

        'extra_preargs' na 'extra_postargs' are implementation- dependent.
        On platforms that have the notion of a command-line (e.g. Unix,
        DOS/Windows), they are most likely lists of strings: extra
        command-line arguments to prepend/append to the compiler command
        line.  On other platforms, consult the implementation class
        documentation.  In any event, they are intended kama an escape hatch
        kila those occasions when the abstract compiler framework doesn't
        cut the mustard.

        'depends', ikiwa given, ni a list of filenames that all targets
        depend on.  If a source file ni older than any file kwenye
        depends, then the source file will be recompiled.  This
        supports dependency tracking, but only at a coarse
        granularity.

        Raises CompileError on failure.
        """
        # A concrete compiler kundi can either override this method
        # entirely ama implement _compile().
        macros, objects, extra_postargs, pp_opts, build = \
                self._setup_compile(output_dir, macros, include_dirs, sources,
                                    depends, extra_postargs)
        cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)

        kila obj kwenye objects:
            jaribu:
                src, ext = build[obj]
            tatizo KeyError:
                endelea
            self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)

        # Return *all* object filenames, sio just the ones we just built.
        rudisha objects

    eleza _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        """Compile 'src' to product 'obj'."""
        # A concrete compiler kundi that does sio override compile()
        # should implement _compile().
        pita

    eleza create_static_lib(self, objects, output_libname, output_dir=Tupu,
                          debug=0, target_lang=Tupu):
        """Link a bunch of stuff together to create a static library file.
        The "bunch of stuff" consists of the list of object files supplied
        kama 'objects', the extra object files supplied to
        'add_link_object()' and/or 'set_link_objects()', the libraries
        supplied to 'add_library()' and/or 'set_libraries()', na the
        libraries supplied kama 'libraries' (ikiwa any).

        'output_libname' should be a library name, sio a filename; the
        filename will be inferred kutoka the library name.  'output_dir' is
        the directory where the library file will be put.

        'debug' ni a boolean; ikiwa true, debugging information will be
        included kwenye the library (note that on most platforms, it ni the
        compile step where this matters: the 'debug' flag ni included here
        just kila consistency).

        'target_lang' ni the target language kila which the given objects
        are being compiled. This allows specific linkage time treatment of
        certain languages.

        Raises LibError on failure.
        """
        pita


    # values kila target_desc parameter kwenye link()
    SHARED_OBJECT = "shared_object"
    SHARED_LIBRARY = "shared_library"
    EXECUTABLE = "executable"

    eleza link(self,
             target_desc,
             objects,
             output_filename,
             output_dir=Tupu,
             libraries=Tupu,
             library_dirs=Tupu,
             runtime_library_dirs=Tupu,
             export_symbols=Tupu,
             debug=0,
             extra_preargs=Tupu,
             extra_postargs=Tupu,
             build_temp=Tupu,
             target_lang=Tupu):
        """Link a bunch of stuff together to create an executable ama
        shared library file.

        The "bunch of stuff" consists of the list of object files supplied
        kama 'objects'.  'output_filename' should be a filename.  If
        'output_dir' ni supplied, 'output_filename' ni relative to it
        (i.e. 'output_filename' can provide directory components if
        needed).

        'libraries' ni a list of libraries to link against.  These are
        library names, sio filenames, since they're translated into
        filenames kwenye a platform-specific way (eg. "foo" becomes "libfoo.a"
        on Unix na "foo.lib" on DOS/Windows).  However, they can include a
        directory component, which means the linker will look kwenye that
        specific directory rather than searching all the normal locations.

        'library_dirs', ikiwa supplied, should be a list of directories to
        search kila libraries that were specified kama bare library names
        (ie. no directory component).  These are on top of the system
        default na those supplied to 'add_library_dir()' and/or
        'set_library_dirs()'.  'runtime_library_dirs' ni a list of
        directories that will be embedded into the shared library na used
        to search kila other shared libraries that *it* depends on at
        run-time.  (This may only be relevant on Unix.)

        'export_symbols' ni a list of symbols that the shared library will
        export.  (This appears to be relevant only on Windows.)

        'debug' ni kama kila 'compile()' na 'create_static_lib()', ukijumuisha the
        slight distinction that it actually matters on most platforms (as
        opposed to 'create_static_lib()', which includes a 'debug' flag
        mostly kila form's sake).

        'extra_preargs' na 'extra_postargs' are kama kila 'compile()' (except
        of course that they supply command-line arguments kila the
        particular linker being used).

        'target_lang' ni the target language kila which the given objects
        are being compiled. This allows specific linkage time treatment of
        certain languages.

        Raises LinkError on failure.
        """
        ashiria NotImplementedError


    # Old 'link_*()' methods, rewritten to use the new 'link()' method.

    eleza link_shared_lib(self,
                        objects,
                        output_libname,
                        output_dir=Tupu,
                        libraries=Tupu,
                        library_dirs=Tupu,
                        runtime_library_dirs=Tupu,
                        export_symbols=Tupu,
                        debug=0,
                        extra_preargs=Tupu,
                        extra_postargs=Tupu,
                        build_temp=Tupu,
                        target_lang=Tupu):
        self.link(CCompiler.SHARED_LIBRARY, objects,
                  self.library_filename(output_libname, lib_type='shared'),
                  output_dir,
                  libraries, library_dirs, runtime_library_dirs,
                  export_symbols, debug,
                  extra_preargs, extra_postargs, build_temp, target_lang)


    eleza link_shared_object(self,
                           objects,
                           output_filename,
                           output_dir=Tupu,
                           libraries=Tupu,
                           library_dirs=Tupu,
                           runtime_library_dirs=Tupu,
                           export_symbols=Tupu,
                           debug=0,
                           extra_preargs=Tupu,
                           extra_postargs=Tupu,
                           build_temp=Tupu,
                           target_lang=Tupu):
        self.link(CCompiler.SHARED_OBJECT, objects,
                  output_filename, output_dir,
                  libraries, library_dirs, runtime_library_dirs,
                  export_symbols, debug,
                  extra_preargs, extra_postargs, build_temp, target_lang)


    eleza link_executable(self,
                        objects,
                        output_progname,
                        output_dir=Tupu,
                        libraries=Tupu,
                        library_dirs=Tupu,
                        runtime_library_dirs=Tupu,
                        debug=0,
                        extra_preargs=Tupu,
                        extra_postargs=Tupu,
                        target_lang=Tupu):
        self.link(CCompiler.EXECUTABLE, objects,
                  self.executable_filename(output_progname), output_dir,
                  libraries, library_dirs, runtime_library_dirs, Tupu,
                  debug, extra_preargs, extra_postargs, Tupu, target_lang)


    # -- Miscellaneous methods -----------------------------------------
    # These are all used by the 'gen_lib_options() function; there is
    # no appropriate default implementation so subclasses should
    # implement all of these.

    eleza library_dir_option(self, dir):
        """Return the compiler option to add 'dir' to the list of
        directories searched kila libraries.
        """
        ashiria NotImplementedError

    eleza runtime_library_dir_option(self, dir):
        """Return the compiler option to add 'dir' to the list of
        directories searched kila runtime libraries.
        """
        ashiria NotImplementedError

    eleza library_option(self, lib):
        """Return the compiler option to add 'lib' to the list of libraries
        linked into the shared library ama executable.
        """
        ashiria NotImplementedError

    eleza has_function(self, funcname, includes=Tupu, include_dirs=Tupu,
                     libraries=Tupu, library_dirs=Tupu):
        """Return a boolean indicating whether funcname ni supported on
        the current platform.  The optional arguments can be used to
        augment the compilation environment.
        """
        # this can't be included at module scope because it tries to
        # agiza math which might sio be available at that point - maybe
        # the necessary logic should just be inlined?
        agiza tempfile
        ikiwa includes ni Tupu:
            includes = []
        ikiwa include_dirs ni Tupu:
            include_dirs = []
        ikiwa libraries ni Tupu:
            libraries = []
        ikiwa library_dirs ni Tupu:
            library_dirs = []
        fd, fname = tempfile.mkstemp(".c", funcname, text=Kweli)
        f = os.fdopen(fd, "w")
        jaribu:
            kila incl kwenye includes:
                f.write("""#include "%s"\n""" % incl)
            f.write("""\
int main (int argc, char **argv) {
    %s();
    rudisha 0;
}
""" % funcname)
        mwishowe:
            f.close()
        jaribu:
            objects = self.compile([fname], include_dirs=include_dirs)
        tatizo CompileError:
            rudisha Uongo

        jaribu:
            self.link_executable(objects, "a.out",
                                 libraries=libraries,
                                 library_dirs=library_dirs)
        tatizo (LinkError, TypeError):
            rudisha Uongo
        rudisha Kweli

    eleza find_library_file (self, dirs, lib, debug=0):
        """Search the specified list of directories kila a static ama shared
        library file 'lib' na rudisha the full path to that file.  If
        'debug' true, look kila a debugging version (ikiwa that makes sense on
        the current platform).  Return Tupu ikiwa 'lib' wasn't found kwenye any of
        the specified directories.
        """
        ashiria NotImplementedError

    # -- Filename generation methods -----------------------------------

    # The default implementation of the filename generating methods are
    # prejudiced towards the Unix/DOS/Windows view of the world:
    #   * object files are named by replacing the source file extension
    #     (eg. .c/.cpp -> .o/.obj)
    #   * library files (shared ama static) are named by plugging the
    #     library name na extension into a format string, eg.
    #     "lib%s.%s" % (lib_name, ".a") kila Unix static libraries
    #   * executables are named by appending an extension (possibly
    #     empty) to the program name: eg. progname + ".exe" for
    #     Windows
    #
    # To reduce redundant code, these methods expect to find
    # several attributes kwenye the current object (presumably defined
    # kama kundi attributes):
    #   * src_extensions -
    #     list of C/C++ source file extensions, eg. ['.c', '.cpp']
    #   * obj_extension -
    #     object file extension, eg. '.o' ama '.obj'
    #   * static_lib_extension -
    #     extension kila static library files, eg. '.a' ama '.lib'
    #   * shared_lib_extension -
    #     extension kila shared library/object files, eg. '.so', '.dll'
    #   * static_lib_format -
    #     format string kila generating static library filenames,
    #     eg. 'lib%s.%s' ama '%s.%s'
    #   * shared_lib_format
    #     format string kila generating shared library filenames
    #     (probably same kama static_lib_format, since the extension
    #     ni one of the intended parameters to the format string)
    #   * exe_extension -
    #     extension kila executable files, eg. '' ama '.exe'

    eleza object_filenames(self, source_filenames, strip_dir=0, output_dir=''):
        ikiwa output_dir ni Tupu:
            output_dir = ''
        obj_names = []
        kila src_name kwenye source_filenames:
            base, ext = os.path.splitext(src_name)
            base = os.path.splitdrive(base)[1] # Chop off the drive
            base = base[os.path.isabs(base):]  # If abs, chop off leading /
            ikiwa ext haiko kwenye self.src_extensions:
                ashiria UnknownFileError(
                      "unknown file type '%s' (kutoka '%s')" % (ext, src_name))
            ikiwa strip_dir:
                base = os.path.basename(base)
            obj_names.append(os.path.join(output_dir,
                                          base + self.obj_extension))
        rudisha obj_names

    eleza shared_object_filename(self, basename, strip_dir=0, output_dir=''):
        assert output_dir ni sio Tupu
        ikiwa strip_dir:
            basename = os.path.basename(basename)
        rudisha os.path.join(output_dir, basename + self.shared_lib_extension)

    eleza executable_filename(self, basename, strip_dir=0, output_dir=''):
        assert output_dir ni sio Tupu
        ikiwa strip_dir:
            basename = os.path.basename(basename)
        rudisha os.path.join(output_dir, basename + (self.exe_extension ama ''))

    eleza library_filename(self, libname, lib_type='static',     # ama 'shared'
                         strip_dir=0, output_dir=''):
        assert output_dir ni sio Tupu
        ikiwa lib_type haiko kwenye ("static", "shared", "dylib", "xcode_stub"):
            ashiria ValueError(
                  "'lib_type' must be \"static\", \"shared\", \"dylib\", ama \"xcode_stub\"")
        fmt = getattr(self, lib_type + "_lib_format")
        ext = getattr(self, lib_type + "_lib_extension")

        dir, base = os.path.split(libname)
        filename = fmt % (base, ext)
        ikiwa strip_dir:
            dir = ''

        rudisha os.path.join(output_dir, dir, filename)


    # -- Utility methods -----------------------------------------------

    eleza announce(self, msg, level=1):
        log.debug(msg)

    eleza debug_andika(self, msg):
        kutoka distutils.debug agiza DEBUG
        ikiwa DEBUG:
            andika(msg)

    eleza warn(self, msg):
        sys.stderr.write("warning: %s\n" % msg)

    eleza execute(self, func, args, msg=Tupu, level=1):
        execute(func, args, msg, self.dry_run)

    eleza spawn(self, cmd):
        spawn(cmd, dry_run=self.dry_run)

    eleza move_file(self, src, dst):
        rudisha move_file(src, dst, dry_run=self.dry_run)

    eleza mkpath (self, name, mode=0o777):
        mkpath(name, mode, dry_run=self.dry_run)


# Map a sys.platform/os.name ('posix', 'nt') to the default compiler
# type kila that platform. Keys are interpreted kama re match
# patterns. Order ni important; platform mappings are preferred over
# OS names.
_default_compilers = (

    # Platform string mappings

    # on a cygwin built python we can use gcc like an ordinary UNIXish
    # compiler
    ('cygwin.*', 'unix'),

    # OS name mappings
    ('posix', 'unix'),
    ('nt', 'msvc'),

    )

eleza get_default_compiler(osname=Tupu, platform=Tupu):
    """Determine the default compiler to use kila the given platform.

       osname should be one of the standard Python OS names (i.e. the
       ones returned by os.name) na platform the common value
       returned by sys.platform kila the platform kwenye question.

       The default values are os.name na sys.platform kwenye case the
       parameters are sio given.
    """
    ikiwa osname ni Tupu:
        osname = os.name
    ikiwa platform ni Tupu:
        platform = sys.platform
    kila pattern, compiler kwenye _default_compilers:
        ikiwa re.match(pattern, platform) ni sio Tupu ama \
           re.match(pattern, osname) ni sio Tupu:
            rudisha compiler
    # Default to Unix compiler
    rudisha 'unix'

# Map compiler types to (module_name, class_name) pairs -- ie. where to
# find the code that implements an interface to this compiler.  (The module
# ni assumed to be kwenye the 'distutils' package.)
compiler_class = { 'unix':    ('unixccompiler', 'UnixCCompiler',
                               "standard UNIX-style compiler"),
                   'msvc':    ('_msvccompiler', 'MSVCCompiler',
                               "Microsoft Visual C++"),
                   'cygwin':  ('cygwinccompiler', 'CygwinCCompiler',
                               "Cygwin port of GNU C Compiler kila Win32"),
                   'mingw32': ('cygwinccompiler', 'Mingw32CCompiler',
                               "Mingw32 port of GNU C Compiler kila Win32"),
                   'bcpp':    ('bcppcompiler', 'BCPPCompiler',
                               "Borland C++ Compiler"),
                 }

eleza show_compilers():
    """Print list of available compilers (used by the "--help-compiler"
    options to "build", "build_ext", "build_clib").
    """
    # XXX this "knows" that the compiler option it's describing is
    # "--compiler", which just happens to be the case kila the three
    # commands that use it.
    kutoka distutils.fancy_getopt agiza FancyGetopt
    compilers = []
    kila compiler kwenye compiler_class.keys():
        compilers.append(("compiler="+compiler, Tupu,
                          compiler_class[compiler][2]))
    compilers.sort()
    pretty_printer = FancyGetopt(compilers)
    pretty_printer.print_help("List of available compilers:")


eleza new_compiler(plat=Tupu, compiler=Tupu, verbose=0, dry_run=0, force=0):
    """Generate an instance of some CCompiler subkundi kila the supplied
    platform/compiler combination.  'plat' defaults to 'os.name'
    (eg. 'posix', 'nt'), na 'compiler' defaults to the default compiler
    kila that platform.  Currently only 'posix' na 'nt' are supported, na
    the default compilers are "traditional Unix interface" (UnixCCompiler
    class) na Visual C++ (MSVCCompiler class).  Note that it's perfectly
    possible to ask kila a Unix compiler object under Windows, na a
    Microsoft compiler object under Unix -- ikiwa you supply a value for
    'compiler', 'plat' ni ignored.
    """
    ikiwa plat ni Tupu:
        plat = os.name

    jaribu:
        ikiwa compiler ni Tupu:
            compiler = get_default_compiler(plat)

        (module_name, class_name, long_description) = compiler_class[compiler]
    tatizo KeyError:
        msg = "don't know how to compile C/C++ code on platform '%s'" % plat
        ikiwa compiler ni sio Tupu:
            msg = msg + " ukijumuisha '%s' compiler" % compiler
        ashiria DistutilsPlatformError(msg)

    jaribu:
        module_name = "distutils." + module_name
        __import__ (module_name)
        module = sys.modules[module_name]
        klass = vars(module)[class_name]
    tatizo ImportError:
        ashiria DistutilsModuleError(
              "can't compile C/C++ code: unable to load module '%s'" % \
              module_name)
    tatizo KeyError:
        ashiria DistutilsModuleError(
               "can't compile C/C++ code: unable to find kundi '%s' "
               "in module '%s'" % (class_name, module_name))

    # XXX The Tupu ni necessary to preserve backwards compatibility
    # ukijumuisha classes that expect verbose to be the first positional
    # argument.
    rudisha klass(Tupu, dry_run, force)


eleza gen_preprocess_options(macros, include_dirs):
    """Generate C pre-processor options (-D, -U, -I) kama used by at least
    two types of compilers: the typical Unix compiler na Visual C++.
    'macros' ni the usual thing, a list of 1- ama 2-tuples, where (name,)
    means undefine (-U) macro 'name', na (name,value) means define (-D)
    macro 'name' to 'value'.  'include_dirs' ni just a list of directory
    names to be added to the header file search path (-I).  Returns a list
    of command-line options suitable kila either Unix compilers ama Visual
    C++.
    """
    # XXX it would be nice (mainly aesthetic, na so we don't generate
    # stupid-looking command lines) to go over 'macros' na eliminate
    # redundant definitions/undefinitions (ie. ensure that only the
    # latest mention of a particular macro winds up on the command
    # line).  I don't think it's essential, though, since most (all?)
    # Unix C compilers only pay attention to the latest -D ama -U
    # mention of a macro on their command line.  Similar situation for
    # 'include_dirs'.  I'm punting on both kila now.  Anyways, weeding out
    # redundancies like this should probably be the province of
    # CCompiler, since the data structures used are inherited kutoka it
    # na therefore common to all CCompiler classes.
    pp_opts = []
    kila macro kwenye macros:
        ikiwa sio (isinstance(macro, tuple) na 1 <= len(macro) <= 2):
            ashiria TypeError(
                  "bad macro definition '%s': "
                  "each element of 'macros' list must be a 1- ama 2-tuple"
                  % macro)

        ikiwa len(macro) == 1:        # undefine this macro
            pp_opts.append("-U%s" % macro[0])
        lasivyo len(macro) == 2:
            ikiwa macro[1] ni Tupu:    # define ukijumuisha no explicit value
                pp_opts.append("-D%s" % macro[0])
            isipokua:
                # XXX *don't* need to be clever about quoting the
                # macro value here, because we're going to avoid the
                # shell at all costs when we spawn the command!
                pp_opts.append("-D%s=%s" % macro)

    kila dir kwenye include_dirs:
        pp_opts.append("-I%s" % dir)
    rudisha pp_opts


eleza gen_lib_options (compiler, library_dirs, runtime_library_dirs, libraries):
    """Generate linker options kila searching library directories na
    linking ukijumuisha specific libraries.  'libraries' na 'library_dirs' are,
    respectively, lists of library names (sio filenames!) na search
    directories.  Returns a list of command-line options suitable kila use
    ukijumuisha some compiler (depending on the two format strings pitaed in).
    """
    lib_opts = []

    kila dir kwenye library_dirs:
        lib_opts.append(compiler.library_dir_option(dir))

    kila dir kwenye runtime_library_dirs:
        opt = compiler.runtime_library_dir_option(dir)
        ikiwa isinstance(opt, list):
            lib_opts = lib_opts + opt
        isipokua:
            lib_opts.append(opt)

    # XXX it's important that we *not* remove redundant library mentions!
    # sometimes you really do have to say "-lfoo -lbar -lfoo" kwenye order to
    # resolve all symbols.  I just hope we never have to say "-lfoo obj.o
    # -lbar" to get things to work -- that's certainly a possibility, but a
    # pretty nasty way to arrange your C code.

    kila lib kwenye libraries:
        (lib_dir, lib_name) = os.path.split(lib)
        ikiwa lib_dir:
            lib_file = compiler.find_library_file([lib_dir], lib_name)
            ikiwa lib_file:
                lib_opts.append(lib_file)
            isipokua:
                compiler.warn("no library file corresponding to "
                              "'%s' found (skipping)" % lib)
        isipokua:
            lib_opts.append(compiler.library_option (lib))
    rudisha lib_opts
