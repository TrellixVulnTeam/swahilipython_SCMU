"""
   Test cases kila codeop.py
   Nick Mathewson
"""
agiza unittest
kutoka test.support agiza is_jython

kutoka codeop agiza compile_command, PyCF_DONT_IMPLY_DEDENT
agiza io

ikiwa is_jython:
    agiza sys

    eleza unify_callables(d):
        kila n,v kwenye d.items():
            ikiwa hasattr(v, '__call__'):
                d[n] = Kweli
        rudisha d

kundi CodeopTests(unittest.TestCase):

    eleza assertValid(self, str, symbol='single'):
        '''succeed iff str ni a valid piece of code'''
        ikiwa is_jython:
            code = compile_command(str, "<input>", symbol)
            self.assertKweli(code)
            ikiwa symbol == "single":
                d,r = {},{}
                saved_stdout = sys.stdout
                sys.stdout = io.StringIO()
                jaribu:
                    exec(code, d)
                    exec(compile(str,"<input>","single"), r)
                mwishowe:
                    sys.stdout = saved_stdout
            lasivyo symbol == 'eval':
                ctx = {'a': 2}
                d = { 'value': eval(code,ctx) }
                r = { 'value': eval(str,ctx) }
            self.assertEqual(unify_callables(r),unify_callables(d))
        isipokua:
            expected = compile(str, "<input>", symbol, PyCF_DONT_IMPLY_DEDENT)
            self.assertEqual(compile_command(str, "<input>", symbol), expected)

    eleza assertIncomplete(self, str, symbol='single'):
        '''succeed iff str ni the start of a valid piece of code'''
        self.assertEqual(compile_command(str, symbol=symbol), Tupu)

    eleza assertInvalid(self, str, symbol='single', is_syntax=1):
        '''succeed iff str ni the start of an invalid piece of code'''
        jaribu:
            compile_command(str,symbol=symbol)
            self.fail("No exception ashiriad kila invalid code")
        tatizo SyntaxError:
            self.assertKweli(is_syntax)
        tatizo OverflowError:
            self.assertKweli(not is_syntax)

    eleza test_valid(self):
        av = self.assertValid

        # special case
        ikiwa sio is_jython:
            self.assertEqual(compile_command(""),
                             compile("pita", "<input>", 'single',
                                     PyCF_DONT_IMPLY_DEDENT))
            self.assertEqual(compile_command("\n"),
                             compile("pita", "<input>", 'single',
                                     PyCF_DONT_IMPLY_DEDENT))
        isipokua:
            av("")
            av("\n")

        av("a = 1")
        av("\na = 1")
        av("a = 1\n")
        av("a = 1\n\n")
        av("\n\na = 1\n\n")

        av("eleza x():\n  pita\n")
        av("ikiwa 1:\n pita\n")

        av("\n\nikiwa 1: pita\n")
        av("\n\nikiwa 1: pita\n\n")

        av("eleza x():\n\n pita\n")
        av("eleza x():\n  pita\n  \n")
        av("eleza x():\n  pita\n \n")

        av("pita\n")
        av("3**3\n")

        av("ikiwa 9==3:\n   pita\nisipokua:\n   pita\n")
        av("ikiwa 1:\n pita\n ikiwa 1:\n  pita\n isipokua:\n  pita\n")

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

        av("ikiwa 1:\n pita\n ikiwa 1:\n  pita\n isipokua:\n  pita\n")
        av("#a\n\n   \na=3\n\n")

        av("\n\na**3","eval")
        av("\n \na**3","eval")
        av("#a\n#b\na**3","eval")

        av("eleza f():\n jaribu: pita\n mwishowe: [x kila x kwenye (1,2)]\n")
        av("eleza f():\n pita\n#foo\n")
        av("@a.b.c\neleza f():\n pita\n")

    eleza test_incomplete(self):
        ai = self.assertIncomplete

        ai("(a **")
        ai("(a,b,")
        ai("(a,b,(")
        ai("(a,b,(")
        ai("a = (")
        ai("a = {")
        ai("b + {")

        ai("ikiwa 9==3:\n   pita\nisipokua:")
        ai("ikiwa 9==3:\n   pita\nisipokua:\n")
        ai("ikiwa 9==3:\n   pita\nisipokua:\n   pita")
        ai("ikiwa 1:")
        ai("ikiwa 1:\n")
        ai("ikiwa 1:\n pita\n ikiwa 1:\n  pita\n isipokua:")
        ai("ikiwa 1:\n pita\n ikiwa 1:\n  pita\n isipokua:\n")
        ai("ikiwa 1:\n pita\n ikiwa 1:\n  pita\n isipokua:\n  pita")

        ai("eleza x():")
        ai("eleza x():\n")
        ai("eleza x():\n\n")

        ai("eleza x():\n  pita")
        ai("eleza x():\n  pita\n ")
        ai("eleza x():\n  pita\n  ")
        ai("\n\neleza x():\n  pita")

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

        ai("ikiwa Kweli:\n ikiwa Kweli:\n  ikiwa Kweli:   \n")

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

        ai("ikiwa a:\n pita\nlasivyo b:")
        ai("ikiwa a:\n pita\nlasivyo b:\n pita\nisipokua:")

        ai("wakati a:")
        ai("wakati a:\n pita\nisipokua:")

        ai("kila a kwenye b:")
        ai("kila a kwenye b:\n pita\nisipokua:")

        ai("jaribu:")
        ai("jaribu:\n pita\nexcept:")
        ai("jaribu:\n pita\nmwishowe:")
        ai("jaribu:\n pita\nexcept:\n pita\nmwishowe:")

        ai("ukijumuisha a:")
        ai("ukijumuisha a kama b:")

        ai("kundi a:")
        ai("kundi a(")
        ai("kundi a(b")
        ai("kundi a(b,")
        ai("kundi a():")

        ai("[x for")
        ai("[x kila x in")
        ai("[x kila x kwenye (")

        ai("(x for")
        ai("(x kila x in")
        ai("(x kila x kwenye (")

    eleza test_invalid(self):
        ai = self.assertInvalid
        ai("a b")

        ai("a @")
        ai("a b @")
        ai("a ** @")

        ai("a = ")
        ai("a = 9 +")

        ai("eleza x():\n\npita\n")

        ai("\n\n ikiwa 1: pita\n\npita")

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
        ai("ikiwa (a == 1 na b = 2): pita")

        ai("toa 1")
        ai("toa (1,)")
        ai("toa [1]")
        ai("toa '1'")

        ai("[i kila i kwenye range(10)] = (1, 2, 3)")

    eleza test_filename(self):
        self.assertEqual(compile_command("a = 1\n", "abc").co_filename,
                         compile("a = 1\n", "abc", 'single').co_filename)
        self.assertNotEqual(compile_command("a = 1\n", "abc").co_filename,
                            compile("a = 1\n", "def", 'single').co_filename)


ikiwa __name__ == "__main__":
    unittest.main()
