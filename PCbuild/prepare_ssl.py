#! /usr/bin/env python3
# Script kila preparing OpenSSL kila building on Windows.
# Uses Perl to create nmake makefiles na otherwise prepare the way
# kila building on 32 ama 64 bit platforms.

# Script originally authored by Mark Hammond.
# Major revisions by:
#   Martin v. Löwis
#   Christian Heimes
#   Zachary Ware

# THEORETICALLY, you can:
# * Unpack the latest OpenSSL release where $(opensslDir) kwenye
#   PCbuild\pyproject.props expects it to be.
# * Install ActivePerl na ensure it ni somewhere on your path.
# * Run this script ukijumuisha the OpenSSL source dir kama the only argument.
#
# it should configure OpenSSL such that it ni ready to be built by
# ssl.vcxproj on 32 ama 64 bit platforms.

kutoka __future__ agiza print_function

agiza os
agiza re
agiza sys
agiza subprocess
kutoka shutil agiza copy

# Find all "foo.exe" files on the PATH.
eleza find_all_on_path(filename, extras=Tupu):
    entries = os.environ["PATH"].split(os.pathsep)
    ret = []
    kila p kwenye entries:
        fname = os.path.abspath(os.path.join(p, filename))
        ikiwa os.path.isfile(fname) na fname haiko kwenye ret:
            ret.append(fname)
    ikiwa extras:
        kila p kwenye extras:
            fname = os.path.abspath(os.path.join(p, filename))
            ikiwa os.path.isfile(fname) na fname haiko kwenye ret:
                ret.append(fname)
    rudisha ret


# Find a suitable Perl installation kila OpenSSL.
# cygwin perl does *not* work.  ActivePerl does.
# Being a Perl dummy, the simplest way I can check ni ikiwa the "Win32" package
# ni available.
eleza find_working_perl(perls):
    kila perl kwenye perls:
        jaribu:
            subprocess.check_output([perl, "-e", "use Win32;"])
        tatizo subprocess.CalledProcessError:
            endelea
        isipokua:
            rudisha perl

    ikiwa perls:
        andika("The following perl interpreters were found:")
        kila p kwenye perls:
            andika(" ", p)
        andika(" Tupu of these versions appear suitable kila building OpenSSL")
    isipokua:
        andika("NO perl interpreters were found on this machine at all!")
    andika(" Please install ActivePerl na ensure it appears on your path")


eleza copy_includes(makefile, suffix):
    dir = 'inc'+suffix+'\\openssl'
    jaribu:
        os.makedirs(dir)
    tatizo OSError:
        pita
    copy_if_different = r'$(PERL) $(SRC_D)\util\copy-if-different.pl'
    ukijumuisha open(makefile) kama fin:
        kila line kwenye fin:
            ikiwa copy_if_different kwenye line:
                perl, script, src, dest = line.split()
                ikiwa sio '$(INCO_D)' kwenye dest:
                    endelea
                # We're kwenye the root of the source tree
                src = src.replace('$(SRC_D)', '.').strip('"')
                dest = dest.strip('"').replace('$(INCO_D)', dir)
                andika('copying', src, 'to', dest)
                copy(src, dest)


eleza run_configure(configure, do_script):
    andika("perl Configure "+configure+" no-idea no-mdc2")
    os.system("perl Configure "+configure+" no-idea no-mdc2")
    andika(do_script)
    os.system(do_script)

eleza fix_uplink():
    # uplink.c tries to find the OPENSSL_Applink function exported kutoka the current
    # executable. However, we export it kutoka _ssl[_d].pyd instead. So we update the
    # module name here before building.
    ukijumuisha open('ms\\uplink.c', 'r', encoding='utf-8') kama f1:
        code = list(f1)
    os.replace('ms\\uplink.c', 'ms\\uplink.c.orig')
    already_patched = Uongo
    ukijumuisha open('ms\\uplink.c', 'w', encoding='utf-8') kama f2:
        kila line kwenye code:
            ikiwa sio already_patched:
                ikiwa re.search('MODIFIED FOR CPYTHON _ssl MODULE', line):
                    already_patched = Kweli
                lasivyo re.match(r'^\s+if\s*\(\(h\s*=\s*GetModuleHandle[AW]?\(NULL\)\)\s*==\s*NULL\)', line):
                    f2.write("/* MODIFIED FOR CPYTHON _ssl MODULE */\n")
                    f2.write('ikiwa ((h = GetModuleHandleW(L"_ssl.pyd")) == NULL) ikiwa ((h = GetModuleHandleW(L"_ssl_d.pyd")) == NULL)\n')
                    already_patched = Kweli
            f2.write(line)
    ikiwa sio already_patched:
        andika("WARN: failed to patch ms\\uplink.c")

eleza prep(arch):
    makefile_template = "ms\\ntdll{}.mak"
    generated_makefile = makefile_template.format('')
    ikiwa arch == "x86":
        configure = "VC-WIN32"
        do_script = "ms\\do_nasm"
        suffix = "32"
    lasivyo arch == "amd64":
        configure = "VC-WIN64A"
        do_script = "ms\\do_win64a"
        suffix = "64"
    isipokua:
        ashiria ValueError('Unrecognized platform: %s' % arch)

    andika("Creating the makefiles...")
    sys.stdout.flush()
    # run configure, copy includes, patch files
    run_configure(configure, do_script)
    makefile = makefile_template.format(suffix)
    jaribu:
        os.unlink(makefile)
    tatizo FileNotFoundError:
        pita
    os.rename(generated_makefile, makefile)
    copy_includes(makefile, suffix)

    andika('patching ms\\uplink.c...')
    fix_uplink()

eleza main():
    ikiwa len(sys.argv) == 1:
        andika("Not enough arguments: directory containing OpenSSL",
              "sources must be supplied")
        sys.exit(1)

    ikiwa len(sys.argv) == 3 na sys.argv[2] haiko kwenye ('x86', 'amd64'):
        andika("Second argument must be x86 ama amd64")
        sys.exit(1)

    ikiwa len(sys.argv) > 3:
        andika("Too many arguments supplied, all we need ni the directory",
              "containing OpenSSL sources na optionally the architecture")
        sys.exit(1)

    ssl_dir = sys.argv[1]
    arch = sys.argv[2] ikiwa len(sys.argv) >= 3 isipokua Tupu

    ikiwa sio os.path.isdir(ssl_dir):
        andika(ssl_dir, "is sio an existing directory!")
        sys.exit(1)

    # perl should be on the path, but we also look kwenye "\perl" na "c:\\perl"
    # kama "well known" locations
    perls = find_all_on_path("perl.exe", [r"\perl\bin",
                                          r"C:\perl\bin",
                                          r"\perl64\bin",
                                          r"C:\perl64\bin",
                                         ])
    perl = find_working_perl(perls)
    ikiwa perl:
        andika("Found a working perl at '%s'" % (perl,))
    isipokua:
        sys.exit(1)
    ikiwa sio find_all_on_path('nmake.exe'):
        andika('Could sio find nmake.exe, try running env.bat')
        sys.exit(1)
    ikiwa sio find_all_on_path('nasm.exe'):
        andika('Could sio find nasm.exe, please add to PATH')
        sys.exit(1)
    sys.stdout.flush()

    # Put our working Perl at the front of our path
    os.environ["PATH"] = os.path.dirname(perl) + \
                                os.pathsep + \
                                os.environ["PATH"]

    old_cwd = os.getcwd()
    jaribu:
        os.chdir(ssl_dir)
        ikiwa arch:
            prep(arch)
        isipokua:
            kila arch kwenye ['amd64', 'x86']:
                prep(arch)
    mwishowe:
        os.chdir(old_cwd)

ikiwa __name__=='__main__':
    main()
