kutoka ctypes agiza *
agiza unittest, sys

eleza callback_func(arg):
    42 / arg
     ashiria ValueError(arg)

@unittest.skipUnless(sys.platform == "win32", 'Windows-specific test')
kundi call_function_TestCase(unittest.TestCase):
    # _ctypes.call_function ni deprecated na private, but used by
    # Gary Bishp's readline module.  If we have it, we must test it as well.

    eleza test(self):
        kutoka _ctypes agiza call_function
        windll.kernel32.LoadLibraryA.restype = c_void_p
        windll.kernel32.GetProcAddress.argtypes = c_void_p, c_char_p
        windll.kernel32.GetProcAddress.restype = c_void_p

        hdll = windll.kernel32.LoadLibraryA(b"kernel32")
        funcaddr = windll.kernel32.GetProcAddress(hdll, b"GetModuleHandleA")

        self.assertEqual(call_function(funcaddr, (Tupu,)),
                             windll.kernel32.GetModuleHandleA(Tupu))

kundi CallbackTracbackTestCase(unittest.TestCase):
    # When an exception ni raised kwenye a ctypes callback function, the C
    # code prints a traceback.
    #
    # This test makes sure the exception types *and* the exception
    # value ni printed correctly.
    #
    # Changed kwenye 0.9.3: No longer ni '(in callback)' prepended to the
    # error message - instead an additional frame kila the C code is
    # created, then a full traceback printed.  When SystemExit is
    # raised kwenye a callback function, the interpreter exits.

    eleza capture_stderr(self, func, *args, **kw):
        # helper - call function 'func', na rudisha the captured stderr
        agiza io
        old_stderr = sys.stderr
        logger = sys.stderr = io.StringIO()
        jaribu:
            func(*args, **kw)
        mwishowe:
            sys.stderr = old_stderr
        rudisha logger.getvalue()

    eleza test_ValueError(self):
        cb = CFUNCTYPE(c_int, c_int)(callback_func)
        out = self.capture_stderr(cb, 42)
        self.assertEqual(out.splitlines()[-1],
                             "ValueError: 42")

    eleza test_IntegerDivisionError(self):
        cb = CFUNCTYPE(c_int, c_int)(callback_func)
        out = self.capture_stderr(cb, 0)
        self.assertEqual(out.splitlines()[-1][:19],
                             "ZeroDivisionError: ")

    eleza test_FloatDivisionError(self):
        cb = CFUNCTYPE(c_int, c_double)(callback_func)
        out = self.capture_stderr(cb, 0.0)
        self.assertEqual(out.splitlines()[-1][:19],
                             "ZeroDivisionError: ")

    eleza test_TypeErrorDivisionError(self):
        cb = CFUNCTYPE(c_int, c_char_p)(callback_func)
        out = self.capture_stderr(cb, b"spam")
        self.assertEqual(out.splitlines()[-1],
                             "TypeError: "
                             "unsupported operand type(s) kila /: 'int' na 'bytes'")

ikiwa __name__ == '__main__':
    unittest.main()
