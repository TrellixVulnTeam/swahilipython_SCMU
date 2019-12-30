"""distutils.msvc9compiler

Contains MSVCCompiler, an implementation of the abstract CCompiler class
kila the Microsoft Visual Studio 2008.

The module ni compatible ukijumuisha VS 2005 na VS 2008. You can find legacy support
kila older versions of VS kwenye distutils.msvccompiler.
"""

# Written by Perry Stoll
# hacked by Robin Becker na Thomas Heller to do a better job of
#   finding DevStudio (through the registry)
# ported to VS2005 na VS 2008 by Christian Heimes

agiza os
agiza subprocess
agiza sys
agiza re

kutoka distutils.errors agiza DistutilsExecError, DistutilsPlatformError, \
                             CompileError, LibError, LinkError
kutoka distutils.ccompiler agiza CCompiler, gen_preprocess_options, \
                                gen_lib_options
kutoka distutils agiza log
kutoka distutils.util agiza get_platform

agiza winreg

RegOpenKeyEx = winreg.OpenKeyEx
RegEnumKey = winreg.EnumKey
RegEnumValue = winreg.EnumValue
RegError = winreg.error

HKEYS = (winreg.HKEY_USERS,
         winreg.HKEY_CURRENT_USER,
         winreg.HKEY_LOCAL_MACHINE,
         winreg.HKEY_CLASSES_ROOT)

NATIVE_WIN64 = (sys.platform == 'win32' na sys.maxsize > 2**32)
ikiwa NATIVE_WIN64:
    # Visual C++ ni a 32-bit application, so we need to look in
    # the corresponding registry branch, ikiwa we're running a
    # 64-bit Python on Win64
    VS_BASE = r"Software\Wow6432Node\Microsoft\VisualStudio\%0.1f"
    WINSDK_BASE = r"Software\Wow6432Node\Microsoft\Microsoft SDKs\Windows"
    NET_BASE = r"Software\Wow6432Node\Microsoft\.NETFramework"
isipokua:
    VS_BASE = r"Software\Microsoft\VisualStudio\%0.1f"
    WINSDK_BASE = r"Software\Microsoft\Microsoft SDKs\Windows"
    NET_BASE = r"Software\Microsoft\.NETFramework"

# A map keyed by get_platform() rudisha values to values accepted by
# 'vcvarsall.bat'.  Note a cross-compile may combine these (eg, 'x86_amd64' is
# the param to cross-compile on x86 targeting amd64.)
PLAT_TO_VCVARS = {
    'win32' : 'x86',
    'win-amd64' : 'amd64',
}

kundi Reg:
    """Helper kundi to read values kutoka the registry
    """

    eleza get_value(cls, path, key):
        kila base kwenye HKEYS:
            d = cls.read_values(base, path)
            ikiwa d na key kwenye d:
                rudisha d[key]
         ashiria KeyError(key)
    get_value = classmethod(get_value)

    eleza read_keys(cls, base, key):
        """Return list of registry keys."""
        jaribu:
            handle = RegOpenKeyEx(base, key)
        except RegError:
            rudisha Tupu
        L = []
        i = 0
        wakati Kweli:
            jaribu:
                k = RegEnumKey(handle, i)
            except RegError:
                koma
            L.append(k)
            i += 1
        rudisha L
    read_keys = classmethod(read_keys)

    eleza read_values(cls, base, key):
        """Return dict of registry keys na values.

        All names are converted to lowercase.
        """
        jaribu:
            handle = RegOpenKeyEx(base, key)
        except RegError:
            rudisha Tupu
        d = {}
        i = 0
        wakati Kweli:
            jaribu:
                name, value, type = RegEnumValue(handle, i)
            except RegError:
                koma
            name = name.lower()
            d[cls.convert_mbcs(name)] = cls.convert_mbcs(value)
            i += 1
        rudisha d
    read_values = classmethod(read_values)

    eleza convert_mbcs(s):
        dec = getattr(s, "decode", Tupu)
        ikiwa dec ni sio Tupu:
            jaribu:
                s = dec("mbcs")
            except UnicodeError:
                pass
        rudisha s
    convert_mbcs = staticmethod(convert_mbcs)

kundi MacroExpander:

    eleza __init__(self, version):
        self.macros = {}
        self.vsbase = VS_BASE % version
        self.load_macros(version)

    eleza set_macro(self, macro, path, key):
        self.macros["$(%s)" % macro] = Reg.get_value(path, key)

    eleza load_macros(self, version):
        self.set_macro("VCInstallDir", self.vsbase + r"\Setup\VC", "productdir")
        self.set_macro("VSInstallDir", self.vsbase + r"\Setup\VS", "productdir")
        self.set_macro("FrameworkDir", NET_BASE, "installroot")
        jaribu:
            ikiwa version >= 8.0:
                self.set_macro("FrameworkSDKDir", NET_BASE,
                               "sdkinstallrootv2.0")
            isipokua:
                 ashiria KeyError("sdkinstallrootv2.0")
        except KeyError:
             ashiria DistutilsPlatformError(
            """Python was built ukijumuisha Visual Studio 2008;
extensions must be built ukijumuisha a compiler than can generate compatible binaries.
Visual Studio 2008 was sio found on this system. If you have Cygwin installed,
you can try compiling ukijumuisha MingW32, by passing "-c mingw32" to setup.py.""")

        ikiwa version >= 9.0:
            self.set_macro("FrameworkVersion", self.vsbase, "clr version")
            self.set_macro("WindowsSdkDir", WINSDK_BASE, "currentinstallfolder")
        isipokua:
            p = r"Software\Microsoft\NET Framework Setup\Product"
            kila base kwenye HKEYS:
                jaribu:
                    h = RegOpenKeyEx(base, p)
                except RegError:
                    endelea
                key = RegEnumKey(h, 0)
                d = Reg.get_value(base, r"%s\%s" % (p, key))
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

eleza normalize_and_reduce_paths(paths):
    """Return a list of normalized paths ukijumuisha duplicates removed.

    The current order of paths ni maintained.
    """
    # Paths are normalized so things like:  /a na /a/ aren't both preserved.
    reduced_paths = []
    kila p kwenye paths:
        np = os.path.normpath(p)
        # XXX(nnorwitz): O(n**2), ikiwa reduced_paths gets long perhaps use a set.
        ikiwa np sio kwenye reduced_paths:
            reduced_paths.append(np)
    rudisha reduced_paths

eleza removeDuplicates(variable):
    """Remove duplicate values of an environment variable.
    """
    oldList = variable.split(os.pathsep)
    newList = []
    kila i kwenye oldList:
        ikiwa i sio kwenye newList:
            newList.append(i)
    newVariable = os.pathsep.join(newList)
    rudisha newVariable

eleza find_vcvarsall(version):
    """Find the vcvarsall.bat file

    At first it tries to find the productdir of VS 2008 kwenye the registry. If
    that fails it falls back to the VS90COMNTOOLS env var.
    """
    vsbase = VS_BASE % version
    jaribu:
        productdir = Reg.get_value(r"%s\Setup\VC" % vsbase,
                                   "productdir")
    except KeyError:
        log.debug("Unable to find productdir kwenye registry")
        productdir = Tupu

    ikiwa sio productdir ama sio os.path.isdir(productdir):
        toolskey = "VS%0.f0COMNTOOLS" % version
        toolsdir = os.environ.get(toolskey, Tupu)

        ikiwa toolsdir na os.path.isdir(toolsdir):
            productdir = os.path.join(toolsdir, os.pardir, os.pardir, "VC")
            productdir = os.path.abspath(productdir)
            ikiwa sio os.path.isdir(productdir):
                log.debug("%s ni sio a valid directory" % productdir)
                rudisha Tupu
        isipokua:
            log.debug("Env var %s ni sio set ama invalid" % toolskey)
    ikiwa sio productdir:
        log.debug("No productdir found")
        rudisha Tupu
    vcvarsall = os.path.join(productdir, "vcvarsall.bat")
    ikiwa os.path.isfile(vcvarsall):
        rudisha vcvarsall
    log.debug("Unable to find vcvarsall.bat")
    rudisha Tupu

eleza query_vcvarsall(version, arch="x86"):
    """Launch vcvarsall.bat na read the settings kutoka its environment
    """
    vcvarsall = find_vcvarsall(version)
    interesting = {"include", "lib", "libpath", "path"}
    result = {}

    ikiwa vcvarsall ni Tupu:
         ashiria DistutilsPlatformError("Unable to find vcvarsall.bat")
    log.debug("Calling 'vcvarsall.bat %s' (version=%s)", arch, version)
    popen = subprocess.Popen('"%s" %s & set' % (vcvarsall, arch),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    jaribu:
        stdout, stderr = popen.communicate()
        ikiwa popen.wait() != 0:
             ashiria DistutilsPlatformError(stderr.decode("mbcs"))

        stdout = stdout.decode("mbcs")
        kila line kwenye stdout.split("\n"):
            line = Reg.convert_mbcs(line)
            ikiwa '=' sio kwenye line:
                endelea
            line = line.strip()
            key, value = line.split('=', 1)
            key = key.lower()
            ikiwa key kwenye interesting:
                ikiwa value.endswith(os.pathsep):
                    value = value[:-1]
                result[key] = removeDuplicates(value)

    mwishowe:
        popen.stdout.close()
        popen.stderr.close()

    ikiwa len(result) != len(interesting):
         ashiria ValueError(str(list(result.keys())))

    rudisha result

# More globals
VERSION = get_build_version()
ikiwa VERSION < 8.0:
     ashiria DistutilsPlatformError("VC %0.1f ni sio supported by this module" % VERSION)
# MACROS = MacroExpander(VERSION)

kundi MSVCCompiler(CCompiler) :
    """Concrete kundi that implements an interface to Microsoft Visual C++,
       as defined by the CCompiler abstract class."""

    compiler_type = 'msvc'

    # Just set this so CCompiler's constructor doesn't barf.  We currently
    # don't use the 'set_executables()' bureaucracy provided by CCompiler,
    # as it really isn't necessary kila this sort of single-compiler class.
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
        self.__version = VERSION
        self.__root = r"Software\Microsoft\VisualStudio"
        # self.__macros = MACROS
        self.__paths = []
        # target platform (.plat_name ni consistent ukijumuisha 'bdist')
        self.plat_name = Tupu
        self.__arch = Tupu # deprecated name
        self.initialized = Uongo

    eleza initialize(self, plat_name=Tupu):
        # multi-init means we would need to check platform same each time...
        assert sio self.initialized, "don't init multiple times"
        ikiwa plat_name ni Tupu:
            plat_name = get_platform()
        # sanity check kila platforms to prevent obscure errors later.
        ok_plats = 'win32', 'win-amd64'
        ikiwa plat_name sio kwenye ok_plats:
             ashiria DistutilsPlatformError("--plat-name must be one of %s" %
                                         (ok_plats,))

        ikiwa "DISTUTILS_USE_SDK" kwenye os.environ na "MSSdk" kwenye os.environ na self.find_exe("cl.exe"):
            # Assume that the SDK set up everything alright; don't try to be
            # smarter
            self.cc = "cl.exe"
            self.linker = "link.exe"
            self.lib = "lib.exe"
            self.rc = "rc.exe"
            self.mc = "mc.exe"
        isipokua:
            # On x86, 'vcvars32.bat amd64' creates an env that doesn't work;
            # to cross compile, you use 'x86_amd64'.
            # On AMD64, 'vcvars32.bat amd64' ni a native build env; to cross
            # compile use 'x86' (ie, it runs the x86 compiler directly)
            ikiwa plat_name == get_platform() ama plat_name == 'win32':
                # native build ama cross-compile to win32
                plat_spec = PLAT_TO_VCVARS[plat_name]
            isipokua:
                # cross compile kutoka win32 -> some 64bit
                plat_spec = PLAT_TO_VCVARS[get_platform()] + '_' + \
                            PLAT_TO_VCVARS[plat_name]

            vc_env = query_vcvarsall(VERSION, plat_spec)

            self.__paths = vc_env['path'].split(os.pathsep)
            os.environ['lib'] = vc_env['lib']
            os.environ['include'] = vc_env['include']

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
            #self.set_path_env_var('lib')
            #self.set_path_env_var('include')

        # extend the MSVC path ukijumuisha the current path
        jaribu:
            kila p kwenye os.environ['path'].split(';'):
                self.__paths.append(p)
        except KeyError:
            pass
        self.__paths = normalize_and_reduce_paths(self.__paths)
        os.environ['path'] = ";".join(self.__paths)

        self.preprocess_options = Tupu
        ikiwa self.__arch == "x86":
            self.compile_options = [ '/nologo', '/Ox', '/MD', '/W3',
                                     '/DNDEBUG']
            self.compile_options_debug = ['/nologo', '/Od', '/MDd', '/W3',
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
        self.ldflags_static = [ '/nologo']

        self.initialized = Kweli

    # -- Worker methods ------------------------------------------------

    eleza object_filenames(self,
                         source_filenames,
                         strip_dir=0,
                         output_dir=''):
        # Copied kutoka ccompiler.py, extended to rudisha .res as 'object'-file
        # kila .rc input file
        ikiwa output_dir ni Tupu: output_dir = ''
        obj_names = []
        kila src_name kwenye source_filenames:
            (base, ext) = os.path.splitext (src_name)
            base = os.path.splitdrive(base)[1] # Chop off the drive
            base = base[os.path.isabs(base):]  # If abs, chop off leading /
            ikiwa ext sio kwenye self.src_extensions:
                # Better to  ashiria an exception instead of silently continuing
                # na later complain about sources na targets having
                # different lengths
                 ashiria CompileError ("Don't know how to compile %s" % src_name)
            ikiwa strip_dir:
                base = os.path.basename (base)
            ikiwa ext kwenye self._rc_extensions:
                obj_names.append (os.path.join (output_dir,
                                                base + self.res_extension))
            elikiwa ext kwenye self._mc_extensions:
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
            except KeyError:
                endelea
            ikiwa debug:
                # pass the full pathname to MSVC kwenye debug mode,
                # this allows the debugger to find the source file
                # without asking the user to browse kila it
                src = os.path.abspath(src)

            ikiwa ext kwenye self._c_extensions:
                input_opt = "/Tc" + src
            elikiwa ext kwenye self._cpp_extensions:
                input_opt = "/Tp" + src
            elikiwa ext kwenye self._rc_extensions:
                # compile .RC to .RES file
                input_opt = src
                output_opt = "/fo" + obj
                jaribu:
                    self.spawn([self.rc] + pp_opts +
                               [output_opt] + [input_opt])
                except DistutilsExecError as msg:
                     ashiria CompileError(msg)
                endelea
            elikiwa ext kwenye self._mc_extensions:
                # Compile .MC to .RC file to .RES file.
                #   * '-h dir' specifies the directory kila the
                #     generated include file
                #   * '-r dir' specifies the target directory of the
                #     generated RC file na the binary message resource
                #     it includes
                #
                # For now (since there are no options to change this),
                # we use the source-directory kila the include file and
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

                except DistutilsExecError as msg:
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
            except DistutilsExecError as msg:
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
                pass # XXX what goes here?
            jaribu:
                self.spawn([self.lib] + lib_args)
            except DistutilsExecError as msg:
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
            build_temp = os.path.dirname(objects[0])
            ikiwa export_symbols ni sio Tupu:
                (dll_name, dll_ext) = os.path.splitext(
                    os.path.basename(output_filename))
                implib_file = os.path.join(
                    build_temp,
                    self.library_filename(dll_name))
                ld_args.append ('/IMPLIB:' + implib_file)

            self.manifest_setup_ldargs(output_filename, build_temp, ld_args)

            ikiwa extra_preargs:
                ld_args[:0] = extra_preargs
            ikiwa extra_postargs:
                ld_args.extend(extra_postargs)

            self.mkpath(os.path.dirname(output_filename))
            jaribu:
                self.spawn([self.linker] + ld_args)
            except DistutilsExecError as msg:
                 ashiria LinkError(msg)

            # embed the manifest
            # XXX - this ni somewhat fragile - ikiwa mt.exe fails, distutils
            # will still consider the DLL up-to-date, but it will sio have a
            # manifest.  Maybe we should link to a temp file?  OTOH, that
            # implies a build environment error that shouldn't go undetected.
            mfinfo = self.manifest_get_embed_info(target_desc, ld_args)
            ikiwa mfinfo ni sio Tupu:
                mffilename, mfid = mfinfo
                out_arg = '-outputresource:%s;%s' % (output_filename, mfid)
                jaribu:
                    self.spawn(['mt.exe', '-nologo', '-manifest',
                                mffilename, out_arg])
                except DistutilsExecError as msg:
                     ashiria LinkError(msg)
        isipokua:
            log.debug("skipping %s (up-to-date)", output_filename)

    eleza manifest_setup_ldargs(self, output_filename, build_temp, ld_args):
        # If we need a manifest at all, an embedded manifest ni recommended.
        # See MSDN article titled
        # "How to: Embed a Manifest Inside a C/C++ Application"
        # (currently at http://msdn2.microsoft.com/en-us/library/ms235591(VS.80).aspx)
        # Ask the linker to generate the manifest kwenye the temp dir, so
        # we can check it, na possibly embed it, later.
        temp_manifest = os.path.join(
                build_temp,
                os.path.basename(output_filename) + ".manifest")
        ld_args.append('/MANIFESTFILE:' + temp_manifest)

    eleza manifest_get_embed_info(self, target_desc, ld_args):
        # If a manifest should be embedded, rudisha a tuple of
        # (manifest_filename, resource_id).  Returns Tupu ikiwa no manifest
        # should be embedded.  See http://bugs.python.org/issue7833 kila why
        # we want to avoid any manifest kila extension modules ikiwa we can)
        kila arg kwenye ld_args:
            ikiwa arg.startswith("/MANIFESTFILE:"):
                temp_manifest = arg.split(":", 1)[1]
                koma
        isipokua:
            # no /MANIFESTFILE so nothing to do.
            rudisha Tupu
        ikiwa target_desc == CCompiler.EXECUTABLE:
            # by default, executables always get the manifest ukijumuisha the
            # CRT referenced.
            mfid = 1
        isipokua:
            # Extension modules try na avoid any manifest ikiwa possible.
            mfid = 2
            temp_manifest = self._remove_visual_c_ref(temp_manifest)
        ikiwa temp_manifest ni Tupu:
            rudisha Tupu
        rudisha temp_manifest, mfid

    eleza _remove_visual_c_ref(self, manifest_file):
        jaribu:
            # Remove references to the Visual C runtime, so they will
            # fall through to the Visual C dependency of Python.exe.
            # This way, when installed kila a restricted user (e.g.
            # runtimes are sio kwenye WinSxS folder, but kwenye Python's own
            # folder), the runtimes do sio need to be kwenye every folder
            # ukijumuisha .pyd's.
            # Returns either the filename of the modified manifest or
            # Tupu ikiwa no manifest should be embedded.
            manifest_f = open(manifest_file)
            jaribu:
                manifest_buf = manifest_f.read()
            mwishowe:
                manifest_f.close()
            pattern = re.compile(
                r"""<assemblyIdentity.*?name=("|')Microsoft\."""\
                r"""VC\d{2}\.CRT("|').*?(/>|</assemblyIdentity>)""",
                re.DOTALL)
            manifest_buf = re.sub(pattern, "", manifest_buf)
            pattern = r"<dependentAssembly>\s*</dependentAssembly>"
            manifest_buf = re.sub(pattern, "", manifest_buf)
            # Now see ikiwa any other assemblies are referenced - ikiwa not, we
            # don't want a manifest embedded.
            pattern = re.compile(
                r"""<assemblyIdentity.*?name=(?:"|')(.+?)(?:"|')"""
                r""".*?(?:/>|</assemblyIdentity>)""", re.DOTALL)
            ikiwa re.search(pattern, manifest_buf) ni Tupu:
                rudisha Tupu

            manifest_f = open(manifest_file, 'w')
            jaribu:
                manifest_f.write(manifest_buf)
                rudisha manifest_file
            mwishowe:
                manifest_f.close()
        except OSError:
            pass

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
