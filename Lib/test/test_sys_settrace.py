# Testing the line trace facility.

kutoka test agiza support
agiza unittest
agiza sys
agiza difflib
agiza gc
kutoka functools agiza wraps
agiza asyncio


kundi tracecontext:
    """Context manager that traces its enter na exit."""
    eleza __init__(self, output, value):
        self.output = output
        self.value = value

    eleza __enter__(self):
        self.output.append(self.value)

    eleza __exit__(self, *exc_info):
        self.output.append(-self.value)

kundi asynctracecontext:
    """Asynchronous context manager that traces its aenter na aexit."""
    eleza __init__(self, output, value):
        self.output = output
        self.value = value

    async eleza __aenter__(self):
        self.output.append(self.value)

    async eleza __aexit__(self, *exc_info):
        self.output.append(-self.value)

async eleza asynciter(iterable):
    """Convert an iterable to an asynchronous iterator."""
    kila x kwenye iterable:
        tuma x


# A very basic example.  If this fails, we're kwenye deep trouble.
eleza basic():
    rudisha 1

basic.events = [(0, 'call'),
                (1, 'line'),
                (1, 'rudisha')]

# Many of the tests below are tricky because they involve pita statements.
# If there ni implicit control flow around a pita statement (in an except
# clause ama else clause) under what conditions do you set a line number
# following that clause?


# Some constructs like "wakati 0:", "ikiwa 0:" ama "ikiwa 1:...isipokua:..." are optimized
# away.  No code # exists kila them, so the line numbers skip directly kutoka
# "toa x" to "x = 1".
eleza arigo_example0():
    x = 1
    toa x
    wakati 0:
        pita
    x = 1

arigo_example0.events = [(0, 'call'),
                        (1, 'line'),
                        (2, 'line'),
                        (5, 'line'),
                        (5, 'rudisha')]

eleza arigo_example1():
    x = 1
    toa x
    ikiwa 0:
        pita
    x = 1

arigo_example1.events = [(0, 'call'),
                        (1, 'line'),
                        (2, 'line'),
                        (5, 'line'),
                        (5, 'rudisha')]

eleza arigo_example2():
    x = 1
    toa x
    ikiwa 1:
        x = 1
    isipokua:
        pita
    rudisha Tupu

arigo_example2.events = [(0, 'call'),
                        (1, 'line'),
                        (2, 'line'),
                        (4, 'line'),
                        (7, 'line'),
                        (7, 'rudisha')]


# check that lines consisting of just one instruction get traced:
eleza one_instr_line():
    x = 1
    toa x
    x = 1

one_instr_line.events = [(0, 'call'),
                         (1, 'line'),
                         (2, 'line'),
                         (3, 'line'),
                         (3, 'rudisha')]

eleza no_pop_tops():      # 0
    x = 1               # 1
    kila a kwenye range(2):  # 2
        ikiwa a:           # 3
            x = 1       # 4
        isipokua:           # 5
            x = 1       # 6

no_pop_tops.events = [(0, 'call'),
                      (1, 'line'),
                      (2, 'line'),
                      (3, 'line'),
                      (6, 'line'),
                      (2, 'line'),
                      (3, 'line'),
                      (4, 'line'),
                      (2, 'line'),
                      (2, 'rudisha')]

eleza no_pop_blocks():
    y = 1
    wakati sio y:
        bla
    x = 1

no_pop_blocks.events = [(0, 'call'),
                        (1, 'line'),
                        (2, 'line'),
                        (4, 'line'),
                        (4, 'rudisha')]

eleza called(): # line -3
    x = 1

eleza call():   # line 0
    called()

call.events = [(0, 'call'),
               (1, 'line'),
               (-3, 'call'),
               (-2, 'line'),
               (-2, 'rudisha'),
               (1, 'rudisha')]

eleza ashirias():
    ashiria Exception

eleza test_ashiria():
    jaribu:
        ashirias()
    tatizo Exception kama exc:
        x = 1

test_ashiria.events = [(0, 'call'),
                     (1, 'line'),
                     (2, 'line'),
                     (-3, 'call'),
                     (-2, 'line'),
                     (-2, 'exception'),
                     (-2, 'rudisha'),
                     (2, 'exception'),
                     (3, 'line'),
                     (4, 'line'),
                     (4, 'rudisha')]

eleza _settrace_and_rudisha(tracefunc):
    sys.settrace(tracefunc)
    sys._getframe().f_back.f_trace = tracefunc
eleza settrace_and_rudisha(tracefunc):
    _settrace_and_rudisha(tracefunc)

settrace_and_rudisha.events = [(1, 'rudisha')]

eleza _settrace_and_ashiria(tracefunc):
    sys.settrace(tracefunc)
    sys._getframe().f_back.f_trace = tracefunc
    ashiria RuntimeError
eleza settrace_and_ashiria(tracefunc):
    jaribu:
        _settrace_and_ashiria(tracefunc)
    tatizo RuntimeError kama exc:
        pita

settrace_and_ashiria.events = [(2, 'exception'),
                             (3, 'line'),
                             (4, 'line'),
                             (4, 'rudisha')]

# implicit rudisha example
# This test ni interesting because of the isipokua: pita
# part of the code.  The code generate kila the true
# part of the ikiwa contains a jump past the else branch.
# The compiler then generates an implicit "rudisha Tupu"
# Internally, the compiler visits the pita statement
# na stores its line number kila use on the next instruction.
# The next instruction ni the implicit rudisha Tupu.
eleza irudisha_example():
    a = 5
    b = 5
    ikiwa a == b:
        b = a+1
    isipokua:
        pita

irudisha_example.events = [(0, 'call'),
                          (1, 'line'),
                          (2, 'line'),
                          (3, 'line'),
                          (4, 'line'),
                          (6, 'line'),
                          (6, 'rudisha')]

# Tight loop with while(1) example (SF #765624)
eleza tightloop_example():
    items = range(0, 3)
    jaribu:
        i = 0
        wakati 1:
            b = items[i]; i+=1
    tatizo IndexError:
        pita

tightloop_example.events = [(0, 'call'),
                            (1, 'line'),
                            (2, 'line'),
                            (3, 'line'),
                            (5, 'line'),
                            (5, 'line'),
                            (5, 'line'),
                            (5, 'line'),
                            (5, 'exception'),
                            (6, 'line'),
                            (7, 'line'),
                            (7, 'rudisha')]

eleza tighterloop_example():
    items = range(1, 4)
    jaribu:
        i = 0
        wakati 1: i = items[i]
    tatizo IndexError:
        pita

tighterloop_example.events = [(0, 'call'),
                            (1, 'line'),
                            (2, 'line'),
                            (3, 'line'),
                            (4, 'line'),
                            (4, 'line'),
                            (4, 'line'),
                            (4, 'line'),
                            (4, 'exception'),
                            (5, 'line'),
                            (6, 'line'),
                            (6, 'rudisha')]

eleza generator_function():
    jaribu:
        tuma Kweli
        "endelead"
    mwishowe:
        "finally"
eleza generator_example():
    # any() will leave the generator before its end
    x = any(generator_function())

    # the following lines were sio traced
    kila x kwenye range(10):
        y = x

generator_example.events = ([(0, 'call'),
                             (2, 'line'),
                             (-6, 'call'),
                             (-5, 'line'),
                             (-4, 'line'),
                             (-4, 'rudisha'),
                             (-4, 'call'),
                             (-4, 'exception'),
                             (-1, 'line'),
                             (-1, 'rudisha')] +
                            [(5, 'line'), (6, 'line')] * 10 +
                            [(5, 'line'), (5, 'rudisha')])


kundi Tracer:
    eleza __init__(self, trace_line_events=Tupu, trace_opcode_events=Tupu):
        self.trace_line_events = trace_line_events
        self.trace_opcode_events = trace_opcode_events
        self.events = []

    eleza _reconfigure_frame(self, frame):
        ikiwa self.trace_line_events ni sio Tupu:
            frame.f_trace_lines = self.trace_line_events
        ikiwa self.trace_opcode_events ni sio Tupu:
            frame.f_trace_opcodes = self.trace_opcode_events

    eleza trace(self, frame, event, arg):
        self._reconfigure_frame(frame)
        self.events.append((frame.f_lineno, event))
        rudisha self.trace

    eleza traceWithGenexp(self, frame, event, arg):
        self._reconfigure_frame(frame)
        (o kila o kwenye [1])
        self.events.append((frame.f_lineno, event))
        rudisha self.trace


kundi TraceTestCase(unittest.TestCase):

    # Disable gc collection when tracing, otherwise the
    # deallocators may be traced kama well.
    eleza setUp(self):
        self.using_gc = gc.isenabled()
        gc.disable()
        self.addCleanup(sys.settrace, sys.gettrace())

    eleza tearDown(self):
        ikiwa self.using_gc:
            gc.enable()

    @staticmethod
    eleza make_tracer():
        """Helper to allow test subclasses to configure tracers differently"""
        rudisha Tracer()

    eleza compare_events(self, line_offset, events, expected_events):
        events = [(l - line_offset, e) kila (l, e) kwenye events]
        ikiwa events != expected_events:
            self.fail(
                "events did sio match expectation:\n" +
                "\n".join(difflib.ndiff([str(x) kila x kwenye expected_events],
                                        [str(x) kila x kwenye events])))

    eleza run_and_compare(self, func, events):
        tracer = self.make_tracer()
        sys.settrace(tracer.trace)
        func()
        sys.settrace(Tupu)
        self.compare_events(func.__code__.co_firstlineno,
                            tracer.events, events)

    eleza run_test(self, func):
        self.run_and_compare(func, func.events)

    eleza run_test2(self, func):
        tracer = self.make_tracer()
        func(tracer.trace)
        sys.settrace(Tupu)
        self.compare_events(func.__code__.co_firstlineno,
                            tracer.events, func.events)

    eleza test_set_and_retrieve_none(self):
        sys.settrace(Tupu)
        assert sys.gettrace() ni Tupu

    eleza test_set_and_retrieve_func(self):
        eleza fn(*args):
            pita

        sys.settrace(fn)
        jaribu:
            assert sys.gettrace() ni fn
        mwishowe:
            sys.settrace(Tupu)

    eleza test_01_basic(self):
        self.run_test(basic)
    eleza test_02_arigo0(self):
        self.run_test(arigo_example0)
    eleza test_02_arigo1(self):
        self.run_test(arigo_example1)
    eleza test_02_arigo2(self):
        self.run_test(arigo_example2)
    eleza test_03_one_instr(self):
        self.run_test(one_instr_line)
    eleza test_04_no_pop_blocks(self):
        self.run_test(no_pop_blocks)
    eleza test_05_no_pop_tops(self):
        self.run_test(no_pop_tops)
    eleza test_06_call(self):
        self.run_test(call)
    eleza test_07_ashiria(self):
        self.run_test(test_ashiria)

    eleza test_08_settrace_and_rudisha(self):
        self.run_test2(settrace_and_rudisha)
    eleza test_09_settrace_and_ashiria(self):
        self.run_test2(settrace_and_ashiria)
    eleza test_10_irudisha(self):
        self.run_test(irudisha_example)
    eleza test_11_tightloop(self):
        self.run_test(tightloop_example)
    eleza test_12_tighterloop(self):
        self.run_test(tighterloop_example)

    eleza test_13_genexp(self):
        self.run_test(generator_example)
        # issue1265: ikiwa the trace function contains a generator,
        # na ikiwa the traced function contains another generator
        # that ni sio completely exhausted, the trace stopped.
        # Worse: the 'finally' clause was sio invoked.
        tracer = self.make_tracer()
        sys.settrace(tracer.traceWithGenexp)
        generator_example()
        sys.settrace(Tupu)
        self.compare_events(generator_example.__code__.co_firstlineno,
                            tracer.events, generator_example.events)

    eleza test_14_onliner_if(self):
        eleza onliners():
            ikiwa Kweli: x=Uongo
            isipokua: x=Kweli
            rudisha 0
        self.run_and_compare(
            onliners,
            [(0, 'call'),
             (1, 'line'),
             (3, 'line'),
             (3, 'rudisha')])

    eleza test_15_loops(self):
        # issue1750076: "while" expression ni skipped by debugger
        eleza for_example():
            kila x kwenye range(2):
                pita
        self.run_and_compare(
            for_example,
            [(0, 'call'),
             (1, 'line'),
             (2, 'line'),
             (1, 'line'),
             (2, 'line'),
             (1, 'line'),
             (1, 'rudisha')])

        eleza while_example():
            # While expression should be traced on every loop
            x = 2
            wakati x > 0:
                x -= 1
        self.run_and_compare(
            while_example,
            [(0, 'call'),
             (2, 'line'),
             (3, 'line'),
             (4, 'line'),
             (3, 'line'),
             (4, 'line'),
             (3, 'line'),
             (3, 'rudisha')])

    eleza test_16_blank_lines(self):
        namespace = {}
        exec("eleza f():\n" + "\n" * 256 + "    pita", namespace)
        self.run_and_compare(
            namespace["f"],
            [(0, 'call'),
             (257, 'line'),
             (257, 'rudisha')])

    eleza test_17_none_f_trace(self):
        # Issue 20041: fix TypeError when f_trace ni set to Tupu.
        eleza func():
            sys._getframe().f_trace = Tupu
            lineno = 2
        self.run_and_compare(func,
            [(0, 'call'),
             (1, 'line')])


kundi SkipLineEventsTraceTestCase(TraceTestCase):
    """Repeat the trace tests, but with per-line events skipped"""

    eleza compare_events(self, line_offset, events, expected_events):
        skip_line_events = [e kila e kwenye expected_events ikiwa e[1] != 'line']
        super().compare_events(line_offset, events, skip_line_events)

    @staticmethod
    eleza make_tracer():
        rudisha Tracer(trace_line_events=Uongo)


@support.cpython_only
kundi TraceOpcodesTestCase(TraceTestCase):
    """Repeat the trace tests, but with per-opcodes events enabled"""

    eleza compare_events(self, line_offset, events, expected_events):
        skip_opcode_events = [e kila e kwenye events ikiwa e[1] != 'opcode']
        ikiwa len(events) > 1:
            self.assertLess(len(skip_opcode_events), len(events),
                            msg="No 'opcode' events received by the tracer")
        super().compare_events(line_offset, skip_opcode_events, expected_events)

    @staticmethod
    eleza make_tracer():
        rudisha Tracer(trace_opcode_events=Kweli)


kundi RaisingTraceFuncTestCase(unittest.TestCase):
    eleza setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())

    eleza trace(self, frame, event, arg):
        """A trace function that ashirias an exception kwenye response to a
        specific trace event."""
        ikiwa event == self.ashiriaOnEvent:
            ashiria ValueError # just something that isn't RuntimeError
        isipokua:
            rudisha self.trace

    eleza f(self):
        """The function to trace; ashirias an exception ikiwa that's the case
        we're testing, so that the 'exception' trace event fires."""
        ikiwa self.ashiriaOnEvent == 'exception':
            x = 0
            y = 1/x
        isipokua:
            rudisha 1

    eleza run_test_for_event(self, event):
        """Tests that an exception ashiriad kwenye response to the given event is
        handled OK."""
        self.ashiriaOnEvent = event
        jaribu:
            kila i kwenye range(sys.getrecursionlimit() + 1):
                sys.settrace(self.trace)
                jaribu:
                    self.f()
                tatizo ValueError:
                    pita
                isipokua:
                    self.fail("exception sio ashiriad!")
        tatizo RuntimeError:
            self.fail("recursion counter sio reset")

    # Test the handling of exceptions ashiriad by each kind of trace event.
    eleza test_call(self):
        self.run_test_for_event('call')
    eleza test_line(self):
        self.run_test_for_event('line')
    eleza test_rudisha(self):
        self.run_test_for_event('rudisha')
    eleza test_exception(self):
        self.run_test_for_event('exception')

    eleza test_trash_stack(self):
        eleza f():
            kila i kwenye range(5):
                andika(i)  # line tracing will ashiria an exception at this line

        eleza g(frame, why, extra):
            ikiwa (why == 'line' and
                frame.f_lineno == f.__code__.co_firstlineno + 2):
                ashiria RuntimeError("i am crashing")
            rudisha g

        sys.settrace(g)
        jaribu:
            f()
        tatizo RuntimeError:
            # the test ni really that this doesn't segfault:
            agiza gc
            gc.collect()
        isipokua:
            self.fail("exception sio propagated")


    eleza test_exception_arguments(self):
        eleza f():
            x = 0
            # this should ashiria an error
            x.no_such_attr
        eleza g(frame, event, arg):
            ikiwa (event == 'exception'):
                type, exception, trace = arg
                self.assertIsInstance(exception, Exception)
            rudisha g

        existing = sys.gettrace()
        jaribu:
            sys.settrace(g)
            jaribu:
                f()
            tatizo AttributeError:
                # this ni expected
                pita
        mwishowe:
            sys.settrace(existing)


# 'Jump' tests: assigning to frame.f_lineno within a trace function
# moves the execution position - it's how debuggers implement a Jump
# command (aka. "Set next statement").

kundi JumpTracer:
    """Defines a trace function that jumps kutoka one place to another."""

    eleza __init__(self, function, jumpFrom, jumpTo, event='line',
                 decorated=Uongo):
        self.code = function.__code__
        self.jumpFrom = jumpFrom
        self.jumpTo = jumpTo
        self.event = event
        self.firstLine = Tupu ikiwa decorated else self.code.co_firstlineno
        self.done = Uongo

    eleza trace(self, frame, event, arg):
        ikiwa self.done:
            rudisha
        # frame.f_code.co_firstlineno ni the first line of the decorator when
        # 'function' ni decorated na the decorator may be written using
        # multiple physical lines when it ni too long. Use the first line
        # trace event kwenye 'function' to find the first line of 'function'.
        ikiwa (self.firstLine ni Tupu na frame.f_code == self.code and
                event == 'line'):
            self.firstLine = frame.f_lineno - 1
        ikiwa (event == self.event na self.firstLine and
                frame.f_lineno == self.firstLine + self.jumpFrom):
            f = frame
            wakati f ni sio Tupu na f.f_code != self.code:
                f = f.f_back
            ikiwa f ni sio Tupu:
                # Cope with non-integer self.jumpTo (because of
                # no_jump_to_non_integers below).
                jaribu:
                    frame.f_lineno = self.firstLine + self.jumpTo
                tatizo TypeError:
                    frame.f_lineno = self.jumpTo
                self.done = Kweli
        rudisha self.trace

# This verifies the line-numbers-must-be-integers rule.
eleza no_jump_to_non_integers(output):
    jaribu:
        output.append(2)
    tatizo ValueError kama e:
        output.append('integer' kwenye str(e))

# This verifies that you can't set f_lineno via _getframe ama similar
# trickery.
eleza no_jump_without_trace_function():
    jaribu:
        previous_frame = sys._getframe().f_back
        previous_frame.f_lineno = previous_frame.f_lineno
    tatizo ValueError kama e:
        # This ni the exception we wanted; make sure the error message
        # talks about trace functions.
        ikiwa 'trace' haiko kwenye str(e):
            ashiria
    isipokua:
        # Something's wrong - the expected exception wasn't ashiriad.
        ashiria AssertionError("Trace-function-less jump failed to fail")


kundi JumpTestCase(unittest.TestCase):
    eleza setUp(self):
        self.addCleanup(sys.settrace, sys.gettrace())
        sys.settrace(Tupu)

    eleza compare_jump_output(self, expected, received):
        ikiwa received != expected:
            self.fail( "Outputs don't match:\n" +
                       "Expected: " + repr(expected) + "\n" +
                       "Received: " + repr(received))

    eleza run_test(self, func, jumpFrom, jumpTo, expected, error=Tupu,
                 event='line', decorated=Uongo):
        tracer = JumpTracer(func, jumpFrom, jumpTo, event, decorated)
        sys.settrace(tracer.trace)
        output = []
        ikiwa error ni Tupu:
            func(output)
        isipokua:
            with self.assertRaisesRegex(*error):
                func(output)
        sys.settrace(Tupu)
        self.compare_jump_output(expected, output)

    eleza run_async_test(self, func, jumpFrom, jumpTo, expected, error=Tupu,
                 event='line', decorated=Uongo):
        tracer = JumpTracer(func, jumpFrom, jumpTo, event, decorated)
        sys.settrace(tracer.trace)
        output = []
        ikiwa error ni Tupu:
            asyncio.run(func(output))
        isipokua:
            with self.assertRaisesRegex(*error):
                asyncio.run(func(output))
        sys.settrace(Tupu)
        asyncio.set_event_loop_policy(Tupu)
        self.compare_jump_output(expected, output)

    eleza jump_test(jumpFrom, jumpTo, expected, error=Tupu, event='line'):
        """Decorator that creates a test that makes a jump
        kutoka one place to another kwenye the following code.
        """
        eleza decorator(func):
            @wraps(func)
            eleza test(self):
                self.run_test(func, jumpFrom, jumpTo, expected,
                              error=error, event=event, decorated=Kweli)
            rudisha test
        rudisha decorator

    eleza async_jump_test(jumpFrom, jumpTo, expected, error=Tupu, event='line'):
        """Decorator that creates a test that makes a jump
        kutoka one place to another kwenye the following asynchronous code.
        """
        eleza decorator(func):
            @wraps(func)
            eleza test(self):
                self.run_async_test(func, jumpFrom, jumpTo, expected,
                              error=error, event=event, decorated=Kweli)
            rudisha test
        rudisha decorator

    ## The first set of 'jump' tests are kila things that are allowed:

    @jump_test(1, 3, [3])
    eleza test_jump_simple_forwards(output):
        output.append(1)
        output.append(2)
        output.append(3)

    @jump_test(2, 1, [1, 1, 2])
    eleza test_jump_simple_backwards(output):
        output.append(1)
        output.append(2)

    @jump_test(3, 5, [2, 5])
    eleza test_jump_out_of_block_forwards(output):
        kila i kwenye 1, 2:
            output.append(2)
            kila j kwenye [3]:  # Also tests jumping over a block
                output.append(4)
        output.append(5)

    @jump_test(6, 1, [1, 3, 5, 1, 3, 5, 6, 7])
    eleza test_jump_out_of_block_backwards(output):
        output.append(1)
        kila i kwenye [1]:
            output.append(3)
            kila j kwenye [2]:  # Also tests jumping over a block
                output.append(5)
            output.append(6)
        output.append(7)

    @async_jump_test(4, 5, [3, 5])
    async eleza test_jump_out_of_async_for_block_forwards(output):
        kila i kwenye [1]:
            async kila i kwenye asynciter([1, 2]):
                output.append(3)
                output.append(4)
            output.append(5)

    @async_jump_test(5, 2, [2, 4, 2, 4, 5, 6])
    async eleza test_jump_out_of_async_for_block_backwards(output):
        kila i kwenye [1]:
            output.append(2)
            async kila i kwenye asynciter([1]):
                output.append(4)
                output.append(5)
            output.append(6)

    @jump_test(1, 2, [3])
    eleza test_jump_to_codeless_line(output):
        output.append(1)
        # Jumping to this line should skip to the next one.
        output.append(3)

    @jump_test(2, 2, [1, 2, 3])
    eleza test_jump_to_same_line(output):
        output.append(1)
        output.append(2)
        output.append(3)

    # Tests jumping within a finally block, na over one.
    @jump_test(4, 9, [2, 9])
    eleza test_jump_in_nested_finally(output):
        jaribu:
            output.append(2)
        mwishowe:
            output.append(4)
            jaribu:
                output.append(6)
            mwishowe:
                output.append(8)
            output.append(9)

    @jump_test(6, 7, [2, 7], (ZeroDivisionError, ''))
    eleza test_jump_in_nested_finally_2(output):
        jaribu:
            output.append(2)
            1/0
            rudisha
        mwishowe:
            output.append(6)
            output.append(7)
        output.append(8)

    @jump_test(6, 11, [2, 11], (ZeroDivisionError, ''))
    eleza test_jump_in_nested_finally_3(output):
        jaribu:
            output.append(2)
            1/0
            rudisha
        mwishowe:
            output.append(6)
            jaribu:
                output.append(8)
            mwishowe:
                output.append(10)
            output.append(11)
        output.append(12)

    @jump_test(5, 11, [2, 4, 12])
    eleza test_jump_over_rudisha_try_finally_in_finally_block(output):
        jaribu:
            output.append(2)
        mwishowe:
            output.append(4)
            output.append(5)
            rudisha
            jaribu:
                output.append(8)
            mwishowe:
                output.append(10)
            pita
        output.append(12)

    @jump_test(3, 4, [1, 4])
    eleza test_jump_infinite_while_loop(output):
        output.append(1)
        wakati Kweli:
            output.append(3)
        output.append(4)

    @jump_test(2, 4, [4, 4])
    eleza test_jump_forwards_into_while_block(output):
        i = 1
        output.append(2)
        wakati i <= 2:
            output.append(4)
            i += 1

    @jump_test(5, 3, [3, 3, 3, 5])
    eleza test_jump_backwards_into_while_block(output):
        i = 1
        wakati i <= 2:
            output.append(3)
            i += 1
        output.append(5)

    @jump_test(2, 3, [1, 3])
    eleza test_jump_forwards_out_of_with_block(output):
        with tracecontext(output, 1):
            output.append(2)
        output.append(3)

    @async_jump_test(2, 3, [1, 3])
    async eleza test_jump_forwards_out_of_async_with_block(output):
        async with asynctracecontext(output, 1):
            output.append(2)
        output.append(3)

    @jump_test(3, 1, [1, 2, 1, 2, 3, -2])
    eleza test_jump_backwards_out_of_with_block(output):
        output.append(1)
        with tracecontext(output, 2):
            output.append(3)

    @async_jump_test(3, 1, [1, 2, 1, 2, 3, -2])
    async eleza test_jump_backwards_out_of_async_with_block(output):
        output.append(1)
        async with asynctracecontext(output, 2):
            output.append(3)

    @jump_test(2, 5, [5])
    eleza test_jump_forwards_out_of_try_finally_block(output):
        jaribu:
            output.append(2)
        mwishowe:
            output.append(4)
        output.append(5)

    @jump_test(3, 1, [1, 1, 3, 5])
    eleza test_jump_backwards_out_of_try_finally_block(output):
        output.append(1)
        jaribu:
            output.append(3)
        mwishowe:
            output.append(5)

    @jump_test(2, 6, [6])
    eleza test_jump_forwards_out_of_try_except_block(output):
        jaribu:
            output.append(2)
        except:
            output.append(4)
            ashiria
        output.append(6)

    @jump_test(3, 1, [1, 1, 3])
    eleza test_jump_backwards_out_of_try_except_block(output):
        output.append(1)
        jaribu:
            output.append(3)
        except:
            output.append(5)
            ashiria

    @jump_test(5, 7, [4, 7, 8])
    eleza test_jump_between_except_blocks(output):
        jaribu:
            1/0
        tatizo ZeroDivisionError:
            output.append(4)
            output.append(5)
        tatizo FloatingPointError:
            output.append(7)
        output.append(8)

    @jump_test(5, 6, [4, 6, 7])
    eleza test_jump_within_except_block(output):
        jaribu:
            1/0
        except:
            output.append(4)
            output.append(5)
            output.append(6)
        output.append(7)

    @jump_test(2, 4, [1, 4, 5, -4])
    eleza test_jump_across_with(output):
        output.append(1)
        with tracecontext(output, 2):
            output.append(3)
        with tracecontext(output, 4):
            output.append(5)

    @async_jump_test(2, 4, [1, 4, 5, -4])
    async eleza test_jump_across_async_with(output):
        output.append(1)
        async with asynctracecontext(output, 2):
            output.append(3)
        async with asynctracecontext(output, 4):
            output.append(5)

    @jump_test(4, 5, [1, 3, 5, 6])
    eleza test_jump_out_of_with_block_within_for_block(output):
        output.append(1)
        kila i kwenye [1]:
            with tracecontext(output, 3):
                output.append(4)
            output.append(5)
        output.append(6)

    @async_jump_test(4, 5, [1, 3, 5, 6])
    async eleza test_jump_out_of_async_with_block_within_for_block(output):
        output.append(1)
        kila i kwenye [1]:
            async with asynctracecontext(output, 3):
                output.append(4)
            output.append(5)
        output.append(6)

    @jump_test(4, 5, [1, 2, 3, 5, -2, 6])
    eleza test_jump_out_of_with_block_within_with_block(output):
        output.append(1)
        with tracecontext(output, 2):
            with tracecontext(output, 3):
                output.append(4)
            output.append(5)
        output.append(6)

    @async_jump_test(4, 5, [1, 2, 3, 5, -2, 6])
    async eleza test_jump_out_of_async_with_block_within_with_block(output):
        output.append(1)
        with tracecontext(output, 2):
            async with asynctracecontext(output, 3):
                output.append(4)
            output.append(5)
        output.append(6)

    @jump_test(5, 6, [2, 4, 6, 7])
    eleza test_jump_out_of_with_block_within_finally_block(output):
        jaribu:
            output.append(2)
        mwishowe:
            with tracecontext(output, 4):
                output.append(5)
            output.append(6)
        output.append(7)

    @async_jump_test(5, 6, [2, 4, 6, 7])
    async eleza test_jump_out_of_async_with_block_within_finally_block(output):
        jaribu:
            output.append(2)
        mwishowe:
            async with asynctracecontext(output, 4):
                output.append(5)
            output.append(6)
        output.append(7)

    @jump_test(8, 11, [1, 3, 5, 11, 12])
    eleza test_jump_out_of_complex_nested_blocks(output):
        output.append(1)
        kila i kwenye [1]:
            output.append(3)
            kila j kwenye [1, 2]:
                output.append(5)
                jaribu:
                    kila k kwenye [1, 2]:
                        output.append(8)
                mwishowe:
                    output.append(10)
            output.append(11)
        output.append(12)

    @jump_test(3, 5, [1, 2, 5])
    eleza test_jump_out_of_with_assignment(output):
        output.append(1)
        with tracecontext(output, 2) \
                kama x:
            output.append(4)
        output.append(5)

    @async_jump_test(3, 5, [1, 2, 5])
    async eleza test_jump_out_of_async_with_assignment(output):
        output.append(1)
        async with asynctracecontext(output, 2) \
                kama x:
            output.append(4)
        output.append(5)

    @jump_test(3, 6, [1, 6, 8, 9])
    eleza test_jump_over_rudisha_in_try_finally_block(output):
        output.append(1)
        jaribu:
            output.append(3)
            ikiwa sio output: # always false
                rudisha
            output.append(6)
        mwishowe:
            output.append(8)
        output.append(9)

    @jump_test(5, 8, [1, 3, 8, 10, 11, 13])
    eleza test_jump_over_koma_in_try_finally_block(output):
        output.append(1)
        wakati Kweli:
            output.append(3)
            jaribu:
                output.append(5)
                ikiwa sio output: # always false
                    koma
                output.append(8)
            mwishowe:
                output.append(10)
            output.append(11)
            koma
        output.append(13)

    @jump_test(1, 7, [7, 8])
    eleza test_jump_over_for_block_before_else(output):
        output.append(1)
        ikiwa sio output:  # always false
            kila i kwenye [3]:
                output.append(4)
        isipokua:
            output.append(6)
            output.append(7)
        output.append(8)

    @async_jump_test(1, 7, [7, 8])
    async eleza test_jump_over_async_for_block_before_else(output):
        output.append(1)
        ikiwa sio output:  # always false
            async kila i kwenye asynciter([3]):
                output.append(4)
        isipokua:
            output.append(6)
            output.append(7)
        output.append(8)

    # The second set of 'jump' tests are kila things that are sio allowed:

    @jump_test(2, 3, [1], (ValueError, 'after'))
    eleza test_no_jump_too_far_forwards(output):
        output.append(1)
        output.append(2)

    @jump_test(2, -2, [1], (ValueError, 'before'))
    eleza test_no_jump_too_far_backwards(output):
        output.append(1)
        output.append(2)

    # Test each kind of 'except' line.
    @jump_test(2, 3, [4], (ValueError, 'except'))
    eleza test_no_jump_to_except_1(output):
        jaribu:
            output.append(2)
        except:
            output.append(4)
            ashiria

    @jump_test(2, 3, [4], (ValueError, 'except'))
    eleza test_no_jump_to_except_2(output):
        jaribu:
            output.append(2)
        tatizo ValueError:
            output.append(4)
            ashiria

    @jump_test(2, 3, [4], (ValueError, 'except'))
    eleza test_no_jump_to_except_3(output):
        jaribu:
            output.append(2)
        tatizo ValueError kama e:
            output.append(4)
            ashiria e

    @jump_test(2, 3, [4], (ValueError, 'except'))
    eleza test_no_jump_to_except_4(output):
        jaribu:
            output.append(2)
        tatizo (ValueError, RuntimeError) kama e:
            output.append(4)
            ashiria e

    @jump_test(1, 3, [], (ValueError, 'into'))
    eleza test_no_jump_forwards_into_for_block(output):
        output.append(1)
        kila i kwenye 1, 2:
            output.append(3)

    @async_jump_test(1, 3, [], (ValueError, 'into'))
    async eleza test_no_jump_forwards_into_async_for_block(output):
        output.append(1)
        async kila i kwenye asynciter([1, 2]):
            output.append(3)

    @jump_test(3, 2, [2, 2], (ValueError, 'into'))
    eleza test_no_jump_backwards_into_for_block(output):
        kila i kwenye 1, 2:
            output.append(2)
        output.append(3)

    @async_jump_test(3, 2, [2, 2], (ValueError, 'into'))
    async eleza test_no_jump_backwards_into_async_for_block(output):
        async kila i kwenye asynciter([1, 2]):
            output.append(2)
        output.append(3)

    @jump_test(1, 3, [], (ValueError, 'into'))
    eleza test_no_jump_forwards_into_with_block(output):
        output.append(1)
        with tracecontext(output, 2):
            output.append(3)

    @async_jump_test(1, 3, [], (ValueError, 'into'))
    async eleza test_no_jump_forwards_into_async_with_block(output):
        output.append(1)
        async with asynctracecontext(output, 2):
            output.append(3)

    @jump_test(3, 2, [1, 2, -1], (ValueError, 'into'))
    eleza test_no_jump_backwards_into_with_block(output):
        with tracecontext(output, 1):
            output.append(2)
        output.append(3)

    @async_jump_test(3, 2, [1, 2, -1], (ValueError, 'into'))
    async eleza test_no_jump_backwards_into_async_with_block(output):
        async with asynctracecontext(output, 1):
            output.append(2)
        output.append(3)

    @jump_test(1, 3, [], (ValueError, 'into'))
    eleza test_no_jump_forwards_into_try_finally_block(output):
        output.append(1)
        jaribu:
            output.append(3)
        mwishowe:
            output.append(5)

    @jump_test(5, 2, [2, 4], (ValueError, 'into'))
    eleza test_no_jump_backwards_into_try_finally_block(output):
        jaribu:
            output.append(2)
        mwishowe:
            output.append(4)
        output.append(5)

    @jump_test(1, 3, [], (ValueError, 'into'))
    eleza test_no_jump_forwards_into_try_except_block(output):
        output.append(1)
        jaribu:
            output.append(3)
        except:
            output.append(5)
            ashiria

    @jump_test(6, 2, [2], (ValueError, 'into'))
    eleza test_no_jump_backwards_into_try_except_block(output):
        jaribu:
            output.append(2)
        except:
            output.append(4)
            ashiria
        output.append(6)

    # 'except' with a variable creates an implicit finally block
    @jump_test(5, 7, [4], (ValueError, 'into'))
    eleza test_no_jump_between_except_blocks_2(output):
        jaribu:
            1/0
        tatizo ZeroDivisionError:
            output.append(4)
            output.append(5)
        tatizo FloatingPointError kama e:
            output.append(7)
        output.append(8)

    @jump_test(1, 5, [], (ValueError, "into a 'finally'"))
    eleza test_no_jump_into_finally_block(output):
        output.append(1)
        jaribu:
            output.append(3)
        mwishowe:
            output.append(5)

    @jump_test(3, 6, [2, 5, 6], (ValueError, "into a 'finally'"))
    eleza test_no_jump_into_finally_block_kutoka_try_block(output):
        jaribu:
            output.append(2)
            output.append(3)
        mwishowe:  # still executed ikiwa the jump ni failed
            output.append(5)
            output.append(6)
        output.append(7)

    @jump_test(5, 1, [1, 3], (ValueError, "out of a 'finally'"))
    eleza test_no_jump_out_of_finally_block(output):
        output.append(1)
        jaribu:
            output.append(3)
        mwishowe:
            output.append(5)

    @jump_test(1, 5, [], (ValueError, "into an 'except'"))
    eleza test_no_jump_into_bare_except_block(output):
        output.append(1)
        jaribu:
            output.append(3)
        except:
            output.append(5)

    @jump_test(1, 5, [], (ValueError, "into an 'except'"))
    eleza test_no_jump_into_qualified_except_block(output):
        output.append(1)
        jaribu:
            output.append(3)
        tatizo Exception:
            output.append(5)

    @jump_test(3, 6, [2, 5, 6], (ValueError, "into an 'except'"))
    eleza test_no_jump_into_bare_except_block_kutoka_try_block(output):
        jaribu:
            output.append(2)
            output.append(3)
        except:  # executed ikiwa the jump ni failed
            output.append(5)
            output.append(6)
            ashiria
        output.append(8)

    @jump_test(3, 6, [2], (ValueError, "into an 'except'"))
    eleza test_no_jump_into_qualified_except_block_kutoka_try_block(output):
        jaribu:
            output.append(2)
            output.append(3)
        tatizo ZeroDivisionError:
            output.append(5)
            output.append(6)
            ashiria
        output.append(8)

    @jump_test(7, 1, [1, 3, 6], (ValueError, "out of an 'except'"))
    eleza test_no_jump_out_of_bare_except_block(output):
        output.append(1)
        jaribu:
            output.append(3)
            1/0
        except:
            output.append(6)
            output.append(7)

    @jump_test(7, 1, [1, 3, 6], (ValueError, "out of an 'except'"))
    eleza test_no_jump_out_of_qualified_except_block(output):
        output.append(1)
        jaribu:
            output.append(3)
            1/0
        tatizo Exception:
            output.append(6)
            output.append(7)

    @jump_test(3, 5, [1, 2, -2], (ValueError, 'into'))
    eleza test_no_jump_between_with_blocks(output):
        output.append(1)
        with tracecontext(output, 2):
            output.append(3)
        with tracecontext(output, 4):
            output.append(5)

    @async_jump_test(3, 5, [1, 2, -2], (ValueError, 'into'))
    async eleza test_no_jump_between_async_with_blocks(output):
        output.append(1)
        async with asynctracecontext(output, 2):
            output.append(3)
        async with asynctracecontext(output, 4):
            output.append(5)

    @jump_test(5, 7, [2, 4], (ValueError, 'finally'))
    eleza test_no_jump_over_rudisha_out_of_finally_block(output):
        jaribu:
            output.append(2)
        mwishowe:
            output.append(4)
            output.append(5)
            rudisha
        output.append(7)

    @jump_test(7, 4, [1, 6], (ValueError, 'into'))
    eleza test_no_jump_into_for_block_before_else(output):
        output.append(1)
        ikiwa sio output:  # always false
            kila i kwenye [3]:
                output.append(4)
        isipokua:
            output.append(6)
            output.append(7)
        output.append(8)

    @async_jump_test(7, 4, [1, 6], (ValueError, 'into'))
    async eleza test_no_jump_into_async_for_block_before_else(output):
        output.append(1)
        ikiwa sio output:  # always false
            async kila i kwenye asynciter([3]):
                output.append(4)
        isipokua:
            output.append(6)
            output.append(7)
        output.append(8)

    eleza test_no_jump_to_non_integers(self):
        self.run_test(no_jump_to_non_integers, 2, "Spam", [Kweli])

    eleza test_no_jump_without_trace_function(self):
        # Must set sys.settrace(Tupu) kwenye setUp(), else condition ni not
        # triggered.
        no_jump_without_trace_function()

    eleza test_large_function(self):
        d = {}
        exec("""eleza f(output):        # line 0
            x = 0                     # line 1
            y = 1                     # line 2
            '''                       # line 3
            %s                        # lines 4-1004
            '''                       # line 1005
            x += 1                    # line 1006
            output.append(x)          # line 1007
            rudisha""" % ('\n' * 1000,), d)
        f = d['f']
        self.run_test(f, 2, 1007, [0])

    eleza test_jump_to_firstlineno(self):
        # This tests that PDB can jump back to the first line kwenye a
        # file.  See issue #1689458.  It can only be triggered kwenye a
        # function call ikiwa the function ni defined on a single line.
        code = compile("""
# Comments don't count.
output.append(2)  # firstlineno ni here.
output.append(3)
output.append(4)
""", "<fake module>", "exec")
        kundi fake_function:
            __code__ = code
        tracer = JumpTracer(fake_function, 2, 0)
        sys.settrace(tracer.trace)
        namespace = {"output": []}
        exec(code, namespace)
        sys.settrace(Tupu)
        self.compare_jump_output([2, 3, 2, 3, 4], namespace["output"])

    @jump_test(2, 3, [1], event='call', error=(ValueError, "can't jump kutoka"
               " the 'call' trace event of a new frame"))
    eleza test_no_jump_kutoka_call(output):
        output.append(1)
        eleza nested():
            output.append(3)
        nested()
        output.append(5)

    @jump_test(2, 1, [1], event='rudisha', error=(ValueError,
               "can only jump kutoka a 'line' trace event"))
    eleza test_no_jump_kutoka_rudisha_event(output):
        output.append(1)
        rudisha

    @jump_test(2, 1, [1], event='exception', error=(ValueError,
               "can only jump kutoka a 'line' trace event"))
    eleza test_no_jump_kutoka_exception_event(output):
        output.append(1)
        1 / 0

    @jump_test(3, 2, [2], event='rudisha', error=(ValueError,
               "can't jump kutoka a tuma statement"))
    eleza test_no_jump_kutoka_tuma(output):
        eleza gen():
            output.append(2)
            tuma 3
        next(gen())
        output.append(5)


ikiwa __name__ == "__main__":
    unittest.main()
