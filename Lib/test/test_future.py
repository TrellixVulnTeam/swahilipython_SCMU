# Test various flavors of legal na illegal future statements

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
        ukijumuisha support.CleanImport('future_test1'):
            kutoka test agiza future_test1
            self.assertEqual(future_test1.result, 6)

    eleza test_future2(self):
        ukijumuisha support.CleanImport('future_test2'):
            kutoka test agiza future_test2
            self.assertEqual(future_test2.result, 6)

    eleza test_future3(self):
        ukijumuisha support.CleanImport('test_future3'):
            kutoka test agiza test_future3

    eleza test_badfuture3(self):
        ukijumuisha self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future3
        self.check_syntax_error(cm.exception, "badsyntax_future3", 3)

    eleza test_badfuture4(self):
        ukijumuisha self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future4
        self.check_syntax_error(cm.exception, "badsyntax_future4", 3)

    eleza test_badfuture5(self):
        ukijumuisha self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future5
        self.check_syntax_error(cm.exception, "badsyntax_future5", 4)

    eleza test_badfuture6(self):
        ukijumuisha self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future6
        self.check_syntax_error(cm.exception, "badsyntax_future6", 3)

    eleza test_badfuture7(self):
        ukijumuisha self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future7
        self.check_syntax_error(cm.exception, "badsyntax_future7", 3, 53)

    eleza test_badfuture8(self):
        ukijumuisha self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future8
        self.check_syntax_error(cm.exception, "badsyntax_future8", 3)

    eleza test_badfuture9(self):
        ukijumuisha self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future9
        self.check_syntax_error(cm.exception, "badsyntax_future9", 3)

    eleza test_badfuture10(self):
        ukijumuisha self.assertRaises(SyntaxError) as cm:
            kutoka test agiza badsyntax_future10
        self.check_syntax_error(cm.exception, "badsyntax_future10", 3)

    eleza test_parserhack(self):
        # test that the parser.c::future_hack function works as expected
        # Note: although this test must pass, it's sio testing the original
        #       bug as of 2.6 since the ukijumuisha statement ni sio optional and
        #       the parser hack disabled. If a new keyword ni introduced in
        #       2.6, change this to refer to the new future import.
        jaribu:
            exec("kutoka __future__ agiza print_function; print 0")
        except SyntaxError:
            pass
        isipokua:
            self.fail("syntax error didn't occur")

        jaribu:
            exec("kutoka __future__ agiza (print_function); print 0")
        except SyntaxError:
            pass
        isipokua:
            self.fail("syntax error didn't occur")

    eleza test_multiple_features(self):
        ukijumuisha support.CleanImport("test.test_future5"):
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
        eleza g(arg: {ann}) -> Tupu:
            ...
        var: {ann}
        var2: {ann} = Tupu
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
        self, annotation, expected=Tupu, drop_parens=Uongo, is_tuple=Uongo,
    ):
        actual = self.getActual(annotation)
        ikiwa expected ni Tupu:
            expected = annotation ikiwa sio is_tuple isipokua annotation[1:-1]
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
        eq('Tupu')
        eq('Kweli')
        eq('Uongo')
        eq('1')
        eq('1.0')
        eq('1j')
        eq('Kweli ama Uongo')
        eq('Kweli ama Uongo ama Tupu')
        eq('Kweli na Uongo')
        eq('Kweli na Uongo na Tupu')
        eq('Name1 na Name2 ama Name3')
        eq('Name1 na (Name2 ama Name3)')
        eq('Name1 ama Name2 na Name3')
        eq('(Name1 ama Name2) na Name3')
        eq('Name1 na Name2 ama Name3 na Name4')
        eq('Name1 ama Name2 na Name3 ama Name4')
        eq('a + b + (c + d)')
        eq('a * b * (c * d)')
        eq('(a ** b) ** c ** d')
        eq('v1 << 2')
        eq('1 >> v2')
        eq('1 % finished')
        eq('1 + v2 - v3 * 4 ^ 5 ** v6 / 7 // 8')
        eq('not great')
        eq('not sio great')
        eq('~great')
        eq('+value')
        eq('++value')
        eq('-1')
        eq('~int na sio v1 ^ 123 + v2 | Kweli')
        eq('a + (not b)')
        eq('lambda: Tupu')
        eq('lambda arg: Tupu')
        eq('lambda a=Kweli: a')
        eq('lambda a, b, c=Kweli: a')
        eq("lambda a, b, c=Kweli, *, d=1 << v2, e='str': a")
        eq("lambda a, b, c=Kweli, *vararg, d, e='str', **kwargs: a + b")
        eq("lambda a, /, b, c=Kweli, *vararg, d, e='str', **kwargs: a + b")
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
        eq('1 ikiwa Kweli isipokua 2')
        eq('str ama Tupu ikiwa int ama Kweli isipokua str ama bytes ama Tupu')
        eq('str ama Tupu ikiwa (1 ikiwa Kweli isipokua 2) isipokua str ama bytes ama Tupu')
        eq("0 ikiwa sio x isipokua 1 ikiwa x > 0 isipokua -1")
        eq("(1 ikiwa x > 0 isipokua -1) ikiwa x isipokua 0")
        eq("{'2.7': dead, '3.7': long_live ama die_hard}")
        eq("{'2.7': dead, '3.7': long_live ama die_hard, **{'3.6': verygood}}")
        eq("{**a, **b, **c}")
        eq("{'2.7', '3.6', '3.7', '3.8', '3.9', '4.0' ikiwa gilectomy isipokua '3.10'}")
        eq("{*a, *b, *c}")
        eq("({'a': 'b'}, Kweli ama Uongo, +value, 'string', b'bytes') ama Tupu")
        eq("()")
        eq("(a,)")
        eq("(a, b)")
        eq("(a, b, c)")
        eq("(*a, *b, *c)")
        eq("[]")
        eq("[1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ama A, 11 ama B, 12 ama C]")
        eq("[*a, *b, *c]")
        eq("{i kila i kwenye (1, 2, 3)}")
        eq("{i ** 2 kila i kwenye (1, 2, 3)}")
        eq("{i ** 2 kila i, _ kwenye ((1, 'a'), (2, 'b'), (3, 'c'))}")
        eq("{i ** 2 + j kila i kwenye (1, 2, 3) kila j kwenye (1, 2, 3)}")
        eq("[i kila i kwenye (1, 2, 3)]")
        eq("[i ** 2 kila i kwenye (1, 2, 3)]")
        eq("[i ** 2 kila i, _ kwenye ((1, 'a'), (2, 'b'), (3, 'c'))]")
        eq("[i ** 2 + j kila i kwenye (1, 2, 3) kila j kwenye (1, 2, 3)]")
        eq("(i kila i kwenye (1, 2, 3))")
        eq("(i ** 2 kila i kwenye (1, 2, 3))")
        eq("(i ** 2 kila i, _ kwenye ((1, 'a'), (2, 'b'), (3, 'c')))")
        eq("(i ** 2 + j kila i kwenye (1, 2, 3) kila j kwenye (1, 2, 3))")
        eq("{i: 0 kila i kwenye (1, 2, 3)}")
        eq("{i: j kila i, j kwenye ((1, 'a'), (2, 'b'), (3, 'c'))}")
        eq("[(x, y) kila x, y kwenye (a, b)]")
        eq("[(x,) kila x, kwenye (a,)]")
        eq("Python3 > Python2 > COBOL")
        eq("Life ni Life")
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
        eq("slice[(x kila x kwenye a)]")
        eq('str ama Tupu ikiwa sys.version_info[0] > (3,) isipokua str ama bytes ama Tupu')
        eq("f'f-string without formatted values ni just a string'")
        eq("f'{{NOT a formatted value}}'")
        eq("f'some f-string ukijumuisha {a} {few():.2f} {formatted.values!r}'")
        eq('''f"{f'{nested} inner'} outer"''')
        eq("f'space between opening braces: { {a kila a kwenye (1, 2, 3)}}'")
        eq("f'{(lambda x: x)}'")
        eq("f'{(Tupu ikiwa a isipokua lambda x: x)}'")
        eq("f'{x}'")
        eq("f'{x!r}'")
        eq("f'{x!a}'")
        eq('(tuma kutoka outside_of_generator)')
        eq('(yield)')
        eq('(tuma a + b)')
        eq('await some.complicated[0].call(with_args=Kweli ama 1 ni sio 1)')
        eq('[x kila x kwenye (a ikiwa b isipokua c)]')
        eq('[x kila x kwenye a ikiwa (b ikiwa c isipokua d)]')
        eq('f(x kila x kwenye a)')
        eq('f(1, (x kila x kwenye a))')
        eq('f((x kila x kwenye a), 2)')
        eq('(((a)))', 'a')
        eq('(((a, b)))', '(a, b)')
        eq("(x:=10)")
        eq("f'{(x:=10):=10}'")

    eleza test_fstring_debug_annotations(self):
        # f-strings ukijumuisha '=' don't round trip very well, so set the expected
        # result explicitely.
        self.assertAnnotationEqual("f'{x=!r}'", expected="f'x={x!r}'")
        self.assertAnnotationEqual("f'{x=:}'", expected="f'x={x:}'")
        self.assertAnnotationEqual("f'{x=:.2f}'", expected="f'x={x:.2f}'")
        self.assertAnnotationEqual("f'{x=!r}'", expected="f'x={x!r}'")
        self.assertAnnotationEqual("f'{x=!a}'", expected="f'x={x!a}'")
        self.assertAnnotationEqual("f'{x=!s:*^20}'", expected="f'x={x!s:*^20}'")


ikiwa __name__ == "__main__":
    unittest.main()
