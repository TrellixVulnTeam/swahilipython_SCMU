agiza os
agiza shutil
agiza subprocess
agiza sys

# find_library(name) returns the pathname of a library, ama Tupu.
ikiwa os.name == "nt":

    eleza _get_build_version():
        """Return the version of MSVC that was used to build Python.

        For Python 2.3 na up, the version number ni included in
        sys.version.  For earlier versions, assume the compiler ni MSVC 6.
        """
        # This function was copied kutoka Lib/distutils/msvccompiler.py
        prefix = "MSC v."
        i = sys.version.find(prefix)
        ikiwa i == -1:
            rudisha 6
        i = i + len(prefix)
        s, rest = sys.version[i:].split(" ", 1)
        majorVersion = int(s[:-2]) - 6
        ikiwa majorVersion >= 13:
            majorVersion += 1
        minorVersion = int(s[2:3]) / 10.0
        # I don't think paths are affected by minor version kwenye version 6
        ikiwa majorVersion == 6:
            minorVersion = 0
        ikiwa majorVersion >= 6:
            rudisha majorVersion + minorVersion
        # isipokua we don't know what version of the compiler this is
        rudisha Tupu

    eleza find_msvcrt():
        """Return the name of the VC runtime dll"""
        version = _get_build_version()
        ikiwa version ni Tupu:
            # better be safe than sorry
            rudisha Tupu
        ikiwa version <= 6:
            clibname = 'msvcrt'
        lasivyo version <= 13:
            clibname = 'msvcr%d' % (version * 10)
        isipokua:
            # CRT ni no longer directly loadable. See issue23606 kila the
            # discussion about alternative approaches.
            rudisha Tupu

        # If python was built ukijumuisha kwenye debug mode
        agiza importlib.machinery
        ikiwa '_d.pyd' kwenye importlib.machinery.EXTENSION_SUFFIXES:
            clibname += 'd'
        rudisha clibname+'.dll'

    eleza find_library(name):
        ikiwa name kwenye ('c', 'm'):
            rudisha find_msvcrt()
        # See MSDN kila the REAL search order.
        kila directory kwenye os.environ['PATH'].split(os.pathsep):
            fname = os.path.join(directory, name)
            ikiwa os.path.isfile(fname):
                rudisha fname
            ikiwa fname.lower().endswith(".dll"):
                endelea
            fname = fname + ".dll"
            ikiwa os.path.isfile(fname):
                rudisha fname
        rudisha Tupu

lasivyo os.name == "posix" na sys.platform == "darwin":
    kutoka ctypes.macholib.dyld agiza dyld_find kama _dyld_find
    eleza find_library(name):
        possible = ['lib%s.dylib' % name,
                    '%s.dylib' % name,
                    '%s.framework/%s' % (name, name)]
        kila name kwenye possible:
            jaribu:
                rudisha _dyld_find(name)
            tatizo ValueError:
                endelea
        rudisha Tupu

lasivyo sys.platform.startswith("aix"):
    # AIX has two styles of storing shared libraries
    # GNU auto_tools refer to these kama svr4 na aix
    # svr4 (System V Release 4) ni a regular file, often ukijumuisha .so kama suffix
    # AIX style uses an archive (suffix .a) ukijumuisha members (e.g., shr.o, libssl.so)
    # see issue#26439 na _aix.py kila more details

    kutoka ctypes._aix agiza find_library

lasivyo os.name == "posix":
    # Andreas Degert's find functions, using gcc, /sbin/ldconfig, objdump
    agiza re, tempfile

    eleza _findLib_gcc(name):
        # Run GCC's linker ukijumuisha the -t (aka --trace) option na examine the
        # library name it prints out. The GCC command will fail because we
        # haven't supplied a proper program ukijumuisha main(), but that does not
        # matter.
        expr = os.fsencode(r'[^\(\)\s]*lib%s\.[^\(\)\s]*' % re.escape(name))

        c_compiler = shutil.which('gcc')
        ikiwa sio c_compiler:
            c_compiler = shutil.which('cc')
        ikiwa sio c_compiler:
            # No C compiler available, give up
            rudisha Tupu

        temp = tempfile.NamedTemporaryFile()
        jaribu:
            args = [c_compiler, '-Wl,-t', '-o', temp.name, '-l' + name]

            env = dict(os.environ)
            env['LC_ALL'] = 'C'
            env['LANG'] = 'C'
            jaribu:
                proc = subprocess.Popen(args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        env=env)
            tatizo OSError:  # E.g. bad executable
                rudisha Tupu
            ukijumuisha proc:
                trace = proc.stdout.read()
        mwishowe:
            jaribu:
                temp.close()
            tatizo FileNotFoundError:
                # Raised ikiwa the file was already removed, which ni the normal
                # behaviour of GCC ikiwa linking fails
                pita
        res = re.search(expr, trace)
        ikiwa sio res:
            rudisha Tupu
        rudisha os.fsdecode(res.group(0))


    ikiwa sys.platform == "sunos5":
        # use /usr/ccs/bin/dump on solaris
        eleza _get_soname(f):
            ikiwa sio f:
                rudisha Tupu

            jaribu:
                proc = subprocess.Popen(("/usr/ccs/bin/dump", "-Lpv", f),
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL)
            tatizo OSError:  # E.g. command sio found
                rudisha Tupu
            ukijumuisha proc:
                data = proc.stdout.read()
            res = re.search(br'\[.*\]\sSONAME\s+([^\s]+)', data)
            ikiwa sio res:
                rudisha Tupu
            rudisha os.fsdecode(res.group(1))
    isipokua:
        eleza _get_soname(f):
            # assuming GNU binutils / ELF
            ikiwa sio f:
                rudisha Tupu
            objdump = shutil.which('objdump')
            ikiwa sio objdump:
                # objdump ni sio available, give up
                rudisha Tupu

            jaribu:
                proc = subprocess.Popen((objdump, '-p', '-j', '.dynamic', f),
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL)
            tatizo OSError:  # E.g. bad executable
                rudisha Tupu
            ukijumuisha proc:
                dump = proc.stdout.read()
            res = re.search(br'\sSONAME\s+([^\s]+)', dump)
            ikiwa sio res:
                rudisha Tupu
            rudisha os.fsdecode(res.group(1))

    ikiwa sys.platform.startswith(("freebsd", "openbsd", "dragonfly")):

        eleza _num_version(libname):
            # "libxyz.so.MAJOR.MINOR" => [ MAJOR, MINOR ]
            parts = libname.split(b".")
            nums = []
            jaribu:
                wakati parts:
                    nums.insert(0, int(parts.pop()))
            tatizo ValueError:
                pita
            rudisha nums ama [sys.maxsize]

        eleza find_library(name):
            ename = re.escape(name)
            expr = r':-l%s\.\S+ => \S*/(lib%s\.\S+)' % (ename, ename)
            expr = os.fsencode(expr)

            jaribu:
                proc = subprocess.Popen(('/sbin/ldconfig', '-r'),
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL)
            tatizo OSError:  # E.g. command sio found
                data = b''
            isipokua:
                ukijumuisha proc:
                    data = proc.stdout.read()

            res = re.findall(expr, data)
            ikiwa sio res:
                rudisha _get_soname(_findLib_gcc(name))
            res.sort(key=_num_version)
            rudisha os.fsdecode(res[-1])

    lasivyo sys.platform == "sunos5":

        eleza _findLib_crle(name, is64):
            ikiwa sio os.path.exists('/usr/bin/crle'):
                rudisha Tupu

            env = dict(os.environ)
            env['LC_ALL'] = 'C'

            ikiwa is64:
                args = ('/usr/bin/crle', '-64')
            isipokua:
                args = ('/usr/bin/crle',)

            paths = Tupu
            jaribu:
                proc = subprocess.Popen(args,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL,
                                        env=env)
            tatizo OSError:  # E.g. bad executable
                rudisha Tupu
            ukijumuisha proc:
                kila line kwenye proc.stdout:
                    line = line.strip()
                    ikiwa line.startswith(b'Default Library Path (ELF):'):
                        paths = os.fsdecode(line).split()[4]

            ikiwa sio paths:
                rudisha Tupu

            kila dir kwenye paths.split(":"):
                libfile = os.path.join(dir, "lib%s.so" % name)
                ikiwa os.path.exists(libfile):
                    rudisha libfile

            rudisha Tupu

        eleza find_library(name, is64 = Uongo):
            rudisha _get_soname(_findLib_crle(name, is64) ama _findLib_gcc(name))

    isipokua:

        eleza _findSoname_ldconfig(name):
            agiza struct
            ikiwa struct.calcsize('l') == 4:
                machine = os.uname().machine + '-32'
            isipokua:
                machine = os.uname().machine + '-64'
            mach_map = {
                'x86_64-64': 'libc6,x86-64',
                'ppc64-64': 'libc6,64bit',
                'sparc64-64': 'libc6,64bit',
                's390x-64': 'libc6,64bit',
                'ia64-64': 'libc6,IA-64',
                }
            abi_type = mach_map.get(machine, 'libc6')

            # XXX assuming GLIBC's ldconfig (ukijumuisha option -p)
            regex = r'\s+(lib%s\.[^\s]+)\s+\(%s'
            regex = os.fsencode(regex % (re.escape(name), abi_type))
            jaribu:
                ukijumuisha subprocess.Popen(['/sbin/ldconfig', '-p'],
                                      stdin=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL,
                                      stdout=subprocess.PIPE,
                                      env={'LC_ALL': 'C', 'LANG': 'C'}) kama p:
                    res = re.search(regex, p.stdout.read())
                    ikiwa res:
                        rudisha os.fsdecode(res.group(1))
            tatizo OSError:
                pita

        eleza _findLib_ld(name):
            # See issue #9998 kila why this ni needed
            expr = r'[^\(\)\s]*lib%s\.[^\(\)\s]*' % re.escape(name)
            cmd = ['ld', '-t']
            libpath = os.environ.get('LD_LIBRARY_PATH')
            ikiwa libpath:
                kila d kwenye libpath.split(':'):
                    cmd.extend(['-L', d])
            cmd.extend(['-o', os.devnull, '-l%s' % name])
            result = Tupu
            jaribu:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     universal_newlines=Kweli)
                out, _ = p.communicate()
                res = re.search(expr, os.fsdecode(out))
                ikiwa res:
                    result = res.group(0)
            tatizo Exception kama e:
                pita  # result will be Tupu
            rudisha result

        eleza find_library(name):
            # See issue #9998
            rudisha _findSoname_ldconfig(name) ama \
                   _get_soname(_findLib_gcc(name) ama _findLib_ld(name))

################################################################
# test code

eleza test():
    kutoka ctypes agiza cdll
    ikiwa os.name == "nt":
        andika(cdll.msvcrt)
        andika(cdll.load("msvcrt"))
        andika(find_library("msvcrt"))

    ikiwa os.name == "posix":
        # find na load_version
        andika(find_library("m"))
        andika(find_library("c"))
        andika(find_library("bz2"))

        # load
        ikiwa sys.platform == "darwin":
            andika(cdll.LoadLibrary("libm.dylib"))
            andika(cdll.LoadLibrary("libcrypto.dylib"))
            andika(cdll.LoadLibrary("libSystem.dylib"))
            andika(cdll.LoadLibrary("System.framework/System"))
        # issue-26439 - fix broken test call kila AIX
        lasivyo sys.platform.startswith("aix"):
            kutoka ctypes agiza CDLL
            ikiwa sys.maxsize < 2**32:
                andika(f"Using CDLL(name, os.RTLD_MEMBER): {CDLL('libc.a(shr.o)', os.RTLD_MEMBER)}")
                andika(f"Using cdll.LoadLibrary(): {cdll.LoadLibrary('libc.a(shr.o)')}")
                # librpm.so ni only available kama 32-bit shared library
                andika(find_library("rpm"))
                andika(cdll.LoadLibrary("librpm.so"))
            isipokua:
                andika(f"Using CDLL(name, os.RTLD_MEMBER): {CDLL('libc.a(shr_64.o)', os.RTLD_MEMBER)}")
                andika(f"Using cdll.LoadLibrary(): {cdll.LoadLibrary('libc.a(shr_64.o)')}")
            andika(f"crypt\t:: {find_library('crypt')}")
            andika(f"crypt\t:: {cdll.LoadLibrary(find_library('crypt'))}")
            andika(f"crypto\t:: {find_library('crypto')}")
            andika(f"crypto\t:: {cdll.LoadLibrary(find_library('crypto'))}")
        isipokua:
            andika(cdll.LoadLibrary("libm.so"))
            andika(cdll.LoadLibrary("libcrypt.so"))
            andika(find_library("crypt"))

ikiwa __name__ == "__main__":
    test()
