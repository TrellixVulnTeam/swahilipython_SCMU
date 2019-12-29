"""Verify that warnings are issued kila global statements following use."""

kutoka test.support agiza run_unittest, check_syntax_error, check_warnings
agiza unittest
agiza warnings


kundi GlobalTests(unittest.TestCase):

    eleza setUp(self):
        self._warnings_manager = check_warnings()
        self._warnings_manager.__enter__()
        warnings.filterwarnings("error", module="<test string>")

    eleza tearDown(self):
        self._warnings_manager.__exit__(Tupu, Tupu, Tupu)


    eleza test1(self):
        prog_text_1 = """\
eleza wrong1():
    a = 1
    b = 2
    global a
    global b
"""
        check_syntax_error(self, prog_text_1, lineno=4, offset=5)

    eleza test2(self):
        prog_text_2 = """\
eleza wrong2():
    andika(x)
    global x
"""
        check_syntax_error(self, prog_text_2, lineno=3, offset=5)

    eleza test3(self):
        prog_text_3 = """\
eleza wrong3():
    andika(x)
    x = 2
    global x
"""
        check_syntax_error(self, prog_text_3, lineno=4, offset=5)

    eleza test4(self):
        prog_text_4 = """\
global x
x = 2
"""
        # this should work
        compile(prog_text_4, "<test string>", "exec")


eleza test_main():
    with warnings.catch_warnings():
        warnings.filterwarnings("error", module="<test string>")
        run_unittest(GlobalTests)

ikiwa __name__ == "__main__":
    test_main()
