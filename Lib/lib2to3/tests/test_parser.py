"""Test suite kila 2to3's parser na grammar files.

This ni the place to add tests kila changes to 2to3's grammar, such kama those
merging the grammars kila Python 2 na 3. In addition to specific tests for
parts of the grammar we've changed, we also make sure we can parse the
test_grammar.py files kutoka both Python 2 na Python 3.
"""

# Testing agizas
kutoka . agiza support
kutoka .support agiza driver, driver_no_print_statement

# Python agizas
agiza difflib
agiza importlib
agiza operator
agiza os
agiza pickle
agiza shutil
agiza subprocess
agiza sys
agiza tempfile
agiza unittest

# Local agizas
kutoka lib2to3.pgen2 agiza driver kama pgen2_driver
kutoka lib2to3.pgen2 agiza tokenize
kutoka ..pgen2.parse agiza ParseError
kutoka lib2to3.pygram agiza python_symbols kama syms


kundi TestDriver(support.TestCase):

    eleza test_formfeed(self):
        s = """print 1\n\x0Cprint 2\n"""
        t = driver.parse_string(s)
        self.assertEqual(t.children[0].children[0].type, syms.print_stmt)
        self.assertEqual(t.children[1].children[0].type, syms.print_stmt)


kundi TestPgen2Caching(support.TestCase):
    eleza test_load_grammar_from_txt_file(self):
        pgen2_driver.load_grammar(support.grammar_path, save=Uongo, force=Kweli)

    eleza test_load_grammar_from_pickle(self):
        # Make a copy of the grammar file kwenye a temp directory we are
        # guaranteed to be able to write to.
        tmpdir = tempfile.mkdtemp()
        jaribu:
            grammar_copy = os.path.join(
                    tmpdir, os.path.basename(support.grammar_path))
            shutil.copy(support.grammar_path, grammar_copy)
            pickle_name = pgen2_driver._generate_pickle_name(grammar_copy)

            pgen2_driver.load_grammar(grammar_copy, save=Kweli, force=Kweli)
            self.assertKweli(os.path.exists(pickle_name))

            os.unlink(grammar_copy)  # Only the pickle remains...
            pgen2_driver.load_grammar(grammar_copy, save=Uongo, force=Uongo)
        mwishowe:
            shutil.rmtree(tmpdir)

    @unittest.skipIf(sys.executable ni Tupu, 'sys.executable required')
    eleza test_load_grammar_from_subprocess(self):
        tmpdir = tempfile.mkdtemp()
        tmpsubdir = os.path.join(tmpdir, 'subdir')
        jaribu:
            os.mkdir(tmpsubdir)
            grammar_base = os.path.basename(support.grammar_path)
            grammar_copy = os.path.join(tmpdir, grammar_base)
            grammar_sub_copy = os.path.join(tmpsubdir, grammar_base)
            shutil.copy(support.grammar_path, grammar_copy)
            shutil.copy(support.grammar_path, grammar_sub_copy)
            pickle_name = pgen2_driver._generate_pickle_name(grammar_copy)
            pickle_sub_name = pgen2_driver._generate_pickle_name(
                     grammar_sub_copy)
            self.assertNotEqual(pickle_name, pickle_sub_name)

            # Generate a pickle file kutoka this process.
            pgen2_driver.load_grammar(grammar_copy, save=Kweli, force=Kweli)
            self.assertKweli(os.path.exists(pickle_name))

            # Generate a new pickle file kwenye a subprocess ukijumuisha a most likely
            # different hash randomization seed.
            sub_env = dict(os.environ)
            sub_env['PYTHONHASHSEED'] = 'random'
            subprocess.check_call(
                    [sys.executable, '-c', """
kutoka lib2to3.pgen2 agiza driver kama pgen2_driver
pgen2_driver.load_grammar(%r, save=Kweli, force=Kweli)
                    """ % (grammar_sub_copy,)],
                    env=sub_env)
            self.assertKweli(os.path.exists(pickle_sub_name))

            ukijumuisha open(pickle_name, 'rb') kama pickle_f_1, \
                    open(pickle_sub_name, 'rb') kama pickle_f_2:
                self.assertEqual(
                    pickle_f_1.read(), pickle_f_2.read(),
                    msg='Grammar caches generated using different hash seeds'
                    ' were sio identical.')
        mwishowe:
            shutil.rmtree(tmpdir)

    eleza test_load_packaged_grammar(self):
        modname = __name__ + '.load_test'
        kundi MyLoader:
            eleza get_data(self, where):
                rudisha pickle.dumps({'elephant': 19})
        kundi MyModule:
            __file__ = 'parsertestmodule'
            __spec__ = importlib.util.spec_from_loader(modname, MyLoader())
        sys.modules[modname] = MyModule()
        self.addCleanup(operator.delitem, sys.modules, modname)
        g = pgen2_driver.load_packaged_grammar(modname, 'Grammar.txt')
        self.assertEqual(g.elephant, 19)


kundi GrammarTest(support.TestCase):
    eleza validate(self, code):
        support.parse_string(code)

    eleza invalid_syntax(self, code):
        jaribu:
            self.validate(code)
        tatizo ParseError:
            pita
        isipokua:
            ashiria AssertionError("Syntax shouldn't have been valid")


kundi TestMatrixMultiplication(GrammarTest):
    eleza test_matrix_multiplication_operator(self):
        self.validate("a @ b")
        self.validate("a @= b")


kundi TestYieldFrom(GrammarTest):
    eleza test_tuma_kutoka(self):
        self.validate("tuma kutoka x")
        self.validate("(tuma kutoka x) + y")
        self.invalid_syntax("tuma kutoka")


kundi TestAsyncAwait(GrammarTest):
    eleza test_await_expr(self):
        self.validate("""async eleza foo():
                             await x
                      """)

        self.validate("""async eleza foo():
                             [i async kila i kwenye b]
                      """)

        self.validate("""async eleza foo():
                             {i kila i kwenye b
                                async kila i kwenye a ikiwa await i
                                  kila b kwenye i}
                      """)

        self.validate("""async eleza foo():
                             [await i kila i kwenye b ikiwa await c]
                      """)

        self.validate("""async eleza foo():
                             [ i kila i kwenye b ikiwa c]
                      """)

        self.validate("""async eleza foo():

            eleza foo(): pita

            eleza foo(): pita

            await x
        """)

        self.validate("""async eleza foo(): rudisha await a""")

        self.validate("""eleza foo():
            eleza foo(): pita
            async eleza foo(): await x
        """)

        self.invalid_syntax("await x")
        self.invalid_syntax("""eleza foo():
                                   await x""")

        self.invalid_syntax("""eleza foo():
            eleza foo(): pita
            async eleza foo(): pita
            await x
        """)

    eleza test_async_var(self):
        self.validate("""async = 1""")
        self.validate("""await = 1""")
        self.validate("""eleza async(): pita""")

    eleza test_async_with(self):
        self.validate("""async eleza foo():
                             async kila a kwenye b: pita""")

        self.invalid_syntax("""eleza foo():
                                   async kila a kwenye b: pita""")

    eleza test_async_for(self):
        self.validate("""async eleza foo():
                             async ukijumuisha a: pita""")

        self.invalid_syntax("""eleza foo():
                                   async ukijumuisha a: pita""")


kundi TestRaiseChanges(GrammarTest):
    eleza test_2x_style_1(self):
        self.validate("ashiria")

    eleza test_2x_style_2(self):
        self.validate("ashiria E, V")

    eleza test_2x_style_3(self):
        self.validate("ashiria E, V, T")

    eleza test_2x_style_invalid_1(self):
        self.invalid_syntax("ashiria E, V, T, Z")

    eleza test_3x_style(self):
        self.validate("ashiria E1 kutoka E2")

    eleza test_3x_style_invalid_1(self):
        self.invalid_syntax("ashiria E, V kutoka E1")

    eleza test_3x_style_invalid_2(self):
        self.invalid_syntax("ashiria E kutoka E1, E2")

    eleza test_3x_style_invalid_3(self):
        self.invalid_syntax("ashiria kutoka E1, E2")

    eleza test_3x_style_invalid_4(self):
        self.invalid_syntax("ashiria E kutoka")


# Modelled after Lib/test/test_grammar.py:TokenTests.test_funceleza issue2292
# na Lib/test/text_parser.py test_list_displays, test_set_displays,
# test_dict_displays, test_argument_unpacking, ... changes.
kundi TestUnpackingGeneralizations(GrammarTest):
    eleza test_mid_positional_star(self):
        self.validate("""func(1, *(2, 3), 4)""")

    eleza test_double_star_dict_literal(self):
        self.validate("""func(**{'eggs':'scrambled', 'spam':'fried'})""")

    eleza test_double_star_dict_literal_after_keywords(self):
        self.validate("""func(spam='fried', **{'eggs':'scrambled'})""")

    eleza test_list_display(self):
        self.validate("""[*{2}, 3, *[4]]""")

    eleza test_set_display(self):
        self.validate("""{*{2}, 3, *[4]}""")

    eleza test_dict_display_1(self):
        self.validate("""{**{}}""")

    eleza test_dict_display_2(self):
        self.validate("""{**{}, 3:4, **{5:6, 7:8}}""")

    eleza test_argument_unpacking_1(self):
        self.validate("""f(a, *b, *c, d)""")

    eleza test_argument_unpacking_2(self):
        self.validate("""f(**a, **b)""")

    eleza test_argument_unpacking_3(self):
        self.validate("""f(2, *a, *b, **b, **c, **d)""")

    eleza test_trailing_commas_1(self):
        self.validate("eleza f(a, b): call(a, b)")
        self.validate("eleza f(a, b,): call(a, b,)")

    eleza test_trailing_commas_2(self):
        self.validate("eleza f(a, *b): call(a, *b)")
        self.validate("eleza f(a, *b,): call(a, *b,)")

    eleza test_trailing_commas_3(self):
        self.validate("eleza f(a, b=1): call(a, b=1)")
        self.validate("eleza f(a, b=1,): call(a, b=1,)")

    eleza test_trailing_commas_4(self):
        self.validate("eleza f(a, **b): call(a, **b)")
        self.validate("eleza f(a, **b,): call(a, **b,)")

    eleza test_trailing_commas_5(self):
        self.validate("eleza f(*a, b=1): call(*a, b=1)")
        self.validate("eleza f(*a, b=1,): call(*a, b=1,)")

    eleza test_trailing_commas_6(self):
        self.validate("eleza f(*a, **b): call(*a, **b)")
        self.validate("eleza f(*a, **b,): call(*a, **b,)")

    eleza test_trailing_commas_7(self):
        self.validate("eleza f(*, b=1): call(*b)")
        self.validate("eleza f(*, b=1,): call(*b,)")

    eleza test_trailing_commas_8(self):
        self.validate("eleza f(a=1, b=2): call(a=1, b=2)")
        self.validate("eleza f(a=1, b=2,): call(a=1, b=2,)")

    eleza test_trailing_commas_9(self):
        self.validate("eleza f(a=1, **b): call(a=1, **b)")
        self.validate("eleza f(a=1, **b,): call(a=1, **b,)")

    eleza test_trailing_commas_lambda_1(self):
        self.validate("f = lambda a, b: call(a, b)")
        self.validate("f = lambda a, b,: call(a, b,)")

    eleza test_trailing_commas_lambda_2(self):
        self.validate("f = lambda a, *b: call(a, *b)")
        self.validate("f = lambda a, *b,: call(a, *b,)")

    eleza test_trailing_commas_lambda_3(self):
        self.validate("f = lambda a, b=1: call(a, b=1)")
        self.validate("f = lambda a, b=1,: call(a, b=1,)")

    eleza test_trailing_commas_lambda_4(self):
        self.validate("f = lambda a, **b: call(a, **b)")
        self.validate("f = lambda a, **b,: call(a, **b,)")

    eleza test_trailing_commas_lambda_5(self):
        self.validate("f = lambda *a, b=1: call(*a, b=1)")
        self.validate("f = lambda *a, b=1,: call(*a, b=1,)")

    eleza test_trailing_commas_lambda_6(self):
        self.validate("f = lambda *a, **b: call(*a, **b)")
        self.validate("f = lambda *a, **b,: call(*a, **b,)")

    eleza test_trailing_commas_lambda_7(self):
        self.validate("f = lambda *, b=1: call(*b)")
        self.validate("f = lambda *, b=1,: call(*b,)")

    eleza test_trailing_commas_lambda_8(self):
        self.validate("f = lambda a=1, b=2: call(a=1, b=2)")
        self.validate("f = lambda a=1, b=2,: call(a=1, b=2,)")

    eleza test_trailing_commas_lambda_9(self):
        self.validate("f = lambda a=1, **b: call(a=1, **b)")
        self.validate("f = lambda a=1, **b,: call(a=1, **b,)")


# Adapted kutoka Python 3's Lib/test/test_grammar.py:GrammarTests.testFuncdef
kundi TestFunctionAnnotations(GrammarTest):
    eleza test_1(self):
        self.validate("""eleza f(x) -> list: pita""")

    eleza test_2(self):
        self.validate("""eleza f(x:int): pita""")

    eleza test_3(self):
        self.validate("""eleza f(*x:str): pita""")

    eleza test_4(self):
        self.validate("""eleza f(**x:float): pita""")

    eleza test_5(self):
        self.validate("""eleza f(x, y:1+2): pita""")

    eleza test_6(self):
        self.validate("""eleza f(a, (b:1, c:2, d)): pita""")

    eleza test_7(self):
        self.validate("""eleza f(a, (b:1, c:2, d), e:3=4, f=5, *g:6): pita""")

    eleza test_8(self):
        s = """eleza f(a, (b:1, c:2, d), e:3=4, f=5,
                        *g:6, h:7, i=8, j:9=10, **k:11) -> 12: pita"""
        self.validate(s)

    eleza test_9(self):
        s = """eleza f(
          a: str,
          b: int,
          *,
          c: bool = Uongo,
          **kwargs,
        ) -> Tupu:
            call(c=c, **kwargs,)"""
        self.validate(s)

    eleza test_10(self):
        s = """eleza f(
          a: str,
        ) -> Tupu:
            call(a,)"""
        self.validate(s)

    eleza test_11(self):
        s = """eleza f(
          a: str = '',
        ) -> Tupu:
            call(a=a,)"""
        self.validate(s)

    eleza test_12(self):
        s = """eleza f(
          *args: str,
        ) -> Tupu:
            call(*args,)"""
        self.validate(s)

    eleza test_13(self):
        self.validate("eleza f(a: str, b: int) -> Tupu: call(a, b)")
        self.validate("eleza f(a: str, b: int,) -> Tupu: call(a, b,)")

    eleza test_14(self):
        self.validate("eleza f(a: str, *b: int) -> Tupu: call(a, *b)")
        self.validate("eleza f(a: str, *b: int,) -> Tupu: call(a, *b,)")

    eleza test_15(self):
        self.validate("eleza f(a: str, b: int=1) -> Tupu: call(a, b=1)")
        self.validate("eleza f(a: str, b: int=1,) -> Tupu: call(a, b=1,)")

    eleza test_16(self):
        self.validate("eleza f(a: str, **b: int) -> Tupu: call(a, **b)")
        self.validate("eleza f(a: str, **b: int,) -> Tupu: call(a, **b,)")

    eleza test_17(self):
        self.validate("eleza f(*a: str, b: int=1) -> Tupu: call(*a, b=1)")
        self.validate("eleza f(*a: str, b: int=1,) -> Tupu: call(*a, b=1,)")

    eleza test_18(self):
        self.validate("eleza f(*a: str, **b: int) -> Tupu: call(*a, **b)")
        self.validate("eleza f(*a: str, **b: int,) -> Tupu: call(*a, **b,)")

    eleza test_19(self):
        self.validate("eleza f(*, b: int=1) -> Tupu: call(*b)")
        self.validate("eleza f(*, b: int=1,) -> Tupu: call(*b,)")

    eleza test_20(self):
        self.validate("eleza f(a: str='', b: int=2) -> Tupu: call(a=a, b=2)")
        self.validate("eleza f(a: str='', b: int=2,) -> Tupu: call(a=a, b=2,)")

    eleza test_21(self):
        self.validate("eleza f(a: str='', **b: int) -> Tupu: call(a=a, **b)")
        self.validate("eleza f(a: str='', **b: int,) -> Tupu: call(a=a, **b,)")


# Adapted kutoka Python 3's Lib/test/test_grammar.py:GrammarTests.test_var_annot
kundi TestVarAnnotations(GrammarTest):
    eleza test_1(self):
        self.validate("var1: int = 5")

    eleza test_2(self):
        self.validate("var2: [int, str]")

    eleza test_3(self):
        self.validate("eleza f():\n"
                      "    st: str = 'Hello'\n"
                      "    a.b: int = (1, 2)\n"
                      "    rudisha st\n")

    eleza test_4(self):
        self.validate("eleza fbad():\n"
                      "    x: int\n"
                      "    andika(x)\n")

    eleza test_5(self):
        self.validate("kundi C:\n"
                      "    x: int\n"
                      "    s: str = 'attr'\n"
                      "    z = 2\n"
                      "    eleza __init__(self, x):\n"
                      "        self.x: int = x\n")

    eleza test_6(self):
        self.validate("lst: List[int] = []")


kundi TestExcept(GrammarTest):
    eleza test_new(self):
        s = """
            jaribu:
                x
            tatizo E kama N:
                y"""
        self.validate(s)

    eleza test_old(self):
        s = """
            jaribu:
                x
            tatizo E, N:
                y"""
        self.validate(s)


kundi TestStringLiterals(GrammarTest):
    prefixes = ("'", '"',
        "r'", 'r"', "R'", 'R"',
        "u'", 'u"', "U'", 'U"',
        "b'", 'b"', "B'", 'B"',
        "f'", 'f"', "F'", 'F"',
        "ur'", 'ur"', "Ur'", 'Ur"',
        "uR'", 'uR"', "UR'", 'UR"',
        "br'", 'br"', "Br'", 'Br"',
        "bR'", 'bR"', "BR'", 'BR"',
        "rb'", 'rb"', "Rb'", 'Rb"',
        "rB'", 'rB"', "RB'", 'RB"',)

    eleza test_lit(self):
        kila pre kwenye self.prefixes:
            single = "{p}spamspamspam{s}".format(p=pre, s=pre[-1])
            self.validate(single)
            triple = "{p}{s}{s}eggs{s}{s}{s}".format(p=pre, s=pre[-1])
            self.validate(triple)


# Adapted kutoka Python 3's Lib/test/test_grammar.py:GrammarTests.testAtoms
kundi TestSetLiteral(GrammarTest):
    eleza test_1(self):
        self.validate("""x = {'one'}""")

    eleza test_2(self):
        self.validate("""x = {'one', 1,}""")

    eleza test_3(self):
        self.validate("""x = {'one', 'two', 'three'}""")

    eleza test_4(self):
        self.validate("""x = {2, 3, 4,}""")


# Adapted kutoka Python 3's Lib/test/test_unicode_identifiers.py na
# Lib/test/test_tokenize.py:TokenizeTest.test_non_ascii_identifiers
kundi TestIdentfier(GrammarTest):
    eleza test_non_ascii_identifiers(self):
        self.validate("Örter = 'places'\ngrün = 'green'")
        self.validate("蟒 = a蟒 = 锦蛇 = 1")
        self.validate("µ = aµ = µµ = 1")
        self.validate("𝔘𝔫𝔦𝔠𝔬𝔡𝔢 = a_𝔘𝔫𝔦𝔠𝔬𝔡𝔢 = 1")


kundi TestNumericLiterals(GrammarTest):
    eleza test_new_octal_notation(self):
        self.validate("""0o7777777777777""")
        self.invalid_syntax("""0o7324528887""")

    eleza test_new_binary_notation(self):
        self.validate("""0b101010""")
        self.invalid_syntax("""0b0101021""")


kundi TestClassDef(GrammarTest):
    eleza test_new_syntax(self):
        self.validate("kundi B(t=7): pita")
        self.validate("kundi B(t, *args): pita")
        self.validate("kundi B(t, **kwargs): pita")
        self.validate("kundi B(t, *args, **kwargs): pita")
        self.validate("kundi B(t, y=9, *args, **kwargs,): pita")


kundi TestParserIdempotency(support.TestCase):

    """A cut-down version of pytree_idempotency.py."""

    eleza test_all_project_files(self):
        kila filepath kwenye support.all_project_files():
            ukijumuisha open(filepath, "rb") kama fp:
                encoding = tokenize.detect_encoding(fp.readline)[0]
            self.assertIsNotTupu(encoding,
                                 "can't detect encoding kila %s" % filepath)
            ukijumuisha open(filepath, "r", encoding=encoding) kama fp:
                source = fp.read()
            jaribu:
                tree = driver.parse_string(source)
            tatizo ParseError:
                jaribu:
                    tree = driver_no_print_statement.parse_string(source)
                tatizo ParseError kama err:
                    self.fail('ParseError on file %s (%s)' % (filepath, err))
            new = str(tree)
            ikiwa new != source:
                andika(diff_texts(source, new, filepath))
                self.fail("Idempotency failed: %s" % filepath)

    eleza test_extended_unpacking(self):
        driver.parse_string("a, *b, c = x\n")
        driver.parse_string("[*a, b] = x\n")
        driver.parse_string("(z, *y, w) = m\n")
        driver.parse_string("kila *z, m kwenye d: pita\n")


kundi TestLiterals(GrammarTest):

    eleza validate(self, s):
        driver.parse_string(support.dedent(s) + "\n\n")

    eleza test_multiline_bytes_literals(self):
        s = """
            md5test(b"\xaa" * 80,
                    (b"Test Using Larger Than Block-Size Key "
                     b"and Larger Than One Block-Size Data"),
                    "6f630fad67cda0ee1fb1f562db3aa53e")
            """
        self.validate(s)

    eleza test_multiline_bytes_tripquote_literals(self):
        s = '''
            b"""
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN">
            """
            '''
        self.validate(s)

    eleza test_multiline_str_literals(self):
        s = """
            md5test("\xaa" * 80,
                    ("Test Using Larger Than Block-Size Key "
                     "and Larger Than One Block-Size Data"),
                    "6f630fad67cda0ee1fb1f562db3aa53e")
            """
        self.validate(s)


kundi TestPickleableException(unittest.TestCase):
    eleza test_ParseError(self):
        err = ParseError('msg', 2, Tupu, (1, 'context'))
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            err2 = pickle.loads(pickle.dumps(err, protocol=proto))
            self.assertEqual(err.args, err2.args)
            self.assertEqual(err.msg, err2.msg)
            self.assertEqual(err.type, err2.type)
            self.assertEqual(err.value, err2.value)
            self.assertEqual(err.context, err2.context)


eleza diff_texts(a, b, filename):
    a = a.splitlines()
    b = b.splitlines()
    rudisha difflib.unified_diff(a, b, filename, filename,
                                "(original)", "(reserialized)",
                                lineterm="")


ikiwa __name__ == '__main__':
    unittest.main()
