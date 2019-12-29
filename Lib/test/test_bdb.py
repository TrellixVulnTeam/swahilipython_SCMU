""" Test the bdb module.

    A test defines a list of tuples that may be seen kama paired tuples, each
    pair being defined by 'expect_tuple, set_tuple' kama follows:

        ([event, [lineno[, co_name[, eargs]]]]), (set_type, [sargs])

    * 'expect_tuple' describes the expected current state of the Bdb instance.
      It may be the empty tuple na no check ni done kwenye that case.
    * 'set_tuple' defines the set_*() method to be invoked when the Bdb
      instance reaches this state.

    Example of an 'expect_tuple, set_tuple' pair:

        ('line', 2, 'tfunc_main'), ('step', )

    Definitions of the members of the 'expect_tuple':
        event:
            Name of the trace event. The set methods that do sio give back
            control to the tracer [1] do sio trigger a tracer event na in
            that case the next 'event' may be 'Tupu' by convention, its value
            ni sio checked.
            [1] Methods that trigger a trace event are set_step(), set_next(),
            set_rudisha(), set_until() na set_endelea().
        lineno:
            Line number. Line numbers are relative to the start of the
            function when tracing a function kwenye the test_bdb module (i.e. this
            module).
        co_name:
            Name of the function being currently traced.
        eargs:
            A tuple:
            * On an 'exception' event the tuple holds a kundi object, the
              current exception must be an instance of this class.
            * On a 'line' event, the tuple holds a dictionary na a list. The
              dictionary maps each komapoint number that has been hit on this
              line to its hits count. The list holds the list of komapoint
              number temporaries that are being deleted.

    Definitions of the members of the 'set_tuple':
        set_type:
            The type of the set method to be invoked. This may
            be the type of one of the Bdb set methods: 'step', 'next',
            'until', 'rudisha', 'endelea', 'koma', 'quit', ama the type of one
            of the set methods added by test_bdb.Bdb: 'ignore', 'enable',
            'disable', 'clear', 'up', 'down'.
        sargs:
            The arguments of the set method ikiwa any, packed kwenye a tuple.
"""

agiza bdb kama _bdb
agiza sys
agiza os
agiza unittest
agiza textwrap
agiza importlib
agiza linecache
kutoka contextlib agiza contextmanager
kutoka itertools agiza islice, repeat
agiza test.support

kundi BdbException(Exception): pita
kundi BdbError(BdbException): """Error ashiriad by the Bdb instance."""
kundi BdbSyntaxError(BdbException): """Syntax error kwenye the test case."""
kundi BdbNotExpectedError(BdbException): """Unexpected result."""

# When 'dry_run' ni set to true, expect tuples are ignored na the actual
# state of the tracer ni printed after running each set_*() method of the test
# case. The full list of komapoints na their attributes ni also printed
# after each 'line' event where a komapoint has been hit.
dry_run = 0

eleza reset_Breakpoint():
    _bdb.Breakpoint.next = 1
    _bdb.Breakpoint.bplist = {}
    _bdb.Breakpoint.bpbynumber = [Tupu]

eleza info_komapoints():
    bp_list = [bp kila  bp kwenye _bdb.Breakpoint.bpbynumber ikiwa bp]
    ikiwa sio bp_list:
        rudisha ''

    header_added = Uongo
    kila bp kwenye bp_list:
        ikiwa sio header_added:
            info = 'BpNum Temp Enb Hits Ignore Where\n'
            header_added = Kweli

        disp = 'yes ' ikiwa bp.temporary isipokua 'no  '
        enab = 'yes' ikiwa bp.enabled isipokua 'no '
        info += ('%-5d %s %s %-4d %-6d at %s:%d' %
                    (bp.number, disp, enab, bp.hits, bp.ignore,
                     os.path.basename(bp.file), bp.line))
        ikiwa bp.cond:
            info += '\n\tstop only ikiwa %s' % (bp.cond,)
        info += '\n'
    rudisha info

kundi Bdb(_bdb.Bdb):
    """Extend Bdb to enhance test coverage."""

    eleza trace_dispatch(self, frame, event, arg):
        self.currentbp = Tupu
        rudisha super().trace_dispatch(frame, event, arg)

    eleza set_koma(self, filename, lineno, temporary=Uongo, cond=Tupu,
                  funcname=Tupu):
        ikiwa isinstance(funcname, str):
            ikiwa filename == __file__:
                globals_ = globals()
            isipokua:
                module = importlib.import_module(filename[:-3])
                globals_ = module.__dict__
            func = eval(funcname, globals_)
            code = func.__code__
            filename = code.co_filename
            lineno = code.co_firstlineno
            funcname = code.co_name

        res = super().set_koma(filename, lineno, temporary=temporary,
                                 cond=cond, funcname=funcname)
        ikiwa isinstance(res, str):
            ashiria BdbError(res)
        rudisha res

    eleza get_stack(self, f, t):
        self.stack, self.index = super().get_stack(f, t)
        self.frame = self.stack[self.index][0]
        rudisha self.stack, self.index

    eleza set_ignore(self, bpnum):
        """Increment the ignore count of Breakpoint number 'bpnum'."""
        bp = self.get_bpbynumber(bpnum)
        bp.ignore += 1

    eleza set_enable(self, bpnum):
        bp = self.get_bpbynumber(bpnum)
        bp.enabled = Kweli

    eleza set_disable(self, bpnum):
        bp = self.get_bpbynumber(bpnum)
        bp.enabled = Uongo

    eleza set_clear(self, fname, lineno):
        err = self.clear_koma(fname, lineno)
        ikiwa err:
            ashiria BdbError(err)

    eleza set_up(self):
        """Move up kwenye the frame stack."""
        ikiwa sio self.index:
            ashiria BdbError('Oldest frame')
        self.index -= 1
        self.frame = self.stack[self.index][0]

    eleza set_down(self):
        """Move down kwenye the frame stack."""
        ikiwa self.index + 1 == len(self.stack):
            ashiria BdbError('Newest frame')
        self.index += 1
        self.frame = self.stack[self.index][0]

kundi Tracer(Bdb):
    """A tracer kila testing the bdb module."""

    eleza __init__(self, expect_set, skip=Tupu, dry_run=Uongo, test_case=Tupu):
        super().__init__(skip=skip)
        self.expect_set = expect_set
        self.dry_run = dry_run
        self.header = ('Dry-run results kila %s:' % test_case if
                       test_case ni sio Tupu isipokua Tupu)
        self.init_test()

    eleza init_test(self):
        self.cur_tatizo = Tupu
        self.expect_set_no = 0
        self.komapoint_hits = Tupu
        self.expected_list = list(islice(self.expect_set, 0, Tupu, 2))
        self.set_list = list(islice(self.expect_set, 1, Tupu, 2))

    eleza trace_dispatch(self, frame, event, arg):
        # On an 'exception' event, call_exc_trace() kwenye Python/ceval.c discards
        # a BdbException ashiriad by the Tracer instance, so we ashiria it on the
        # next trace_dispatch() call that occurs unless the set_quit() or
        # set_endelea() method has been invoked on the 'exception' event.
        ikiwa self.cur_tatizo ni sio Tupu:
            ashiria self.cur_except

        ikiwa event == 'exception':
            jaribu:
                res = super().trace_dispatch(frame, event, arg)
                rudisha res
            tatizo BdbException kama e:
                self.cur_tatizo = e
                rudisha self.trace_dispatch
        isipokua:
            rudisha super().trace_dispatch(frame, event, arg)

    eleza user_call(self, frame, argument_list):
        # Adopt the same behavior kama pdb and, kama a side effect, skip also the
        # first 'call' event when the Tracer ni started ukijumuisha Tracer.runcall()
        # which may be possibly considered kama a bug.
        ikiwa sio self.stop_here(frame):
            rudisha
        self.process_event('call', frame, argument_list)
        self.next_set_method()

    eleza user_line(self, frame):
        self.process_event('line', frame)

        ikiwa self.dry_run na self.komapoint_hits:
            info = info_komapoints().strip('\n')
            # Indent each line.
            kila line kwenye info.split('\n'):
                andika('  ' + line)
        self.delete_temporaries()
        self.komapoint_hits = Tupu

        self.next_set_method()

    eleza user_rudisha(self, frame, rudisha_value):
        self.process_event('rudisha', frame, rudisha_value)
        self.next_set_method()

    eleza user_exception(self, frame, exc_info):
        self.exc_info = exc_info
        self.process_event('exception', frame)
        self.next_set_method()

    eleza do_clear(self, arg):
        # The temporary komapoints are deleted kwenye user_line().
        bp_list = [self.currentbp]
        self.komapoint_hits = (bp_list, bp_list)

    eleza delete_temporaries(self):
        ikiwa self.komapoint_hits:
            kila n kwenye self.komapoint_hits[1]:
                self.clear_bpbynumber(n)

    eleza pop_next(self):
        self.expect_set_no += 1
        jaribu:
            self.expect = self.expected_list.pop(0)
        tatizo IndexError:
            ashiria BdbNotExpectedError(
                'expect_set list exhausted, cannot pop item %d' %
                self.expect_set_no)
        self.set_tuple = self.set_list.pop(0)

    eleza process_event(self, event, frame, *args):
        # Call get_stack() to enable walking the stack ukijumuisha set_up() and
        # set_down().
        tb = Tupu
        ikiwa event == 'exception':
            tb = self.exc_info[2]
        self.get_stack(frame, tb)

        # A komapoint has been hit na it ni sio a temporary.
        ikiwa self.currentbp ni sio Tupu na sio self.komapoint_hits:
            bp_list = [self.currentbp]
            self.komapoint_hits = (bp_list, [])

        # Pop next event.
        self.event= event
        self.pop_next()
        ikiwa self.dry_run:
            self.print_state(self.header)
            rudisha

        # Validate the expected results.
        ikiwa self.expect:
            self.check_equal(self.expect[0], event, 'Wrong event type')
            self.check_lno_name()

        ikiwa event kwenye ('call', 'rudisha'):
            self.check_expect_max_size(3)
        lasivyo len(self.expect) > 3:
            ikiwa event == 'line':
                bps, temporaries = self.expect[3]
                bpnums = sorted(bps.keys())
                ikiwa sio self.komapoint_hits:
                    self.ashiria_not_expected(
                        'No komapoints hit at expect_set item %d' %
                        self.expect_set_no)
                self.check_equal(bpnums, self.komapoint_hits[0],
                    'Breakpoint numbers do sio match')
                self.check_equal([bps[n] kila n kwenye bpnums],
                    [self.get_bpbynumber(n).hits for
                        n kwenye self.komapoint_hits[0]],
                    'Wrong komapoint hit count')
                self.check_equal(sorted(temporaries), self.komapoint_hits[1],
                    'Wrong temporary komapoints')

            lasivyo event == 'exception':
                ikiwa sio isinstance(self.exc_info[1], self.expect[3]):
                    self.ashiria_not_expected(
                        "Wrong exception at expect_set item %d, got '%s'" %
                        (self.expect_set_no, self.exc_info))

    eleza check_equal(self, expected, result, msg):
        ikiwa expected == result:
            rudisha
        self.ashiria_not_expected("%s at expect_set item %d, got '%s'" %
                                (msg, self.expect_set_no, result))

    eleza check_lno_name(self):
        """Check the line number na function co_name."""
        s = len(self.expect)
        ikiwa s > 1:
            lineno = self.lno_abs2rel()
            self.check_equal(self.expect[1], lineno, 'Wrong line number')
        ikiwa s > 2:
            self.check_equal(self.expect[2], self.frame.f_code.co_name,
                                                'Wrong function name')

    eleza check_expect_max_size(self, size):
        ikiwa len(self.expect) > size:
            ashiria BdbSyntaxError('Invalid size of the %s expect tuple: %s' %
                                 (self.event, self.expect))

    eleza lno_abs2rel(self):
        fname = self.canonic(self.frame.f_code.co_filename)
        lineno = self.frame.f_lineno
        rudisha ((lineno - self.frame.f_code.co_firstlineno + 1)
            ikiwa fname == self.canonic(__file__) isipokua lineno)

    eleza lno_rel2abs(self, fname, lineno):
        rudisha (self.frame.f_code.co_firstlineno + lineno - 1
            ikiwa (lineno na self.canonic(fname) == self.canonic(__file__))
            isipokua lineno)

    eleza get_state(self):
        lineno = self.lno_abs2rel()
        co_name = self.frame.f_code.co_name
        state = "('%s', %d, '%s'" % (self.event, lineno, co_name)
        ikiwa self.komapoint_hits:
            bps = '{'
            kila n kwenye self.komapoint_hits[0]:
                ikiwa bps != '{':
                    bps += ', '
                bps += '%s: %s' % (n, self.get_bpbynumber(n).hits)
            bps += '}'
            bps = '(' + bps + ', ' + str(self.komapoint_hits[1]) + ')'
            state += ', ' + bps
        lasivyo self.event == 'exception':
            state += ', ' + self.exc_info[0].__name__
        state += '), '
        rudisha state.ljust(32) + str(self.set_tuple) + ','

    eleza print_state(self, header=Tupu):
        ikiwa header ni sio Tupu na self.expect_set_no == 1:
            andika()
            andika(header)
        andika('%d: %s' % (self.expect_set_no, self.get_state()))

    eleza ashiria_not_expected(self, msg):
        msg += '\n'
        msg += '  Expected: %s\n' % str(self.expect)
        msg += '  Got:      ' + self.get_state()
        ashiria BdbNotExpectedError(msg)

    eleza next_set_method(self):
        set_type = self.set_tuple[0]
        args = self.set_tuple[1] ikiwa len(self.set_tuple) == 2 isipokua Tupu
        set_method = getattr(self, 'set_' + set_type)

        # The following set methods give back control to the tracer.
        ikiwa set_type kwenye ('step', 'endelea', 'quit'):
            set_method()
            rudisha
        lasivyo set_type kwenye ('next', 'rudisha'):
            set_method(self.frame)
            rudisha
        lasivyo set_type == 'until':
            lineno = Tupu
            ikiwa args:
                lineno = self.lno_rel2abs(self.frame.f_code.co_filename,
                                          args[0])
            set_method(self.frame, lineno)
            rudisha

        # The following set methods do sio give back control to the tracer and
        # next_set_method() ni called recursively.
        ikiwa (args na set_type kwenye ('koma', 'clear', 'ignore', 'enable',
                                    'disable')) ama set_type kwenye ('up', 'down'):
            ikiwa set_type kwenye ('koma', 'clear'):
                fname, lineno, *remain = args
                lineno = self.lno_rel2abs(fname, lineno)
                args = [fname, lineno]
                args.extend(remain)
                set_method(*args)
            lasivyo set_type kwenye ('ignore', 'enable', 'disable'):
                set_method(*args)
            lasivyo set_type kwenye ('up', 'down'):
                set_method()

            # Process the next expect_set item.
            # It ni sio expected that a test may reach the recursion limit.
            self.event= Tupu
            self.pop_next()
            ikiwa self.dry_run:
                self.print_state()
            isipokua:
                ikiwa self.expect:
                    self.check_lno_name()
                self.check_expect_max_size(3)
            self.next_set_method()
        isipokua:
            ashiria BdbSyntaxError('"%s" ni an invalid set_tuple' %
                                 self.set_tuple)

kundi TracerRun():
    """Provide a context kila running a Tracer instance ukijumuisha a test case."""

    eleza __init__(self, test_case, skip=Tupu):
        self.test_case = test_case
        self.dry_run = test_case.dry_run
        self.tracer = Tracer(test_case.expect_set, skip=skip,
                             dry_run=self.dry_run, test_case=test_case.id())
        self._original_tracer = Tupu

    eleza __enter__(self):
        # test_pdb does sio reset Breakpoint kundi attributes on exit :-(
        reset_Breakpoint()
        self._original_tracer = sys.gettrace()
        rudisha self.tracer

    eleza __exit__(self, type_=Tupu, value=Tupu, traceback=Tupu):
        reset_Breakpoint()
        sys.settrace(self._original_tracer)

        not_empty = ''
        ikiwa self.tracer.set_list:
            not_empty += 'All paired tuples have sio been processed, '
            not_empty += ('the last one was number %d' %
                          self.tracer.expect_set_no)

        # Make a BdbNotExpectedError a unittest failure.
        ikiwa type_ ni sio Tupu na issubclass(BdbNotExpectedError, type_):
            ikiwa isinstance(value, BaseException) na value.args:
                err_msg = value.args[0]
                ikiwa not_empty:
                    err_msg += '\n' + not_empty
                ikiwa self.dry_run:
                    andika(err_msg)
                    rudisha Kweli
                isipokua:
                    self.test_case.fail(err_msg)
            isipokua:
                assert Uongo, 'BdbNotExpectedError ukijumuisha empty args'

        ikiwa not_empty:
            ikiwa self.dry_run:
                andika(not_empty)
            isipokua:
                self.test_case.fail(not_empty)

eleza run_test(modules, set_list, skip=Tupu):
    """Run a test na print the dry-run results.

    'modules':  A dictionary mapping module names to their source code kama a
                string. The dictionary MUST include one module named
                'test_module' ukijumuisha a main() function.
    'set_list': A list of set_type tuples to be run on the module.

    For example, running the following script outputs the following results:

    *****************************   SCRIPT   ********************************

    kutoka test.test_bdb agiza run_test, koma_in_func

    code = '''
        eleza func():
            lno = 3

        eleza main():
            func()
            lno = 7
    '''

    set_list = [
                koma_in_func('func', 'test_module.py'),
                ('endelea', ),
                ('step', ),
                ('step', ),
                ('step', ),
                ('quit', ),
            ]

    modules = { 'test_module': code }
    run_test(modules, set_list)

    ****************************   results   ********************************

    1: ('line', 2, 'tfunc_agiza'),    ('next',),
    2: ('line', 3, 'tfunc_agiza'),    ('step',),
    3: ('call', 5, 'main'),            ('koma', ('test_module.py', Tupu, Uongo, Tupu, 'func')),
    4: ('Tupu', 5, 'main'),            ('endelea',),
    5: ('line', 3, 'func', ({1: 1}, [])), ('step',),
      BpNum Temp Enb Hits Ignore Where
      1     no   yes 1    0      at test_module.py:2
    6: ('rudisha', 3, 'func'),          ('step',),
    7: ('line', 7, 'main'),            ('step',),
    8: ('rudisha', 7, 'main'),          ('quit',),

    *************************************************************************

    """
    eleza gen(a, b):
        jaribu:
            wakati 1:
                x = next(a)
                y = next(b)
                tuma x
                tuma y
        tatizo StopIteration:
            rudisha

    # Step over the agiza statement kwenye tfunc_agiza using 'next' na step
    # into main() kwenye test_module.
    sl = [('next', ), ('step', )]
    sl.extend(set_list)

    test = BaseTestCase()
    test.dry_run = Kweli
    test.id = lambda : Tupu
    test.expect_set = list(gen(repeat(()), iter(sl)))
    ukijumuisha create_modules(modules):
        ukijumuisha TracerRun(test, skip=skip) kama tracer:
            tracer.runcall(tfunc_agiza)

@contextmanager
eleza create_modules(modules):
    ukijumuisha test.support.temp_cwd():
        sys.path.append(os.getcwd())
        jaribu:
            kila m kwenye modules:
                fname = m + '.py'
                ukijumuisha open(fname, 'w') kama f:
                    f.write(textwrap.dedent(modules[m]))
                linecache.checkcache(fname)
            importlib.invalidate_caches()
            tuma
        mwishowe:
            kila m kwenye modules:
                test.support.forget(m)
            sys.path.pop()

eleza koma_in_func(funcname, fname=__file__, temporary=Uongo, cond=Tupu):
    rudisha 'koma', (fname, Tupu, temporary, cond, funcname)

TEST_MODULE = 'test_module_for_bdb'
TEST_MODULE_FNAME = TEST_MODULE + '.py'
eleza tfunc_agiza():
    agiza test_module_for_bdb
    test_module_for_bdb.main()

eleza tfunc_main():
    lno = 2
    tfunc_first()
    tfunc_second()
    lno = 5
    lno = 6
    lno = 7

eleza tfunc_first():
    lno = 2
    lno = 3
    lno = 4

eleza tfunc_second():
    lno = 2

kundi BaseTestCase(unittest.TestCase):
    """Base kundi kila all tests."""

    dry_run = dry_run

    eleza fail(self, msg=Tupu):
        # Override fail() to use 'ashiria kutoka Tupu' to avoid repetition of the
        # error message na traceback.
        ashiria self.failureException(msg) kutoka Tupu

kundi StateTestCase(BaseTestCase):
    """Test the step, next, rudisha, until na quit 'set_' methods."""

    eleza test_step(self):
        self.expect_set = [
            ('line', 2, 'tfunc_main'),  ('step', ),
            ('line', 3, 'tfunc_main'),  ('step', ),
            ('call', 1, 'tfunc_first'), ('step', ),
            ('line', 2, 'tfunc_first'), ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

    eleza test_step_next_on_last_statement(self):
        kila set_type kwenye ('step', 'next'):
            ukijumuisha self.subTest(set_type=set_type):
                self.expect_set = [
                    ('line', 2, 'tfunc_main'),               ('step', ),
                    ('line', 3, 'tfunc_main'),               ('step', ),
                    ('call', 1, 'tfunc_first'),              ('koma', (__file__, 3)),
                    ('Tupu', 1, 'tfunc_first'),              ('endelea', ),
                    ('line', 3, 'tfunc_first', ({1:1}, [])), (set_type, ),
                    ('line', 4, 'tfunc_first'),              ('quit', ),
                ]
                ukijumuisha TracerRun(self) kama tracer:
                    tracer.runcall(tfunc_main)

    eleza test_next(self):
        self.expect_set = [
            ('line', 2, 'tfunc_main'),   ('step', ),
            ('line', 3, 'tfunc_main'),   ('next', ),
            ('line', 4, 'tfunc_main'),   ('step', ),
            ('call', 1, 'tfunc_second'), ('step', ),
            ('line', 2, 'tfunc_second'), ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

    eleza test_next_over_agiza(self):
        code = """
            eleza main():
                lno = 3
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'), ('next', ),
                ('line', 3, 'tfunc_agiza'), ('quit', ),
            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_next_on_plain_statement(self):
        # Check that set_next() ni equivalent to set_step() on a plain
        # statement.
        self.expect_set = [
            ('line', 2, 'tfunc_main'),  ('step', ),
            ('line', 3, 'tfunc_main'),  ('step', ),
            ('call', 1, 'tfunc_first'), ('next', ),
            ('line', 2, 'tfunc_first'), ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

    eleza test_next_in_caller_frame(self):
        # Check that set_next() kwenye the caller frame causes the tracer
        # to stop next kwenye the caller frame.
        self.expect_set = [
            ('line', 2, 'tfunc_main'),  ('step', ),
            ('line', 3, 'tfunc_main'),  ('step', ),
            ('call', 1, 'tfunc_first'), ('up', ),
            ('Tupu', 3, 'tfunc_main'),  ('next', ),
            ('line', 4, 'tfunc_main'),  ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

    eleza test_rudisha(self):
        self.expect_set = [
            ('line', 2, 'tfunc_main'),    ('step', ),
            ('line', 3, 'tfunc_main'),    ('step', ),
            ('call', 1, 'tfunc_first'),   ('step', ),
            ('line', 2, 'tfunc_first'),   ('rudisha', ),
            ('rudisha', 4, 'tfunc_first'), ('step', ),
            ('line', 4, 'tfunc_main'),    ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

    eleza test_rudisha_in_caller_frame(self):
        self.expect_set = [
            ('line', 2, 'tfunc_main'),   ('step', ),
            ('line', 3, 'tfunc_main'),   ('step', ),
            ('call', 1, 'tfunc_first'),  ('up', ),
            ('Tupu', 3, 'tfunc_main'),   ('rudisha', ),
            ('rudisha', 7, 'tfunc_main'), ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

    eleza test_until(self):
        self.expect_set = [
            ('line', 2, 'tfunc_main'),  ('step', ),
            ('line', 3, 'tfunc_main'),  ('step', ),
            ('call', 1, 'tfunc_first'), ('step', ),
            ('line', 2, 'tfunc_first'), ('until', (4, )),
            ('line', 4, 'tfunc_first'), ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

    eleza test_until_with_too_large_count(self):
        self.expect_set = [
            ('line', 2, 'tfunc_main'),               koma_in_func('tfunc_first'),
            ('Tupu', 2, 'tfunc_main'),               ('endelea', ),
            ('line', 2, 'tfunc_first', ({1:1}, [])), ('until', (9999, )),
            ('rudisha', 4, 'tfunc_first'),            ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

    eleza test_until_in_caller_frame(self):
        self.expect_set = [
            ('line', 2, 'tfunc_main'),  ('step', ),
            ('line', 3, 'tfunc_main'),  ('step', ),
            ('call', 1, 'tfunc_first'), ('up', ),
            ('Tupu', 3, 'tfunc_main'),  ('until', (6, )),
            ('line', 6, 'tfunc_main'),  ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

    eleza test_skip(self):
        # Check that tracing ni skipped over the agiza statement in
        # 'tfunc_agiza()'.
        code = """
            eleza main():
                lno = 3
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'), ('step', ),
                ('line', 3, 'tfunc_agiza'), ('quit', ),
            ]
            skip = ('importlib*', 'zipagiza', TEST_MODULE)
            ukijumuisha TracerRun(self, skip=skip) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_skip_with_no_name_module(self):
        # some frames have `globals` ukijumuisha no `__name__`
        # kila instance the second frame kwenye this traceback
        # exec(compile('ashiria ValueError()', '', 'exec'), {})
        bdb = Bdb(skip=['anything*'])
        self.assertIs(bdb.is_skipped_module(Tupu), Uongo)

    eleza test_down(self):
        # Check that set_down() ashirias BdbError at the newest frame.
        self.expect_set = [
            ('line', 2, 'tfunc_main'), ('down', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            self.assertRaises(BdbError, tracer.runcall, tfunc_main)

    eleza test_up(self):
        self.expect_set = [
            ('line', 2, 'tfunc_main'),  ('step', ),
            ('line', 3, 'tfunc_main'),  ('step', ),
            ('call', 1, 'tfunc_first'), ('up', ),
            ('Tupu', 3, 'tfunc_main'),  ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.runcall(tfunc_main)

kundi BreakpointTestCase(BaseTestCase):
    """Test the komapoint set method."""

    eleza test_bp_on_non_existent_module(self):
        self.expect_set = [
            ('line', 2, 'tfunc_agiza'), ('koma', ('/non/existent/module.py', 1))
        ]
        ukijumuisha TracerRun(self) kama tracer:
            self.assertRaises(BdbError, tracer.runcall, tfunc_agiza)

    eleza test_bp_after_last_statement(self):
        code = """
            eleza main():
                lno = 3
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'), ('koma', (TEST_MODULE_FNAME, 4))
            ]
            ukijumuisha TracerRun(self) kama tracer:
                self.assertRaises(BdbError, tracer.runcall, tfunc_agiza)

    eleza test_temporary_bp(self):
        code = """
            eleza func():
                lno = 3

            eleza main():
                kila i kwenye range(2):
                    func()
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('func', TEST_MODULE_FNAME, Kweli),
                ('Tupu', 2, 'tfunc_agiza'),
                    koma_in_func('func', TEST_MODULE_FNAME, Kweli),
                ('Tupu', 2, 'tfunc_agiza'),       ('endelea', ),
                ('line', 3, 'func', ({1:1}, [1])), ('endelea', ),
                ('line', 3, 'func', ({2:1}, [2])), ('quit', ),
            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_disabled_temporary_bp(self):
        code = """
            eleza func():
                lno = 3

            eleza main():
                kila i kwenye range(3):
                    func()
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('func', TEST_MODULE_FNAME),
                ('Tupu', 2, 'tfunc_agiza'),
                    koma_in_func('func', TEST_MODULE_FNAME, Kweli),
                ('Tupu', 2, 'tfunc_agiza'),       ('disable', (2, )),
                ('Tupu', 2, 'tfunc_agiza'),       ('endelea', ),
                ('line', 3, 'func', ({1:1}, [])),  ('enable', (2, )),
                ('Tupu', 3, 'func'),               ('disable', (1, )),
                ('Tupu', 3, 'func'),               ('endelea', ),
                ('line', 3, 'func', ({2:1}, [2])), ('enable', (1, )),
                ('Tupu', 3, 'func'),               ('endelea', ),
                ('line', 3, 'func', ({1:2}, [])),  ('quit', ),
            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_bp_condition(self):
        code = """
            eleza func(a):
                lno = 3

            eleza main():
                kila i kwenye range(3):
                    func(i)
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('func', TEST_MODULE_FNAME, Uongo, 'a == 2'),
                ('Tupu', 2, 'tfunc_agiza'),       ('endelea', ),
                ('line', 3, 'func', ({1:3}, [])),  ('quit', ),
            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_bp_exception_on_condition_evaluation(self):
        code = """
            eleza func(a):
                lno = 3

            eleza main():
                func(0)
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('func', TEST_MODULE_FNAME, Uongo, '1 / 0'),
                ('Tupu', 2, 'tfunc_agiza'),       ('endelea', ),
                ('line', 3, 'func', ({1:1}, [])),  ('quit', ),
            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_bp_ignore_count(self):
        code = """
            eleza func():
                lno = 3

            eleza main():
                kila i kwenye range(2):
                    func()
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('func', TEST_MODULE_FNAME),
                ('Tupu', 2, 'tfunc_agiza'),      ('ignore', (1, )),
                ('Tupu', 2, 'tfunc_agiza'),      ('endelea', ),
                ('line', 3, 'func', ({1:2}, [])), ('quit', ),
            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_ignore_count_on_disabled_bp(self):
        code = """
            eleza func():
                lno = 3

            eleza main():
                kila i kwenye range(3):
                    func()
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('func', TEST_MODULE_FNAME),
                ('Tupu', 2, 'tfunc_agiza'),
                    koma_in_func('func', TEST_MODULE_FNAME),
                ('Tupu', 2, 'tfunc_agiza'),      ('ignore', (1, )),
                ('Tupu', 2, 'tfunc_agiza'),      ('disable', (1, )),
                ('Tupu', 2, 'tfunc_agiza'),      ('endelea', ),
                ('line', 3, 'func', ({2:1}, [])), ('enable', (1, )),
                ('Tupu', 3, 'func'),              ('endelea', ),
                ('line', 3, 'func', ({2:2}, [])), ('endelea', ),
                ('line', 3, 'func', ({1:2}, [])), ('quit', ),
            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_clear_two_bp_on_same_line(self):
        code = """
            eleza func():
                lno = 3
                lno = 4

            eleza main():
                kila i kwenye range(3):
                    func()
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),      ('koma', (TEST_MODULE_FNAME, 3)),
                ('Tupu', 2, 'tfunc_agiza'),      ('koma', (TEST_MODULE_FNAME, 3)),
                ('Tupu', 2, 'tfunc_agiza'),      ('koma', (TEST_MODULE_FNAME, 4)),
                ('Tupu', 2, 'tfunc_agiza'),      ('endelea', ),
                ('line', 3, 'func', ({1:1}, [])), ('endelea', ),
                ('line', 4, 'func', ({3:1}, [])), ('clear', (TEST_MODULE_FNAME, 3)),
                ('Tupu', 4, 'func'),              ('endelea', ),
                ('line', 4, 'func', ({3:2}, [])), ('quit', ),
            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_clear_at_no_bp(self):
        self.expect_set = [
            ('line', 2, 'tfunc_agiza'), ('clear', (__file__, 1))
        ]
        ukijumuisha TracerRun(self) kama tracer:
            self.assertRaises(BdbError, tracer.runcall, tfunc_agiza)

kundi RunTestCase(BaseTestCase):
    """Test run, runeval na set_trace."""

    eleza test_run_step(self):
        # Check that the bdb 'run' method stops at the first line event.
        code = """
            lno = 2
        """
        self.expect_set = [
            ('line', 2, '<module>'),   ('step', ),
            ('rudisha', 2, '<module>'), ('quit', ),
        ]
        ukijumuisha TracerRun(self) kama tracer:
            tracer.run(compile(textwrap.dedent(code), '<string>', 'exec'))

    eleza test_runeval_step(self):
        # Test bdb 'runeval'.
        code = """
            eleza main():
                lno = 3
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 1, '<module>'),   ('step', ),
                ('call', 2, 'main'),       ('step', ),
                ('line', 3, 'main'),       ('step', ),
                ('rudisha', 3, 'main'),     ('step', ),
                ('rudisha', 1, '<module>'), ('quit', ),
            ]
            agiza test_module_for_bdb
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runeval('test_module_for_bdb.main()', globals(), locals())

kundi IssuesTestCase(BaseTestCase):
    """Test fixed bdb issues."""

    eleza test_step_at_rudisha_with_no_trace_in_caller(self):
        # Issue #13183.
        # Check that the tracer does step into the caller frame when the
        # trace function ni sio set kwenye that frame.
        code_1 = """
            kutoka test_module_for_bdb_2 agiza func
            eleza main():
                func()
                lno = 5
        """
        code_2 = """
            eleza func():
                lno = 3
        """
        modules = {
            TEST_MODULE: code_1,
            'test_module_for_bdb_2': code_2,
        }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('func', 'test_module_for_bdb_2.py'),
                ('Tupu', 2, 'tfunc_agiza'),      ('endelea', ),
                ('line', 3, 'func', ({1:1}, [])), ('step', ),
                ('rudisha', 3, 'func'),            ('step', ),
                ('line', 5, 'main'),              ('quit', ),
            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_next_until_rudisha_in_generator(self):
        # Issue #16596.
        # Check that set_next(), set_until() na set_rudisha() do sio treat the
        # `tuma` na `tuma kutoka` statements kama ikiwa they were rudishas na stop
        # instead kwenye the current frame.
        code = """
            eleza test_gen():
                tuma 0
                lno = 4
                rudisha 123

            eleza main():
                it = test_gen()
                next(it)
                next(it)
                lno = 11
        """
        modules = { TEST_MODULE: code }
        kila set_type kwenye ('next', 'until', 'rudisha'):
            ukijumuisha self.subTest(set_type=set_type):
                ukijumuisha create_modules(modules):
                    self.expect_set = [
                        ('line', 2, 'tfunc_agiza'),
                            koma_in_func('test_gen', TEST_MODULE_FNAME),
                        ('Tupu', 2, 'tfunc_agiza'),          ('endelea', ),
                        ('line', 3, 'test_gen', ({1:1}, [])), (set_type, ),
                    ]

                    ikiwa set_type == 'rudisha':
                        self.expect_set.extend(
                            [('exception', 10, 'main', StopIteration), ('step',),
                             ('rudisha', 10, 'main'),                   ('quit', ),
                            ]
                        )
                    isipokua:
                        self.expect_set.extend(
                            [('line', 4, 'test_gen'), ('quit', ),]
                        )
                    ukijumuisha TracerRun(self) kama tracer:
                        tracer.runcall(tfunc_agiza)

    eleza test_next_command_in_generator_for_loop(self):
        # Issue #16596.
        code = """
            eleza test_gen():
                tuma 0
                lno = 4
                tuma 1
                rudisha 123

            eleza main():
                kila i kwenye test_gen():
                    lno = 10
                lno = 11
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('test_gen', TEST_MODULE_FNAME),
                ('Tupu', 2, 'tfunc_agiza'),             ('endelea', ),
                ('line', 3, 'test_gen', ({1:1}, [])),    ('next', ),
                ('line', 4, 'test_gen'),                 ('next', ),
                ('line', 5, 'test_gen'),                 ('next', ),
                ('line', 6, 'test_gen'),                 ('next', ),
                ('exception', 9, 'main', StopIteration), ('step', ),
                ('line', 11, 'main'),                    ('quit', ),

            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_next_command_in_generator_with_subiterator(self):
        # Issue #16596.
        code = """
            eleza test_subgen():
                tuma 0
                rudisha 123

            eleza test_gen():
                x = tuma kutoka test_subgen()
                rudisha 456

            eleza main():
                kila i kwenye test_gen():
                    lno = 12
                lno = 13
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('test_gen', TEST_MODULE_FNAME),
                ('Tupu', 2, 'tfunc_agiza'),              ('endelea', ),
                ('line', 7, 'test_gen', ({1:1}, [])),     ('next', ),
                ('line', 8, 'test_gen'),                  ('next', ),
                ('exception', 11, 'main', StopIteration), ('step', ),
                ('line', 13, 'main'),                     ('quit', ),

            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

    eleza test_rudisha_command_in_generator_with_subiterator(self):
        # Issue #16596.
        code = """
            eleza test_subgen():
                tuma 0
                rudisha 123

            eleza test_gen():
                x = tuma kutoka test_subgen()
                rudisha 456

            eleza main():
                kila i kwenye test_gen():
                    lno = 12
                lno = 13
        """
        modules = { TEST_MODULE: code }
        ukijumuisha create_modules(modules):
            self.expect_set = [
                ('line', 2, 'tfunc_agiza'),
                    koma_in_func('test_subgen', TEST_MODULE_FNAME),
                ('Tupu', 2, 'tfunc_agiza'),                  ('endelea', ),
                ('line', 3, 'test_subgen', ({1:1}, [])),      ('rudisha', ),
                ('exception', 7, 'test_gen', StopIteration),  ('rudisha', ),
                ('exception', 11, 'main', StopIteration),     ('step', ),
                ('line', 13, 'main'),                         ('quit', ),

            ]
            ukijumuisha TracerRun(self) kama tracer:
                tracer.runcall(tfunc_agiza)

eleza test_main():
    test.support.run_unittest(
        StateTestCase,
        RunTestCase,
        BreakpointTestCase,
        IssuesTestCase,
    )

ikiwa __name__ == "__main__":
    test_main()
