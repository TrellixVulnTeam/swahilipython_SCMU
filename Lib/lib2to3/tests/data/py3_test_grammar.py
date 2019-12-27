# Python test set -- part 1, grammar.
# This just tests whether the parser accepts them all.

# NOTE: When you run this test as a script kutoka the command line, you
# get warnings about certain hex/oct constants.  Since those are
# issued by the parser, you can't suppress them by adding a
# filterwarnings() call to this module.  Therefore, to shut up the
# regression test, the filterwarnings() call has been added to
# regrtest.py.

kutoka test.support agiza run_unittest, check_syntax_error
agiza unittest
agiza sys
# testing agiza *
kutoka sys agiza *

kundi TokenTests(unittest.TestCase):

    eleza testBackslash(self):
        # Backslash means line continuation:
        x = 1 \
        + 1
        self.assertEquals(x, 2, 'backslash for line continuation')

        # Backslash does not means continuation in comments :\
        x = 0
        self.assertEquals(x, 0, 'backslash ending comment')

    eleza testPlainIntegers(self):
        self.assertEquals(type(000), type(0))
        self.assertEquals(0xff, 255)
        self.assertEquals(0o377, 255)
        self.assertEquals(2147483647, 0o17777777777)
        self.assertEquals(0b1001, 9)
        # "0x" is not a valid literal
        self.assertRaises(SyntaxError, eval, "0x")
        kutoka sys agiza maxsize
        ikiwa maxsize == 2147483647:
            self.assertEquals(-2147483647-1, -0o20000000000)
            # XXX -2147483648
            self.assert_(0o37777777777 > 0)
            self.assert_(0xffffffff > 0)
            self.assert_(0b1111111111111111111111111111111 > 0)
            for s in ('2147483648', '0o40000000000', '0x100000000',
                      '0b10000000000000000000000000000000'):
                try:
                    x = eval(s)
                except OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        elikiwa maxsize == 9223372036854775807:
            self.assertEquals(-9223372036854775807-1, -0o1000000000000000000000)
            self.assert_(0o1777777777777777777777 > 0)
            self.assert_(0xffffffffffffffff > 0)
            self.assert_(0b11111111111111111111111111111111111111111111111111111111111111 > 0)
            for s in '9223372036854775808', '0o2000000000000000000000', \
                     '0x10000000000000000', \
                     '0b100000000000000000000000000000000000000000000000000000000000000':
                try:
                    x = eval(s)
                except OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        else:
            self.fail('Weird maxsize value %r' % maxsize)

    eleza testLongIntegers(self):
        x = 0
        x = 0xffffffffffffffff
        x = 0Xffffffffffffffff
        x = 0o77777777777777777
        x = 0O77777777777777777
        x = 123456789012345678901234567890
        x = 0b100000000000000000000000000000000000000000000000000000000000000000000
        x = 0B111111111111111111111111111111111111111111111111111111111111111111111

    eleza testUnderscoresInNumbers(self):
        # Integers
        x = 1_0
        x = 123_456_7_89
        x = 0xabc_123_4_5
        x = 0X_abc_123
        x = 0B11_01
        x = 0b_11_01
        x = 0o45_67
        x = 0O_45_67

        # Floats
        x = 3_1.4
        x = 03_1.4
        x = 3_1.
        x = .3_1
        x = 3.1_4
        x = 0_3.1_4
        x = 3e1_4
        x = 3_1e+4_1
        x = 3_1E-4_1

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
        x = ''; y = ""; self.assert_(len(x) == 0 and x == y)
        x = '\''; y = "'"; self.assert_(len(x) == 1 and x == y and ord(x) == 39)
        x = '"'; y = "\""; self.assert_(len(x) == 1 and x == y and ord(x) == 34)
        x = "doesn't \"shrink\" does it"
        y = 'doesn\'t "shrink" does it'
        self.assert_(len(x) == 24 and x == y)
        x = "does \"shrink\" doesn't it"
        y = 'does "shrink" doesn\'t it'
        self.assert_(len(x) == 24 and x == y)
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
        x = rf"hello \{True}"; y = f"hello \\{True}"
        self.assertEquals(x, y)

    eleza testEllipsis(self):
        x = ...
        self.assert_(x is Ellipsis)
        self.assertRaises(SyntaxError, eval, ".. .")

kundi GrammarTests(unittest.TestCase):

    # single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
    # XXX can't test in a script -- this rule is only used when interactive

    # file_input: (NEWLINE | stmt)* ENDMARKER
    # Being tested as this very moment this very module

    # expr_input: testlist NEWLINE
    # XXX Hard to test -- used only in calls to input()

    eleza testEvalInput(self):
        # testlist ENDMARKER
        x = eval('1, 0 or 1')

    eleza testFuncdef(self):
        ### [decorators] 'def' NAME parameters ['->' test] ':' suite
        ### decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
        ### decorators: decorator+
        ### parameters: '(' [typedargslist] ')'
        ### typedargslist: ((tfpeleza ['=' test] ',')*
        ###                ('*' [tfpdef] (',' tfpeleza ['=' test])* [',' '**' tfpdef] | '**' tfpdef)
        ###                | tfpeleza ['=' test] (',' tfpeleza ['=' test])* [','])
        ### tfpdef: NAME [':' test]
        ### varargslist: ((vfpeleza ['=' test] ',')*
        ###              ('*' [vfpdef] (',' vfpeleza ['=' test])*  [',' '**' vfpdef] | '**' vfpdef)
        ###              | vfpeleza ['=' test] (',' vfpeleza ['=' test])* [','])
        ### vfpdef: NAME
        eleza f1(): pass
        f1()
        f1(*())
        f1(*(), **{})
        eleza f2(one_argument): pass
        eleza f3(two, arguments): pass
        self.assertEquals(f2.__code__.co_varnames, ('one_argument',))
        self.assertEquals(f3.__code__.co_varnames, ('two', 'arguments'))
        eleza a1(one_arg,): pass
        eleza a2(two, args,): pass
        eleza v0(*rest): pass
        eleza v1(a, *rest): pass
        eleza v2(a, b, *rest): pass

        f1()
        f2(1)
        f2(1,)
        f3(1, 2)
        f3(1, 2,)
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

        # keyword argument type tests
        try:
            str('x', **{b'foo':1 })
        except TypeError:
            pass
        else:
            self.fail('Bytes should not work as keyword argument names')
        # keyword only argument tests
        eleza pos0key1(*, key): rudisha key
        pos0key1(key=100)
        eleza pos2key2(p1, p2, *, k1, k2=100): rudisha p1,p2,k1,k2
        pos2key2(1, 2, k1=100)
        pos2key2(1, 2, k1=100, k2=200)
        pos2key2(1, 2, k2=100, k1=200)
        eleza pos2key2dict(p1, p2, *, k1=100, k2, **kwarg): rudisha p1,p2,k1,k2,kwarg
        pos2key2dict(1,2,k2=100,tokwarg1=100,tokwarg2=200)
        pos2key2dict(1,2,tokwarg1=100,tokwarg2=200, k2=100)

        # keyword arguments after *arglist
        eleza f(*args, **kwargs):
            rudisha args, kwargs
        self.assertEquals(f(1, x=2, *[3, 4], y=5), ((1, 3, 4),
                                                    {'x':2, 'y':5}))
        self.assertRaises(SyntaxError, eval, "f(1, *(2,3), 4)")
        self.assertRaises(SyntaxError, eval, "f(1, x=2, *(3,4), x=5)")

        # argument annotation tests
        eleza f(x) -> list: pass
        self.assertEquals(f.__annotations__, {'return': list})
        eleza f(x:int): pass
        self.assertEquals(f.__annotations__, {'x': int})
        eleza f(*x:str): pass
        self.assertEquals(f.__annotations__, {'x': str})
        eleza f(**x:float): pass
        self.assertEquals(f.__annotations__, {'x': float})
        eleza f(x, y:1+2): pass
        self.assertEquals(f.__annotations__, {'y': 3})
        eleza f(a, b:1, c:2, d): pass
        self.assertEquals(f.__annotations__, {'b': 1, 'c': 2})
        eleza f(a, b:1, c:2, d, e:3=4, f=5, *g:6): pass
        self.assertEquals(f.__annotations__,
                          {'b': 1, 'c': 2, 'e': 3, 'g': 6})
        eleza f(a, b:1, c:2, d, e:3=4, f=5, *g:6, h:7, i=8, j:9=10,
              **k:11) -> 12: pass
        self.assertEquals(f.__annotations__,
                          {'b': 1, 'c': 2, 'e': 3, 'g': 6, 'h': 7, 'j': 9,
                           'k': 11, 'return': 12})
        # Check for SF Bug #1697248 - mixing decorators and a rudisha annotation
        eleza null(x): rudisha x
        @null
        eleza f(x) -> list: pass
        self.assertEquals(f.__annotations__, {'return': list})

        # test closures with a variety of oparg's
        closure = 1
        eleza f(): rudisha closure
        eleza f(x=1): rudisha closure
        eleza f(*, k=1): rudisha closure
        eleza f() -> int: rudisha closure

        # Check ast errors in *args and *kwargs
        check_syntax_error(self, "f(*g(1=2))")
        check_syntax_error(self, "f(**g(1=2))")

    eleza testLambdef(self):
        ### lambdef: 'lambda' [varargslist] ':' test
        l1 = lambda : 0
        self.assertEquals(l1(), 0)
        l2 = lambda : a[d] # XXX just testing the expression
        l3 = lambda : [2 < x for x in [-1, 3, 0]]
        self.assertEquals(l3(), [0, 1, 0])
        l4 = lambda x = lambda y = lambda z=1 : z : y() : x()
        self.assertEquals(l4(), 1)
        l5 = lambda x, y, z=2: x + y + z
        self.assertEquals(l5(1, 2), 5)
        self.assertEquals(l5(1, 2, 3), 6)
        check_syntax_error(self, "lambda x: x = 2")
        check_syntax_error(self, "lambda (None,): None")
        l6 = lambda x, y, *, k=20: x+y+k
        self.assertEquals(l6(1,2), 1+2+20)
        self.assertEquals(l6(1,2,k=10), 1+2+10)


    ### stmt: simple_stmt | compound_stmt
    # Tested below

    eleza testSimpleStmt(self):
        ### simple_stmt: small_stmt (';' small_stmt)* [';']
        x = 1; pass; del x
        eleza foo():
            # verify statements that end with semi-colons
            x = 1; pass; del x;
        foo()

    ### small_stmt: expr_stmt | pass_stmt | del_stmt | flow_stmt | import_stmt | global_stmt | access_stmt
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

    eleza testDelStmt(self):
        # 'del' exprlist
        abc = [1,2,3]
        x, y, z = abc
        xyz = x, y, z

        del abc
        del x, y, (z, xyz)

    eleza testPassStmt(self):
        # 'pass'
        pass

    # flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt
    # Tested below

    eleza testBreakStmt(self):
        # 'break'
        while 1: break

    eleza testContinueStmt(self):
        # 'continue'
        i = 1
        while i: i = 0; continue

        msg = ""
        while not msg:
            msg = "ok"
            try:
                continue
                msg = "continue failed to continue inside try"
            except:
                msg = "continue inside try called except block"
        ikiwa msg != "ok":
            self.fail(msg)

        msg = ""
        while not msg:
            msg = "finally block not called"
            try:
                continue
            finally:
                msg = "ok"
        ikiwa msg != "ok":
            self.fail(msg)

    eleza test_break_continue_loop(self):
        # This test warrants an explanation. It is a test specifically for SF bugs
        # #463359 and #462937. The bug is that a 'break' statement executed or
        # exception raised inside a try/except inside a loop, *after* a continue
        # statement has been executed in that loop, will cause the wrong number of
        # arguments to be popped off the stack and the instruction pointer reset to
        # a very small number (usually 0.) Because of this, the following test
        # *must* written as a function, and the tracking vars *must* be function
        # arguments with default values. Otherwise, the test will loop and loop.

        eleza test_inner(extra_burning_oil = 1, count=0):
            big_hippo = 2
            while big_hippo:
                count += 1
                try:
                    ikiwa extra_burning_oil and big_hippo == 1:
                        extra_burning_oil -= 1
                        break
                    big_hippo -= 1
                    continue
                except:
                    raise
            ikiwa count > 2 or big_hippo != 1:
                self.fail("continue then break in try/except in loop broken!")
        test_inner()

    eleza testReturn(self):
        # 'return' [testlist]
        eleza g1(): return
        eleza g2(): rudisha 1
        g1()
        x = g2()
        check_syntax_error(self, "kundi foo:rudisha 1")

    eleza testYield(self):
        check_syntax_error(self, "kundi foo:yield 1")

    eleza testRaise(self):
        # 'raise' test [',' test]
        try: raise RuntimeError('just testing')
        except RuntimeError: pass
        try: raise KeyboardInterrupt
        except KeyboardInterrupt: pass

    eleza testImport(self):
        # 'agiza' dotted_as_names
        agiza sys
        agiza time, sys
        # 'kutoka' dotted_name 'agiza' ('*' | '(' import_as_names ')' | import_as_names)
        kutoka time agiza time
        kutoka time agiza (time)
        # not testable inside a function, but already done at top of the module
        # kutoka sys agiza *
        kutoka sys agiza path, argv
        kutoka sys agiza (path, argv)
        kutoka sys agiza (path, argv,)

    eleza testGlobal(self):
        # 'global' NAME (',' NAME)*
        global a
        global a, b
        global one, two, three, four, five, six, seven, eight, nine, ten

    eleza testNonlocal(self):
        # 'nonlocal' NAME (',' NAME)*
        x = 0
        y = 0
        eleza f():
            nonlocal x
            nonlocal x, y

    eleza testAssert(self):
        # assert_stmt: 'assert' test [',' test]
        assert 1
        assert 1, 1
        assert lambda x:x
        assert 1, lambda x:x+1
        try:
            assert 0, "msg"
        except AssertionError as e:
            self.assertEquals(e.args[0], "msg")
        else:
            ikiwa __debug__:
                self.fail("AssertionError not raised by assert 0")

    ### compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funceleza | classdef
    # Tested below

    eleza testIf(self):
        # 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
        ikiwa 1: pass
        ikiwa 1: pass
        else: pass
        ikiwa 0: pass
        elikiwa 0: pass
        ikiwa 0: pass
        elikiwa 0: pass
        elikiwa 0: pass
        elikiwa 0: pass
        else: pass

    eleza testWhile(self):
        # 'while' test ':' suite ['else' ':' suite]
        while 0: pass
        while 0: pass
        else: pass

        # Issue1920: "while 0" is optimized away,
        # ensure that the "else" clause is still present.
        x = 0
        while 0:
            x = 1
        else:
            x = 2
        self.assertEquals(x, 2)

    eleza testFor(self):
        # 'for' exprlist 'in' exprlist ':' suite ['else' ':' suite]
        for i in 1, 2, 3: pass
        for i, j, k in (): pass
        else: pass
        kundi Squares:
            eleza __init__(self, max):
                self.max = max
                self.sofar = []
            eleza __len__(self): rudisha len(self.sofar)
            eleza __getitem__(self, i):
                ikiwa not 0 <= i < self.max: raise IndexError
                n = len(self.sofar)
                while n <= i:
                    self.sofar.append(n*n)
                    n = n+1
                rudisha self.sofar[i]
        n = 0
        for x in Squares(10): n = n+x
        ikiwa n != 285:
            self.fail('for over growing sequence')

        result = []
        for x, in [(1,), (2,), (3,)]:
            result.append(x)
        self.assertEqual(result, [1, 2, 3])

    eleza testTry(self):
        ### try_stmt: 'try' ':' suite (except_clause ':' suite)+ ['else' ':' suite]
        ###         | 'try' ':' suite 'finally' ':' suite
        ### except_clause: 'except' [expr ['as' expr]]
        try:
            1/0
        except ZeroDivisionError:
            pass
        else:
            pass
        try: 1/0
        except EOFError: pass
        except TypeError as msg: pass
        except RuntimeError as msg: pass
        except: pass
        else: pass
        try: 1/0
        except (EOFError, TypeError, ZeroDivisionError): pass
        try: 1/0
        except (EOFError, TypeError, ZeroDivisionError) as msg: pass
        try: pass
        finally: pass

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
        ikiwa not 1: pass
        ikiwa 1 and 1: pass
        ikiwa 1 or 1: pass
        ikiwa not not not 1: pass
        ikiwa not 1 and 1 and 1: pass
        ikiwa 1 and 1 or 1 and 1 and 1 or not 1 and 1: pass

    eleza testComparison(self):
        ### comparison: expr (comp_op expr)*
        ### comp_op: '<'|'>'|'=='|'>='|'<='|'!='|'in'|'not' 'in'|'is'|'is' 'not'
        ikiwa 1: pass
        x = (1 == 1)
        ikiwa 1 == 1: pass
        ikiwa 1 != 1: pass
        ikiwa 1 < 1: pass
        ikiwa 1 > 1: pass
        ikiwa 1 <= 1: pass
        ikiwa 1 >= 1: pass
        ikiwa 1 is 1: pass
        ikiwa 1 is not 1: pass
        ikiwa 1 in (): pass
        ikiwa 1 not in (): pass
        ikiwa 1 < 1 > 1 == 1 >= 1 <= 1 != 1 in 1 not in 1 is 1 is not 1: pass

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
        # The testing here is fairly incomplete.
        # Test cases should include: commas with 1 and 2 colons
        d = {}
        d[1] = 1
        d[1,] = 2
        d[1,2] = 3
        d[1,2,3] = 4
        L = list(d)
        L.sort(key=lambda x: x ikiwa isinstance(x, tuple) else ())
        self.assertEquals(str(L), '[1, (1,), (1, 2), (1, 2, 3)]')

    eleza testAtoms(self):
        ### atom: '(' [testlist] ')' | '[' [testlist] ']' | '{' [dictsetmaker] '}' | NAME | NUMBER | STRING
        ### dictsetmaker: (test ':' test (',' test ':' test)* [',']) | (test (',' test)* [','])

        x = (1)
        x = (1 or 2 or 3)
        x = (1 or 2 or 3, 2, 3)

        x = []
        x = [1]
        x = [1 or 2 or 3]
        x = [1 or 2 or 3, 2, 3]
        x = []

        x = {}
        x = {'one': 1}
        x = {'one': 1,}
        x = {'one' or 'two': 1 or 2}
        x = {'one': 1, 'two': 2}
        x = {'one': 1, 'two': 2,}
        x = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}

        x = {'one'}
        x = {'one', 1,}
        x = {'one', 'two', 'three'}
        x = {2, 3, 4,}

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
        eleza class_decorator(x): rudisha x
        @class_decorator
        kundi G: pass

    eleza testDictcomps(self):
        # dictorsetmaker: ( (test ':' test (comp_for |
        #                                   (',' test ':' test)* [','])) |
        #                   (test (comp_for | (',' test)* [','])) )
        nums = [1, 2, 3]
        self.assertEqual({i:i+1 for i in nums}, {1: 2, 2: 3, 3: 4})

    eleza testListcomps(self):
        # list comprehension tests
        nums = [1, 2, 3, 4, 5]
        strs = ["Apple", "Banana", "Coconut"]
        spcs = ["  Apple", " Banana ", "Coco  nut  "]

        self.assertEqual([s.strip() for s in spcs], ['Apple', 'Banana', 'Coco  nut'])
        self.assertEqual([3 * x for x in nums], [3, 6, 9, 12, 15])
        self.assertEqual([x for x in nums ikiwa x > 2], [3, 4, 5])
        self.assertEqual([(i, s) for i in nums for s in strs],
                         [(1, 'Apple'), (1, 'Banana'), (1, 'Coconut'),
                          (2, 'Apple'), (2, 'Banana'), (2, 'Coconut'),
                          (3, 'Apple'), (3, 'Banana'), (3, 'Coconut'),
                          (4, 'Apple'), (4, 'Banana'), (4, 'Coconut'),
                          (5, 'Apple'), (5, 'Banana'), (5, 'Coconut')])
        self.assertEqual([(i, s) for i in nums for s in [f for f in strs ikiwa "n" in f]],
                         [(1, 'Banana'), (1, 'Coconut'), (2, 'Banana'), (2, 'Coconut'),
                          (3, 'Banana'), (3, 'Coconut'), (4, 'Banana'), (4, 'Coconut'),
                          (5, 'Banana'), (5, 'Coconut')])
        self.assertEqual([(lambda a:[a**i for i in range(a+1)])(j) for j in range(5)],
                         [[1], [1, 1], [1, 2, 4], [1, 3, 9, 27], [1, 4, 16, 64, 256]])

        eleza test_in_func(l):
            rudisha [0 < x < 3 for x in l ikiwa x > 2]

        self.assertEqual(test_in_func(nums), [False, False, False])

        eleza test_nested_front():
            self.assertEqual([[y for y in [x, x + 1]] for x in [1,3,5]],
                             [[1, 2], [3, 4], [5, 6]])

        test_nested_front()

        check_syntax_error(self, "[i, s for i in nums for s in strs]")
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
            for (sno, sname) in suppliers
              for (pno, pname) in parts
                for (sp_sno, sp_pno) in suppart
                  ikiwa sno == sp_sno and pno == sp_pno
        ]

        self.assertEqual(x, [('Boeing', 'Airliner'), ('Boeing', 'Engine'), ('Ford', 'Engine'),
                             ('Macdonalds', 'Cheeseburger')])

    eleza testGenexps(self):
        # generator expression tests
        g = ([x for x in range(10)] for x in range(1))
        self.assertEqual(next(g), [x for x in range(10)])
        try:
            next(g)
            self.fail('should produce StopIteration exception')
        except StopIteration:
            pass

        a = 1
        try:
            g = (a for d in a)
            next(g)
            self.fail('should produce TypeError')
        except TypeError:
            pass

        self.assertEqual(list((x, y) for x in 'abcd' for y in 'abcd'), [(x, y) for x in 'abcd' for y in 'abcd'])
        self.assertEqual(list((x, y) for x in 'ab' for y in 'xy'), [(x, y) for x in 'ab' for y in 'xy'])

        a = [x for x in range(10)]
        b = (x for x in (y for y in a))
        self.assertEqual(sum(b), sum([x for x in range(10)]))

        self.assertEqual(sum(x**2 for x in range(10)), sum([x**2 for x in range(10)]))
        self.assertEqual(sum(x*x for x in range(10) ikiwa x%2), sum([x*x for x in range(10) ikiwa x%2]))
        self.assertEqual(sum(x for x in (y for y in range(10))), sum([x for x in range(10)]))
        self.assertEqual(sum(x for x in (y for y in (z for z in range(10)))), sum([x for x in range(10)]))
        self.assertEqual(sum(x for x in [y for y in (z for z in range(10))]), sum([x for x in range(10)]))
        self.assertEqual(sum(x for x in (y for y in (z for z in range(10) ikiwa True)) ikiwa True), sum([x for x in range(10)]))
        self.assertEqual(sum(x for x in (y for y in (z for z in range(10) ikiwa True) ikiwa False) ikiwa True), 0)
        check_syntax_error(self, "foo(x for x in range(10), 100)")
        check_syntax_error(self, "foo(100, x for x in range(10))")

    eleza testComprehensionSpecials(self):
        # test for outmost iterable precomputation
        x = 10; g = (i for i in range(x)); x = 5
        self.assertEqual(len(list(g)), 10)

        # This should hold, since we're only precomputing outmost iterable.
        x = 10; t = False; g = ((i,j) for i in range(x) ikiwa t for j in range(x))
        x = 5; t = True;
        self.assertEqual([(i,j) for i in range(10) for j in range(5)], list(g))

        # Grammar allows multiple adjacent 'if's in listcomps and genexps,
        # even though it's silly. Make sure it works (ifelse broke this.)
        self.assertEqual([ x for x in range(10) ikiwa x % 2 ikiwa x % 3 ], [1, 5, 7])
        self.assertEqual(list(x for x in range(10) ikiwa x % 2 ikiwa x % 3), [1, 5, 7])

        # verify unpacking single element tuples in listcomp/genexp.
        self.assertEqual([x for x, in [(4,), (5,), (6,)]], [4, 5, 6])
        self.assertEqual(list(x for x, in [(7,), (8,), (9,)]), [7, 8, 9])

    eleza test_with_statement(self):
        kundi manager(object):
            eleza __enter__(self):
                rudisha (1, 2)
            eleza __exit__(self, *args):
                pass

        with manager():
            pass
        with manager() as x:
            pass
        with manager() as (x, y):
            pass
        with manager(), manager():
            pass
        with manager() as x, manager() as y:
            pass
        with manager() as x, manager():
            pass

    eleza testIfElseExpr(self):
        # Test ifelse expressions in various cases
        eleza _checkeval(msg, ret):
            "helper to check that evaluation of expressions is done correctly"
            andika(x)
            rudisha ret

        # the next line is not allowed anymore
        #self.assertEqual([ x() for x in lambda: True, lambda: False ikiwa x() ], [True])
        self.assertEqual([ x() for x in (lambda: True, lambda: False) ikiwa x() ], [True])
        self.assertEqual([ x(False) for x in (lambda x: False ikiwa x else True, lambda x: True ikiwa x else False) ikiwa x(False) ], [True])
        self.assertEqual((5 ikiwa 1 else _checkeval("check 1", 0)), 5)
        self.assertEqual((_checkeval("check 2", 0) ikiwa 0 else 5), 5)
        self.assertEqual((5 and 6 ikiwa 0 else 1), 1)
        self.assertEqual(((5 and 6) ikiwa 0 else 1), 1)
        self.assertEqual((5 and (6 ikiwa 1 else 1)), 6)
        self.assertEqual((0 or _checkeval("check 3", 2) ikiwa 0 else 3), 3)
        self.assertEqual((1 or _checkeval("check 4", 2) ikiwa 1 else _checkeval("check 5", 3)), 1)
        self.assertEqual((0 or 5 ikiwa 1 else _checkeval("check 6", 3)), 5)
        self.assertEqual((not 5 ikiwa 1 else 1), False)
        self.assertEqual((not 5 ikiwa 0 else 1), 1)
        self.assertEqual((6 + 1 ikiwa 1 else 2), 7)
        self.assertEqual((6 - 1 ikiwa 1 else 2), 5)
        self.assertEqual((6 * 2 ikiwa 1 else 4), 12)
        self.assertEqual((6 / 2 ikiwa 1 else 3), 3)
        self.assertEqual((6 < 4 ikiwa 0 else 2), 2)


eleza test_main():
    run_unittest(TokenTests, GrammarTests)

ikiwa __name__ == '__main__':
    test_main()
