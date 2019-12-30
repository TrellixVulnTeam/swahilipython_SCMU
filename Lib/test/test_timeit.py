agiza timeit
agiza unittest
agiza sys
agiza io
kutoka textwrap agiza dedent

kutoka test.support agiza captured_stdout
kutoka test.support agiza captured_stderr

# timeit's default number of iterations.
DEFAULT_NUMBER = 1000000

# timeit's default number of repetitions.
DEFAULT_REPEAT = 5

# XXX: some tests are commented out that would improve the coverage but take a
# long time to run because they test the default number of loops, which is
# large.  The tests could be enabled ikiwa there was a way to override the default
# number of loops during testing, but this would require changing the signature
# of some functions that use the default kama a default argument.

kundi FakeTimer:
    BASE_TIME = 42.0
    eleza __init__(self, seconds_per_increment=1.0):
        self.count = 0
        self.setup_calls = 0
        self.seconds_per_increment=seconds_per_increment
        timeit._fake_timer = self

    eleza __call__(self):
        rudisha self.BASE_TIME + self.count * self.seconds_per_increment

    eleza inc(self):
        self.count += 1

    eleza setup(self):
        self.setup_calls += 1

    eleza wrap_timer(self, timer):
        """Records 'timer' na returns self kama callable timer."""
        self.saved_timer = timer
        rudisha self

kundi TestTimeit(unittest.TestCase):

    eleza tearDown(self):
        jaribu:
            toa timeit._fake_timer
        tatizo AttributeError:
            pita

    eleza test_reindent_empty(self):
        self.assertEqual(timeit.reindent("", 0), "")
        self.assertEqual(timeit.reindent("", 4), "")

    eleza test_reindent_single(self):
        self.assertEqual(timeit.reindent("pita", 0), "pita")
        self.assertEqual(timeit.reindent("pita", 4), "pita")

    eleza test_reindent_multi_empty(self):
        self.assertEqual(timeit.reindent("\n\n", 0), "\n\n")
        self.assertEqual(timeit.reindent("\n\n", 4), "\n    \n    ")

    eleza test_reindent_multi(self):
        self.assertEqual(timeit.reindent(
            "andika()\npita\nkoma", 0),
            "andika()\npita\nkoma")
        self.assertEqual(timeit.reindent(
            "andika()\npita\nkoma", 4),
            "andika()\n    pita\n    koma")

    eleza test_timer_invalid_stmt(self):
        self.assertRaises(ValueError, timeit.Timer, stmt=Tupu)
        self.assertRaises(SyntaxError, timeit.Timer, stmt='return')
        self.assertRaises(SyntaxError, timeit.Timer, stmt='tuma')
        self.assertRaises(SyntaxError, timeit.Timer, stmt='tuma kutoka ()')
        self.assertRaises(SyntaxError, timeit.Timer, stmt='koma')
        self.assertRaises(SyntaxError, timeit.Timer, stmt='endelea')
        self.assertRaises(SyntaxError, timeit.Timer, stmt='kutoka timeit agiza *')

    eleza test_timer_invalid_setup(self):
        self.assertRaises(ValueError, timeit.Timer, setup=Tupu)
        self.assertRaises(SyntaxError, timeit.Timer, setup='return')
        self.assertRaises(SyntaxError, timeit.Timer, setup='tuma')
        self.assertRaises(SyntaxError, timeit.Timer, setup='tuma kutoka ()')
        self.assertRaises(SyntaxError, timeit.Timer, setup='koma')
        self.assertRaises(SyntaxError, timeit.Timer, setup='endelea')
        self.assertRaises(SyntaxError, timeit.Timer, setup='kutoka timeit agiza *')

    fake_setup = "agiza timeit\ntimeit._fake_timer.setup()"
    fake_stmt = "agiza timeit\ntimeit._fake_timer.inc()"

    eleza fake_callable_setup(self):
        self.fake_timer.setup()

    eleza fake_callable_stmt(self):
        self.fake_timer.inc()

    eleza timeit(self, stmt, setup, number=Tupu, globals=Tupu):
        self.fake_timer = FakeTimer()
        t = timeit.Timer(stmt=stmt, setup=setup, timer=self.fake_timer,
                globals=globals)
        kwargs = {}
        ikiwa number ni Tupu:
            number = DEFAULT_NUMBER
        isipokua:
            kwargs['number'] = number
        delta_time = t.timeit(**kwargs)
        self.assertEqual(self.fake_timer.setup_calls, 1)
        self.assertEqual(self.fake_timer.count, number)
        self.assertEqual(delta_time, number)

    # Takes too long to run kwenye debug build.
    #eleza test_timeit_default_iters(self):
    #    self.timeit(self.fake_stmt, self.fake_setup)

    eleza test_timeit_zero_iters(self):
        self.timeit(self.fake_stmt, self.fake_setup, number=0)

    eleza test_timeit_few_iters(self):
        self.timeit(self.fake_stmt, self.fake_setup, number=3)

    eleza test_timeit_callable_stmt(self):
        self.timeit(self.fake_callable_stmt, self.fake_setup, number=3)

    eleza test_timeit_callable_setup(self):
        self.timeit(self.fake_stmt, self.fake_callable_setup, number=3)

    eleza test_timeit_callable_stmt_and_setup(self):
        self.timeit(self.fake_callable_stmt,
                self.fake_callable_setup, number=3)

    # Takes too long to run kwenye debug build.
    #eleza test_timeit_function(self):
    #    delta_time = timeit.timeit(self.fake_stmt, self.fake_setup,
    #            timer=FakeTimer())
    #    self.assertEqual(delta_time, DEFAULT_NUMBER)

    eleza test_timeit_function_zero_iters(self):
        delta_time = timeit.timeit(self.fake_stmt, self.fake_setup, number=0,
                timer=FakeTimer())
        self.assertEqual(delta_time, 0)

    eleza test_timeit_globals_args(self):
        global _global_timer
        _global_timer = FakeTimer()
        t = timeit.Timer(stmt='_global_timer.inc()', timer=_global_timer)
        self.assertRaises(NameError, t.timeit, number=3)
        timeit.timeit(stmt='_global_timer.inc()', timer=_global_timer,
                      globals=globals(), number=3)
        local_timer = FakeTimer()
        timeit.timeit(stmt='local_timer.inc()', timer=local_timer,
                      globals=locals(), number=3)

    eleza repeat(self, stmt, setup, repeat=Tupu, number=Tupu):
        self.fake_timer = FakeTimer()
        t = timeit.Timer(stmt=stmt, setup=setup, timer=self.fake_timer)
        kwargs = {}
        ikiwa repeat ni Tupu:
            repeat = DEFAULT_REPEAT
        isipokua:
            kwargs['repeat'] = repeat
        ikiwa number ni Tupu:
            number = DEFAULT_NUMBER
        isipokua:
            kwargs['number'] = number
        delta_times = t.repeat(**kwargs)
        self.assertEqual(self.fake_timer.setup_calls, repeat)
        self.assertEqual(self.fake_timer.count, repeat * number)
        self.assertEqual(delta_times, repeat * [float(number)])

    # Takes too long to run kwenye debug build.
    #eleza test_repeat_default(self):
    #    self.repeat(self.fake_stmt, self.fake_setup)

    eleza test_repeat_zero_reps(self):
        self.repeat(self.fake_stmt, self.fake_setup, repeat=0)

    eleza test_repeat_zero_iters(self):
        self.repeat(self.fake_stmt, self.fake_setup, number=0)

    eleza test_repeat_few_reps_and_iters(self):
        self.repeat(self.fake_stmt, self.fake_setup, repeat=3, number=5)

    eleza test_repeat_callable_stmt(self):
        self.repeat(self.fake_callable_stmt, self.fake_setup,
                repeat=3, number=5)

    eleza test_repeat_callable_setup(self):
        self.repeat(self.fake_stmt, self.fake_callable_setup,
                repeat=3, number=5)

    eleza test_repeat_callable_stmt_and_setup(self):
        self.repeat(self.fake_callable_stmt, self.fake_callable_setup,
                repeat=3, number=5)

    # Takes too long to run kwenye debug build.
    #eleza test_repeat_function(self):
    #    delta_times = timeit.repeat(self.fake_stmt, self.fake_setup,
    #            timer=FakeTimer())
    #    self.assertEqual(delta_times, DEFAULT_REPEAT * [float(DEFAULT_NUMBER)])

    eleza test_repeat_function_zero_reps(self):
        delta_times = timeit.repeat(self.fake_stmt, self.fake_setup, repeat=0,
                timer=FakeTimer())
        self.assertEqual(delta_times, [])

    eleza test_repeat_function_zero_iters(self):
        delta_times = timeit.repeat(self.fake_stmt, self.fake_setup, number=0,
                timer=FakeTimer())
        self.assertEqual(delta_times, DEFAULT_REPEAT * [0.0])

    eleza assert_exc_string(self, exc_string, expected_exc_name):
        exc_lines = exc_string.splitlines()
        self.assertGreater(len(exc_lines), 2)
        self.assertKweli(exc_lines[0].startswith('Traceback'))
        self.assertKweli(exc_lines[-1].startswith(expected_exc_name))

    eleza test_print_exc(self):
        s = io.StringIO()
        t = timeit.Timer("1/0")
        jaribu:
            t.timeit()
        tatizo:
            t.print_exc(s)
        self.assert_exc_string(s.getvalue(), 'ZeroDivisionError')

    MAIN_DEFAULT_OUTPUT = "1 loop, best of 5: 1 sec per loop\n"

    eleza run_main(self, seconds_per_increment=1.0, switches=Tupu, timer=Tupu):
        ikiwa timer ni Tupu:
            timer = FakeTimer(seconds_per_increment=seconds_per_increment)
        ikiwa switches ni Tupu:
            args = []
        isipokua:
            args = switches[:]
        args.append(self.fake_stmt)
        # timeit.main() modifies sys.path, so save na restore it.
        orig_sys_path = sys.path[:]
        ukijumuisha captured_stdout() kama s:
            timeit.main(args=args, _wrap_timer=timer.wrap_timer)
        sys.path[:] = orig_sys_path[:]
        rudisha s.getvalue()

    eleza test_main_bad_switch(self):
        s = self.run_main(switches=['--bad-switch'])
        self.assertEqual(s, dedent("""\
            option --bad-switch sio recognized
            use -h/--help kila command line help
            """))

    eleza test_main_seconds(self):
        s = self.run_main(seconds_per_increment=5.5)
        self.assertEqual(s, "1 loop, best of 5: 5.5 sec per loop\n")

    eleza test_main_milliseconds(self):
        s = self.run_main(seconds_per_increment=0.0055)
        self.assertEqual(s, "50 loops, best of 5: 5.5 msec per loop\n")

    eleza test_main_microseconds(self):
        s = self.run_main(seconds_per_increment=0.0000025, switches=['-n100'])
        self.assertEqual(s, "100 loops, best of 5: 2.5 usec per loop\n")

    eleza test_main_fixed_iters(self):
        s = self.run_main(seconds_per_increment=2.0, switches=['-n35'])
        self.assertEqual(s, "35 loops, best of 5: 2 sec per loop\n")

    eleza test_main_setup(self):
        s = self.run_main(seconds_per_increment=2.0,
                switches=['-n35', '-s', 'andika("CustomSetup")'])
        self.assertEqual(s, "CustomSetup\n" * DEFAULT_REPEAT +
                "35 loops, best of 5: 2 sec per loop\n")

    eleza test_main_multiple_setups(self):
        s = self.run_main(seconds_per_increment=2.0,
                switches=['-n35', '-s', 'a = "CustomSetup"', '-s', 'andika(a)'])
        self.assertEqual(s, "CustomSetup\n" * DEFAULT_REPEAT +
                "35 loops, best of 5: 2 sec per loop\n")

    eleza test_main_fixed_reps(self):
        s = self.run_main(seconds_per_increment=60.0, switches=['-r9'])
        self.assertEqual(s, "1 loop, best of 9: 60 sec per loop\n")

    eleza test_main_negative_reps(self):
        s = self.run_main(seconds_per_increment=60.0, switches=['-r-5'])
        self.assertEqual(s, "1 loop, best of 1: 60 sec per loop\n")

    @unittest.skipIf(sys.flags.optimize >= 2, "need __doc__")
    eleza test_main_help(self):
        s = self.run_main(switches=['-h'])
        # Note: It's sio clear that the trailing space was intended kama part of
        # the help text, but since it's there, check kila it.
        self.assertEqual(s, timeit.__doc__ + ' ')

    eleza test_main_verbose(self):
        s = self.run_main(switches=['-v'])
        self.assertEqual(s, dedent("""\
                1 loop -> 1 secs

                raw times: 1 sec, 1 sec, 1 sec, 1 sec, 1 sec

                1 loop, best of 5: 1 sec per loop
            """))

    eleza test_main_very_verbose(self):
        s = self.run_main(seconds_per_increment=0.000_030, switches=['-vv'])
        self.assertEqual(s, dedent("""\
                1 loop -> 3e-05 secs
                2 loops -> 6e-05 secs
                5 loops -> 0.00015 secs
                10 loops -> 0.0003 secs
                20 loops -> 0.0006 secs
                50 loops -> 0.0015 secs
                100 loops -> 0.003 secs
                200 loops -> 0.006 secs
                500 loops -> 0.015 secs
                1000 loops -> 0.03 secs
                2000 loops -> 0.06 secs
                5000 loops -> 0.15 secs
                10000 loops -> 0.3 secs

                raw times: 300 msec, 300 msec, 300 msec, 300 msec, 300 msec

                10000 loops, best of 5: 30 usec per loop
            """))

    eleza test_main_with_time_unit(self):
        unit_sec = self.run_main(seconds_per_increment=0.003,
                switches=['-u', 'sec'])
        self.assertEqual(unit_sec,
                "100 loops, best of 5: 0.003 sec per loop\n")
        unit_msec = self.run_main(seconds_per_increment=0.003,
                switches=['-u', 'msec'])
        self.assertEqual(unit_msec,
                "100 loops, best of 5: 3 msec per loop\n")
        unit_usec = self.run_main(seconds_per_increment=0.003,
                switches=['-u', 'usec'])
        self.assertEqual(unit_usec,
                "100 loops, best of 5: 3e+03 usec per loop\n")
        # Test invalid unit input
        ukijumuisha captured_stderr() kama error_stringio:
            invalid = self.run_main(seconds_per_increment=0.003,
                    switches=['-u', 'parsec'])
        self.assertEqual(error_stringio.getvalue(),
                    "Unrecognized unit. Please select nsec, usec, msec, ama sec.\n")

    eleza test_main_exception(self):
        ukijumuisha captured_stderr() kama error_stringio:
            s = self.run_main(switches=['1/0'])
        self.assert_exc_string(error_stringio.getvalue(), 'ZeroDivisionError')

    eleza test_main_exception_fixed_reps(self):
        ukijumuisha captured_stderr() kama error_stringio:
            s = self.run_main(switches=['-n1', '1/0'])
        self.assert_exc_string(error_stringio.getvalue(), 'ZeroDivisionError')

    eleza autorange(self, seconds_per_increment=1/1024, callback=Tupu):
        timer = FakeTimer(seconds_per_increment=seconds_per_increment)
        t = timeit.Timer(stmt=self.fake_stmt, setup=self.fake_setup, timer=timer)
        rudisha t.autorange(callback)

    eleza test_autorange(self):
        num_loops, time_taken = self.autorange()
        self.assertEqual(num_loops, 500)
        self.assertEqual(time_taken, 500/1024)

    eleza test_autorange_second(self):
        num_loops, time_taken = self.autorange(seconds_per_increment=1.0)
        self.assertEqual(num_loops, 1)
        self.assertEqual(time_taken, 1.0)

    eleza test_autorange_with_callback(self):
        eleza callback(a, b):
            andika("{} {:.3f}".format(a, b))
        ukijumuisha captured_stdout() kama s:
            num_loops, time_taken = self.autorange(callback=callback)
        self.assertEqual(num_loops, 500)
        self.assertEqual(time_taken, 500/1024)
        expected = ('1 0.001\n'
                    '2 0.002\n'
                    '5 0.005\n'
                    '10 0.010\n'
                    '20 0.020\n'
                    '50 0.049\n'
                    '100 0.098\n'
                    '200 0.195\n'
                    '500 0.488\n')
        self.assertEqual(s.getvalue(), expected)


ikiwa __name__ == '__main__':
    unittest.main()
