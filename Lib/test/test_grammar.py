# Python test set -- part 1, grammar.
# This just tests whether the parser accepts them all.

kutoka test.support agiza check_syntax_error, check_syntax_warning
agiza inspect
agiza unittest
agiza sys
agiza warnings
# testing agiza *
kutoka sys agiza *

# different agiza patterns to check that __annotations__ does not interfere
# with agiza machinery
agiza test.ann_module as ann_module
agiza typing
kutoka collections agiza ChainMap
kutoka test agiza ann_module2
agiza test

# These are shared with test_tokenize and other test modules.
#
# Note: since several test cases filter out floats by looking for "e" and ".",
# don't add hexadecimal literals that contain "e" or "E".
VALID_UNDERSCORE_LITERALS = [
    '0_0_0',
    '4_2',
    '1_0000_0000',
    '0b1001_0100',
    '0xffff_ffff',
    '0o5_7_7',
    '1_00_00.5',
    '1_00_00.5e5',
    '1_00_00e5_1',
    '1e1_0',
    '.1_4',
    '.1_4e1',
    '0b_0',
    '0x_f',
    '0o_5',
    '1_00_00j',
    '1_00_00.5j',
    '1_00_00e5_1j',
    '.1_4j',
    '(1_2.5+3_3j)',
    '(.5_6j)',
]
INVALID_UNDERSCORE_LITERALS = [
    # Trailing underscores:
    '0_',
    '42_',
    '1.4j_',
    '0x_',
    '0b1_',
    '0xf_',
    '0o5_',
    '0 ikiwa 1_Else 1',
    # Underscores in the base selector:
    '0_b0',
    '0_xf',
    '0_o5',
    # Old-style octal, still disallowed:
    '0_7',
    '09_99',
    # Multiple consecutive underscores:
    '4_______2',
    '0.1__4',
    '0.1__4j',
    '0b1001__0100',
    '0xffff__ffff',
    '0x___',
    '0o5__77',
    '1e1__0',
    '1e1__0j',
    # Underscore right before a dot:
    '1_.4',
    '1_.4j',
    # Underscore right after a dot:
    '1._4',
    '1._4j',
    '._5',
    '._5j',
    # Underscore right after a sign:
    '1.0e+_1',
    '1.0e+_1j',
    # Underscore right before j:
    '1.4_j',
    '1.4e5_j',
    # Underscore right before e:
    '1_e1',
    '1.4_e1',
    '1.4_e1j',
    # Underscore right after e:
    '1e_1',
    '1.4e_1',
    '1.4e_1j',
    # Complex cases with parens:
    '(1+1.5_j_)',
    '(1+1.5_j)',
]


kundi TokenTests(unittest.TestCase):

    kutoka test.support agiza check_syntax_error

    eleza test_backslash(self):
        # Backslash means line continuation:
        x = 1 \
        + 1
        self.assertEqual(x, 2, 'backslash for line continuation')

        # Backslash does not means continuation in comments :\
        x = 0
        self.assertEqual(x, 0, 'backslash ending comment')

    eleza test_plain_integers(self):
        self.assertEqual(type(000), type(0))
        self.assertEqual(0xff, 255)
        self.assertEqual(0o377, 255)
        self.assertEqual(2147483647, 0o17777777777)
        self.assertEqual(0b1001, 9)
        # "0x" is not a valid literal
        self.assertRaises(SyntaxError, eval, "0x")
        kutoka sys agiza maxsize
        ikiwa maxsize == 2147483647:
            self.assertEqual(-2147483647-1, -0o20000000000)
            # XXX -2147483648
            self.assertTrue(0o37777777777 > 0)
            self.assertTrue(0xffffffff > 0)
            self.assertTrue(0b1111111111111111111111111111111 > 0)
            for s in ('2147483648', '0o40000000000', '0x100000000',
                      '0b10000000000000000000000000000000'):
                try:
                    x = eval(s)
                except OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        elikiwa maxsize == 9223372036854775807:
            self.assertEqual(-9223372036854775807-1, -0o1000000000000000000000)
            self.assertTrue(0o1777777777777777777777 > 0)
            self.assertTrue(0xffffffffffffffff > 0)
            self.assertTrue(0b11111111111111111111111111111111111111111111111111111111111111 > 0)
            for s in '9223372036854775808', '0o2000000000000000000000', \
                     '0x10000000000000000', \
                     '0b100000000000000000000000000000000000000000000000000000000000000':
                try:
                    x = eval(s)
                except OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        else:
            self.fail('Weird maxsize value %r' % maxsize)

    eleza test_long_integers(self):
        x = 0
        x = 0xffffffffffffffff
        x = 0Xffffffffffffffff
        x = 0o77777777777777777
        x = 0O77777777777777777
        x = 123456789012345678901234567890
        x = 0b100000000000000000000000000000000000000000000000000000000000000000000
        x = 0B111111111111111111111111111111111111111111111111111111111111111111111

    eleza test_floats(self):
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

    eleza test_float_exponent_tokenization(self):
        # See issue 21642.
        self.assertEqual(1 ikiwa 1else 0, 1)
        self.assertEqual(1 ikiwa 0else 0, 0)
        self.assertRaises(SyntaxError, eval, "0 ikiwa 1Else 0")

    eleza test_underscore_literals(self):
        for lit in VALID_UNDERSCORE_LITERALS:
            self.assertEqual(eval(lit), eval(lit.replace('_', '')))
        for lit in INVALID_UNDERSCORE_LITERALS:
            self.assertRaises(SyntaxError, eval, lit)
        # Sanity check: no literal begins with an underscore
        self.assertRaises(NameError, eval, "_0")

    eleza test_bad_numerical_literals(self):
        check = self.check_syntax_error
        check("0b12", "invalid digit '2' in binary literal")
        check("0b1_2", "invalid digit '2' in binary literal")
        check("0b2", "invalid digit '2' in binary literal")
        check("0b1_", "invalid binary literal")
        check("0b", "invalid binary literal")
        check("0o18", "invalid digit '8' in octal literal")
        check("0o1_8", "invalid digit '8' in octal literal")
        check("0o8", "invalid digit '8' in octal literal")
        check("0o1_", "invalid octal literal")
        check("0o", "invalid octal literal")
        check("0x1_", "invalid hexadecimal literal")
        check("0x", "invalid hexadecimal literal")
        check("1_", "invalid decimal literal")
        check("012",
              "leading zeros in decimal integer literals are not permitted; "
              "use an 0o prefix for octal integers")
        check("1.2_", "invalid decimal literal")
        check("1e2_", "invalid decimal literal")
        check("1e+", "invalid decimal literal")

    eleza test_string_literals(self):
        x = ''; y = ""; self.assertTrue(len(x) == 0 and x == y)
        x = '\''; y = "'"; self.assertTrue(len(x) == 1 and x == y and ord(x) == 39)
        x = '"'; y = "\""; self.assertTrue(len(x) == 1 and x == y and ord(x) == 34)
        x = "doesn't \"shrink\" does it"
        y = 'doesn\'t "shrink" does it'
        self.assertTrue(len(x) == 24 and x == y)
        x = "does \"shrink\" doesn't it"
        y = 'does "shrink" doesn\'t it'
        self.assertTrue(len(x) == 24 and x == y)
        x = """
The "quick"
brown fox
jumps over
the 'lazy' dog.
"""
        y = '\nThe "quick"\nbrown fox\njumps over\nthe \'lazy\' dog.\n'
        self.assertEqual(x, y)
        y = '''
The "quick"
brown fox
jumps over
the 'lazy' dog.
'''
        self.assertEqual(x, y)
        y = "\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the 'lazy' dog.\n\
"
        self.assertEqual(x, y)
        y = '\n\
The \"quick\"\n\
brown fox\n\
jumps over\n\
the \'lazy\' dog.\n\
'
        self.assertEqual(x, y)

    eleza test_ellipsis(self):
        x = ...
        self.assertTrue(x is Ellipsis)
        self.assertRaises(SyntaxError, eval, ".. .")

    eleza test_eof_error(self):
        samples = ("eleza foo(", "\neleza foo(", "eleza foo(\n")
        for s in samples:
            with self.assertRaises(SyntaxError) as cm:
                compile(s, "<test>", "exec")
            self.assertIn("unexpected EOF", str(cm.exception))

var_annot_global: int # a global annotated is necessary for test_var_annot

# custom namespace for testing __annotations__

kundi CNS:
    eleza __init__(self):
        self._dct = {}
    eleza __setitem__(self, item, value):
        self._dct[item.lower()] = value
    eleza __getitem__(self, item):
        rudisha self._dct[item]


kundi GrammarTests(unittest.TestCase):

    kutoka test.support agiza check_syntax_error, check_syntax_warning

    # single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
    # XXX can't test in a script -- this rule is only used when interactive

    # file_input: (NEWLINE | stmt)* ENDMARKER
    # Being tested as this very moment this very module

    # expr_input: testlist NEWLINE
    # XXX Hard to test -- used only in calls to input()

    eleza test_eval_input(self):
        # testlist ENDMARKER
        x = eval('1, 0 or 1')

    eleza test_var_annot_basics(self):
        # all these should be allowed
        var1: int = 5
        var2: [int, str]
        my_lst = [42]
        eleza one():
            rudisha 1
        int.new_attr: int
        [list][0]: type
        my_lst[one()-1]: int = 5
        self.assertEqual(my_lst, [5])

    eleza test_var_annot_syntax_errors(self):
        # parser pass
        check_syntax_error(self, "eleza f: int")
        check_syntax_error(self, "x: int: str")
        check_syntax_error(self, "eleza f():\n"
                                 "    nonlocal x: int\n")
        # AST pass
        check_syntax_error(self, "[x, 0]: int\n")
        check_syntax_error(self, "f(): int\n")
        check_syntax_error(self, "(x,): int")
        check_syntax_error(self, "eleza f():\n"
                                 "    (x, y): int = (1, 2)\n")
        # symtable pass
        check_syntax_error(self, "eleza f():\n"
                                 "    x: int\n"
                                 "    global x\n")
        check_syntax_error(self, "eleza f():\n"
                                 "    global x\n"
                                 "    x: int\n")

    eleza test_var_annot_basic_semantics(self):
        # execution order
        with self.assertRaises(ZeroDivisionError):
            no_name[does_not_exist]: no_name_again = 1/0
        with self.assertRaises(NameError):
            no_name[does_not_exist]: 1/0 = 0
        global var_annot_global

        # function semantics
        eleza f():
            st: str = "Hello"
            a.b: int = (1, 2)
            rudisha st
        self.assertEqual(f.__annotations__, {})
        eleza f_OK():
            x: 1/0
        f_OK()
        eleza fbad():
            x: int
            andika(x)
        with self.assertRaises(UnboundLocalError):
            fbad()
        eleza f2bad():
            (no_such_global): int
            andika(no_such_global)
        try:
            f2bad()
        except Exception as e:
            self.assertIs(type(e), NameError)

        # kundi semantics
        kundi C:
            __foo: int
            s: str = "attr"
            z = 2
            eleza __init__(self, x):
                self.x: int = x
        self.assertEqual(C.__annotations__, {'_C__foo': int, 's': str})
        with self.assertRaises(NameError):
            kundi CBad:
                no_such_name_defined.attr: int = 0
        with self.assertRaises(NameError):
            kundi Cbad2(C):
                x: int
                x.y: list = []

    eleza test_var_annot_metaclass_semantics(self):
        kundi CMeta(type):
            @classmethod
            eleza __prepare__(metacls, name, bases, **kwds):
                rudisha {'__annotations__': CNS()}
        kundi CC(metaclass=CMeta):
            XX: 'ANNOT'
        self.assertEqual(CC.__annotations__['xx'], 'ANNOT')

    eleza test_var_annot_module_semantics(self):
        with self.assertRaises(AttributeError):
            andika(test.__annotations__)
        self.assertEqual(ann_module.__annotations__,
                     {1: 2, 'x': int, 'y': str, 'f': typing.Tuple[int, int]})
        self.assertEqual(ann_module.M.__annotations__,
                              {'123': 123, 'o': type})
        self.assertEqual(ann_module2.__annotations__, {})

    eleza test_var_annot_in_module(self):
        # check that functions fail the same way when executed
        # outside of module where they were defined
        kutoka test.ann_module3 agiza f_bad_ann, g_bad_ann, D_bad_ann
        with self.assertRaises(NameError):
            f_bad_ann()
        with self.assertRaises(NameError):
            g_bad_ann()
        with self.assertRaises(NameError):
            D_bad_ann(5)

    eleza test_var_annot_simple_exec(self):
        gns = {}; lns= {}
        exec("'docstring'\n"
             "__annotations__[1] = 2\n"
             "x: int = 5\n", gns, lns)
        self.assertEqual(lns["__annotations__"], {1: 2, 'x': int})
        with self.assertRaises(KeyError):
            gns['__annotations__']

    eleza test_var_annot_custom_maps(self):
        # tests with custom locals() and __annotations__
        ns = {'__annotations__': CNS()}
        exec('X: int; Z: str = "Z"; (w): complex = 1j', ns)
        self.assertEqual(ns['__annotations__']['x'], int)
        self.assertEqual(ns['__annotations__']['z'], str)
        with self.assertRaises(KeyError):
            ns['__annotations__']['w']
        nonloc_ns = {}
        kundi CNS2:
            eleza __init__(self):
                self._dct = {}
            eleza __setitem__(self, item, value):
                nonlocal nonloc_ns
                self._dct[item] = value
                nonloc_ns[item] = value
            eleza __getitem__(self, item):
                rudisha self._dct[item]
        exec('x: int = 1', {}, CNS2())
        self.assertEqual(nonloc_ns['__annotations__']['x'], int)

    eleza test_var_annot_refleak(self):
        # complex case: custom locals plus custom __annotations__
        # this was causing refleak
        cns = CNS()
        nonloc_ns = {'__annotations__': cns}
        kundi CNS2:
            eleza __init__(self):
                self._dct = {'__annotations__': cns}
            eleza __setitem__(self, item, value):
                nonlocal nonloc_ns
                self._dct[item] = value
                nonloc_ns[item] = value
            eleza __getitem__(self, item):
                rudisha self._dct[item]
        exec('X: str', {}, CNS2())
        self.assertEqual(nonloc_ns['__annotations__']['x'], str)

    eleza test_var_annot_rhs(self):
        ns = {}
        exec('x: tuple = 1, 2', ns)
        self.assertEqual(ns['x'], (1, 2))
        stmt = ('eleza f():\n'
                '    x: int = yield')
        exec(stmt, ns)
        self.assertEqual(list(ns['f']()), [None])

        ns = {"a": 1, 'b': (2, 3, 4), "c":5, "Tuple": typing.Tuple}
        exec('x: Tuple[int, ...] = a,*b,c', ns)
        self.assertEqual(ns['x'], (1, 2, 3, 4, 5))

    eleza test_funcdef(self):
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
        self.assertEqual(f2.__code__.co_varnames, ('one_argument',))
        self.assertEqual(f3.__code__.co_varnames, ('two', 'arguments'))
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
        d01(*[] or [2])
        d01(*() or (), *{} and (), **() or {})
        d01(**{'a':2})
        d01(**{'a':2} or {})
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

        self.assertRaises(SyntaxError, eval, "eleza f(*): pass")
        self.assertRaises(SyntaxError, eval, "eleza f(*,): pass")
        self.assertRaises(SyntaxError, eval, "eleza f(*, **kwds): pass")

        # keyword arguments after *arglist
        eleza f(*args, **kwargs):
            rudisha args, kwargs
        self.assertEqual(f(1, x=2, *[3, 4], y=5), ((1, 3, 4),
                                                    {'x':2, 'y':5}))
        self.assertEqual(f(1, *(2,3), 4), ((1, 2, 3, 4), {}))
        self.assertRaises(SyntaxError, eval, "f(1, x=2, *(3,4), x=5)")
        self.assertEqual(f(**{'eggs':'scrambled', 'spam':'fried'}),
                         ((), {'eggs':'scrambled', 'spam':'fried'}))
        self.assertEqual(f(spam='fried', **{'eggs':'scrambled'}),
                         ((), {'eggs':'scrambled', 'spam':'fried'}))

        # Check ast errors in *args and *kwargs
        check_syntax_error(self, "f(*g(1=2))")
        check_syntax_error(self, "f(**g(1=2))")

        # argument annotation tests
        eleza f(x) -> list: pass
        self.assertEqual(f.__annotations__, {'return': list})
        eleza f(x: int): pass
        self.assertEqual(f.__annotations__, {'x': int})
        eleza f(x: int, /): pass
        self.assertEqual(f.__annotations__, {'x': int})
        eleza f(x: int = 34, /): pass
        self.assertEqual(f.__annotations__, {'x': int})
        eleza f(*x: str): pass
        self.assertEqual(f.__annotations__, {'x': str})
        eleza f(**x: float): pass
        self.assertEqual(f.__annotations__, {'x': float})
        eleza f(x, y: 1+2): pass
        self.assertEqual(f.__annotations__, {'y': 3})
        eleza f(x, y: 1+2, /): pass
        self.assertEqual(f.__annotations__, {'y': 3})
        eleza f(a, b: 1, c: 2, d): pass
        self.assertEqual(f.__annotations__, {'b': 1, 'c': 2})
        eleza f(a, b: 1, /, c: 2, d): pass
        self.assertEqual(f.__annotations__, {'b': 1, 'c': 2})
        eleza f(a, b: 1, c: 2, d, e: 3 = 4, f=5, *g: 6): pass
        self.assertEqual(f.__annotations__,
                         {'b': 1, 'c': 2, 'e': 3, 'g': 6})
        eleza f(a, b: 1, c: 2, d, e: 3 = 4, f=5, *g: 6, h: 7, i=8, j: 9 = 10,
              **k: 11) -> 12: pass
        self.assertEqual(f.__annotations__,
                         {'b': 1, 'c': 2, 'e': 3, 'g': 6, 'h': 7, 'j': 9,
                          'k': 11, 'return': 12})
        eleza f(a, b: 1, c: 2, d, e: 3 = 4, f: int = 5, /, *g: 6, h: 7, i=8, j: 9 = 10,
              **k: 11) -> 12: pass
        self.assertEqual(f.__annotations__,
                          {'b': 1, 'c': 2, 'e': 3, 'f': int, 'g': 6, 'h': 7, 'j': 9,
                           'k': 11, 'return': 12})
        # Check for issue #20625 -- annotations mangling
        kundi Spam:
            eleza f(self, *, __kw: 1):
                pass
        kundi Ham(Spam): pass
        self.assertEqual(Spam.f.__annotations__, {'_Spam__kw': 1})
        self.assertEqual(Ham.f.__annotations__, {'_Spam__kw': 1})
        # Check for SF Bug #1697248 - mixing decorators and a rudisha annotation
        eleza null(x): rudisha x
        @null
        eleza f(x) -> list: pass
        self.assertEqual(f.__annotations__, {'return': list})

        # test closures with a variety of opargs
        closure = 1
        eleza f(): rudisha closure
        eleza f(x=1): rudisha closure
        eleza f(*, k=1): rudisha closure
        eleza f() -> int: rudisha closure

        # Check trailing commas are permitted in funceleza argument list
        eleza f(a,): pass
        eleza f(*args,): pass
        eleza f(**kwds,): pass
        eleza f(a, *args,): pass
        eleza f(a, **kwds,): pass
        eleza f(*args, b,): pass
        eleza f(*, b,): pass
        eleza f(*args, **kwds,): pass
        eleza f(a, *args, b,): pass
        eleza f(a, *, b,): pass
        eleza f(a, *args, **kwds,): pass
        eleza f(*args, b, **kwds,): pass
        eleza f(*, b, **kwds,): pass
        eleza f(a, *args, b, **kwds,): pass
        eleza f(a, *, b, **kwds,): pass

    eleza test_lambdef(self):
        ### lambdef: 'lambda' [varargslist] ':' test
        l1 = lambda : 0
        self.assertEqual(l1(), 0)
        l2 = lambda : a[d] # XXX just testing the expression
        l3 = lambda : [2 < x for x in [-1, 3, 0]]
        self.assertEqual(l3(), [0, 1, 0])
        l4 = lambda x = lambda y = lambda z=1 : z : y() : x()
        self.assertEqual(l4(), 1)
        l5 = lambda x, y, z=2: x + y + z
        self.assertEqual(l5(1, 2), 5)
        self.assertEqual(l5(1, 2, 3), 6)
        check_syntax_error(self, "lambda x: x = 2")
        check_syntax_error(self, "lambda (None,): None")
        l6 = lambda x, y, *, k=20: x+y+k
        self.assertEqual(l6(1,2), 1+2+20)
        self.assertEqual(l6(1,2,k=10), 1+2+10)

        # check that trailing commas are permitted
        l10 = lambda a,: 0
        l11 = lambda *args,: 0
        l12 = lambda **kwds,: 0
        l13 = lambda a, *args,: 0
        l14 = lambda a, **kwds,: 0
        l15 = lambda *args, b,: 0
        l16 = lambda *, b,: 0
        l17 = lambda *args, **kwds,: 0
        l18 = lambda a, *args, b,: 0
        l19 = lambda a, *, b,: 0
        l20 = lambda a, *args, **kwds,: 0
        l21 = lambda *args, b, **kwds,: 0
        l22 = lambda *, b, **kwds,: 0
        l23 = lambda a, *args, b, **kwds,: 0
        l24 = lambda a, *, b, **kwds,: 0


    ### stmt: simple_stmt | compound_stmt
    # Tested below

    eleza test_simple_stmt(self):
        ### simple_stmt: small_stmt (';' small_stmt)* [';']
        x = 1; pass; del x
        eleza foo():
            # verify statements that end with semi-colons
            x = 1; pass; del x;
        foo()

    ### small_stmt: expr_stmt | pass_stmt | del_stmt | flow_stmt | import_stmt | global_stmt | access_stmt
    # Tested below

    eleza test_expr_stmt(self):
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

    # Check the heuristic for print & exec covers significant cases
    # As well as placing some limits on false positives
    eleza test_former_statements_refer_to_builtins(self):
        keywords = "print", "exec"
        # Cases where we want the custom error
        cases = [
            "{} foo",
            "{} {{1:foo}}",
            "ikiwa 1: {} foo",
            "ikiwa 1: {} {{1:foo}}",
            "ikiwa 1:\n    {} foo",
            "ikiwa 1:\n    {} {{1:foo}}",
        ]
        for keyword in keywords:
            custom_msg = "call to '{}'".format(keyword)
            for case in cases:
                source = case.format(keyword)
                with self.subTest(source=source):
                    with self.assertRaisesRegex(SyntaxError, custom_msg):
                        exec(source)
                source = source.replace("foo", "(foo.)")
                with self.subTest(source=source):
                    with self.assertRaisesRegex(SyntaxError, "invalid syntax"):
                        exec(source)

    eleza test_del_stmt(self):
        # 'del' exprlist
        abc = [1,2,3]
        x, y, z = abc
        xyz = x, y, z

        del abc
        del x, y, (z, xyz)

    eleza test_pass_stmt(self):
        # 'pass'
        pass

    # flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt
    # Tested below

    eleza test_break_stmt(self):
        # 'break'
        while 1: break

    eleza test_continue_stmt(self):
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

    eleza test_return(self):
        # 'return' [testlist_star_expr]
        eleza g1(): return
        eleza g2(): rudisha 1
        eleza g3():
            z = [2, 3]
            rudisha 1, *z

        g1()
        x = g2()
        y = g3()
        self.assertEqual(y, (1, 2, 3), "unparenthesized star expr return")
        check_syntax_error(self, "kundi foo:rudisha 1")

    eleza test_break_in_finally(self):
        count = 0
        while count < 2:
            count += 1
            try:
                pass
            finally:
                break
        self.assertEqual(count, 1)

        count = 0
        while count < 2:
            count += 1
            try:
                continue
            finally:
                break
        self.assertEqual(count, 1)

        count = 0
        while count < 2:
            count += 1
            try:
                1/0
            finally:
                break
        self.assertEqual(count, 1)

        for count in [0, 1]:
            self.assertEqual(count, 0)
            try:
                pass
            finally:
                break
        self.assertEqual(count, 0)

        for count in [0, 1]:
            self.assertEqual(count, 0)
            try:
                continue
            finally:
                break
        self.assertEqual(count, 0)

        for count in [0, 1]:
            self.assertEqual(count, 0)
            try:
                1/0
            finally:
                break
        self.assertEqual(count, 0)

    eleza test_continue_in_finally(self):
        count = 0
        while count < 2:
            count += 1
            try:
                pass
            finally:
                continue
            break
        self.assertEqual(count, 2)

        count = 0
        while count < 2:
            count += 1
            try:
                break
            finally:
                continue
        self.assertEqual(count, 2)

        count = 0
        while count < 2:
            count += 1
            try:
                1/0
            finally:
                continue
            break
        self.assertEqual(count, 2)

        for count in [0, 1]:
            try:
                pass
            finally:
                continue
            break
        self.assertEqual(count, 1)

        for count in [0, 1]:
            try:
                break
            finally:
                continue
        self.assertEqual(count, 1)

        for count in [0, 1]:
            try:
                1/0
            finally:
                continue
            break
        self.assertEqual(count, 1)

    eleza test_return_in_finally(self):
        eleza g1():
            try:
                pass
            finally:
                rudisha 1
        self.assertEqual(g1(), 1)

        eleza g2():
            try:
                rudisha 2
            finally:
                rudisha 3
        self.assertEqual(g2(), 3)

        eleza g3():
            try:
                1/0
            finally:
                rudisha 4
        self.assertEqual(g3(), 4)

    eleza test_break_in_finally_after_return(self):
        # See issue #37830
        eleza g1(x):
            for count in [0, 1]:
                count2 = 0
                while count2 < 20:
                    count2 += 10
                    try:
                        rudisha count + count2
                    finally:
                        ikiwa x:
                            break
            rudisha 'end', count, count2
        self.assertEqual(g1(False), 10)
        self.assertEqual(g1(True), ('end', 1, 10))

        eleza g2(x):
            for count in [0, 1]:
                for count2 in [10, 20]:
                    try:
                        rudisha count + count2
                    finally:
                        ikiwa x:
                            break
            rudisha 'end', count, count2
        self.assertEqual(g2(False), 10)
        self.assertEqual(g2(True), ('end', 1, 10))

    eleza test_continue_in_finally_after_return(self):
        # See issue #37830
        eleza g1(x):
            count = 0
            while count < 100:
                count += 1
                try:
                    rudisha count
                finally:
                    ikiwa x:
                        continue
            rudisha 'end', count
        self.assertEqual(g1(False), 1)
        self.assertEqual(g1(True), ('end', 100))

        eleza g2(x):
            for count in [0, 1]:
                try:
                    rudisha count
                finally:
                    ikiwa x:
                        continue
            rudisha 'end', count
        self.assertEqual(g2(False), 0)
        self.assertEqual(g2(True), ('end', 1))

    eleza test_yield(self):
        # Allowed as standalone statement
        eleza g(): yield 1
        eleza g(): yield kutoka ()
        # Allowed as RHS of assignment
        eleza g(): x = yield 1
        eleza g(): x = yield kutoka ()
        # Ordinary yield accepts implicit tuples
        eleza g(): yield 1, 1
        eleza g(): x = yield 1, 1
        # 'yield kutoka' does not
        check_syntax_error(self, "eleza g(): yield kutoka (), 1")
        check_syntax_error(self, "eleza g(): x = yield kutoka (), 1")
        # Requires parentheses as subexpression
        eleza g(): 1, (yield 1)
        eleza g(): 1, (yield kutoka ())
        check_syntax_error(self, "eleza g(): 1, yield 1")
        check_syntax_error(self, "eleza g(): 1, yield kutoka ()")
        # Requires parentheses as call argument
        eleza g(): f((yield 1))
        eleza g(): f((yield 1), 1)
        eleza g(): f((yield kutoka ()))
        eleza g(): f((yield kutoka ()), 1)
        # Do not require parenthesis for tuple unpacking
        eleza g(): rest = 4, 5, 6; yield 1, 2, 3, *rest
        self.assertEqual(list(g()), [(1, 2, 3, 4, 5, 6)])
        check_syntax_error(self, "eleza g(): f(yield 1)")
        check_syntax_error(self, "eleza g(): f(yield 1, 1)")
        check_syntax_error(self, "eleza g(): f(yield kutoka ())")
        check_syntax_error(self, "eleza g(): f(yield kutoka (), 1)")
        # Not allowed at top level
        check_syntax_error(self, "yield")
        check_syntax_error(self, "yield kutoka")
        # Not allowed at kundi scope
        check_syntax_error(self, "kundi foo:yield 1")
        check_syntax_error(self, "kundi foo:yield kutoka ()")
        # Check annotation refleak on SyntaxError
        check_syntax_error(self, "eleza g(a:(yield)): pass")

    eleza test_yield_in_comprehensions(self):
        # Check yield in comprehensions
        eleza g(): [x for x in [(yield 1)]]
        eleza g(): [x for x in [(yield kutoka ())]]

        check = self.check_syntax_error
        check("eleza g(): [(yield x) for x in ()]",
              "'yield' inside list comprehension")
        check("eleza g(): [x for x in () ikiwa not (yield x)]",
              "'yield' inside list comprehension")
        check("eleza g(): [y for x in () for y in [(yield x)]]",
              "'yield' inside list comprehension")
        check("eleza g(): {(yield x) for x in ()}",
              "'yield' inside set comprehension")
        check("eleza g(): {(yield x): x for x in ()}",
              "'yield' inside dict comprehension")
        check("eleza g(): {x: (yield x) for x in ()}",
              "'yield' inside dict comprehension")
        check("eleza g(): ((yield x) for x in ())",
              "'yield' inside generator expression")
        check("eleza g(): [(yield kutoka x) for x in ()]",
              "'yield' inside list comprehension")
        check("kundi C: [(yield x) for x in ()]",
              "'yield' inside list comprehension")
        check("[(yield x) for x in ()]",
              "'yield' inside list comprehension")

    eleza test_raise(self):
        # 'raise' test [',' test]
        try: raise RuntimeError('just testing')
        except RuntimeError: pass
        try: raise KeyboardInterrupt
        except KeyboardInterrupt: pass

    eleza test_agiza(self):
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

    eleza test_global(self):
        # 'global' NAME (',' NAME)*
        global a
        global a, b
        global one, two, three, four, five, six, seven, eight, nine, ten

    eleza test_nonlocal(self):
        # 'nonlocal' NAME (',' NAME)*
        x = 0
        y = 0
        eleza f():
            nonlocal x
            nonlocal x, y

    eleza test_assert(self):
        # assertTruestmt: 'assert' test [',' test]
        assert 1
        assert 1, 1
        assert lambda x:x
        assert 1, lambda x:x+1

        try:
            assert True
        except AssertionError as e:
            self.fail("'assert True' should not have raised an AssertionError")

        try:
            assert True, 'this should always pass'
        except AssertionError as e:
            self.fail("'assert True, msg' should not have "
                      "raised an AssertionError")

    # these tests fail ikiwa python is run with -O, so check __debug__
    @unittest.skipUnless(__debug__, "Won't work ikiwa __debug__ is False")
    eleza testAssert2(self):
        try:
            assert 0, "msg"
        except AssertionError as e:
            self.assertEqual(e.args[0], "msg")
        else:
            self.fail("AssertionError not raised by assert 0")

        try:
            assert False
        except AssertionError as e:
            self.assertEqual(len(e.args), 0)
        else:
            self.fail("AssertionError not raised by 'assert False'")

        self.check_syntax_warning('assert(x, "msg")',
                                  'assertion is always true')
        with warnings.catch_warnings():
            warnings.simplefilter('error', SyntaxWarning)
            compile('assert x, "msg"', '<testcase>', 'exec')


    ### compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funceleza | classdef
    # Tested below

    eleza test_if(self):
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

    eleza test_while(self):
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
        self.assertEqual(x, 2)

    eleza test_for(self):
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

    eleza test_try(self):
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
        except: pass
        else: pass
        try: 1/0
        except (EOFError, TypeError, ZeroDivisionError): pass
        try: 1/0
        except (EOFError, TypeError, ZeroDivisionError) as msg: pass
        try: pass
        finally: pass

    eleza test_suite(self):
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

    eleza test_test(self):
        ### and_test ('or' and_test)*
        ### and_test: not_test ('and' not_test)*
        ### not_test: 'not' not_test | comparison
        ikiwa not 1: pass
        ikiwa 1 and 1: pass
        ikiwa 1 or 1: pass
        ikiwa not not not 1: pass
        ikiwa not 1 and 1 and 1: pass
        ikiwa 1 and 1 or 1 and 1 and 1 or not 1 and 1: pass

    eleza test_comparison(self):
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
        ikiwa x is x: pass
        ikiwa x is not x: pass
        ikiwa 1 in (): pass
        ikiwa 1 not in (): pass
        ikiwa 1 < 1 > 1 == 1 >= 1 <= 1 != 1 in 1 not in x is x is not x: pass

    eleza test_comparison_is_literal(self):
        eleza check(test, msg='"is" with a literal'):
            self.check_syntax_warning(test, msg)

        check('x is 1')
        check('x is "thing"')
        check('1 is x')
        check('x is y is 1')
        check('x is not 1', '"is not" with a literal')

        with warnings.catch_warnings():
            warnings.simplefilter('error', SyntaxWarning)
            compile('x is None', '<testcase>', 'exec')
            compile('x is False', '<testcase>', 'exec')
            compile('x is True', '<testcase>', 'exec')
            compile('x is ...', '<testcase>', 'exec')

    eleza test_warn_missed_comma(self):
        eleza check(test):
            self.check_syntax_warning(test, msg)

        msg=r'is not callable; perhaps you missed a comma\?'
        check('[(1, 2) (3, 4)]')
        check('[(x, y) (3, 4)]')
        check('[[1, 2] (3, 4)]')
        check('[{1, 2} (3, 4)]')
        check('[{1: 2} (3, 4)]')
        check('[[i for i in range(5)] (3, 4)]')
        check('[{i for i in range(5)} (3, 4)]')
        check('[(i for i in range(5)) (3, 4)]')
        check('[{i: i for i in range(5)} (3, 4)]')
        check('[f"{x}" (3, 4)]')
        check('[f"x={x}" (3, 4)]')
        check('["abc" (3, 4)]')
        check('[b"abc" (3, 4)]')
        check('[123 (3, 4)]')
        check('[12.3 (3, 4)]')
        check('[12.3j (3, 4)]')
        check('[None (3, 4)]')
        check('[True (3, 4)]')
        check('[... (3, 4)]')

        msg=r'is not subscriptable; perhaps you missed a comma\?'
        check('[{1, 2} [i, j]]')
        check('[{i for i in range(5)} [i, j]]')
        check('[(i for i in range(5)) [i, j]]')
        check('[(lambda x, y: x) [i, j]]')
        check('[123 [i, j]]')
        check('[12.3 [i, j]]')
        check('[12.3j [i, j]]')
        check('[None [i, j]]')
        check('[True [i, j]]')
        check('[... [i, j]]')

        msg=r'indices must be integers or slices, not tuple; perhaps you missed a comma\?'
        check('[(1, 2) [i, j]]')
        check('[(x, y) [i, j]]')
        check('[[1, 2] [i, j]]')
        check('[[i for i in range(5)] [i, j]]')
        check('[f"{x}" [i, j]]')
        check('[f"x={x}" [i, j]]')
        check('["abc" [i, j]]')
        check('[b"abc" [i, j]]')

        msg=r'indices must be integers or slices, not tuple;'
        check('[[1, 2] [3, 4]]')
        msg=r'indices must be integers or slices, not list;'
        check('[[1, 2] [[3, 4]]]')
        check('[[1, 2] [[i for i in range(5)]]]')
        msg=r'indices must be integers or slices, not set;'
        check('[[1, 2] [{3, 4}]]')
        check('[[1, 2] [{i for i in range(5)}]]')
        msg=r'indices must be integers or slices, not dict;'
        check('[[1, 2] [{3: 4}]]')
        check('[[1, 2] [{i: i for i in range(5)}]]')
        msg=r'indices must be integers or slices, not generator;'
        check('[[1, 2] [(i for i in range(5))]]')
        msg=r'indices must be integers or slices, not function;'
        check('[[1, 2] [(lambda x, y: x)]]')
        msg=r'indices must be integers or slices, not str;'
        check('[[1, 2] [f"{x}"]]')
        check('[[1, 2] [f"x={x}"]]')
        check('[[1, 2] ["abc"]]')
        msg=r'indices must be integers or slices, not'
        check('[[1, 2] [b"abc"]]')
        check('[[1, 2] [12.3]]')
        check('[[1, 2] [12.3j]]')
        check('[[1, 2] [None]]')
        check('[[1, 2] [...]]')

        with warnings.catch_warnings():
            warnings.simplefilter('error', SyntaxWarning)
            compile('[(lambda x, y: x) (3, 4)]', '<testcase>', 'exec')
            compile('[[1, 2] [i]]', '<testcase>', 'exec')
            compile('[[1, 2] [0]]', '<testcase>', 'exec')
            compile('[[1, 2] [True]]', '<testcase>', 'exec')
            compile('[[1, 2] [1:2]]', '<testcase>', 'exec')
            compile('[{(1, 2): 3} [i, j]]', '<testcase>', 'exec')

    eleza test_binary_mask_ops(self):
        x = 1 & 1
        x = 1 ^ 1
        x = 1 | 1

    eleza test_shift_ops(self):
        x = 1 << 1
        x = 1 >> 1
        x = 1 << 1 >> 1

    eleza test_additive_ops(self):
        x = 1
        x = 1 + 1
        x = 1 - 1 - 1
        x = 1 - 1 + 1 - 1 + 1

    eleza test_multiplicative_ops(self):
        x = 1 * 1
        x = 1 / 1
        x = 1 % 1
        x = 1 / 1 * 1 % 1

    eleza test_unary_ops(self):
        x = +1
        x = -1
        x = ~1
        x = ~1 ^ 1 & 1 | 1 & 1 ^ -1
        x = -1*1/1 + 1*1 - ---1*1

    eleza test_selectors(self):
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
        L.sort(key=lambda x: (type(x).__name__, x))
        self.assertEqual(str(L), '[1, (1,), (1, 2), (1, 2, 3)]')

    eleza test_atoms(self):
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

    eleza test_classdef(self):
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

    eleza test_dictcomps(self):
        # dictorsetmaker: ( (test ':' test (comp_for |
        #                                   (',' test ':' test)* [','])) |
        #                   (test (comp_for | (',' test)* [','])) )
        nums = [1, 2, 3]
        self.assertEqual({i:i+1 for i in nums}, {1: 2, 2: 3, 3: 4})

    eleza test_listcomps(self):
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

    eleza test_genexps(self):
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

    eleza test_comprehension_specials(self):
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

    eleza test_if_else_expr(self):
        # Test ifelse expressions in various cases
        eleza _checkeval(msg, ret):
            "helper to check that evaluation of expressions is done correctly"
            andika(msg)
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

    eleza test_paren_evaluation(self):
        self.assertEqual(16 // (4 // 2), 8)
        self.assertEqual((16 // 4) // 2, 2)
        self.assertEqual(16 // 4 // 2, 2)
        x = 2
        y = 3
        self.assertTrue(False is (x is y))
        self.assertFalse((False is x) is y)
        self.assertFalse(False is x is y)

    eleza test_matrix_mul(self):
        # This is not intended to be a comprehensive test, rather just to be few
        # samples of the @ operator in test_grammar.py.
        kundi M:
            eleza __matmul__(self, o):
                rudisha 4
            eleza __imatmul__(self, o):
                self.other = o
                rudisha self
        m = M()
        self.assertEqual(m @ m, 4)
        m @= 42
        self.assertEqual(m.other, 42)

    eleza test_async_await(self):
        async eleza test():
            eleza sum():
                pass
            ikiwa 1:
                await someobj()

        self.assertEqual(test.__name__, 'test')
        self.assertTrue(bool(test.__code__.co_flags & inspect.CO_COROUTINE))

        eleza decorator(func):
            setattr(func, '_marked', True)
            rudisha func

        @decorator
        async eleza test2():
            rudisha 22
        self.assertTrue(test2._marked)
        self.assertEqual(test2.__name__, 'test2')
        self.assertTrue(bool(test2.__code__.co_flags & inspect.CO_COROUTINE))

    eleza test_async_for(self):
        kundi Done(Exception): pass

        kundi AIter:
            eleza __aiter__(self):
                rudisha self
            async eleza __anext__(self):
                raise StopAsyncIteration

        async eleza foo():
            async for i in AIter():
                pass
            async for i, j in AIter():
                pass
            async for i in AIter():
                pass
            else:
                pass
            raise Done

        with self.assertRaises(Done):
            foo().send(None)

    eleza test_async_with(self):
        kundi Done(Exception): pass

        kundi manager:
            async eleza __aenter__(self):
                rudisha (1, 2)
            async eleza __aexit__(self, *exc):
                rudisha False

        async eleza foo():
            async with manager():
                pass
            async with manager() as x:
                pass
            async with manager() as (x, y):
                pass
            async with manager(), manager():
                pass
            async with manager() as x, manager() as y:
                pass
            async with manager() as x, manager():
                pass
            raise Done

        with self.assertRaises(Done):
            foo().send(None)


ikiwa __name__ == '__main__':
    unittest.main()
