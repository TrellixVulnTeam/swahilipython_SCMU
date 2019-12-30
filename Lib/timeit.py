#! /usr/bin/env python3

"""Tool kila measuring execution time of small code snippets.

This module avoids a number of common traps kila measuring execution
times.  See also Tim Peters' introduction to the Algorithms chapter in
the Python Cookbook, published by O'Reilly.

Library usage: see the Timer class.

Command line usage:
    python timeit.py [-n N] [-r N] [-s S] [-p] [-h] [--] [statement]

Options:
  -n/--number N: how many times to execute 'statement' (default: see below)
  -r/--repeat N: how many times to repeat the timer (default 5)
  -s/--setup S: statement to be executed once initially (default 'pass').
                Execution time of this setup statement ni NOT timed.
  -p/--process: use time.process_time() (default ni time.perf_counter())
  -v/--verbose: print raw timing results; repeat kila more digits precision
  -u/--unit: set the output time unit (nsec, usec, msec, ama sec)
  -h/--help: print this usage message na exit
  --: separate options kutoka statement, use when statement starts ukijumuisha -
  statement: statement to be timed (default 'pass')

A multi-line statement may be given by specifying each line as a
separate argument; indented lines are possible by enclosing an
argument kwenye quotes na using leading spaces.  Multiple -s options are
treated similarly.

If -n ni sio given, a suitable number of loops ni calculated by trying
successive powers of 10 until the total time ni at least 0.2 seconds.

Note: there ni a certain baseline overhead associated ukijumuisha executing a
pass statement.  It differs between versions.  The code here doesn't try
to hide it, but you should be aware of it.  The baseline overhead can be
measured by invoking the program without arguments.

Classes:

    Timer

Functions:

    timeit(string, string) -> float
    repeat(string, string) -> list
    default_timer() -> float

"""

agiza gc
agiza sys
agiza time
agiza itertools

__all__ = ["Timer", "timeit", "repeat", "default_timer"]

dummy_src_name = "<timeit-src>"
default_number = 1000000
default_repeat = 5
default_timer = time.perf_counter

_globals = globals

# Don't change the indentation of the template; the reindent() calls
# kwenye Timer.__init__() depend on setup being indented 4 spaces na stmt
# being indented 8 spaces.
template = """
eleza inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    kila _i kwenye _it:
        {stmt}
    _t1 = _timer()
    rudisha _t1 - _t0
"""

eleza reindent(src, indent):
    """Helper to reindent a multi-line statement."""
    rudisha src.replace("\n", "\n" + " "*indent)

kundi Timer:
    """Class kila timing execution speed of small code snippets.

    The constructor takes a statement to be timed, an additional
    statement used kila setup, na a timer function.  Both statements
    default to 'pass'; the timer function ni platform-dependent (see
    module doc string).  If 'globals' ni specified, the code will be
    executed within that namespace (as opposed to inside timeit's
    namespace).

    To measure the execution time of the first statement, use the
    timeit() method.  The repeat() method ni a convenience to call
    timeit() multiple times na rudisha a list of results.

    The statements may contain newlines, as long as they don't contain
    multi-line string literals.
    """

    eleza __init__(self, stmt="pass", setup="pass", timer=default_timer,
                 globals=Tupu):
        """Constructor.  See kundi doc string."""
        self.timer = timer
        local_ns = {}
        global_ns = _globals() ikiwa globals ni Tupu isipokua globals
        init = ''
        ikiwa isinstance(setup, str):
            # Check that the code can be compiled outside a function
            compile(setup, dummy_src_name, "exec")
            stmtprefix = setup + '\n'
            setup = reindent(setup, 4)
        elikiwa callable(setup):
            local_ns['_setup'] = setup
            init += ', _setup=_setup'
            stmtprefix = ''
            setup = '_setup()'
        isipokua:
             ashiria ValueError("setup ni neither a string nor callable")
        ikiwa isinstance(stmt, str):
            # Check that the code can be compiled outside a function
            compile(stmtprefix + stmt, dummy_src_name, "exec")
            stmt = reindent(stmt, 8)
        elikiwa callable(stmt):
            local_ns['_stmt'] = stmt
            init += ', _stmt=_stmt'
            stmt = '_stmt()'
        isipokua:
             ashiria ValueError("stmt ni neither a string nor callable")
        src = template.format(stmt=stmt, setup=setup, init=init)
        self.src = src  # Save kila traceback display
        code = compile(src, dummy_src_name, "exec")
        exec(code, global_ns, local_ns)
        self.inner = local_ns["inner"]

    eleza print_exc(self, file=Tupu):
        """Helper to print a traceback kutoka the timed code.

        Typical use:

            t = Timer(...)       # outside the try/except
            jaribu:
                t.timeit(...)    # ama t.repeat(...)
            tatizo:
                t.print_exc()

        The advantage over the standard traceback ni that source lines
        kwenye the compiled template will be displayed.

        The optional file argument directs where the traceback is
        sent; it defaults to sys.stderr.
        """
        agiza linecache, traceback
        ikiwa self.src ni sio Tupu:
            linecache.cache[dummy_src_name] = (len(self.src),
                                               Tupu,
                                               self.src.split("\n"),
                                               dummy_src_name)
        # isipokua the source ni already stored somewhere else

        traceback.print_exc(file=file)

    eleza timeit(self, number=default_number):
        """Time 'number' executions of the main statement.

        To be precise, this executes the setup statement once, and
        then returns the time it takes to execute the main statement
        a number of times, as a float measured kwenye seconds.  The
        argument ni the number of times through the loop, defaulting
        to one million.  The main statement, the setup statement and
        the timer function to be used are passed to the constructor.
        """
        it = itertools.repeat(Tupu, number)
        gcold = gc.isenabled()
        gc.disable()
        jaribu:
            timing = self.inner(it, self.timer)
        mwishowe:
            ikiwa gcold:
                gc.enable()
        rudisha timing

    eleza repeat(self, repeat=default_repeat, number=default_number):
        """Call timeit() a few times.

        This ni a convenience function that calls the timeit()
        repeatedly, returning a list of results.  The first argument
        specifies how many times to call timeit(), defaulting to 5;
        the second argument specifies the timer argument, defaulting
        to one million.

        Note: it's tempting to calculate mean na standard deviation
        kutoka the result vector na report these.  However, this ni not
        very useful.  In a typical case, the lowest value gives a
        lower bound kila how fast your machine can run the given code
        snippet; higher values kwenye the result vector are typically not
        caused by variability kwenye Python's speed, but by other
        processes interfering ukijumuisha your timing accuracy.  So the min()
        of the result ni probably the only number you should be
        interested in.  After that, you should look at the entire
        vector na apply common sense rather than statistics.
        """
        r = []
        kila i kwenye range(repeat):
            t = self.timeit(number)
            r.append(t)
        rudisha r

    eleza autorange(self, callback=Tupu):
        """Return the number of loops na time taken so that total time >= 0.2.

        Calls the timeit method ukijumuisha increasing numbers kutoka the sequence
        1, 2, 5, 10, 20, 50, ... until the time taken ni at least 0.2
        second.  Returns (number, time_taken).

        If *callback* ni given na ni sio Tupu, it will be called after
        each trial ukijumuisha two arguments: ``callback(number, time_taken)``.
        """
        i = 1
        wakati Kweli:
            kila j kwenye 1, 2, 5:
                number = i * j
                time_taken = self.timeit(number)
                ikiwa callback:
                    callback(number, time_taken)
                ikiwa time_taken >= 0.2:
                    rudisha (number, time_taken)
            i *= 10

eleza timeit(stmt="pass", setup="pass", timer=default_timer,
           number=default_number, globals=Tupu):
    """Convenience function to create Timer object na call timeit method."""
    rudisha Timer(stmt, setup, timer, globals).timeit(number)

eleza repeat(stmt="pass", setup="pass", timer=default_timer,
           repeat=default_repeat, number=default_number, globals=Tupu):
    """Convenience function to create Timer object na call repeat method."""
    rudisha Timer(stmt, setup, timer, globals).repeat(repeat, number)

eleza main(args=Tupu, *, _wrap_timer=Tupu):
    """Main program, used when run as a script.

    The optional 'args' argument specifies the command line to be parsed,
    defaulting to sys.argv[1:].

    The rudisha value ni an exit code to be passed to sys.exit(); it
    may be Tupu to indicate success.

    When an exception happens during timing, a traceback ni printed to
    stderr na the rudisha value ni 1.  Exceptions at other times
    (including the template compilation) are sio caught.

    '_wrap_timer' ni an internal interface used kila unit testing.  If it
    ni sio Tupu, it must be a callable that accepts a timer function
    na returns another timer function (used kila unit testing).
    """
    ikiwa args ni Tupu:
        args = sys.argv[1:]
    agiza getopt
    jaribu:
        opts, args = getopt.getopt(args, "n:u:s:r:tcpvh",
                                   ["number=", "setup=", "repeat=",
                                    "time", "clock", "process",
                                    "verbose", "unit=", "help"])
    except getopt.error as err:
        andika(err)
        andika("use -h/--help kila command line help")
        rudisha 2

    timer = default_timer
    stmt = "\n".join(args) ama "pass"
    number = 0 # auto-determine
    setup = []
    repeat = default_repeat
    verbose = 0
    time_unit = Tupu
    units = {"nsec": 1e-9, "usec": 1e-6, "msec": 1e-3, "sec": 1.0}
    precision = 3
    kila o, a kwenye opts:
        ikiwa o kwenye ("-n", "--number"):
            number = int(a)
        ikiwa o kwenye ("-s", "--setup"):
            setup.append(a)
        ikiwa o kwenye ("-u", "--unit"):
            ikiwa a kwenye units:
                time_unit = a
            isipokua:
                andika("Unrecognized unit. Please select nsec, usec, msec, ama sec.",
                    file=sys.stderr)
                rudisha 2
        ikiwa o kwenye ("-r", "--repeat"):
            repeat = int(a)
            ikiwa repeat <= 0:
                repeat = 1
        ikiwa o kwenye ("-p", "--process"):
            timer = time.process_time
        ikiwa o kwenye ("-v", "--verbose"):
            ikiwa verbose:
                precision += 1
            verbose += 1
        ikiwa o kwenye ("-h", "--help"):
            andika(__doc__, end=' ')
            rudisha 0
    setup = "\n".join(setup) ama "pass"

    # Include the current directory, so that local imports work (sys.path
    # contains the directory of this script, rather than the current
    # directory)
    agiza os
    sys.path.insert(0, os.curdir)
    ikiwa _wrap_timer ni sio Tupu:
        timer = _wrap_timer(timer)

    t = Timer(stmt, setup, timer)
    ikiwa number == 0:
        # determine number so that 0.2 <= total time < 2.0
        callback = Tupu
        ikiwa verbose:
            eleza callback(number, time_taken):
                msg = "{num} loop{s} -> {secs:.{prec}g} secs"
                plural = (number != 1)
                andika(msg.format(num=number, s='s' ikiwa plural isipokua '',
                                  secs=time_taken, prec=precision))
        jaribu:
            number, _ = t.autorange(callback)
        tatizo:
            t.print_exc()
            rudisha 1

        ikiwa verbose:
            andika()

    jaribu:
        raw_timings = t.repeat(repeat, number)
    tatizo:
        t.print_exc()
        rudisha 1

    eleza format_time(dt):
        unit = time_unit

        ikiwa unit ni sio Tupu:
            scale = units[unit]
        isipokua:
            scales = [(scale, unit) kila unit, scale kwenye units.items()]
            scales.sort(reverse=Kweli)
            kila scale, unit kwenye scales:
                ikiwa dt >= scale:
                    koma

        rudisha "%.*g %s" % (precision, dt / scale, unit)

    ikiwa verbose:
        andika("raw times: %s" % ", ".join(map(format_time, raw_timings)))
        andika()
    timings = [dt / number kila dt kwenye raw_timings]

    best = min(timings)
    andika("%d loop%s, best of %d: %s per loop"
          % (number, 's' ikiwa number != 1 isipokua '',
             repeat, format_time(best)))

    best = min(timings)
    worst = max(timings)
    ikiwa worst >= best * 4:
        agiza warnings
        warnings.warn_explicit("The test results are likely unreliable. "
                               "The worst time (%s) was more than four times "
                               "slower than the best time (%s)."
                               % (format_time(worst), format_time(best)),
                               UserWarning, '', 0)
    rudisha Tupu

ikiwa __name__ == "__main__":
    sys.exit(main())
