agiza dis
agiza unittest

kutoka test.bytecode_helper agiza BytecodeTestCase


eleza count_instr_recursively(f, opname):
    count = 0
    kila instr kwenye dis.get_instructions(f):
        ikiwa instr.opname == opname:
            count += 1
    ikiwa hasattr(f, '__code__'):
        f = f.__code__
    kila c kwenye f.co_consts:
        ikiwa hasattr(c, 'co_code'):
            count += count_instr_recursively(c, opname)
    rudisha count


kundi TestTranforms(BytecodeTestCase):

    eleza check_jump_targets(self, code):
        instructions = list(dis.get_instructions(code))
        targets = {instr.offset: instr kila instr kwenye instructions}
        kila instr kwenye instructions:
            ikiwa 'JUMP_' haiko kwenye instr.opname:
                endelea
            tgt = targets[instr.argval]
            # jump to unconditional jump
            ikiwa tgt.opname kwenye ('JUMP_ABSOLUTE', 'JUMP_FORWARD'):
                self.fail(f'{instr.opname} at {instr.offset} '
                          f'jumps to {tgt.opname} at {tgt.offset}')
            # unconditional jump to RETURN_VALUE
            ikiwa (instr.opname kwenye ('JUMP_ABSOLUTE', 'JUMP_FORWARD') and
                tgt.opname == 'RETURN_VALUE'):
                self.fail(f'{instr.opname} at {instr.offset} '
                          f'jumps to {tgt.opname} at {tgt.offset}')
            # JUMP_IF_*_OR_POP jump to conditional jump
            ikiwa '_OR_POP' kwenye instr.opname na 'JUMP_IF_' kwenye tgt.opname:
                self.fail(f'{instr.opname} at {instr.offset} '
                          f'jumps to {tgt.opname} at {tgt.offset}')

    eleza check_lnotab(self, code):
        "Check that the lnotab byte offsets are sensible."
        code = dis._get_code_object(code)
        lnotab = list(dis.findlinestarts(code))
        # Don't bother checking ikiwa the line info ni sensible, because
        # most of the line info we can get at comes kutoka lnotab.
        min_bytecode = min(t[0] kila t kwenye lnotab)
        max_bytecode = max(t[0] kila t kwenye lnotab)
        self.assertGreaterEqual(min_bytecode, 0)
        self.assertLess(max_bytecode, len(code.co_code))
        # This could conceivably test more (and probably should, kama there
        # aren't very many tests of lnotab), ikiwa peepholer wasn't scheduled
        # to be replaced anyway.

    eleza test_unot(self):
        # UNARY_NOT POP_JUMP_IF_FALSE  -->  POP_JUMP_IF_TRUE'
        eleza unot(x):
            ikiwa sio x == 2:
                toa x
        self.assertNotInBytecode(unot, 'UNARY_NOT')
        self.assertNotInBytecode(unot, 'POP_JUMP_IF_FALSE')
        self.assertInBytecode(unot, 'POP_JUMP_IF_TRUE')
        self.check_lnotab(unot)

    eleza test_elim_inversion_of_is_or_in(self):
        kila line, cmp_op kwenye (
            ('not a ni b', 'is not',),
            ('not a kwenye b', 'not in',),
            ('not a ni sio b', 'is',),
            ('not a haiko kwenye b', 'in',),
            ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'COMPARE_OP', cmp_op)
            self.check_lnotab(code)

    eleza test_global_as_constant(self):
        # LOAD_GLOBAL Tupu/Kweli/Uongo  -->  LOAD_CONST Tupu/Kweli/Uongo
        eleza f():
            x = Tupu
            x = Tupu
            rudisha x
        eleza g():
            x = Kweli
            rudisha x
        eleza h():
            x = Uongo
            rudisha x

        kila func, elem kwenye ((f, Tupu), (g, Kweli), (h, Uongo)):
            self.assertNotInBytecode(func, 'LOAD_GLOBAL')
            self.assertInBytecode(func, 'LOAD_CONST', elem)
            self.check_lnotab(func)

        eleza f():
            'Adding a docstring made this test fail kwenye Py2.5.0'
            rudisha Tupu

        self.assertNotInBytecode(f, 'LOAD_GLOBAL')
        self.assertInBytecode(f, 'LOAD_CONST', Tupu)
        self.check_lnotab(f)

    eleza test_while_one(self):
        # Skip over:  LOAD_CONST trueconst  POP_JUMP_IF_FALSE xx
        eleza f():
            wakati 1:
                pita
            rudisha list
        kila elem kwenye ('LOAD_CONST', 'POP_JUMP_IF_FALSE'):
            self.assertNotInBytecode(f, elem)
        kila elem kwenye ('JUMP_ABSOLUTE',):
            self.assertInBytecode(f, elem)
        self.check_lnotab(f)

    eleza test_pack_unpack(self):
        kila line, elem kwenye (
            ('a, = a,', 'LOAD_CONST',),
            ('a, b = a, b', 'ROT_TWO',),
            ('a, b, c = a, b, c', 'ROT_THREE',),
            ):
            code = compile(line,'','single')
            self.assertInBytecode(code, elem)
            self.assertNotInBytecode(code, 'BUILD_TUPLE')
            self.assertNotInBytecode(code, 'UNPACK_TUPLE')
            self.check_lnotab(code)

    eleza test_folding_of_tuples_of_constants(self):
        kila line, elem kwenye (
            ('a = 1,2,3', (1, 2, 3)),
            ('("a","b","c")', ('a', 'b', 'c')),
            ('a,b,c = 1,2,3', (1, 2, 3)),
            ('(Tupu, 1, Tupu)', (Tupu, 1, Tupu)),
            ('((1, 2), 3, 4)', ((1, 2), 3, 4)),
            ):
            code = compile(line,'','single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            self.assertNotInBytecode(code, 'BUILD_TUPLE')
            self.check_lnotab(code)

        # Long tuples should be folded too.
        code = compile(repr(tuple(range(10000))),'','single')
        self.assertNotInBytecode(code, 'BUILD_TUPLE')
        # One LOAD_CONST kila the tuple, one kila the Tupu rudisha value
        load_consts = [instr kila instr kwenye dis.get_instructions(code)
                              ikiwa instr.opname == 'LOAD_CONST']
        self.assertEqual(len(load_consts), 2)
        self.check_lnotab(code)

        # Bug 1053819:  Tuple of constants misidentified when presented with:
        # . . . opcode_with_arg 100   unary_opcode   BUILD_TUPLE 1  . . .
        # The following would segfault upon compilation
        eleza crater():
            (~[
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
            ],)
        self.check_lnotab(crater)

    eleza test_folding_of_lists_of_constants(self):
        kila line, elem kwenye (
            # in/not kwenye constants with BUILD_LIST should be folded to a tuple:
            ('a kwenye [1,2,3]', (1, 2, 3)),
            ('a haiko kwenye ["a","b","c"]', ('a', 'b', 'c')),
            ('a kwenye [Tupu, 1, Tupu]', (Tupu, 1, Tupu)),
            ('a haiko kwenye [(1, 2), 3, 4]', ((1, 2), 3, 4)),
            ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            self.assertNotInBytecode(code, 'BUILD_LIST')
            self.check_lnotab(code)

    eleza test_folding_of_sets_of_constants(self):
        kila line, elem kwenye (
            # in/not kwenye constants with BUILD_SET should be folded to a frozenset:
            ('a kwenye {1,2,3}', frozenset({1, 2, 3})),
            ('a haiko kwenye {"a","b","c"}', frozenset({'a', 'c', 'b'})),
            ('a kwenye {Tupu, 1, Tupu}', frozenset({1, Tupu})),
            ('a haiko kwenye {(1, 2), 3, 4}', frozenset({(1, 2), 3, 4})),
            ('a kwenye {1, 2, 3, 3, 2, 1}', frozenset({1, 2, 3})),
            ):
            code = compile(line, '', 'single')
            self.assertNotInBytecode(code, 'BUILD_SET')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            self.check_lnotab(code)

        # Ensure that the resulting code actually works:
        eleza f(a):
            rudisha a kwenye {1, 2, 3}

        eleza g(a):
            rudisha a haiko kwenye {1, 2, 3}

        self.assertKweli(f(3))
        self.assertKweli(not f(4))
        self.check_lnotab(f)

        self.assertKweli(not g(3))
        self.assertKweli(g(4))
        self.check_lnotab(g)


    eleza test_folding_of_binops_on_constants(self):
        kila line, elem kwenye (
            ('a = 2+3+4', 9),                   # chained fold
            ('"@"*4', '@@@@'),                  # check string ops
            ('a="abc" + "def"', 'abcdef'),      # check string ops
            ('a = 3**4', 81),                   # binary power
            ('a = 3*4', 12),                    # binary multiply
            ('a = 13//4', 3),                   # binary floor divide
            ('a = 14%4', 2),                    # binary modulo
            ('a = 2+3', 5),                     # binary add
            ('a = 13-4', 9),                    # binary subtract
            ('a = (12,13)[1]', 13),             # binary subscr
            ('a = 13 << 2', 52),                # binary lshift
            ('a = 13 >> 2', 3),                 # binary rshift
            ('a = 13 & 7', 5),                  # binary and
            ('a = 13 ^ 7', 10),                 # binary xor
            ('a = 13 | 7', 15),                 # binary or
            ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            kila instr kwenye dis.get_instructions(code):
                self.assertUongo(instr.opname.startswith('BINARY_'))
            self.check_lnotab(code)

        # Verify that unfoldables are skipped
        code = compile('a=2+"b"', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', 2)
        self.assertInBytecode(code, 'LOAD_CONST', 'b')
        self.check_lnotab(code)

        # Verify that large sequences do sio result kutoka folding
        code = compile('a="x"*10000', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', 10000)
        self.assertNotIn("x"*10000, code.co_consts)
        self.check_lnotab(code)
        code = compile('a=1<<1000', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', 1000)
        self.assertNotIn(1<<1000, code.co_consts)
        self.check_lnotab(code)
        code = compile('a=2**1000', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', 1000)
        self.assertNotIn(2**1000, code.co_consts)
        self.check_lnotab(code)

    eleza test_binary_subscr_on_unicode(self):
        # valid code get optimized
        code = compile('"foo"[0]', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', 'f')
        self.assertNotInBytecode(code, 'BINARY_SUBSCR')
        self.check_lnotab(code)
        code = compile('"\u0061\uffff"[1]', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', '\uffff')
        self.assertNotInBytecode(code,'BINARY_SUBSCR')
        self.check_lnotab(code)

        # With PEP 393, non-BMP char get optimized
        code = compile('"\U00012345"[0]', '', 'single')
        self.assertInBytecode(code, 'LOAD_CONST', '\U00012345')
        self.assertNotInBytecode(code, 'BINARY_SUBSCR')
        self.check_lnotab(code)

        # invalid code doesn't get optimized
        # out of range
        code = compile('"fuu"[10]', '', 'single')
        self.assertInBytecode(code, 'BINARY_SUBSCR')
        self.check_lnotab(code)

    eleza test_folding_of_unaryops_on_constants(self):
        kila line, elem kwenye (
            ('-0.5', -0.5),                     # unary negative
            ('-0.0', -0.0),                     # -0.0
            ('-(1.0-1.0)', -0.0),               # -0.0 after folding
            ('-0', 0),                          # -0
            ('~-2', 1),                         # unary invert
            ('+1', 1),                          # unary positive
        ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            kila instr kwenye dis.get_instructions(code):
                self.assertUongo(instr.opname.startswith('UNARY_'))
            self.check_lnotab(code)

        # Check that -0.0 works after marshaling
        eleza negzero():
            rudisha -(1.0-1.0)

        kila instr kwenye dis.get_instructions(negzero):
            self.assertUongo(instr.opname.startswith('UNARY_'))
        self.check_lnotab(negzero)

        # Verify that unfoldables are skipped
        kila line, elem, opname kwenye (
            ('-"abc"', 'abc', 'UNARY_NEGATIVE'),
            ('~"abc"', 'abc', 'UNARY_INVERT'),
        ):
            code = compile(line, '', 'single')
            self.assertInBytecode(code, 'LOAD_CONST', elem)
            self.assertInBytecode(code, opname)
            self.check_lnotab(code)

    eleza test_elim_extra_rudisha(self):
        # RETURN LOAD_CONST Tupu RETURN  -->  RETURN
        eleza f(x):
            rudisha x
        self.assertNotInBytecode(f, 'LOAD_CONST', Tupu)
        rudishas = [instr kila instr kwenye dis.get_instructions(f)
                          ikiwa instr.opname == 'RETURN_VALUE']
        self.assertEqual(len(rudishas), 1)
        self.check_lnotab(f)

    eleza test_elim_jump_to_rudisha(self):
        # JUMP_FORWARD to RETURN -->  RETURN
        eleza f(cond, true_value, false_value):
            # Intentionally use two-line expression to test issue37213.
            rudisha (true_value ikiwa cond
                    else false_value)
        self.check_jump_targets(f)
        self.assertNotInBytecode(f, 'JUMP_FORWARD')
        self.assertNotInBytecode(f, 'JUMP_ABSOLUTE')
        rudishas = [instr kila instr kwenye dis.get_instructions(f)
                          ikiwa instr.opname == 'RETURN_VALUE']
        self.assertEqual(len(rudishas), 2)
        self.check_lnotab(f)

    eleza test_elim_jump_to_uncond_jump(self):
        # POP_JUMP_IF_FALSE to JUMP_FORWARD --> POP_JUMP_IF_FALSE to non-jump
        eleza f():
            ikiwa a:
                # Intentionally use two-line expression to test issue37213.
                ikiwa (c
                    ama d):
                    foo()
            isipokua:
                baz()
        self.check_jump_targets(f)
        self.check_lnotab(f)

    eleza test_elim_jump_to_uncond_jump2(self):
        # POP_JUMP_IF_FALSE to JUMP_ABSOLUTE --> POP_JUMP_IF_FALSE to non-jump
        eleza f():
            wakati a:
                # Intentionally use two-line expression to test issue37213.
                ikiwa (c
                    ama d):
                    a = foo()
        self.check_jump_targets(f)
        self.check_lnotab(f)

    eleza test_elim_jump_to_uncond_jump3(self):
        # Intentionally use two-line expressions to test issue37213.
        # JUMP_IF_FALSE_OR_POP to JUMP_IF_FALSE_OR_POP --> JUMP_IF_FALSE_OR_POP to non-jump
        eleza f(a, b, c):
            rudisha ((a na b)
                    na c)
        self.check_jump_targets(f)
        self.check_lnotab(f)
        self.assertEqual(count_instr_recursively(f, 'JUMP_IF_FALSE_OR_POP'), 2)
        # JUMP_IF_TRUE_OR_POP to JUMP_IF_TRUE_OR_POP --> JUMP_IF_TRUE_OR_POP to non-jump
        eleza f(a, b, c):
            rudisha ((a ama b)
                    ama c)
        self.check_jump_targets(f)
        self.check_lnotab(f)
        self.assertEqual(count_instr_recursively(f, 'JUMP_IF_TRUE_OR_POP'), 2)
        # JUMP_IF_FALSE_OR_POP to JUMP_IF_TRUE_OR_POP --> POP_JUMP_IF_FALSE to non-jump
        eleza f(a, b, c):
            rudisha ((a na b)
                    ama c)
        self.check_jump_targets(f)
        self.check_lnotab(f)
        self.assertNotInBytecode(f, 'JUMP_IF_FALSE_OR_POP')
        self.assertInBytecode(f, 'JUMP_IF_TRUE_OR_POP')
        self.assertInBytecode(f, 'POP_JUMP_IF_FALSE')
        # JUMP_IF_TRUE_OR_POP to JUMP_IF_FALSE_OR_POP --> POP_JUMP_IF_TRUE to non-jump
        eleza f(a, b, c):
            rudisha ((a ama b)
                    na c)
        self.check_jump_targets(f)
        self.check_lnotab(f)
        self.assertNotInBytecode(f, 'JUMP_IF_TRUE_OR_POP')
        self.assertInBytecode(f, 'JUMP_IF_FALSE_OR_POP')
        self.assertInBytecode(f, 'POP_JUMP_IF_TRUE')

    eleza test_elim_jump_after_rudisha1(self):
        # Eliminate dead code: jumps immediately after rudishas can't be reached
        eleza f(cond1, cond2):
            ikiwa cond1: rudisha 1
            ikiwa cond2: rudisha 2
            wakati 1:
                rudisha 3
            wakati 1:
                ikiwa cond1: rudisha 4
                rudisha 5
            rudisha 6
        self.assertNotInBytecode(f, 'JUMP_FORWARD')
        self.assertNotInBytecode(f, 'JUMP_ABSOLUTE')
        rudishas = [instr kila instr kwenye dis.get_instructions(f)
                          ikiwa instr.opname == 'RETURN_VALUE']
        self.assertLessEqual(len(rudishas), 6)
        self.check_lnotab(f)

    eleza test_elim_jump_after_rudisha2(self):
        # Eliminate dead code: jumps immediately after rudishas can't be reached
        eleza f(cond1, cond2):
            wakati 1:
                ikiwa cond1: rudisha 4
        self.assertNotInBytecode(f, 'JUMP_FORWARD')
        # There should be one jump kila the wakati loop.
        rudishas = [instr kila instr kwenye dis.get_instructions(f)
                          ikiwa instr.opname == 'JUMP_ABSOLUTE']
        self.assertEqual(len(rudishas), 1)
        rudishas = [instr kila instr kwenye dis.get_instructions(f)
                          ikiwa instr.opname == 'RETURN_VALUE']
        self.assertLessEqual(len(rudishas), 2)
        self.check_lnotab(f)

    eleza test_make_function_doesnt_bail(self):
        eleza f():
            eleza g()->1+1:
                pita
            rudisha g
        self.assertNotInBytecode(f, 'BINARY_ADD')
        self.check_lnotab(f)

    eleza test_constant_folding(self):
        # Issue #11244: aggressive constant folding.
        exprs = [
            '3 * -5',
            '-3 * 5',
            '2 * (3 * 4)',
            '(2 * 3) * 4',
            '(-1, 2, 3)',
            '(1, -2, 3)',
            '(1, 2, -3)',
            '(1, 2, -3) * 6',
            'lambda x: x kwenye {(3 * -5) + (-1 - 6), (1, -2, 3) * 2, Tupu}',
        ]
        kila e kwenye exprs:
            code = compile(e, '', 'single')
            kila instr kwenye dis.get_instructions(code):
                self.assertUongo(instr.opname.startswith('UNARY_'))
                self.assertUongo(instr.opname.startswith('BINARY_'))
                self.assertUongo(instr.opname.startswith('BUILD_'))
            self.check_lnotab(code)

    eleza test_in_literal_list(self):
        eleza containtest():
            rudisha x kwenye [a, b]
        self.assertEqual(count_instr_recursively(containtest, 'BUILD_LIST'), 0)
        self.check_lnotab(containtest)

    eleza test_iterate_literal_list(self):
        eleza forloop():
            kila x kwenye [a, b]:
                pita
        self.assertEqual(count_instr_recursively(forloop, 'BUILD_LIST'), 0)
        self.check_lnotab(forloop)

    eleza test_condition_with_binop_with_bools(self):
        eleza f():
            ikiwa Kweli ama Uongo:
                rudisha 1
            rudisha 0
        self.assertEqual(f(), 1)
        self.check_lnotab(f)

    eleza test_if_with_if_expression(self):  # XXX does this belong kwenye 3.8?
        # Check bpo-37289
        eleza f(x):
            ikiwa (Kweli ikiwa x else Uongo):
                rudisha Kweli
            rudisha Uongo
        self.assertKweli(f(Kweli))
        self.check_lnotab(f)

    eleza test_trailing_nops(self):
        # Check the lnotab of a function that even after trivial
        # optimization has trailing nops, which the lnotab adjustment has to
        # handle properly (bpo-38115).
        eleza f(x):
            wakati 1:
                rudisha 3
            wakati 1:
                rudisha 5
            rudisha 6
        self.check_lnotab(f)


kundi TestBuglets(unittest.TestCase):

    eleza test_bug_11510(self):
        # folded constant set optimization was commingled with the tuple
        # unpacking optimization which would fail ikiwa the set had duplicate
        # elements so that the set length was unexpected
        eleza f():
            x, y = {1, 1}
            rudisha x, y
        with self.assertRaises(ValueError):
            f()


ikiwa __name__ == "__main__":
    unittest.main()
