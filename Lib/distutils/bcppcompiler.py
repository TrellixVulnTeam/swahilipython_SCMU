"""distutils.bcppcompiler

Contains BorlandCCompiler, an implementation of the abstract CCompiler class
kila the Borland C++ compiler.
"""

# This implementation by Lyle Johnson, based on the original msvccompiler.py
# module na using the directions originally published by Gordon Williams.

# XXX looks like there's a LOT of overlap between these two classes:
# someone should sit down na factor out the common code as
# WindowsCCompiler!  --GPW


agiza os
kutoka distutils.errors agiza \
     DistutilsExecError, DistutilsPlatformError, \
     CompileError, LibError, LinkError, UnknownFileError
kutoka distutils.ccompiler agiza \
     CCompiler, gen_preprocess_options, gen_lib_options
kutoka distutils.file_util agiza write_file
kutoka distutils.dep_util agiza newer
kutoka distutils agiza log

kundi BCPPCompiler(CCompiler) :
    """Concrete kundi that implements an interface to the Borland C/C++
    compiler, kama defined by the CCompiler abstract class.
    """

    compiler_type = 'bcpp'

    # Just set this so CCompiler's constructor doesn't barf.  We currently
    # don't use the 'set_executables()' bureaucracy provided by CCompiler,
    # kama it really isn't necessary kila this sort of single-compiler class.
    # Would be nice to have a consistent interface ukijumuisha UnixCCompiler,
    # though, so it's worth thinking about.
    executables = {}

    # Private kundi data (need to distinguish C kutoka C++ source kila compiler)
    _c_extensions = ['.c']
    _cpp_extensions = ['.cc', '.cpp', '.cxx']

    # Needed kila the filename generation methods provided by the
    # base class, CCompiler.
    src_extensions = _c_extensions + _cpp_extensions
    obj_extension = '.obj'
    static_lib_extension = '.lib'
    shared_lib_extension = '.dll'
    static_lib_format = shared_lib_format = '%s%s'
    exe_extension = '.exe'


    eleza __init__ (self,
                  verbose=0,
                  dry_run=0,
                  force=0):

        CCompiler.__init__ (self, verbose, dry_run, force)

        # These executables are assumed to all be kwenye the path.
        # Borland doesn't seem to use any special registry settings to
        # indicate their installation locations.

        self.cc = "bcc32.exe"
        self.linker = "ilink32.exe"
        self.lib = "tlib.exe"

        self.preprocess_options = Tupu
        self.compile_options = ['/tWM', '/O2', '/q', '/g0']
        self.compile_options_debug = ['/tWM', '/Od', '/q', '/g0']

        self.ldflags_shared = ['/Tpd', '/Gn', '/q', '/x']
        self.ldflags_shared_debug = ['/Tpd', '/Gn', '/q', '/x']
        self.ldflags_static = []
        self.ldflags_exe = ['/Gn', '/q', '/x']
        self.ldflags_exe_debug = ['/Gn', '/q', '/x','/r']


    # -- Worker methods ------------------------------------------------

    eleza compile(self, sources,
                output_dir=Tupu, macros=Tupu, include_dirs=Tupu, debug=0,
                extra_preargs=Tupu, extra_postargs=Tupu, depends=Tupu):

        macros, objects, extra_postargs, pp_opts, build = \
                self._setup_compile(output_dir, macros, include_dirs, sources,
                                    depends, extra_postargs)
        compile_opts = extra_preargs ama []
        compile_opts.append ('-c')
        ikiwa debug:
            compile_opts.extend (self.compile_options_debug)
        isipokua:
            compile_opts.extend (self.compile_options)

        kila obj kwenye objects:
            jaribu:
                src, ext = build[obj]
            tatizo KeyError:
                endelea
            # XXX why do the normpath here?
            src = os.path.normpath(src)
            obj = os.path.normpath(obj)
            # XXX _setup_compile() did a mkpath() too but before the normpath.
            # Is it possible to skip the normpath?
            self.mkpath(os.path.dirname(obj))

            ikiwa ext == '.res':
                # This ni already a binary file -- skip it.
                endelea # the 'for' loop
            ikiwa ext == '.rc':
                # This needs to be compiled to a .res file -- do it now.
                jaribu:
                    self.spawn (["brcc32", "-fo", obj, src])
                tatizo DistutilsExecError kama msg:
                    ashiria CompileError(msg)
                endelea # the 'for' loop

            # The next two are both kila the real compiler.
            ikiwa ext kwenye self._c_extensions:
                input_opt = ""
            lasivyo ext kwenye self._cpp_extensions:
                input_opt = "-P"
            isipokua:
                # Unknown file type -- no extra options.  The compiler
                # will probably fail, but let it just kwenye case this ni a
                # file the compiler recognizes even ikiwa we don't.
                input_opt = ""

            output_opt = "-o" + obj

            # Compiler command line syntax is: "bcc32 [options] file(s)".
            # Note that the source file names must appear at the end of
            # the command line.
            jaribu:
                self.spawn ([self.cc] + compile_opts + pp_opts +
                            [input_opt, output_opt] +
                            extra_postargs + [src])
            tatizo DistutilsExecError kama msg:
                ashiria CompileError(msg)

        rudisha objects

    # compile ()


    eleza create_static_lib (self,
                           objects,
                           output_libname,
                           output_dir=Tupu,
                           debug=0,
                           target_lang=Tupu):

        (objects, output_dir) = self._fix_object_args (objects, output_dir)
        output_filename = \
            self.library_filename (output_libname, output_dir=output_dir)

        ikiwa self._need_link (objects, output_filename):
            lib_args = [output_filename, '/u'] + objects
            ikiwa debug:
                pita                    # XXX what goes here?
            jaribu:
                self.spawn ([self.lib] + lib_args)
            tatizo DistutilsExecError kama msg:
                ashiria LibError(msg)
        isipokua:
            log.debug("skipping %s (up-to-date)", output_filename)

    # create_static_lib ()


    eleza link (self,
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

        # XXX this ignores 'build_temp'!  should follow the lead of
        # msvccompiler.py

        (objects, output_dir) = self._fix_object_args (objects, output_dir)
        (libraries, library_dirs, runtime_library_dirs) = \
            self._fix_lib_args (libraries, library_dirs, runtime_library_dirs)

        ikiwa runtime_library_dirs:
            log.warn("I don't know what to do ukijumuisha 'runtime_library_dirs': %s",
                     str(runtime_library_dirs))

        ikiwa output_dir ni sio Tupu:
            output_filename = os.path.join (output_dir, output_filename)

        ikiwa self._need_link (objects, output_filename):

            # Figure out linker args based on type of target.
            ikiwa target_desc == CCompiler.EXECUTABLE:
                startup_obj = 'c0w32'
                ikiwa debug:
                    ld_args = self.ldflags_exe_debug[:]
                isipokua:
                    ld_args = self.ldflags_exe[:]
            isipokua:
                startup_obj = 'c0d32'
                ikiwa debug:
                    ld_args = self.ldflags_shared_debug[:]
                isipokua:
                    ld_args = self.ldflags_shared[:]


            # Create a temporary exports file kila use by the linker
            ikiwa export_symbols ni Tupu:
                def_file = ''
            isipokua:
                head, tail = os.path.split (output_filename)
                modname, ext = os.path.splitext (tail)
                temp_dir = os.path.dirname(objects[0]) # preserve tree structure
                def_file = os.path.join (temp_dir, '%s.def' % modname)
                contents = ['EXPORTS']
                kila sym kwenye (export_symbols ama []):
                    contents.append('  %s=_%s' % (sym, sym))
                self.execute(write_file, (def_file, contents),
                             "writing %s" % def_file)

            # Borland C++ has problems ukijumuisha '/' kwenye paths
            objects2 = map(os.path.normpath, objects)
            # split objects kwenye .obj na .res files
            # Borland C++ needs them at different positions kwenye the command line
            objects = [startup_obj]
            resources = []
            kila file kwenye objects2:
                (base, ext) = os.path.splitext(os.path.normcase(file))
                ikiwa ext == '.res':
                    resources.append(file)
                isipokua:
                    objects.append(file)


            kila l kwenye library_dirs:
                ld_args.append("/L%s" % os.path.normpath(l))
            ld_args.append("/L.") # we sometimes use relative paths

            # list of object files
            ld_args.extend(objects)

            # XXX the command-line syntax kila Borland C++ ni a bit wonky;
            # certain filenames are jammed together kwenye one big string, but
            # comma-delimited.  This doesn't mesh too well ukijumuisha the
            # Unix-centric attitude (ukijumuisha a DOS/Windows quoting hack) of
            # 'spawn()', so constructing the argument list ni a bit
            # awkward.  Note that doing the obvious thing na jamming all
            # the filenames na commas into one argument would be wrong,
            # because 'spawn()' would quote any filenames ukijumuisha spaces kwenye
            # them.  Arghghh!.  Apparently it works fine kama coded...

            # name of dll/exe file
            ld_args.extend([',',output_filename])
            # no map file na start libraries
            ld_args.append(',,')

            kila lib kwenye libraries:
                # see ikiwa we find it na ikiwa there ni a bcpp specific lib
                # (xxx_bcpp.lib)
                libfile = self.find_library_file(library_dirs, lib, debug)
                ikiwa libfile ni Tupu:
                    ld_args.append(lib)
                    # probably a BCPP internal library -- don't warn
                isipokua:
                    # full name which prefers bcpp_xxx.lib over xxx.lib
                    ld_args.append(libfile)

            # some default libraries
            ld_args.append ('import32')
            ld_args.append ('cw32mt')

            # eleza file kila export symbols
            ld_args.extend([',',def_file])
            # add resource files
            ld_args.append(',')
            ld_args.extend(resources)


            ikiwa extra_preargs:
                ld_args[:0] = extra_preargs
            ikiwa extra_postargs:
                ld_args.extend(extra_postargs)

            self.mkpath (os.path.dirname (output_filename))
            jaribu:
                self.spawn ([self.linker] + ld_args)
            tatizo DistutilsExecError kama msg:
                ashiria LinkError(msg)

        isipokua:
            log.debug("skipping %s (up-to-date)", output_filename)

    # link ()

    # -- Miscellaneous methods -----------------------------------------


    eleza find_library_file (self, dirs, lib, debug=0):
        # List of effective library names to try, kwenye order of preference:
        # xxx_bcpp.lib ni better than xxx.lib
        # na xxx_d.lib ni better than xxx.lib ikiwa debug ni set
        #
        # The "_bcpp" suffix ni to handle a Python installation kila people
        # ukijumuisha multiple compilers (primarily Distutils hackers, I suspect
        # ;-).  The idea ni they'd have one static library kila each
        # compiler they care about, since (almost?) every Windows compiler
        # seems to have a different format kila static libraries.
        ikiwa debug:
            dlib = (lib + "_d")
            try_names = (dlib + "_bcpp", lib + "_bcpp", dlib, lib)
        isipokua:
            try_names = (lib + "_bcpp", lib)

        kila dir kwenye dirs:
            kila name kwenye try_names:
                libfile = os.path.join(dir, self.library_filename(name))
                ikiwa os.path.exists(libfile):
                    rudisha libfile
        isipokua:
            # Oops, didn't find it kwenye *any* of 'dirs'
            rudisha Tupu

    # overwrite the one kutoka CCompiler to support rc na res-files
    eleza object_filenames (self,
                          source_filenames,
                          strip_dir=0,
                          output_dir=''):
        ikiwa output_dir ni Tupu: output_dir = ''
        obj_names = []
        kila src_name kwenye source_filenames:
            # use normcase to make sure '.rc' ni really '.rc' na sio '.RC'
            (base, ext) = os.path.splitext (os.path.normcase(src_name))
            ikiwa ext haiko kwenye (self.src_extensions + ['.rc','.res']):
                ashiria UnknownFileError("unknown file type '%s' (kutoka '%s')" % \
                      (ext, src_name))
            ikiwa strip_dir:
                base = os.path.basename (base)
            ikiwa ext == '.res':
                # these can go unchanged
                obj_names.append (os.path.join (output_dir, base + ext))
            lasivyo ext == '.rc':
                # these need to be compiled to .res-files
                obj_names.append (os.path.join (output_dir, base + '.res'))
            isipokua:
                obj_names.append (os.path.join (output_dir,
                                            base + self.obj_extension))
        rudisha obj_names

    # object_filenames ()

    eleza preprocess (self,
                    source,
                    output_file=Tupu,
                    macros=Tupu,
                    include_dirs=Tupu,
                    extra_preargs=Tupu,
                    extra_postargs=Tupu):

        (_, macros, include_dirs) = \
            self._fix_compile_args(Tupu, macros, include_dirs)
        pp_opts = gen_preprocess_options(macros, include_dirs)
        pp_args = ['cpp32.exe'] + pp_opts
        ikiwa output_file ni sio Tupu:
            pp_args.append('-o' + output_file)
        ikiwa extra_preargs:
            pp_args[:0] = extra_preargs
        ikiwa extra_postargs:
            pp_args.extend(extra_postargs)
        pp_args.append(source)

        # We need to preprocess: either we're being forced to, ama the
        # source file ni newer than the target (or the target doesn't
        # exist).
        ikiwa self.force ama output_file ni Tupu ama newer(source, output_file):
            ikiwa output_file:
                self.mkpath(os.path.dirname(output_file))
            jaribu:
                self.spawn(pp_args)
            tatizo DistutilsExecError kama msg:
                andika(msg)
                ashiria CompileError(msg)

    # preprocess()
