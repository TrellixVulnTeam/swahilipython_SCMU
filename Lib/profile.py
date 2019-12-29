#! /usr/bin/env python3
#
# Class kila profiling python code. rev 1.0  6/2/94
#
# Written by James Roskind
# Based on prior profile module by Sjoerd Mullender...
#   which was hacked somewhat by: Guido van Rossum

"""Class kila profiling Python code."""

# Copyright Disney Enterprises, Inc.  All Rights Reserved.
# Licensed to PSF under a Contributor Agreement
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may sio use this file tatizo kwenye compliance ukijumuisha the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law ama agreed to kwenye writing, software
# distributed under the License ni distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express ama implied.  See the License kila the specific language
# governing permissions na limitations under the License.


agiza sys
agiza time
agiza marshal

__all__ = ["run", "runctx", "Profile"]

# Sample timer kila use with
#i_count = 0
#eleza integer_timer():
#       global i_count
#       i_count = i_count + 1
#       rudisha i_count
#itimes = integer_timer # replace ukijumuisha C coded timer rudishaing integers

kundi _Utils:
    """Support kundi kila utility functions which are shared by
    profile.py na cProfile.py modules.
    Not supposed to be used directly.
    """

    eleza __init__(self, profiler):
        self.profiler = profiler

    eleza run(self, statement, filename, sort):
        prof = self.profiler()
        jaribu:
            prof.run(statement)
        tatizo SystemExit:
            pita
        mwishowe:
            self._show(prof, filename, sort)

    eleza runctx(self, statement, globals, locals, filename, sort):
        prof = self.profiler()
        jaribu:
            prof.runctx(statement, globals, locals)
        tatizo SystemExit:
            pita
        mwishowe:
            self._show(prof, filename, sort)

    eleza _show(self, prof, filename, sort):
        ikiwa filename ni sio Tupu:
            prof.dump_stats(filename)
        isipokua:
            prof.print_stats(sort)


#**************************************************************************
# The following are the static member functions kila the profiler class
# Note that an instance of Profile() ni *not* needed to call them.
#**************************************************************************

eleza run(statement, filename=Tupu, sort=-1):
    """Run statement under profiler optionally saving results kwenye filename

    This function takes a single argument that can be pitaed to the
    "exec" statement, na an optional file name.  In all cases this
    routine attempts to "exec" its first argument na gather profiling
    statistics kutoka the execution. If no file name ni present, then this
    function automatically prints a simple profiling report, sorted by the
    standard name string (file/line/function-name) that ni presented in
    each line.
    """
    rudisha _Utils(Profile).run(statement, filename, sort)

eleza runctx(statement, globals, locals, filename=Tupu, sort=-1):
    """Run statement under profiler, supplying your own globals na locals,
    optionally saving results kwenye filename.

    statement na filename have the same semantics kama profile.run
    """
    rudisha _Utils(Profile).runctx(statement, globals, locals, filename, sort)


kundi Profile:
    """Profiler class.

    self.cur ni always a tuple.  Each such tuple corresponds to a stack
    frame that ni currently active (self.cur[-2]).  The following are the
    definitions of its members.  We use this external "parallel stack" to
    avoid contaminating the program that we are profiling. (old profiler
    used to write into the frames local dictionary!!) Derived classes
    can change the definition of some entries, kama long kama they leave
    [-2:] intact (frame na previous tuple).  In case an internal error is
    detected, the -3 element ni used kama the function name.

    [ 0] = Time that needs to be charged to the parent frame's function.
           It ni used so that a function call will sio have to access the
           timing data kila the parent frame.
    [ 1] = Total time spent kwenye this frame's function, excluding time in
           subfunctions (this latter ni tallied kwenye cur[2]).
    [ 2] = Total time spent kwenye subfunctions, excluding time executing the
           frame's function (this latter ni tallied kwenye cur[1]).
    [-3] = Name of the function that corresponds to this frame.
    [-2] = Actual frame that we correspond to (used to sync exception handling).
    [-1] = Our parent 6-tuple (corresponds to frame.f_back).

    Timing data kila each function ni stored kama a 5-tuple kwenye the dictionary
    self.timings[].  The index ni always the name stored kwenye self.cur[-3].
    The following are the definitions of the members:

    [0] = The number of times this function was called, sio counting direct
          ama indirect recursion,
    [1] = Number of times this function appears on the stack, minus one
    [2] = Total time spent internal to this function
    [3] = Cumulative time that this function was present on the stack.  In
          non-recursive functions, this ni the total execution time kutoka start
          to finish of each invocation of a function, including time spent in
          all subfunctions.
    [4] = A dictionary indicating kila each function name, the number of times
          it was called by us.
    """

    bias = 0  # calibration constant

    eleza __init__(self, timer=Tupu, bias=Tupu):
        self.timings = {}
        self.cur = Tupu
        self.cmd = ""
        self.c_func_name = ""

        ikiwa bias ni Tupu:
            bias = self.bias
        self.bias = bias     # Materialize kwenye local dict kila lookup speed.

        ikiwa sio timer:
            self.timer = self.get_time = time.process_time
            self.dispatcher = self.trace_dispatch_i
        isipokua:
            self.timer = timer
            t = self.timer() # test out timer function
            jaribu:
                length = len(t)
            tatizo TypeError:
                self.get_time = timer
                self.dispatcher = self.trace_dispatch_i
            isipokua:
                ikiwa length == 2:
                    self.dispatcher = self.trace_dispatch
                isipokua:
                    self.dispatcher = self.trace_dispatch_l
                # This get_time() implementation needs to be defined
                # here to capture the pitaed-in timer kwenye the parameter
                # list (kila performance).  Note that we can't assume
                # the timer() result contains two values kwenye all
                # cases.
                eleza get_time_timer(timer=timer, sum=sum):
                    rudisha sum(timer())
                self.get_time = get_time_timer
        self.t = self.get_time()
        self.simulate_call('profiler')

    # Heavily optimized dispatch routine kila time.process_time() timer

    eleza trace_dispatch(self, frame, event, arg):
        timer = self.timer
        t = timer()
        t = t[0] + t[1] - self.t - self.bias

        ikiwa event == "c_call":
            self.c_func_name = arg.__name__

        ikiwa self.dispatch[event](self, frame,t):
            t = timer()
            self.t = t[0] + t[1]
        isipokua:
            r = timer()
            self.t = r[0] + r[1] - t # put back unrecorded delta

    # Dispatch routine kila best timer program (rudisha = scalar, fastest if
    # an integer but float works too -- na time.process_time() relies on that).

    eleza trace_dispatch_i(self, frame, event, arg):
        timer = self.timer
        t = timer() - self.t - self.bias

        ikiwa event == "c_call":
            self.c_func_name = arg.__name__

        ikiwa self.dispatch[event](self, frame, t):
            self.t = timer()
        isipokua:
            self.t = timer() - t  # put back unrecorded delta

    # Dispatch routine kila macintosh (timer rudishas time kwenye ticks of
    # 1/60th second)

    eleza trace_dispatch_mac(self, frame, event, arg):
        timer = self.timer
        t = timer()/60.0 - self.t - self.bias

        ikiwa event == "c_call":
            self.c_func_name = arg.__name__

        ikiwa self.dispatch[event](self, frame, t):
            self.t = timer()/60.0
        isipokua:
            self.t = timer()/60.0 - t  # put back unrecorded delta

    # SLOW generic dispatch routine kila timer rudishaing lists of numbers

    eleza trace_dispatch_l(self, frame, event, arg):
        get_time = self.get_time
        t = get_time() - self.t - self.bias

        ikiwa event == "c_call":
            self.c_func_name = arg.__name__

        ikiwa self.dispatch[event](self, frame, t):
            self.t = get_time()
        isipokua:
            self.t = get_time() - t # put back unrecorded delta

    # In the event handlers, the first 3 elements of self.cur are unpacked
    # into vrbls w/ 3-letter names.  The last two characters are meant to be
    # mnemonic:
    #     _pt  self.cur[0] "parent time"   time to be charged to parent frame
    #     _it  self.cur[1] "internal time" time spent directly kwenye the function
    #     _et  self.cur[2] "external time" time spent kwenye subfunctions

    eleza trace_dispatch_exception(self, frame, t):
        rpt, rit, ret, rfn, rframe, rcur = self.cur
        ikiwa (rframe ni sio frame) na rcur:
            rudisha self.trace_dispatch_rudisha(rframe, t)
        self.cur = rpt, rit+t, ret, rfn, rframe, rcur
        rudisha 1


    eleza trace_dispatch_call(self, frame, t):
        ikiwa self.cur na frame.f_back ni sio self.cur[-2]:
            rpt, rit, ret, rfn, rframe, rcur = self.cur
            ikiwa sio isinstance(rframe, Profile.fake_frame):
                assert rframe.f_back ni frame.f_back, ("Bad call", rfn,
                                                       rframe, rframe.f_back,
                                                       frame, frame.f_back)
                self.trace_dispatch_rudisha(rframe, 0)
                assert (self.cur ni Tupu ama \
                        frame.f_back ni self.cur[-2]), ("Bad call",
                                                        self.cur[-3])
        fcode = frame.f_code
        fn = (fcode.co_filename, fcode.co_firstlineno, fcode.co_name)
        self.cur = (t, 0, 0, fn, frame, self.cur)
        timings = self.timings
        ikiwa fn kwenye timings:
            cc, ns, tt, ct, callers = timings[fn]
            timings[fn] = cc, ns + 1, tt, ct, callers
        isipokua:
            timings[fn] = 0, 0, 0, 0, {}
        rudisha 1

    eleza trace_dispatch_c_call (self, frame, t):
        fn = ("", 0, self.c_func_name)
        self.cur = (t, 0, 0, fn, frame, self.cur)
        timings = self.timings
        ikiwa fn kwenye timings:
            cc, ns, tt, ct, callers = timings[fn]
            timings[fn] = cc, ns+1, tt, ct, callers
        isipokua:
            timings[fn] = 0, 0, 0, 0, {}
        rudisha 1

    eleza trace_dispatch_rudisha(self, frame, t):
        ikiwa frame ni sio self.cur[-2]:
            assert frame ni self.cur[-2].f_back, ("Bad rudisha", self.cur[-3])
            self.trace_dispatch_rudisha(self.cur[-2], 0)

        # Prefix "r" means part of the Returning ama exiting frame.
        # Prefix "p" means part of the Previous ama Parent ama older frame.

        rpt, rit, ret, rfn, frame, rcur = self.cur
        rit = rit + t
        frame_total = rit + ret

        ppt, pit, pet, pfn, pframe, pcur = rcur
        self.cur = ppt, pit + rpt, pet + frame_total, pfn, pframe, pcur

        timings = self.timings
        cc, ns, tt, ct, callers = timings[rfn]
        ikiwa sio ns:
            # This ni the only occurrence of the function on the stack.
            # Else this ni a (directly ama indirectly) recursive call, and
            # its cumulative time will get updated when the topmost call to
            # it rudishas.
            ct = ct + frame_total
            cc = cc + 1

        ikiwa pfn kwenye callers:
            callers[pfn] = callers[pfn] + 1  # hack: gather more
            # stats such kama the amount of time added to ct courtesy
            # of this specific call, na the contribution to cc
            # courtesy of this call.
        isipokua:
            callers[pfn] = 1

        timings[rfn] = cc, ns - 1, tt + rit, ct, callers

        rudisha 1


    dispatch = {
        "call": trace_dispatch_call,
        "exception": trace_dispatch_exception,
        "rudisha": trace_dispatch_rudisha,
        "c_call": trace_dispatch_c_call,
        "c_exception": trace_dispatch_rudisha,  # the C function rudishaed
        "c_rudisha": trace_dispatch_rudisha,
        }


    # The next few functions play ukijumuisha self.cmd. By carefully preloading
    # our parallel stack, we can force the profiled result to include
    # an arbitrary string kama the name of the calling function.
    # We use self.cmd kama that string, na the resulting stats look
    # very nice :-).

    eleza set_cmd(self, cmd):
        ikiwa self.cur[-1]: rudisha   # already set
        self.cmd = cmd
        self.simulate_call(cmd)

    kundi fake_code:
        eleza __init__(self, filename, line, name):
            self.co_filename = filename
            self.co_line = line
            self.co_name = name
            self.co_firstlineno = 0

        eleza __repr__(self):
            rudisha repr((self.co_filename, self.co_line, self.co_name))

    kundi fake_frame:
        eleza __init__(self, code, prior):
            self.f_code = code
            self.f_back = prior

    eleza simulate_call(self, name):
        code = self.fake_code('profile', 0, name)
        ikiwa self.cur:
            pframe = self.cur[-2]
        isipokua:
            pframe = Tupu
        frame = self.fake_frame(code, pframe)
        self.dispatch['call'](self, frame, 0)

    # collect stats kutoka pending stack, including getting final
    # timings kila self.cmd frame.

    eleza simulate_cmd_complete(self):
        get_time = self.get_time
        t = get_time() - self.t
        wakati self.cur[-1]:
            # We *can* cause assertion errors here if
            # dispatch_trace_rudisha checks kila a frame match!
            self.dispatch['rudisha'](self, self.cur[-2], t)
            t = 0
        self.t = get_time() - t


    eleza print_stats(self, sort=-1):
        agiza pstats
        pstats.Stats(self).strip_dirs().sort_stats(sort). \
                  print_stats()

    eleza dump_stats(self, file):
        ukijumuisha open(file, 'wb') kama f:
            self.create_stats()
            marshal.dump(self.stats, f)

    eleza create_stats(self):
        self.simulate_cmd_complete()
        self.snapshot_stats()

    eleza snapshot_stats(self):
        self.stats = {}
        kila func, (cc, ns, tt, ct, callers) kwenye self.timings.items():
            callers = callers.copy()
            nc = 0
            kila callcnt kwenye callers.values():
                nc += callcnt
            self.stats[func] = cc, nc, tt, ct, callers


    # The following two methods can be called by clients to use
    # a profiler to profile a statement, given kama a string.

    eleza run(self, cmd):
        agiza __main__
        dict = __main__.__dict__
        rudisha self.runctx(cmd, dict, dict)

    eleza runctx(self, cmd, globals, locals):
        self.set_cmd(cmd)
        sys.setprofile(self.dispatcher)
        jaribu:
            exec(cmd, globals, locals)
        mwishowe:
            sys.setprofile(Tupu)
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

        self.set_cmd(repr(func))
        sys.setprofile(self.dispatcher)
        jaribu:
            rudisha func(*args, **kw)
        mwishowe:
            sys.setprofile(Tupu)
    runcall.__text_signature__ = '($self, func, /, *args, **kw)'


    #******************************************************************
    # The following calculates the overhead kila using a profiler.  The
    # problem ni that it takes a fair amount of time kila the profiler
    # to stop the stopwatch (kutoka the time it receives an event).
    # Similarly, there ni a delay kutoka the time that the profiler
    # re-starts the stopwatch before the user's code really gets to
    # endelea.  The following code tries to measure the difference on
    # a per-event basis.
    #
    # Note that this difference ni only significant ikiwa there are a lot of
    # events, na relatively little user code per event.  For example,
    # code ukijumuisha small functions will typically benefit kutoka having the
    # profiler calibrated kila the current platform.  This *could* be
    # done on the fly during init() time, but it ni sio worth the
    # effort.  Also note that ikiwa too large a value specified, then
    # execution time on some functions will actually appear kama a
    # negative number.  It ni *normal* kila some functions (ukijumuisha very
    # low call counts) to have such negative stats, even ikiwa the
    # calibration figure ni "correct."
    #
    # One alternative to profile-time calibration adjustments (i.e.,
    # adding kwenye the magic little delta during each event) ni to track
    # more carefully the number of events (and cumulatively, the number
    # of events during sub functions) that are seen.  If this were
    # done, then the arithmetic could be done after the fact (i.e., at
    # display time).  Currently, we track only call/rudisha events.
    # These values can be deduced by examining the callees na callers
    # vectors kila each functions.  Hence we *can* almost correct the
    # internal time figure at print time (note that we currently don't
    # track exception event processing counts).  Unfortunately, there
    # ni currently no similar information kila cumulative sub-function
    # time.  It would sio be hard to "get all this info" at profiler
    # time.  Specifically, we would have to extend the tuples to keep
    # counts of this kwenye each frame, na then extend the defs of timing
    # tuples to include the significant two figures. I'm a bit fearful
    # that this additional feature will slow the heavily optimized
    # event/time ratio (i.e., the profiler would run slower, fur a very
    # low "value added" feature.)
    #**************************************************************

    eleza calibrate(self, m, verbose=0):
        ikiwa self.__class__ ni sio Profile:
            ashiria TypeError("Subclasses must override .calibrate().")

        saved_bias = self.bias
        self.bias = 0
        jaribu:
            rudisha self._calibrate_inner(m, verbose)
        mwishowe:
            self.bias = saved_bias

    eleza _calibrate_inner(self, m, verbose):
        get_time = self.get_time

        # Set up a test case to be run ukijumuisha na without profiling.  Include
        # lots of calls, because we're trying to quantify stopwatch overhead.
        # Do sio ashiria any exceptions, though, because we want to know
        # exactly how many profile events are generated (one call event, +
        # one rudisha event, per Python-level call).

        eleza f1(n):
            kila i kwenye range(n):
                x = 1

        eleza f(m, f1=f1):
            kila i kwenye range(m):
                f1(100)

        f(m)    # warm up the cache

        # elapsed_noprofile <- time f(m) takes without profiling.
        t0 = get_time()
        f(m)
        t1 = get_time()
        elapsed_noprofile = t1 - t0
        ikiwa verbose:
            andika("elapsed time without profiling =", elapsed_noprofile)

        # elapsed_profile <- time f(m) takes ukijumuisha profiling.  The difference
        # ni profiling overhead, only some of which the profiler subtracts
        # out on its own.
        p = Profile()
        t0 = get_time()
        p.runctx('f(m)', globals(), locals())
        t1 = get_time()
        elapsed_profile = t1 - t0
        ikiwa verbose:
            andika("elapsed time ukijumuisha profiling =", elapsed_profile)

        # reported_time <- "CPU seconds" the profiler charged to f na f1.
        total_calls = 0.0
        reported_time = 0.0
        kila (filename, line, funcname), (cc, ns, tt, ct, callers) kwenye \
                p.timings.items():
            ikiwa funcname kwenye ("f", "f1"):
                total_calls += cc
                reported_time += tt

        ikiwa verbose:
            andika("'CPU seconds' profiler reported =", reported_time)
            andika("total # calls =", total_calls)
        ikiwa total_calls != m + 1:
            ashiria ValueError("internal error: total calls = %d" % total_calls)

        # reported_time - elapsed_noprofile = overhead the profiler wasn't
        # able to measure.  Divide by twice the number of calls (since there
        # are two profiler events per call kwenye this test) to get the hidden
        # overhead per event.
        mean = (reported_time - elapsed_noprofile) / 2.0 / total_calls
        ikiwa verbose:
            andika("mean stopwatch overhead per profile event =", mean)
        rudisha mean

#****************************************************************************

eleza main():
    agiza os
    kutoka optparse agiza OptionParser

    usage = "profile.py [-o output_file_path] [-s sort] [-m module | scriptfile] [arg] ..."
    parser = OptionParser(usage=usage)
    parser.allow_interspersed_args = Uongo
    parser.add_option('-o', '--outfile', dest="outfile",
        help="Save stats to <outfile>", default=Tupu)
    parser.add_option('-m', dest="module", action="store_true",
        help="Profile a library module.", default=Uongo)
    parser.add_option('-s', '--sort', dest="sort",
        help="Sort order when printing to stdout, based on pstats.Stats class",
        default=-1)

    ikiwa sio sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)

    (options, args) = parser.parse_args()
    sys.argv[:] = args

    ikiwa len(args) > 0:
        ikiwa options.module:
            agiza runpy
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
