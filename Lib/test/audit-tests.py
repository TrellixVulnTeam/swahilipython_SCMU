"""This script contains the actual auditing tests.

It should not be imported directly, but should be run by the test_audit
module with arguments identifying each test.

"""

agiza contextlib
agiza sys


kundi TestHook:
    """Used in standard hook tests to collect any logged events.

    Should be used in a with block to ensure that it has no impact
    after the test completes.
    """

    eleza __init__(self, raise_on_events=None, exc_type=RuntimeError):
        self.raise_on_events = raise_on_events or ()
        self.exc_type = exc_type
        self.seen = []
        self.closed = False

    eleza __enter__(self, *a):
        sys.addaudithook(self)
        rudisha self

    eleza __exit__(self, *a):
        self.close()

    eleza close(self):
        self.closed = True

    @property
    eleza seen_events(self):
        rudisha [i[0] for i in self.seen]

    eleza __call__(self, event, args):
        ikiwa self.closed:
            return
        self.seen.append((event, args))
        ikiwa event in self.raise_on_events:
            raise self.exc_type("saw event " + event)


kundi TestFinalizeHook:
    """Used in the test_finalize_hooks function to ensure that hooks
    are correctly cleaned up, that they are notified about the cleanup,
    and are unable to prevent it.
    """

    eleza __init__(self):
        andika("Created", id(self), file=sys.stdout, flush=True)

    eleza __call__(self, event, args):
        # Avoid recursion when we call id() below
        ikiwa event == "builtins.id":
            return

        andika(event, id(self), file=sys.stdout, flush=True)

        ikiwa event == "cpython._PySys_ClearAuditHooks":
            raise RuntimeError("Should be ignored")
        elikiwa event == "cpython.PyInterpreterState_Clear":
            raise RuntimeError("Should be ignored")


# Simple helpers, since we are not in unittest here
eleza assertEqual(x, y):
    ikiwa x != y:
        raise AssertionError(f"{x!r} should equal {y!r}")


eleza assertIn(el, series):
    ikiwa el not in series:
        raise AssertionError(f"{el!r} should be in {series!r}")


eleza assertNotIn(el, series):
    ikiwa el in series:
        raise AssertionError(f"{el!r} should not be in {series!r}")


eleza assertSequenceEqual(x, y):
    ikiwa len(x) != len(y):
        raise AssertionError(f"{x!r} should equal {y!r}")
    ikiwa any(ix != iy for ix, iy in zip(x, y)):
        raise AssertionError(f"{x!r} should equal {y!r}")


@contextlib.contextmanager
eleza assertRaises(ex_type):
    try:
        yield
        assert False, f"expected {ex_type}"
    except BaseException as ex:
        ikiwa isinstance(ex, AssertionError):
            raise
        assert type(ex) is ex_type, f"{ex} should be {ex_type}"


eleza test_basic():
    with TestHook() as hook:
        sys.audit("test_event", 1, 2, 3)
        assertEqual(hook.seen[0][0], "test_event")
        assertEqual(hook.seen[0][1], (1, 2, 3))


eleza test_block_add_hook():
    # Raising an exception should prevent a new hook kutoka being added,
    # but will not propagate out.
    with TestHook(raise_on_events="sys.addaudithook") as hook1:
        with TestHook() as hook2:
            sys.audit("test_event")
            assertIn("test_event", hook1.seen_events)
            assertNotIn("test_event", hook2.seen_events)


eleza test_block_add_hook_baseexception():
    # Raising BaseException will propagate out when adding a hook
    with assertRaises(BaseException):
        with TestHook(
            raise_on_events="sys.addaudithook", exc_type=BaseException
        ) as hook1:
            # Adding this next hook should raise BaseException
            with TestHook() as hook2:
                pass


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

    with TestHook(raise_on_events="pickle.find_class") as hook:
        with assertRaises(RuntimeError):
            # With the hook enabled, loading globals is not allowed
            pickle.loads(payload_1)
        # pickles with no globals are okay
        pickle.loads(payload_2)


eleza test_monkeypatch():
    kundi A:
        pass

    kundi B:
        pass

    kundi C(A):
        pass

    a = A()

    with TestHook() as hook:
        # Catch name changes
        C.__name__ = "X"
        # Catch type changes
        C.__bases__ = (B,)
        # Ensure bypassing __setattr__ is still caught
        type.__dict__["__bases__"].__set__(C, (B,))
        # Catch attribute replacement
        C.__init__ = B.__init__
        # Catch attribute addition
        C.new_attr = 123
        # Catch kundi changes
        a.__class__ = B

    actual = [(a[0], a[1]) for e, a in hook.seen ikiwa e == "object.__setattr__"]
    assertSequenceEqual(
        [(C, "__name__"), (C, "__bases__"), (C, "__bases__"), (a, "__class__")], actual
    )


eleza test_open():
    # SSLContext.load_dh_params uses _Py_fopen_obj rather than normal open()
    try:
        agiza ssl

        load_dh_params = ssl.create_default_context().load_dh_params
    except ImportError:
        load_dh_params = None

    # Try a range of "open" functions.
    # All of them should fail
    with TestHook(raise_on_events={"open"}) as hook:
        for fn, *args in [
            (open, sys.argv[2], "r"),
            (open, sys.executable, "rb"),
            (open, 3, "wb"),
            (open, sys.argv[2], "w", -1, None, None, None, False, lambda *a: 1),
            (load_dh_params, sys.argv[2]),
        ]:
            ikiwa not fn:
                continue
            with assertRaises(RuntimeError):
                fn(*args)

    actual_mode = [(a[0], a[1]) for e, a in hook.seen ikiwa e == "open" and a[1]]
    actual_flag = [(a[0], a[2]) for e, a in hook.seen ikiwa e == "open" and not a[1]]
    assertSequenceEqual(
        [
            i
            for i in [
                (sys.argv[2], "r"),
                (sys.executable, "r"),
                (3, "w"),
                (sys.argv[2], "w"),
                (sys.argv[2], "rb") ikiwa load_dh_params else None,
            ]
            ikiwa i is not None
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
    try:
        with TestHook() as hook:
            # No traced call
            eval("1")

            # No traced call
            hook.__cantrace__ = False
            eval("2")

            # One traced call
            hook.__cantrace__ = True
            eval("3")

            # Two traced calls (writing to private member, eval)
            hook.__cantrace__ = 1
            eval("4")

            # One traced call (writing to private member)
            hook.__cantrace__ = 0
    finally:
        sys.settrace(old)

    assertSequenceEqual(["call"] * 4, traced)


eleza test_mmap():
    agiza mmap
    with TestHook() as hook:
        mmap.mmap(-1, 8)
        assertEqual(hook.seen[0][1][:2], (-1, 8))


ikiwa __name__ == "__main__":
    kutoka test.libregrtest.setup agiza suppress_msvcrt_asserts
    suppress_msvcrt_asserts(False)

    test = sys.argv[1]
    globals()[test]()
