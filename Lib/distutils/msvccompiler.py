"""distutils.msvccompiler

Contains MSVCCompiler, an implementation of the abstract CCompiler class
kila the Microsoft Visual Studio.
"""

# Written by Perry Stoll
# hacked by Robin Becker na Thomas Heller to do a better job of
#   finding DevStudio (through the registry)

agiza sys, os
kutoka distutils.errors agiza \
     DistutilsExecError, DistutilsPlatformError, \
     CompileError, LibError, LinkError
kutoka distutils.ccompiler agiza \
     CCompiler, gen_preprocess_options, gen_lib_options
kutoka distutils agiza log

_can_read_reg = Uongo
jaribu:
    agiza winreg

    _can_read_reg = Kweli
    hkey_mod = winreg

    RegOpenKeyEx = winreg.OpenKeyEx
    RegEnumKey = winreg.EnumKey
    RegEnumValue = winreg.EnumValue
    RegError = winreg.error

tatizo ImportError:
    jaribu:
        agiza win32api
        agiza win32con
        _can_read_reg = Kweli
        hkey_mod = win32con

        RegOpenKeyEx = win32api.RegOpenKeyEx
        RegEnumKey = win32api.RegEnumKey
        RegEnumValue = win32api.RegEnumValue
        RegError = win32api.error
    tatizo ImportError:
        log.info("Warning: Can't read registry to find the "
                 "necessary compiler setting\n"
                 "Make sure that Python modules winreg, "
                 "win32api ama win32con are installed.")
        pita

ikiwa _can_read_reg:
    HKEYS = (hkey_mod.HKEY_USERS,
             hkey_mod.HKEY_CURRENT_USER,
             hkey_mod.HKEY_LOCAL_MACHINE,
             hkey_mod.HKEY_CLASSES_ROOT)

eleza read_keys(base, key):
    """Return list of registry keys."""
    jaribu:
        handle = RegOpenKeyEx(base, key)
    tatizo RegError:
        rudisha Tupu
    L = []
    i = 0
    wakati Kweli:
        jaribu:
            k = RegEnumKey(handle, i)
        tatizo RegError:
            koma
        L.append(k)
        i += 1
    rudisha L

eleza read_values(base, key):
    """Return dict of registry keys na values.

    All names are converted to lowercase.
    """
    jaribu:
        handle = RegOpenKeyEx(base, key)
    tatizo RegError:
        rudisha Tupu
    d = {}
    i = 0
    wakati Kweli:
        jaribu:
            name, value, type = RegEnumValue(handle, i)
        tatizo RegError:
            koma
        name = name.lower()
        d[convert_mbcs(name)] = convert_mbcs(value)
        i += 1
    rudisha d

eleza convert_mbcs(s):
    dec = getattr(s, "decode", Tupu)
    ikiwa dec ni sio Tupu:
        jaribu:
            s = dec("mbcs")
        tatizo UnicodeError:
            pita
    rudisha s

kundi MacroExpander:
    eleza __init__(self, version):
        self.macros = {}
        self.load_macros(version)

    eleza set_macro(self, macro, path, key):
        kila base kwenye HKEYS:
            d = read_values(base, path)
            ikiwa d:
                self.macros["$(%s)" % macro] = d[key]
                koma

    eleza load_macros(self, version):
        vsbase = r"Software\Microsoft\VisualStudio\%0.1f" % version
        self.set_macro("VCInstallDir", vsbase + r"\Setup\VC", "productdir")
        self.set_macro("VSInstallDir", vsbase + r"\Setup\VS", "productdir")
        net = r"Software\Microsoft\.NETFramework"
        self.set_macro("FrameworkDir", net, "installroot")
        jaribu:
            ikiwa version > 7.0:
                self.set_macro("FrameworkSDKDir", net, "sdkinstallrootv1.1")
            isipokua:
                self.set_macro("FrameworkSDKDir", net, "sdkinstallroot")
        tatizo KeyError kama exc: #
            ashiria DistutilsPlatformError(
            """Python was built ukijumuisha Visual Studio 2003;
extensions must be built ukijumuisha a compiler than can generate compatible binaries.
Visual Studio 2003 was sio found on this system. If you have Cygwin installed,
you can try compiling ukijumuisha MingW32, by pitaing "-c mingw32" to setup.py.""")

        p = r"Software\Microsoft\NET Framework Setup\Product"
        kila base kwenye HKEYS:
            jaribu:
                h = RegOpenKeyEx(base, p)
            tatizo RegError:
                endelea
            key = RegEnumKey(h, 0)
            d = read_values(base, r"%s\%s" % (p, key))
            self.macros["$(FrameworkVersion)"] = d["version"]

    eleza sub(self, s):
        kila k, v kwenye self.macros.items():
            s = s.replace(k, v)
        rudisha s

eleza get_build_version():
    """Return the version of MSVC that was used to build Python.

    For Python 2.3 na up, the version number ni included in
    sys.version.  For earlier versions, assume the compiler ni MSVC 6.
    """
    prefix = "MSC v."
    i = sys.version.find(prefix)
    ikiwa i == -1:
        rudisha 6
    i = i + len(prefix)
    s, rest = sys.version[i:].split(" ", 1)
    majorVersion = int(s[:-2]) - 6
    ikiwa majorVersion >= 13:
        # v13 was skipped na should be v14
        majorVersion += 1
    minorVersion = int(s[2:3]) / 10.0
    # I don't think paths are affected by minor version kwenye version 6
    ikiwa majorVersion == 6:
        minorVersion = 0
    ikiwa majorVersion >= 6:
        rudisha majorVersion + minorVersion
    # isipokua we don't know what version of the compiler this is
    rudisha Tupu

eleza get_build_architecture():
    """Return the processor architecture.

    Possible results are "Intel" ama "AMD64".
    """

    prefix = " bit ("
    i = sys.version.find(prefix)
    ikiwa i == -1:
        rudisha "Intel"
    j = sys.version.find(")", i)
    rudisha sys.version[i+len(prefix):j]

eleza normalize_and_reduce_paths(paths):
    """Return a list of normalized paths ukijumuisha duplicates removed.

    The current order of paths ni maintained.
    """
    # Paths are normalized so things like:  /a na /a/ aren't both preserved.
    reduced_paths = []
    kila p kwenye paths:
        np = os.path.normpath(p)
        # XXX(nnorwitz): O(n**2), ikiwa reduced_paths gets long perhaps use a set.
        ikiwa np haiko kwenye reduced_paths:
            reduced_paths.append(np)
    rudisha reduced_paths


kundi MSVCCompiler(CCompiler) :
    """Concrete kundi that implements an interface to Microsoft Visual C++,
       kama defined by the CCompiler abstract class."""

    compiler_type = 'msvc'

    # Just set this so CCompiler's constructor doesn't barf.  We currently
    # don't use the 'set_executables()' bureaucracy provided by CCompiler,
    # kama it really isn't necessary kila this sort of single-compiler class.
    # Would be nice to have a consistent interface ukijumuisha UnixCCompiler,
    # though, so it's worth thinking about.
    executables = {}

    # Private kundi data (need to distinguish C kutoka C++ source kila compiler)
    _c_extensions = ['.c']
    _cpp_extensions = ['.cc', '.cpp', '.cxx']
    _rc_extensions = ['.rc']
    _mc_extensions = ['.mc']

    # Needed kila the filename generation methods provided by the
    # base class, CCompiler.
    src_extensions = (_c_extensions + _cpp_extensions +
                      _rc_extensions + _mc_extensions)
    res_extension = '.res'
    obj_extension = '.obj'
    static_lib_extension = '.lib'
    shared_lib_extension = '.dll'
    static_lib_format = shared_lib_format = '%s%s'
    exe_extension = '.exe'

    eleza __init__(self, verbose=0, dry_run=0, force=0):
        CCompiler.__init__ (self, verbose, dry_run, force)
        self.__version = get_build_version()
        self.__arch = get_build_architecture()
        ikiwa self.__arch == "Intel":
            # x86
            ikiwa self.__version >= 7:
                self.__root = r"Software\Microsoft\VisualStudio"
                self.__macros = MacroExpander(self.__version)
            isipokua:
                self.__root = r"Software\Microsoft\Devstudio"
            self.__product = "Visual Studio version %s" % self.__version
        isipokua:
            # Win64. Assume this was built ukijumuisha the platform SDK
            self.__product = "Microsoft SDK compiler %s" % (self.__version + 6)

        self.initialized = Uongo

    eleza initialize(self):
        self.__paths = []
        ikiwa "DISTUTILS_USE_SDK" kwenye os.environ na "MSSdk" kwenye os.environ na self.find_exe("cl.exe"):
            # Assume that the SDK set up everything alright; don't try to be
            # smarter
            self.cc = "cl.exe"
            self.linker = "link.exe"
            self.lib = "lib.exe"
            self.rc = "rc.exe"
            self.mc = "mc.exe"
        isipokua:
            self.__paths = self.get_msvc_paths("path")

            ikiwa len(self.__paths) == 0:
                ashiria DistutilsPlatformError("Python was built ukijumuisha %s, "
                       "and extensions need to be built ukijumuisha the same "
                       "version of the compiler, but it isn't installed."
                       % self.__product)

            self.cc = self.find_exe("cl.exe")
            self.linker = self.find_exe("link.exe")
            self.lib = self.find_exe("lib.exe")
            self.rc = self.find_exe("rc.exe")   # resource compiler
            self.mc = self.find_exe("mc.exe")   # message compiler
            self.set_path_env_var('lib')
            self.set_path_env_var('include')

        # extend the MSVC path ukijumuisha the current path
        jaribu:
            kila p kwenye os.environ['path'].split(';'):
                self.__paths.append(p)
        tatizo KeyError:
            pita
        self.__paths = normalize_and_reduce_paths(self.__paths)
        os.environ['path'] = ";".join(self.__paths)

        self.preprocess_options = Tupu
        ikiwa self.__arch == "Intel":
            self.compile_options = [ '/nologo', '/Ox', '/MD', '/W3', '/GX' ,
                                     '/DNDEBUG']
            self.compile_options_debug = ['/nologo', '/Od', '/MDd', '/W3', '/GX',
                                          '/Z7', '/D_DEBUG']
        isipokua:
            # Win64
            self.compile_options = [ '/nologo', '/Ox', '/MD', '/W3', '/GS-' ,
                                     '/DNDEBUG']
            self.compile_options_debug = ['/nologo', '/Od', '/MDd', '/W3', '/GS-',
                                          '/Z7', '/D_DEBUG']

        self.ldflags_shared = ['/DLL', '/nologo', '/INCREMENTAL:NO']
        ikiwa self.__version >= 7:
            self.ldflags_shared_debug = [
                '/DLL', '/nologo', '/INCREMENTAL:no', '/DEBUG'
                ]
        isipokua:
            self.ldflags_shared_debug = [
                '/DLL', '/nologo', '/INCREMENTAL:no', '/pdb:Tupu', '/DEBUG'
                ]
        self.ldflags_static = [ '/nologo']

        self.initialized = Kweli

    # -- Worker methods ------------------------------------------------

    eleza object_filenames(self,
                         source_filenames,
                         strip_dir=0,
                         output_dir=''):
        # Copied kutoka ccompiler.py, extended to rudisha .res kama 'object'-file
        # kila .rc input file
        ikiwa output_dir ni Tupu: output_dir = ''
        obj_names = []
        kila src_name kwenye source_filenames:
            (base, ext) = os.path.splitext (src_name)
            base = os.path.splitdrive(base)[1] # Chop off the drive
            base = base[os.path.isabs(base):]  # If abs, chop off leading /
            ikiwa ext haiko kwenye self.src_extensions:
                # Better to ashiria an exception instead of silently continuing
                # na later complain about sources na targets having
                # different lengths
                ashiria CompileError ("Don't know how to compile %s" % src_name)
            ikiwa strip_dir:
                base = os.path.basename (base)
            ikiwa ext kwenye self._rc_extensions:
                obj_names.append (os.path.join (output_dir,
                                                base + self.res_extension))
            lasivyo ext kwenye self._mc_extensions:
                obj_names.append (os.path.join (output_dir,
                                                base + self.res_extension))
            isipokua:
                obj_names.append (os.path.join (output_dir,
                                                base + self.obj_extension))
        rudisha obj_names


    eleza compile(self, sources,
                output_dir=Tupu, macros=Tupu, include_dirs=Tupu, debug=0,
                extra_preargs=Tupu, extra_postargs=Tupu, depends=Tupu):

        ikiwa sio self.initialized:
            self.initialize()
        compile_info = self._setup_compile(output_dir, macros, include_dirs,
                                           sources, depends, extra_postargs)
        macros, objects, extra_postargs, pp_opts, build = compile_info

        compile_opts = extra_preargs ama []
        compile_opts.append ('/c')
        ikiwa debug:
            compile_opts.extend(self.compile_options_debug)
        isipokua:
            compile_opts.extend(self.compile_options)

        kila obj kwenye objects:
            jaribu:
                src, ext = build[obj]
            tatizo KeyError:
                endelea
            ikiwa debug:
                # pita the full pathname to MSVC kwenye debug mode,
                # this allows the debugger to find the source file
                # without asking the user to browse kila it
                src = os.path.abspath(src)

            ikiwa ext kwenye self._c_extensions:
                input_opt = "/Tc" + src
            lasivyo ext kwenye self._cpp_extensions:
                input_opt = "/Tp" + src
            lasivyo ext kwenye self._rc_extensions:
                # compile .RC to .RES file
                input_opt = src
                output_opt = "/fo" + obj
                jaribu:
                    self.spawn([self.rc] + pp_opts +
                               [output_opt] + [input_opt])
                tatizo DistutilsExecError kama msg:
                    ashiria CompileError(msg)
                endelea
            lasivyo ext kwenye self._mc_extensions:
                # Compile .MC to .RC file to .RES file.
                #   * '-h dir' specifies the directory kila the
                #     generated include file
                #   * '-r dir' specifies the target directory of the
                #     generated RC file na the binary message resource
                #     it includes
                #
                # For now (since there are no options to change this),
                # we use the source-directory kila the include file na
                # the build directory kila the RC file na message
                # resources. This works at least kila win32all.
                h_dir = os.path.dirname(src)
                rc_dir = os.path.dirname(obj)
                jaribu:
                    # first compile .MC to .RC na .H file
                    self.spawn([self.mc] +
                               ['-h', h_dir, '-r', rc_dir] + [src])
                    base, _ = os.path.splitext (os.path.basename (src))
                    rc_file = os.path.join (rc_dir, base + '.rc')
                    # then compile .RC to .RES file
                    self.spawn([self.rc] +
                               ["/fo" + obj] + [rc_file])

                tatizo DistutilsExecError kama msg:
                    ashiria CompileError(msg)
                endelea
            isipokua:
                # how to handle this file?
                ashiria CompileError("Don't know how to compile %s to %s"
                                   % (src, obj))

            output_opt = "/Fo" + obj
            jaribu:
                self.spawn([self.cc] + compile_opts + pp_opts +
                           [input_opt, output_opt] +
                           extra_postargs)
            tatizo DistutilsExecError kama msg:
                ashiria CompileError(msg)

        rudisha objects


    eleza create_static_lib(self,
                          objects,
                          output_libname,
                          output_dir=Tupu,
                          debug=0,
                          target_lang=Tupu):

        ikiwa sio self.initialized:
            self.initialize()
        (objects, output_dir) = self._fix_object_args(objects, output_dir)
        output_filename = self.library_filename(output_libname,
                                                output_dir=output_dir)

        ikiwa self._need_link(objects, output_filename):
            lib_args = objects + ['/OUT:' + output_filename]
            ikiwa debug:
                pita # XXX what goes here?
            jaribu:
                self.spawn([self.lib] + lib_args)
            tatizo DistutilsExecError kama msg:
                ashiria LibError(msg)
        isipokua:
            log.debug("skipping %s (up-to-date)", output_filename)


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

        ikiwa sio self.initialized:
            self.initialize()
        (objects, output_dir) = self._fix_object_args(objects, output_dir)
        fixed_args = self._fix_lib_args(libraries, library_dirs,
                                        runtime_library_dirs)
        (libraries, library_dirs, runtime_library_dirs) = fixed_args

        ikiwa runtime_library_dirs:
            self.warn ("I don't know what to do ukijumuisha 'runtime_library_dirs': "
                       + str (runtime_library_dirs))

        lib_opts = gen_lib_options(self,
                                   library_dirs, runtime_library_dirs,
                                   libraries)
        ikiwa output_dir ni sio Tupu:
            output_filename = os.path.join(output_dir, output_filename)

        ikiwa self._need_link(objects, output_filename):
            ikiwa target_desc == CCompiler.EXECUTABLE:
                ikiwa debug:
                    ldflags = self.ldflags_shared_debug[1:]
                isipokua:
                    ldflags = self.ldflags_shared[1:]
            isipokua:
                ikiwa debug:
                    ldflags = self.ldflags_shared_debug
                isipokua:
                    ldflags = self.ldflags_shared

            export_opts = []
            kila sym kwenye (export_symbols ama []):
                export_opts.append("/EXPORT:" + sym)

            ld_args = (ldflags + lib_opts + export_opts +
                       objects + ['/OUT:' + output_filename])

            # The MSVC linker generates .lib na .exp files, which cannot be
            # suppressed by any linker switches. The .lib files may even be
            # needed! Make sure they are generated kwenye the temporary build
            # directory. Since they have different names kila debug na release
            # builds, they can go into the same directory.
            ikiwa export_symbols ni sio Tupu:
                (dll_name, dll_ext) = os.path.splitext(
                    os.path.basename(output_filename))
                implib_file = os.path.join(
                    os.path.dirname(objects[0]),
                    self.library_filename(dll_name))
                ld_args.append ('/IMPLIB:' + implib_file)

            ikiwa extra_preargs:
                ld_args[:0] = extra_preargs
            ikiwa extra_postargs:
                ld_args.extend(extra_postargs)

            self.mkpath(os.path.dirname(output_filename))
            jaribu:
                self.spawn([self.linker] + ld_args)
            tatizo DistutilsExecError kama msg:
                ashiria LinkError(msg)

        isipokua:
            log.debug("skipping %s (up-to-date)", output_filename)


    # -- Miscellaneous methods -----------------------------------------
    # These are all used by the 'gen_lib_options() function, in
    # ccompiler.py.

    eleza library_dir_option(self, dir):
        rudisha "/LIBPATH:" + dir

    eleza runtime_library_dir_option(self, dir):
        ashiria DistutilsPlatformError(
              "don't know how to set runtime library search path kila MSVC++")

    eleza library_option(self, lib):
        rudisha self.library_filename(lib)


    eleza find_library_file(self, dirs, lib, debug=0):
        # Prefer a debugging library ikiwa found (and requested), but deal
        # ukijumuisha it ikiwa we don't have one.
        ikiwa debug:
            try_names = [lib + "_d", lib]
        isipokua:
            try_names = [lib]
        kila dir kwenye dirs:
            kila name kwenye try_names:
                libfile = os.path.join(dir, self.library_filename (name))
                ikiwa os.path.exists(libfile):
                    rudisha libfile
        isipokua:
            # Oops, didn't find it kwenye *any* of 'dirs'
            rudisha Tupu

    # Helper methods kila using the MSVC registry settings

    eleza find_exe(self, exe):
        """Return path to an MSVC executable program.

        Tries to find the program kwenye several places: first, one of the
        MSVC program search paths kutoka the registry; next, the directories
        kwenye the PATH environment variable.  If any of those work, rudisha an
        absolute path that ni known to exist.  If none of them work, just
        rudisha the original program name, 'exe'.
        """
        kila p kwenye self.__paths:
            fn = os.path.join(os.path.abspath(p), exe)
            ikiwa os.path.isfile(fn):
                rudisha fn

        # didn't find it; try existing path
        kila p kwenye os.environ['Path'].split(';'):
            fn = os.path.join(os.path.abspath(p),exe)
            ikiwa os.path.isfile(fn):
                rudisha fn

        rudisha exe

    eleza get_msvc_paths(self, path, platform='x86'):
        """Get a list of devstudio directories (include, lib ama path).

        Return a list of strings.  The list will be empty ikiwa unable to
        access the registry ama appropriate registry keys sio found.
        """
        ikiwa sio _can_read_reg:
            rudisha []

        path = path + " dirs"
        ikiwa self.__version >= 7:
            key = (r"%s\%0.1f\VC\VC_OBJECTS_PLATFORM_INFO\Win32\Directories"
                   % (self.__root, self.__version))
        isipokua:
            key = (r"%s\6.0\Build System\Components\Platforms"
                   r"\Win32 (%s)\Directories" % (self.__root, platform))

        kila base kwenye HKEYS:
            d = read_values(base, key)
            ikiwa d:
                ikiwa self.__version >= 7:
                    rudisha self.__macros.sub(d[path]).split(";")
                isipokua:
                    rudisha d[path].split(";")
        # MSVC 6 seems to create the registry entries we need only when
        # the GUI ni run.
        ikiwa self.__version == 6:
            kila base kwenye HKEYS:
                ikiwa read_values(base, r"%s\6.0" % self.__root) ni sio Tupu:
                    self.warn("It seems you have Visual Studio 6 installed, "
                        "but the expected registry settings are sio present.\n"
                        "You must at least run the Visual Studio GUI once "
                        "so that these entries are created.")
                    koma
        rudisha []

    eleza set_path_env_var(self, name):
        """Set environment variable 'name' to an MSVC path type value.

        This ni equivalent to a SET command prior to execution of spawned
        commands.
        """

        ikiwa name == "lib":
            p = self.get_msvc_paths("library")
        isipokua:
            p = self.get_msvc_paths(name)
        ikiwa p:
            os.environ[name] = ';'.join(p)


ikiwa get_build_version() >= 8.0:
    log.debug("Importing new compiler kutoka distutils.msvc9compiler")
    OldMSVCCompiler = MSVCCompiler
    kutoka distutils.msvc9compiler agiza MSVCCompiler
    # get_build_architecture sio really relevant now we support cross-compile
    kutoka distutils.msvc9compiler agiza MacroExpander
