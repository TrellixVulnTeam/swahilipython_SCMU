# Python test set -- part 1, grammar.
# This just tests whether the parser accepts them all.

kutoka test.support agiza check_syntax_error, check_syntax_warning
agiza inspect
agiza unittest
agiza sys
agiza warnings
# testing agiza *
kutoka sys agiza *

# different agiza patterns to check that __annotations__ does sio interfere
# ukijumuisha agiza machinery
agiza test.ann_module kama ann_module
agiza typing
kutoka collections agiza ChainMap
kutoka test agiza ann_module2
agiza test

# These are shared ukijumuisha test_tokenize na other test modules.
#
# Note: since several test cases filter out floats by looking kila "e" na ".",
# don't add hexadecimal literals that contain "e" ama "E".
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
    # Underscores kwenye the base selector:
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
    # Complex cases ukijumuisha parens:
    '(1+1.5_j_)',
    '(1+1.5_j)',
]


kundi TokenTests(unittest.TestCase):

    kutoka test.support agiza check_syntax_error

    eleza test_backslash(self):
        # Backslash means line continuation:
        x = 1 \
        + 1
        self.assertEqual(x, 2, 'backslash kila line continuation')

        # Backslash does sio means continuation kwenye comments :\
        x = 0
        self.assertEqual(x, 0, 'backslash ending comment')

    eleza test_plain_integers(self):
        self.assertEqual(type(000), type(0))
        self.assertEqual(0xff, 255)
        self.assertEqual(0o377, 255)
        self.assertEqual(2147483647, 0o17777777777)
        self.assertEqual(0b1001, 9)
        # "0x" ni sio a valid literal
        self.assertRaises(SyntaxError, eval, "0x")
        kutoka sys agiza maxsize
        ikiwa maxsize == 2147483647:
            self.assertEqual(-2147483647-1, -0o20000000000)
            # XXX -2147483648
            self.assertKweli(0o37777777777 > 0)
            self.assertKweli(0xffffffff > 0)
            self.assertKweli(0b1111111111111111111111111111111 > 0)
            kila s kwenye ('2147483648', '0o40000000000', '0x100000000',
                      '0b10000000000000000000000000000000'):
                jaribu:
                    x = eval(s)
                tatizo OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        lasivyo maxsize == 9223372036854775807:
            self.assertEqual(-9223372036854775807-1, -0o1000000000000000000000)
            self.assertKweli(0o1777777777777777777777 > 0)
            self.assertKweli(0xffffffffffffffff > 0)
            self.assertKweli(0b11111111111111111111111111111111111111111111111111111111111111 > 0)
            kila s kwenye '9223372036854775808', '0o2000000000000000000000', \
                     '0x10000000000000000', \
                     '0b100000000000000000000000000000000000000000000000000000000000000':
                jaribu:
                    x = eval(s)
                tatizo OverflowError:
                    self.fail("OverflowError on huge integer literal %r" % s)
        isipokua:
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
        kila lit kwenye VALID_UNDERSCORE_LITERALS:
            self.assertEqual(eval(lit), eval(lit.replace('_', '')))
        kila lit kwenye INVALID_UNDERSCORE_LITERALS:
            self.assertRaises(SyntaxError, eval, lit)
        # Sanity check: no literal begins ukijumuisha an underscore
        self.assertRaises(NameError, eval, "_0")

    eleza test_bad_numerical_literals(self):
        check = self.check_syntax_error
        check("0b12", "invalid digit '2' kwenye binary literal")
        check("0b1_2", "invalid digit '2' kwenye binary literal")
        check("0b2", "invalid digit '2' kwenye binary literal")
        check("0b1_", "invalid binary literal")
        check("0b", "invalid binary literal")
        check("0o18", "invalid digit '8' kwenye octal literal")
        check("0o1_8", "invalid digit '8' kwenye octal literal")
        check("0o8", "invalid digit '8' kwenye octal literal")
        check("0o1_", "invalid octal literal")
        check("0o", "invalid octal literal")
        check("0x1_", "invalid hexadecimal literal")
        check("0x", "invalid hexadecimal literal")
        check("1_", "invalid decimal literal")
        check("012",
              "leading zeros kwenye decimal integer literals are sio permitted; "
              "use an 0o prefix kila octal integers")
        check("1.2_", "invalid decimal literal")
        check("1e2_", "invalid decimal literal")
        check("1e+", "invalid decimal literal")

    eleza test_string_literals(self):
        x = ''; y = ""; self.assertKweli(len(x) == 0 na x == y)
        x = '\''; y = "'"; self.assertKweli(len(x) == 1 na x == y na ord(x) == 39)
        x = '"'; y = "\""; self.assertKweli(len(x) == 1 na x == y na ord(x) == 34)
        x = "doesn't \"shrink\" does it"
        y = 'doesn\'t "shrink" does it'
        self.assertKweli(len(x) == 24 na x == y)
        x = "does \"shrink\" doesn't it"
        y = 'does "shrink" doesn\'t it'
        self.assertKweli(len(x) == 24 na x == y)
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
        self.assertKweli(x ni Ellipsis)
        self.assertRaises(SyntaxError, eval, ".. .")

    eleza test_eof_error(self):
        samples = ("eleza foo(", "\neleza foo(", "eleza foo(\n")
        kila s kwenye samples:
            ukijumuisha self.assertRaises(SyntaxError) kama cm:
                compile(s, "<test>", "exec")
            self.assertIn("unexpected EOF", str(cm.exception))

var_annot_global: int # a global annotated ni necessary kila test_var_annot

# custom namespace kila testing __annotations__

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
    # XXX can't test kwenye a script -- this rule ni only used when interactive

    # file_input: (NEWLINE | stmt)* ENDMARKER
    # Being tested kama this very moment this very module

    # expr_input: testlist NEWLINE
    # XXX Hard to test -- used only kwenye calls to uliza()

    eleza test_eval_uliza(self):
        # testlist ENDMARKER
        x = eval('1, 0 ama 1')

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
        # parser pita
        check_syntax_error(self, "eleza f: int")
        check_syntax_error(self, "x: int: str")
        check_syntax_error(self, "eleza f():\n"
                                 "    nonlocal x: int\n")
        # AST pita
        check_syntax_error(self, "[x, 0]: int\n")
        check_syntax_error(self, "f(): int\n")
        check_syntax_error(self, "(x,): int")
        check_syntax_error(self, "eleza f():\n"
                                 "    (x, y): int = (1, 2)\n")
        # symtable pita
        check_syntax_error(self, "eleza f():\n"
                                 "    x: int\n"
                                 "    global x\n")
        check_syntax_error(self, "eleza f():\n"
                                 "    global x\n"
                                 "    x: int\n")

    eleza test_var_annot_basic_semantics(self):
        # execution order
        ukijumuisha self.assertRaises(ZeroDivisionError):
            no_name[does_not_exist]: no_name_again = 1/0
        ukijumuisha self.assertRaises(NameError):
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
        ukijumuisha self.assertRaises(UnboundLocalError):
            fbad()
        eleza f2bad():
            (no_such_global): int
            andika(no_such_global)
        jaribu:
            f2bad()
        tatizo Exception kama e:
            self.assertIs(type(e), NameError)

        # kundi semantics
        kundi C:
            __foo: int
            s: str = "attr"
            z = 2
            eleza __init__(self, x):
                self.x: int = x
        self.assertEqual(C.__annotations__, {'_C__foo': int, 's': str})
        ukijumuisha self.assertRaises(NameError):
            kundi CBad:
                no_such_name_defined.attr: int = 0
        ukijumuisha self.assertRaises(NameError):
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
        ukijumuisha self.assertRaises(AttributeError):
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
        ukijumuisha self.assertRaises(NameError):
            f_bad_ann()
        ukijumuisha self.assertRaises(NameError):
            g_bad_ann()
        ukijumuisha self.assertRaises(NameError):
            D_bad_ann(5)

    eleza test_var_annot_simple_exec(self):
        gns = {}; lns= {}
        exec("'docstring'\n"
             "__annotations__[1] = 2\n"
             "x: int = 5\n", gns, lns)
        self.assertEqual(lns["__annotations__"], {1: 2, 'x': int})
        ukijumuisha self.assertRaises(KeyError):
            gns['__annotations__']

    eleza test_var_annot_custom_maps(self):
        # tests ukijumuisha custom locals() na __annotations__
        ns = {'__annotations__': CNS()}
        exec('X: int; Z: str = "Z"; (w): complex = 1j', ns)
        self.assertEqual(ns['__annotations__']['x'], int)
        self.assertEqual(ns['__annotations__']['z'], str)
        ukijumuisha self.assertRaises(KeyError):
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
                '    x: int = tuma')
        exec(stmt, ns)
        self.assertEqual(list(ns['f']()), [Tupu])

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
        eleza f1(): pita
        f1()
        f1(*())
        f1(*(), **{})
        eleza f2(one_argument): pita
        eleza f3(two, arguments): pita
        self.assertEqual(f2.__code__.co_varnames, ('one_argument',))
        self.assertEqual(f3.__code__.co_varnames, ('two', 'arguments'))
        eleza a1(one_arg,): pita
        eleza a2(two, args,): pita
        eleza v0(*rest): pita
        eleza v1(a, *rest): pita
        eleza v2(a, b, *rest): pita

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

        eleza d01(a=1): pita
        d01()
        d01(1)
        d01(*(1,))
        d01(*[] ama [2])
        d01(*() ama (), *{} na (), **() ama {})
        d01(**{'a':2})
        d01(**{'a':2} ama {})
        eleza d11(a, b=1): pita
        d11(1)
        d11(1, 2)
        d11(1, **{'b':2})
        eleza d21(a, b, c=1): pita
        d21(1, 2)
        d21(1, 2, 3)
        d21(*(1, 2, 3))
        d21(1, *(2, 3))
        d21(1, 2, *(3,))
        d21(1, 2, **{'c':3})
        eleza d02(a=1, b=2): pita
        d02()
        d02(1)
        d02(1, 2)
        d02(*(1, 2))
        d02(1, *(2,))
        d02(1, **{'b':2})
        d02(**{'a': 1, 'b': 2})
        eleza d12(a, b=1, c=2): pita
        d12(1)
        d12(1, 2)
        d12(1, 2, 3)
        eleza d22(a, b, c=1, d=2): pita
        d22(1, 2)
        d22(1, 2, 3)
        d22(1, 2, 3, 4)
        eleza d01v(a=1, *rest): pita
        d01v()
        d01v(1)
        d01v(1, 2)
        d01v(*(1, 2, 3, 4))
        d01v(*(1,))
        d01v(**{'a':2})
        eleza d11v(a, b=1, *rest): pita
        d11v(1)
        d11v(1, 2)
        d11v(1, 2, 3)
        eleza d21v(a, b, c=1, *rest): pita
        d21v(1, 2)
        d21v(1, 2, 3)
        d21v(1, 2, 3, 4)
        d21v(*(1, 2, 3, 4))
        d21v(1, 2, **{'c': 3})
        eleza d02v(a=1, b=2, *rest): pita
        d02v()
        d02v(1)
        d02v(1, 2)
        d02v(1, 2, 3)
        d02v(1, *(2, 3, 4))
        d02v(**{'a': 1, 'b': 2})
        eleza d12v(a, b=1, c=2, *rest): pita
        d12v(1)
        d12v(1, 2)
        d12v(1, 2, 3)
        d12v(1, 2, 3, 4)
        d12v(*(1, 2, 3, 4))
        d12v(1, 2, *(3, 4, 5))
        d12v(1, *(2,), **{'c': 3})
        eleza d22v(a, b, c=1, d=2, *rest): pita
        d22v(1, 2)
        d22v(1, 2, 3)
        d22v(1, 2, 3, 4)
        d22v(1, 2, 3, 4, 5)
        d22v(*(1, 2, 3, 4))
        d22v(1, 2, *(3, 4, 5))
        d22v(1, *(2, 3), **{'d': 4})

        # keyword argument type tests
        jaribu:
            str('x', **{b'foo':1 })
        tatizo TypeError:
            pita
        isipokua:
            self.fail('Bytes should sio work kama keyword argument names')
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

        self.assertRaises(SyntaxError, eval, "eleza f(*): pita")
        self.assertRaises(SyntaxError, eval, "eleza f(*,): pita")
        self.assertRaises(SyntaxError, eval, "eleza f(*, **kwds): pita")

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

        # Check ast errors kwenye *args na *kwargs
        check_syntax_error(self, "f(*g(1=2))")
        check_syntax_error(self, "f(**g(1=2))")

        # argument annotation tests
        eleza f(x) -> list: pita
        self.assertEqual(f.__annotations__, {'return': list})
        eleza f(x: int): pita
        self.assertEqual(f.__annotations__, {'x': int})
        eleza f(x: int, /): pita
        self.assertEqual(f.__annotations__, {'x': int})
        eleza f(x: int = 34, /): pita
        self.assertEqual(f.__annotations__, {'x': int})
        eleza f(*x: str): pita
        self.assertEqual(f.__annotations__, {'x': str})
        eleza f(**x: float): pita
        self.assertEqual(f.__annotations__, {'x': float})
        eleza f(x, y: 1+2): pita
        self.assertEqual(f.__annotations__, {'y': 3})
        eleza f(x, y: 1+2, /): pita
        self.assertEqual(f.__annotations__, {'y': 3})
        eleza f(a, b: 1, c: 2, d): pita
        self.assertEqual(f.__annotations__, {'b': 1, 'c': 2})
        eleza f(a, b: 1, /, c: 2, d): pita
        self.assertEqual(f.__annotations__, {'b': 1, 'c': 2})
        eleza f(a, b: 1, c: 2, d, e: 3 = 4, f=5, *g: 6): pita
        self.assertEqual(f.__annotations__,
                         {'b': 1, 'c': 2, 'e': 3, 'g': 6})
        eleza f(a, b: 1, c: 2, d, e: 3 = 4, f=5, *g: 6, h: 7, i=8, j: 9 = 10,
              **k: 11) -> 12: pita
        self.assertEqual(f.__annotations__,
                         {'b': 1, 'c': 2, 'e': 3, 'g': 6, 'h': 7, 'j': 9,
                          'k': 11, 'return': 12})
        eleza f(a, b: 1, c: 2, d, e: 3 = 4, f: int = 5, /, *g: 6, h: 7, i=8, j: 9 = 10,
              **k: 11) -> 12: pita
        self.assertEqual(f.__annotations__,
                          {'b': 1, 'c': 2, 'e': 3, 'f': int, 'g': 6, 'h': 7, 'j': 9,
                           'k': 11, 'return': 12})
        # Check kila issue #20625 -- annotations mangling
        kundi Spam:
            eleza f(self, *, __kw: 1):
                pita
        kundi Ham(Spam): pita
        self.assertEqual(Spam.f.__annotations__, {'_Spam__kw': 1})
        self.assertEqual(Ham.f.__annotations__, {'_Spam__kw': 1})
        # Check kila SF Bug #1697248 - mixing decorators na a rudisha annotation
        eleza null(x): rudisha x
        @null
        eleza f(x) -> list: pita
        self.assertEqual(f.__annotations__, {'return': list})

        # test closures ukijumuisha a variety of opargs
        closure = 1
        eleza f(): rudisha closure
        eleza f(x=1): rudisha closure
        eleza f(*, k=1): rudisha closure
        eleza f() -> int: rudisha closure

        # Check trailing commas are permitted kwenye funceleza argument list
        eleza f(a,): pita
        eleza f(*args,): pita
        eleza f(**kwds,): pita
        eleza f(a, *args,): pita
        eleza f(a, **kwds,): pita
        eleza f(*args, b,): pita
        eleza f(*, b,): pita
        eleza f(*args, **kwds,): pita
        eleza f(a, *args, b,): pita
        eleza f(a, *, b,): pita
        eleza f(a, *args, **kwds,): pita
        eleza f(*args, b, **kwds,): pita
        eleza f(*, b, **kwds,): pita
        eleza f(a, *args, b, **kwds,): pita
        eleza f(a, *, b, **kwds,): pita

    eleza test_lambdef(self):
        ### lambdef: 'lambda' [varargslist] ':' test
        l1 = lambda : 0
        self.assertEqual(l1(), 0)
        l2 = lambda : a[d] # XXX just testing the expression
        l3 = lambda : [2 < x kila x kwenye [-1, 3, 0]]
        self.assertEqual(l3(), [0, 1, 0])
        l4 = lambda x = lambda y = lambda z=1 : z : y() : x()
        self.assertEqual(l4(), 1)
        l5 = lambda x, y, z=2: x + y + z
        self.assertEqual(l5(1, 2), 5)
        self.assertEqual(l5(1, 2, 3), 6)
        check_syntax_error(self, "lambda x: x = 2")
        check_syntax_error(self, "lambda (Tupu,): Tupu")
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
        x = 1; pita; toa x
        eleza foo():
            # verify statements that end ukijumuisha semi-colons
            x = 1; pita; toa x;
        foo()

    ### small_stmt: expr_stmt | pita_stmt | del_stmt | flow_stmt | import_stmt | global_stmt | access_stmt
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

    # Check the heuristic kila print & exec covers significant cases
    # As well kama placing some limits on false positives
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
        kila keyword kwenye keywords:
            custom_msg = "call to '{}'".format(keyword)
            kila case kwenye cases:
                source = case.format(keyword)
                ukijumuisha self.subTest(source=source):
                    ukijumuisha self.assertRaisesRegex(SyntaxError, custom_msg):
                        exec(source)
                source = source.replace("foo", "(foo.)")
                ukijumuisha self.subTest(source=source):
                    ukijumuisha self.assertRaisesRegex(SyntaxError, "invalid syntax"):
                        exec(source)

    eleza test_del_stmt(self):
        # 'del' exprlist
        abc = [1,2,3]
        x, y, z = abc
        xyz = x, y, z

        toa abc
        toa x, y, (z, xyz)

    eleza test_pita_stmt(self):
        # 'pita'
        pita

    # flow_stmt: koma_stmt | endelea_stmt | return_stmt | raise_stmt
    # Tested below

    eleza test_koma_stmt(self):
        # 'koma'
        wakati 1: koma

    eleza test_endelea_stmt(self):
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
                msg = "endelea inside try called tatizo block"
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
        # #463359 na #462937. The bug ni that a 'koma' statement executed ama
        # exception raised inside a try/tatizo inside a loop, *after* a endelea
        # statement has been executed kwenye that loop, will cause the wrong number of
        # arguments to be popped off the stack na the instruction pointer reset to
        # a very small number (usually 0.) Because of this, the following test
        # *must* written kama a function, na the tracking vars *must* be function
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
            ikiwa count > 2 ama big_hippo != 1:
                self.fail("endelea then koma kwenye try/tatizo kwenye loop broken!")
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

    eleza test_koma_in_finally(self):
        count = 0
        wakati count < 2:
            count += 1
            jaribu:
                pita
            mwishowe:
                koma
        self.assertEqual(count, 1)

        count = 0
        wakati count < 2:
            count += 1
            jaribu:
                endelea
            mwishowe:
                koma
        self.assertEqual(count, 1)

        count = 0
        wakati count < 2:
            count += 1
            jaribu:
                1/0
            mwishowe:
                koma
        self.assertEqual(count, 1)

        kila count kwenye [0, 1]:
            self.assertEqual(count, 0)
            jaribu:
                pita
            mwishowe:
                koma
        self.assertEqual(count, 0)

        kila count kwenye [0, 1]:
            self.assertEqual(count, 0)
            jaribu:
                endelea
            mwishowe:
                koma
        self.assertEqual(count, 0)

        kila count kwenye [0, 1]:
            self.assertEqual(count, 0)
            jaribu:
                1/0
            mwishowe:
                koma
        self.assertEqual(count, 0)

    eleza test_endelea_in_finally(self):
        count = 0
        wakati count < 2:
            count += 1
            jaribu:
                pita
            mwishowe:
                endelea
            koma
        self.assertEqual(count, 2)

        count = 0
        wakati count < 2:
            count += 1
            jaribu:
                koma
            mwishowe:
                endelea
        self.assertEqual(count, 2)

        count = 0
        wakati count < 2:
            count += 1
            jaribu:
                1/0
            mwishowe:
                endelea
            koma
        self.assertEqual(count, 2)

        kila count kwenye [0, 1]:
            jaribu:
                pita
            mwishowe:
                endelea
            koma
        self.assertEqual(count, 1)

        kila count kwenye [0, 1]:
            jaribu:
                koma
            mwishowe:
                endelea
        self.assertEqual(count, 1)

        kila count kwenye [0, 1]:
            jaribu:
                1/0
            mwishowe:
                endelea
            koma
        self.assertEqual(count, 1)

    eleza test_return_in_finally(self):
        eleza g1():
            jaribu:
                pita
            mwishowe:
                rudisha 1
        self.assertEqual(g1(), 1)

        eleza g2():
            jaribu:
                rudisha 2
            mwishowe:
                rudisha 3
        self.assertEqual(g2(), 3)

        eleza g3():
            jaribu:
                1/0
            mwishowe:
                rudisha 4
        self.assertEqual(g3(), 4)

    eleza test_koma_in_finally_after_return(self):
        # See issue #37830
        eleza g1(x):
            kila count kwenye [0, 1]:
                count2 = 0
                wakati count2 < 20:
                    count2 += 10
                    jaribu:
                        rudisha count + count2
                    mwishowe:
                        ikiwa x:
                            koma
            rudisha 'end', count, count2
        self.assertEqual(g1(Uongo), 10)
        self.assertEqual(g1(Kweli), ('end', 1, 10))

        eleza g2(x):
            kila count kwenye [0, 1]:
                kila count2 kwenye [10, 20]:
                    jaribu:
                        rudisha count + count2
                    mwishowe:
                        ikiwa x:
                            koma
            rudisha 'end', count, count2
        self.assertEqual(g2(Uongo), 10)
        self.assertEqual(g2(Kweli), ('end', 1, 10))

    eleza test_endelea_in_finally_after_return(self):
        # See issue #37830
        eleza g1(x):
            count = 0
            wakati count < 100:
                count += 1
                jaribu:
                    rudisha count
                mwishowe:
                    ikiwa x:
                        endelea
            rudisha 'end', count
        self.assertEqual(g1(Uongo), 1)
        self.assertEqual(g1(Kweli), ('end', 100))

        eleza g2(x):
            kila count kwenye [0, 1]:
                jaribu:
                    rudisha count
                mwishowe:
                    ikiwa x:
                        endelea
            rudisha 'end', count
        self.assertEqual(g2(Uongo), 0)
        self.assertEqual(g2(Kweli), ('end', 1))

    eleza test_tuma(self):
        # Allowed kama standalone statement
        eleza g(): tuma 1
        eleza g(): tuma kutoka ()
        # Allowed kama RHS of assignment
        eleza g(): x = tuma 1
        eleza g(): x = tuma kutoka ()
        # Ordinary tuma accepts implicit tuples
        eleza g(): tuma 1, 1
        eleza g(): x = tuma 1, 1
        # 'tuma from' does not
        check_syntax_error(self, "eleza g(): tuma kutoka (), 1")
        check_syntax_error(self, "eleza g(): x = tuma kutoka (), 1")
        # Requires parentheses kama subexpression
        eleza g(): 1, (tuma 1)
        eleza g(): 1, (tuma kutoka ())
        check_syntax_error(self, "eleza g(): 1, tuma 1")
        check_syntax_error(self, "eleza g(): 1, tuma kutoka ()")
        # Requires parentheses kama call argument
        eleza g(): f((tuma 1))
        eleza g(): f((tuma 1), 1)
        eleza g(): f((tuma kutoka ()))
        eleza g(): f((tuma kutoka ()), 1)
        # Do sio require parenthesis kila tuple unpacking
        eleza g(): rest = 4, 5, 6; tuma 1, 2, 3, *rest
        self.assertEqual(list(g()), [(1, 2, 3, 4, 5, 6)])
        check_syntax_error(self, "eleza g(): f(tuma 1)")
        check_syntax_error(self, "eleza g(): f(tuma 1, 1)")
        check_syntax_error(self, "eleza g(): f(tuma kutoka ())")
        check_syntax_error(self, "eleza g(): f(tuma kutoka (), 1)")
        # Not allowed at top level
        check_syntax_error(self, "tuma")
        check_syntax_error(self, "tuma from")
        # Not allowed at kundi scope
        check_syntax_error(self, "kundi foo:tuma 1")
        check_syntax_error(self, "kundi foo:tuma kutoka ()")
        # Check annotation refleak on SyntaxError
        check_syntax_error(self, "eleza g(a:(tuma)): pita")

    eleza test_tuma_in_comprehensions(self):
        # Check tuma kwenye comprehensions
        eleza g(): [x kila x kwenye [(tuma 1)]]
        eleza g(): [x kila x kwenye [(tuma kutoka ())]]

        check = self.check_syntax_error
        check("eleza g(): [(tuma x) kila x kwenye ()]",
              "'tuma' inside list comprehension")
        check("eleza g(): [x kila x kwenye () ikiwa sio (tuma x)]",
              "'tuma' inside list comprehension")
        check("eleza g(): [y kila x kwenye () kila y kwenye [(tuma x)]]",
              "'tuma' inside list comprehension")
        check("eleza g(): {(tuma x) kila x kwenye ()}",
              "'tuma' inside set comprehension")
        check("eleza g(): {(tuma x): x kila x kwenye ()}",
              "'tuma' inside dict comprehension")
        check("eleza g(): {x: (tuma x) kila x kwenye ()}",
              "'tuma' inside dict comprehension")
        check("eleza g(): ((tuma x) kila x kwenye ())",
              "'tuma' inside generator expression")
        check("eleza g(): [(tuma kutoka x) kila x kwenye ()]",
              "'tuma' inside list comprehension")
        check("kundi C: [(tuma x) kila x kwenye ()]",
              "'tuma' inside list comprehension")
        check("[(tuma x) kila x kwenye ()]",
              "'tuma' inside list comprehension")

    eleza test_raise(self):
        # 'raise' test [',' test]
        jaribu: ashiria RuntimeError('just testing')
        tatizo RuntimeError: pita
        jaribu: ashiria KeyboardInterrupt
        tatizo KeyboardInterrupt: pita

    eleza test_import(self):
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
        # assertKwelistmt: 'assert' test [',' test]
        assert 1
        assert 1, 1
        assert lambda x:x
        assert 1, lambda x:x+1

        jaribu:
            assert Kweli
        tatizo AssertionError kama e:
            self.fail("'assert Kweli' should sio have raised an AssertionError")

        jaribu:
            assert Kweli, 'this should always pita'
        tatizo AssertionError kama e:
            self.fail("'assert Kweli, msg' should sio have "
                      "raised an AssertionError")

    # these tests fail ikiwa python ni run ukijumuisha -O, so check __debug__
    @unittest.skipUnless(__debug__, "Won't work ikiwa __debug__ ni Uongo")
    eleza testAssert2(self):
        jaribu:
            assert 0, "msg"
        tatizo AssertionError kama e:
            self.assertEqual(e.args[0], "msg")
        isipokua:
            self.fail("AssertionError sio raised by assert 0")

        jaribu:
            assert Uongo
        tatizo AssertionError kama e:
            self.assertEqual(len(e.args), 0)
        isipokua:
            self.fail("AssertionError sio raised by 'assert Uongo'")

        self.check_syntax_warning('assert(x, "msg")',
                                  'assertion ni always true')
        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error', SyntaxWarning)
            compile('assert x, "msg"', '<testcase>', 'exec')


    ### compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | funceleza | classdef
    # Tested below

    eleza test_if(self):
        # 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
        ikiwa 1: pita
        ikiwa 1: pita
        isipokua: pita
        ikiwa 0: pita
        lasivyo 0: pita
        ikiwa 0: pita
        lasivyo 0: pita
        lasivyo 0: pita
        lasivyo 0: pita
        isipokua: pita

    eleza test_while(self):
        # 'while' test ':' suite ['else' ':' suite]
        wakati 0: pita
        wakati 0: pita
        isipokua: pita

        # Issue1920: "wakati 0" ni optimized away,
        # ensure that the "else" clause ni still present.
        x = 0
        wakati 0:
            x = 1
        isipokua:
            x = 2
        self.assertEqual(x, 2)

    eleza test_for(self):
        # 'for' exprlist 'in' exprlist ':' suite ['else' ':' suite]
        kila i kwenye 1, 2, 3: pita
        kila i, j, k kwenye (): pita
        isipokua: pita
        kundi Squares:
            eleza __init__(self, max):
                self.max = max
                self.sofar = []
            eleza __len__(self): rudisha len(self.sofar)
            eleza __getitem__(self, i):
                ikiwa sio 0 <= i < self.max: ashiria IndexError
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

    eleza test_try(self):
        ### try_stmt: 'try' ':' suite (except_clause ':' suite)+ ['else' ':' suite]
        ###         | 'try' ':' suite 'finally' ':' suite
        ### except_clause: 'except' [expr ['as' expr]]
        jaribu:
            1/0
        tatizo ZeroDivisionError:
            pita
        isipokua:
            pita
        jaribu: 1/0
        tatizo EOFError: pita
        tatizo TypeError kama msg: pita
        tatizo: pita
        isipokua: pita
        jaribu: 1/0
        tatizo (EOFError, TypeError, ZeroDivisionError): pita
        jaribu: 1/0
        tatizo (EOFError, TypeError, ZeroDivisionError) kama msg: pita
        jaribu: pita
        mwishowe: pita

    eleza test_suite(self):
        # simple_stmt | NEWLINE INDENT NEWLINE* (stmt NEWLINE*)+ DEDENT
        ikiwa 1: pita
        ikiwa 1:
            pita
        ikiwa 1:
            #
            #
            #
            pita
            pita
            #
            pita
            #

    eleza test_test(self):
        ### and_test ('or' and_test)*
        ### and_test: not_test ('and' not_test)*
        ### not_test: 'not' not_test | comparison
        ikiwa sio 1: pita
        ikiwa 1 na 1: pita
        ikiwa 1 ama 1: pita
        ikiwa sio sio sio 1: pita
        ikiwa sio 1 na 1 na 1: pita
        ikiwa 1 na 1 ama 1 na 1 na 1 ama sio 1 na 1: pita

    eleza test_comparison(self):
        ### comparison: expr (comp_op expr)*
        ### comp_op: '<'|'>'|'=='|'>='|'<='|'!='|'in'|'not' 'in'|'is'|'is' 'not'
        ikiwa 1: pita
        x = (1 == 1)
        ikiwa 1 == 1: pita
        ikiwa 1 != 1: pita
        ikiwa 1 < 1: pita
        ikiwa 1 > 1: pita
        ikiwa 1 <= 1: pita
        ikiwa 1 >= 1: pita
        ikiwa x ni x: pita
        ikiwa x ni sio x: pita
        ikiwa 1 kwenye (): pita
        ikiwa 1 haiko kwenye (): pita
        ikiwa 1 < 1 > 1 == 1 >= 1 <= 1 != 1 kwenye 1 haiko kwenye x ni x ni sio x: pita

    eleza test_comparison_is_literal(self):
        eleza check(test, msg='"is" ukijumuisha a literal'):
            self.check_syntax_warning(test, msg)

        check('x ni 1')
        check('x ni "thing"')
        check('1 ni x')
        check('x ni y ni 1')
        check('x ni sio 1', '"is not" ukijumuisha a literal')

        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error', SyntaxWarning)
            compile('x ni Tupu', '<testcase>', 'exec')
            compile('x ni Uongo', '<testcase>', 'exec')
            compile('x ni Kweli', '<testcase>', 'exec')
            compile('x ni ...', '<testcase>', 'exec')

    eleza test_warn_missed_comma(self):
        eleza check(test):
            self.check_syntax_warning(test, msg)

        msg=r'is sio callable; perhaps you missed a comma\?'
        check('[(1, 2) (3, 4)]')
        check('[(x, y) (3, 4)]')
        check('[[1, 2] (3, 4)]')
        check('[{1, 2} (3, 4)]')
        check('[{1: 2} (3, 4)]')
        check('[[i kila i kwenye range(5)] (3, 4)]')
        check('[{i kila i kwenye range(5)} (3, 4)]')
        check('[(i kila i kwenye range(5)) (3, 4)]')
        check('[{i: i kila i kwenye range(5)} (3, 4)]')
        check('[f"{x}" (3, 4)]')
        check('[f"x={x}" (3, 4)]')
        check('["abc" (3, 4)]')
        check('[b"abc" (3, 4)]')
        check('[123 (3, 4)]')
        check('[12.3 (3, 4)]')
        check('[12.3j (3, 4)]')
        check('[Tupu (3, 4)]')
        check('[Kweli (3, 4)]')
        check('[... (3, 4)]')

        msg=r'is sio subscriptable; perhaps you missed a comma\?'
        check('[{1, 2} [i, j]]')
        check('[{i kila i kwenye range(5)} [i, j]]')
        check('[(i kila i kwenye range(5)) [i, j]]')
        check('[(lambda x, y: x) [i, j]]')
        check('[123 [i, j]]')
        check('[12.3 [i, j]]')
        check('[12.3j [i, j]]')
        check('[Tupu [i, j]]')
        check('[Kweli [i, j]]')
        check('[... [i, j]]')

        msg=r'indices must be integers ama slices, sio tuple; perhaps you missed a comma\?'
        check('[(1, 2) [i, j]]')
        check('[(x, y) [i, j]]')
        check('[[1, 2] [i, j]]')
        check('[[i kila i kwenye range(5)] [i, j]]')
        check('[f"{x}" [i, j]]')
        check('[f"x={x}" [i, j]]')
        check('["abc" [i, j]]')
        check('[b"abc" [i, j]]')

        msg=r'indices must be integers ama slices, sio tuple;'
        check('[[1, 2] [3, 4]]')
        msg=r'indices must be integers ama slices, sio list;'
        check('[[1, 2] [[3, 4]]]')
        check('[[1, 2] [[i kila i kwenye range(5)]]]')
        msg=r'indices must be integers ama slices, sio set;'
        check('[[1, 2] [{3, 4}]]')
        check('[[1, 2] [{i kila i kwenye range(5)}]]')
        msg=r'indices must be integers ama slices, sio dict;'
        check('[[1, 2] [{3: 4}]]')
        check('[[1, 2] [{i: i kila i kwenye range(5)}]]')
        msg=r'indices must be integers ama slices, sio generator;'
        check('[[1, 2] [(i kila i kwenye range(5))]]')
        msg=r'indices must be integers ama slices, sio function;'
        check('[[1, 2] [(lambda x, y: x)]]')
        msg=r'indices must be integers ama slices, sio str;'
        check('[[1, 2] [f"{x}"]]')
        check('[[1, 2] [f"x={x}"]]')
        check('[[1, 2] ["abc"]]')
        msg=r'indices must be integers ama slices, not'
        check('[[1, 2] [b"abc"]]')
        check('[[1, 2] [12.3]]')
        check('[[1, 2] [12.3j]]')
        check('[[1, 2] [Tupu]]')
        check('[[1, 2] [...]]')

        ukijumuisha warnings.catch_warnings():
            warnings.simplefilter('error', SyntaxWarning)
            compile('[(lambda x, y: x) (3, 4)]', '<testcase>', 'exec')
            compile('[[1, 2] [i]]', '<testcase>', 'exec')
            compile('[[1, 2] [0]]', '<testcase>', 'exec')
            compile('[[1, 2] [Kweli]]', '<testcase>', 'exec')
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
        # The testing here ni fairly incomplete.
        # Test cases should include: commas ukijumuisha 1 na 2 colons
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
        kundi B: pita
        kundi B2(): pita
        kundi C1(B): pita
        kundi C2(B): pita
        kundi D(C1, C2, B): pita
        kundi C:
            eleza meth1(self): pita
            eleza meth2(self, arg): pita
            eleza meth3(self, a1, a2): pita

        # decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
        # decorators: decorator+
        # decorated: decorators (classeleza | funcdef)
        eleza class_decorator(x): rudisha x
        @class_decorator
        kundi G: pita

    eleza test_dictcomps(self):
        # dictorsetmaker: ( (test ':' test (comp_kila |
        #                                   (',' test ':' test)* [','])) |
        #                   (test (comp_kila | (',' test)* [','])) )
        nums = [1, 2, 3]
        self.assertEqual({i:i+1 kila i kwenye nums}, {1: 2, 2: 3, 3: 4})

    eleza test_listcomps(self):
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
            rudisha [0 < x < 3 kila x kwenye l ikiwa x > 2]

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

    eleza test_genexps(self):
        # generator expression tests
        g = ([x kila x kwenye range(10)] kila x kwenye range(1))
        self.assertEqual(next(g), [x kila x kwenye range(10)])
        jaribu:
            next(g)
            self.fail('should produce StopIteration exception')
        tatizo StopIteration:
            pita

        a = 1
        jaribu:
            g = (a kila d kwenye a)
            next(g)
            self.fail('should produce TypeError')
        tatizo TypeError:
            pita

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

    eleza test_comprehension_specials(self):
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
                pita

        ukijumuisha manager():
            pita
        ukijumuisha manager() kama x:
            pita
        ukijumuisha manager() kama (x, y):
            pita
        ukijumuisha manager(), manager():
            pita
        ukijumuisha manager() kama x, manager() kama y:
            pita
        ukijumuisha manager() kama x, manager():
            pita

    eleza test_if_else_expr(self):
        # Test ifelse expressions kwenye various cases
        eleza _checkeval(msg, ret):
            "helper to check that evaluation of expressions ni done correctly"
            andika(msg)
            rudisha ret

        # the next line ni sio allowed anymore
        #self.assertEqual([ x() kila x kwenye lambda: Kweli, lambda: Uongo ikiwa x() ], [Kweli])
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
        self.assertEqual((sio 5 ikiwa 1 isipokua 1), Uongo)
        self.assertEqual((sio 5 ikiwa 0 isipokua 1), 1)
        self.assertEqual((6 + 1 ikiwa 1 isipokua 2), 7)
        self.assertEqual((6 - 1 ikiwa 1 isipokua 2), 5)
        self.assertEqual((6 * 2 ikiwa 1 isipokua 4), 12)
        self.assertEqual((6 / 2 ikiwa 1 isipokua 3), 3)
        self.assertEqual((6 < 4 ikiwa 0 isipokua 2), 2)

    eleza test_paren_evaluation(self):
        self.assertEqual(16 // (4 // 2), 8)
        self.assertEqual((16 // 4) // 2, 2)
        self.assertEqual(16 // 4 // 2, 2)
        x = 2
        y = 3
        self.assertKweli(Uongo ni (x ni y))
        self.assertUongo((Uongo ni x) ni y)
        self.assertUongo(Uongo ni x ni y)

    eleza test_matrix_mul(self):
        # This ni sio intended to be a comprehensive test, rather just to be few
        # samples of the @ operator kwenye test_grammar.py.
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
                pita
            ikiwa 1:
                await someobj()

        self.assertEqual(test.__name__, 'test')
        self.assertKweli(bool(test.__code__.co_flags & inspect.CO_COROUTINE))

        eleza decorator(func):
            setattr(func, '_marked', Kweli)
            rudisha func

        @decorator
        async eleza test2():
            rudisha 22
        self.assertKweli(test2._marked)
        self.assertEqual(test2.__name__, 'test2')
        self.assertKweli(bool(test2.__code__.co_flags & inspect.CO_COROUTINE))

    eleza test_async_for(self):
        kundi Done(Exception): pita

        kundi AIter:
            eleza __aiter__(self):
                rudisha self
            async eleza __anext__(self):
                ashiria StopAsyncIteration

        async eleza foo():
            async kila i kwenye AIter():
                pita
            async kila i, j kwenye AIter():
                pita
            async kila i kwenye AIter():
                pita
            isipokua:
                pita
            ashiria Done

        ukijumuisha self.assertRaises(Done):
            foo().send(Tupu)

    eleza test_async_with(self):
        kundi Done(Exception): pita

        kundi manager:
            async eleza __aenter__(self):
                rudisha (1, 2)
            async eleza __aexit__(self, *exc):
                rudisha Uongo

        async eleza foo():
            async ukijumuisha manager():
                pita
            async ukijumuisha manager() kama x:
                pita
            async ukijumuisha manager() kama (x, y):
                pita
            async ukijumuisha manager(), manager():
                pita
            async ukijumuisha manager() kama x, manager() kama y:
                pita
            async ukijumuisha manager() kama x, manager():
                pita
            ashiria Done

        ukijumuisha self.assertRaises(Done):
            foo().send(Tupu)


ikiwa __name__ == '__main__':
    unittest.main()
