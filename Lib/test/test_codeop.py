"""
   Test cases for codeop.py
   Nick Mathewson
"""
agiza unittest
kutoka test.support agiza is_jython

kutoka codeop agiza compile_command, PyCF_DONT_IMPLY_DEDENT
agiza io

ikiwa is_jython:
    agiza sys

    eleza unify_callables(d):
        for n,v in d.items():
            ikiwa hasattr(v, '__call__'):
                d[n] = True
        rudisha d

kundi CodeopTests(unittest.TestCase):

    eleza assertValid(self, str, symbol='single'):
        '''succeed iff str is a valid piece of code'''
        ikiwa is_jython:
            code = compile_command(str, "<input>", symbol)
            self.assertTrue(code)
            ikiwa symbol == "single":
                d,r = {},{}
                saved_stdout = sys.stdout
                sys.stdout = io.StringIO()
                try:
                    exec(code, d)
                    exec(compile(str,"<input>","single"), r)
                finally:
                    sys.stdout = saved_stdout
            elikiwa symbol == 'eval':
                ctx = {'a': 2}
                d = { 'value': eval(code,ctx) }
                r = { 'value': eval(str,ctx) }
            self.assertEqual(unify_callables(r),unify_callables(d))
        else:
            expected = compile(str, "<input>", symbol, PyCF_DONT_IMPLY_DEDENT)
            self.assertEqual(compile_command(str, "<input>", symbol), expected)

    eleza assertIncomplete(self, str, symbol='single'):
        '''succeed iff str is the start of a valid piece of code'''
        self.assertEqual(compile_command(str, symbol=symbol), None)

    eleza assertInvalid(self, str, symbol='single', is_syntax=1):
        '''succeed iff str is the start of an invalid piece of code'''
        try:
            compile_command(str,symbol=symbol)
            self.fail("No exception raised for invalid code")
        except SyntaxError:
            self.assertTrue(is_syntax)
        except OverflowError:
            self.assertTrue(not is_syntax)

    eleza test_valid(self):
        av = self.assertValid

        # special case
        ikiwa not is_jython:
            self.assertEqual(compile_command(""),
                             compile("pass", "<input>", 'single',
                                     PyCF_DONT_IMPLY_DEDENT))
            self.assertEqual(compile_command("\n"),
                             compile("pass", "<input>", 'single',
                                     PyCF_DONT_IMPLY_DEDENT))
        else:
            av("")
            av("\n")

        av("a = 1")
        av("\na = 1")
        av("a = 1\n")
        av("a = 1\n\n")
        av("\n\na = 1\n\n")

        av("eleza x():\n  pass\n")
        av("ikiwa 1:\n pass\n")

        av("\n\nikiwa 1: pass\n")
        av("\n\nikiwa 1: pass\n\n")

        av("eleza x():\n\n pass\n")
        av("eleza x():\n  pass\n  \n")
        av("eleza x():\n  pass\n \n")

        av("pass\n")
        av("3**3\n")

        av("ikiwa 9==3:\n   pass\nelse:\n   pass\n")
        av("ikiwa 1:\n pass\n ikiwa 1:\n  pass\n else:\n  pass\n")

        av("#a\n#b\na = 3\n")
        av("#a\n\n   \na=3\n")
        av("a=3\n\n")
        av("a = 9+ \\\n3")

        av("3**3","eval")
        av("(lambda z: \n z**3)","eval")

        av("9+ \\\n3","eval")
        av("9+ \\\n3\n","eval")

        av("\n\na**3","eval")
        av("\n \na**3","eval")
        av("#a\n#b\na**3","eval")

        av("\n\na = 1\n\n")
        av("\n\nikiwa 1: a=1\n\n")

        av("ikiwa 1:\n pass\n ikiwa 1:\n  pass\n else:\n  pass\n")
        av("#a\n\n   \na=3\n\n")

        av("\n\na**3","eval")
        av("\n \na**3","eval")
        av("#a\n#b\na**3","eval")

        av("eleza f():\n try: pass\n finally: [x for x in (1,2)]\n")
        av("eleza f():\n pass\n#foo\n")
        av("@a.b.c\neleza f():\n pass\n")

    eleza test_incomplete(self):
        ai = self.assertIncomplete

        ai("(a **")
        ai("(a,b,")
        ai("(a,b,(")
        ai("(a,b,(")
        ai("a = (")
        ai("a = {")
        ai("b + {")

        ai("ikiwa 9==3:\n   pass\nelse:")
        ai("ikiwa 9==3:\n   pass\nelse:\n")
        ai("ikiwa 9==3:\n   pass\nelse:\n   pass")
        ai("ikiwa 1:")
        ai("ikiwa 1:\n")
        ai("ikiwa 1:\n pass\n ikiwa 1:\n  pass\n else:")
        ai("ikiwa 1:\n pass\n ikiwa 1:\n  pass\n else:\n")
        ai("ikiwa 1:\n pass\n ikiwa 1:\n  pass\n else:\n  pass")

        ai("eleza x():")
        ai("eleza x():\n")
        ai("eleza x():\n\n")

        ai("eleza x():\n  pass")
        ai("eleza x():\n  pass\n ")
        ai("eleza x():\n  pass\n  ")
        ai("\n\neleza x():\n  pass")

        ai("a = 9+ \\")
        ai("a = 'a\\")
        ai("a = '''xy")

        ai("","eval")
        ai("\n","eval")
        ai("(","eval")
        ai("(\n\n\n","eval")
        ai("(9+","eval")
        ai("9+ \\","eval")
        ai("lambda z: \\","eval")

        ai("ikiwa True:\n ikiwa True:\n  ikiwa True:   \n")

        ai("@a(")
        ai("@a(b")
        ai("@a(b,")
        ai("@a(b,c")
        ai("@a(b,c,")

        ai("kutoka a agiza (")
        ai("kutoka a agiza (b")
        ai("kutoka a agiza (b,")
        ai("kutoka a agiza (b,c")
        ai("kutoka a agiza (b,c,")

        ai("[");
        ai("[a");
        ai("[a,");
        ai("[a,b");
        ai("[a,b,");

        ai("{");
        ai("{a");
        ai("{a:");
        ai("{a:b");
        ai("{a:b,");
        ai("{a:b,c");
        ai("{a:b,c:");
        ai("{a:b,c:d");
        ai("{a:b,c:d,");

        ai("a(")
        ai("a(b")
        ai("a(b,")
        ai("a(b,c")
        ai("a(b,c,")

        ai("a[")
        ai("a[b")
        ai("a[b,")
        ai("a[b:")
        ai("a[b:c")
        ai("a[b:c:")
        ai("a[b:c:d")

        ai("eleza a(")
        ai("eleza a(b")
        ai("eleza a(b,")
        ai("eleza a(b,c")
        ai("eleza a(b,c,")

        ai("(")
        ai("(a")
        ai("(a,")
        ai("(a,b")
        ai("(a,b,")

        ai("ikiwa a:\n pass\nelikiwa b:")
        ai("ikiwa a:\n pass\nelikiwa b:\n pass\nelse:")

        ai("while a:")
        ai("while a:\n pass\nelse:")

        ai("for a in b:")
        ai("for a in b:\n pass\nelse:")

        ai("try:")
        ai("try:\n pass\nexcept:")
        ai("try:\n pass\nfinally:")
        ai("try:\n pass\nexcept:\n pass\nfinally:")

        ai("with a:")
        ai("with a as b:")

        ai("kundi a:")
        ai("kundi a(")
        ai("kundi a(b")
        ai("kundi a(b,")
        ai("kundi a():")

        ai("[x for")
        ai("[x for x in")
        ai("[x for x in (")

        ai("(x for")
        ai("(x for x in")
        ai("(x for x in (")

    eleza test_invalid(self):
        ai = self.assertInvalid
        ai("a b")

        ai("a @")
        ai("a b @")
        ai("a ** @")

        ai("a = ")
        ai("a = 9 +")

        ai("eleza x():\n\npass\n")

        ai("\n\n ikiwa 1: pass\n\npass")

        ai("a = 9+ \\\n")
        ai("a = 'a\\ ")
        ai("a = 'a\\\n")

        ai("a = 1","eval")
        ai("a = (","eval")
        ai("]","eval")
        ai("())","eval")
        ai("[}","eval")
        ai("9+","eval")
        ai("lambda z:","eval")
        ai("a b","eval")

        ai("rudisha 2.3")
        ai("ikiwa (a == 1 and b = 2): pass")

        ai("del 1")
        ai("del (1,)")
        ai("del [1]")
        ai("del '1'")

        ai("[i for i in range(10)] = (1, 2, 3)")

    eleza test_filename(self):
        self.assertEqual(compile_command("a = 1\n", "abc").co_filename,
                         compile("a = 1\n", "abc", 'single').co_filename)
        self.assertNotEqual(compile_command("a = 1\n", "abc").co_filename,
                            compile("a = 1\n", "def", 'single').co_filename)


ikiwa __name__ == "__main__":
    unittest.main()
