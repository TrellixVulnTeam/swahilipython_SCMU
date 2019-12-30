# Autodetecting setup.py script kila building the Python extensions

agiza argparse
agiza importlib._bootstrap
agiza importlib.machinery
agiza importlib.util
agiza os
agiza re
agiza sys
agiza sysconfig
kutoka glob agiza glob

kutoka distutils agiza log
kutoka distutils.command.build_ext agiza build_ext
kutoka distutils.command.build_scripts agiza build_scripts
kutoka distutils.command.install agiza install
kutoka distutils.command.install_lib agiza install_lib
kutoka distutils.core agiza Extension, setup
kutoka distutils.errors agiza CCompilerError, DistutilsError
kutoka distutils.spawn agiza find_executable


# Compile extensions used to test Python?
TEST_EXTENSIONS = Kweli

# This global variable ni used to hold the list of modules to be disabled.
DISABLED_MODULE_LIST = []


eleza get_platform():
    # Cross compiling
    ikiwa "_PYTHON_HOST_PLATFORM" kwenye os.environ:
        rudisha os.environ["_PYTHON_HOST_PLATFORM"]

    # Get value of sys.platform
    ikiwa sys.platform.startswith('osf1'):
        rudisha 'osf1'
    rudisha sys.platform


CROSS_COMPILING = ("_PYTHON_HOST_PLATFORM" kwenye os.environ)
HOST_PLATFORM = get_platform()
MS_WINDOWS = (HOST_PLATFORM == 'win32')
CYGWIN = (HOST_PLATFORM == 'cygwin')
MACOS = (HOST_PLATFORM == 'darwin')
AIX = (HOST_PLATFORM.startswith('aix'))
VXWORKS = ('vxworks' kwenye HOST_PLATFORM)


SUMMARY = """
Python ni an interpreted, interactive, object-oriented programming
language. It ni often compared to Tcl, Perl, Scheme ama Java.

Python combines remarkable power ukijumuisha very clear syntax. It has
modules, classes, exceptions, very high level dynamic data types, na
dynamic typing. There are interfaces to many system calls na
libraries, kama well kama to various windowing systems (X11, Motif, Tk,
Mac, MFC). New built-in modules are easily written kwenye C ama C++. Python
is also usable kama an extension language kila applications that need a
programmable interface.

The Python implementation ni portable: it runs on many brands of UNIX,
on Windows, DOS, Mac, Amiga... If your favorite system isn't
listed here, it may still be supported, ikiwa there's a C compiler for
it. Ask around on comp.lang.python -- ama just try compiling Python
yourself.
"""

CLASSIFIERS = """
Development Status :: 6 - Mature
License :: OSI Approved :: Python Software Foundation License
Natural Language :: English
Programming Language :: C
Programming Language :: Python
Topic :: Software Development
"""


# Set common compiler na linker flags derived kutoka the Makefile,
# reserved kila building the interpreter na the stdlib modules.
# See bpo-21121 na bpo-35257
eleza set_compiler_flags(compiler_flags, compiler_py_flags_nodist):
    flags = sysconfig.get_config_var(compiler_flags)
    py_flags_nodist = sysconfig.get_config_var(compiler_py_flags_nodist)
    sysconfig.get_config_vars()[compiler_flags] = flags + ' ' + py_flags_nodist


eleza add_dir_to_list(dirlist, dir):
    """Add the directory 'dir' to the list 'dirlist' (after any relative
    directories) if:

    1) 'dir' ni sio already kwenye 'dirlist'
    2) 'dir' actually exists, na ni a directory.
    """
    ikiwa dir ni Tupu ama sio os.path.isdir(dir) ama dir kwenye dirlist:
        rudisha
    kila i, path kwenye enumerate(dirlist):
        ikiwa sio os.path.isabs(path):
            dirlist.insert(i + 1, dir)
            rudisha
    dirlist.insert(0, dir)


eleza sysroot_paths(make_vars, subdirs):
    """Get the paths of sysroot sub-directories.

    * make_vars: a sequence of names of variables of the Makefile where
      sysroot may be set.
    * subdirs: a sequence of names of subdirectories used kama the location for
      headers ama libraries.
    """

    dirs = []
    kila var_name kwenye make_vars:
        var = sysconfig.get_config_var(var_name)
        ikiwa var ni sio Tupu:
            m = re.search(r'--sysroot=([^"]\S*|"[^"]+")', var)
            ikiwa m ni sio Tupu:
                sysroot = m.group(1).strip('"')
                kila subdir kwenye subdirs:
                    ikiwa os.path.isabs(subdir):
                        subdir = subdir[1:]
                    path = os.path.join(sysroot, subdir)
                    ikiwa os.path.isdir(path):
                        dirs.append(path)
                koma
    rudisha dirs

MACOS_SDK_ROOT = Tupu

eleza macosx_sdk_root():
    """Return the directory of the current macOS SDK.

    If no SDK was explicitly configured, call the compiler to find which
    include files paths are being searched by default.  Use '/' ikiwa the
    compiler ni searching /usr/include (meaning system header files are
    installed) ama use the root of an SDK ikiwa that ni being searched.
    (The SDK may be supplied via Xcode ama via the Command Line Tools).
    The SDK paths used by Apple-supplied tool chains depend on the
    setting of various variables; see the xcrun man page kila more info.
    """
    global MACOS_SDK_ROOT

    # If already called, rudisha cached result.
    ikiwa MACOS_SDK_ROOT:
        rudisha MACOS_SDK_ROOT

    cflags = sysconfig.get_config_var('CFLAGS')
    m = re.search(r'-isysroot\s+(\S+)', cflags)
    ikiwa m ni sio Tupu:
        MACOS_SDK_ROOT = m.group(1)
    isipokua:
        MACOS_SDK_ROOT = '/'
        cc = sysconfig.get_config_var('CC')
        tmpfile = '/tmp/setup_sdk_root.%d' % os.getpid()
        jaribu:
            os.unlink(tmpfile)
        tatizo:
            pita
        ret = os.system('%s -E -v - </dev/null 2>%s 1>/dev/null' % (cc, tmpfile))
        in_incdirs = Uongo
        jaribu:
            ikiwa ret >> 8 == 0:
                ukijumuisha open(tmpfile) kama fp:
                    kila line kwenye fp.readlines():
                        ikiwa line.startswith("#include <...>"):
                            in_incdirs = Kweli
                        lasivyo line.startswith("End of search list"):
                            in_incdirs = Uongo
                        lasivyo in_incdirs:
                            line = line.strip()
                            ikiwa line == '/usr/include':
                                MACOS_SDK_ROOT = '/'
                            lasivyo line.endswith(".sdk/usr/include"):
                                MACOS_SDK_ROOT = line[:-12]
        mwishowe:
            os.unlink(tmpfile)

    rudisha MACOS_SDK_ROOT


eleza is_macosx_sdk_path(path):
    """
    Returns Kweli ikiwa 'path' can be located kwenye an OSX SDK
    """
    rudisha ( (path.startswith('/usr/') na sio path.startswith('/usr/local'))
                ama path.startswith('/System/')
                ama path.startswith('/Library/') )


eleza find_file(filename, std_dirs, paths):
    """Searches kila the directory where a given file ni located,
    na returns a possibly-empty list of additional directories, ama Tupu
    ikiwa the file couldn't be found at all.

    'filename' ni the name of a file, such kama readline.h ama libcrypto.a.
    'std_dirs' ni the list of standard system directories; ikiwa the
        file ni found kwenye one of them, no additional directives are needed.
    'paths' ni a list of additional locations to check; ikiwa the file is
        found kwenye one of them, the resulting list will contain the directory.
    """
    ikiwa MACOS:
        # Honor the MacOSX SDK setting when one was specified.
        # An SDK ni a directory ukijumuisha the same structure kama a real
        # system, but ukijumuisha only header files na libraries.
        sysroot = macosx_sdk_root()

    # Check the standard locations
    kila dir kwenye std_dirs:
        f = os.path.join(dir, filename)

        ikiwa MACOS na is_macosx_sdk_path(dir):
            f = os.path.join(sysroot, dir[1:], filename)

        ikiwa os.path.exists(f): rudisha []

    # Check the additional directories
    kila dir kwenye paths:
        f = os.path.join(dir, filename)

        ikiwa MACOS na is_macosx_sdk_path(dir):
            f = os.path.join(sysroot, dir[1:], filename)

        ikiwa os.path.exists(f):
            rudisha [dir]

    # Not found anywhere
    rudisha Tupu


eleza find_library_file(compiler, libname, std_dirs, paths):
    result = compiler.find_library_file(std_dirs + paths, libname)
    ikiwa result ni Tupu:
        rudisha Tupu

    ikiwa MACOS:
        sysroot = macosx_sdk_root()

    # Check whether the found file ni kwenye one of the standard directories
    dirname = os.path.dirname(result)
    kila p kwenye std_dirs:
        # Ensure path doesn't end ukijumuisha path separator
        p = p.rstrip(os.sep)

        ikiwa MACOS na is_macosx_sdk_path(p):
            # Note that, kama of Xcode 7, Apple SDKs may contain textual stub
            # libraries ukijumuisha .tbd extensions rather than the normal .dylib
            # shared libraries installed kwenye /.  The Apple compiler tool
            # chain handles this transparently but it can cause problems
            # kila programs that are being built ukijumuisha an SDK na searching
            # kila specific libraries.  Distutils find_library_file() now
            # knows to also search kila na rudisha .tbd files.  But callers
            # of find_library_file need to keep kwenye mind that the base filename
            # of the returned SDK library file might have a different extension
            # kutoka that of the library file installed on the running system,
            # kila example:
            #   /Applications/Xcode.app/Contents/Developer/Platforms/
            #       MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/
            #       usr/lib/libedit.tbd
            # vs
            #   /usr/lib/libedit.dylib
            ikiwa os.path.join(sysroot, p[1:]) == dirname:
                rudisha [ ]

        ikiwa p == dirname:
            rudisha [ ]

    # Otherwise, it must have been kwenye one of the additional directories,
    # so we have to figure out which one.
    kila p kwenye paths:
        # Ensure path doesn't end ukijumuisha path separator
        p = p.rstrip(os.sep)

        ikiwa MACOS na is_macosx_sdk_path(p):
            ikiwa os.path.join(sysroot, p[1:]) == dirname:
                rudisha [ p ]

        ikiwa p == dirname:
            rudisha [p]
    isipokua:
        assert Uongo, "Internal error: Path sio found kwenye std_dirs ama paths"


eleza find_module_file(module, dirlist):
    """Find a module kwenye a set of possible folders. If it ni sio found
    rudisha the unadorned filename"""
    list = find_file(module, [], dirlist)
    ikiwa sio list:
        rudisha module
    ikiwa len(list) > 1:
        log.info("WARNING: multiple copies of %s found", module)
    rudisha os.path.join(list[0], module)


kundi PyBuildExt(build_ext):

    eleza __init__(self, dist):
        build_ext.__init__(self, dist)
        self.srcdir = Tupu
        self.lib_dirs = Tupu
        self.inc_dirs = Tupu
        self.config_h_vars = Tupu
        self.failed = []
        self.failed_on_agiza = []
        self.missing = []
        ikiwa '-j' kwenye os.environ.get('MAKEFLAGS', ''):
            self.parallel = Kweli

    eleza add(self, ext):
        self.extensions.append(ext)

    eleza build_extensions(self):
        self.srcdir = sysconfig.get_config_var('srcdir')
        ikiwa sio self.srcdir:
            # Maybe running on Windows but sio using CYGWIN?
            ashiria ValueError("No source directory; cansio proceed.")
        self.srcdir = os.path.abspath(self.srcdir)

        # Detect which modules should be compiled
        self.detect_modules()

        # Remove modules that are present on the disabled list
        extensions = [ext kila ext kwenye self.extensions
                      ikiwa ext.name haiko kwenye DISABLED_MODULE_LIST]
        # move ctypes to the end, it depends on other modules
        ext_map = dict((ext.name, i) kila i, ext kwenye enumerate(extensions))
        ikiwa "_ctypes" kwenye ext_map:
            ctypes = extensions.pop(ext_map["_ctypes"])
            extensions.append(ctypes)
        self.extensions = extensions

        # Fix up the autodetected modules, prefixing all the source files
        # ukijumuisha Modules/.
        moddirlist = [os.path.join(self.srcdir, 'Modules')]

        # Fix up the paths kila scripts, too
        self.distribution.scripts = [os.path.join(self.srcdir, filename)
                                     kila filename kwenye self.distribution.scripts]

        # Python header files
        headers = [sysconfig.get_config_h_filename()]
        headers += glob(os.path.join(sysconfig.get_path('include'), "*.h"))

        # The sysconfig variables built by makesetup that list the already
        # built modules na the disabled modules kama configured by the Setup
        # files.
        sysconf_built = sysconfig.get_config_var('MODBUILT_NAMES').split()
        sysconf_dis = sysconfig.get_config_var('MODDISABLED_NAMES').split()

        mods_built = []
        mods_disabled = []
        kila ext kwenye self.extensions:
            ext.sources = [ find_module_file(filename, moddirlist)
                            kila filename kwenye ext.sources ]
            ikiwa ext.depends ni sio Tupu:
                ext.depends = [find_module_file(filename, moddirlist)
                               kila filename kwenye ext.depends]
            isipokua:
                ext.depends = []
            # re-compile extensions ikiwa a header file has been changed
            ext.depends.extend(headers)

            # If a module has already been built ama has been disabled kwenye the
            # Setup files, don't build it here.
            ikiwa ext.name kwenye sysconf_built:
                mods_built.append(ext)
            ikiwa ext.name kwenye sysconf_dis:
                mods_disabled.append(ext)

        mods_configured = mods_built + mods_disabled
        ikiwa mods_configured:
            self.extensions = [x kila x kwenye self.extensions ikiwa x haiko kwenye
                               mods_configured]
            # Remove the shared libraries built by a previous build.
            kila ext kwenye mods_configured:
                fullpath = self.get_ext_fullpath(ext.name)
                ikiwa os.path.exists(fullpath):
                    os.unlink(fullpath)

        # When you run "make CC=altcc" ama something similar, you really want
        # those environment variables pitaed into the setup.py phase.  Here's
        # a small set of useful ones.
        compiler = os.environ.get('CC')
        args = {}
        # unfortunately, distutils doesn't let us provide separate C na C++
        # compilers
        ikiwa compiler ni sio Tupu:
            (ccshared,cflags) = sysconfig.get_config_vars('CCSHARED','CFLAGS')
            args['compiler_so'] = compiler + ' ' + ccshared + ' ' + cflags
        self.compiler.set_executables(**args)

        build_ext.build_extensions(self)

        kila ext kwenye self.extensions:
            self.check_extension_import(ext)

        longest = max([len(e.name) kila e kwenye self.extensions], default=0)
        ikiwa self.failed ama self.failed_on_import:
            all_failed = self.failed + self.failed_on_import
            longest = max(longest, max([len(name) kila name kwenye all_failed]))

        eleza print_three_column(lst):
            lst.sort(key=str.lower)
            # guarantee zip() doesn't drop anything
            wakati len(lst) % 3:
                lst.append("")
            kila e, f, g kwenye zip(lst[::3], lst[1::3], lst[2::3]):
                andika("%-*s   %-*s   %-*s" % (longest, e, longest, f,
                                              longest, g))

        ikiwa self.missing:
            andika()
            andika("Python build finished successfully!")
            andika("The necessary bits to build these optional modules were sio "
                  "found:")
            print_three_column(self.missing)
            andika("To find the necessary bits, look kwenye setup.py in"
                  " detect_modules() kila the module's name.")
            andika()

        ikiwa mods_built:
            andika()
            andika("The following modules found by detect_modules() in"
            " setup.py, have been")
            andika("built by the Makefile instead, kama configured by the"
            " Setup files:")
            print_three_column([ext.name kila ext kwenye mods_built])
            andika()

        ikiwa mods_disabled:
            andika()
            andika("The following modules found by detect_modules() in"
            " setup.py have not")
            andika("been built, they are *disabled* kwenye the Setup files:")
            print_three_column([ext.name kila ext kwenye mods_disabled])
            andika()

        ikiwa self.failed:
            failed = self.failed[:]
            andika()
            andika("Failed to build these modules:")
            print_three_column(failed)
            andika()

        ikiwa self.failed_on_import:
            failed = self.failed_on_import[:]
            andika()
            andika("Following modules built successfully"
                  " but were removed because they could sio be imported:")
            print_three_column(failed)
            andika()

        ikiwa any('_ssl' kwenye l
               kila l kwenye (self.missing, self.failed, self.failed_on_import)):
            andika()
            andika("Could sio build the ssl module!")
            andika("Python requires an OpenSSL 1.0.2 ama 1.1 compatible "
                  "libssl ukijumuisha X509_VERIFY_PARAM_set1_host().")
            andika("LibreSSL 2.6.4 na earlier do sio provide the necessary "
                  "APIs, https://github.com/libressl-portable/portable/issues/381")
            andika()

    eleza build_extension(self, ext):

        ikiwa ext.name == '_ctypes':
            ikiwa sio self.configure_ctypes(ext):
                self.failed.append(ext.name)
                rudisha

        jaribu:
            build_ext.build_extension(self, ext)
        tatizo (CCompilerError, DistutilsError) kama why:
            self.announce('WARNING: building of extension "%s" failed: %s' %
                          (ext.name, why))
            self.failed.append(ext.name)
            rudisha

    eleza check_extension_import(self, ext):
        # Don't try to agiza an extension that has failed to compile
        ikiwa ext.name kwenye self.failed:
            self.announce(
                'WARNING: skipping agiza check kila failed build "%s"' %
                ext.name, level=1)
            rudisha

        # Workaround kila Mac OS X: The Carbon-based modules cansio be
        # reliably imported into a command-line Python
        ikiwa 'Carbon' kwenye ext.extra_link_args:
            self.announce(
                'WARNING: skipping agiza check kila Carbon-based "%s"' %
                ext.name)
            rudisha

        ikiwa MACOS na (
                sys.maxsize > 2**32 na '-arch' kwenye ext.extra_link_args):
            # Don't bother doing an agiza check when an extension was
            # build ukijumuisha an explicit '-arch' flag on OSX. That's currently
            # only used to build 32-bit only extensions kwenye a 4-way
            # universal build na loading 32-bit code into a 64-bit
            # process will fail.
            self.announce(
                'WARNING: skipping agiza check kila "%s"' %
                ext.name)
            rudisha

        # Workaround kila Cygwin: Cygwin currently has fork issues when many
        # modules have been imported
        ikiwa CYGWIN:
            self.announce('WARNING: skipping agiza check kila Cygwin-based "%s"'
                % ext.name)
            rudisha
        ext_filename = os.path.join(
            self.build_lib,
            self.get_ext_filename(self.get_ext_fullname(ext.name)))

        # If the build directory didn't exist when setup.py was
        # started, sys.path_importer_cache has a negative result
        # cached.  Clear that cache before trying to import.
        sys.path_importer_cache.clear()

        # Don't try to load extensions kila cross builds
        ikiwa CROSS_COMPILING:
            rudisha

        loader = importlib.machinery.ExtensionFileLoader(ext.name, ext_filename)
        spec = importlib.util.spec_from_file_location(ext.name, ext_filename,
                                                      loader=loader)
        jaribu:
            importlib._bootstrap._load(spec)
        tatizo ImportError kama why:
            self.failed_on_import.append(ext.name)
            self.announce('*** WARNING: renaming "%s" since importing it'
                          ' failed: %s' % (ext.name, why), level=3)
            assert sio self.inplace
            basename, tail = os.path.splitext(ext_filename)
            newname = basename + "_failed" + tail
            ikiwa os.path.exists(newname):
                os.remove(newname)
            os.rename(ext_filename, newname)

        tatizo:
            exc_type, why, tb = sys.exc_info()
            self.announce('*** WARNING: importing extension "%s" '
                          'failed ukijumuisha %s: %s' % (ext.name, exc_type, why),
                          level=3)
            self.failed.append(ext.name)

    eleza add_multiarch_paths(self):
        # Debian/Ubuntu multiarch support.
        # https://wiki.ubuntu.com/MultiarchSpec
        cc = sysconfig.get_config_var('CC')
        tmpfile = os.path.join(self.build_temp, 'multiarch')
        ikiwa sio os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        ret = os.system(
            '%s -print-multiarch > %s 2> /dev/null' % (cc, tmpfile))
        multiarch_path_component = ''
        jaribu:
            ikiwa ret >> 8 == 0:
                ukijumuisha open(tmpfile) kama fp:
                    multiarch_path_component = fp.readline().strip()
        mwishowe:
            os.unlink(tmpfile)

        ikiwa multiarch_path_component != '':
            add_dir_to_list(self.compiler.library_dirs,
                            '/usr/lib/' + multiarch_path_component)
            add_dir_to_list(self.compiler.include_dirs,
                            '/usr/include/' + multiarch_path_component)
            rudisha

        ikiwa sio find_executable('dpkg-architecture'):
            rudisha
        opt = ''
        ikiwa CROSS_COMPILING:
            opt = '-t' + sysconfig.get_config_var('HOST_GNU_TYPE')
        tmpfile = os.path.join(self.build_temp, 'multiarch')
        ikiwa sio os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        ret = os.system(
            'dpkg-architecture %s -qDEB_HOST_MULTIARCH > %s 2> /dev/null' %
            (opt, tmpfile))
        jaribu:
            ikiwa ret >> 8 == 0:
                ukijumuisha open(tmpfile) kama fp:
                    multiarch_path_component = fp.readline().strip()
                add_dir_to_list(self.compiler.library_dirs,
                                '/usr/lib/' + multiarch_path_component)
                add_dir_to_list(self.compiler.include_dirs,
                                '/usr/include/' + multiarch_path_component)
        mwishowe:
            os.unlink(tmpfile)

    eleza add_cross_compiling_paths(self):
        cc = sysconfig.get_config_var('CC')
        tmpfile = os.path.join(self.build_temp, 'ccpaths')
        ikiwa sio os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        ret = os.system('%s -E -v - </dev/null 2>%s 1>/dev/null' % (cc, tmpfile))
        is_gcc = Uongo
        is_clang = Uongo
        in_incdirs = Uongo
        jaribu:
            ikiwa ret >> 8 == 0:
                ukijumuisha open(tmpfile) kama fp:
                    kila line kwenye fp.readlines():
                        ikiwa line.startswith("gcc version"):
                            is_gcc = Kweli
                        lasivyo line.startswith("clang version"):
                            is_clang = Kweli
                        lasivyo line.startswith("#include <...>"):
                            in_incdirs = Kweli
                        lasivyo line.startswith("End of search list"):
                            in_incdirs = Uongo
                        lasivyo (is_gcc ama is_clang) na line.startswith("LIBRARY_PATH"):
                            kila d kwenye line.strip().split("=")[1].split(":"):
                                d = os.path.normpath(d)
                                ikiwa '/gcc/' haiko kwenye d:
                                    add_dir_to_list(self.compiler.library_dirs,
                                                    d)
                        lasivyo (is_gcc ama is_clang) na in_incdirs na '/gcc/' haiko kwenye line na '/clang/' haiko kwenye line:
                            add_dir_to_list(self.compiler.include_dirs,
                                            line.strip())
        mwishowe:
            os.unlink(tmpfile)

    eleza add_ldflags_cppflags(self):
        # Add paths specified kwenye the environment variables LDFLAGS na
        # CPPFLAGS kila header na library files.
        # We must get the values kutoka the Makefile na sio the environment
        # directly since an inconsistently reproducible issue comes up where
        # the environment variable ni sio set even though the value were pitaed
        # into configure na stored kwenye the Makefile (issue found on OS X 10.3).
        kila env_var, arg_name, dir_list kwenye (
                ('LDFLAGS', '-R', self.compiler.runtime_library_dirs),
                ('LDFLAGS', '-L', self.compiler.library_dirs),
                ('CPPFLAGS', '-I', self.compiler.include_dirs)):
            env_val = sysconfig.get_config_var(env_var)
            ikiwa env_val:
                parser = argparse.ArgumentParser()
                parser.add_argument(arg_name, dest="dirs", action="append")
                options, _ = parser.parse_known_args(env_val.split())
                ikiwa options.dirs:
                    kila directory kwenye reversed(options.dirs):
                        add_dir_to_list(dir_list, directory)

    eleza configure_compiler(self):
        # Ensure that /usr/local ni always used, but the local build
        # directories (i.e. '.' na 'Include') must be first.  See issue
        # 10520.
        ikiwa sio CROSS_COMPILING:
            add_dir_to_list(self.compiler.library_dirs, '/usr/local/lib')
            add_dir_to_list(self.compiler.include_dirs, '/usr/local/include')
        # only change this kila cross builds kila 3.3, issues on Mageia
        ikiwa CROSS_COMPILING:
            self.add_cross_compiling_paths()
        self.add_multiarch_paths()
        self.add_ldflags_cppflags()

    eleza init_inc_lib_dirs(self):
        ikiwa (sio CROSS_COMPILING na
                os.path.normpath(sys.base_prefix) != '/usr' na
                sio sysconfig.get_config_var('PYTHONFRAMEWORK')):
            # OSX note: Don't add LIBDIR na INCLUDEDIR to building a framework
            # (PYTHONFRAMEWORK ni set) to avoid # linking problems when
            # building a framework ukijumuisha different architectures than
            # the one that ni currently installed (issue #7473)
            add_dir_to_list(self.compiler.library_dirs,
                            sysconfig.get_config_var("LIBDIR"))
            add_dir_to_list(self.compiler.include_dirs,
                            sysconfig.get_config_var("INCLUDEDIR"))

        system_lib_dirs = ['/lib64', '/usr/lib64', '/lib', '/usr/lib']
        system_include_dirs = ['/usr/include']
        # lib_dirs na inc_dirs are used to search kila files;
        # ikiwa a file ni found kwenye one of those directories, it can
        # be assumed that no additional -I,-L directives are needed.
        ikiwa sio CROSS_COMPILING:
            self.lib_dirs = self.compiler.library_dirs + system_lib_dirs
            self.inc_dirs = self.compiler.include_dirs + system_include_dirs
        isipokua:
            # Add the sysroot paths. 'sysroot' ni a compiler option used to
            # set the logical path of the standard system headers na
            # libraries.
            self.lib_dirs = (self.compiler.library_dirs +
                             sysroot_paths(('LDFLAGS', 'CC'), system_lib_dirs))
            self.inc_dirs = (self.compiler.include_dirs +
                             sysroot_paths(('CPPFLAGS', 'CFLAGS', 'CC'),
                                           system_include_dirs))

        config_h = sysconfig.get_config_h_filename()
        ukijumuisha open(config_h) kama file:
            self.config_h_vars = sysconfig.parse_config_h(file)

        # OSF/1 na Unixware have some stuff kwenye /usr/ccs/lib (like -ldb)
        ikiwa HOST_PLATFORM kwenye ['osf1', 'unixware7', 'openunix8']:
            self.lib_dirs += ['/usr/ccs/lib']

        # HP-UX11iv3 keeps files kwenye lib/hpux folders.
        ikiwa HOST_PLATFORM == 'hp-ux11':
            self.lib_dirs += ['/usr/lib/hpux64', '/usr/lib/hpux32']

        ikiwa MACOS:
            # This should work on any unixy platform ;-)
            # If the user has bothered specifying additional -I na -L flags
            # kwenye OPT na LDFLAGS we might kama well use them here.
            #
            # NOTE: using shlex.split would technically be more correct, but
            # also gives a bootstrap problem. Let's hope nobody uses
            # directories ukijumuisha whitespace kwenye the name to store libraries.
            cflags, ldflags = sysconfig.get_config_vars(
                    'CFLAGS', 'LDFLAGS')
            kila item kwenye cflags.split():
                ikiwa item.startswith('-I'):
                    self.inc_dirs.append(item[2:])

            kila item kwenye ldflags.split():
                ikiwa item.startswith('-L'):
                    self.lib_dirs.append(item[2:])

    eleza detect_simple_extensions(self):
        #
        # The following modules are all pretty straightforward, na compile
        # on pretty much any POSIXish platform.
        #

        # array objects
        self.add(Extension('array', ['arraymodule.c']))

        # Context Variables
        self.add(Extension('_contextvars', ['_contextvarsmodule.c']))

        shared_math = 'Modules/_math.o'

        # math library functions, e.g. sin()
        self.add(Extension('math',  ['mathmodule.c'],
                           extra_objects=[shared_math],
                           depends=['_math.h', shared_math],
                           libraries=['m']))

        # complex math library functions
        self.add(Extension('cmath', ['cmathmodule.c'],
                           extra_objects=[shared_math],
                           depends=['_math.h', shared_math],
                           libraries=['m']))

        # time libraries: librt may be needed kila clock_gettime()
        time_libs = []
        lib = sysconfig.get_config_var('TIMEMODULE_LIB')
        ikiwa lib:
            time_libs.append(lib)

        # time operations na variables
        self.add(Extension('time', ['timemodule.c'],
                           libraries=time_libs))
        # libm ni needed by delta_new() that uses round() na by accum() that
        # uses modf().
        self.add(Extension('_datetime', ['_datetimemodule.c'],
                           libraries=['m']))
        # random number generator implemented kwenye C
        self.add(Extension("_random", ["_randommodule.c"]))
        # bisect
        self.add(Extension("_bisect", ["_bisectmodule.c"]))
        # heapq
        self.add(Extension("_heapq", ["_heapqmodule.c"]))
        # C-optimized pickle replacement
        self.add(Extension("_pickle", ["_pickle.c"],
                           extra_compile_args=['-DPy_BUILD_CORE_MODULE']))
        # atexit
        self.add(Extension("atexit", ["atexitmodule.c"]))
        # _json speedups
        self.add(Extension("_json", ["_json.c"],
                           extra_compile_args=['-DPy_BUILD_CORE_MODULE']))

        # profiler (_lsprof ni kila cProfile.py)
        self.add(Extension('_lsprof', ['_lsprof.c', 'rotatingtree.c']))
        # static Unicode character database
        self.add(Extension('unicodedata', ['unicodedata.c'],
                           depends=['unicodedata_db.h', 'unicodename_db.h']))
        # _opcode module
        self.add(Extension('_opcode', ['_opcode.c']))
        # asyncio speedups
        self.add(Extension("_asyncio", ["_asynciomodule.c"]))
        # _abc speedups
        self.add(Extension("_abc", ["_abc.c"]))
        # _queue module
        self.add(Extension("_queue", ["_queuemodule.c"]))
        # _statistics module
        self.add(Extension("_statistics", ["_statisticsmodule.c"]))

        # Modules ukijumuisha some UNIX dependencies -- on by default:
        # (If you have a really backward UNIX, select na socket may sio be
        # supported...)

        # fcntl(2) na ioctl(2)
        libs = []
        ikiwa (self.config_h_vars.get('FLOCK_NEEDS_LIBBSD', Uongo)):
            # May be necessary on AIX kila flock function
            libs = ['bsd']
        self.add(Extension('fcntl', ['fcntlmodule.c'],
                           libraries=libs))
        # pwd(3)
        self.add(Extension('pwd', ['pwdmodule.c']))
        # grp(3)
        ikiwa sio VXWORKS:
            self.add(Extension('grp', ['grpmodule.c']))
        # spwd, shadow pitawords
        ikiwa (self.config_h_vars.get('HAVE_GETSPNAM', Uongo) ama
                self.config_h_vars.get('HAVE_GETSPENT', Uongo)):
            self.add(Extension('spwd', ['spwdmodule.c']))
        # AIX has shadow pitawords, but access ni sio via getspent(), etc.
        # module support ni sio expected so it sio 'missing'
        lasivyo sio AIX:
            self.missing.append('spwd')

        # select(2); sio on ancient System V
        self.add(Extension('select', ['selectmodule.c']))

        # Fred Drake's interface to the Python parser
        self.add(Extension('parser', ['parsermodule.c']))

        # Memory-mapped files (also works on Win32).
        self.add(Extension('mmap', ['mmapmodule.c']))

        # Lance Ellinghaus's syslog module
        # syslog daemon interface
        self.add(Extension('syslog', ['syslogmodule.c']))

        # Python interface to subinterpreter C-API.
        self.add(Extension('_xxsubinterpreters', ['_xxsubinterpretersmodule.c']))

        #
        # Here ends the simple stuff.  From here on, modules need certain
        # libraries, are platform-specific, ama present other surprises.
        #

        # Multimedia modules
        # These don't work kila 64-bit platforms!!!
        # These represent audio samples ama images kama strings:
        #
        # Operations on audio samples
        # According to #993173, this one should actually work fine on
        # 64-bit platforms.
        #
        # audioop needs libm kila floor() kwenye multiple functions.
        self.add(Extension('audioop', ['audioop.c'],
                           libraries=['m']))

        # CSV files
        self.add(Extension('_csv', ['_csv.c']))

        # POSIX subprocess module helper.
        self.add(Extension('_posixsubprocess', ['_posixsubprocess.c']))

    eleza detect_test_extensions(self):
        # Python C API test module
        self.add(Extension('_testcapi', ['_testcapimodule.c'],
                           depends=['testcapi_long.h']))

        # Python Internal C API test module
        self.add(Extension('_testinternalcapi', ['_testinternalcapi.c'],
                           extra_compile_args=['-DPy_BUILD_CORE_MODULE']))

        # Python PEP-3118 (buffer protocol) test module
        self.add(Extension('_testbuffer', ['_testbuffer.c']))

        # Test loading multiple modules kutoka one compiled file (http://bugs.python.org/issue16421)
        self.add(Extension('_testimportmultiple', ['_testimportmultiple.c']))

        # Test multi-phase extension module init (PEP 489)
        self.add(Extension('_testmultiphase', ['_testmultiphase.c']))

        # Fuzz tests.
        self.add(Extension('_xxtestfuzz',
                           ['_xxtestfuzz/_xxtestfuzz.c',
                            '_xxtestfuzz/fuzzer.c']))

    eleza detect_readline_curses(self):
        # readline
        do_readline = self.compiler.find_library_file(self.lib_dirs, 'readline')
        readline_termcap_library = ""
        curses_library = ""
        # Cansio use os.popen here kwenye py3k.
        tmpfile = os.path.join(self.build_temp, 'readline_termcap_lib')
        ikiwa sio os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        # Determine ikiwa readline ni already linked against curses ama tinfo.
        ikiwa do_readline:
            ikiwa CROSS_COMPILING:
                ret = os.system("%s -d %s | grep '(NEEDED)' > %s" \
                                % (sysconfig.get_config_var('READELF'),
                                   do_readline, tmpfile))
            lasivyo find_executable('ldd'):
                ret = os.system("ldd %s > %s" % (do_readline, tmpfile))
            isipokua:
                ret = 256
            ikiwa ret >> 8 == 0:
                ukijumuisha open(tmpfile) kama fp:
                    kila ln kwenye fp:
                        ikiwa 'curses' kwenye ln:
                            readline_termcap_library = re.sub(
                                r'.*lib(n?cursesw?)\.so.*', r'\1', ln
                            ).rstrip()
                            koma
                        # termcap interface split out kutoka ncurses
                        ikiwa 'tinfo' kwenye ln:
                            readline_termcap_library = 'tinfo'
                            koma
            ikiwa os.path.exists(tmpfile):
                os.unlink(tmpfile)
        # Issue 7384: If readline ni already linked against curses,
        # use the same library kila the readline na curses modules.
        ikiwa 'curses' kwenye readline_termcap_library:
            curses_library = readline_termcap_library
        lasivyo self.compiler.find_library_file(self.lib_dirs, 'ncursesw'):
            curses_library = 'ncursesw'
        # Issue 36210: OSS provided ncurses does sio link on AIX
        # Use IBM supplied 'curses' kila successful build of _curses
        lasivyo AIX na self.compiler.find_library_file(self.lib_dirs, 'curses'):
            curses_library = 'curses'
        lasivyo self.compiler.find_library_file(self.lib_dirs, 'ncurses'):
            curses_library = 'ncurses'
        lasivyo self.compiler.find_library_file(self.lib_dirs, 'curses'):
            curses_library = 'curses'

        ikiwa MACOS:
            os_release = int(os.uname()[2].split('.')[0])
            dep_target = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET')
            ikiwa (dep_target na
                    (tuple(int(n) kila n kwenye dep_target.split('.')[0:2])
                        < (10, 5) ) ):
                os_release = 8
            ikiwa os_release < 9:
                # MacOSX 10.4 has a broken readline. Don't try to build
                # the readline module unless the user has installed a fixed
                # readline package
                ikiwa find_file('readline/rlconf.h', self.inc_dirs, []) ni Tupu:
                    do_readline = Uongo
        ikiwa do_readline:
            ikiwa MACOS na os_release < 9:
                # In every directory on the search path search kila a dynamic
                # library na then a static library, instead of first looking
                # kila dynamic libraries on the entire path.
                # This way a statically linked custom readline gets picked up
                # before the (possibly broken) dynamic library kwenye /usr/lib.
                readline_extra_link_args = ('-Wl,-search_paths_first',)
            isipokua:
                readline_extra_link_args = ()

            readline_libs = ['readline']
            ikiwa readline_termcap_library:
                pita # Issue 7384: Already linked against curses ama tinfo.
            lasivyo curses_library:
                readline_libs.append(curses_library)
            lasivyo self.compiler.find_library_file(self.lib_dirs +
                                                     ['/usr/lib/termcap'],
                                                     'termcap'):
                readline_libs.append('termcap')
            self.add(Extension('readline', ['readline.c'],
                               library_dirs=['/usr/lib/termcap'],
                               extra_link_args=readline_extra_link_args,
                               libraries=readline_libs))
        isipokua:
            self.missing.append('readline')

        # Curses support, requiring the System V version of curses, often
        # provided by the ncurses library.
        curses_defines = []
        curses_includes = []
        panel_library = 'panel'
        ikiwa curses_library == 'ncursesw':
            curses_defines.append(('HAVE_NCURSESW', '1'))
            ikiwa sio CROSS_COMPILING:
                curses_includes.append('/usr/include/ncursesw')
            # Bug 1464056: If _curses.so links ukijumuisha ncursesw,
            # _curses_panel.so must link ukijumuisha panelw.
            panel_library = 'panelw'
            ikiwa MACOS:
                # On OS X, there ni no separate /usr/lib/libncursesw nor
                # libpanelw.  If we are here, we found a locally-supplied
                # version of libncursesw.  There should also be a
                # libpanelw.  _XOPEN_SOURCE defines are usually excluded
                # kila OS X but we need _XOPEN_SOURCE_EXTENDED here for
                # ncurses wide char support
                curses_defines.append(('_XOPEN_SOURCE_EXTENDED', '1'))
        lasivyo MACOS na curses_library == 'ncurses':
            # Building ukijumuisha the system-suppied combined libncurses/libpanel
            curses_defines.append(('HAVE_NCURSESW', '1'))
            curses_defines.append(('_XOPEN_SOURCE_EXTENDED', '1'))

        curses_enabled = Kweli
        ikiwa curses_library.startswith('ncurses'):
            curses_libs = [curses_library]
            self.add(Extension('_curses', ['_cursesmodule.c'],
                               include_dirs=curses_includes,
                               define_macros=curses_defines,
                               libraries=curses_libs))
        lasivyo curses_library == 'curses' na sio MACOS:
                # OSX has an old Berkeley curses, sio good enough for
                # the _curses module.
            ikiwa (self.compiler.find_library_file(self.lib_dirs, 'terminfo')):
                curses_libs = ['curses', 'terminfo']
            lasivyo (self.compiler.find_library_file(self.lib_dirs, 'termcap')):
                curses_libs = ['curses', 'termcap']
            isipokua:
                curses_libs = ['curses']

            self.add(Extension('_curses', ['_cursesmodule.c'],
                               define_macros=curses_defines,
                               libraries=curses_libs))
        isipokua:
            curses_enabled = Uongo
            self.missing.append('_curses')

        # If the curses module ni enabled, check kila the panel module
        # _curses_panel needs some form of ncurses
        skip_curses_panel = Kweli ikiwa AIX isipokua Uongo
        ikiwa (curses_enabled na sio skip_curses_panel na
                self.compiler.find_library_file(self.lib_dirs, panel_library)):
            self.add(Extension('_curses_panel', ['_curses_panel.c'],
                               include_dirs=curses_includes,
                               define_macros=curses_defines,
                               libraries=[panel_library, *curses_libs]))
        lasivyo sio skip_curses_panel:
            self.missing.append('_curses_panel')

    eleza detect_crypt(self):
        # crypt module.
        ikiwa VXWORKS:
            # bpo-31904: crypt() function ni sio provided by VxWorks.
            # DES_crypt() OpenSSL provides ni too weak to implement
            # the encryption.
            rudisha

        ikiwa self.compiler.find_library_file(self.lib_dirs, 'crypt'):
            libs = ['crypt']
        isipokua:
            libs = []

        self.add(Extension('_crypt', ['_cryptmodule.c'],
                               libraries=libs))

    eleza detect_socket(self):
        # socket(2)
        ikiwa sio VXWORKS:
            self.add(Extension('_socket', ['socketmodule.c'],
                               depends=['socketmodule.h']))
        lasivyo self.compiler.find_library_file(self.lib_dirs, 'net'):
            libs = ['net']
            self.add(Extension('_socket', ['socketmodule.c'],
                               depends=['socketmodule.h'],
                               libraries=libs))

    eleza detect_dbm_gdbm(self):
        # Modules that provide persistent dictionary-like semantics.  You will
        # probably want to arrange kila at least one of them to be available on
        # your machine, though none are defined by default because of library
        # dependencies.  The Python module dbm/__init__.py provides an
        # implementation independent wrapper kila these; dbm/dumb.py provides
        # similar functionality (but slower of course) implemented kwenye Python.

        # Sleepycat^WOracle Berkeley DB interface.
        #  http://www.oracle.com/database/berkeley-db/db/index.html
        #
        # This requires the Sleepycat^WOracle DB code. The supported versions
        # are set below.  Visit the URL above to download
        # a release.  Most open source OSes come ukijumuisha one ama more
        # versions of BerkeleyDB already installed.

        max_db_ver = (5, 3)
        min_db_ver = (3, 3)
        db_setup_debug = Uongo   # verbose debug prints kutoka this script?

        eleza allow_db_ver(db_ver):
            """Returns a boolean ikiwa the given BerkeleyDB version ni acceptable.

            Args:
              db_ver: A tuple of the version to verify.
            """
            ikiwa sio (min_db_ver <= db_ver <= max_db_ver):
                rudisha Uongo
            rudisha Kweli

        eleza gen_db_minor_ver_nums(major):
            ikiwa major == 4:
                kila x kwenye range(max_db_ver[1]+1):
                    ikiwa allow_db_ver((4, x)):
                        tuma x
            lasivyo major == 3:
                kila x kwenye (3,):
                    ikiwa allow_db_ver((3, x)):
                        tuma x
            isipokua:
                ashiria ValueError("unknown major BerkeleyDB version", major)

        # construct a list of paths to look kila the header file kwenye on
        # top of the normal inc_dirs.
        db_inc_paths = [
            '/usr/include/db4',
            '/usr/local/include/db4',
            '/opt/sfw/include/db4',
            '/usr/include/db3',
            '/usr/local/include/db3',
            '/opt/sfw/include/db3',
            # Fink defaults (http://fink.sourceforge.net/)
            '/sw/include/db4',
            '/sw/include/db3',
        ]
        # 4.x minor number specific paths
        kila x kwenye gen_db_minor_ver_nums(4):
            db_inc_paths.append('/usr/include/db4%d' % x)
            db_inc_paths.append('/usr/include/db4.%d' % x)
            db_inc_paths.append('/usr/local/BerkeleyDB.4.%d/include' % x)
            db_inc_paths.append('/usr/local/include/db4%d' % x)
            db_inc_paths.append('/pkg/db-4.%d/include' % x)
            db_inc_paths.append('/opt/db-4.%d/include' % x)
            # MacPorts default (http://www.macports.org/)
            db_inc_paths.append('/opt/local/include/db4%d' % x)
        # 3.x minor number specific paths
        kila x kwenye gen_db_minor_ver_nums(3):
            db_inc_paths.append('/usr/include/db3%d' % x)
            db_inc_paths.append('/usr/local/BerkeleyDB.3.%d/include' % x)
            db_inc_paths.append('/usr/local/include/db3%d' % x)
            db_inc_paths.append('/pkg/db-3.%d/include' % x)
            db_inc_paths.append('/opt/db-3.%d/include' % x)

        ikiwa CROSS_COMPILING:
            db_inc_paths = []

        # Add some common subdirectories kila Sleepycat DB to the list,
        # based on the standard include directories. This way DB3/4 gets
        # picked up when it ni installed kwenye a non-standard prefix na
        # the user has added that prefix into inc_dirs.
        std_variants = []
        kila dn kwenye self.inc_dirs:
            std_variants.append(os.path.join(dn, 'db3'))
            std_variants.append(os.path.join(dn, 'db4'))
            kila x kwenye gen_db_minor_ver_nums(4):
                std_variants.append(os.path.join(dn, "db4%d"%x))
                std_variants.append(os.path.join(dn, "db4.%d"%x))
            kila x kwenye gen_db_minor_ver_nums(3):
                std_variants.append(os.path.join(dn, "db3%d"%x))
                std_variants.append(os.path.join(dn, "db3.%d"%x))

        db_inc_paths = std_variants + db_inc_paths
        db_inc_paths = [p kila p kwenye db_inc_paths ikiwa os.path.exists(p)]

        db_ver_inc_map = {}

        ikiwa MACOS:
            sysroot = macosx_sdk_root()

        kundi db_found(Exception): pita
        jaribu:
            # See whether there ni a Sleepycat header kwenye the standard
            # search path.
            kila d kwenye self.inc_dirs + db_inc_paths:
                f = os.path.join(d, "db.h")
                ikiwa MACOS na is_macosx_sdk_path(d):
                    f = os.path.join(sysroot, d[1:], "db.h")

                ikiwa db_setup_debug: andika("db: looking kila db.h in", f)
                ikiwa os.path.exists(f):
                    ukijumuisha open(f, 'rb') kama file:
                        f = file.read()
                    m = re.search(br"#define\WDB_VERSION_MAJOR\W(\d+)", f)
                    ikiwa m:
                        db_major = int(m.group(1))
                        m = re.search(br"#define\WDB_VERSION_MINOR\W(\d+)", f)
                        db_minor = int(m.group(1))
                        db_ver = (db_major, db_minor)

                        # Avoid 4.6 prior to 4.6.21 due to a BerkeleyDB bug
                        ikiwa db_ver == (4, 6):
                            m = re.search(br"#define\WDB_VERSION_PATCH\W(\d+)", f)
                            db_patch = int(m.group(1))
                            ikiwa db_patch < 21:
                                andika("db.h:", db_ver, "patch", db_patch,
                                      "being ignored (4.6.x must be >= 4.6.21)")
                                endelea

                        ikiwa ( (db_ver haiko kwenye db_ver_inc_map) na
                            allow_db_ver(db_ver) ):
                            # save the include directory ukijumuisha the db.h version
                            # (first occurrence only)
                            db_ver_inc_map[db_ver] = d
                            ikiwa db_setup_debug:
                                andika("db.h: found", db_ver, "in", d)
                        isipokua:
                            # we already found a header kila this library version
                            ikiwa db_setup_debug: andika("db.h: ignoring", d)
                    isipokua:
                        # ignore this header, it didn't contain a version number
                        ikiwa db_setup_debug:
                            andika("db.h: no version number version in", d)

            db_found_vers = list(db_ver_inc_map.keys())
            db_found_vers.sort()

            wakati db_found_vers:
                db_ver = db_found_vers.pop()
                db_incdir = db_ver_inc_map[db_ver]

                # check lib directories parallel to the location of the header
                db_dirs_to_check = [
                    db_incdir.replace("include", 'lib64'),
                    db_incdir.replace("include", 'lib'),
                ]

                ikiwa sio MACOS:
                    db_dirs_to_check = list(filter(os.path.isdir, db_dirs_to_check))

                isipokua:
                    # Same kama other branch, but takes OSX SDK into account
                    tmp = []
                    kila dn kwenye db_dirs_to_check:
                        ikiwa is_macosx_sdk_path(dn):
                            ikiwa os.path.isdir(os.path.join(sysroot, dn[1:])):
                                tmp.append(dn)
                        isipokua:
                            ikiwa os.path.isdir(dn):
                                tmp.append(dn)
                    db_dirs_to_check = tmp

                    db_dirs_to_check = tmp

                # Look kila a version specific db-X.Y before an ambiguous dbX
                # XXX should we -ever- look kila a dbX name?  Do any
                # systems really sio name their library by version na
                # symlink to more general names?
                kila dblib kwenye (('db-%d.%d' % db_ver),
                              ('db%d%d' % db_ver),
                              ('db%d' % db_ver[0])):
                    dblib_file = self.compiler.find_library_file(
                                    db_dirs_to_check + self.lib_dirs, dblib )
                    ikiwa dblib_file:
                        dblib_dir = [ os.path.abspath(os.path.dirname(dblib_file)) ]
                        ashiria db_found
                    isipokua:
                        ikiwa db_setup_debug: andika("db lib: ", dblib, "sio found")

        tatizo db_found:
            ikiwa db_setup_debug:
                andika("bsddb using BerkeleyDB lib:", db_ver, dblib)
                andika("bsddb lib dir:", dblib_dir, " inc dir:", db_incdir)
            dblibs = [dblib]
            # Only add the found library na include directories ikiwa they aren't
            # already being searched. This avoids an explicit runtime library
            # dependency.
            ikiwa db_incdir kwenye self.inc_dirs:
                db_incs = Tupu
            isipokua:
                db_incs = [db_incdir]
            ikiwa dblib_dir[0] kwenye self.lib_dirs:
                dblib_dir = Tupu
        isipokua:
            ikiwa db_setup_debug: andika("db: no appropriate library found")
            db_incs = Tupu
            dblibs = []
            dblib_dir = Tupu

        dbm_setup_debug = Uongo   # verbose debug prints kutoka this script?
        dbm_order = ['gdbm']
        # The standard Unix dbm module:
        ikiwa sio CYGWIN:
            config_args = [arg.strip("'")
                           kila arg kwenye sysconfig.get_config_var("CONFIG_ARGS").split()]
            dbm_args = [arg kila arg kwenye config_args
                        ikiwa arg.startswith('--with-dbmliborder=')]
            ikiwa dbm_args:
                dbm_order = [arg.split('=')[-1] kila arg kwenye dbm_args][-1].split(":")
            isipokua:
                dbm_order = "ndbm:gdbm:bdb".split(":")
            dbmext = Tupu
            kila cand kwenye dbm_order:
                ikiwa cand == "ndbm":
                    ikiwa find_file("ndbm.h", self.inc_dirs, []) ni sio Tupu:
                        # Some systems have -lndbm, others have -lgdbm_compat,
                        # others don't have either
                        ikiwa self.compiler.find_library_file(self.lib_dirs,
                                                               'ndbm'):
                            ndbm_libs = ['ndbm']
                        lasivyo self.compiler.find_library_file(self.lib_dirs,
                                                             'gdbm_compat'):
                            ndbm_libs = ['gdbm_compat']
                        isipokua:
                            ndbm_libs = []
                        ikiwa dbm_setup_debug: andika("building dbm using ndbm")
                        dbmext = Extension('_dbm', ['_dbmmodule.c'],
                                           define_macros=[
                                               ('HAVE_NDBM_H',Tupu),
                                               ],
                                           libraries=ndbm_libs)
                        koma

                lasivyo cand == "gdbm":
                    ikiwa self.compiler.find_library_file(self.lib_dirs, 'gdbm'):
                        gdbm_libs = ['gdbm']
                        ikiwa self.compiler.find_library_file(self.lib_dirs,
                                                               'gdbm_compat'):
                            gdbm_libs.append('gdbm_compat')
                        ikiwa find_file("gdbm/ndbm.h", self.inc_dirs, []) ni sio Tupu:
                            ikiwa dbm_setup_debug: andika("building dbm using gdbm")
                            dbmext = Extension(
                                '_dbm', ['_dbmmodule.c'],
                                define_macros=[
                                    ('HAVE_GDBM_NDBM_H', Tupu),
                                    ],
                                libraries = gdbm_libs)
                            koma
                        ikiwa find_file("gdbm-ndbm.h", self.inc_dirs, []) ni sio Tupu:
                            ikiwa dbm_setup_debug: andika("building dbm using gdbm")
                            dbmext = Extension(
                                '_dbm', ['_dbmmodule.c'],
                                define_macros=[
                                    ('HAVE_GDBM_DASH_NDBM_H', Tupu),
                                    ],
                                libraries = gdbm_libs)
                            koma
                lasivyo cand == "bdb":
                    ikiwa dblibs:
                        ikiwa dbm_setup_debug: andika("building dbm using bdb")
                        dbmext = Extension('_dbm', ['_dbmmodule.c'],
                                           library_dirs=dblib_dir,
                                           runtime_library_dirs=dblib_dir,
                                           include_dirs=db_incs,
                                           define_macros=[
                                               ('HAVE_BERKDB_H', Tupu),
                                               ('DB_DBM_HSEARCH', Tupu),
                                               ],
                                           libraries=dblibs)
                        koma
            ikiwa dbmext ni sio Tupu:
                self.add(dbmext)
            isipokua:
                self.missing.append('_dbm')

        # Anthony Baxter's gdbm module.  GNU dbm(3) will require -lgdbm:
        ikiwa ('gdbm' kwenye dbm_order na
            self.compiler.find_library_file(self.lib_dirs, 'gdbm')):
            self.add(Extension('_gdbm', ['_gdbmmodule.c'],
                               libraries=['gdbm']))
        isipokua:
            self.missing.append('_gdbm')

    eleza detect_sqlite(self):
        # The sqlite interface
        sqlite_setup_debug = Uongo   # verbose debug prints kutoka this script?

        # We hunt kila #define SQLITE_VERSION "n.n.n"
        # We need to find >= sqlite version 3.3.9, kila sqlite3_prepare_v2
        sqlite_incdir = sqlite_libdir = Tupu
        sqlite_inc_paths = [ '/usr/include',
                             '/usr/include/sqlite',
                             '/usr/include/sqlite3',
                             '/usr/local/include',
                             '/usr/local/include/sqlite',
                             '/usr/local/include/sqlite3',
                             ]
        ikiwa CROSS_COMPILING:
            sqlite_inc_paths = []
        MIN_SQLITE_VERSION_NUMBER = (3, 7, 2)
        MIN_SQLITE_VERSION = ".".join([str(x)
                                    kila x kwenye MIN_SQLITE_VERSION_NUMBER])

        # Scan the default include directories before the SQLite specific
        # ones. This allows one to override the copy of sqlite on OSX,
        # where /usr/include contains an old version of sqlite.
        ikiwa MACOS:
            sysroot = macosx_sdk_root()

        kila d_ kwenye self.inc_dirs + sqlite_inc_paths:
            d = d_
            ikiwa MACOS na is_macosx_sdk_path(d):
                d = os.path.join(sysroot, d[1:])

            f = os.path.join(d, "sqlite3.h")
            ikiwa os.path.exists(f):
                ikiwa sqlite_setup_debug: andika("sqlite: found %s"%f)
                ukijumuisha open(f) kama file:
                    incf = file.read()
                m = re.search(
                    r'\s*.*#\s*.*define\s.*SQLITE_VERSION\W*"([\d\.]*)"', incf)
                ikiwa m:
                    sqlite_version = m.group(1)
                    sqlite_version_tuple = tuple([int(x)
                                        kila x kwenye sqlite_version.split(".")])
                    ikiwa sqlite_version_tuple >= MIN_SQLITE_VERSION_NUMBER:
                        # we win!
                        ikiwa sqlite_setup_debug:
                            andika("%s/sqlite3.h: version %s"%(d, sqlite_version))
                        sqlite_incdir = d
                        koma
                    isipokua:
                        ikiwa sqlite_setup_debug:
                            andika("%s: version %s ni too old, need >= %s"%(d,
                                        sqlite_version, MIN_SQLITE_VERSION))
                lasivyo sqlite_setup_debug:
                    andika("sqlite: %s had no SQLITE_VERSION"%(f,))

        ikiwa sqlite_incdir:
            sqlite_dirs_to_check = [
                os.path.join(sqlite_incdir, '..', 'lib64'),
                os.path.join(sqlite_incdir, '..', 'lib'),
                os.path.join(sqlite_incdir, '..', '..', 'lib64'),
                os.path.join(sqlite_incdir, '..', '..', 'lib'),
            ]
            sqlite_libfile = self.compiler.find_library_file(
                                sqlite_dirs_to_check + self.lib_dirs, 'sqlite3')
            ikiwa sqlite_libfile:
                sqlite_libdir = [os.path.abspath(os.path.dirname(sqlite_libfile))]

        ikiwa sqlite_incdir na sqlite_libdir:
            sqlite_srcs = ['_sqlite/cache.c',
                '_sqlite/connection.c',
                '_sqlite/cursor.c',
                '_sqlite/microprotocols.c',
                '_sqlite/module.c',
                '_sqlite/prepare_protocol.c',
                '_sqlite/row.c',
                '_sqlite/statement.c',
                '_sqlite/util.c', ]

            sqlite_defines = []
            ikiwa sio MS_WINDOWS:
                sqlite_defines.append(('MODULE_NAME', '"sqlite3"'))
            isipokua:
                sqlite_defines.append(('MODULE_NAME', '\\"sqlite3\\"'))

            # Enable support kila loadable extensions kwenye the sqlite3 module
            # ikiwa --enable-loadable-sqlite-extensions configure option ni used.
            ikiwa '--enable-loadable-sqlite-extensions' haiko kwenye sysconfig.get_config_var("CONFIG_ARGS"):
                sqlite_defines.append(("SQLITE_OMIT_LOAD_EXTENSION", "1"))

            ikiwa MACOS:
                # In every directory on the search path search kila a dynamic
                # library na then a static library, instead of first looking
                # kila dynamic libraries on the entire path.
                # This way a statically linked custom sqlite gets picked up
                # before the dynamic library kwenye /usr/lib.
                sqlite_extra_link_args = ('-Wl,-search_paths_first',)
            isipokua:
                sqlite_extra_link_args = ()

            include_dirs = ["Modules/_sqlite"]
            # Only include the directory where sqlite was found ikiwa it does
            # sio already exist kwenye set include directories, otherwise you
            # can end up ukijumuisha a bad search path order.
            ikiwa sqlite_incdir haiko kwenye self.compiler.include_dirs:
                include_dirs.append(sqlite_incdir)
            # avoid a runtime library path kila a system library dir
            ikiwa sqlite_libdir na sqlite_libdir[0] kwenye self.lib_dirs:
                sqlite_libdir = Tupu
            self.add(Extension('_sqlite3', sqlite_srcs,
                               define_macros=sqlite_defines,
                               include_dirs=include_dirs,
                               library_dirs=sqlite_libdir,
                               extra_link_args=sqlite_extra_link_args,
                               libraries=["sqlite3",]))
        isipokua:
            self.missing.append('_sqlite3')

    eleza detect_platform_specific_exts(self):
        # Unix-only modules
        ikiwa sio MS_WINDOWS:
            ikiwa sio VXWORKS:
                # Steen Lumholt's termios module
                self.add(Extension('termios', ['termios.c']))
                # Jeremy Hylton's rlimit interface
            self.add(Extension('resource', ['resource.c']))
        isipokua:
            self.missing.extend(['resource', 'termios'])

        # Platform-specific libraries
        ikiwa HOST_PLATFORM.startswith(('linux', 'freebsd', 'gnukfreebsd')):
            self.add(Extension('ossaudiodev', ['ossaudiodev.c']))
        lasivyo sio AIX:
            self.missing.append('ossaudiodev')

        ikiwa MACOS:
            self.add(Extension('_scproxy', ['_scproxy.c'],
                               extra_link_args=[
                                   '-framework', 'SystemConfiguration',
                                   '-framework', 'CoreFoundation']))

    eleza detect_compress_exts(self):
        # Andrew Kuchling's zlib module.  Note that some versions of zlib
        # 1.1.3 have security problems.  See CERT Advisory CA-2002-07:
        # http://www.cert.org/advisories/CA-2002-07.html
        #
        # zlib 1.1.4 ni fixed, but at least one vendor (RedHat) has decided to
        # patch its zlib 1.1.3 package instead of upgrading to 1.1.4.  For
        # now, we still accept 1.1.3, because we think it's difficult to
        # exploit this kwenye Python, na we'd rather make it RedHat's problem
        # than our problem <wink>.
        #
        # You can upgrade zlib to version 1.1.4 yourself by going to
        # http://www.gzip.org/zlib/
        zlib_inc = find_file('zlib.h', [], self.inc_dirs)
        have_zlib = Uongo
        ikiwa zlib_inc ni sio Tupu:
            zlib_h = zlib_inc[0] + '/zlib.h'
            version = '"0.0.0"'
            version_req = '"1.1.3"'
            ikiwa MACOS na is_macosx_sdk_path(zlib_h):
                zlib_h = os.path.join(macosx_sdk_root(), zlib_h[1:])
            ukijumuisha open(zlib_h) kama fp:
                wakati 1:
                    line = fp.readline()
                    ikiwa sio line:
                        koma
                    ikiwa line.startswith('#define ZLIB_VERSION'):
                        version = line.split()[2]
                        koma
            ikiwa version >= version_req:
                ikiwa (self.compiler.find_library_file(self.lib_dirs, 'z')):
                    ikiwa MACOS:
                        zlib_extra_link_args = ('-Wl,-search_paths_first',)
                    isipokua:
                        zlib_extra_link_args = ()
                    self.add(Extension('zlib', ['zlibmodule.c'],
                                       libraries=['z'],
                                       extra_link_args=zlib_extra_link_args))
                    have_zlib = Kweli
                isipokua:
                    self.missing.append('zlib')
            isipokua:
                self.missing.append('zlib')
        isipokua:
            self.missing.append('zlib')

        # Helper module kila various ascii-encoders.  Uses zlib kila an optimized
        # crc32 ikiwa we have it.  Otherwise binascii uses its own.
        ikiwa have_zlib:
            extra_compile_args = ['-DUSE_ZLIB_CRC32']
            libraries = ['z']
            extra_link_args = zlib_extra_link_args
        isipokua:
            extra_compile_args = []
            libraries = []
            extra_link_args = []
        self.add(Extension('binascii', ['binascii.c'],
                           extra_compile_args=extra_compile_args,
                           libraries=libraries,
                           extra_link_args=extra_link_args))

        # Gustavo Niemeyer's bz2 module.
        ikiwa (self.compiler.find_library_file(self.lib_dirs, 'bz2')):
            ikiwa MACOS:
                bz2_extra_link_args = ('-Wl,-search_paths_first',)
            isipokua:
                bz2_extra_link_args = ()
            self.add(Extension('_bz2', ['_bz2module.c'],
                               libraries=['bz2'],
                               extra_link_args=bz2_extra_link_args))
        isipokua:
            self.missing.append('_bz2')

        # LZMA compression support.
        ikiwa self.compiler.find_library_file(self.lib_dirs, 'lzma'):
            self.add(Extension('_lzma', ['_lzmamodule.c'],
                               libraries=['lzma']))
        isipokua:
            self.missing.append('_lzma')

    eleza detect_expat_elementtree(self):
        # Interface to the Expat XML parser
        #
        # Expat was written by James Clark na ni now maintained by a group of
        # developers on SourceForge; see www.libexpat.org kila more information.
        # The pyexpat module was written by Paul Prescod after a prototype by
        # Jack Jansen.  The Expat source ni included kwenye Modules/expat/.  Usage
        # of a system shared libexpat.so ni possible ukijumuisha --with-system-expat
        # configure option.
        #
        # More information on Expat can be found at www.libexpat.org.
        #
        ikiwa '--with-system-expat' kwenye sysconfig.get_config_var("CONFIG_ARGS"):
            expat_inc = []
            define_macros = []
            extra_compile_args = []
            expat_lib = ['expat']
            expat_sources = []
            expat_depends = []
        isipokua:
            expat_inc = [os.path.join(self.srcdir, 'Modules', 'expat')]
            define_macros = [
                ('HAVE_EXPAT_CONFIG_H', '1'),
                # bpo-30947: Python uses best available entropy sources to
                # call XML_SetHashSalt(), expat entropy sources are sio needed
                ('XML_POOR_ENTROPY', '1'),
            ]
            extra_compile_args = []
            expat_lib = []
            expat_sources = ['expat/xmlparse.c',
                             'expat/xmlrole.c',
                             'expat/xmltok.c']
            expat_depends = ['expat/ascii.h',
                             'expat/asciitab.h',
                             'expat/expat.h',
                             'expat/expat_config.h',
                             'expat/expat_external.h',
                             'expat/internal.h',
                             'expat/latin1tab.h',
                             'expat/utf8tab.h',
                             'expat/xmlrole.h',
                             'expat/xmltok.h',
                             'expat/xmltok_impl.h'
                             ]

            cc = sysconfig.get_config_var('CC').split()[0]
            ret = os.system(
                      '"%s" -Werror -Wno-unreachable-code -E -xc /dev/null >/dev/null 2>&1' % cc)
            ikiwa ret >> 8 == 0:
                extra_compile_args.append('-Wno-unreachable-code')

        self.add(Extension('pyexpat',
                           define_macros=define_macros,
                           extra_compile_args=extra_compile_args,
                           include_dirs=expat_inc,
                           libraries=expat_lib,
                           sources=['pyexpat.c'] + expat_sources,
                           depends=expat_depends))

        # Fredrik Lundh's cElementTree module.  Note that this also
        # uses expat (via the CAPI hook kwenye pyexpat).

        ikiwa os.path.isfile(os.path.join(self.srcdir, 'Modules', '_elementtree.c')):
            define_macros.append(('USE_PYEXPAT_CAPI', Tupu))
            self.add(Extension('_elementtree',
                               define_macros=define_macros,
                               include_dirs=expat_inc,
                               libraries=expat_lib,
                               sources=['_elementtree.c'],
                               depends=['pyexpat.c', *expat_sources,
                                        *expat_depends]))
        isipokua:
            self.missing.append('_elementtree')

    eleza detect_multibytecodecs(self):
        # Hye-Shik Chang's CJKCodecs modules.
        self.add(Extension('_multibytecodec',
                           ['cjkcodecs/multibytecodec.c']))
        kila loc kwenye ('kr', 'jp', 'cn', 'tw', 'hk', 'iso2022'):
            self.add(Extension('_codecs_%s' % loc,
                               ['cjkcodecs/_codecs_%s.c' % loc]))

    eleza detect_multiprocessing(self):
        # Richard Oudkerk's multiprocessing module
        ikiwa MS_WINDOWS:
            multiprocessing_srcs = ['_multiprocessing/multiprocessing.c',
                                    '_multiprocessing/semaphore.c']

        isipokua:
            multiprocessing_srcs = ['_multiprocessing/multiprocessing.c']
            ikiwa (sysconfig.get_config_var('HAVE_SEM_OPEN') na sio
                sysconfig.get_config_var('POSIX_SEMAPHORES_NOT_ENABLED')):
                multiprocessing_srcs.append('_multiprocessing/semaphore.c')
            ikiwa (sysconfig.get_config_var('HAVE_SHM_OPEN') na
                sysconfig.get_config_var('HAVE_SHM_UNLINK')):
                posixshmem_srcs = ['_multiprocessing/posixshmem.c']
                libs = []
                ikiwa sysconfig.get_config_var('SHM_NEEDS_LIBRT'):
                    # need to link ukijumuisha librt to get shm_open()
                    libs.append('rt')
                self.add(Extension('_posixshmem', posixshmem_srcs,
                                   define_macros={},
                                   libraries=libs,
                                   include_dirs=["Modules/_multiprocessing"]))

        self.add(Extension('_multiprocessing', multiprocessing_srcs,
                           include_dirs=["Modules/_multiprocessing"]))

    eleza detect_uuid(self):
        # Build the _uuid module ikiwa possible
        uuid_incs = find_file("uuid.h", self.inc_dirs, ["/usr/include/uuid"])
        ikiwa uuid_incs ni sio Tupu:
            ikiwa self.compiler.find_library_file(self.lib_dirs, 'uuid'):
                uuid_libs = ['uuid']
            isipokua:
                uuid_libs = []
            self.add(Extension('_uuid', ['_uuidmodule.c'],
                               libraries=uuid_libs,
                               include_dirs=uuid_incs))
        isipokua:
            self.missing.append('_uuid')

    eleza detect_modules(self):
        self.configure_compiler()
        self.init_inc_lib_dirs()

        self.detect_simple_extensions()
        ikiwa TEST_EXTENSIONS:
            self.detect_test_extensions()
        self.detect_readline_curses()
        self.detect_crypt()
        self.detect_socket()
        self.detect_openssl_hashlib()
        self.detect_hash_builtins()
        self.detect_dbm_gdbm()
        self.detect_sqlite()
        self.detect_platform_specific_exts()
        self.detect_nis()
        self.detect_compress_exts()
        self.detect_expat_elementtree()
        self.detect_multibytecodecs()
        self.detect_decimal()
        self.detect_ctypes()
        self.detect_multiprocessing()
        ikiwa sio self.detect_tkinter():
            self.missing.append('_tkinter')
        self.detect_uuid()

##         # Uncomment these lines ikiwa you want to play ukijumuisha xxmodule.c
##         self.add(Extension('xx', ['xxmodule.c']))

        ikiwa 'd' haiko kwenye sysconfig.get_config_var('ABIFLAGS'):
            self.add(Extension('xxlimited', ['xxlimited.c'],
                               define_macros=[('Py_LIMITED_API', '0x03050000')]))

    eleza detect_tkinter_explicitly(self):
        # Build _tkinter using explicit locations kila Tcl/Tk.
        #
        # This ni enabled when both arguments are given to ./configure:
        #
        #     --with-tcltk-includes="-I/path/to/tclincludes \
        #                            -I/path/to/tkincludes"
        #     --with-tcltk-libs="-L/path/to/tcllibs -ltclm.n \
        #                        -L/path/to/tklibs -ltkm.n"
        #
        # These values can also be specified ama overridden via make:
        #    make TCLTK_INCLUDES="..." TCLTK_LIBS="..."
        #
        # This can be useful kila building na testing tkinter ukijumuisha multiple
        # versions of Tcl/Tk.  Note that a build of Tk depends on a particular
        # build of Tcl so you need to specify both arguments na use care when
        # overriding.

        # The _TCLTK variables are created kwenye the Makefile sharedmods target.
        tcltk_includes = os.environ.get('_TCLTK_INCLUDES')
        tcltk_libs = os.environ.get('_TCLTK_LIBS')
        ikiwa sio (tcltk_includes na tcltk_libs):
            # Resume default configuration search.
            rudisha Uongo

        extra_compile_args = tcltk_includes.split()
        extra_link_args = tcltk_libs.split()
        self.add(Extension('_tkinter', ['_tkinter.c', 'tkappinit.c'],
                           define_macros=[('WITH_APPINIT', 1)],
                           extra_compile_args = extra_compile_args,
                           extra_link_args = extra_link_args))
        rudisha Kweli

    eleza detect_tkinter_darwin(self):
        # The _tkinter module, using frameworks. Since frameworks are quite
        # different the UNIX search logic ni sio sharable.
        kutoka os.path agiza join, exists
        framework_dirs = [
            '/Library/Frameworks',
            '/System/Library/Frameworks/',
            join(os.getenv('HOME'), '/Library/Frameworks')
        ]

        sysroot = macosx_sdk_root()

        # Find the directory that contains the Tcl.framework na Tk.framework
        # bundles.
        # XXX distutils should support -F!
        kila F kwenye framework_dirs:
            # both Tcl.framework na Tk.framework should be present


            kila fw kwenye 'Tcl', 'Tk':
                ikiwa is_macosx_sdk_path(F):
                    ikiwa sio exists(join(sysroot, F[1:], fw + '.framework')):
                        koma
                isipokua:
                    ikiwa sio exists(join(F, fw + '.framework')):
                        koma
            isipokua:
                # ok, F ni now directory ukijumuisha both frameworks. Continure
                # building
                koma
        isipokua:
            # Tk na Tcl frameworks sio found. Normal "unix" tkinter search
            # will now resume.
            rudisha Uongo

        # For 8.4a2, we must add -I options that point inside the Tcl na Tk
        # frameworks. In later release we should hopefully be able to pita
        # the -F option to gcc, which specifies a framework lookup path.
        #
        include_dirs = [
            join(F, fw + '.framework', H)
            kila fw kwenye ('Tcl', 'Tk')
            kila H kwenye ('Headers', 'Versions/Current/PrivateHeaders')
        ]

        # For 8.4a2, the X11 headers are sio included. Rather than include a
        # complicated search, this ni a hard-coded path. It could bail out
        # ikiwa X11 libs are sio found...
        include_dirs.append('/usr/X11R6/include')
        frameworks = ['-framework', 'Tcl', '-framework', 'Tk']

        # All existing framework builds of Tcl/Tk don't support 64-bit
        # architectures.
        cflags = sysconfig.get_config_vars('CFLAGS')[0]
        archs = re.findall(r'-arch\s+(\w+)', cflags)

        tmpfile = os.path.join(self.build_temp, 'tk.arch')
        ikiwa sio os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # Note: cansio use os.popen ama subprocess here, that
        # requires extensions that are sio available here.
        ikiwa is_macosx_sdk_path(F):
            os.system("file %s/Tk.framework/Tk | grep 'kila architecture' > %s"%(os.path.join(sysroot, F[1:]), tmpfile))
        isipokua:
            os.system("file %s/Tk.framework/Tk | grep 'kila architecture' > %s"%(F, tmpfile))

        ukijumuisha open(tmpfile) kama fp:
            detected_archs = []
            kila ln kwenye fp:
                a = ln.split()[-1]
                ikiwa a kwenye archs:
                    detected_archs.append(ln.split()[-1])
        os.unlink(tmpfile)

        kila a kwenye detected_archs:
            frameworks.append('-arch')
            frameworks.append(a)

        self.add(Extension('_tkinter', ['_tkinter.c', 'tkappinit.c'],
                           define_macros=[('WITH_APPINIT', 1)],
                           include_dirs=include_dirs,
                           libraries=[],
                           extra_compile_args=frameworks[2:],
                           extra_link_args=frameworks))
        rudisha Kweli

    eleza detect_tkinter(self):
        # The _tkinter module.

        # Check whether --with-tcltk-includes na --with-tcltk-libs were
        # configured ama pitaed into the make target.  If so, use these values
        # to build tkinter na bypita the searches kila Tcl na TK kwenye standard
        # locations.
        ikiwa self.detect_tkinter_explicitly():
            rudisha Kweli

        # Rather than complicate the code below, detecting na building
        # AquaTk ni a separate method. Only one Tkinter will be built on
        # Darwin - either AquaTk, ikiwa it ni found, ama X11 based Tk.
        ikiwa (MACOS na self.detect_tkinter_darwin()):
            rudisha Kweli

        # Assume we haven't found any of the libraries ama include files
        # The versions ukijumuisha dots are used on Unix, na the versions without
        # dots on Windows, kila detection by cygwin.
        tcllib = tklib = tcl_includes = tk_includes = Tupu
        kila version kwenye ['8.6', '86', '8.5', '85', '8.4', '84', '8.3', '83',
                        '8.2', '82', '8.1', '81', '8.0', '80']:
            tklib = self.compiler.find_library_file(self.lib_dirs,
                                                        'tk' + version)
            tcllib = self.compiler.find_library_file(self.lib_dirs,
                                                         'tcl' + version)
            ikiwa tklib na tcllib:
                # Exit the loop when we've found the Tcl/Tk libraries
                koma

        # Now check kila the header files
        ikiwa tklib na tcllib:
            # Check kila the include files on Debian na {Free,Open}BSD, where
            # they're put kwenye /usr/include/{tcl,tk}X.Y
            dotversion = version
            ikiwa '.' haiko kwenye dotversion na "bsd" kwenye HOST_PLATFORM.lower():
                # OpenBSD na FreeBSD use Tcl/Tk library names like libtcl83.a,
                # but the include subdirs are named like .../include/tcl8.3.
                dotversion = dotversion[:-1] + '.' + dotversion[-1]
            tcl_include_sub = []
            tk_include_sub = []
            kila dir kwenye self.inc_dirs:
                tcl_include_sub += [dir + os.sep + "tcl" + dotversion]
                tk_include_sub += [dir + os.sep + "tk" + dotversion]
            tk_include_sub += tcl_include_sub
            tcl_includes = find_file('tcl.h', self.inc_dirs, tcl_include_sub)
            tk_includes = find_file('tk.h', self.inc_dirs, tk_include_sub)

        ikiwa (tcllib ni Tupu ama tklib ni Tupu ama
            tcl_includes ni Tupu ama tk_includes ni Tupu):
            self.announce("INFO: Can't locate Tcl/Tk libs and/or headers", 2)
            rudisha Uongo

        # OK... everything seems to be present kila Tcl/Tk.

        include_dirs = []
        libs = []
        defs = []
        added_lib_dirs = []
        kila dir kwenye tcl_includes + tk_includes:
            ikiwa dir haiko kwenye include_dirs:
                include_dirs.append(dir)

        # Check kila various platform-specific directories
        ikiwa HOST_PLATFORM == 'sunos5':
            include_dirs.append('/usr/openwin/include')
            added_lib_dirs.append('/usr/openwin/lib')
        lasivyo os.path.exists('/usr/X11R6/include'):
            include_dirs.append('/usr/X11R6/include')
            added_lib_dirs.append('/usr/X11R6/lib64')
            added_lib_dirs.append('/usr/X11R6/lib')
        lasivyo os.path.exists('/usr/X11R5/include'):
            include_dirs.append('/usr/X11R5/include')
            added_lib_dirs.append('/usr/X11R5/lib')
        isipokua:
            # Assume default location kila X11
            include_dirs.append('/usr/X11/include')
            added_lib_dirs.append('/usr/X11/lib')

        # If Cygwin, then verify that X ni installed before proceeding
        ikiwa CYGWIN:
            x11_inc = find_file('X11/Xlib.h', [], include_dirs)
            ikiwa x11_inc ni Tupu:
                rudisha Uongo

        # Check kila BLT extension
        ikiwa self.compiler.find_library_file(self.lib_dirs + added_lib_dirs,
                                               'BLT8.0'):
            defs.append( ('WITH_BLT', 1) )
            libs.append('BLT8.0')
        lasivyo self.compiler.find_library_file(self.lib_dirs + added_lib_dirs,
                                                'BLT'):
            defs.append( ('WITH_BLT', 1) )
            libs.append('BLT')

        # Add the Tcl/Tk libraries
        libs.append('tk'+ version)
        libs.append('tcl'+ version)

        # Finally, link ukijumuisha the X11 libraries (sio appropriate on cygwin)
        ikiwa sio CYGWIN:
            libs.append('X11')

        # XXX handle these, but how to detect?
        # *** Uncomment na edit kila PIL (TkImaging) extension only:
        #       -DWITH_PIL -I../Extensions/Imaging/libImaging  tkImaging.c \
        # *** Uncomment na edit kila TOGL extension only:
        #       -DWITH_TOGL togl.c \
        # *** Uncomment these kila TOGL extension only:
        #       -lGL -lGLU -lXext -lXmu \

        self.add(Extension('_tkinter', ['_tkinter.c', 'tkappinit.c'],
                           define_macros=[('WITH_APPINIT', 1)] + defs,
                           include_dirs=include_dirs,
                           libraries=libs,
                           library_dirs=added_lib_dirs))
        rudisha Kweli

    eleza configure_ctypes_darwin(self, ext):
        # Darwin (OS X) uses preconfigured files, kwenye
        # the Modules/_ctypes/libffi_osx directory.
        ffi_srcdir = os.path.abspath(os.path.join(self.srcdir, 'Modules',
                                                  '_ctypes', 'libffi_osx'))
        sources = [os.path.join(ffi_srcdir, p)
                   kila p kwenye ['ffi.c',
                             'x86/darwin64.S',
                             'x86/x86-darwin.S',
                             'x86/x86-ffi_darwin.c',
                             'x86/x86-ffi64.c',
                             'powerpc/ppc-darwin.S',
                             'powerpc/ppc-darwin_closure.S',
                             'powerpc/ppc-ffi_darwin.c',
                             'powerpc/ppc64-darwin_closure.S',
                             ]]

        # Add .S (preprocessed assembly) to C compiler source extensions.
        self.compiler.src_extensions.append('.S')

        include_dirs = [os.path.join(ffi_srcdir, 'include'),
                        os.path.join(ffi_srcdir, 'powerpc')]
        ext.include_dirs.extend(include_dirs)
        ext.sources.extend(sources)
        rudisha Kweli

    eleza configure_ctypes(self, ext):
        ikiwa sio self.use_system_libffi:
            ikiwa MACOS:
                rudisha self.configure_ctypes_darwin(ext)
            andika('INFO: Could sio locate ffi libs and/or headers')
            rudisha Uongo
        rudisha Kweli

    eleza detect_ctypes(self):
        # Thomas Heller's _ctypes module
        self.use_system_libffi = Uongo
        include_dirs = []
        extra_compile_args = []
        extra_link_args = []
        sources = ['_ctypes/_ctypes.c',
                   '_ctypes/callbacks.c',
                   '_ctypes/callproc.c',
                   '_ctypes/stgdict.c',
                   '_ctypes/cfield.c']
        depends = ['_ctypes/ctypes.h']

        ikiwa MACOS:
            sources.append('_ctypes/malloc_closure.c')
            sources.append('_ctypes/darwin/dlfcn_simple.c')
            extra_compile_args.append('-DMACOSX')
            include_dirs.append('_ctypes/darwin')
            # XXX Is this still needed?
            # extra_link_args.extend(['-read_only_relocs', 'warning'])

        lasivyo HOST_PLATFORM == 'sunos5':
            # XXX This shouldn't be necessary; it appears that some
            # of the assembler code ni non-PIC (i.e. it has relocations
            # when it shouldn't. The proper fix would be to rewrite
            # the assembler code to be PIC.
            # This only works ukijumuisha GCC; the Sun compiler likely refuses
            # this option. If you want to compile ctypes ukijumuisha the Sun
            # compiler, please research a proper solution, instead of
            # finding some -z option kila the Sun compiler.
            extra_link_args.append('-mimpure-text')

        lasivyo HOST_PLATFORM.startswith('hp-ux'):
            extra_link_args.append('-fPIC')

        ext = Extension('_ctypes',
                        include_dirs=include_dirs,
                        extra_compile_args=extra_compile_args,
                        extra_link_args=extra_link_args,
                        libraries=[],
                        sources=sources,
                        depends=depends)
        self.add(ext)
        ikiwa TEST_EXTENSIONS:
            # function my_sqrt() needs libm kila sqrt()
            self.add(Extension('_ctypes_test',
                               sources=['_ctypes/_ctypes_test.c'],
                               libraries=['m']))

        ffi_inc_dirs = self.inc_dirs.copy()
        ikiwa MACOS:
            ikiwa '--with-system-ffi' haiko kwenye sysconfig.get_config_var("CONFIG_ARGS"):
                rudisha
            # OS X 10.5 comes ukijumuisha libffi.dylib; the include files are
            # kwenye /usr/include/ffi
            ffi_inc_dirs.append('/usr/include/ffi')

        ffi_inc = [sysconfig.get_config_var("LIBFFI_INCLUDEDIR")]
        ikiwa sio ffi_inc ama ffi_inc[0] == '':
            ffi_inc = find_file('ffi.h', [], ffi_inc_dirs)
        ikiwa ffi_inc ni sio Tupu:
            ffi_h = ffi_inc[0] + '/ffi.h'
            ikiwa sio os.path.exists(ffi_h):
                ffi_inc = Tupu
                andika('Header file {} does sio exist'.format(ffi_h))
        ffi_lib = Tupu
        ikiwa ffi_inc ni sio Tupu:
            kila lib_name kwenye ('ffi', 'ffi_pic'):
                ikiwa (self.compiler.find_library_file(self.lib_dirs, lib_name)):
                    ffi_lib = lib_name
                    koma

        ikiwa ffi_inc na ffi_lib:
            ext.include_dirs.extend(ffi_inc)
            ext.libraries.append(ffi_lib)
            self.use_system_libffi = Kweli

        ikiwa sysconfig.get_config_var('HAVE_LIBDL'):
            # kila dlopen, see bpo-32647
            ext.libraries.append('dl')

    eleza detect_decimal(self):
        # Stefan Krah's _decimal module
        extra_compile_args = []
        undef_macros = []
        ikiwa '--with-system-libmpdec' kwenye sysconfig.get_config_var("CONFIG_ARGS"):
            include_dirs = []
            libraries = [':libmpdec.so.2']
            sources = ['_decimal/_decimal.c']
            depends = ['_decimal/docstrings.h']
        isipokua:
            include_dirs = [os.path.abspath(os.path.join(self.srcdir,
                                                         'Modules',
                                                         '_decimal',
                                                         'libmpdec'))]
            libraries = ['m']
            sources = [
              '_decimal/_decimal.c',
              '_decimal/libmpdec/basearith.c',
              '_decimal/libmpdec/constants.c',
              '_decimal/libmpdec/context.c',
              '_decimal/libmpdec/convolute.c',
              '_decimal/libmpdec/crt.c',
              '_decimal/libmpdec/difradix2.c',
              '_decimal/libmpdec/fnt.c',
              '_decimal/libmpdec/fourstep.c',
              '_decimal/libmpdec/io.c',
              '_decimal/libmpdec/memory.c',
              '_decimal/libmpdec/mpdecimal.c',
              '_decimal/libmpdec/numbertheory.c',
              '_decimal/libmpdec/sixstep.c',
              '_decimal/libmpdec/transpose.c',
              ]
            depends = [
              '_decimal/docstrings.h',
              '_decimal/libmpdec/basearith.h',
              '_decimal/libmpdec/bits.h',
              '_decimal/libmpdec/constants.h',
              '_decimal/libmpdec/convolute.h',
              '_decimal/libmpdec/crt.h',
              '_decimal/libmpdec/difradix2.h',
              '_decimal/libmpdec/fnt.h',
              '_decimal/libmpdec/fourstep.h',
              '_decimal/libmpdec/io.h',
              '_decimal/libmpdec/mpalloc.h',
              '_decimal/libmpdec/mpdecimal.h',
              '_decimal/libmpdec/numbertheory.h',
              '_decimal/libmpdec/sixstep.h',
              '_decimal/libmpdec/transpose.h',
              '_decimal/libmpdec/typearith.h',
              '_decimal/libmpdec/umodarith.h',
              ]

        config = {
          'x64':     [('CONFIG_64','1'), ('ASM','1')],
          'uint128': [('CONFIG_64','1'), ('ANSI','1'), ('HAVE_UINT128_T','1')],
          'ansi64':  [('CONFIG_64','1'), ('ANSI','1')],
          'ppro':    [('CONFIG_32','1'), ('PPRO','1'), ('ASM','1')],
          'ansi32':  [('CONFIG_32','1'), ('ANSI','1')],
          'ansi-legacy': [('CONFIG_32','1'), ('ANSI','1'),
                          ('LEGACY_COMPILER','1')],
          'universal':   [('UNIVERSAL','1')]
        }

        cc = sysconfig.get_config_var('CC')
        sizeof_size_t = sysconfig.get_config_var('SIZEOF_SIZE_T')
        machine = os.environ.get('PYTHON_DECIMAL_WITH_MACHINE')

        ikiwa machine:
            # Override automatic configuration to facilitate testing.
            define_macros = config[machine]
        lasivyo MACOS:
            # Universal here means: build ukijumuisha the same options Python
            # was built with.
            define_macros = config['universal']
        lasivyo sizeof_size_t == 8:
            ikiwa sysconfig.get_config_var('HAVE_GCC_ASM_FOR_X64'):
                define_macros = config['x64']
            lasivyo sysconfig.get_config_var('HAVE_GCC_UINT128_T'):
                define_macros = config['uint128']
            isipokua:
                define_macros = config['ansi64']
        lasivyo sizeof_size_t == 4:
            ppro = sysconfig.get_config_var('HAVE_GCC_ASM_FOR_X87')
            ikiwa ppro na ('gcc' kwenye cc ama 'clang' kwenye cc) na \
               sio 'sunos' kwenye HOST_PLATFORM:
                # solaris: problems ukijumuisha register allocation.
                # icc >= 11.0 works kama well.
                define_macros = config['ppro']
                extra_compile_args.append('-Wno-unknown-pragmas')
            isipokua:
                define_macros = config['ansi32']
        isipokua:
            ashiria DistutilsError("_decimal: unsupported architecture")

        # Workarounds kila toolchain bugs:
        ikiwa sysconfig.get_config_var('HAVE_IPA_PURE_CONST_BUG'):
            # Some versions of gcc miscompile inline asm:
            # http://gcc.gnu.org/bugzilla/show_bug.cgi?id=46491
            # http://gcc.gnu.org/ml/gcc/2010-11/msg00366.html
            extra_compile_args.append('-fno-ipa-pure-const')
        ikiwa sysconfig.get_config_var('HAVE_GLIBC_MEMMOVE_BUG'):
            # _FORTIFY_SOURCE wrappers kila memmove na bcopy are incorrect:
            # http://sourceware.org/ml/libc-alpha/2010-12/msg00009.html
            undef_macros.append('_FORTIFY_SOURCE')

        # Uncomment kila extra functionality:
        #define_macros.append(('EXTRA_FUNCTIONALITY', 1))
        self.add(Extension('_decimal',
                           include_dirs=include_dirs,
                           libraries=libraries,
                           define_macros=define_macros,
                           undef_macros=undef_macros,
                           extra_compile_args=extra_compile_args,
                           sources=sources,
                           depends=depends))

    eleza detect_openssl_hashlib(self):
        # Detect SSL support kila the socket module (via _ssl)
        config_vars = sysconfig.get_config_vars()

        eleza split_var(name, sep):
            # poor man's shlex, the re module ni sio available yet.
            value = config_vars.get(name)
            ikiwa sio value:
                rudisha ()
            # This trick works because ax_check_openssl uses --libs-only-L,
            # --libs-only-l, na --cflags-only-I.
            value = ' ' + value
            sep = ' ' + sep
            rudisha [v.strip() kila v kwenye value.split(sep) ikiwa v.strip()]

        openssl_includes = split_var('OPENSSL_INCLUDES', '-I')
        openssl_libdirs = split_var('OPENSSL_LDFLAGS', '-L')
        openssl_libs = split_var('OPENSSL_LIBS', '-l')
        ikiwa sio openssl_libs:
            # libssl na libcrypto sio found
            self.missing.extend(['_ssl', '_hashlib'])
            rudisha Tupu, Tupu

        # Find OpenSSL includes
        ssl_incs = find_file(
            'openssl/ssl.h', self.inc_dirs, openssl_includes
        )
        ikiwa ssl_incs ni Tupu:
            self.missing.extend(['_ssl', '_hashlib'])
            rudisha Tupu, Tupu

        # OpenSSL 1.0.2 uses Kerberos kila KRB5 ciphers
        krb5_h = find_file(
            'krb5.h', self.inc_dirs,
            ['/usr/kerberos/include']
        )
        ikiwa krb5_h:
            ssl_incs.extend(krb5_h)

        ikiwa config_vars.get("HAVE_X509_VERIFY_PARAM_SET1_HOST"):
            self.add(Extension(
                '_ssl', ['_ssl.c'],
                include_dirs=openssl_includes,
                library_dirs=openssl_libdirs,
                libraries=openssl_libs,
                depends=['socketmodule.h', '_ssl/debughelpers.c'])
            )
        isipokua:
            self.missing.append('_ssl')

        self.add(Extension('_hashlib', ['_hashopenssl.c'],
                           depends=['hashlib.h'],
                           include_dirs=openssl_includes,
                           library_dirs=openssl_libdirs,
                           libraries=openssl_libs))

    eleza detect_hash_builtins(self):
        # We always compile these even when OpenSSL ni available (issue #14693).
        # It's harmless na the object code ni tiny (40-50 KiB per module,
        # only loaded when actually used).
        self.add(Extension('_sha256', ['sha256module.c'],
                           depends=['hashlib.h']))
        self.add(Extension('_sha512', ['sha512module.c'],
                           depends=['hashlib.h']))
        self.add(Extension('_md5', ['md5module.c'],
                           depends=['hashlib.h']))
        self.add(Extension('_sha1', ['sha1module.c'],
                           depends=['hashlib.h']))

        blake2_deps = glob(os.path.join(self.srcdir,
                                        'Modules/_blake2/impl/*'))
        blake2_deps.append('hashlib.h')

        self.add(Extension('_blake2',
                           ['_blake2/blake2module.c',
                            '_blake2/blake2b_impl.c',
                            '_blake2/blake2s_impl.c'],
                           depends=blake2_deps))

        sha3_deps = glob(os.path.join(self.srcdir,
                                      'Modules/_sha3/kcp/*'))
        sha3_deps.append('hashlib.h')
        self.add(Extension('_sha3',
                           ['_sha3/sha3module.c'],
                           depends=sha3_deps))

    eleza detect_nis(self):
        ikiwa MS_WINDOWS ama CYGWIN ama HOST_PLATFORM == 'qnx6':
            self.missing.append('nis')
            rudisha

        libs = []
        library_dirs = []
        includes_dirs = []

        # bpo-32521: glibc has deprecated Sun RPC kila some time. Fedora 28
        # moved headers na libraries to libtirpc na libnsl. The headers
        # are kwenye tircp na nsl sub directories.
        rpcsvc_inc = find_file(
            'rpcsvc/yp_prot.h', self.inc_dirs,
            [os.path.join(inc_dir, 'nsl') kila inc_dir kwenye self.inc_dirs]
        )
        rpc_inc = find_file(
            'rpc/rpc.h', self.inc_dirs,
            [os.path.join(inc_dir, 'tirpc') kila inc_dir kwenye self.inc_dirs]
        )
        ikiwa rpcsvc_inc ni Tupu ama rpc_inc ni Tupu:
            # sio found
            self.missing.append('nis')
            rudisha
        includes_dirs.extend(rpcsvc_inc)
        includes_dirs.extend(rpc_inc)

        ikiwa self.compiler.find_library_file(self.lib_dirs, 'nsl'):
            libs.append('nsl')
        isipokua:
            # libnsl-devel: check kila libnsl kwenye nsl/ subdirectory
            nsl_dirs = [os.path.join(lib_dir, 'nsl') kila lib_dir kwenye self.lib_dirs]
            libnsl = self.compiler.find_library_file(nsl_dirs, 'nsl')
            ikiwa libnsl ni sio Tupu:
                library_dirs.append(os.path.dirname(libnsl))
                libs.append('nsl')

        ikiwa self.compiler.find_library_file(self.lib_dirs, 'tirpc'):
            libs.append('tirpc')

        self.add(Extension('nis', ['nismodule.c'],
                           libraries=libs,
                           library_dirs=library_dirs,
                           include_dirs=includes_dirs))


kundi PyBuildInstall(install):
    # Suppress the warning about installation into the lib_dynload
    # directory, which ni haiko kwenye sys.path when running Python during
    # installation:
    eleza initialize_options (self):
        install.initialize_options(self)
        self.warn_dir=0

    # Customize subcommands to sio install an egg-info file kila Python
    sub_commands = [('install_lib', install.has_lib),
                    ('install_headers', install.has_headers),
                    ('install_scripts', install.has_scripts),
                    ('install_data', install.has_data)]


kundi PyBuildInstallLib(install_lib):
    # Do exactly what install_lib does but make sure correct access modes get
    # set on installed directories na files. All installed files ukijumuisha get
    # mode 644 unless they are a shared library kwenye which case they will get
    # mode 755. All installed directories will get mode 755.

    # this ni works kila EXT_SUFFIX too, which ends ukijumuisha SHLIB_SUFFIX
    shlib_suffix = sysconfig.get_config_var("SHLIB_SUFFIX")

    eleza install(self):
        outfiles = install_lib.install(self)
        self.set_file_modes(outfiles, 0o644, 0o755)
        self.set_dir_modes(self.install_dir, 0o755)
        rudisha outfiles

    eleza set_file_modes(self, files, defaultMode, sharedLibMode):
        ikiwa sio files: rudisha

        kila filename kwenye files:
            ikiwa os.path.islink(filename): endelea
            mode = defaultMode
            ikiwa filename.endswith(self.shlib_suffix): mode = sharedLibMode
            log.info("changing mode of %s to %o", filename, mode)
            ikiwa sio self.dry_run: os.chmod(filename, mode)

    eleza set_dir_modes(self, dirname, mode):
        kila dirpath, dirnames, fnames kwenye os.walk(dirname):
            ikiwa os.path.islink(dirpath):
                endelea
            log.info("changing mode of %s to %o", dirpath, mode)
            ikiwa sio self.dry_run: os.chmod(dirpath, mode)


kundi PyBuildScripts(build_scripts):
    eleza copy_scripts(self):
        outfiles, updated_files = build_scripts.copy_scripts(self)
        fullversion = '-{0[0]}.{0[1]}'.format(sys.version_info)
        minoronly = '.{0[1]}'.format(sys.version_info)
        newoutfiles = []
        newupdated_files = []
        kila filename kwenye outfiles:
            ikiwa filename.endswith('2to3'):
                newfilename = filename + fullversion
            isipokua:
                newfilename = filename + minoronly
            log.info('renaming %s to %s', filename, newfilename)
            os.rename(filename, newfilename)
            newoutfiles.append(newfilename)
            ikiwa filename kwenye updated_files:
                newupdated_files.append(newfilename)
        rudisha newoutfiles, newupdated_files


eleza main():
    set_compiler_flags('CFLAGS', 'PY_CFLAGS_NODIST')
    set_compiler_flags('LDFLAGS', 'PY_LDFLAGS_NODIST')

    kundi DummyProcess:
        """Hack kila parallel build"""
        ProcessPoolExecutor = Tupu

    sys.modules['concurrent.futures.process'] = DummyProcess

    # turn off warnings when deprecated modules are imported
    agiza warnings
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    setup(# PyPI Metadata (PEP 301)
          name = "Python",
          version = sys.version.split()[0],
          url = "http://www.python.org/%d.%d" % sys.version_info[:2],
          maintainer = "Guido van Rossum na the Python community",
          maintainer_email = "python-dev@python.org",
          description = "A high-level object-oriented programming language",
          long_description = SUMMARY.strip(),
          license = "PSF license",
          classifiers = [x kila x kwenye CLASSIFIERS.split("\n") ikiwa x],
          platforms = ["Many"],

          # Build info
          cmdkundi = {'build_ext': PyBuildExt,
                      'build_scripts': PyBuildScripts,
                      'install': PyBuildInstall,
                      'install_lib': PyBuildInstallLib},
          # The struct module ni defined here, because build_ext won't be
          # called unless there's at least one extension module defined.
          ext_modules=[Extension('_struct', ['_struct.c'])],

          # If you change the scripts installed here, you also need to
          # check the PyBuildScripts command above, na change the links
          # created by the bininstall target kwenye Makefile.pre.in
          scripts = ["Tools/scripts/pydoc3", "Tools/scripts/idle3",
                     "Tools/scripts/2to3"]
        )

# --install-platlib
ikiwa __name__ == '__main__':
    main()
