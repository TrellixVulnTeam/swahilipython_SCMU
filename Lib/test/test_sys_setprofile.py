agiza gc
agiza pprint
agiza sys
agiza unittest


kundi TestGetProfile(unittest.TestCase):
    eleza setUp(self):
        sys.setprofile(Tupu)

    eleza tearDown(self):
        sys.setprofile(Tupu)

    eleza test_empty(self):
        self.assertIsTupu(sys.getprofile())

    eleza test_setget(self):
        eleza fn(*args):
            pita

        sys.setprofile(fn)
        self.assertIs(sys.getprofile(), fn)

kundi HookWatcher:
    eleza __init__(self):
        self.frames = []
        self.events = []

    eleza callback(self, frame, event, arg):
        ikiwa (event == "call"
            ama event == "rudisha"
            ama event == "exception"):
            self.add_event(event, frame)

    eleza add_event(self, event, frame=Tupu):
        """Add an event to the log."""
        ikiwa frame ni Tupu:
            frame = sys._getframe(1)

        jaribu:
            frameno = self.frames.index(frame)
        tatizo ValueError:
            frameno = len(self.frames)
            self.frames.append(frame)

        self.events.append((frameno, event, ident(frame)))

    eleza get_events(self):
        """Remove calls to add_event()."""
        disallowed = [ident(self.add_event.__func__), ident(ident)]
        self.frames = Tupu

        rudisha [item kila item kwenye self.events ikiwa item[2] haiko kwenye disallowed]


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

    eleza trace_rudisha(self, frame):
        self.add_event('rudisha', frame)
        self.stack.pop()

    eleza trace_exception(self, frame):
        self.testcase.fail(
            "the profiler should never receive exception events")

    eleza trace_pita(self, frame):
        pita

    dispatch = {
        'call': trace_call,
        'exception': trace_exception,
        'rudisha': trace_rudisha,
        'c_call': trace_pita,
        'c_rudisha': trace_pita,
        'c_exception': trace_pita,
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
            pita
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
                              ])

    eleza test_exception(self):
        eleza f(p):
            1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
                              ])

    eleza test_caught_exception(self):
        eleza f(p):
            jaribu: 1/0
            except: pita
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
                              ])

    eleza test_caught_nested_exception(self):
        eleza f(p):
            jaribu: 1/0
            except: pita
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
                              ])

    eleza test_nested_exception(self):
        eleza f(p):
            1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              # This isn't what I expected:
                              # (0, 'exception', protect_ident),
                              # I expected this again:
                              (1, 'rudisha', f_ident),
                              ])

    eleza test_exception_in_except_clause(self):
        eleza f(p):
            1/0
        eleza g(p):
            jaribu:
                f(p)
            except:
                jaribu: f(p)
                except: pita
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              (2, 'call', f_ident),
                              (2, 'rudisha', f_ident),
                              (3, 'call', f_ident),
                              (3, 'rudisha', f_ident),
                              (1, 'rudisha', g_ident),
                              ])

    eleza test_exception_propagation(self):
        eleza f(p):
            1/0
        eleza g(p):
            jaribu: f(p)
            mwishowe: p.add_event("falling through")
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              (2, 'call', f_ident),
                              (2, 'rudisha', f_ident),
                              (1, 'falling through', g_ident),
                              (1, 'rudisha', g_ident),
                              ])

    eleza test_ashiria_twice(self):
        eleza f(p):
            jaribu: 1/0
            except: 1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
                              ])

    eleza test_ashiria_reashiria(self):
        eleza f(p):
            jaribu: 1/0
            except: ashiria
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
                              ])

    eleza test_ashiria(self):
        eleza f(p):
            ashiria Exception()
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
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
                              (5, 'rudisha', f_ident),
                              (4, 'rudisha', g_ident),
                              (3, 'rudisha', h_ident),
                              (2, 'rudisha', i_ident),
                              (1, 'rudisha', j_ident),
                              ])

    eleza test_generator(self):
        eleza f():
            kila i kwenye range(2):
                tuma i
        eleza g(p):
            kila i kwenye f():
                pita
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              # call the iterator twice to generate values
                              (2, 'call', f_ident),
                              (2, 'rudisha', f_ident),
                              (2, 'call', f_ident),
                              (2, 'rudisha', f_ident),
                              # once more; rudishas end-of-iteration with
                              # actually raising an exception
                              (2, 'call', f_ident),
                              (2, 'rudisha', f_ident),
                              (1, 'rudisha', g_ident),
                              ])

    eleza test_stop_iteration(self):
        eleza f():
            kila i kwenye range(2):
                tuma i
        eleza g(p):
            kila i kwenye f():
                pita
        f_ident = ident(f)
        g_ident = ident(g)
        self.check_events(g, [(1, 'call', g_ident),
                              # call the iterator twice to generate values
                              (2, 'call', f_ident),
                              (2, 'rudisha', f_ident),
                              (2, 'call', f_ident),
                              (2, 'rudisha', f_ident),
                              # once more to hit the ashiria:
                              (2, 'call', f_ident),
                              (2, 'rudisha', f_ident),
                              (1, 'rudisha', g_ident),
                              ])


kundi ProfileSimulatorTestCase(TestCaseBase):
    eleza new_watcher(self):
        rudisha ProfileSimulator(self)

    eleza test_simple(self):
        eleza f(p):
            pita
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
                              ])

    eleza test_basic_exception(self):
        eleza f(p):
            1/0
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
                              ])

    eleza test_caught_exception(self):
        eleza f(p):
            jaribu: 1/0
            except: pita
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident),
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
                              (5, 'rudisha', f_ident),
                              (4, 'rudisha', g_ident),
                              (3, 'rudisha', h_ident),
                              (2, 'rudisha', i_ident),
                              (1, 'rudisha', j_ident),
                              ])

    # bpo-34125: profiling method_descriptor with **kwargs
    eleza test_unbound_method(self):
        kwargs = {}
        eleza f(p):
            dict.get({}, 42, **kwargs)
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident)])

    # Test an invalid call (bpo-34126)
    eleza test_unbound_method_no_args(self):
        eleza f(p):
            dict.get()
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident)])

    # Test an invalid call (bpo-34126)
    eleza test_unbound_method_invalid_args(self):
        eleza f(p):
            dict.get(print, 42)
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident)])

    # Test an invalid call (bpo-34125)
    eleza test_unbound_method_no_keyword_args(self):
        kwargs = {}
        eleza f(p):
            dict.get(**kwargs)
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident)])

    # Test an invalid call (bpo-34125)
    eleza test_unbound_method_invalid_keyword_args(self):
        kwargs = {}
        eleza f(p):
            dict.get(print, 42, **kwargs)
        f_ident = ident(f)
        self.check_events(f, [(1, 'call', f_ident),
                              (1, 'rudisha', f_ident)])


eleza ident(function):
    ikiwa hasattr(function, "f_code"):
        code = function.f_code
    isipokua:
        code = function.__code__
    rudisha code.co_firstlineno, code.co_name


eleza protect(f, p):
    jaribu: f(p)
    except: pita

protect_ident = ident(protect)


eleza capture_events(callable, p=Tupu):
    ikiwa p ni Tupu:
        p = HookWatcher()
    # Disable the garbage collector. This prevents __del__s kutoka showing up in
    # traces.
    old_gc = gc.isenabled()
    gc.disable()
    jaribu:
        sys.setprofile(p.callback)
        protect(callable, p)
        sys.setprofile(Tupu)
    mwishowe:
        ikiwa old_gc:
            gc.enable()
    rudisha p.get_events()[1:-1]


eleza show_events(callable):
    agiza pprint
    pprint.pandika(capture_events(callable))


ikiwa __name__ == "__main__":
    unittest.main()
