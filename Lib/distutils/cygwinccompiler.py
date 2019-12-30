"""distutils.cygwinccompiler

Provides the CygwinCCompiler class, a subkundi of UnixCCompiler that
handles the Cygwin port of the GNU C compiler to Windows.  It also contains
the Mingw32CCompiler kundi which handles the mingw32 port of GCC (same as
cygwin kwenye no-cygwin mode).
"""

# problems:
#
# * ikiwa you use a msvc compiled python version (1.5.2)
#   1. you have to insert a __GNUC__ section kwenye its config.h
#   2. you have to generate an agiza library kila its dll
#      - create a def-file kila python??.dll
#      - create an agiza library using
#             dlltool --dllname python15.dll --eleza python15.eleza \
#                       --output-lib libpython15.a
#
#   see also http://starship.python.net/crew/kernr/mingw32/Notes.html
#
# * We put export_symbols kwenye a def-file, na don't use
#   --export-all-symbols because it doesn't worked reliable kwenye some
#   tested configurations. And because other windows compilers also
#   need their symbols specified this no serious problem.
#
# tested configurations:
#
# * cygwin gcc 2.91.57/ld 2.9.4/dllwrap 0.2.4 works
#   (after patching python's config.h na kila C++ some other include files)
#   see also http://starship.python.net/crew/kernr/mingw32/Notes.html
# * mingw32 gcc 2.95.2/ld 2.9.4/dllwrap 0.2.4 works
#   (ld doesn't support -shared, so we use dllwrap)
# * cygwin gcc 2.95.2/ld 2.10.90/dllwrap 2.10.90 works now
#   - its dllwrap doesn't work, there ni a bug kwenye binutils 2.10.90
#     see also http://sources.redhat.com/ml/cygwin/2000-06/msg01274.html
#   - using gcc -mdll instead dllwrap doesn't work without -static because
#     it tries to link against dlls instead their agiza libraries. (If
#     it finds the dll first.)
#     By specifying -static we force ld to link against the agiza libraries,
#     this ni windows standard na there are normally sio the necessary symbols
#     kwenye the dlls.
#   *** only the version of June 2000 shows these problems
# * cygwin gcc 3.2/ld 2.13.90 works
#   (ld supports -shared)
# * mingw gcc 3.2/ld 2.13 works
#   (ld supports -shared)

agiza os
agiza sys
agiza copy
kutoka subprocess agiza Popen, PIPE, check_output
agiza re

kutoka distutils.ccompiler agiza gen_preprocess_options, gen_lib_options
kutoka distutils.unixccompiler agiza UnixCCompiler
kutoka distutils.file_util agiza write_file
kutoka distutils.errors agiza (DistutilsExecError, CCompilerError,
        CompileError, UnknownFileError)
kutoka distutils agiza log
kutoka distutils.version agiza LooseVersion
kutoka distutils.spawn agiza find_executable

eleza get_msvcr():
    """Include the appropriate MSVC runtime library ikiwa Python was built
    ukijumuisha MSVC 7.0 ama later.
    """
    msc_pos = sys.version.find('MSC v.')
    ikiwa msc_pos != -1:
        msc_ver = sys.version[msc_pos+6:msc_pos+10]
        ikiwa msc_ver == '1300':
            # MSVC 7.0
            rudisha ['msvcr70']
        lasivyo msc_ver == '1310':
            # MSVC 7.1
            rudisha ['msvcr71']
        lasivyo msc_ver == '1400':
            # VS2005 / MSVC 8.0
            rudisha ['msvcr80']
        lasivyo msc_ver == '1500':
            # VS2008 / MSVC 9.0
            rudisha ['msvcr90']
        lasivyo msc_ver == '1600':
            # VS2010 / MSVC 10.0
            rudisha ['msvcr100']
        isipokua:
            ashiria ValueError("Unknown MS Compiler version %s " % msc_ver)


kundi CygwinCCompiler(UnixCCompiler):
    """ Handles the Cygwin port of the GNU C compiler to Windows.
    """
    compiler_type = 'cygwin'
    obj_extension = ".o"
    static_lib_extension = ".a"
    shared_lib_extension = ".dll"
    static_lib_format = "lib%s%s"
    shared_lib_format = "%s%s"
    exe_extension = ".exe"

    eleza __init__(self, verbose=0, dry_run=0, force=0):

        UnixCCompiler.__init__(self, verbose, dry_run, force)

        status, details = check_config_h()
        self.debug_andika("Python's GCC status: %s (details: %s)" %
                         (status, details))
        ikiwa status ni sio CONFIG_H_OK:
            self.warn(
                "Python's pyconfig.h doesn't seem to support your compiler. "
                "Reason: %s. "
                "Compiling may fail because of undefined preprocessor macros."
                % details)

        self.gcc_version, self.ld_version, self.dllwrap_version = \
            get_versions()
        self.debug_andika(self.compiler_type + ": gcc %s, ld %s, dllwrap %s\n" %
                         (self.gcc_version,
                          self.ld_version,
                          self.dllwrap_version) )

        # ld_version >= "2.10.90" na < "2.13" should also be able to use
        # gcc -mdll instead of dllwrap
        # Older dllwraps had own version numbers, newer ones use the
        # same kama the rest of binutils ( also ld )
        # dllwrap 2.10.90 ni buggy
        ikiwa self.ld_version >= "2.10.90":
            self.linker_dll = "gcc"
        isipokua:
            self.linker_dll = "dllwrap"

        # ld_version >= "2.13" support -shared so use it instead of
        # -mdll -static
        ikiwa self.ld_version >= "2.13":
            shared_option = "-shared"
        isipokua:
            shared_option = "-mdll -static"

        # Hard-code GCC because that's what this ni all about.
        # XXX optimization, warnings etc. should be customizable.
        self.set_executables(compiler='gcc -mcygwin -O -Wall',
                             compiler_so='gcc -mcygwin -mdll -O -Wall',
                             compiler_cxx='g++ -mcygwin -O -Wall',
                             linker_exe='gcc -mcygwin',
                             linker_so=('%s -mcygwin %s' %
                                        (self.linker_dll, shared_option)))

        # cygwin na mingw32 need different sets of libraries
        ikiwa self.gcc_version == "2.91.57":
            # cygwin shouldn't need msvcrt, but without the dlls will crash
            # (gcc version 2.91.57) -- perhaps something about initialization
            self.dll_libraries=["msvcrt"]
            self.warn(
                "Consider upgrading to a newer version of gcc")
        isipokua:
            # Include the appropriate MSVC runtime library ikiwa Python was built
            # ukijumuisha MSVC 7.0 ama later.
            self.dll_libraries = get_msvcr()

    eleza _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        """Compiles the source by spawning GCC na windres ikiwa needed."""
        ikiwa ext == '.rc' ama ext == '.res':
            # gcc needs '.res' na '.rc' compiled to object files !!!
            jaribu:
                self.spawn(["windres", "-i", src, "-o", obj])
            tatizo DistutilsExecError kama msg:
                ashiria CompileError(msg)
        isipokua: # kila other files use the C-compiler
            jaribu:
                self.spawn(self.compiler_so + cc_args + [src, '-o', obj] +
                           extra_postargs)
            tatizo DistutilsExecError kama msg:
                ashiria CompileError(msg)

    eleza link(self, target_desc, objects, output_filename, output_dir=Tupu,
             libraries=Tupu, library_dirs=Tupu, runtime_library_dirs=Tupu,
             export_symbols=Tupu, debug=0, extra_preargs=Tupu,
             extra_postargs=Tupu, build_temp=Tupu, target_lang=Tupu):
        """Link the objects."""
        # use separate copies, so we can modify the lists
        extra_preargs = copy.copy(extra_preargs ama [])
        libraries = copy.copy(libraries ama [])
        objects = copy.copy(objects ama [])

        # Additional libraries
        libraries.extend(self.dll_libraries)

        # handle export symbols by creating a def-file
        # ukijumuisha executables this only works ukijumuisha gcc/ld kama linker
        ikiwa ((export_symbols ni sio Tupu) na
            (target_desc != self.EXECUTABLE ama self.linker_dll == "gcc")):
            # (The linker doesn't do anything ikiwa output ni up-to-date.
            # So it would probably better to check ikiwa we really need this,
            # but kila this we had to insert some unchanged parts of
            # UnixCCompiler, na this ni sio what we want.)

            # we want to put some files kwenye the same directory kama the
            # object files are, build_temp doesn't help much
            # where are the object files
            temp_dir = os.path.dirname(objects[0])
            # name of dll to give the helper files the same base name
            (dll_name, dll_extension) = os.path.splitext(
                os.path.basename(output_filename))

            # generate the filenames kila these files
            def_file = os.path.join(temp_dir, dll_name + ".def")
            lib_file = os.path.join(temp_dir, 'lib' + dll_name + ".a")

            # Generate .eleza file
            contents = [
                "LIBRARY %s" % os.path.basename(output_filename),
                "EXPORTS"]
            kila sym kwenye export_symbols:
                contents.append(sym)
            self.execute(write_file, (def_file, contents),
                         "writing %s" % def_file)

            # next add options kila def-file na to creating agiza libraries

            # dllwrap uses different options than gcc/ld
            ikiwa self.linker_dll == "dllwrap":
                extra_preargs.extend(["--output-lib", lib_file])
                # kila dllwrap we have to use a special option
                extra_preargs.extend(["--def", def_file])
            # we use gcc/ld here na can be sure ld ni >= 2.9.10
            isipokua:
                # doesn't work: bfd_close build\...\libfoo.a: Invalid operation
                #extra_preargs.extend(["-Wl,--out-implib,%s" % lib_file])
                # kila gcc/ld the def-file ni specified kama any object files
                objects.append(def_file)

        #end: ikiwa ((export_symbols ni sio Tupu) na
        #        (target_desc != self.EXECUTABLE ama self.linker_dll == "gcc")):

        # who wants symbols na a many times larger output file
        # should explicitly switch the debug mode on
        # otherwise we let dllwrap/ld strip the output file
        # (On my machine: 10KiB < stripped_file < ??100KiB
        #   unstripped_file = stripped_file + XXX KiB
        #  ( XXX=254 kila a typical python extension))
        ikiwa sio debug:
            extra_preargs.append("-s")

        UnixCCompiler.link(self, target_desc, objects, output_filename,
                           output_dir, libraries, library_dirs,
                           runtime_library_dirs,
                           Tupu, # export_symbols, we do this kwenye our def-file
                           debug, extra_preargs, extra_postargs, build_temp,
                           target_lang)

    # -- Miscellaneous methods -----------------------------------------

    eleza object_filenames(self, source_filenames, strip_dir=0, output_dir=''):
        """Adds supports kila rc na res files."""
        ikiwa output_dir ni Tupu:
            output_dir = ''
        obj_names = []
        kila src_name kwenye source_filenames:
            # use normcase to make sure '.rc' ni really '.rc' na sio '.RC'
            base, ext = os.path.splitext(os.path.normcase(src_name))
            ikiwa ext haiko kwenye (self.src_extensions + ['.rc','.res']):
                ashiria UnknownFileError("unknown file type '%s' (kutoka '%s')" % \
                      (ext, src_name))
            ikiwa strip_dir:
                base = os.path.basename (base)
            ikiwa ext kwenye ('.res', '.rc'):
                # these need to be compiled to object files
                obj_names.append (os.path.join(output_dir,
                                              base + ext + self.obj_extension))
            isipokua:
                obj_names.append (os.path.join(output_dir,
                                               base + self.obj_extension))
        rudisha obj_names

# the same kama cygwin plus some additional parameters
kundi Mingw32CCompiler(CygwinCCompiler):
    """ Handles the Mingw32 port of the GNU C compiler to Windows.
    """
    compiler_type = 'mingw32'

    eleza __init__(self, verbose=0, dry_run=0, force=0):

        CygwinCCompiler.__init__ (self, verbose, dry_run, force)

        # ld_version >= "2.13" support -shared so use it instead of
        # -mdll -static
        ikiwa self.ld_version >= "2.13":
            shared_option = "-shared"
        isipokua:
            shared_option = "-mdll -static"

        # A real mingw32 doesn't need to specify a different entry point,
        # but cygwin 2.91.57 kwenye no-cygwin-mode needs it.
        ikiwa self.gcc_version <= "2.91.57":
            entry_point = '--entry _DllMain@12'
        isipokua:
            entry_point = ''

        ikiwa is_cygwingcc():
            ashiria CCompilerError(
                'Cygwin gcc cansio be used ukijumuisha --compiler=mingw32')

        self.set_executables(compiler='gcc -O -Wall',
                             compiler_so='gcc -mdll -O -Wall',
                             compiler_cxx='g++ -O -Wall',
                             linker_exe='gcc',
                             linker_so='%s %s %s'
                                        % (self.linker_dll, shared_option,
                                           entry_point))
        # Maybe we should also append -mthreads, but then the finished
        # dlls need another dll (mingwm10.dll see Mingw32 docs)
        # (-mthreads: Support thread-safe exception handling on `Mingw32')

        # no additional libraries needed
        self.dll_libraries=[]

        # Include the appropriate MSVC runtime library ikiwa Python was built
        # ukijumuisha MSVC 7.0 ama later.
        self.dll_libraries = get_msvcr()

# Because these compilers aren't configured kwenye Python's pyconfig.h file by
# default, we should at least warn the user ikiwa he ni using an unmodified
# version.

CONFIG_H_OK = "ok"
CONFIG_H_NOTOK = "sio ok"
CONFIG_H_UNCERTAIN = "uncertain"

eleza check_config_h():
    """Check ikiwa the current Python installation appears amenable to building
    extensions ukijumuisha GCC.

    Returns a tuple (status, details), where 'status' ni one of the following
    constants:

    - CONFIG_H_OK: all ni well, go ahead na compile
    - CONFIG_H_NOTOK: doesn't look good
    - CONFIG_H_UNCERTAIN: sio sure -- unable to read pyconfig.h

    'details' ni a human-readable string explaining the situation.

    Note there are two ways to conclude "OK": either 'sys.version' contains
    the string "GCC" (implying that this Python was built ukijumuisha GCC), ama the
    installed "pyconfig.h" contains the string "__GNUC__".
    """

    # XXX since this function also checks sys.version, it's sio strictly a
    # "pyconfig.h" check -- should probably be renamed...

    kutoka distutils agiza sysconfig

    # ikiwa sys.version contains GCC then python was compiled ukijumuisha GCC, na the
    # pyconfig.h file should be OK
    ikiwa "GCC" kwenye sys.version:
        rudisha CONFIG_H_OK, "sys.version mentions 'GCC'"

    # let's see ikiwa __GNUC__ ni mentioned kwenye python.h
    fn = sysconfig.get_config_h_filename()
    jaribu:
        config_h = open(fn)
        jaribu:
            ikiwa "__GNUC__" kwenye config_h.read():
                rudisha CONFIG_H_OK, "'%s' mentions '__GNUC__'" % fn
            isipokua:
                rudisha CONFIG_H_NOTOK, "'%s' does sio mention '__GNUC__'" % fn
        mwishowe:
            config_h.close()
    tatizo OSError kama exc:
        rudisha (CONFIG_H_UNCERTAIN,
                "couldn't read '%s': %s" % (fn, exc.strerror))

RE_VERSION = re.compile(br'(\d+\.\d+(\.\d+)*)')

eleza _find_exe_version(cmd):
    """Find the version of an executable by running `cmd` kwenye the shell.

    If the command ni sio found, ama the output does sio match
    `RE_VERSION`, returns Tupu.
    """
    executable = cmd.split()[0]
    ikiwa find_executable(executable) ni Tupu:
        rudisha Tupu
    out = Popen(cmd, shell=Kweli, stdout=PIPE).stdout
    jaribu:
        out_string = out.read()
    mwishowe:
        out.close()
    result = RE_VERSION.search(out_string)
    ikiwa result ni Tupu:
        rudisha Tupu
    # LooseVersion works ukijumuisha strings
    # so we need to decode our bytes
    rudisha LooseVersion(result.group(1).decode())

eleza get_versions():
    """ Try to find out the versions of gcc, ld na dllwrap.

    If sio possible it returns Tupu kila it.
    """
    commands = ['gcc -dumpversion', 'ld -v', 'dllwrap --version']
    rudisha tuple([_find_exe_version(cmd) kila cmd kwenye commands])

eleza is_cygwingcc():
    '''Try to determine ikiwa the gcc that would be used ni kutoka cygwin.'''
    out_string = check_output(['gcc', '-dumpmachine'])
    rudisha out_string.strip().endswith(b'cygwin')
