"""Tests kila the unparse.py script kwenye the Tools/parser directory."""

agiza unittest
agiza test.support
agiza io
agiza os
agiza random
agiza tokenize
agiza ast

kutoka test.test_tools agiza basepath, toolsdir, skip_if_missing

skip_if_missing()

parser_path = os.path.join(toolsdir, "parser")

ukijumuisha test.support.DirsOnSysPath(parser_path):
    agiza unparse

eleza read_pyfile(filename):
    """Read na rudisha the contents of a Python source file (as a
    string), taking into account the file encoding."""
    ukijumuisha open(filename, "rb") kama pyfile:
        encoding = tokenize.detect_encoding(pyfile.readline)[0]
    ukijumuisha open(filename, "r", encoding=encoding) kama pyfile:
        source = pyfile.read()
    rudisha source

for_else = """\
eleza f():
    kila x kwenye range(10):
        koma
    isipokua:
        y = 2
    z = 3
"""

while_else = """\
eleza g():
    wakati Kweli:
        koma
    isipokua:
        y = 2
    z = 3
"""

relative_agiza = """\
kutoka . agiza fred
kutoka .. agiza barney
kutoka .australia agiza shrimp kama prawns
"""

nonlocal_ex = """\
eleza f():
    x = 1
    eleza g():
        nonlocal x
        x = 2
        y = 7
        eleza h():
            nonlocal x, y
"""

# also acts kama test kila 'tatizo ... kama ...'
raise_kutoka = """\
jaribu:
    1 / 0
tatizo ZeroDivisionError kama e:
    ashiria ArithmeticError kutoka e
"""

class_decorator = """\
@f1(arg)
@f2
kundi Foo: pita
"""

elif1 = """\
ikiwa cond1:
    suite1
lasivyo cond2:
    suite2
isipokua:
    suite3
"""

elif2 = """\
ikiwa cond1:
    suite1
lasivyo cond2:
    suite2
"""

try_except_finally = """\
jaribu:
    suite1
tatizo ex1:
    suite2
tatizo ex2:
    suite3
isipokua:
    suite4
mwishowe:
    suite5
"""

with_simple = """\
ukijumuisha f():
    suite1
"""

with_as = """\
ukijumuisha f() kama x:
    suite1
"""

with_two_items = """\
ukijumuisha f() kama x, g() kama y:
    suite1
"""

kundi ASTTestCase(unittest.TestCase):
    eleza assertASTEqual(self, ast1, ast2):
        self.assertEqual(ast.dump(ast1), ast.dump(ast2))

    eleza check_roundtrip(self, code1, filename="internal"):
        ast1 = compile(code1, filename, "exec", ast.PyCF_ONLY_AST)
        unparse_buffer = io.StringIO()
        unparse.Unparser(ast1, unparse_buffer)
        code2 = unparse_buffer.getvalue()
        ast2 = compile(code2, filename, "exec", ast.PyCF_ONLY_AST)
        self.assertASTEqual(ast1, ast2)

kundi UnparseTestCase(ASTTestCase):
    # Tests kila specific bugs found kwenye earlier versions of unparse

    eleza test_fstrings(self):
        # See issue 25180
        self.check_roundtrip(r"""f'{f"{0}"*3}'""")
        self.check_roundtrip(r"""f'{f"{y}"*3}'""")

    eleza test_strings(self):
        self.check_roundtrip("u'foo'")
        self.check_roundtrip("r'foo'")
        self.check_roundtrip("b'foo'")

    eleza test_del_statement(self):
        self.check_roundtrip("toa x, y, z")

    eleza test_shifts(self):
        self.check_roundtrip("45 << 2")
        self.check_roundtrip("13 >> 7")

    eleza test_for_else(self):
        self.check_roundtrip(for_else)

    eleza test_while_else(self):
        self.check_roundtrip(while_else)

    eleza test_unary_parens(self):
        self.check_roundtrip("(-1)**7")
        self.check_roundtrip("(-1.)**8")
        self.check_roundtrip("(-1j)**6")
        self.check_roundtrip("sio Kweli ama Uongo")
        self.check_roundtrip("Kweli ama sio Uongo")

    eleza test_integer_parens(self):
        self.check_roundtrip("3 .__abs__()")

    eleza test_huge_float(self):
        self.check_roundtrip("1e1000")
        self.check_roundtrip("-1e1000")
        self.check_roundtrip("1e1000j")
        self.check_roundtrip("-1e1000j")

    eleza test_min_int(self):
        self.check_roundtrip(str(-2**31))
        self.check_roundtrip(str(-2**63))

    eleza test_imaginary_literals(self):
        self.check_roundtrip("7j")
        self.check_roundtrip("-7j")
        self.check_roundtrip("0j")
        self.check_roundtrip("-0j")

    eleza test_lambda_parentheses(self):
        self.check_roundtrip("(lambda: int)()")

    eleza test_chained_comparisons(self):
        self.check_roundtrip("1 < 4 <= 5")
        self.check_roundtrip("a ni b ni c ni sio d")

    eleza test_function_arguments(self):
        self.check_roundtrip("eleza f(): pita")
        self.check_roundtrip("eleza f(a): pita")
        self.check_roundtrip("eleza f(b = 2): pita")
        self.check_roundtrip("eleza f(a, b): pita")
        self.check_roundtrip("eleza f(a, b = 2): pita")
        self.check_roundtrip("eleza f(a = 5, b = 2): pita")
        self.check_roundtrip("eleza f(*, a = 1, b = 2): pita")
        self.check_roundtrip("eleza f(*, a = 1, b): pita")
        self.check_roundtrip("eleza f(*, a, b = 2): pita")
        self.check_roundtrip("eleza f(a, b = Tupu, *, c, **kwds): pita")
        self.check_roundtrip("eleza f(a=2, *args, c=5, d, **kwds): pita")
        self.check_roundtrip("eleza f(*args, **kwargs): pita")

    eleza test_relative_import(self):
        self.check_roundtrip(relative_import)

    eleza test_nonlocal(self):
        self.check_roundtrip(nonlocal_ex)

    eleza test_raise_from(self):
        self.check_roundtrip(raise_from)

    eleza test_bytes(self):
        self.check_roundtrip("b'123'")

    eleza test_annotations(self):
        self.check_roundtrip("eleza f(a : int): pita")
        self.check_roundtrip("eleza f(a: int = 5): pita")
        self.check_roundtrip("eleza f(*args: [int]): pita")
        self.check_roundtrip("eleza f(**kwargs: dict): pita")
        self.check_roundtrip("eleza f() -> Tupu: pita")

    eleza test_set_literal(self):
        self.check_roundtrip("{'a', 'b', 'c'}")

    eleza test_set_comprehension(self):
        self.check_roundtrip("{x kila x kwenye range(5)}")

    eleza test_dict_comprehension(self):
        self.check_roundtrip("{x: x*x kila x kwenye range(10)}")

    eleza test_class_decorators(self):
        self.check_roundtrip(class_decorator)

    eleza test_class_definition(self):
        self.check_roundtrip("kundi A(metaclass=type, *[], **{}): pita")

    eleza test_elifs(self):
        self.check_roundtrip(elif1)
        self.check_roundtrip(elif2)

    eleza test_try_except_finally(self):
        self.check_roundtrip(try_except_finally)

    eleza test_starred_assignment(self):
        self.check_roundtrip("a, *b, c = seq")
        self.check_roundtrip("a, (*b, c) = seq")
        self.check_roundtrip("a, *b[0], c = seq")
        self.check_roundtrip("a, *(b, c) = seq")

    eleza test_with_simple(self):
        self.check_roundtrip(with_simple)

    eleza test_with_as(self):
        self.check_roundtrip(with_as)

    eleza test_with_two_items(self):
        self.check_roundtrip(with_two_items)

    eleza test_dict_unpacking_in_dict(self):
        # See issue 26489
        self.check_roundtrip(r"""{**{'y': 2}, 'x': 1}""")
        self.check_roundtrip(r"""{**{'y': 2}, **{'x': 1}}""")


kundi DirectoryTestCase(ASTTestCase):
    """Test roundtrip behaviour on all files kwenye Lib na Lib/test."""
    NAMES = Tupu

    # test directories, relative to the root of the distribution
    test_directories = 'Lib', os.path.join('Lib', 'test')

    @classmethod
    eleza get_names(cls):
        ikiwa cls.NAMES ni sio Tupu:
            rudisha cls.NAMES

        names = []
        kila d kwenye cls.test_directories:
            test_dir = os.path.join(basepath, d)
            kila n kwenye os.listdir(test_dir):
                ikiwa n.endswith('.py') na sio n.startswith('bad'):
                    names.append(os.path.join(test_dir, n))

        # Test limited subset of files unless the 'cpu' resource ni specified.
        ikiwa sio test.support.is_resource_enabled("cpu"):
            names = random.sample(names, 10)
        # bpo-31174: Store the names sample to always test the same files.
        # It prevents false alarms when hunting reference leaks.
        cls.NAMES = names
        rudisha names

    eleza test_files(self):
        # get names of files to test
        names = self.get_names()

        kila filename kwenye names:
            ikiwa test.support.verbose:
                andika('Testing %s' % filename)

            # Some f-strings are sio correctly round-tripped by
            #  Tools/parser/unparse.py.  See issue 28002 kila details.
            #  We need to skip files that contain such f-strings.
            ikiwa os.path.basename(filename) kwenye ('test_fstring.py', ):
                ikiwa test.support.verbose:
                    andika(f'Skipping {filename}: see issue 28002')
                endelea

            ukijumuisha self.subTest(filename=filename):
                source = read_pyfile(filename)
                self.check_roundtrip(source)


ikiwa __name__ == '__main__':
    unittest.main()
