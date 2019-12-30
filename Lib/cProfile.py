#! /usr/bin/env python3

"""Python interface for the 'lsprof' profiler.
   Compatible with the 'profile' module.
"""

__all__ = ["run", "runctx", "Profile"]

agiza _lsprof
agiza profile as _pyprofile

# ____________________________________________________________
# Simple interface

def run(statement, filename=None, sort=-1):
    return _pyprofile._Utils(Profile).run(statement, filename, sort)

def runctx(statement, globals, locals, filename=None, sort=-1):
    return _pyprofile._Utils(Profile).runctx(statement, globals, locals,
                                             filename, sort)

run.__doc__ = _pyprofile.run.__doc__
runctx.__doc__ = _pyprofile.runctx.__doc__

# ____________________________________________________________

kundi Profile(_lsprof.Profiler):
    """Profile(timer=None, timeunit=None, subcalls=True, builtins=True)

    Builds a profiler object using the specified timer function.
    The default timer is a fast built-in one based on real time.
    For custom timer functions returning integers, timeunit can
    be a float specifying a scale (i.e. how long each integer unit
    is, in seconds).
    """

    # Most of the functionality is in the base class.
    # This subkundi only adds convenient and backward-compatible methods.

    def print_stats(self, sort=-1):
        agiza pstats
        pstats.Stats(self).strip_dirs().sort_stats(sort).print_stats()

    def dump_stats(self, file):
        agiza marshal
        with open(file, 'wb') as f:
            self.create_stats()
            marshal.dump(self.stats, f)

    def create_stats(self):
        self.disable()
        self.snapshot_stats()

    def snapshot_stats(self):
        entries = self.getstats()
        self.stats = {}
        callersdicts = {}
        # call information
        for entry in entries:
            func = label(entry.code)
            nc = entry.callcount         # ncalls column of pstats (before '/')
            cc = nc - entry.reccallcount # ncalls column of pstats (after '/')
            tt = entry.inlinetime        # tottime column of pstats
            ct = entry.totaltime         # cumtime column of pstats
            callers = {}
            callersdicts[id(entry.code)] = callers
            self.stats[func] = cc, nc, tt, ct, callers
        # subcall information
        for entry in entries:
            if entry.calls:
                func = label(entry.code)
                for subentry in entry.calls:
                    jaribu:
                        callers = callersdicts[id(subentry.code)]
                    tatizo KeyError:
                        endelea
                    nc = subentry.callcount
                    cc = nc - subentry.reccallcount
                    tt = subentry.inlinetime
                    ct = subentry.totaltime
                    if func in callers:
                        prev = callers[func]
                        nc += prev[0]
                        cc += prev[1]
                        tt += prev[2]
                        ct += prev[3]
                    callers[func] = nc, cc, tt, ct

    # The following two methods can be called by clients to use
    # a profiler to profile a statement, given as a string.

    def run(self, cmd):
        agiza __main__
        dict = __main__.__dict__
        return self.runctx(cmd, dict, dict)

    def runctx(self, cmd, globals, locals):
        self.enable()
        jaribu:
            exec(cmd, globals, locals)
        mwishowe:
            self.disable()
        return self

    # This method is more useful to profile a single function call.
    def runcall(*args, **kw):
        if len(args) >= 2:
            self, func, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor 'runcall' of 'Profile' object "
                            "needs an argument")
        lasivyo 'func' in kw:
            func = kw.pop('func')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'func' as keyword argument is deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            ashiria TypeError('runcall expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        self.enable()
        jaribu:
            return func(*args, **kw)
        mwishowe:
            self.disable()
    runcall.__text_signature__ = '($self, func, /, *args, **kw)'

    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, *exc_info):
        self.disable()

# ____________________________________________________________

def label(code):
    if isinstance(code, str):
        return ('~', 0, code)    # built-in functions ('~' sorts at the end)
    isipokua:
        return (code.co_filename, code.co_firstlineno, code.co_name)

# ____________________________________________________________

def main():
    agiza os
    agiza sys
    agiza runpy
    agiza pstats
    kutoka optparse agiza OptionParser
    usage = "cProfile.py [-o output_file_path] [-s sort] [-m module | scriptfile] [arg] ..."
    parser = OptionParser(usage=usage)
    parser.allow_interspersed_args = False
    parser.add_option('-o', '--outfile', dest="outfile",
        help="Save stats to <outfile>", default=None)
    parser.add_option('-s', '--sort', dest="sort",
        help="Sort order when printing to stdout, based on pstats.Stats class",
        default=-1,
        choices=sorted(pstats.Stats.sort_arg_dict_default))
    parser.add_option('-m', dest="module", action="store_true",
        help="Profile a library module", default=False)

    if sio sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)

    (options, args) = parser.parse_args()
    sys.argv[:] = args

    if len(args) > 0:
        if options.module:
            code = "run_module(modname, run_name='__main__')"
            globs = {
                'run_module': runpy.run_module,
                'modname': args[0]
            }
        isipokua:
            progname = args[0]
            sys.path.insert(0, os.path.dirname(progname))
            with open(progname, 'rb') as fp:
                code = compile(fp.read(), progname, 'exec')
            globs = {
                '__file__': progname,
                '__name__': '__main__',
                '__package__': None,
                '__cached__': None,
            }
        runctx(code, globs, None, options.outfile, options.sort)
    isipokua:
        parser.print_usage()
    return parser

# When invoked as main program, invoke the profiler on a script
if __name__ == '__main__':
    main()
