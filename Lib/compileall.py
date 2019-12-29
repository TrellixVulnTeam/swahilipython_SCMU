"""Module/script to byte-compile all .py files to .pyc files.

When called kama a script ukijumuisha arguments, this compiles the directories
given kama arguments recursively; the -l option prevents it kutoka
recursing into directories.

Without arguments, ikiwa compiles all modules on sys.path, without
recursing into subdirectories.  (Even though it should do so for
packages -- kila now, you'll have to deal ukijumuisha packages separately.)

See module py_compile kila details of the actual byte-compilation.
"""
agiza os
agiza sys
agiza importlib.util
agiza py_compile
agiza struct

kutoka functools agiza partial

__all__ = ["compile_dir","compile_file","compile_path"]

eleza _walk_dir(dir, ddir=Tupu, maxlevels=10, quiet=0):
    ikiwa quiet < 2 na isinstance(dir, os.PathLike):
        dir = os.fspath(dir)
    ikiwa sio quiet:
        andika('Listing {!r}...'.format(dir))
    jaribu:
        names = os.listdir(dir)
    tatizo OSError:
        ikiwa quiet < 2:
            andika("Can't list {!r}".format(dir))
        names = []
    names.sort()
    kila name kwenye names:
        ikiwa name == '__pycache__':
            endelea
        fullname = os.path.join(dir, name)
        ikiwa ddir ni sio Tupu:
            dfile = os.path.join(ddir, name)
        isipokua:
            dfile = Tupu
        ikiwa sio os.path.isdir(fullname):
            tuma fullname
        lasivyo (maxlevels > 0 na name != os.curdir na name != os.pardir and
              os.path.isdir(fullname) na sio os.path.islink(fullname)):
            tuma kutoka _walk_dir(fullname, ddir=dfile,
                                 maxlevels=maxlevels - 1, quiet=quiet)

eleza compile_dir(dir, maxlevels=10, ddir=Tupu, force=Uongo, rx=Tupu,
                quiet=0, legacy=Uongo, optimize=-1, workers=1,
                invalidation_mode=Tupu):
    """Byte-compile all modules kwenye the given directory tree.

    Arguments (only dir ni required):

    dir:       the directory to byte-compile
    maxlevels: maximum recursion level (default 10)
    ddir:      the directory that will be prepended to the path to the
               file kama it ni compiled into each byte-code file.
    force:     ikiwa Kweli, force compilation, even ikiwa timestamps are up-to-date
    quiet:     full output ukijumuisha Uongo ama 0, errors only ukijumuisha 1,
               no output ukijumuisha 2
    legacy:    ikiwa Kweli, produce legacy pyc paths instead of PEP 3147 paths
    optimize:  optimization level ama -1 kila level of the interpreter
    workers:   maximum number of parallel workers
    invalidation_mode: how the up-to-dateness of the pyc will be checked
    """
    ProcessPoolExecutor = Tupu
    ikiwa workers < 0:
        ashiria ValueError('workers must be greater ama equal to 0')
    ikiwa workers != 1:
        jaribu:
            # Only agiza when needed, kama low resource platforms may
            # fail to agiza it
            kutoka concurrent.futures agiza ProcessPoolExecutor
        tatizo ImportError:
            workers = 1
    files = _walk_dir(dir, quiet=quiet, maxlevels=maxlevels,
                      ddir=ddir)
    success = Kweli
    ikiwa workers != 1 na ProcessPoolExecutor ni sio Tupu:
        # If workers == 0, let ProcessPoolExecutor choose
        workers = workers ama Tupu
        ukijumuisha ProcessPoolExecutor(max_workers=workers) kama executor:
            results = executor.map(partial(compile_file,
                                           ddir=ddir, force=force,
                                           rx=rx, quiet=quiet,
                                           legacy=legacy,
                                           optimize=optimize,
                                           invalidation_mode=invalidation_mode),
                                   files)
            success = min(results, default=Kweli)
    isipokua:
        kila file kwenye files:
            ikiwa sio compile_file(file, ddir, force, rx, quiet,
                                legacy, optimize, invalidation_mode):
                success = Uongo
    rudisha success

eleza compile_file(fullname, ddir=Tupu, force=Uongo, rx=Tupu, quiet=0,
                 legacy=Uongo, optimize=-1,
                 invalidation_mode=Tupu):
    """Byte-compile one file.

    Arguments (only fullname ni required):

    fullname:  the file to byte-compile
    ddir:      ikiwa given, the directory name compiled kwenye to the
               byte-code file.
    force:     ikiwa Kweli, force compilation, even ikiwa timestamps are up-to-date
    quiet:     full output ukijumuisha Uongo ama 0, errors only ukijumuisha 1,
               no output ukijumuisha 2
    legacy:    ikiwa Kweli, produce legacy pyc paths instead of PEP 3147 paths
    optimize:  optimization level ama -1 kila level of the interpreter
    invalidation_mode: how the up-to-dateness of the pyc will be checked
    """
    success = Kweli
    ikiwa quiet < 2 na isinstance(fullname, os.PathLike):
        fullname = os.fspath(fullname)
    name = os.path.basename(fullname)
    ikiwa ddir ni sio Tupu:
        dfile = os.path.join(ddir, name)
    isipokua:
        dfile = Tupu
    ikiwa rx ni sio Tupu:
        mo = rx.search(fullname)
        ikiwa mo:
            rudisha success
    ikiwa os.path.isfile(fullname):
        ikiwa legacy:
            cfile = fullname + 'c'
        isipokua:
            ikiwa optimize >= 0:
                opt = optimize ikiwa optimize >= 1 isipokua ''
                cfile = importlib.util.cache_kutoka_source(
                                fullname, optimization=opt)
            isipokua:
                cfile = importlib.util.cache_kutoka_source(fullname)
            cache_dir = os.path.dirname(cfile)
        head, tail = name[:-3], name[-3:]
        ikiwa tail == '.py':
            ikiwa sio force:
                jaribu:
                    mtime = int(os.stat(fullname).st_mtime)
                    expect = struct.pack('<4sll', importlib.util.MAGIC_NUMBER,
                                         0, mtime)
                    ukijumuisha open(cfile, 'rb') kama chandle:
                        actual = chandle.read(12)
                    ikiwa expect == actual:
                        rudisha success
                tatizo OSError:
                    pita
            ikiwa sio quiet:
                andika('Compiling {!r}...'.format(fullname))
            jaribu:
                ok = py_compile.compile(fullname, cfile, dfile, Kweli,
                                        optimize=optimize,
                                        invalidation_mode=invalidation_mode)
            tatizo py_compile.PyCompileError kama err:
                success = Uongo
                ikiwa quiet >= 2:
                    rudisha success
                lasivyo quiet:
                    andika('*** Error compiling {!r}...'.format(fullname))
                isipokua:
                    andika('*** ', end='')
                # escape non-printable characters kwenye msg
                msg = err.msg.encode(sys.stdout.encoding,
                                     errors='backslashreplace')
                msg = msg.decode(sys.stdout.encoding)
                andika(msg)
            tatizo (SyntaxError, UnicodeError, OSError) kama e:
                success = Uongo
                ikiwa quiet >= 2:
                    rudisha success
                lasivyo quiet:
                    andika('*** Error compiling {!r}...'.format(fullname))
                isipokua:
                    andika('*** ', end='')
                andika(e.__class__.__name__ + ':', e)
            isipokua:
                ikiwa ok == 0:
                    success = Uongo
    rudisha success

eleza compile_path(skip_curdir=1, maxlevels=0, force=Uongo, quiet=0,
                 legacy=Uongo, optimize=-1,
                 invalidation_mode=Tupu):
    """Byte-compile all module on sys.path.

    Arguments (all optional):

    skip_curdir: ikiwa true, skip current directory (default Kweli)
    maxlevels:   max recursion level (default 0)
    force: kama kila compile_dir() (default Uongo)
    quiet: kama kila compile_dir() (default 0)
    legacy: kama kila compile_dir() (default Uongo)
    optimize: kama kila compile_dir() (default -1)
    invalidation_mode: kama kila compiler_dir()
    """
    success = Kweli
    kila dir kwenye sys.path:
        ikiwa (not dir ama dir == os.curdir) na skip_curdir:
            ikiwa quiet < 2:
                andika('Skipping current directory')
        isipokua:
            success = success na compile_dir(
                dir,
                maxlevels,
                Tupu,
                force,
                quiet=quiet,
                legacy=legacy,
                optimize=optimize,
                invalidation_mode=invalidation_mode,
            )
    rudisha success


eleza main():
    """Script main program."""
    agiza argparse

    parser = argparse.ArgumentParser(
        description='Utilities to support installing Python libraries.')
    parser.add_argument('-l', action='store_const', const=0,
                        default=10, dest='maxlevels',
                        help="don't recurse into subdirectories")
    parser.add_argument('-r', type=int, dest='recursion',
                        help=('control the maximum recursion level. '
                              'ikiwa `-l` na `-r` options are specified, '
                              'then `-r` takes precedence.'))
    parser.add_argument('-f', action='store_true', dest='force',
                        help='force rebuild even ikiwa timestamps are up to date')
    parser.add_argument('-q', action='count', dest='quiet', default=0,
                        help='output only error messages; -qq will suppress '
                             'the error messages kama well.')
    parser.add_argument('-b', action='store_true', dest='legacy',
                        help='use legacy (pre-PEP3147) compiled file locations')
    parser.add_argument('-d', metavar='DESTDIR',  dest='ddir', default=Tupu,
                        help=('directory to prepend to file paths kila use kwenye '
                              'compile-time tracebacks na kwenye runtime '
                              'tracebacks kwenye cases where the source file ni '
                              'unavailable'))
    parser.add_argument('-x', metavar='REGEXP', dest='rx', default=Tupu,
                        help=('skip files matching the regular expression; '
                              'the regexp ni searched kila kwenye the full path '
                              'of each file considered kila compilation'))
    parser.add_argument('-i', metavar='FILE', dest='flist',
                        help=('add all the files na directories listed kwenye '
                              'FILE to the list considered kila compilation; '
                              'ikiwa "-", names are read kutoka stdin'))
    parser.add_argument('compile_dest', metavar='FILE|DIR', nargs='*',
                        help=('zero ama more file na directory names '
                              'to compile; ikiwa no arguments given, defaults '
                              'to the equivalent of -l sys.path'))
    parser.add_argument('-j', '--workers', default=1,
                        type=int, help='Run compileall concurrently')
    invalidation_modes = [mode.name.lower().replace('_', '-')
                          kila mode kwenye py_compile.PycInvalidationMode]
    parser.add_argument('--invalidation-mode',
                        choices=sorted(invalidation_modes),
                        help=('set .pyc invalidation mode; defaults to '
                              '"checked-hash" ikiwa the SOURCE_DATE_EPOCH '
                              'environment variable ni set, na '
                              '"timestamp" otherwise.'))

    args = parser.parse_args()
    compile_dests = args.compile_dest

    ikiwa args.rx:
        agiza re
        args.rx = re.compile(args.rx)


    ikiwa args.recursion ni sio Tupu:
        maxlevels = args.recursion
    isipokua:
        maxlevels = args.maxlevels

    # ikiwa flist ni provided then load it
    ikiwa args.flist:
        jaribu:
            ukijumuisha (sys.stdin ikiwa args.flist=='-' isipokua open(args.flist)) kama f:
                kila line kwenye f:
                    compile_dests.append(line.strip())
        tatizo OSError:
            ikiwa args.quiet < 2:
                andika("Error reading file list {}".format(args.flist))
            rudisha Uongo

    ikiwa args.invalidation_mode:
        ivl_mode = args.invalidation_mode.replace('-', '_').upper()
        invalidation_mode = py_compile.PycInvalidationMode[ivl_mode]
    isipokua:
        invalidation_mode = Tupu

    success = Kweli
    jaribu:
        ikiwa compile_dests:
            kila dest kwenye compile_dests:
                ikiwa os.path.isfile(dest):
                    ikiwa sio compile_file(dest, args.ddir, args.force, args.rx,
                                        args.quiet, args.legacy,
                                        invalidation_mode=invalidation_mode):
                        success = Uongo
                isipokua:
                    ikiwa sio compile_dir(dest, maxlevels, args.ddir,
                                       args.force, args.rx, args.quiet,
                                       args.legacy, workers=args.workers,
                                       invalidation_mode=invalidation_mode):
                        success = Uongo
            rudisha success
        isipokua:
            rudisha compile_path(legacy=args.legacy, force=args.force,
                                quiet=args.quiet,
                                invalidation_mode=invalidation_mode)
    tatizo KeyboardInterrupt:
        ikiwa args.quiet < 2:
            andika("\n[interrupted]")
        rudisha Uongo
    rudisha Kweli


ikiwa __name__ == '__main__':
    exit_status = int(not main())
    sys.exit(exit_status)
