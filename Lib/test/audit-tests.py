"""This script contains the actual auditing tests.

It should sio be imported directly, but should be run by the test_audit
module ukijumuisha arguments identifying each test.

"""

agiza contextlib
agiza sys


kundi TestHook:
    """Used kwenye standard hook tests to collect any logged events.

    Should be used kwenye a ukijumuisha block to ensure that it has no impact
    after the test completes.
    """

    eleza __init__(self, raise_on_events=Tupu, exc_type=RuntimeError):
        self.raise_on_events = raise_on_events ama ()
        self.exc_type = exc_type
        self.seen = []
        self.closed = Uongo

    eleza __enter__(self, *a):
        sys.addaudithook(self)
        rudisha self

    eleza __exit__(self, *a):
        self.close()

    eleza close(self):
        self.closed = Kweli

    @property
    eleza seen_events(self):
        rudisha [i[0] kila i kwenye self.seen]

    eleza __call__(self, event, args):
        ikiwa self.closed:
            return
        self.seen.append((event, args))
        ikiwa event kwenye self.raise_on_events:
            ashiria self.exc_type("saw event " + event)


kundi TestFinalizeHook:
    """Used kwenye the test_finalize_hooks function to ensure that hooks
    are correctly cleaned up, that they are notified about the cleanup,
    na are unable to prevent it.
    """

    eleza __init__(self):
        andika("Created", id(self), file=sys.stdout, flush=Kweli)

    eleza __call__(self, event, args):
        # Avoid recursion when we call id() below
        ikiwa event == "builtins.id":
            return

        andika(event, id(self), file=sys.stdout, flush=Kweli)

        ikiwa event == "cpython._PySys_ClearAuditHooks":
            ashiria RuntimeError("Should be ignored")
        lasivyo event == "cpython.PyInterpreterState_Clear":
            ashiria RuntimeError("Should be ignored")


# Simple helpers, since we are haiko kwenye unittest here
eleza assertEqual(x, y):
    ikiwa x != y:
        ashiria AssertionError(f"{x!r} should equal {y!r}")


eleza assertIn(el, series):
    ikiwa el haiko kwenye series:
        ashiria AssertionError(f"{el!r} should be kwenye {series!r}")


eleza assertNotIn(el, series):
    ikiwa el kwenye series:
        ashiria AssertionError(f"{el!r} should sio be kwenye {series!r}")


eleza assertSequenceEqual(x, y):
    ikiwa len(x) != len(y):
        ashiria AssertionError(f"{x!r} should equal {y!r}")
    ikiwa any(ix != iy kila ix, iy kwenye zip(x, y)):
        ashiria AssertionError(f"{x!r} should equal {y!r}")


@contextlib.contextmanager
eleza assertRaises(ex_type):
    jaribu:
        tuma
        assert Uongo, f"expected {ex_type}"
    tatizo BaseException kama ex:
        ikiwa isinstance(ex, AssertionError):
            raise
        assert type(ex) ni ex_type, f"{ex} should be {ex_type}"


eleza test_basic():
    ukijumuisha TestHook() kama hook:
        sys.audit("test_event", 1, 2, 3)
        assertEqual(hook.seen[0][0], "test_event")
        assertEqual(hook.seen[0][1], (1, 2, 3))


eleza test_block_add_hook():
    # Raising an exception should prevent a new hook kutoka being added,
    # but will sio propagate out.
    ukijumuisha TestHook(raise_on_events="sys.addaudithook") kama hook1:
        ukijumuisha TestHook() kama hook2:
            sys.audit("test_event")
            assertIn("test_event", hook1.seen_events)
            assertNotIn("test_event", hook2.seen_events)


eleza test_block_add_hook_baseexception():
    # Raising BaseException will propagate out when adding a hook
    ukijumuisha assertRaises(BaseException):
        ukijumuisha TestHook(
            raise_on_events="sys.addaudithook", exc_type=BaseException
        ) kama hook1:
            # Adding this next hook should ashiria BaseException
            ukijumuisha TestHook() kama hook2:
                pita


eleza test_finalize_hooks():
    sys.addaudithook(TestFinalizeHook())


eleza test_pickle():
    agiza pickle

    kundi PicklePrint:
        eleza __reduce_ex__(self, p):
            rudisha str, ("Pwned!",)

    payload_1 = pickle.dumps(PicklePrint())
    payload_2 = pickle.dumps(("a", "b", "c", 1, 2, 3))

    # Before we add the hook, ensure our malicious pickle loads
    assertEqual("Pwned!", pickle.loads(payload_1))

    ukijumuisha TestHook(raise_on_events="pickle.find_class") kama hook:
        ukijumuisha assertRaises(RuntimeError):
            # With the hook enabled, loading globals ni sio allowed
            pickle.loads(payload_1)
        # pickles ukijumuisha no globals are okay
        pickle.loads(payload_2)


eleza test_monkeypatch():
    kundi A:
        pita

    kundi B:
        pita

    kundi C(A):
        pita

    a = A()

    ukijumuisha TestHook() kama hook:
        # Catch name changes
        C.__name__ = "X"
        # Catch type changes
        C.__bases__ = (B,)
        # Ensure bypitaing __setattr__ ni still caught
        type.__dict__["__bases__"].__set__(C, (B,))
        # Catch attribute replacement
        C.__init__ = B.__init__
        # Catch attribute addition
        C.new_attr = 123
        # Catch kundi changes
        a.__class__ = B

    actual = [(a[0], a[1]) kila e, a kwenye hook.seen ikiwa e == "object.__setattr__"]
    assertSequenceEqual(
        [(C, "__name__"), (C, "__bases__"), (C, "__bases__"), (a, "__class__")], actual
    )


eleza test_open():
    # SSLContext.load_dh_params uses _Py_fopen_obj rather than normal open()
    jaribu:
        agiza ssl

        load_dh_params = ssl.create_default_context().load_dh_params
    tatizo ImportError:
        load_dh_params = Tupu

    # Try a range of "open" functions.
    # All of them should fail
    ukijumuisha TestHook(raise_on_events={"open"}) kama hook:
        kila fn, *args kwenye [
            (open, sys.argv[2], "r"),
            (open, sys.executable, "rb"),
            (open, 3, "wb"),
            (open, sys.argv[2], "w", -1, Tupu, Tupu, Tupu, Uongo, lambda *a: 1),
            (load_dh_params, sys.argv[2]),
        ]:
            ikiwa sio fn:
                endelea
            ukijumuisha assertRaises(RuntimeError):
                fn(*args)

    actual_mode = [(a[0], a[1]) kila e, a kwenye hook.seen ikiwa e == "open" na a[1]]
    actual_flag = [(a[0], a[2]) kila e, a kwenye hook.seen ikiwa e == "open" na sio a[1]]
    assertSequenceEqual(
        [
            i
            kila i kwenye [
                (sys.argv[2], "r"),
                (sys.executable, "r"),
                (3, "w"),
                (sys.argv[2], "w"),
                (sys.argv[2], "rb") ikiwa load_dh_params isipokua Tupu,
            ]
            ikiwa i ni sio Tupu
        ],
        actual_mode,
    )
    assertSequenceEqual([], actual_flag)


eleza test_cantrace():
    traced = []

    eleza trace(frame, event, *args):
        ikiwa frame.f_code == TestHook.__call__.__code__:
            traced.append(event)

    old = sys.settrace(trace)
    jaribu:
        ukijumuisha TestHook() kama hook:
            # No traced call
            eval("1")

            # No traced call
            hook.__cantrace__ = Uongo
            eval("2")

            # One traced call
            hook.__cantrace__ = Kweli
            eval("3")

            # Two traced calls (writing to private member, eval)
            hook.__cantrace__ = 1
            eval("4")

            # One traced call (writing to private member)
            hook.__cantrace__ = 0
    mwishowe:
        sys.settrace(old)

    assertSequenceEqual(["call"] * 4, traced)


eleza test_mmap():
    agiza mmap
    ukijumuisha TestHook() kama hook:
        mmap.mmap(-1, 8)
        assertEqual(hook.seen[0][1][:2], (-1, 8))


ikiwa __name__ == "__main__":
    kutoka test.libregrtest.setup agiza suppress_msvcrt_asserts
    suppress_msvcrt_asserts(Uongo)

    test = sys.argv[1]
    globals()[test]()
