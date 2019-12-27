# Test various flavors of legal and illegal future statements

agiza unittest
kutoka test agiza support
kutoka textwrap agiza dedent
agiza os
agiza re

rx = re.compile(r'\((\S+).py, line (\d+)')

eleza get_error_location(msg):
    mo = rx.search(str(msg))
    rudisha mo.group(1, 2)

kundi FutureTest(unittest.TestCase):

    eleza check_syntax_error(self, err, basename, lineno, offset=1):
        self.assertIn('%s.py, line %d' % (basename, lineno), str(err))
        self.assertEqual(os.path.basename(err.filename), basename + '.py')
        self.assertEqual(err.lineno, lineno)
        self.assertEqual(err.offset, offset)

    eleza test_future1(self):
        with support.CleanImport('future_test1'):
            kutoka test agiza future_test1
            self.assertEqual(future_test1.result, 6)

    eleza test_future2(self):
        with support.CleanImport('future_test2'):
            kutoka test agiza future_test2
            self.assertEqual(future_test2.result, 6)

    eleza test_future3(self):
        with support.CleanImport('test_future3'):
            kutoka test agiza test_future3

    eleza test_badfuture3(self):
        with self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future3
        self.check_syntax_error(cm.exception, "badsyntax_future3", 3)

    eleza test_badfuture4(self):
        with self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future4
        self.check_syntax_error(cm.exception, "badsyntax_future4", 3)

    eleza test_badfuture5(self):
        with self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future5
        self.check_syntax_error(cm.exception, "badsyntax_future5", 4)

    eleza test_badfuture6(self):
        with self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future6
        self.check_syntax_error(cm.exception, "badsyntax_future6", 3)

    eleza test_badfuture7(self):
        with self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future7
        self.check_syntax_error(cm.exception, "badsyntax_future7", 3, 53)

    eleza test_badfuture8(self):
        with self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future8
        self.check_syntax_error(cm.exception, "badsyntax_future8", 3)

    eleza test_badfuture9(self):
        with self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future9
        self.check_syntax_error(cm.exception, "badsyntax_future9", 3)

    eleza test_badfuture10(self):
        with self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future10
        self.check_syntax_error(cm.exception, "badsyntax_future10", 3)

    eleza test_parserhack(self):
        # test that the parser.c::future_hack function works as expected
        # Note: although this test must pass, it's not testing the original
        #       bug as of 2.6 since the with statement is not optional and
        #       the parser hack disabled. If a new keyword is introduced in
        #       2.6, change this to refer to the new future agiza.
        try:
            exec("kutoka __future__ agiza print_function; print 0")
        except SyntaxError:
            pass
        else:
            self.fail("syntax error didn't occur")

        try:
            exec("kutoka __future__ agiza (print_function); print 0")
        except SyntaxError:
            pass
        else:
            self.fail("syntax error didn't occur")

    eleza test_multiple_features(self):
        with support.CleanImport("test.test_future5"):
            kutoka test agiza test_future5

    eleza test_unicode_literals_exec(self):
        scope = {}
        exec("kutoka __future__ agiza unicode_literals; x = ''", {}, scope)
        self.assertIsInstance(scope["x"], str)

kundi AnnotationsFutureTestCase(unittest.TestCase):
    template = dedent(
        """
        kutoka __future__ agiza annotations
        eleza f() -> {ann}:
            ...
        eleza g(arg: {ann}) -> None:
            ...
        var: {ann}
        var2: {ann} = None
        """
    )

    eleza getActual(self, annotation):
        scope = {}
        exec(self.template.format(ann=annotation), {}, scope)
        func_ret_ann = scope['f'].__annotations__['return']
        func_arg_ann = scope['g'].__annotations__['arg']
        var_ann1 = scope['__annotations__']['var']
        var_ann2 = scope['__annotations__']['var2']
        self.assertEqual(func_ret_ann, func_arg_ann)
        self.assertEqual(func_ret_ann, var_ann1)
        self.assertEqual(func_ret_ann, var_ann2)
        rudisha func_ret_ann

    eleza assertAnnotationEqual(
        self, annotation, expected=None, drop_parens=False, is_tuple=False,
    ):
        actual = self.getActual(annotation)
        ikiwa expected is None:
            expected = annotation ikiwa not is_tuple else annotation[1:-1]
        ikiwa drop_parens:
            self.assertNotEqual(actual, expected)
            actual = actual.replace("(", "").replace(")", "")

        self.assertEqual(actual, expected)

    eleza test_annotations(self):
        eq = self.assertAnnotationEqual
        eq('...')
        eq("'some_string'")
        eq("b'\\xa3'")
        eq('Name')
        eq('None')
        eq('True')
        eq('False')
        eq('1')
        eq('1.0')
        eq('1j')
        eq('True or False')
        eq('True or False or None')
        eq('True and False')
        eq('True and False and None')
        eq('Name1 and Name2 or Name3')
        eq('Name1 and (Name2 or Name3)')
        eq('Name1 or Name2 and Name3')
        eq('(Name1 or Name2) and Name3')
        eq('Name1 and Name2 or Name3 and Name4')
        eq('Name1 or Name2 and Name3 or Name4')
        eq('a + b + (c + d)')
        eq('a * b * (c * d)')
        eq('(a ** b) ** c ** d')
        eq('v1 << 2')
        eq('1 >> v2')
        eq('1 % finished')
        eq('1 + v2 - v3 * 4 ^ 5 ** v6 / 7 // 8')
        eq('not great')
        eq('not not great')
        eq('~great')
        eq('+value')
        eq('++value')
        eq('-1')
        eq('~int and not v1 ^ 123 + v2 | True')
        eq('a + (not b)')
        eq('lambda: None')
        eq('lambda arg: None')
        eq('lambda a=True: a')
        eq('lambda a, b, c=True: a')
        eq("lambda a, b, c=True, *, d=1 << v2, e='str': a")
        eq("lambda a, b, c=True, *vararg, d, e='str', **kwargs: a + b")
        eq("lambda a, /, b, c=True, *vararg, d, e='str', **kwargs: a + b")
        eq('lambda x, /: x')
        eq('lambda x=1, /: x')
        eq('lambda x, /, y: x + y')
        eq('lambda x=1, /, y=2: x + y')
        eq('lambda x, /, y=1: x + y')
        eq('lambda x, /, y=1, *, z=3: x + y + z')
        eq('lambda x=1, /, y=2, *, z=3: x + y + z')
        eq('lambda x=1, /, y=2, *, z: x + y + z')
        eq('lambda x=1, y=2, z=3, /, w=4, *, l, l2: x + y + z + w + l + l2')
        eq('lambda x=1, y=2, z=3, /, w=4, *, l, l2, **kwargs: x + y + z + w + l + l2')
        eq('lambda x, /, y=1, *, z: x + y + z')
        eq('lambda x: lambda y: x + y')
        eq('1 ikiwa True else 2')
        eq('str or None ikiwa int or True else str or bytes or None')
        eq('str or None ikiwa (1 ikiwa True else 2) else str or bytes or None')
        eq("0 ikiwa not x else 1 ikiwa x > 0 else -1")
        eq("(1 ikiwa x > 0 else -1) ikiwa x else 0")
        eq("{'2.7': dead, '3.7': long_live or die_hard}")
        eq("{'2.7': dead, '3.7': long_live or die_hard, **{'3.6': verygood}}")
        eq("{**a, **b, **c}")
        eq("{'2.7', '3.6', '3.7', '3.8', '3.9', '4.0' ikiwa gilectomy else '3.10'}")
        eq("{*a, *b, *c}")
        eq("({'a': 'b'}, True or False, +value, 'string', b'bytes') or None")
        eq("()")
        eq("(a,)")
        eq("(a, b)")
        eq("(a, b, c)")
        eq("(*a, *b, *c)")
        eq("[]")
        eq("[1, 2, 3, 4, 5, 6, 7, 8, 9, 10 or A, 11 or B, 12 or C]")
        eq("[*a, *b, *c]")
        eq("{i for i in (1, 2, 3)}")
        eq("{i ** 2 for i in (1, 2, 3)}")
        eq("{i ** 2 for i, _ in ((1, 'a'), (2, 'b'), (3, 'c'))}")
        eq("{i ** 2 + j for i in (1, 2, 3) for j in (1, 2, 3)}")
        eq("[i for i in (1, 2, 3)]")
        eq("[i ** 2 for i in (1, 2, 3)]")
        eq("[i ** 2 for i, _ in ((1, 'a'), (2, 'b'), (3, 'c'))]")
        eq("[i ** 2 + j for i in (1, 2, 3) for j in (1, 2, 3)]")
        eq("(i for i in (1, 2, 3))")
        eq("(i ** 2 for i in (1, 2, 3))")
        eq("(i ** 2 for i, _ in ((1, 'a'), (2, 'b'), (3, 'c')))")
        eq("(i ** 2 + j for i in (1, 2, 3) for j in (1, 2, 3))")
        eq("{i: 0 for i in (1, 2, 3)}")
        eq("{i: j for i, j in ((1, 'a'), (2, 'b'), (3, 'c'))}")
        eq("[(x, y) for x, y in (a, b)]")
        eq("[(x,) for x, in (a,)]")
        eq("Python3 > Python2 > COBOL")
        eq("Life is Life")
        eq("call()")
        eq("call(arg)")
        eq("call(kwarg='hey')")
        eq("call(arg, kwarg='hey')")
        eq("call(arg, *args, another, kwarg='hey')")
        eq("call(arg, another, kwarg='hey', **kwargs, kwarg2='ho')")
        eq("lukasz.langa.pl")
        eq("call.me(maybe)")
        eq("1 .real")
        eq("1.0.real")
        eq("....__class__")
        eq("list[str]")
        eq("dict[str, int]")
        eq("set[str,]")
        eq("tuple[str, ...]")
        eq("tuple[str, int, float, dict[str, int]]")
        eq("slice[0]")
        eq("slice[0:1]")
        eq("slice[0:1:2]")
        eq("slice[:]")
        eq("slice[:-1]")
        eq("slice[1:]")
        eq("slice[::-1]")
        eq("slice[()]")
        eq("slice[a, b:c, d:e:f]")
        eq("slice[(x for x in a)]")
        eq('str or None ikiwa sys.version_info[0] > (3,) else str or bytes or None')
        eq("f'f-string without formatted values is just a string'")
        eq("f'{{NOT a formatted value}}'")
        eq("f'some f-string with {a} {few():.2f} {formatted.values!r}'")
        eq('''f"{f'{nested} inner'} outer"''')
        eq("f'space between opening braces: { {a for a in (1, 2, 3)}}'")
        eq("f'{(lambda x: x)}'")
        eq("f'{(None ikiwa a else lambda x: x)}'")
        eq("f'{x}'")
        eq("f'{x!r}'")
        eq("f'{x!a}'")
        eq('(yield kutoka outside_of_generator)')
        eq('(yield)')
        eq('(yield a + b)')
        eq('await some.complicated[0].call(with_args=True or 1 is not 1)')
        eq('[x for x in (a ikiwa b else c)]')
        eq('[x for x in a ikiwa (b ikiwa c else d)]')
        eq('f(x for x in a)')
        eq('f(1, (x for x in a))')
        eq('f((x for x in a), 2)')
        eq('(((a)))', 'a')
        eq('(((a, b)))', '(a, b)')
        eq("(x:=10)")
        eq("f'{(x:=10):=10}'")

    eleza test_fstring_debug_annotations(self):
        # f-strings with '=' don't round trip very well, so set the expected
        # result explicitely.
        self.assertAnnotationEqual("f'{x=!r}'", expected="f'x={x!r}'")
        self.assertAnnotationEqual("f'{x=:}'", expected="f'x={x:}'")
        self.assertAnnotationEqual("f'{x=:.2f}'", expected="f'x={x:.2f}'")
        self.assertAnnotationEqual("f'{x=!r}'", expected="f'x={x!r}'")
        self.assertAnnotationEqual("f'{x=!a}'", expected="f'x={x!a}'")
        self.assertAnnotationEqual("f'{x=!s:*^20}'", expected="f'x={x!s:*^20}'")


ikiwa __name__ == "__main__":
    unittest.main()
