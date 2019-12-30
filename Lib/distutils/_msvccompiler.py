"""distutils._msvccompiler

Contains MSVCCompiler, an implementation of the abstract CCompiler class
kila Microsoft Visual Studio 2015.

The module ni compatible ukijumuisha VS 2015 na later. You can find legacy support
kila older versions kwenye distutils.msvc9compiler na distutils.msvccompiler.
"""

# Written by Perry Stoll
# hacked by Robin Becker na Thomas Heller to do a better job of
#   finding DevStudio (through the registry)
# ported to VS 2005 na VS 2008 by Christian Heimes
# ported to VS 2015 by Steve Dower

agiza os
agiza shutil
agiza stat
agiza subprocess
agiza winreg

kutoka distutils.errors agiza DistutilsExecError, DistutilsPlatformError, \
                             CompileError, LibError, LinkError
kutoka distutils.ccompiler agiza CCompiler, gen_lib_options
kutoka distutils agiza log
kutoka distutils.util agiza get_platform

kutoka itertools agiza count

eleza _find_vc2015():
    jaribu:
        key = winreg.OpenKeyEx(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\VisualStudio\SxS\VC7",
            access=winreg.KEY_READ | winreg.KEY_WOW64_32KEY
        )
    except OSError:
        log.debug("Visual C++ ni sio registered")
        rudisha Tupu, Tupu

    best_version = 0
    best_dir = Tupu
    ukijumuisha key:
        kila i kwenye count():
            jaribu:
                v, vc_dir, vt = winreg.EnumValue(key, i)
            except OSError:
                koma
            ikiwa v na vt == winreg.REG_SZ na os.path.isdir(vc_dir):
                jaribu:
                    version = int(float(v))
                except (ValueError, TypeError):
                    endelea
                ikiwa version >= 14 na version > best_version:
                    best_version, best_dir = version, vc_dir
    rudisha best_version, best_dir

eleza _find_vc2017():
    """Returns "15, path" based on the result of invoking vswhere.exe
    If no install ni found, returns "Tupu, Tupu"

    The version ni returned to avoid unnecessarily changing the function
    result. It may be ignored when the path ni sio Tupu.

    If vswhere.exe ni sio available, by definition, VS 2017 ni not
    installed.
    """
    agiza json

    root = os.environ.get("ProgramFiles(x86)") ama os.environ.get("ProgramFiles")
    ikiwa sio root:
        rudisha Tupu, Tupu

    jaribu:
        path = subprocess.check_output([
            os.path.join(root, "Microsoft Visual Studio", "Installer", "vswhere.exe"),
            "-latest",
            "-prerelease",
            "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            "-property", "installationPath",
            "-products", "*",
        ], encoding="mbcs", errors="strict").strip()
    except (subprocess.CalledProcessError, OSError, UnicodeDecodeError):
        rudisha Tupu, Tupu

    path = os.path.join(path, "VC", "Auxiliary", "Build")
    ikiwa os.path.isdir(path):
        rudisha 15, path

    rudisha Tupu, Tupu

PLAT_SPEC_TO_RUNTIME = {
    'x86' : 'x86',
    'x86_amd64' : 'x64',
    'x86_arm' : 'arm',
    'x86_arm64' : 'arm64'
}

eleza _find_vcvarsall(plat_spec):
    _, best_dir = _find_vc2017()
    vcruntime = Tupu

    ikiwa plat_spec kwenye PLAT_SPEC_TO_RUNTIME:
        vcruntime_plat = PLAT_SPEC_TO_RUNTIME[plat_spec]
    isipokua:
        vcruntime_plat = 'x64' ikiwa 'amd64' kwenye plat_spec isipokua 'x86'

    ikiwa best_dir:
        vcredist = os.path.join(best_dir, "..", "..", "redist", "MSVC", "**",
            vcruntime_plat, "Microsoft.VC14*.CRT", "vcruntime140.dll")
        jaribu:
            agiza glob
            vcruntime = glob.glob(vcredist, recursive=Kweli)[-1]
        except (ImportError, OSError, LookupError):
            vcruntime = Tupu

    ikiwa sio best_dir:
        best_version, best_dir = _find_vc2015()
        ikiwa best_version:
            vcruntime = os.path.join(best_dir, 'redist', vcruntime_plat,
                "Microsoft.VC140.CRT", "vcruntime140.dll")

    ikiwa sio best_dir:
        log.debug("No suitable Visual C++ version found")
        rudisha Tupu, Tupu

    vcvarsall = os.path.join(best_dir, "vcvarsall.bat")
    ikiwa sio os.path.isfile(vcvarsall):
        log.debug("%s cannot be found", vcvarsall)
        rudisha Tupu, Tupu

    ikiwa sio vcruntime ama sio os.path.isfile(vcruntime):
        log.debug("%s cannot be found", vcruntime)
        vcruntime = Tupu

    rudisha vcvarsall, vcruntime

eleza _get_vc_env(plat_spec):
    ikiwa os.getenv("DISTUTILS_USE_SDK"):
        rudisha {
            key.lower(): value
            kila key, value kwenye os.environ.items()
        }

    vcvarsall, vcruntime = _find_vcvarsall(plat_spec)
    ikiwa sio vcvarsall:
         ashiria DistutilsPlatformError("Unable to find vcvarsall.bat")

    jaribu:
        out = subprocess.check_output(
            'cmd /u /c "{}" {} && set'.format(vcvarsall, plat_spec),
            stderr=subprocess.STDOUT,
        ).decode('utf-16le', errors='replace')
    except subprocess.CalledProcessError as exc:
        log.error(exc.output)
         ashiria DistutilsPlatformError("Error executing {}"
                .format(exc.cmd))

    env = {
        key.lower(): value
        kila key, _, value in
        (line.partition('=') kila line kwenye out.splitlines())
        ikiwa key na value
    }

    ikiwa vcruntime:
        env['py_vcruntime_redist'] = vcruntime
    rudisha env

eleza _find_exe(exe, paths=Tupu):
    """Return path to an MSVC executable program.

    Tries to find the program kwenye several places: first, one of the
    MSVC program search paths kutoka the registry; next, the directories
    kwenye the PATH environment variable.  If any of those work, rudisha an
    absolute path that ni known to exist.  If none of them work, just
    rudisha the original program name, 'exe'.
    """
    ikiwa sio paths:
        paths = os.getenv('path').split(os.pathsep)
    kila p kwenye paths:
        fn = os.path.join(os.path.abspath(p), exe)
        ikiwa os.path.isfile(fn):
            rudisha fn
    rudisha exe

# A map keyed by get_platform() rudisha values to values accepted by
# 'vcvarsall.bat'. Always cross-compile kutoka x86 to work ukijumuisha the
# lighter-weight MSVC installs that do sio include native 64-bit tools.
PLAT_TO_VCVARS = {
    'win32' : 'x86',
    'win-amd64' : 'x86_amd64',
    'win-arm32' : 'x86_arm',
    'win-arm64' : 'x86_arm64'
}

# A set containing the DLLs that are guaranteed to be available for
# all micro versions of this Python version. Known extension
# dependencies that are sio kwenye this set will be copied to the output
# path.
_BUNDLED_DLLS = frozenset(['vcruntime140.dll'])

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
        # target platform (.plat_name ni consistent ukijumuisha 'bdist')
        self.plat_name = Tupu
        self.initialized = Uongo

    eleza initialize(self, plat_name=Tupu):
        # multi-init means we would need to check platform same each time...
        assert sio self.initialized, "don't init multiple times"
        ikiwa plat_name ni Tupu:
            plat_name = get_platform()
        # sanity check kila platforms to prevent obscure errors later.
        ikiwa plat_name sio kwenye PLAT_TO_VCVARS:
             ashiria DistutilsPlatformError("--plat-name must be one of {}"
                                         .format(tuple(PLAT_TO_VCVARS)))

        # Get the vcvarsall.bat spec kila the requested platform.
        plat_spec = PLAT_TO_VCVARS[plat_name]

        vc_env = _get_vc_env(plat_spec)
        ikiwa sio vc_env:
             ashiria DistutilsPlatformError("Unable to find a compatible "
                "Visual Studio installation.")

        self._paths = vc_env.get('path', '')
        paths = self._paths.split(os.pathsep)
        self.cc = _find_exe("cl.exe", paths)
        self.linker = _find_exe("link.exe", paths)
        self.lib = _find_exe("lib.exe", paths)
        self.rc = _find_exe("rc.exe", paths)   # resource compiler
        self.mc = _find_exe("mc.exe", paths)   # message compiler
        self.mt = _find_exe("mt.exe", paths)   # message compiler
        self._vcruntime_redist = vc_env.get('py_vcruntime_redist', '')

        kila dir kwenye vc_env.get('include', '').split(os.pathsep):
            ikiwa dir:
                self.add_include_dir(dir.rstrip(os.sep))

        kila dir kwenye vc_env.get('lib', '').split(os.pathsep):
            ikiwa dir:
                self.add_library_dir(dir.rstrip(os.sep))

        self.preprocess_options = Tupu
        # If vcruntime_redist ni available, link against it dynamically. Otherwise,
        # use /MT[d] to build statically, then switch kutoka libucrt[d].lib to ucrt[d].lib
        # later to dynamically link to ucrtbase but sio vcruntime.
        self.compile_options = [
            '/nologo', '/Ox', '/W3', '/GL', '/DNDEBUG'
        ]
        self.compile_options.append('/MD' ikiwa self._vcruntime_redist isipokua '/MT')

        self.compile_options_debug = [
            '/nologo', '/Od', '/MDd', '/Zi', '/W3', '/D_DEBUG'
        ]

        ldflags = [
            '/nologo', '/INCREMENTAL:NO', '/LTCG'
        ]
        ikiwa sio self._vcruntime_redist:
            ldflags.extend(('/nodefaultlib:libucrt.lib', 'ucrt.lib'))

        ldflags_debug = [
            '/nologo', '/INCREMENTAL:NO', '/LTCG', '/DEBUG:FULL'
        ]

        self.ldflags_exe = [*ldflags, '/MANIFEST:EMBED,ID=1']
        self.ldflags_exe_debug = [*ldflags_debug, '/MANIFEST:EMBED,ID=1']
        self.ldflags_shared = [*ldflags, '/DLL', '/MANIFEST:EMBED,ID=2', '/MANIFESTUAC:NO']
        self.ldflags_shared_debug = [*ldflags_debug, '/DLL', '/MANIFEST:EMBED,ID=2', '/MANIFESTUAC:NO']
        self.ldflags_static = [*ldflags]
        self.ldflags_static_debug = [*ldflags_debug]

        self._ldflags = {
            (CCompiler.EXECUTABLE, Tupu): self.ldflags_exe,
            (CCompiler.EXECUTABLE, Uongo): self.ldflags_exe,
            (CCompiler.EXECUTABLE, Kweli): self.ldflags_exe_debug,
            (CCompiler.SHARED_OBJECT, Tupu): self.ldflags_shared,
            (CCompiler.SHARED_OBJECT, Uongo): self.ldflags_shared,
            (CCompiler.SHARED_OBJECT, Kweli): self.ldflags_shared_debug,
            (CCompiler.SHARED_LIBRARY, Tupu): self.ldflags_static,
            (CCompiler.SHARED_LIBRARY, Uongo): self.ldflags_static,
            (CCompiler.SHARED_LIBRARY, Kweli): self.ldflags_static_debug,
        }

        self.initialized = Kweli

    # -- Worker methods ------------------------------------------------

    eleza object_filenames(self,
                         source_filenames,
                         strip_dir=0,
                         output_dir=''):
        ext_map = {
            **{ext: self.obj_extension kila ext kwenye self.src_extensions},
            **{ext: self.res_extension kila ext kwenye self._rc_extensions + self._mc_extensions},
        }

        output_dir = output_dir ama ''

        eleza make_out_path(p):
            base, ext = os.path.splitext(p)
            ikiwa strip_dir:
                base = os.path.basename(base)
            isipokua:
                _, base = os.path.splitdrive(base)
                ikiwa base.startswith((os.path.sep, os.path.altsep)):
                    base = base[1:]
            jaribu:
                # XXX: This may produce absurdly long paths. We should check
                # the length of the result na trim base until we fit within
                # 260 characters.
                rudisha os.path.join(output_dir, base + ext_map[ext])
            except LookupError:
                # Better to  ashiria an exception instead of silently continuing
                # na later complain about sources na targets having
                # different lengths
                 ashiria CompileError("Don't know how to compile {}".format(p))

        rudisha list(map(make_out_path, source_filenames))


    eleza compile(self, sources,
                output_dir=Tupu, macros=Tupu, include_dirs=Tupu, debug=0,
                extra_preargs=Tupu, extra_postargs=Tupu, depends=Tupu):

        ikiwa sio self.initialized:
            self.initialize()
        compile_info = self._setup_compile(output_dir, macros, include_dirs,
                                           sources, depends, extra_postargs)
        macros, objects, extra_postargs, pp_opts, build = compile_info

        compile_opts = extra_preargs ama []
        compile_opts.append('/c')
        ikiwa debug:
            compile_opts.extend(self.compile_options_debug)
        isipokua:
            compile_opts.extend(self.compile_options)


        add_cpp_opts = Uongo

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
                add_cpp_opts = Kweli
            elikiwa ext kwenye self._rc_extensions:
                # compile .RC to .RES file
                input_opt = src
                output_opt = "/fo" + obj
                jaribu:
                    self.spawn([self.rc] + pp_opts + [output_opt, input_opt])
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
                    self.spawn([self.mc, '-h', h_dir, '-r', rc_dir, src])
                    base, _ = os.path.splitext(os.path.basename (src))
                    rc_file = os.path.join(rc_dir, base + '.rc')
                    # then compile .RC to .RES file
                    self.spawn([self.rc, "/fo" + obj, rc_file])

                except DistutilsExecError as msg:
                     ashiria CompileError(msg)
                endelea
            isipokua:
                # how to handle this file?
                 ashiria CompileError("Don't know how to compile {} to {}"
                                   .format(src, obj))

            args = [self.cc] + compile_opts + pp_opts
            ikiwa add_cpp_opts:
                args.append('/EHsc')
            args.append(input_opt)
            args.append("/Fo" + obj)
            args.extend(extra_postargs)

            jaribu:
                self.spawn(args)
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
        objects, output_dir = self._fix_object_args(objects, output_dir)
        output_filename = self.library_filename(output_libname,
                                                output_dir=output_dir)

        ikiwa self._need_link(objects, output_filename):
            lib_args = objects + ['/OUT:' + output_filename]
            ikiwa debug:
                pass # XXX what goes here?
            jaribu:
                log.debug('Executing "%s" %s', self.lib, ' '.join(lib_args))
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
        objects, output_dir = self._fix_object_args(objects, output_dir)
        fixed_args = self._fix_lib_args(libraries, library_dirs,
                                        runtime_library_dirs)
        libraries, library_dirs, runtime_library_dirs = fixed_args

        ikiwa runtime_library_dirs:
            self.warn("I don't know what to do ukijumuisha 'runtime_library_dirs': "
                       + str(runtime_library_dirs))

        lib_opts = gen_lib_options(self,
                                   library_dirs, runtime_library_dirs,
                                   libraries)
        ikiwa output_dir ni sio Tupu:
            output_filename = os.path.join(output_dir, output_filename)

        ikiwa self._need_link(objects, output_filename):
            ldflags = self._ldflags[target_desc, debug]

            export_opts = ["/EXPORT:" + sym kila sym kwenye (export_symbols ama [])]

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

            ikiwa extra_preargs:
                ld_args[:0] = extra_preargs
            ikiwa extra_postargs:
                ld_args.extend(extra_postargs)

            output_dir = os.path.dirname(os.path.abspath(output_filename))
            self.mkpath(output_dir)
            jaribu:
                log.debug('Executing "%s" %s', self.linker, ' '.join(ld_args))
                self.spawn([self.linker] + ld_args)
                self._copy_vcruntime(output_dir)
            except DistutilsExecError as msg:
                 ashiria LinkError(msg)
        isipokua:
            log.debug("skipping %s (up-to-date)", output_filename)

    eleza _copy_vcruntime(self, output_dir):
        vcruntime = self._vcruntime_redist
        ikiwa sio vcruntime ama sio os.path.isfile(vcruntime):
            return

        ikiwa os.path.basename(vcruntime).lower() kwenye _BUNDLED_DLLS:
            return

        log.debug('Copying "%s"', vcruntime)
        vcruntime = shutil.copy(vcruntime, output_dir)
        os.chmod(vcruntime, stat.S_IWRITE)

    eleza spawn(self, cmd):
        old_path = os.getenv('path')
        jaribu:
            os.environ['path'] = self._paths
            rudisha super().spawn(cmd)
        mwishowe:
            os.environ['path'] = old_path

    # -- Miscellaneous methods -----------------------------------------
    # These are all used by the 'gen_lib_options() function, in
    # ccompiler.py.

    eleza library_dir_option(self, dir):
        rudisha "/LIBPATH:" + dir

    eleza runtime_library_dir_option(self, dir):
         ashiria DistutilsPlatformError(
              "don't know how to set runtime library search path kila MSVC")

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
                libfile = os.path.join(dir, self.library_filename(name))
                ikiwa os.path.isfile(libfile):
                    rudisha libfile
        isipokua:
            # Oops, didn't find it kwenye *any* of 'dirs'
            rudisha Tupu
