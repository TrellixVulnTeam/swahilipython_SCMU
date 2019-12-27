"""Module/script to byte-compile all .py files to .pyc files.

When called as a script with arguments, this compiles the directories
given as arguments recursively; the -l option prevents it kutoka
recursing into directories.

Without arguments, ikiwa compiles all modules on sys.path, without
recursing into subdirectories.  (Even though it should do so for
packages -- for now, you'll have to deal with packages separately.)

See module py_compile for details of the actual byte-compilation.
"""
agiza os
agiza sys
agiza importlib.util
agiza py_compile
agiza struct

kutoka functools agiza partial

__all__ = ["compile_dir","compile_file","compile_path"]

eleza _walk_dir(dir, ddir=None, maxlevels=10, quiet=0):
    ikiwa quiet < 2 and isinstance(dir, os.PathLike):
        dir = os.fspath(dir)
    ikiwa not quiet:
        andika('Listing {!r}...'.format(dir))
    try:
        names = os.listdir(dir)
    except OSError:
        ikiwa quiet < 2:
            andika("Can't list {!r}".format(dir))
        names = []
    names.sort()
    for name in names:
        ikiwa name == '__pycache__':
            continue
        fullname = os.path.join(dir, name)
        ikiwa ddir is not None:
            dfile = os.path.join(ddir, name)
        else:
            dfile = None
        ikiwa not os.path.isdir(fullname):
            yield fullname
        elikiwa (maxlevels > 0 and name != os.curdir and name != os.pardir and
              os.path.isdir(fullname) and not os.path.islink(fullname)):
            yield kutoka _walk_dir(fullname, ddir=dfile,
                                 maxlevels=maxlevels - 1, quiet=quiet)

eleza compile_dir(dir, maxlevels=10, ddir=None, force=False, rx=None,
                quiet=0, legacy=False, optimize=-1, workers=1,
                invalidation_mode=None):
    """Byte-compile all modules in the given directory tree.

    Arguments (only dir is required):

    dir:       the directory to byte-compile
    maxlevels: maximum recursion level (default 10)
    ddir:      the directory that will be prepended to the path to the
               file as it is compiled into each byte-code file.
    force:     ikiwa True, force compilation, even ikiwa timestamps are up-to-date
    quiet:     full output with False or 0, errors only with 1,
               no output with 2
    legacy:    ikiwa True, produce legacy pyc paths instead of PEP 3147 paths
    optimize:  optimization level or -1 for level of the interpreter
    workers:   maximum number of parallel workers
    invalidation_mode: how the up-to-dateness of the pyc will be checked
    """
    ProcessPoolExecutor = None
    ikiwa workers < 0:
        raise ValueError('workers must be greater or equal to 0')
    ikiwa workers != 1:
        try:
            # Only agiza when needed, as low resource platforms may
            # fail to agiza it
            kutoka concurrent.futures agiza ProcessPoolExecutor
        except ImportError:
            workers = 1
    files = _walk_dir(dir, quiet=quiet, maxlevels=maxlevels,
                      ddir=ddir)
    success = True
    ikiwa workers != 1 and ProcessPoolExecutor is not None:
        # If workers == 0, let ProcessPoolExecutor choose
        workers = workers or None
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results = executor.map(partial(compile_file,
                                           ddir=ddir, force=force,
                                           rx=rx, quiet=quiet,
                                           legacy=legacy,
                                           optimize=optimize,
                                           invalidation_mode=invalidation_mode),
                                   files)
            success = min(results, default=True)
    else:
        for file in files:
            ikiwa not compile_file(file, ddir, force, rx, quiet,
                                legacy, optimize, invalidation_mode):
                success = False
    rudisha success

eleza compile_file(fullname, ddir=None, force=False, rx=None, quiet=0,
                 legacy=False, optimize=-1,
                 invalidation_mode=None):
    """Byte-compile one file.

    Arguments (only fullname is required):

    fullname:  the file to byte-compile
    ddir:      ikiwa given, the directory name compiled in to the
               byte-code file.
    force:     ikiwa True, force compilation, even ikiwa timestamps are up-to-date
    quiet:     full output with False or 0, errors only with 1,
               no output with 2
    legacy:    ikiwa True, produce legacy pyc paths instead of PEP 3147 paths
    optimize:  optimization level or -1 for level of the interpreter
    invalidation_mode: how the up-to-dateness of the pyc will be checked
    """
    success = True
    ikiwa quiet < 2 and isinstance(fullname, os.PathLike):
        fullname = os.fspath(fullname)
    name = os.path.basename(fullname)
    ikiwa ddir is not None:
        dfile = os.path.join(ddir, name)
    else:
        dfile = None
    ikiwa rx is not None:
        mo = rx.search(fullname)
        ikiwa mo:
            rudisha success
    ikiwa os.path.isfile(fullname):
        ikiwa legacy:
            cfile = fullname + 'c'
        else:
            ikiwa optimize >= 0:
                opt = optimize ikiwa optimize >= 1 else ''
                cfile = importlib.util.cache_kutoka_source(
                                fullname, optimization=opt)
            else:
                cfile = importlib.util.cache_kutoka_source(fullname)
            cache_dir = os.path.dirname(cfile)
        head, tail = name[:-3], name[-3:]
        ikiwa tail == '.py':
            ikiwa not force:
                try:
                    mtime = int(os.stat(fullname).st_mtime)
                    expect = struct.pack('<4sll', importlib.util.MAGIC_NUMBER,
                                         0, mtime)
                    with open(cfile, 'rb') as chandle:
                        actual = chandle.read(12)
                    ikiwa expect == actual:
                        rudisha success
                except OSError:
                    pass
            ikiwa not quiet:
                andika('Compiling {!r}...'.format(fullname))
            try:
                ok = py_compile.compile(fullname, cfile, dfile, True,
                                        optimize=optimize,
                                        invalidation_mode=invalidation_mode)
            except py_compile.PyCompileError as err:
                success = False
                ikiwa quiet >= 2:
                    rudisha success
                elikiwa quiet:
                    andika('*** Error compiling {!r}...'.format(fullname))
                else:
                    andika('*** ', end='')
                # escape non-printable characters in msg
                msg = err.msg.encode(sys.stdout.encoding,
                                     errors='backslashreplace')
                msg = msg.decode(sys.stdout.encoding)
                andika(msg)
            except (SyntaxError, UnicodeError, OSError) as e:
                success = False
                ikiwa quiet >= 2:
                    rudisha success
                elikiwa quiet:
                    andika('*** Error compiling {!r}...'.format(fullname))
                else:
                    andika('*** ', end='')
                andika(e.__class__.__name__ + ':', e)
            else:
                ikiwa ok == 0:
                    success = False
    rudisha success

eleza compile_path(skip_curdir=1, maxlevels=0, force=False, quiet=0,
                 legacy=False, optimize=-1,
                 invalidation_mode=None):
    """Byte-compile all module on sys.path.

    Arguments (all optional):

    skip_curdir: ikiwa true, skip current directory (default True)
    maxlevels:   max recursion level (default 0)
    force: as for compile_dir() (default False)
    quiet: as for compile_dir() (default 0)
    legacy: as for compile_dir() (default False)
    optimize: as for compile_dir() (default -1)
    invalidation_mode: as for compiler_dir()
    """
    success = True
    for dir in sys.path:
        ikiwa (not dir or dir == os.curdir) and skip_curdir:
            ikiwa quiet < 2:
                andika('Skipping current directory')
        else:
            success = success and compile_dir(
                dir,
                maxlevels,
                None,
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
                              'ikiwa `-l` and `-r` options are specified, '
                              'then `-r` takes precedence.'))
    parser.add_argument('-f', action='store_true', dest='force',
                        help='force rebuild even ikiwa timestamps are up to date')
    parser.add_argument('-q', action='count', dest='quiet', default=0,
                        help='output only error messages; -qq will suppress '
                             'the error messages as well.')
    parser.add_argument('-b', action='store_true', dest='legacy',
                        help='use legacy (pre-PEP3147) compiled file locations')
    parser.add_argument('-d', metavar='DESTDIR',  dest='ddir', default=None,
                        help=('directory to prepend to file paths for use in '
                              'compile-time tracebacks and in runtime '
                              'tracebacks in cases where the source file is '
                              'unavailable'))
    parser.add_argument('-x', metavar='REGEXP', dest='rx', default=None,
                        help=('skip files matching the regular expression; '
                              'the regexp is searched for in the full path '
                              'of each file considered for compilation'))
    parser.add_argument('-i', metavar='FILE', dest='flist',
                        help=('add all the files and directories listed in '
                              'FILE to the list considered for compilation; '
                              'ikiwa "-", names are read kutoka stdin'))
    parser.add_argument('compile_dest', metavar='FILE|DIR', nargs='*',
                        help=('zero or more file and directory names '
                              'to compile; ikiwa no arguments given, defaults '
                              'to the equivalent of -l sys.path'))
    parser.add_argument('-j', '--workers', default=1,
                        type=int, help='Run compileall concurrently')
    invalidation_modes = [mode.name.lower().replace('_', '-')
                          for mode in py_compile.PycInvalidationMode]
    parser.add_argument('--invalidation-mode',
                        choices=sorted(invalidation_modes),
                        help=('set .pyc invalidation mode; defaults to '
                              '"checked-hash" ikiwa the SOURCE_DATE_EPOCH '
                              'environment variable is set, and '
                              '"timestamp" otherwise.'))

    args = parser.parse_args()
    compile_dests = args.compile_dest

    ikiwa args.rx:
        agiza re
        args.rx = re.compile(args.rx)


    ikiwa args.recursion is not None:
        maxlevels = args.recursion
    else:
        maxlevels = args.maxlevels

    # ikiwa flist is provided then load it
    ikiwa args.flist:
        try:
            with (sys.stdin ikiwa args.flist=='-' else open(args.flist)) as f:
                for line in f:
                    compile_dests.append(line.strip())
        except OSError:
            ikiwa args.quiet < 2:
                andika("Error reading file list {}".format(args.flist))
            rudisha False

    ikiwa args.invalidation_mode:
        ivl_mode = args.invalidation_mode.replace('-', '_').upper()
        invalidation_mode = py_compile.PycInvalidationMode[ivl_mode]
    else:
        invalidation_mode = None

    success = True
    try:
        ikiwa compile_dests:
            for dest in compile_dests:
                ikiwa os.path.isfile(dest):
                    ikiwa not compile_file(dest, args.ddir, args.force, args.rx,
                                        args.quiet, args.legacy,
                                        invalidation_mode=invalidation_mode):
                        success = False
                else:
                    ikiwa not compile_dir(dest, maxlevels, args.ddir,
                                       args.force, args.rx, args.quiet,
                                       args.legacy, workers=args.workers,
                                       invalidation_mode=invalidation_mode):
                        success = False
            rudisha success
        else:
            rudisha compile_path(legacy=args.legacy, force=args.force,
                                quiet=args.quiet,
                                invalidation_mode=invalidation_mode)
    except KeyboardInterrupt:
        ikiwa args.quiet < 2:
            andika("\n[interrupted]")
        rudisha False
    rudisha True


ikiwa __name__ == '__main__':
    exit_status = int(not main())
    sys.exit(exit_status)
