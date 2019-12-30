#! /usr/bin/env python3

"""Python interface kila the 'lsprof' profiler.
   Compatible ukijumuisha the 'profile' module.
"""

__all__ = ["run", "runctx", "Profile"]

agiza _lsprof
agiza profile kama _pyprofile

# ____________________________________________________________
# Simple interface

eleza run(statement, filename=Tupu, sort=-1):
    rudisha _pyprofile._Utils(Profile).run(statement, filename, sort)

eleza runctx(statement, globals, locals, filename=Tupu, sort=-1):
    rudisha _pyprofile._Utils(Profile).runctx(statement, globals, locals,
                                             filename, sort)

run.__doc__ = _pyprofile.run.__doc__
runctx.__doc__ = _pyprofile.runctx.__doc__

# ____________________________________________________________

kundi Profile(_lsprof.Profiler):
    """Profile(timer=Tupu, timeunit=Tupu, subcalls=Kweli, builtins=Kweli)

    Builds a profiler object using the specified timer function.
    The default timer ni a fast built-in one based on real time.
    For custom timer functions returning integers, timeunit can
    be a float specifying a scale (i.e. how long each integer unit
    is, kwenye seconds).
    """

    # Most of the functionality ni kwenye the base class.
    # This subkundi only adds convenient na backward-compatible methods.

    eleza print_stats(self, sort=-1):
        agiza pstats
        pstats.Stats(self).strip_dirs().sort_stats(sort).print_stats()

    eleza dump_stats(self, file):
        agiza marshal
        ukijumuisha open(file, 'wb') kama f:
            self.create_stats()
            marshal.dump(self.stats, f)

    eleza create_stats(self):
        self.disable()
        self.snapshot_stats()

    eleza snapshot_stats(self):
        entries = self.getstats()
        self.stats = {}
        callersdicts = {}
        # call information
        kila entry kwenye entries:
            func = label(entry.code)
            nc = entry.callcount         # ncalls column of pstats (before '/')
            cc = nc - entry.reccallcount # ncalls column of pstats (after '/')
            tt = entry.inlinetime        # tottime column of pstats
            ct = entry.totaltime         # cumtime column of pstats
            callers = {}
            callersdicts[id(entry.code)] = callers
            self.stats[func] = cc, nc, tt, ct, callers
        # subcall information
        kila entry kwenye entries:
            ikiwa entry.calls:
                func = label(entry.code)
                kila subentry kwenye entry.calls:
                    jaribu:
                        callers = callersdicts[id(subentry.code)]
                    tatizo KeyError:
                        endelea
                    nc = subentry.callcount
                    cc = nc - subentry.reccallcount
                    tt = subentry.inlinetime
                    ct = subentry.totaltime
                    ikiwa func kwenye callers:
                        prev = callers[func]
                        nc += prev[0]
                        cc += prev[1]
                        tt += prev[2]
                        ct += prev[3]
                    callers[func] = nc, cc, tt, ct

    # The following two methods can be called by clients to use
    # a profiler to profile a statement, given kama a string.

    eleza run(self, cmd):
        agiza __main__
        dict = __main__.__dict__
        rudisha self.runctx(cmd, dict, dict)

    eleza runctx(self, cmd, globals, locals):
        self.enable()
        jaribu:
            exec(cmd, globals, locals)
        mwishowe:
            self.disable()
        rudisha self

    # This method ni more useful to profile a single function call.
    eleza runcall(*args, **kw):
        ikiwa len(args) >= 2:
            self, func, *args = args
        lasivyo sio args:
            ashiria TypeError("descriptor 'runcall' of 'Profile' object "
                            "needs an argument")
        lasivyo 'func' kwenye kw:
            func = kw.pop('func')
            self, *args = args
            agiza warnings
            warnings.warn("Passing 'func' kama keyword argument ni deprecated",
                          DeprecationWarning, stacklevel=2)
        isipokua:
            ashiria TypeError('runcall expected at least 1 positional argument, '
                            'got %d' % (len(args)-1))

        self.enable()
        jaribu:
            rudisha func(*args, **kw)
        mwishowe:
            self.disable()
    runcall.__text_signature__ = '($self, func, /, *args, **kw)'

    eleza __enter__(self):
        self.enable()
        rudisha self

    eleza __exit__(self, *exc_info):
        self.disable()

# ____________________________________________________________

eleza label(code):
    ikiwa isinstance(code, str):
        rudisha ('~', 0, code)    # built-in functions ('~' sorts at the end)
    isipokua:
        rudisha (code.co_filename, code.co_firstlineno, code.co_name)

# ____________________________________________________________

eleza main():
    agiza os
    agiza sys
    agiza runpy
    agiza pstats
    kutoka optparse agiza OptionParser
    usage = "cProfile.py [-o output_file_path] [-s sort] [-m module | scriptfile] [arg] ..."
    parser = OptionParser(usage=usage)
    parser.allow_interspersed_args = Uongo
    parser.add_option('-o', '--outfile', dest="outfile",
        help="Save stats to <outfile>", default=Tupu)
    parser.add_option('-s', '--sort', dest="sort",
        help="Sort order when printing to stdout, based on pstats.Stats class",
        default=-1,
        choices=sorted(pstats.Stats.sort_arg_dict_default))
    parser.add_option('-m', dest="module", action="store_true",
        help="Profile a library module", default=Uongo)

    ikiwa sio sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)

    (options, args) = parser.parse_args()
    sys.argv[:] = args

    ikiwa len(args) > 0:
        ikiwa options.module:
            code = "run_module(modname, run_name='__main__')"
            globs = {
                'run_module': runpy.run_module,
                'modname': args[0]
            }
        isipokua:
            progname = args[0]
            sys.path.insert(0, os.path.dirname(progname))
            ukijumuisha open(progname, 'rb') kama fp:
                code = compile(fp.read(), progname, 'exec')
            globs = {
                '__file__': progname,
                '__name__': '__main__',
                '__package__': Tupu,
                '__cached__': Tupu,
            }
        runctx(code, globs, Tupu, options.outfile, options.sort)
    isipokua:
        parser.print_usage()
    rudisha parser

# When invoked kama main program, invoke the profiler on a script
ikiwa __name__ == '__main__':
    main()
