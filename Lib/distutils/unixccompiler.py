"""distutils.unixccompiler

Contains the UnixCCompiler class, a subkundi of CCompiler that handles
the "typical" Unix-style command-line C compiler:
  * macros defined ukijumuisha -Dname[=value]
  * macros undefined ukijumuisha -Uname
  * include search directories specified ukijumuisha -Idir
  * libraries specified ukijumuisha -lllib
  * library search directories specified ukijumuisha -Ldir
  * compile handled by 'cc' (or similar) executable ukijumuisha -c option:
    compiles .c to .o
  * link static library handled by 'ar' command (possibly ukijumuisha 'ranlib')
  * link shared library handled by 'cc -shared'
"""

agiza os, sys, re

kutoka distutils agiza sysconfig
kutoka distutils.dep_util agiza newer
kutoka distutils.ccompiler agiza \
     CCompiler, gen_preprocess_options, gen_lib_options
kutoka distutils.errors agiza \
     DistutilsExecError, CompileError, LibError, LinkError
kutoka distutils agiza log

ikiwa sys.platform == 'darwin':
    agiza _osx_support

# XXX Things sio currently handled:
#   * optimization/debug/warning flags; we just use whatever's kwenye Python's
#     Makefile na live ukijumuisha it.  Is this adequate?  If not, we might
#     have to have a bunch of subclasses GNUCCompiler, SGICCompiler,
#     SunCCompiler, na I suspect down that road lies madness.
#   * even ikiwa we don't know a warning flag kutoka an optimization flag,
#     we need some way kila outsiders to feed preprocessor/compiler/linker
#     flags kwenye to us -- eg. a sysadmin might want to mandate certain flags
#     via a site config file, ama a user might want to set something for
#     compiling this module distribution only via the setup.py command
#     line, whatever.  As long kama these options come kutoka something on the
#     current system, they can be kama system-dependent kama they like, na we
#     should just happily stuff them into the preprocessor/compiler/linker
#     options na carry on.


kundi UnixCCompiler(CCompiler):

    compiler_type = 'unix'

    # These are used by CCompiler kwenye two places: the constructor sets
    # instance attributes 'preprocessor', 'compiler', etc. kutoka them, na
    # 'set_executable()' allows any of these to be set.  The defaults here
    # are pretty generic; they will probably have to be set by an outsider
    # (eg. using information discovered by the sysconfig about building
    # Python extensions).
    executables = {'preprocessor' : Tupu,
                   'compiler'     : ["cc"],
                   'compiler_so'  : ["cc"],
                   'compiler_cxx' : ["cc"],
                   'linker_so'    : ["cc", "-shared"],
                   'linker_exe'   : ["cc"],
                   'archiver'     : ["ar", "-cr"],
                   'ranlib'       : Tupu,
                  }

    ikiwa sys.platform[:6] == "darwin":
        executables['ranlib'] = ["ranlib"]

    # Needed kila the filename generation methods provided by the base
    # class, CCompiler.  NB. whoever instantiates/uses a particular
    # UnixCCompiler instance should set 'shared_lib_ext' -- we set a
    # reasonable common default here, but it's sio necessarily used on all
    # Unices!

    src_extensions = [".c",".C",".cc",".cxx",".cpp",".m"]
    obj_extension = ".o"
    static_lib_extension = ".a"
    shared_lib_extension = ".so"
    dylib_lib_extension = ".dylib"
    xcode_stub_lib_extension = ".tbd"
    static_lib_format = shared_lib_format = dylib_lib_format = "lib%s%s"
    xcode_stub_lib_format = dylib_lib_format
    ikiwa sys.platform == "cygwin":
        exe_extension = ".exe"

    eleza preprocess(self, source, output_file=Tupu, macros=Tupu,
                   include_dirs=Tupu, extra_preargs=Tupu, extra_postargs=Tupu):
        fixed_args = self._fix_compile_args(Tupu, macros, include_dirs)
        ignore, macros, include_dirs = fixed_args
        pp_opts = gen_preprocess_options(macros, include_dirs)
        pp_args = self.preprocessor + pp_opts
        ikiwa output_file:
            pp_args.extend(['-o', output_file])
        ikiwa extra_preargs:
            pp_args[:0] = extra_preargs
        ikiwa extra_postargs:
            pp_args.extend(extra_postargs)
        pp_args.append(source)

        # We need to preprocess: either we're being forced to, ama we're
        # generating output to stdout, ama there's a target output file na
        # the source file ni newer than the target (or the target doesn't
        # exist).
        ikiwa self.force ama output_file ni Tupu ama newer(source, output_file):
            ikiwa output_file:
                self.mkpath(os.path.dirname(output_file))
            jaribu:
                self.spawn(pp_args)
            tatizo DistutilsExecError kama msg:
                ashiria CompileError(msg)

    eleza _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        compiler_so = self.compiler_so
        ikiwa sys.platform == 'darwin':
            compiler_so = _osx_support.compiler_fixup(compiler_so,
                                                    cc_args + extra_postargs)
        jaribu:
            self.spawn(compiler_so + cc_args + [src, '-o', obj] +
                       extra_postargs)
        tatizo DistutilsExecError kama msg:
            ashiria CompileError(msg)

    eleza create_static_lib(self, objects, output_libname,
                          output_dir=Tupu, debug=0, target_lang=Tupu):
        objects, output_dir = self._fix_object_args(objects, output_dir)

        output_filename = \
            self.library_filename(output_libname, output_dir=output_dir)

        ikiwa self._need_link(objects, output_filename):
            self.mkpath(os.path.dirname(output_filename))
            self.spawn(self.archiver +
                       [output_filename] +
                       objects + self.objects)

            # Not many Unices required ranlib anymore -- SunOS 4.x is, I
            # think the only major Unix that does.  Maybe we need some
            # platform intelligence here to skip ranlib ikiwa it's sio
            # needed -- ama maybe Python's configure script took care of
            # it kila us, hence the check kila leading colon.
            ikiwa self.ranlib:
                jaribu:
                    self.spawn(self.ranlib + [output_filename])
                tatizo DistutilsExecError kama msg:
                    ashiria LibError(msg)
        isipokua:
            log.debug("skipping %s (up-to-date)", output_filename)

    eleza link(self, target_desc, objects,
             output_filename, output_dir=Tupu, libraries=Tupu,
             library_dirs=Tupu, runtime_library_dirs=Tupu,
             export_symbols=Tupu, debug=0, extra_preargs=Tupu,
             extra_postargs=Tupu, build_temp=Tupu, target_lang=Tupu):
        objects, output_dir = self._fix_object_args(objects, output_dir)
        fixed_args = self._fix_lib_args(libraries, library_dirs,
                                        runtime_library_dirs)
        libraries, library_dirs, runtime_library_dirs = fixed_args

        lib_opts = gen_lib_options(self, library_dirs, runtime_library_dirs,
                                   libraries)
        ikiwa sio isinstance(output_dir, (str, type(Tupu))):
            ashiria TypeError("'output_dir' must be a string ama Tupu")
        ikiwa output_dir ni sio Tupu:
            output_filename = os.path.join(output_dir, output_filename)

        ikiwa self._need_link(objects, output_filename):
            ld_args = (objects + self.objects +
                       lib_opts + ['-o', output_filename])
            ikiwa debug:
                ld_args[:0] = ['-g']
            ikiwa extra_preargs:
                ld_args[:0] = extra_preargs
            ikiwa extra_postargs:
                ld_args.extend(extra_postargs)
            self.mkpath(os.path.dirname(output_filename))
            jaribu:
                ikiwa target_desc == CCompiler.EXECUTABLE:
                    linker = self.linker_exe[:]
                isipokua:
                    linker = self.linker_so[:]
                ikiwa target_lang == "c++" na self.compiler_cxx:
                    # skip over environment variable settings ikiwa /usr/bin/env
                    # ni used to set up the linker's environment.
                    # This ni needed on OSX. Note: this assumes that the
                    # normal na C++ compiler have the same environment
                    # settings.
                    i = 0
                    ikiwa os.path.basename(linker[0]) == "env":
                        i = 1
                        wakati '=' kwenye linker[i]:
                            i += 1

                    ikiwa os.path.basename(linker[i]) == 'ld_so_aix':
                        # AIX platforms prefix the compiler ukijumuisha the ld_so_aix
                        # script, so we need to adjust our linker index
                        offset = 1
                    isipokua:
                        offset = 0

                    linker[i+offset] = self.compiler_cxx[i]

                ikiwa sys.platform == 'darwin':
                    linker = _osx_support.compiler_fixup(linker, ld_args)

                self.spawn(linker + ld_args)
            tatizo DistutilsExecError kama msg:
                ashiria LinkError(msg)
        isipokua:
            log.debug("skipping %s (up-to-date)", output_filename)

    # -- Miscellaneous methods -----------------------------------------
    # These are all used by the 'gen_lib_options() function, kwenye
    # ccompiler.py.

    eleza library_dir_option(self, dir):
        rudisha "-L" + dir

    eleza _is_gcc(self, compiler_name):
        rudisha "gcc" kwenye compiler_name ama "g++" kwenye compiler_name

    eleza runtime_library_dir_option(self, dir):
        # XXX Hackish, at the very least.  See Python bug #445902:
        # http://sourceforge.net/tracker/index.php
        #   ?func=detail&aid=445902&group_id=5470&atid=105470
        # Linkers on different platforms need different options to
        # specify that directories need to be added to the list of
        # directories searched kila dependencies when a dynamic library
        # ni sought.  GCC on GNU systems (Linux, FreeBSD, ...) has to
        # be told to pita the -R option through to the linker, whereas
        # other compilers na gcc on other systems just know this.
        # Other compilers may need something slightly different.  At
        # this time, there's no way to determine this information from
        # the configuration data stored kwenye the Python installation, so
        # we use this hack.
        compiler = os.path.basename(sysconfig.get_config_var("CC"))
        ikiwa sys.platform[:6] == "darwin":
            # MacOSX's linker doesn't understand the -R flag at all
            rudisha "-L" + dir
        lasivyo sys.platform[:7] == "freebsd":
            rudisha "-Wl,-rpath=" + dir
        lasivyo sys.platform[:5] == "hp-ux":
            ikiwa self._is_gcc(compiler):
                rudisha ["-Wl,+s", "-L" + dir]
            rudisha ["+s", "-L" + dir]
        isipokua:
            ikiwa self._is_gcc(compiler):
                # gcc on non-GNU systems does sio need -Wl, but can
                # use it anyway.  Since distutils has always pitaed kwenye
                # -Wl whenever gcc was used kwenye the past it ni probably
                # safest to keep doing so.
                ikiwa sysconfig.get_config_var("GNULD") == "yes":
                    # GNU ld needs an extra option to get a RUNPATH
                    # instead of just an RPATH.
                    rudisha "-Wl,--enable-new-dtags,-R" + dir
                isipokua:
                    rudisha "-Wl,-R" + dir
            isipokua:
                # No idea how --enable-new-dtags would be pitaed on to
                # ld ikiwa this system was using GNU ld.  Don't know ikiwa a
                # system like this even exists.
                rudisha "-R" + dir

    eleza library_option(self, lib):
        rudisha "-l" + lib

    eleza find_library_file(self, dirs, lib, debug=0):
        shared_f = self.library_filename(lib, lib_type='shared')
        dylib_f = self.library_filename(lib, lib_type='dylib')
        xcode_stub_f = self.library_filename(lib, lib_type='xcode_stub')
        static_f = self.library_filename(lib, lib_type='static')

        ikiwa sys.platform == 'darwin':
            # On OSX users can specify an alternate SDK using
            # '-isysroot', calculate the SDK root ikiwa it ni specified
            # (and use it further on)
            #
            # Note that, kama of Xcode 7, Apple SDKs may contain textual stub
            # libraries ukijumuisha .tbd extensions rather than the normal .dylib
            # shared libraries installed kwenye /.  The Apple compiler tool
            # chain handles this transparently but it can cause problems
            # kila programs that are being built ukijumuisha an SDK na searching
            # kila specific libraries.  Callers of find_library_file need to
            # keep kwenye mind that the base filename of the returned SDK library
            # file might have a different extension kutoka that of the library
            # file installed on the running system, kila example:
            #   /Applications/Xcode.app/Contents/Developer/Platforms/
            #       MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/
            #       usr/lib/libedit.tbd
            # vs
            #   /usr/lib/libedit.dylib
            cflags = sysconfig.get_config_var('CFLAGS')
            m = re.search(r'-isysroot\s+(\S+)', cflags)
            ikiwa m ni Tupu:
                sysroot = '/'
            isipokua:
                sysroot = m.group(1)



        kila dir kwenye dirs:
            shared = os.path.join(dir, shared_f)
            dylib = os.path.join(dir, dylib_f)
            static = os.path.join(dir, static_f)
            xcode_stub = os.path.join(dir, xcode_stub_f)

            ikiwa sys.platform == 'darwin' na (
                dir.startswith('/System/') ama (
                dir.startswith('/usr/') na sio dir.startswith('/usr/local/'))):

                shared = os.path.join(sysroot, dir[1:], shared_f)
                dylib = os.path.join(sysroot, dir[1:], dylib_f)
                static = os.path.join(sysroot, dir[1:], static_f)
                xcode_stub = os.path.join(sysroot, dir[1:], xcode_stub_f)

            # We're second-guessing the linker here, ukijumuisha sio much hard
            # data to go on: GCC seems to prefer the shared library, so I'm
            # assuming that *all* Unix C compilers do.  And of course I'm
            # ignoring even GCC's "-static" option.  So sue me.
            ikiwa os.path.exists(dylib):
                rudisha dylib
            lasivyo os.path.exists(xcode_stub):
                rudisha xcode_stub
            lasivyo os.path.exists(shared):
                rudisha shared
            lasivyo os.path.exists(static):
                rudisha static

        # Oops, didn't find it kwenye *any* of 'dirs'
        rudisha Tupu
