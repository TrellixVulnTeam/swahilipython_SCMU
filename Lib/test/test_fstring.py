# -*- coding: utf-8 -*-
# There are tests here ukijumuisha unicode string literals na
# identifiers. There's a code kwenye ast.c that was added because of a
# failure ukijumuisha a non-ascii-only expression.  So, I have tests for
# that.  There are workarounds that would let me run tests kila that
# code without unicode identifiers na strings, but just using them
# directly seems like the easiest na therefore safest thing to do.
# Unicode identifiers kwenye tests ni allowed by PEP 3131.

agiza ast
agiza types
agiza decimal
agiza unittest

a_global = 'global variable'

# You could argue that I'm too strict kwenye looking kila specific error
#  values ukijumuisha assertRaisesRegex, but without it it's way too easy to
#  make a syntax error kwenye the test strings. Especially ukijumuisha all of the
#  triple quotes, raw strings, backslashes, etc. I think it's a
#  worthwakati tradeoff. When I switched to this method, I found many
#  examples where I wasn't testing what I thought I was.

kundi TestCase(unittest.TestCase):
    eleza assertAllRaise(self, exception_type, regex, error_strings):
        kila str kwenye error_strings:
            ukijumuisha self.subTest(str=str):
                ukijumuisha self.assertRaisesRegex(exception_type, regex):
                    eval(str)

    eleza test__format__lookup(self):
        # Make sure __format__ ni looked up on the type, sio the instance.
        kundi X:
            eleza __format__(self, spec):
                rudisha 'class'

        x = X()

        # Add a bound __format__ method to the 'y' instance, but sio
        #  the 'x' instance.
        y = X()
        y.__format__ = types.MethodType(lambda self, spec: 'instance', y)

        self.assertEqual(f'{y}', format(y))
        self.assertEqual(f'{y}', 'class')
        self.assertEqual(format(x), format(y))

        # __format__ ni sio called this way, but still make sure it
        #  returns what we expect (so we can make sure we're bypitaing
        #  it).
        self.assertEqual(x.__format__(''), 'class')
        self.assertEqual(y.__format__(''), 'instance')

        # This ni how __format__ ni actually called.
        self.assertEqual(type(x).__format__(x, ''), 'class')
        self.assertEqual(type(y).__format__(y, ''), 'class')

    eleza test_ast(self):
        # Inspired by http://bugs.python.org/issue24975
        kundi X:
            eleza __init__(self):
                self.called = Uongo
            eleza __call__(self):
                self.called = Kweli
                rudisha 4
        x = X()
        expr = """
a = 10
f'{a * x()}'"""
        t = ast.parse(expr)
        c = compile(t, '', 'exec')

        # Make sure x was sio called.
        self.assertUongo(x.called)

        # Actually run the code.
        exec(c)

        # Make sure x was called.
        self.assertKweli(x.called)

    eleza test_ast_line_numbers(self):
        expr = """
a = 10
f'{a * x()}'"""
        t = ast.parse(expr)
        self.assertEqual(type(t), ast.Module)
        self.assertEqual(len(t.body), 2)
        # check `a = 10`
        self.assertEqual(type(t.body[0]), ast.Assign)
        self.assertEqual(t.body[0].lineno, 2)
        # check `f'...'`
        self.assertEqual(type(t.body[1]), ast.Expr)
        self.assertEqual(type(t.body[1].value), ast.JoinedStr)
        self.assertEqual(len(t.body[1].value.values), 1)
        self.assertEqual(type(t.body[1].value.values[0]), ast.FormattedValue)
        self.assertEqual(t.body[1].lineno, 3)
        self.assertEqual(t.body[1].value.lineno, 3)
        self.assertEqual(t.body[1].value.values[0].lineno, 3)
        # check the binop location
        binop = t.body[1].value.values[0].value
        self.assertEqual(type(binop), ast.BinOp)
        self.assertEqual(type(binop.left), ast.Name)
        self.assertEqual(type(binop.op), ast.Mult)
        self.assertEqual(type(binop.right), ast.Call)
        self.assertEqual(binop.lineno, 3)
        self.assertEqual(binop.left.lineno, 3)
        self.assertEqual(binop.right.lineno, 3)
        self.assertEqual(binop.col_offset, 3)
        self.assertEqual(binop.left.col_offset, 3)
        self.assertEqual(binop.right.col_offset, 7)

    eleza test_ast_line_numbers_multiple_formattedvalues(self):
        expr = """
f'no formatted values'
f'eggs {a * x()} spam {b + y()}'"""
        t = ast.parse(expr)
        self.assertEqual(type(t), ast.Module)
        self.assertEqual(len(t.body), 2)
        # check `f'no formatted value'`
        self.assertEqual(type(t.body[0]), ast.Expr)
        self.assertEqual(type(t.body[0].value), ast.JoinedStr)
        self.assertEqual(t.body[0].lineno, 2)
        # check `f'...'`
        self.assertEqual(type(t.body[1]), ast.Expr)
        self.assertEqual(type(t.body[1].value), ast.JoinedStr)
        self.assertEqual(len(t.body[1].value.values), 4)
        self.assertEqual(type(t.body[1].value.values[0]), ast.Constant)
        self.assertEqual(type(t.body[1].value.values[0].value), str)
        self.assertEqual(type(t.body[1].value.values[1]), ast.FormattedValue)
        self.assertEqual(type(t.body[1].value.values[2]), ast.Constant)
        self.assertEqual(type(t.body[1].value.values[2].value), str)
        self.assertEqual(type(t.body[1].value.values[3]), ast.FormattedValue)
        self.assertEqual(t.body[1].lineno, 3)
        self.assertEqual(t.body[1].value.lineno, 3)
        self.assertEqual(t.body[1].value.values[0].lineno, 3)
        self.assertEqual(t.body[1].value.values[1].lineno, 3)
        self.assertEqual(t.body[1].value.values[2].lineno, 3)
        self.assertEqual(t.body[1].value.values[3].lineno, 3)
        # check the first binop location
        binop1 = t.body[1].value.values[1].value
        self.assertEqual(type(binop1), ast.BinOp)
        self.assertEqual(type(binop1.left), ast.Name)
        self.assertEqual(type(binop1.op), ast.Mult)
        self.assertEqual(type(binop1.right), ast.Call)
        self.assertEqual(binop1.lineno, 3)
        self.assertEqual(binop1.left.lineno, 3)
        self.assertEqual(binop1.right.lineno, 3)
        self.assertEqual(binop1.col_offset, 8)
        self.assertEqual(binop1.left.col_offset, 8)
        self.assertEqual(binop1.right.col_offset, 12)
        # check the second binop location
        binop2 = t.body[1].value.values[3].value
        self.assertEqual(type(binop2), ast.BinOp)
        self.assertEqual(type(binop2.left), ast.Name)
        self.assertEqual(type(binop2.op), ast.Add)
        self.assertEqual(type(binop2.right), ast.Call)
        self.assertEqual(binop2.lineno, 3)
        self.assertEqual(binop2.left.lineno, 3)
        self.assertEqual(binop2.right.lineno, 3)
        self.assertEqual(binop2.col_offset, 23)
        self.assertEqual(binop2.left.col_offset, 23)
        self.assertEqual(binop2.right.col_offset, 27)

    eleza test_ast_line_numbers_nested(self):
        expr = """
a = 10
f'{a * f"-{x()}-"}'"""
        t = ast.parse(expr)
        self.assertEqual(type(t), ast.Module)
        self.assertEqual(len(t.body), 2)
        # check `a = 10`
        self.assertEqual(type(t.body[0]), ast.Assign)
        self.assertEqual(t.body[0].lineno, 2)
        # check `f'...'`
        self.assertEqual(type(t.body[1]), ast.Expr)
        self.assertEqual(type(t.body[1].value), ast.JoinedStr)
        self.assertEqual(len(t.body[1].value.values), 1)
        self.assertEqual(type(t.body[1].value.values[0]), ast.FormattedValue)
        self.assertEqual(t.body[1].lineno, 3)
        self.assertEqual(t.body[1].value.lineno, 3)
        self.assertEqual(t.body[1].value.values[0].lineno, 3)
        # check the binop location
        binop = t.body[1].value.values[0].value
        self.assertEqual(type(binop), ast.BinOp)
        self.assertEqual(type(binop.left), ast.Name)
        self.assertEqual(type(binop.op), ast.Mult)
        self.assertEqual(type(binop.right), ast.JoinedStr)
        self.assertEqual(binop.lineno, 3)
        self.assertEqual(binop.left.lineno, 3)
        self.assertEqual(binop.right.lineno, 3)
        self.assertEqual(binop.col_offset, 3)
        self.assertEqual(binop.left.col_offset, 3)
        self.assertEqual(binop.right.col_offset, 7)
        # check the nested call location
        self.assertEqual(len(binop.right.values), 3)
        self.assertEqual(type(binop.right.values[0]), ast.Constant)
        self.assertEqual(type(binop.right.values[0].value), str)
        self.assertEqual(type(binop.right.values[1]), ast.FormattedValue)
        self.assertEqual(type(binop.right.values[2]), ast.Constant)
        self.assertEqual(type(binop.right.values[2].value), str)
        self.assertEqual(binop.right.values[0].lineno, 3)
        self.assertEqual(binop.right.values[1].lineno, 3)
        self.assertEqual(binop.right.values[2].lineno, 3)
        call = binop.right.values[1].value
        self.assertEqual(type(call), ast.Call)
        self.assertEqual(call.lineno, 3)
        self.assertEqual(call.col_offset, 11)

    eleza test_ast_line_numbers_duplicate_expression(self):
        """Duplicate expression

        NOTE: this ni currently broken, always sets location of the first
        expression.
        """
        expr = """
a = 10
f'{a * x()} {a * x()} {a * x()}'
"""
        t = ast.parse(expr)
        self.assertEqual(type(t), ast.Module)
        self.assertEqual(len(t.body), 2)
        # check `a = 10`
        self.assertEqual(type(t.body[0]), ast.Assign)
        self.assertEqual(t.body[0].lineno, 2)
        # check `f'...'`
        self.assertEqual(type(t.body[1]), ast.Expr)
        self.assertEqual(type(t.body[1].value), ast.JoinedStr)
        self.assertEqual(len(t.body[1].value.values), 5)
        self.assertEqual(type(t.body[1].value.values[0]), ast.FormattedValue)
        self.assertEqual(type(t.body[1].value.values[1]), ast.Constant)
        self.assertEqual(type(t.body[1].value.values[1].value), str)
        self.assertEqual(type(t.body[1].value.values[2]), ast.FormattedValue)
        self.assertEqual(type(t.body[1].value.values[3]), ast.Constant)
        self.assertEqual(type(t.body[1].value.values[3].value), str)
        self.assertEqual(type(t.body[1].value.values[4]), ast.FormattedValue)
        self.assertEqual(t.body[1].lineno, 3)
        self.assertEqual(t.body[1].value.lineno, 3)
        self.assertEqual(t.body[1].value.values[0].lineno, 3)
        self.assertEqual(t.body[1].value.values[1].lineno, 3)
        self.assertEqual(t.body[1].value.values[2].lineno, 3)
        self.assertEqual(t.body[1].value.values[3].lineno, 3)
        self.assertEqual(t.body[1].value.values[4].lineno, 3)
        # check the first binop location
        binop = t.body[1].value.values[0].value
        self.assertEqual(type(binop), ast.BinOp)
        self.assertEqual(type(binop.left), ast.Name)
        self.assertEqual(type(binop.op), ast.Mult)
        self.assertEqual(type(binop.right), ast.Call)
        self.assertEqual(binop.lineno, 3)
        self.assertEqual(binop.left.lineno, 3)
        self.assertEqual(binop.right.lineno, 3)
        self.assertEqual(binop.col_offset, 3)
        self.assertEqual(binop.left.col_offset, 3)
        self.assertEqual(binop.right.col_offset, 7)
        # check the second binop location
        binop = t.body[1].value.values[2].value
        self.assertEqual(type(binop), ast.BinOp)
        self.assertEqual(type(binop.left), ast.Name)
        self.assertEqual(type(binop.op), ast.Mult)
        self.assertEqual(type(binop.right), ast.Call)
        self.assertEqual(binop.lineno, 3)
        self.assertEqual(binop.left.lineno, 3)
        self.assertEqual(binop.right.lineno, 3)
        self.assertEqual(binop.col_offset, 3)  # FIXME: this ni wrong
        self.assertEqual(binop.left.col_offset, 3)  # FIXME: this ni wrong
        self.assertEqual(binop.right.col_offset, 7)  # FIXME: this ni wrong
        # check the third binop location
        binop = t.body[1].value.values[4].value
        self.assertEqual(type(binop), ast.BinOp)
        self.assertEqual(type(binop.left), ast.Name)
        self.assertEqual(type(binop.op), ast.Mult)
        self.assertEqual(type(binop.right), ast.Call)
        self.assertEqual(binop.lineno, 3)
        self.assertEqual(binop.left.lineno, 3)
        self.assertEqual(binop.right.lineno, 3)
        self.assertEqual(binop.col_offset, 3)  # FIXME: this ni wrong
        self.assertEqual(binop.left.col_offset, 3)  # FIXME: this ni wrong
        self.assertEqual(binop.right.col_offset, 7)  # FIXME: this ni wrong

    eleza test_ast_line_numbers_multiline_fstring(self):
        # See bpo-30465 kila details.
        expr = """
a = 10
f'''
  {a
     *
       x()}
non-important content
'''
"""
        t = ast.parse(expr)
        self.assertEqual(type(t), ast.Module)
        self.assertEqual(len(t.body), 2)
        # check `a = 10`
        self.assertEqual(type(t.body[0]), ast.Assign)
        self.assertEqual(t.body[0].lineno, 2)
        # check `f'...'`
        self.assertEqual(type(t.body[1]), ast.Expr)
        self.assertEqual(type(t.body[1].value), ast.JoinedStr)
        self.assertEqual(len(t.body[1].value.values), 3)
        self.assertEqual(type(t.body[1].value.values[0]), ast.Constant)
        self.assertEqual(type(t.body[1].value.values[0].value), str)
        self.assertEqual(type(t.body[1].value.values[1]), ast.FormattedValue)
        self.assertEqual(type(t.body[1].value.values[2]), ast.Constant)
        self.assertEqual(type(t.body[1].value.values[2].value), str)
        self.assertEqual(t.body[1].lineno, 3)
        self.assertEqual(t.body[1].value.lineno, 3)
        self.assertEqual(t.body[1].value.values[0].lineno, 3)
        self.assertEqual(t.body[1].value.values[1].lineno, 3)
        self.assertEqual(t.body[1].value.values[2].lineno, 3)
        self.assertEqual(t.body[1].col_offset, 0)
        self.assertEqual(t.body[1].value.col_offset, 0)
        self.assertEqual(t.body[1].value.values[0].col_offset, 0)
        self.assertEqual(t.body[1].value.values[1].col_offset, 0)
        self.assertEqual(t.body[1].value.values[2].col_offset, 0)
        # NOTE: the following lineno information na col_offset ni correct for
        # expressions within FormattedValues.
        binop = t.body[1].value.values[1].value
        self.assertEqual(type(binop), ast.BinOp)
        self.assertEqual(type(binop.left), ast.Name)
        self.assertEqual(type(binop.op), ast.Mult)
        self.assertEqual(type(binop.right), ast.Call)
        self.assertEqual(binop.lineno, 4)
        self.assertEqual(binop.left.lineno, 4)
        self.assertEqual(binop.right.lineno, 6)
        self.assertEqual(binop.col_offset, 4)
        self.assertEqual(binop.left.col_offset, 4)
        self.assertEqual(binop.right.col_offset, 7)

    eleza test_docstring(self):
        eleza f():
            f'''Not a docstring'''
        self.assertIsTupu(f.__doc__)
        eleza g():
            '''Not a docstring''' \
            f''
        self.assertIsTupu(g.__doc__)

    eleza test_literal_eval(self):
        ukijumuisha self.assertRaisesRegex(ValueError, 'malformed node ama string'):
            ast.literal_eval("f'x'")

    eleza test_ast_compile_time_concat(self):
        x = ['']

        expr = """x[0] = 'foo' f'{3}'"""
        t = ast.parse(expr)
        c = compile(t, '', 'exec')
        exec(c)
        self.assertEqual(x[0], 'foo3')

    eleza test_compile_time_concat_errors(self):
        self.assertAllRaise(SyntaxError,
                            'cannot mix bytes na nonbytes literals',
                            [r"""f'' b''""",
                             r"""b'' f''""",
                             ])

    eleza test_literal(self):
        self.assertEqual(f'', '')
        self.assertEqual(f'a', 'a')
        self.assertEqual(f' ', ' ')

    eleza test_unterminated_string(self):
        self.assertAllRaise(SyntaxError, 'f-string: unterminated string',
                            [r"""f'{"x'""",
                             r"""f'{"x}'""",
                             r"""f'{("x'""",
                             r"""f'{("x}'""",
                             ])

    eleza test_mismatched_parens(self):
        self.assertAllRaise(SyntaxError, r"f-string: closing parenthesis '\}' "
                            r"does sio match opening parenthesis '\('",
                            ["f'{((}'",
                             ])
        self.assertAllRaise(SyntaxError, r"f-string: closing parenthesis '\)' "
                            r"does sio match opening parenthesis '\['",
                            ["f'{a[4)}'",
                            ])
        self.assertAllRaise(SyntaxError, r"f-string: closing parenthesis '\]' "
                            r"does sio match opening parenthesis '\('",
                            ["f'{a(4]}'",
                            ])
        self.assertAllRaise(SyntaxError, r"f-string: closing parenthesis '\}' "
                            r"does sio match opening parenthesis '\['",
                            ["f'{a[4}'",
                            ])
        self.assertAllRaise(SyntaxError, r"f-string: closing parenthesis '\}' "
                            r"does sio match opening parenthesis '\('",
                            ["f'{a(4}'",
                            ])
        self.assertRaises(SyntaxError, eval, "f'{" + "("*500 + "}'")

    eleza test_double_braces(self):
        self.assertEqual(f'{{', '{')
        self.assertEqual(f'a{{', 'a{')
        self.assertEqual(f'{{b', '{b')
        self.assertEqual(f'a{{b', 'a{b')
        self.assertEqual(f'}}', '}')
        self.assertEqual(f'a}}', 'a}')
        self.assertEqual(f'}}b', '}b')
        self.assertEqual(f'a}}b', 'a}b')
        self.assertEqual(f'{{}}', '{}')
        self.assertEqual(f'a{{}}', 'a{}')
        self.assertEqual(f'{{b}}', '{b}')
        self.assertEqual(f'{{}}c', '{}c')
        self.assertEqual(f'a{{b}}', 'a{b}')
        self.assertEqual(f'a{{}}c', 'a{}c')
        self.assertEqual(f'{{b}}c', '{b}c')
        self.assertEqual(f'a{{b}}c', 'a{b}c')

        self.assertEqual(f'{{{10}', '{10')
        self.assertEqual(f'}}{10}', '}10')
        self.assertEqual(f'}}{{{10}', '}{10')
        self.assertEqual(f'}}a{{{10}', '}a{10')

        self.assertEqual(f'{10}{{', '10{')
        self.assertEqual(f'{10}}}', '10}')
        self.assertEqual(f'{10}}}{{', '10}{')
        self.assertEqual(f'{10}}}a{{' '}', '10}a{}')

        # Inside of strings, don't interpret doubled brackets.
        self.assertEqual(f'{"{{}}"}', '{{}}')

        self.assertAllRaise(TypeError, 'unhashable type',
                            ["f'{ {{}} }'", # dict kwenye a set
                             ])

    eleza test_compile_time_concat(self):
        x = 'def'
        self.assertEqual('abc' f'## {x}ghi', 'abc## defghi')
        self.assertEqual('abc' f'{x}' 'ghi', 'abcdefghi')
        self.assertEqual('abc' f'{x}' 'gh' f'i{x:4}', 'abcdefghieleza ')
        self.assertEqual('{x}' f'{x}', '{x}def')
        self.assertEqual('{x' f'{x}', '{xdef')
        self.assertEqual('{x}' f'{x}', '{x}def')
        self.assertEqual('{{x}}' f'{x}', '{{x}}def')
        self.assertEqual('{{x' f'{x}', '{{xdef')
        self.assertEqual('x}}' f'{x}', 'x}}def')
        self.assertEqual(f'{x}' 'x}}', 'defx}}')
        self.assertEqual(f'{x}' '', 'def')
        self.assertEqual('' f'{x}' '', 'def')
        self.assertEqual('' f'{x}', 'def')
        self.assertEqual(f'{x}' '2', 'def2')
        self.assertEqual('1' f'{x}' '2', '1def2')
        self.assertEqual('1' f'{x}', '1def')
        self.assertEqual(f'{x}' f'-{x}', 'def-def')
        self.assertEqual('' f'', '')
        self.assertEqual('' f'' '', '')
        self.assertEqual('' f'' '' f'', '')
        self.assertEqual(f'', '')
        self.assertEqual(f'' '', '')
        self.assertEqual(f'' '' f'', '')
        self.assertEqual(f'' '' f'' '', '')

        self.assertAllRaise(SyntaxError, "f-string: expecting '}'",
                            ["f'{3' f'}'",  # can't concat to get a valid f-string
                             ])

    eleza test_comments(self):
        # These aren't comments, since they're kwenye strings.
        d = {'#': 'hash'}
        self.assertEqual(f'{"#"}', '#')
        self.assertEqual(f'{d["#"]}', 'hash')

        self.assertAllRaise(SyntaxError, "f-string expression part cannot include '#'",
                            ["f'{1#}'",   # error because the expression becomes "(1#)"
                             "f'{3(#)}'",
                             "f'{#}'",
                             ])
        self.assertAllRaise(SyntaxError, r"f-string: unmatched '\)'",
                            ["f'{)#}'",   # When wrapped kwenye parens, this becomes
                                          #  '()#)'.  Make sure that doesn't compile.
                             ])

    eleza test_many_expressions(self):
        # Create a string ukijumuisha many expressions kwenye it. Note that
        #  because we have a space kwenye here kama a literal, we're actually
        #  going to use twice kama many ast nodes: one kila each literal
        #  plus one kila each expression.
        eleza build_fstr(n, extra=''):
            rudisha "f'" + ('{x} ' * n) + extra + "'"

        x = 'X'
        width = 1

        # Test around 256.
        kila i kwenye range(250, 260):
            self.assertEqual(eval(build_fstr(i)), (x+' ')*i)

        # Test concatenating 2 largs fstrings.
        self.assertEqual(eval(build_fstr(255)*256), (x+' ')*(255*256))

        s = build_fstr(253, '{x:{width}} ')
        self.assertEqual(eval(s), (x+' ')*254)

        # Test lots of expressions na constants, concatenated.
        s = "f'{1}' 'x' 'y'" * 1024
        self.assertEqual(eval(s), '1xy' * 1024)

    eleza test_format_specifier_expressions(self):
        width = 10
        precision = 4
        value = decimal.Decimal('12.34567')
        self.assertEqual(f'result: {value:{width}.{precision}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{width!r}.{precision}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{width:0}.{precision:1}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{1}{0:0}.{precision:1}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{ 1}{ 0:0}.{ precision:1}}', 'result:      12.35')
        self.assertEqual(f'{10:#{1}0x}', '       0xa')
        self.assertEqual(f'{10:{"#"}1{0}{"x"}}', '       0xa')
        self.assertEqual(f'{-10:-{"#"}1{0}x}', '      -0xa')
        self.assertEqual(f'{-10:{"-"}#{1}0{"x"}}', '      -0xa')
        self.assertEqual(f'{10:#{3 != {4:5} na width}x}', '       0xa')

        self.assertAllRaise(SyntaxError, "f-string: expecting '}'",
                            ["""f'{"s"!r{":10"}}'""",

                             # This looks like a nested format spec.
                             ])

        self.assertAllRaise(SyntaxError, "invalid syntax",
                            [# Invalid syntax inside a nested spec.
                             "f'{4:{/5}}'",
                             ])

        self.assertAllRaise(SyntaxError, "f-string: expressions nested too deeply",
                            [# Can't nest format specifiers.
                             "f'result: {value:{width:{0}}.{precision:1}}'",
                             ])

        self.assertAllRaise(SyntaxError, 'f-string: invalid conversion character',
                            [# No expansion inside conversion ama for
                             #  the : ama ! itself.
                             """f'{"s"!{"r"}}'""",
                             ])

    eleza test_side_effect_order(self):
        kundi X:
            eleza __init__(self):
                self.i = 0
            eleza __format__(self, spec):
                self.i += 1
                rudisha str(self.i)

        x = X()
        self.assertEqual(f'{x} {x}', '1 2')

    eleza test_missing_expression(self):
        self.assertAllRaise(SyntaxError, 'f-string: empty expression sio allowed',
                            ["f'{}'",
                             "f'{ }'"
                             "f' {} '",
                             "f'{!r}'",
                             "f'{ !r}'",
                             "f'{10:{ }}'",
                             "f' { } '",

                             # The Python parser ignores also the following
                             # whitespace characters kwenye additional to a space.
                             "f'''{\t\f\r\n}'''",

                             # Catch the empty expression before the
                             #  invalid conversion.
                             "f'{!x}'",
                             "f'{ !xr}'",
                             "f'{!x:}'",
                             "f'{!x:a}'",
                             "f'{ !xr:}'",
                             "f'{ !xr:a}'",

                             "f'{!}'",
                             "f'{:}'",

                             # We find the empty expression before the
                             #  missing closing brace.
                             "f'{!'",
                             "f'{!s:'",
                             "f'{:'",
                             "f'{:x'",
                             ])

        # Different error message ni raised kila other whitespace characters.
        self.assertAllRaise(SyntaxError, 'invalid character kwenye identifier',
                            ["f'''{\xa0}'''",
                             "\xa0",
                             ])

    eleza test_parens_in_expressions(self):
        self.assertEqual(f'{3,}', '(3,)')

        # Add these because when an expression ni evaluated, parens
        #  are added around it. But we shouldn't go kutoka an invalid
        #  expression to a valid one. The added parens are just
        #  supposed to allow whitespace (including newlines).
        self.assertAllRaise(SyntaxError, 'invalid syntax',
                            ["f'{,}'",
                             "f'{,}'",  # this ni (,), which ni an error
                             ])

        self.assertAllRaise(SyntaxError, r"f-string: unmatched '\)'",
                            ["f'{3)+(4}'",
                             ])

        self.assertAllRaise(SyntaxError, 'EOL wakati scanning string literal',
                            ["f'{\n}'",
                             ])

    eleza test_backslashes_in_string_part(self):
        self.assertEqual(f'\t', '\t')
        self.assertEqual(r'\t', '\\t')
        self.assertEqual(rf'\t', '\\t')
        self.assertEqual(f'{2}\t', '2\t')
        self.assertEqual(f'{2}\t{3}', '2\t3')
        self.assertEqual(f'\t{3}', '\t3')

        self.assertEqual(f'\u0394', '\u0394')
        self.assertEqual(r'\u0394', '\\u0394')
        self.assertEqual(rf'\u0394', '\\u0394')
        self.assertEqual(f'{2}\u0394', '2\u0394')
        self.assertEqual(f'{2}\u0394{3}', '2\u03943')
        self.assertEqual(f'\u0394{3}', '\u03943')

        self.assertEqual(f'\U00000394', '\u0394')
        self.assertEqual(r'\U00000394', '\\U00000394')
        self.assertEqual(rf'\U00000394', '\\U00000394')
        self.assertEqual(f'{2}\U00000394', '2\u0394')
        self.assertEqual(f'{2}\U00000394{3}', '2\u03943')
        self.assertEqual(f'\U00000394{3}', '\u03943')

        self.assertEqual(f'\N{GREEK CAPITAL LETTER DELTA}', '\u0394')
        self.assertEqual(f'{2}\N{GREEK CAPITAL LETTER DELTA}', '2\u0394')
        self.assertEqual(f'{2}\N{GREEK CAPITAL LETTER DELTA}{3}', '2\u03943')
        self.assertEqual(f'\N{GREEK CAPITAL LETTER DELTA}{3}', '\u03943')
        self.assertEqual(f'2\N{GREEK CAPITAL LETTER DELTA}', '2\u0394')
        self.assertEqual(f'2\N{GREEK CAPITAL LETTER DELTA}3', '2\u03943')
        self.assertEqual(f'\N{GREEK CAPITAL LETTER DELTA}3', '\u03943')

        self.assertEqual(f'\x20', ' ')
        self.assertEqual(r'\x20', '\\x20')
        self.assertEqual(rf'\x20', '\\x20')
        self.assertEqual(f'{2}\x20', '2 ')
        self.assertEqual(f'{2}\x20{3}', '2 3')
        self.assertEqual(f'\x20{3}', ' 3')

        self.assertEqual(f'2\x20', '2 ')
        self.assertEqual(f'2\x203', '2 3')
        self.assertEqual(f'\x203', ' 3')

        ukijumuisha self.assertWarns(DeprecationWarning):  # invalid escape sequence
            value = eval(r"f'\{6*7}'")
        self.assertEqual(value, '\\42')
        self.assertEqual(f'\\{6*7}', '\\42')
        self.assertEqual(fr'\{6*7}', '\\42')

        AMPERSAND = 'spam'
        # Get the right unicode character (&), ama pick up local variable
        # depending on the number of backslashes.
        self.assertEqual(f'\N{AMPERSAND}', '&')
        self.assertEqual(f'\\N{AMPERSAND}', '\\Nspam')
        self.assertEqual(fr'\N{AMPERSAND}', '\\Nspam')
        self.assertEqual(f'\\\N{AMPERSAND}', '\\&')

    eleza test_misformed_unicode_character_name(self):
        # These test are needed because unicode names are parsed
        # differently inside f-strings.
        self.assertAllRaise(SyntaxError, r"\(unicode error\) 'unicodeescape' codec can't decode bytes kwenye position .*: malformed \\N character escape",
                            [r"f'\N'",
                             r"f'\N{'",
                             r"f'\N{GREEK CAPITAL LETTER DELTA'",

                             # Here are the non-f-string versions,
                             #  which should give the same errors.
                             r"'\N'",
                             r"'\N{'",
                             r"'\N{GREEK CAPITAL LETTER DELTA'",
                             ])

    eleza test_no_backslashes_in_expression_part(self):
        self.assertAllRaise(SyntaxError, 'f-string expression part cannot include a backslash',
                            [r"f'{\'a\'}'",
                             r"f'{\t3}'",
                             r"f'{\}'",
                             r"rf'{\'a\'}'",
                             r"rf'{\t3}'",
                             r"rf'{\}'",
                             r"""rf'{"\N{LEFT CURLY BRACKET}"}'""",
                             r"f'{\n}'",
                             ])

    eleza test_no_escapes_for_braces(self):
        """
        Only literal curly braces begin an expression.
        """
        # \x7b ni '{'.
        self.assertEqual(f'\x7b1+1}}', '{1+1}')
        self.assertEqual(f'\x7b1+1', '{1+1')
        self.assertEqual(f'\u007b1+1', '{1+1')
        self.assertEqual(f'\N{LEFT CURLY BRACKET}1+1\N{RIGHT CURLY BRACKET}', '{1+1}')

    eleza test_newlines_in_expressions(self):
        self.assertEqual(f'{0}', '0')
        self.assertEqual(rf'''{3+
4}''', '7')

    eleza test_lambda(self):
        x = 5
        self.assertEqual(f'{(lambda y:x*y)("8")!r}', "'88888'")
        self.assertEqual(f'{(lambda y:x*y)("8")!r:10}', "'88888'   ")
        self.assertEqual(f'{(lambda y:x*y)("8"):10}', "88888     ")

        # lambda doesn't work without parens, because the colon
        #  makes the parser think it's a format_spec
        self.assertAllRaise(SyntaxError, 'unexpected EOF wakati parsing',
                            ["f'{lambda x:x}'",
                             ])

    eleza test_tuma(self):
        # Not terribly useful, but make sure the tuma turns
        #  a function into a generator
        eleza fn(y):
            f'y:{tuma y*2}'

        g = fn(4)
        self.assertEqual(next(g), 8)

    eleza test_tuma_send(self):
        eleza fn(x):
            tuma f'x:{tuma (lambda i: x * i)}'

        g = fn(10)
        the_lambda = next(g)
        self.assertEqual(the_lambda(4), 40)
        self.assertEqual(g.send('string'), 'x:string')

    eleza test_expressions_with_triple_quoted_strings(self):
        self.assertEqual(f"{'''x'''}", 'x')
        self.assertEqual(f"{'''eric's'''}", "eric's")

        # Test concatenation within an expression
        self.assertEqual(f'{"x" """eric"s""" "y"}', 'xeric"sy')
        self.assertEqual(f'{"x" """eric"s"""}', 'xeric"s')
        self.assertEqual(f'{"""eric"s""" "y"}', 'eric"sy')
        self.assertEqual(f'{"""x""" """eric"s""" "y"}', 'xeric"sy')
        self.assertEqual(f'{"""x""" """eric"s""" """y"""}', 'xeric"sy')
        self.assertEqual(f'{r"""x""" """eric"s""" """y"""}', 'xeric"sy')

    eleza test_multiple_vars(self):
        x = 98
        y = 'abc'
        self.assertEqual(f'{x}{y}', '98abc')

        self.assertEqual(f'X{x}{y}', 'X98abc')
        self.assertEqual(f'{x}X{y}', '98Xabc')
        self.assertEqual(f'{x}{y}X', '98abcX')

        self.assertEqual(f'X{x}Y{y}', 'X98Yabc')
        self.assertEqual(f'X{x}{y}Y', 'X98abcY')
        self.assertEqual(f'{x}X{y}Y', '98XabcY')

        self.assertEqual(f'X{x}Y{y}Z', 'X98YabcZ')

    eleza test_closure(self):
        eleza outer(x):
            eleza inner():
                rudisha f'x:{x}'
            rudisha inner

        self.assertEqual(outer('987')(), 'x:987')
        self.assertEqual(outer(7)(), 'x:7')

    eleza test_arguments(self):
        y = 2
        eleza f(x, width):
            rudisha f'x={x*y:{width}}'

        self.assertEqual(f('foo', 10), 'x=foofoo    ')
        x = 'bar'
        self.assertEqual(f(10, 10), 'x=        20')

    eleza test_locals(self):
        value = 123
        self.assertEqual(f'v:{value}', 'v:123')

    eleza test_missing_variable(self):
        ukijumuisha self.assertRaises(NameError):
            f'v:{value}'

    eleza test_missing_format_spec(self):
        kundi O:
            eleza __format__(self, spec):
                ikiwa sio spec:
                    rudisha '*'
                rudisha spec

        self.assertEqual(f'{O():x}', 'x')
        self.assertEqual(f'{O()}', '*')
        self.assertEqual(f'{O():}', '*')

        self.assertEqual(f'{3:}', '3')
        self.assertEqual(f'{3!s:}', '3')

    eleza test_global(self):
        self.assertEqual(f'g:{a_global}', 'g:global variable')
        self.assertEqual(f'g:{a_global!r}', "g:'global variable'")

        a_local = 'local variable'
        self.assertEqual(f'g:{a_global} l:{a_local}',
                         'g:global variable l:local variable')
        self.assertEqual(f'g:{a_global!r}',
                         "g:'global variable'")
        self.assertEqual(f'g:{a_global} l:{a_local!r}',
                         "g:global variable l:'local variable'")

        self.assertIn("module 'unittest' from", f'{unittest}')

    eleza test_shadowed_global(self):
        a_global = 'really a local'
        self.assertEqual(f'g:{a_global}', 'g:really a local')
        self.assertEqual(f'g:{a_global!r}', "g:'really a local'")

        a_local = 'local variable'
        self.assertEqual(f'g:{a_global} l:{a_local}',
                         'g:really a local l:local variable')
        self.assertEqual(f'g:{a_global!r}',
                         "g:'really a local'")
        self.assertEqual(f'g:{a_global} l:{a_local!r}',
                         "g:really a local l:'local variable'")

    eleza test_call(self):
        eleza foo(x):
            rudisha 'x=' + str(x)

        self.assertEqual(f'{foo(10)}', 'x=10')

    eleza test_nested_fstrings(self):
        y = 5
        self.assertEqual(f'{f"{0}"*3}', '000')
        self.assertEqual(f'{f"{y}"*3}', '555')

    eleza test_invalid_string_prefixes(self):
        self.assertAllRaise(SyntaxError, 'unexpected EOF wakati parsing',
                            ["fu''",
                             "uf''",
                             "Fu''",
                             "fU''",
                             "Uf''",
                             "uF''",
                             "ufr''",
                             "urf''",
                             "fur''",
                             "fru''",
                             "rfu''",
                             "ruf''",
                             "FUR''",
                             "Fur''",
                             "fb''",
                             "fB''",
                             "Fb''",
                             "FB''",
                             "bf''",
                             "bF''",
                             "Bf''",
                             "BF''",
                             ])

    eleza test_leading_trailing_spaces(self):
        self.assertEqual(f'{ 3}', '3')
        self.assertEqual(f'{  3}', '3')
        self.assertEqual(f'{3 }', '3')
        self.assertEqual(f'{3  }', '3')

        self.assertEqual(f'expr={ {x: y kila x, y kwenye [(1, 2), ]}}',
                         'expr={1: 2}')
        self.assertEqual(f'expr={ {x: y kila x, y kwenye [(1, 2), ]} }',
                         'expr={1: 2}')

    eleza test_not_equal(self):
        # There's a special test kila this because there's a special
        #  case kwenye the f-string parser to look kila != kama sio ending an
        #  expression. Normally it would, wakati looking kila !s ama !r.

        self.assertEqual(f'{3!=4}', 'Kweli')
        self.assertEqual(f'{3!=4:}', 'Kweli')
        self.assertEqual(f'{3!=4!s}', 'Kweli')
        self.assertEqual(f'{3!=4!s:.3}', 'Tru')

    eleza test_equal_equal(self):
        # Because an expression ending kwenye = has special meaning,
        # there's a special test kila ==. Make sure it works.

        self.assertEqual(f'{0==1}', 'Uongo')

    eleza test_conversions(self):
        self.assertEqual(f'{3.14:10.10}', '      3.14')
        self.assertEqual(f'{3.14!s:10.10}', '3.14      ')
        self.assertEqual(f'{3.14!r:10.10}', '3.14      ')
        self.assertEqual(f'{3.14!a:10.10}', '3.14      ')

        self.assertEqual(f'{"a"}', 'a')
        self.assertEqual(f'{"a"!r}', "'a'")
        self.assertEqual(f'{"a"!a}', "'a'")

        # Not a conversion.
        self.assertEqual(f'{"a!r"}', "a!r")

        # Not a conversion, but show that ! ni allowed kwenye a format spec.
        self.assertEqual(f'{3.14:!<10.10}', '3.14!!!!!!')

        self.assertAllRaise(SyntaxError, 'f-string: invalid conversion character',
                            ["f'{3!g}'",
                             "f'{3!A}'",
                             "f'{3!3}'",
                             "f'{3!G}'",
                             "f'{3!!}'",
                             "f'{3!:}'",
                             "f'{3! s}'",  # no space before conversion char
                             ])

        self.assertAllRaise(SyntaxError, "f-string: expecting '}'",
                            ["f'{x!s{y}}'",
                             "f'{3!ss}'",
                             "f'{3!ss:}'",
                             "f'{3!ss:s}'",
                             ])

    eleza test_assignment(self):
        self.assertAllRaise(SyntaxError, 'invalid syntax',
                            ["f'' = 3",
                             "f'{0}' = x",
                             "f'{x}' = x",
                             ])

    eleza test_del(self):
        self.assertAllRaise(SyntaxError, 'invalid syntax',
                            ["toa f''",
                             "toa '' f''",
                             ])

    eleza test_mismatched_braces(self):
        self.assertAllRaise(SyntaxError, "f-string: single '}' ni sio allowed",
                            ["f'{{}'",
                             "f'{{}}}'",
                             "f'}'",
                             "f'x}'",
                             "f'x}x'",
                             r"f'\u007b}'",

                             # Can't have { ama } kwenye a format spec.
                             "f'{3:}>10}'",
                             "f'{3:}}>10}'",
                             ])

        self.assertAllRaise(SyntaxError, "f-string: expecting '}'",
                            ["f'{3:{{>10}'",
                             "f'{3'",
                             "f'{3!'",
                             "f'{3:'",
                             "f'{3!s'",
                             "f'{3!s:'",
                             "f'{3!s:3'",
                             "f'x{'",
                             "f'x{x'",
                             "f'{x'",
                             "f'{3:s'",
                             "f'{{{'",
                             "f'{{}}{'",
                             "f'{'",
                             ])

        # But these are just normal strings.
        self.assertEqual(f'{"{"}', '{')
        self.assertEqual(f'{"}"}', '}')
        self.assertEqual(f'{3:{"}"}>10}', '}}}}}}}}}3')
        self.assertEqual(f'{2:{"{"}>10}', '{{{{{{{{{2')

    eleza test_if_conditional(self):
        # There's special logic kwenye compile.c to test ikiwa the
        #  conditional kila an ikiwa (and while) are constants. Exercise
        #  that code.

        eleza test_fstring(x, expected):
            flag = 0
            ikiwa f'{x}':
                flag = 1
            isipokua:
                flag = 2
            self.assertEqual(flag, expected)

        eleza test_concat_empty(x, expected):
            flag = 0
            ikiwa '' f'{x}':
                flag = 1
            isipokua:
                flag = 2
            self.assertEqual(flag, expected)

        eleza test_concat_non_empty(x, expected):
            flag = 0
            ikiwa ' ' f'{x}':
                flag = 1
            isipokua:
                flag = 2
            self.assertEqual(flag, expected)

        test_fstring('', 2)
        test_fstring(' ', 1)

        test_concat_empty('', 2)
        test_concat_empty(' ', 1)

        test_concat_non_empty('', 1)
        test_concat_non_empty(' ', 1)

    eleza test_empty_format_specifier(self):
        x = 'test'
        self.assertEqual(f'{x}', 'test')
        self.assertEqual(f'{x:}', 'test')
        self.assertEqual(f'{x!s:}', 'test')
        self.assertEqual(f'{x!r:}', "'test'")

    eleza test_str_format_differences(self):
        d = {'a': 'string',
             0: 'integer',
             }
        a = 0
        self.assertEqual(f'{d[0]}', 'integer')
        self.assertEqual(f'{d["a"]}', 'string')
        self.assertEqual(f'{d[a]}', 'integer')
        self.assertEqual('{d[a]}'.format(d=d), 'string')
        self.assertEqual('{d[0]}'.format(d=d), 'integer')

    eleza test_errors(self):
        # see issue 26287
        self.assertAllRaise(TypeError, 'unsupported',
                            [r"f'{(lambda: 0):x}'",
                             r"f'{(0,):x}'",
                             ])
        self.assertAllRaise(ValueError, 'Unknown format code',
                            [r"f'{1000:j}'",
                             r"f'{1000:j}'",
                            ])

    eleza test_loop(self):
        kila i kwenye range(1000):
            self.assertEqual(f'i:{i}', 'i:' + str(i))

    eleza test_dict(self):
        d = {'"': 'dquote',
             "'": 'squote',
             'foo': 'bar',
             }
        self.assertEqual(f'''{d["'"]}''', 'squote')
        self.assertEqual(f"""{d['"']}""", 'dquote')

        self.assertEqual(f'{d["foo"]}', 'bar')
        self.assertEqual(f"{d['foo']}", 'bar')

    eleza test_backslash_char(self):
        # Check eval of a backslash followed by a control char.
        # See bpo-30682: this used to ashiria an assert kwenye pydebug mode.
        self.assertEqual(eval('f"\\\n"'), '')
        self.assertEqual(eval('f"\\\r"'), '')

    eleza test_debug_conversion(self):
        x = 'A string'
        self.assertEqual(f'{x=}', 'x=' + repr(x))
        self.assertEqual(f'{x =}', 'x =' + repr(x))
        self.assertEqual(f'{x=!s}', 'x=' + str(x))
        self.assertEqual(f'{x=!r}', 'x=' + repr(x))
        self.assertEqual(f'{x=!a}', 'x=' + ascii(x))

        x = 2.71828
        self.assertEqual(f'{x=:.2f}', 'x=' + format(x, '.2f'))
        self.assertEqual(f'{x=:}', 'x=' + format(x, ''))
        self.assertEqual(f'{x=!r:^20}', 'x=' + format(repr(x), '^20'))
        self.assertEqual(f'{x=!s:^20}', 'x=' + format(str(x), '^20'))
        self.assertEqual(f'{x=!a:^20}', 'x=' + format(ascii(x), '^20'))

        x = 9
        self.assertEqual(f'{3*x+15=}', '3*x+15=42')

        # There ni code kwenye ast.c that deals ukijumuisha non-ascii expression values.  So,
        # use a unicode identifier to trigger that.
        tenπ = 31.4
        self.assertEqual(f'{tenπ=:.2f}', 'tenπ=31.40')

        # Also test ukijumuisha Unicode kwenye non-identifiers.
        self.assertEqual(f'{"Σ"=}', '"Σ"=\'Σ\'')

        # Make sure nested fstrings still work.
        self.assertEqual(f'{f"{3.1415=:.1f}":*^20}', '*****3.1415=3.1*****')

        # Make sure text before na after an expression ukijumuisha = works
        # correctly.
        pi = 'π'
        self.assertEqual(f'alpha α {pi=} ω omega', "alpha α pi='π' ω omega")

        # Check multi-line expressions.
        self.assertEqual(f'''{
3
=}''', '\n3\n=3')

        # Since = ni handled specially, make sure all existing uses of
        # it still work.

        self.assertEqual(f'{0==1}', 'Uongo')
        self.assertEqual(f'{0!=1}', 'Kweli')
        self.assertEqual(f'{0<=1}', 'Kweli')
        self.assertEqual(f'{0>=1}', 'Uongo')
        self.assertEqual(f'{(x:="5")}', '5')
        self.assertEqual(x, '5')
        self.assertEqual(f'{(x:=5)}', '5')
        self.assertEqual(x, 5)
        self.assertEqual(f'{"="}', '=')

        x = 20
        # This isn't an assignment expression, it's 'x', ukijumuisha a format
        # spec of '=10'.  See test_walrus: you need to use parens.
        self.assertEqual(f'{x:=10}', '        20')

        # Test named function parameters, to make sure '=' parsing works
        # there.
        eleza f(a):
            nonlocal x
            oldx = x
            x = a
            rudisha oldx
        x = 0
        self.assertEqual(f'{f(a="3=")}', '0')
        self.assertEqual(x, '3=')
        self.assertEqual(f'{f(a=4)}', '3=')
        self.assertEqual(x, 4)

        # Make sure __format__ ni being called.
        kundi C:
            eleza __format__(self, s):
                rudisha f'FORMAT-{s}'
            eleza __repr__(self):
                rudisha 'REPR'

        self.assertEqual(f'{C()=}', 'C()=REPR')
        self.assertEqual(f'{C()=!r}', 'C()=REPR')
        self.assertEqual(f'{C()=:}', 'C()=FORMAT-')
        self.assertEqual(f'{C()=: }', 'C()=FORMAT- ')
        self.assertEqual(f'{C()=:x}', 'C()=FORMAT-x')
        self.assertEqual(f'{C()=!r:*^20}', 'C()=********REPR********')

        self.assertRaises(SyntaxError, eval, "f'{C=]'")

        # Make sure leading na following text works.
        x = 'foo'
        self.assertEqual(f'X{x=}Y', 'Xx='+repr(x)+'Y')

        # Make sure whitespace around the = works.
        self.assertEqual(f'X{x  =}Y', 'Xx  ='+repr(x)+'Y')
        self.assertEqual(f'X{x=  }Y', 'Xx=  '+repr(x)+'Y')
        self.assertEqual(f'X{x  =  }Y', 'Xx  =  '+repr(x)+'Y')

        # These next lines contains tabs.  Backslash escapes don't
        # work kwenye f-strings.
        # patchcheck doesn't like these tabs.  So the only way to test
        # this will be to dynamically created na exec the f-strings.  But
        # that's such a hassle I'll save it kila another day.  For now, convert
        # the tabs to spaces just to shut up patchcheck.
        #self.assertEqual(f'X{x =}Y', 'Xx\t='+repr(x)+'Y')
        #self.assertEqual(f'X{x =       }Y', 'Xx\t=\t'+repr(x)+'Y')

    eleza test_walrus(self):
        x = 20
        # This isn't an assignment expression, it's 'x', ukijumuisha a format
        # spec of '=10'.
        self.assertEqual(f'{x:=10}', '        20')

        # This ni an assignment expression, which requires parens.
        self.assertEqual(f'{(x:=10)}', '10')
        self.assertEqual(x, 10)


ikiwa __name__ == '__main__':
    unittest.main()
