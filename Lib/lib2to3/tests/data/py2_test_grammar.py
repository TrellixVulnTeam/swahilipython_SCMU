# Python test set -- part 1, grammar.
# This just tests whether the parser accepts them all.

# NOTE: When you run this test as a script kutoka the command line, you
# get warnings about certain hex/oct constants.  Since those are
# issued by the parser, you can't suppress them by adding a
# filterwarnings() call to this module.  Therefore, to shut up the
# regression test, the filterwarnings() call has been added to
# regrtest.py.

kutoka test.test_support agiza run_unittest, check_syntax_error
agiza unittest
agiza sys
# testing agiza *
kutoka sys agiza *

kundi TokenTests(unittest.TestCase):

    eleza testBackslash(self):
        # Backslash means line continuation:
        x = 1 \
        + 1
        self.assertEquals(x, 2, 'backslash kila line continuation')

        # Backslash does sio means continuation kwenye comments :\
        x = 0
        self.assertEquals(x, 0, 'backslash ending comment')

    eleza testPlainIntegers(self):
        self.assertEquals(0xff, 255)
        self.assertEquals(0377, 255)
        self.assertEquals(2147483647, 017777777777)
        # "0x" ni sio a valid literal
        self.assertRaises(SyntaxError, eval, "0x")
        kutoka sys agiza maxint
        ikiwa maxint == 2147483647:
            self.assertEquals(-2147483647-1, -020000000000)
            # XXX -2147483648
            self.assert_(037777777777 > 0)
            self.assert_(0xffffffff > 0)
            kila s kwenye '2147483648', '040000000000', '0x100000000':
                jaribu:
                    x = eval(s)
                except OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        elikiwa maxint == 9223372036854775807:
            self.assertEquals(-9223372036854775807-1, -01000000000000000000000)
            self.assert_(01777777777777777777777 > 0)
            self.assert_(0xffffffffffffffff > 0)
            kila s kwenye '9223372036854775808', '02000000000000000000000', \
                     '0x10000000000000000':
                jaribu:
                    x = eval(s)
                except OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        isipokua:
            self.fail('Weird maxint value %r' % maxint)

    eleza testLongIntegers(self):
        x = 0L
        x = 0l
        x = 0xffffffffffffffffL
        x = 0xffffffffffffffffl
        x = 077777777777777777L
        x = 077777777777777777l
        x = 123456789012345678901234567890L
        x = 123456789012345678901234567890l

    eleza testFloats(self):
        x = 3.14
        x = 314.
        x = 0.314
        # XXX x = 000.314
        x = .314
        x = 3e14
        x = 3E14
        x = 3e-14
        x = 3e+14
        x = 3.e14
        x = .3e14
        x = 3.1e4

    eleza testStringLiterals(self):
        x = ''; y = ""; self.assert_(len(x) == 0 na x == y)
        x = '\''; y = "'"; self.assert_(len(x) == 1 na x == y na ord(x) == 39)
        x = '"'; y = "\""; self.assert_(len(x) == 1 na x == y na ord(x) == 34)
        x = "doesn't \"shrink\" does it"
        y = 'doesn\'t "shrink" does it'
        self.assert_(len(x) == 24 na x == y)
        x = "does \"shrink\" doesn't it"
        y = 'does "shrink" doesn\'t it'
        self.assert_(len(x) == 24 na x == y)
        x = """
The "quick"
brown fox
jumps over
the 'lazy' dog.
"""
        y = '\nThe "quick"\nbrown fox\njumps over\nthe \'lazy\' dog.\n'
        self.assertEquals(x, y)
        y = '''
The "quick"
brown fox
jumps over
the 'lazy' dog.
'''
        self.assertEquals(x, y)
        y = "\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the 'lazy' dog.\n\
"
        self.assertEquals(x, y)
        y = '\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the \'lazy\' dog.\n\
'
        self.assertEquals(x, y)


kundi GrammarTests(unittest.TestCase):

    # single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
    # XXX can't test kwenye a script -- this rule ni only used when interactive

    # file_input: (NEWLINE | stmt)* ENDMARKER
    # Being tested as this very moment this very module

    # expr_input: testlist NEWLINE
    # XXX Hard to test -- used only kwenye calls to uliza()

    eleza testEvalInput(self):
        # testlist ENDMARKER
        x = eval('1, 0 ama 1')

    eleza testFuncdef(self):
        ### 'def' NAME parameters ':' suite
        ### parameters: '(' [varargslist] ')'
        ### varargslist: (fpeleza ['=' test] ',')* ('*' NAME [',' ('**'|'*' '*') NAME]
        ###            | ('**'|'*' '*') NAME)
        ###            | fpeleza ['=' test] (',' fpeleza ['=' test])* [',']
        ### fpdef: NAME | '(' fplist ')'
        ### fplist: fpeleza (',' fpdef)* [',']
        ### arglist: (argument ',')* (argument | *' test [',' '**' test] | '**' test)
        ### argument: [test '='] test   # Really [keyword '='] test
        eleza f1(): pass
        f1()
        f1(*())
        f1(*(), **{})
        eleza f2(one_argument): pass
        eleza f3(two, arguments): pass
        eleza f4(two, (compound, (argument, list))): pass
        eleza f5((compound, first), two): pass
        self.assertEquals(f2.func_code.co_varnames, ('one_argument',))
        self.assertEquals(f3.func_code.co_varnames, ('two', 'arguments'))
        ikiwa sys.platform.startswith('java'):
            self.assertEquals(f4.func_code.co_varnames,
                   ('two', '(compound, (argument, list))', 'compound', 'argument',
                                'list',))
            self.assertEquals(f5.func_code.co_varnames,
                   ('(compound, first)', 'two', 'compound', 'first'))
        isipokua:
            self.assertEquals(f4.func_code.co_varnames,
                  ('two', '.1', 'compound', 'argument',  'list'))
            self.assertEquals(f5.func_code.co_varnames,
                  ('.0', 'two', 'compound', 'first'))
        eleza a1(one_arg,): pass
        eleza a2(two, args,): pass
        eleza v0(*rest): pass
        eleza v1(a, *rest): pass
        eleza v2(a, b, *rest): pass
        eleza v3(a, (b, c), *rest): rudisha a, b, c, rest

        f1()
        f2(1)
        f2(1,)
        f3(1, 2)
        f3(1, 2,)
        f4(1, (2, (3, 4)))
        v0()
        v0(1)
        v0(1,)
        v0(1,2)
        v0(1,2,3,4,5,6,7,8,9,0)
        v1(1)
        v1(1,)
        v1(1,2)
        v1(1,2,3)
        v1(1,2,3,4,5,6,7,8,9,0)
        v2(1,2)
        v2(1,2,3)
        v2(1,2,3,4)
        v2(1,2,3,4,5,6,7,8,9,0)
        v3(1,(2,3))
        v3(1,(2,3),4)
        v3(1,(2,3),4,5,6,7,8,9,0)

        # ceval unpacks the formal arguments into the first argcount names;
        # thus, the names nested inside tuples must appear after these names.
        ikiwa sys.platform.startswith('java'):
            self.assertEquals(v3.func_code.co_varnames, ('a', '(b, c)', 'rest', 'b', 'c'))
        isipokua:
            self.assertEquals(v3.func_code.co_varnames, ('a', '.1', 'rest', 'b', 'c'))
        self.assertEquals(v3(1, (2, 3), 4), (1, 2, 3, (4,)))
        eleza d01(a=1): pass
        d01()
        d01(1)
        d01(*(1,))
        d01(**{'a':2})
        eleza d11(a, b=1): pass
        d11(1)
        d11(1, 2)
        d11(1, **{'b':2})
        eleza d21(a, b, c=1): pass
        d21(1, 2)
        d21(1, 2, 3)
        d21(*(1, 2, 3))
        d21(1, *(2, 3))
        d21(1, 2, *(3,))
        d21(1, 2, **{'c':3})
        eleza d02(a=1, b=2): pass
        d02()
        d02(1)
        d02(1, 2)
        d02(*(1, 2))
        d02(1, *(2,))
        d02(1, **{'b':2})
        d02(**{'a': 1, 'b': 2})
        eleza d12(a, b=1, c=2): pass
        d12(1)
        d12(1, 2)
        d12(1, 2, 3)
        eleza d22(a, b, c=1, d=2): pass
        d22(1, 2)
        d22(1, 2, 3)
        d22(1, 2, 3, 4)
        eleza d01v(a=1, *rest): pass
        d01v()
        d01v(1)
        d01v(1, 2)
        d01v(*(1, 2, 3, 4))
        d01v(*(1,))
        d01v(**{'a':2})
        eleza d11v(a, b=1, *rest): pass
        d11v(1)
        d11v(1, 2)
        d11v(1, 2, 3)
        eleza d21v(a, b, c=1, *rest): pass
        d21v(1, 2)
        d21v(1, 2, 3)
        d21v(1, 2, 3, 4)
        d21v(*(1, 2, 3, 4))
        d21v(1, 2, **{'c': 3})
        eleza d02v(a=1, b=2, *rest): pass
        d02v()
        d02v(1)
        d02v(1, 2)
        d02v(1, 2, 3)
        d02v(1, *(2, 3, 4))
        d02v(**{'a': 1, 'b': 2})
        eleza d12v(a, b=1, c=2, *rest): pass
        d12v(1)
        d12v(1, 2)
        d12v(1, 2, 3)
        d12v(1, 2, 3, 4)
        d12v(*(1, 2, 3, 4))
        d12v(1, 2, *(3, 4, 5))
        d12v(1, *(2,), **{'c': 3})
        eleza d22v(a, b, c=1, d=2, *rest): pass
        d22v(1, 2)
        d22v(1, 2, 3)
        d22v(1, 2, 3, 4)
        d22v(1, 2, 3, 4, 5)
        d22v(*(1, 2, 3, 4))
        d22v(1, 2, *(3, 4, 5))
        d22v(1, *(2, 3), **{'d': 4})
        eleza d31v((x)): pass
        d31v(1)
        eleza d32v((x,)): pass
        d32v((1,))

        # keyword arguments after *arglist
        eleza f(*args, **kwargs):
            rudisha args, kwargs
        self.assertEquals(f(1, x=2, *[3, 4], y=5), ((1, 3, 4),
                                                    {'x':2, 'y':5}))
        self.assertRaises(SyntaxError, eval, "f(1, *(2,3), 4)")
        self.assertRaises(SyntaxError, eval, "f(1, x=2, *(3,4), x=5)")

        # Check ast errors kwenye *args na *kwargs
        check_syntax_error(self, "f(*g(1=2))")
        check_syntax_error(self, "f(**g(1=2))")

    eleza testLambdef(self):
        ### lambdef: 'lambda' [varargslist] ':' test
        l1 = lambda : 0
        self.assertEquals(l1(), 0)
        l2 = lambda : a[d] # XXX just testing the expression
        l3 = lambda : [2 < x kila x kwenye [-1, 3, 0L]]
        self.assertEquals(l3(), [0, 1, 0])
        l4 = lambda x = lambda y = lambda z=1 : z : y() : x()
        self.assertEquals(l4(), 1)
        l5 = lambda x, y, z=2: x + y + z
        self.assertEquals(l5(1, 2), 5)
        self.assertEquals(l5(1, 2, 3), 6)
        check_syntax_error(self, "lambda x: x = 2")
        check_syntax_error(self, "lambda (Tupu,): Tupu")

    ### stmt: simple_stmt | compound_stmt
    # Tested below

    eleza testSimpleStmt(self):
        ### simple_stmt: small_stmt (';' small_stmt)* [';']
        x = 1; pass; toa x
        eleza foo():
            # verify statements that end ukijumuisha semi-colons
            x = 1; pass; toa x;
        foo()

    ### small_stmt: expr_stmt | print_stmt  | pass_stmt | del_stmt | flow_stmt | import_stmt | global_stmt | access_stmt | exec_stmt
    # Tested below

    eleza testExprStmt(self):
        # (exprlist '=')* exprlist
        1
        1, 2, 3
        x = 1
        x = 1, 2, 3
        x = y = z = 1, 2, 3
        x, y, z = 1, 2, 3
        abc = a, b, c = x, y, z = xyz = 1, 2, (3, 4)

        check_syntax_error(self, "x + 1 = 1")
        check_syntax_error(self, "a + 1 = b + 2")

    eleza testPrintStmt(self):
        # 'print' (test ',')* [test]
        agiza StringIO

        # Can't test printing to real stdout without comparing output
        # which ni sio available kwenye unittest.
        save_stdout = sys.stdout
        sys.stdout = StringIO.StringIO()

        print 1, 2, 3
        print 1, 2, 3,
        print
        print 0 ama 1, 0 ama 1,
        print 0 ama 1

        # 'print' '>>' test ','
        print >> sys.stdout, 1, 2, 3
        print >> sys.stdout, 1, 2, 3,
        print >> sys.stdout
        print >> sys.stdout, 0 ama 1, 0 ama 1,
        print >> sys.stdout, 0 ama 1

        # test printing to an instance
        kundi Gulp:
            eleza write(self, msg): pass

        gulp = Gulp()
        print >> gulp, 1, 2, 3
        print >> gulp, 1, 2, 3,
        print >> gulp
        print >> gulp, 0 ama 1, 0 ama 1,
        print >> gulp, 0 ama 1

        # test print >> Tupu
        eleza driver():
            oldstdout = sys.stdout
            sys.stdout = Gulp()
            jaribu:
                tellme(Gulp())
                tellme()
            mwishowe:
                sys.stdout = oldstdout

        # we should see this once
        eleza tellme(file=sys.stdout):
            print >> file, 'hello world'

        driver()

        # we should sio see this at all
        eleza tellme(file=Tupu):
            print >> file, 'goodbye universe'

        driver()

        self.assertEqual(sys.stdout.getvalue(), '''\
1 2 3
1 2 3
1 1 1
1 2 3
1 2 3
1 1 1
hello world
''')
        sys.stdout = save_stdout

        # syntax errors
        check_syntax_error(self, 'print ,')
        check_syntax_error(self, 'print >> x,')

    eleza testDelStmt(self):
        # 'del' exprlist
        abc = [1,2,3]
        x, y, z = abc
        xyz = x, y, z

        toa abc
        toa x, y, (z, xyz)

    eleza testPassStmt(self):
        # 'pass'
        pass

    # flow_stmt: koma_stmt | endelea_stmt | return_stmt | raise_stmt
    # Tested below

    eleza testBreakStmt(self):
        # 'koma'
        wakati 1: koma

    eleza testContinueStmt(self):
        # 'endelea'
        i = 1
        wakati i: i = 0; endelea

        msg = ""
        wakati sio msg:
            msg = "ok"
            jaribu:
                endelea
                msg = "endelea failed to endelea inside try"
            tatizo:
                msg = "endelea inside try called except block"
        ikiwa msg != "ok":
            self.fail(msg)

        msg = ""
        wakati sio msg:
            msg = "finally block sio called"
            jaribu:
                endelea
            mwishowe:
                msg = "ok"
        ikiwa msg != "ok":
            self.fail(msg)

    eleza test_koma_endelea_loop(self):
        # This test warrants an explanation. It ni a test specifically kila SF bugs
        # #463359 na #462937. The bug ni that a 'koma' statement executed or
        # exception raised inside a try/except inside a loop, *after* a endelea
        # statement has been executed kwenye that loop, will cause the wrong number of
        # arguments to be popped off the stack na the instruction pointer reset to
        # a very small number (usually 0.) Because of this, the following test
        # *must* written as a function, na the tracking vars *must* be function
        # arguments ukijumuisha default values. Otherwise, the test will loop na loop.

        eleza test_inner(extra_burning_oil = 1, count=0):
            big_hippo = 2
            wakati big_hippo:
                count += 1
                jaribu:
                    ikiwa extra_burning_oil na big_hippo == 1:
                        extra_burning_oil -= 1
                        koma
                    big_hippo -= 1
                    endelea
                tatizo:
                    raise
            ikiwa count > 2 ama big_hippo <> 1:
                self.fail("endelea then koma kwenye try/except kwenye loop broken!")
        test_inner()

    eleza testReturn(self):
        # 'return' [testlist]
        eleza g1(): return
        eleza g2(): rudisha 1
        g1()
        x = g2()
        check_syntax_error(self, "kundi foo:rudisha 1")

    eleza testYield(self):
        check_syntax_error(self, "kundi foo:tuma 1")

    eleza testRaise(self):
        # 'raise' test [',' test]
        jaribu:  ashiria RuntimeError, 'just testing'
        except RuntimeError: pass
        jaribu:  ashiria KeyboardInterrupt
        except KeyboardInterrupt: pass

    eleza testImport(self):
        # 'import' dotted_as_names
        agiza sys
        agiza time, sys
        # 'from' dotted_name 'import' ('*' | '(' import_as_names ')' | import_as_names)
        kutoka time agiza time
        kutoka time agiza (time)
        # sio testable inside a function, but already done at top of the module
        # kutoka sys agiza *
        kutoka sys agiza path, argv
        kutoka sys agiza (path, argv)
        kutoka sys agiza (path, argv,)

    eleza testGlobal(self):
        # 'global' NAME (',' NAME)*
        global a
        global a, b
        global one, two, three, four, five, six, seven, eight, nine, ten

    eleza testExec(self):
        # 'exec' expr ['in' expr [',' expr]]
        z = Tupu
        toa z
        exec 'z=1+1\n'
        ikiwa z != 2: self.fail('exec \'z=1+1\'\\n')
        toa z
        exec 'z=1+1'
        ikiwa z != 2: self.fail('exec \'z=1+1\'')
        z = Tupu
        toa z
        agiza types
        ikiwa hasattr(types, "UnicodeType"):
            exec r"""ikiwa 1:
            exec u'z=1+1\n'
            ikiwa z != 2: self.fail('exec u\'z=1+1\'\\n')
            toa z
            exec u'z=1+1'
            ikiwa z != 2: self.fail('exec u\'z=1+1\'')"""
        g = {}
        exec 'z = 1' kwenye g
        ikiwa g.has_key('__builtins__'): toa g['__builtins__']
        ikiwa g != {'z': 1}: self.fail('exec \'z = 1\' kwenye g')
        g = {}
        l = {}

        agiza warnings
        warnings.filterwarnings("ignore", "global statement", module="<string>")
        exec 'global a; a = 1; b = 2' kwenye g, l
        ikiwa g.has_key('__builtins__'): toa g['__builtins__']
        ikiwa l.has_key('__builtins__'): toa l['__builtins__']
        ikiwa (g, l) != ({'a':1}, {'b':2}):
            self.fail('exec ... kwenye g (%s), l (%s)' %(g,l))

    eleza testAssert(self):
        # assert_stmt: 'assert' test [',' test]
        assert 1
        assert 1, 1
        assert lambda x:x
        assert 1, lambda x:x+1
        jaribu:
            assert 0, "msg"
        except AssertionError, e:
            self.assertEquals(e.args[0], "msg")
        isipokua:
            ikiwa __debug__:
                self.fail("AssertionError sio raised by assert 0")

    ### compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funceleza | classdef
    # Tested below

    eleza testIf(self):
        # 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
        ikiwa 1: pass
        ikiwa 1: pass
        isipokua: pass
        ikiwa 0: pass
        elikiwa 0: pass
        ikiwa 0: pass
        elikiwa 0: pass
        elikiwa 0: pass
        elikiwa 0: pass
        isipokua: pass

    eleza testWhile(self):
        # 'while' test ':' suite ['else' ':' suite]
        wakati 0: pass
        wakati 0: pass
        isipokua: pass

        # Issue1920: "wakati 0" ni optimized away,
        # ensure that the "else" clause ni still present.
        x = 0
        wakati 0:
            x = 1
        isipokua:
            x = 2
        self.assertEquals(x, 2)

    eleza testFor(self):
        # 'for' exprlist 'in' exprlist ':' suite ['else' ':' suite]
        kila i kwenye 1, 2, 3: pass
        kila i, j, k kwenye (): pass
        isipokua: pass
        kundi Squares:
            eleza __init__(self, max):
                self.max = max
                self.sofar = []
            eleza __len__(self): rudisha len(self.sofar)
            eleza __getitem__(self, i):
                ikiwa sio 0 <= i < self.max:  ashiria IndexError
                n = len(self.sofar)
                wakati n <= i:
                    self.sofar.append(n*n)
                    n = n+1
                rudisha self.sofar[i]
        n = 0
        kila x kwenye Squares(10): n = n+x
        ikiwa n != 285:
            self.fail('kila over growing sequence')

        result = []
        kila x, kwenye [(1,), (2,), (3,)]:
            result.append(x)
        self.assertEqual(result, [1, 2, 3])

    eleza testTry(self):
        ### try_stmt: 'try' ':' suite (except_clause ':' suite)+ ['else' ':' suite]
        ###         | 'try' ':' suite 'finally' ':' suite
        ### except_clause: 'except' [expr [('as' | ',') expr]]
        jaribu:
            1/0
        except ZeroDivisionError:
            pass
        isipokua:
            pass
        jaribu: 1/0
        except EOFError: pass
        except TypeError as msg: pass
        except RuntimeError, msg: pass
        tatizo: pass
        isipokua: pass
        jaribu: 1/0
        except (EOFError, TypeError, ZeroDivisionError): pass
        jaribu: 1/0
        except (EOFError, TypeError, ZeroDivisionError), msg: pass
        jaribu: pass
        mwishowe: pass

    eleza testSuite(self):
        # simple_stmt | NEWLINE INDENT NEWLINE* (stmt NEWLINE*)+ DEDENT
        ikiwa 1: pass
        ikiwa 1:
            pass
        ikiwa 1:
            #
            #
            #
            pass
            pass
            #
            pass
            #

    eleza testTest(self):
        ### and_test ('or' and_test)*
        ### and_test: not_test ('and' not_test)*
        ### not_test: 'not' not_test | comparison
        ikiwa sio 1: pass
        ikiwa 1 na 1: pass
        ikiwa 1 ama 1: pass
        ikiwa sio sio sio 1: pass
        ikiwa sio 1 na 1 na 1: pass
        ikiwa 1 na 1 ama 1 na 1 na 1 ama sio 1 na 1: pass

    eleza testComparison(self):
        ### comparison: expr (comp_op expr)*
        ### comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
        ikiwa 1: pass
        x = (1 == 1)
        ikiwa 1 == 1: pass
        ikiwa 1 != 1: pass
        ikiwa 1 <> 1: pass
        ikiwa 1 < 1: pass
        ikiwa 1 > 1: pass
        ikiwa 1 <= 1: pass
        ikiwa 1 >= 1: pass
        ikiwa 1 ni 1: pass
        ikiwa 1 ni sio 1: pass
        ikiwa 1 kwenye (): pass
        ikiwa 1 sio kwenye (): pass
        ikiwa 1 < 1 > 1 == 1 >= 1 <= 1 <> 1 != 1 kwenye 1 sio kwenye 1 ni 1 ni sio 1: pass

    eleza testBinaryMaskOps(self):
        x = 1 & 1
        x = 1 ^ 1
        x = 1 | 1

    eleza testShiftOps(self):
        x = 1 << 1
        x = 1 >> 1
        x = 1 << 1 >> 1

    eleza testAdditiveOps(self):
        x = 1
        x = 1 + 1
        x = 1 - 1 - 1
        x = 1 - 1 + 1 - 1 + 1

    eleza testMultiplicativeOps(self):
        x = 1 * 1
        x = 1 / 1
        x = 1 % 1
        x = 1 / 1 * 1 % 1

    eleza testUnaryOps(self):
        x = +1
        x = -1
        x = ~1
        x = ~1 ^ 1 & 1 | 1 & 1 ^ -1
        x = -1*1/1 + 1*1 - ---1*1

    eleza testSelectors(self):
        ### trailer: '(' [testlist] ')' | '[' subscript ']' | '.' NAME
        ### subscript: expr | [expr] ':' [expr]

        agiza sys, time
        c = sys.path[0]
        x = time.time()
        x = sys.modules['time'].time()
        a = '01234'
        c = a[0]
        c = a[-1]
        s = a[0:5]
        s = a[:5]
        s = a[0:]
        s = a[:]
        s = a[-5:]
        s = a[:-1]
        s = a[-4:-3]
        # A rough test of SF bug 1333982.  http://python.org/sf/1333982
        # The testing here ni fairly incomplete.
        # Test cases should include: commas ukijumuisha 1 na 2 colons
        d = {}
        d[1] = 1
        d[1,] = 2
        d[1,2] = 3
        d[1,2,3] = 4
        L = list(d)
        L.sort()
        self.assertEquals(str(L), '[1, (1,), (1, 2), (1, 2, 3)]')

    eleza testAtoms(self):
        ### atom: '(' [testlist] ')' | '[' [testlist] ']' | '{' [dictmaker] '}' | '`' testlist '`' | NAME | NUMBER | STRING
        ### dictmaker: test ':' test (',' test ':' test)* [',']

        x = (1)
        x = (1 ama 2 ama 3)
        x = (1 ama 2 ama 3, 2, 3)

        x = []
        x = [1]
        x = [1 ama 2 ama 3]
        x = [1 ama 2 ama 3, 2, 3]
        x = []

        x = {}
        x = {'one': 1}
        x = {'one': 1,}
        x = {'one' ama 'two': 1 ama 2}
        x = {'one': 1, 'two': 2}
        x = {'one': 1, 'two': 2,}
        x = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}

        x = `x`
        x = `1 ama 2 ama 3`
        self.assertEqual(`1,2`, '(1, 2)')

        x = x
        x = 'x'
        x = 123

    ### exprlist: expr (',' expr)* [',']
    ### testlist: test (',' test)* [',']
    # These have been exercised enough above

    eleza testClassdef(self):
        # 'class' NAME ['(' [testlist] ')'] ':' suite
        kundi B: pass
        kundi B2(): pass
        kundi C1(B): pass
        kundi C2(B): pass
        kundi D(C1, C2, B): pass
        kundi C:
            eleza meth1(self): pass
            eleza meth2(self, arg): pass
            eleza meth3(self, a1, a2): pass
        # decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
        # decorators: decorator+
        # decorated: decorators (classeleza | funcdef)
        eleza class_decorator(x):
            x.decorated = Kweli
            rudisha x
        @class_decorator
        kundi G:
            pass
        self.assertEqual(G.decorated, Kweli)

    eleza testListcomps(self):
        # list comprehension tests
        nums = [1, 2, 3, 4, 5]
        strs = ["Apple", "Banana", "Coconut"]
        spcs = ["  Apple", " Banana ", "Coco  nut  "]

        self.assertEqual([s.strip() kila s kwenye spcs], ['Apple', 'Banana', 'Coco  nut'])
        self.assertEqual([3 * x kila x kwenye nums], [3, 6, 9, 12, 15])
        self.assertEqual([x kila x kwenye nums ikiwa x > 2], [3, 4, 5])
        self.assertEqual([(i, s) kila i kwenye nums kila s kwenye strs],
                         [(1, 'Apple'), (1, 'Banana'), (1, 'Coconut'),
                          (2, 'Apple'), (2, 'Banana'), (2, 'Coconut'),
                          (3, 'Apple'), (3, 'Banana'), (3, 'Coconut'),
                          (4, 'Apple'), (4, 'Banana'), (4, 'Coconut'),
                          (5, 'Apple'), (5, 'Banana'), (5, 'Coconut')])
        self.assertEqual([(i, s) kila i kwenye nums kila s kwenye [f kila f kwenye strs ikiwa "n" kwenye f]],
                         [(1, 'Banana'), (1, 'Coconut'), (2, 'Banana'), (2, 'Coconut'),
                          (3, 'Banana'), (3, 'Coconut'), (4, 'Banana'), (4, 'Coconut'),
                          (5, 'Banana'), (5, 'Coconut')])
        self.assertEqual([(lambda a:[a**i kila i kwenye range(a+1)])(j) kila j kwenye range(5)],
                         [[1], [1, 1], [1, 2, 4], [1, 3, 9, 27], [1, 4, 16, 64, 256]])

        eleza test_in_func(l):
            rudisha [Tupu < x < 3 kila x kwenye l ikiwa x > 2]

        self.assertEqual(test_in_func(nums), [Uongo, Uongo, Uongo])

        eleza test_nested_front():
            self.assertEqual([[y kila y kwenye [x, x + 1]] kila x kwenye [1,3,5]],
                             [[1, 2], [3, 4], [5, 6]])

        test_nested_front()

        check_syntax_error(self, "[i, s kila i kwenye nums kila s kwenye strs]")
        check_syntax_error(self, "[x ikiwa y]")

        suppliers = [
          (1, "Boeing"),
          (2, "Ford"),
          (3, "Macdonalds")
        ]

        parts = [
          (10, "Airliner"),
          (20, "Engine"),
          (30, "Cheeseburger")
        ]

        suppart = [
          (1, 10), (1, 20), (2, 20), (3, 30)
        ]

        x = [
          (sname, pname)
            kila (sno, sname) kwenye suppliers
              kila (pno, pname) kwenye parts
                kila (sp_sno, sp_pno) kwenye suppart
                  ikiwa sno == sp_sno na pno == sp_pno
        ]

        self.assertEqual(x, [('Boeing', 'Airliner'), ('Boeing', 'Engine'), ('Ford', 'Engine'),
                             ('Macdonalds', 'Cheeseburger')])

    eleza testGenexps(self):
        # generator expression tests
        g = ([x kila x kwenye range(10)] kila x kwenye range(1))
        self.assertEqual(g.next(), [x kila x kwenye range(10)])
        jaribu:
            g.next()
            self.fail('should produce StopIteration exception')
        except StopIteration:
            pass

        a = 1
        jaribu:
            g = (a kila d kwenye a)
            g.next()
            self.fail('should produce TypeError')
        except TypeError:
            pass

        self.assertEqual(list((x, y) kila x kwenye 'abcd' kila y kwenye 'abcd'), [(x, y) kila x kwenye 'abcd' kila y kwenye 'abcd'])
        self.assertEqual(list((x, y) kila x kwenye 'ab' kila y kwenye 'xy'), [(x, y) kila x kwenye 'ab' kila y kwenye 'xy'])

        a = [x kila x kwenye range(10)]
        b = (x kila x kwenye (y kila y kwenye a))
        self.assertEqual(sum(b), sum([x kila x kwenye range(10)]))

        self.assertEqual(sum(x**2 kila x kwenye range(10)), sum([x**2 kila x kwenye range(10)]))
        self.assertEqual(sum(x*x kila x kwenye range(10) ikiwa x%2), sum([x*x kila x kwenye range(10) ikiwa x%2]))
        self.assertEqual(sum(x kila x kwenye (y kila y kwenye range(10))), sum([x kila x kwenye range(10)]))
        self.assertEqual(sum(x kila x kwenye (y kila y kwenye (z kila z kwenye range(10)))), sum([x kila x kwenye range(10)]))
        self.assertEqual(sum(x kila x kwenye [y kila y kwenye (z kila z kwenye range(10))]), sum([x kila x kwenye range(10)]))
        self.assertEqual(sum(x kila x kwenye (y kila y kwenye (z kila z kwenye range(10) ikiwa Kweli)) ikiwa Kweli), sum([x kila x kwenye range(10)]))
        self.assertEqual(sum(x kila x kwenye (y kila y kwenye (z kila z kwenye range(10) ikiwa Kweli) ikiwa Uongo) ikiwa Kweli), 0)
        check_syntax_error(self, "foo(x kila x kwenye range(10), 100)")
        check_syntax_error(self, "foo(100, x kila x kwenye range(10))")

    eleza testComprehensionSpecials(self):
        # test kila outmost iterable precomputation
        x = 10; g = (i kila i kwenye range(x)); x = 5
        self.assertEqual(len(list(g)), 10)

        # This should hold, since we're only precomputing outmost iterable.
        x = 10; t = Uongo; g = ((i,j) kila i kwenye range(x) ikiwa t kila j kwenye range(x))
        x = 5; t = Kweli;
        self.assertEqual([(i,j) kila i kwenye range(10) kila j kwenye range(5)], list(g))

        # Grammar allows multiple adjacent 'if's kwenye listcomps na genexps,
        # even though it's silly. Make sure it works (ifelse broke this.)
        self.assertEqual([ x kila x kwenye range(10) ikiwa x % 2 ikiwa x % 3 ], [1, 5, 7])
        self.assertEqual(list(x kila x kwenye range(10) ikiwa x % 2 ikiwa x % 3), [1, 5, 7])

        # verify unpacking single element tuples kwenye listcomp/genexp.
        self.assertEqual([x kila x, kwenye [(4,), (5,), (6,)]], [4, 5, 6])
        self.assertEqual(list(x kila x, kwenye [(7,), (8,), (9,)]), [7, 8, 9])

    eleza test_with_statement(self):
        kundi manager(object):
            eleza __enter__(self):
                rudisha (1, 2)
            eleza __exit__(self, *args):
                pass

        ukijumuisha manager():
            pass
        ukijumuisha manager() as x:
            pass
        ukijumuisha manager() as (x, y):
            pass
        ukijumuisha manager(), manager():
            pass
        ukijumuisha manager() as x, manager() as y:
            pass
        ukijumuisha manager() as x, manager():
            pass

    eleza testIfElseExpr(self):
        # Test ifelse expressions kwenye various cases
        eleza _checkeval(msg, ret):
            "helper to check that evaluation of expressions ni done correctly"
            print x
            rudisha ret

        self.assertEqual([ x() kila x kwenye lambda: Kweli, lambda: Uongo ikiwa x() ], [Kweli])
        self.assertEqual([ x() kila x kwenye (lambda: Kweli, lambda: Uongo) ikiwa x() ], [Kweli])
        self.assertEqual([ x(Uongo) kila x kwenye (lambda x: Uongo ikiwa x isipokua Kweli, lambda x: Kweli ikiwa x isipokua Uongo) ikiwa x(Uongo) ], [Kweli])
        self.assertEqual((5 ikiwa 1 isipokua _checkeval("check 1", 0)), 5)
        self.assertEqual((_checkeval("check 2", 0) ikiwa 0 isipokua 5), 5)
        self.assertEqual((5 na 6 ikiwa 0 isipokua 1), 1)
        self.assertEqual(((5 na 6) ikiwa 0 isipokua 1), 1)
        self.assertEqual((5 na (6 ikiwa 1 isipokua 1)), 6)
        self.assertEqual((0 ama _checkeval("check 3", 2) ikiwa 0 isipokua 3), 3)
        self.assertEqual((1 ama _checkeval("check 4", 2) ikiwa 1 isipokua _checkeval("check 5", 3)), 1)
        self.assertEqual((0 ama 5 ikiwa 1 isipokua _checkeval("check 6", 3)), 5)
        self.assertEqual((not 5 ikiwa 1 isipokua 1), Uongo)
        self.assertEqual((not 5 ikiwa 0 isipokua 1), 1)
        self.assertEqual((6 + 1 ikiwa 1 isipokua 2), 7)
        self.assertEqual((6 - 1 ikiwa 1 isipokua 2), 5)
        self.assertEqual((6 * 2 ikiwa 1 isipokua 4), 12)
        self.assertEqual((6 / 2 ikiwa 1 isipokua 3), 3)
        self.assertEqual((6 < 4 ikiwa 0 isipokua 2), 2)


eleza test_main():
    run_unittest(TokenTests, GrammarTests)

ikiwa __name__ == '__main__':
    test_main()
