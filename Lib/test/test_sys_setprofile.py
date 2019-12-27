agiza gc
agiza pprint
agiza sys
agiza unittest


kundi TestGetProfile(unittest.TestCase):
    eleza setUp(self):
        sys.setprofile(None)

    eleza tearDown(self):
        sys.setprofile(None)

    eleza test_empty(self):
        self.assertIsNone(sys.getprofile())

    eleza test_setget(self):
        eleza fn(*args):
            pass

        sys.setprofile(fn)
        self.assertIs(sys.getprofile(), fn)

kundi HookWatcher:
    eleza __init__(self):
        self.frames = []
        self.events = []

    eleza callback(self, frame, event, arg):
        ikiwa (event == "call"
            or event == "return"
            or event == "exception"):
            self.add_event(event, frame)

    eleza add_event(self, event, frame=None):
        """Add an event to the log."""
        ikiwa frame is None:
            frame = sys._getframe(1)

        try:
            frameno = self.frames.index(frame)
        except ValueError:
            frameno = len(self.frames)
            self.frames.append(frame)

        self.events.append((frameno, event, ident(frame)))

    eleza get_events(self):
        """Remove calls to add_event()."""
        disallowed = [ident(self.add_event.__func__), ident(ident)]
        self.frames = None

        rudisha [item for item in self.events ikiwa item[2] not in disallowed]


kundi ProfileSimulator(HookWatcher):
    eleza __init__(self, testcase):
        self.testcase = testcase
        self.stack = []
        HookWatcher.__init__(self)

    eleza callback(self, frame, event, arg):
        # Callback registered with sys.setprofile()/sys.settrace()
        self.dispatch[event](self, frame)

    eleza trace_call(self, frame):
        self.add_event('call', frame)
        self.stack.append(frame)

    eleza trace_return(self, frame):
        self.add_event('return', frame)
        self.stack.pop()

    eleza trace_exception(self, frame):
        self.testcase.fail(
            "the profiler should never receive exception events")

    eleza trace_pass(self, frame):
        pass

    dispatch = {
        'call': trace_call,
        'exception': trace_exception,
        'return': trace_return,
        'c_call': trace_pass,
        'c_return': trace_pass,
        'c_exception': trace_pass,
        }


kundi TestCaseBase(unittest.TestCase):
    eleza check_events(self, callable, expected):
        events = capture_events(callable, self.new_watcher())
        ikiwa events != expected:
            self.fail("Expected events:\n%s\nReceived events:\n%s"
                      % (pprint.pformat(expected), pprint.pformat(events)))


kundi ProfileHookTestCase(TestCaseBase):
    eleza new_watcher(self):
        rudisha HookWatcher()

    eleza test_simple(self):
        eleza f(p):
            pass
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_exception(self):
        eleza f(p):
            1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_caught_exception(self):
        eleza f(p):
            try: 1/0
            except: pass
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_caught_nested_exception(self):
        eleza f(p):
            try: 1/0
            except: pass
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_nested_exception(self):
        eleza f(p):
            1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              # This isn't what I expected:
                              # (0, 'exception', protect_ident),
                              # I expected this again:
                              (1, 'return', f_ident),
                              ])

    eleza test_exception_in_except_clause(self):
        eleza f(p):
            1/0
        eleza g(p):
            try:
                f(p)
            except:
                try: f(p)
                except: pass
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (3, 'call', f_ident),
                              (3, 'return', f_ident),
                              (1, 'return', g_ident),
                              ])

    eleza test_exception_propagation(self):
        eleza f(p):
            1/0
        eleza g(p):
            try: f(p)
            finally: p.add_event("falling through")
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (1, 'falling through', g_ident),
                              (1, 'return', g_ident),
                              ])

    eleza test_raise_twice(self):
        eleza f(p):
            try: 1/0
            except: 1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_raise_reraise(self):
        eleza f(p):
            try: 1/0
            except: raise
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_raise(self):
        eleza f(p):
            raise Exception()
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_distant_exception(self):
        eleza f():
            1/0
        eleza g():
            f()
        eleza h():
            g()
        eleza i():
            h()
        eleza j(p):
            i()
        f_ident = ident(f)
        g_ident = ident(g)
        h_ident = ident(h)
        i_ident = ident(i)
        j_ident = ident(j)
        self.check_events(j, [(1, 'call', j_ident),
                              (2, 'call', i_ident),
                              (3, 'call', h_ident),
                              (4, 'call', g_ident),
                              (5, 'call', f_ident),
                              (5, 'return', f_ident),
                              (4, 'return', g_ident),
                              (3, 'return', h_ident),
                              (2, 'return', i_ident),
                              (1, 'return', j_ident),
                              ])

    eleza test_generator(self):
        eleza f():
            for i in range(2):
                yield i
        eleza g(p):
            for i in f():
                pass
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              # call the iterator twice to generate values
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              # once more; returns end-of-iteration with
                              # actually raising an exception
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (1, 'return', g_ident),
                              ])

    eleza test_stop_iteration(self):
        eleza f():
            for i in range(2):
                yield i
        eleza g(p):
            for i in f():
                pass
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              # call the iterator twice to generate values
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              # once more to hit the raise:
                              (2, 'call', f_ident),
                              (2, 'return', f_ident),
                              (1, 'return', g_ident),
                              ])


kundi ProfileSimulatorTestCase(TestCaseBase):
    eleza new_watcher(self):
        rudisha ProfileSimulator(self)

    eleza test_simple(self):
        eleza f(p):
            pass
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_basic_exception(self):
        eleza f(p):
            1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_caught_exception(self):
        eleza f(p):
            try: 1/0
            except: pass
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident),
                              ])

    eleza test_distant_exception(self):
        eleza f():
            1/0
        eleza g():
            f()
        eleza h():
            g()
        eleza i():
            h()
        eleza j(p):
            i()
        f_ident = ident(f)
        g_ident = ident(g)
        h_ident = ident(h)
        i_ident = ident(i)
        j_ident = ident(j)
        self.check_events(j, [(1, 'call', j_ident),
                              (2, 'call', i_ident),
                              (3, 'call', h_ident),
                              (4, 'call', g_ident),
                              (5, 'call', f_ident),
                              (5, 'return', f_ident),
                              (4, 'return', g_ident),
                              (3, 'return', h_ident),
                              (2, 'return', i_ident),
                              (1, 'return', j_ident),
                              ])

    # bpo-34125: profiling method_descriptor with **kwargs
    eleza test_unbound_method(self):
        kwargs = {}
        eleza f(p):
            dict.get({}, 42, **kwargs)
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident)])

    # Test an invalid call (bpo-34126)
    eleza test_unbound_method_no_args(self):
        eleza f(p):
            dict.get()
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident)])

    # Test an invalid call (bpo-34126)
    eleza test_unbound_method_invalid_args(self):
        eleza f(p):
            dict.get(print, 42)
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident)])

    # Test an invalid call (bpo-34125)
    eleza test_unbound_method_no_keyword_args(self):
        kwargs = {}
        eleza f(p):
            dict.get(**kwargs)
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident)])

    # Test an invalid call (bpo-34125)
    eleza test_unbound_method_invalid_keyword_args(self):
        kwargs = {}
        eleza f(p):
            dict.get(print, 42, **kwargs)
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'return', f_ident)])


eleza ident(function):
    ikiwa hasattr(function, "f_code"):
        code = function.f_code
    else:
        code = function.__code__
    rudisha code.co_firstlineno, code.co_name


eleza protect(f, p):
    try: f(p)
    except: pass

protect_ident = ident(protect)


eleza capture_events(callable, p=None):
    ikiwa p is None:
        p = HookWatcher()
    # Disable the garbage collector. This prevents __del__s kutoka showing up in
    # traces.
    old_gc = gc.isenabled()
    gc.disable()
    try:
        sys.setprofile(p.callback)
        protect(callable, p)
        sys.setprofile(None)
    finally:
        ikiwa old_gc:
            gc.enable()
    rudisha p.get_events()[1:-1]


eleza show_events(callable):
    agiza pprint
    pprint.pandika(capture_events(callable))


ikiwa __name__ == "__main__":
    unittest.main()
