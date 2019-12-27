"""Tests for the unparse.py script in the Tools/parser directory."""

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

with test.support.DirsOnSysPath(parser_path):
    agiza unparse

eleza read_pyfile(filename):
    """Read and rudisha the contents of a Python source file (as a
    string), taking into account the file encoding."""
    with open(filename, "rb") as pyfile:
        encoding = tokenize.detect_encoding(pyfile.readline)[0]
    with open(filename, "r", encoding=encoding) as pyfile:
        source = pyfile.read()
    rudisha source

for_else = """\
eleza f():
    for x in range(10):
        break
    else:
        y = 2
    z = 3
"""

while_else = """\
eleza g():
    while True:
        break
    else:
        y = 2
    z = 3
"""

relative_agiza = """\
kutoka . agiza fred
kutoka .. agiza barney
kutoka .australia agiza shrimp as prawns
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

# also acts as test for 'except ... as ...'
raise_kutoka = """\
try:
    1 / 0
except ZeroDivisionError as e:
    raise ArithmeticError kutoka e
"""

class_decorator = """\
@f1(arg)
@f2
kundi Foo: pass
"""

elif1 = """\
ikiwa cond1:
    suite1
elikiwa cond2:
    suite2
else:
    suite3
"""

elif2 = """\
ikiwa cond1:
    suite1
elikiwa cond2:
    suite2
"""

try_except_finally = """\
try:
    suite1
except ex1:
    suite2
except ex2:
    suite3
else:
    suite4
finally:
    suite5
"""

with_simple = """\
with f():
    suite1
"""

with_as = """\
with f() as x:
    suite1
"""

with_two_items = """\
with f() as x, g() as y:
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
    # Tests for specific bugs found in earlier versions of unparse

    eleza test_fstrings(self):
        # See issue 25180
        self.check_roundtrip(r"""f'{f"{0}"*3}'""")
        self.check_roundtrip(r"""f'{f"{y}"*3}'""")

    eleza test_strings(self):
        self.check_roundtrip("u'foo'")
        self.check_roundtrip("r'foo'")
        self.check_roundtrip("b'foo'")

    eleza test_del_statement(self):
        self.check_roundtrip("del x, y, z")

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
        self.check_roundtrip("not True or False")
        self.check_roundtrip("True or not False")

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
        self.check_roundtrip("a is b is c is not d")

    eleza test_function_arguments(self):
        self.check_roundtrip("eleza f(): pass")
        self.check_roundtrip("eleza f(a): pass")
        self.check_roundtrip("eleza f(b = 2): pass")
        self.check_roundtrip("eleza f(a, b): pass")
        self.check_roundtrip("eleza f(a, b = 2): pass")
        self.check_roundtrip("eleza f(a = 5, b = 2): pass")
        self.check_roundtrip("eleza f(*, a = 1, b = 2): pass")
        self.check_roundtrip("eleza f(*, a = 1, b): pass")
        self.check_roundtrip("eleza f(*, a, b = 2): pass")
        self.check_roundtrip("eleza f(a, b = None, *, c, **kwds): pass")
        self.check_roundtrip("eleza f(a=2, *args, c=5, d, **kwds): pass")
        self.check_roundtrip("eleza f(*args, **kwargs): pass")

    eleza test_relative_agiza(self):
        self.check_roundtrip(relative_agiza)

    eleza test_nonlocal(self):
        self.check_roundtrip(nonlocal_ex)

    eleza test_raise_kutoka(self):
        self.check_roundtrip(raise_kutoka)

    eleza test_bytes(self):
        self.check_roundtrip("b'123'")

    eleza test_annotations(self):
        self.check_roundtrip("eleza f(a : int): pass")
        self.check_roundtrip("eleza f(a: int = 5): pass")
        self.check_roundtrip("eleza f(*args: [int]): pass")
        self.check_roundtrip("eleza f(**kwargs: dict): pass")
        self.check_roundtrip("eleza f() -> None: pass")

    eleza test_set_literal(self):
        self.check_roundtrip("{'a', 'b', 'c'}")

    eleza test_set_comprehension(self):
        self.check_roundtrip("{x for x in range(5)}")

    eleza test_dict_comprehension(self):
        self.check_roundtrip("{x: x*x for x in range(10)}")

    eleza test_class_decorators(self):
        self.check_roundtrip(class_decorator)

    eleza test_class_definition(self):
        self.check_roundtrip("kundi A(metaclass=type, *[], **{}): pass")

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
    """Test roundtrip behaviour on all files in Lib and Lib/test."""
    NAMES = None

    # test directories, relative to the root of the distribution
    test_directories = 'Lib', os.path.join('Lib', 'test')

    @classmethod
    eleza get_names(cls):
        ikiwa cls.NAMES is not None:
            rudisha cls.NAMES

        names = []
        for d in cls.test_directories:
            test_dir = os.path.join(basepath, d)
            for n in os.listdir(test_dir):
                ikiwa n.endswith('.py') and not n.startswith('bad'):
                    names.append(os.path.join(test_dir, n))

        # Test limited subset of files unless the 'cpu' resource is specified.
        ikiwa not test.support.is_resource_enabled("cpu"):
            names = random.sample(names, 10)
        # bpo-31174: Store the names sample to always test the same files.
        # It prevents false alarms when hunting reference leaks.
        cls.NAMES = names
        rudisha names

    eleza test_files(self):
        # get names of files to test
        names = self.get_names()

        for filename in names:
            ikiwa test.support.verbose:
                andika('Testing %s' % filename)

            # Some f-strings are not correctly round-tripped by
            #  Tools/parser/unparse.py.  See issue 28002 for details.
            #  We need to skip files that contain such f-strings.
            ikiwa os.path.basename(filename) in ('test_fstring.py', ):
                ikiwa test.support.verbose:
                    andika(f'Skipping {filename}: see issue 28002')
                continue

            with self.subTest(filename=filename):
                source = read_pyfile(filename)
                self.check_roundtrip(source)


ikiwa __name__ == '__main__':
    unittest.main()
