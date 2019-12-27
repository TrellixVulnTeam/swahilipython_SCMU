agiza sys
agiza unittest
agiza io
agiza atexit
agiza os
kutoka test agiza support
kutoka test.support agiza script_helper

### helpers
eleza h1():
    andika("h1")

eleza h2():
    andika("h2")

eleza h3():
    andika("h3")

eleza h4(*args, **kwargs):
    andika("h4", args, kwargs)

eleza raise1():
    raise TypeError

eleza raise2():
    raise SystemError

eleza exit():
    raise SystemExit


kundi GeneralTest(unittest.TestCase):

    eleza setUp(self):
        self.save_stdout = sys.stdout
        self.save_stderr = sys.stderr
        self.stream = io.StringIO()
        sys.stdout = sys.stderr = self.stream
        atexit._clear()

    eleza tearDown(self):
        sys.stdout = self.save_stdout
        sys.stderr = self.save_stderr
        atexit._clear()

    eleza test_args(self):
        # be sure args are handled properly
        atexit.register(h1)
        atexit.register(h4)
        atexit.register(h4, 4, kw="abc")
        atexit._run_exitfuncs()

        self.assertEqual(self.stream.getvalue(),
                            "h4 (4,) {'kw': 'abc'}\nh4 () {}\nh1\n")

    eleza test_badargs(self):
        atexit.register(lambda: 1, 0, 0, (x for x in (1,2)), 0, 0)
        self.assertRaises(TypeError, atexit._run_exitfuncs)

    eleza test_order(self):
        # be sure handlers are executed in reverse order
        atexit.register(h1)
        atexit.register(h2)
        atexit.register(h3)
        atexit._run_exitfuncs()

        self.assertEqual(self.stream.getvalue(), "h3\nh2\nh1\n")

    eleza test_raise(self):
        # be sure raises are handled properly
        atexit.register(raise1)
        atexit.register(raise2)

        self.assertRaises(TypeError, atexit._run_exitfuncs)

    eleza test_raise_unnormalized(self):
        # Issue #10756: Make sure that an unnormalized exception is
        # handled properly
        atexit.register(lambda: 1 / 0)

        self.assertRaises(ZeroDivisionError, atexit._run_exitfuncs)
        self.assertIn("ZeroDivisionError", self.stream.getvalue())

    eleza test_exit(self):
        # be sure a SystemExit is handled properly
        atexit.register(exit)

        self.assertRaises(SystemExit, atexit._run_exitfuncs)
        self.assertEqual(self.stream.getvalue(), '')

    eleza test_print_tracebacks(self):
        # Issue #18776: the tracebacks should be printed when errors occur.
        eleza f():
            1/0  # one
        eleza g():
            1/0  # two
        eleza h():
            1/0  # three
        atexit.register(f)
        atexit.register(g)
        atexit.register(h)

        self.assertRaises(ZeroDivisionError, atexit._run_exitfuncs)
        stderr = self.stream.getvalue()
        self.assertEqual(stderr.count("ZeroDivisionError"), 3)
        self.assertIn("# one", stderr)
        self.assertIn("# two", stderr)
        self.assertIn("# three", stderr)

    eleza test_stress(self):
        a = [0]
        eleza inc():
            a[0] += 1

        for i in range(128):
            atexit.register(inc)
        atexit._run_exitfuncs()

        self.assertEqual(a[0], 128)

    eleza test_clear(self):
        a = [0]
        eleza inc():
            a[0] += 1

        atexit.register(inc)
        atexit._clear()
        atexit._run_exitfuncs()

        self.assertEqual(a[0], 0)

    eleza test_unregister(self):
        a = [0]
        eleza inc():
            a[0] += 1
        eleza dec():
            a[0] -= 1

        for i in range(4):
            atexit.register(inc)
        atexit.register(dec)
        atexit.unregister(inc)
        atexit._run_exitfuncs()

        self.assertEqual(a[0], -1)

    eleza test_bound_methods(self):
        l = []
        atexit.register(l.append, 5)
        atexit._run_exitfuncs()
        self.assertEqual(l, [5])

        atexit.unregister(l.append)
        atexit._run_exitfuncs()
        self.assertEqual(l, [5])

    eleza test_shutdown(self):
        # Actually test the shutdown mechanism in a subprocess
        code = """ikiwa 1:
            agiza atexit

            eleza f(msg):
                andika(msg)

            atexit.register(f, "one")
            atexit.register(f, "two")
            """
        res = script_helper.assert_python_ok("-c", code)
        self.assertEqual(res.out.decode().splitlines(), ["two", "one"])
        self.assertFalse(res.err)


@support.cpython_only
kundi SubinterpreterTest(unittest.TestCase):

    eleza test_callbacks_leak(self):
        # This test shows a leak in refleak mode ikiwa atexit doesn't
        # take care to free callbacks in its per-subinterpreter module
        # state.
        n = atexit._ncallbacks()
        code = r"""ikiwa 1:
            agiza atexit
            eleza f():
                pass
            atexit.register(f)
            del atexit
            """
        ret = support.run_in_subinterp(code)
        self.assertEqual(ret, 0)
        self.assertEqual(atexit._ncallbacks(), n)

    eleza test_callbacks_leak_refcycle(self):
        # Similar to the above, but with a refcycle through the atexit
        # module.
        n = atexit._ncallbacks()
        code = r"""ikiwa 1:
            agiza atexit
            eleza f():
                pass
            atexit.register(f)
            atexit.__atexit = atexit
            """
        ret = support.run_in_subinterp(code)
        self.assertEqual(ret, 0)
        self.assertEqual(atexit._ncallbacks(), n)

    eleza test_callback_on_subinterpreter_teardown(self):
        # This tests ikiwa a callback is called on
        # subinterpreter teardown.
        expected = b"The test has passed!"
        r, w = os.pipe()

        code = r"""ikiwa 1:
            agiza os
            agiza atexit
            eleza callback():
                os.write({:d}, b"The test has passed!")
            atexit.register(callback)
        """.format(w)
        ret = support.run_in_subinterp(code)
        os.close(w)
        self.assertEqual(os.read(r, len(expected)), expected)
        os.close(r)


ikiwa __name__ == "__main__":
    unittest.main()
