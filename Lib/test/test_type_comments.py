agiza ast
agiza sys
agiza unittest


funceleza = """\
eleza foo():
    # type: () -> int
    pass

eleza bar():  # type: () -> None
    pass
"""

asynceleza = """\
async eleza foo():
    # type: () -> int
    rudisha await bar()

async eleza bar():  # type: () -> int
    rudisha await bar()
"""

asyncvar = """\
async = 12
await = 13
"""

asynccomp = """\
async eleza foo(xs):
    [x async for x in xs]
"""

matmul = """\
a = b @ c
"""

fstring = """\
a = 42
f"{a}"
"""

underscorednumber = """\
a = 42_42_42
"""

redundanteleza = """\
eleza foo():  # type: () -> int
    # type: () -> str
    rudisha ''
"""

nonasciieleza = """\
eleza foo():
    # type: () -> àçčéñt
    pass
"""

forstmt = """\
for a in []:  # type: int
    pass
"""

withstmt = """\
with context() as a:  # type: int
    pass
"""

vardecl = """\
a = 0  # type: int
"""

ignores = """\
eleza foo():
    pass  # type: ignore

eleza bar():
    x = 1  # type: ignore

eleza baz():
    pass  # type: ignore[excuse]
    pass  # type: ignore=excuse
    pass  # type: ignore [excuse]
    x = 1  # type: ignore whatever
"""

# Test for long-form type-comments in arguments.  A test function
# named 'fabvk' would have two positional args, a and b, plus a
# var-arg *v, plus a kw-arg **k.  It is verified in test_longargs()
# that it has exactly these arguments, no more, no fewer.
longargs = """\
eleza fa(
    a = 1,  # type: A
):
    pass

eleza fa(
    a = 1  # type: A
):
    pass

eleza fa(
    a = 1,  # type: A
    /
):
    pass

eleza fab(
    a,  # type: A
    b,  # type: B
):
    pass

eleza fab(
    a,  # type: A
    /,
    b,  # type: B
):
    pass

eleza fab(
    a,  # type: A
    b   # type: B
):
    pass

eleza fv(
    *v,  # type: V
):
    pass

eleza fv(
    *v  # type: V
):
    pass

eleza fk(
    **k,  # type: K
):
    pass

eleza fk(
    **k  # type: K
):
    pass

eleza fvk(
    *v,  # type: V
    **k,  # type: K
):
    pass

eleza fvk(
    *v,  # type: V
    **k  # type: K
):
    pass

eleza fav(
    a,  # type: A
    *v,  # type: V
):
    pass

eleza fav(
    a,  # type: A
    /,
    *v,  # type: V
):
    pass

eleza fav(
    a,  # type: A
    *v  # type: V
):
    pass

eleza fak(
    a,  # type: A
    **k,  # type: K
):
    pass

eleza fak(
    a,  # type: A
    /,
    **k,  # type: K
):
    pass

eleza fak(
    a,  # type: A
    **k  # type: K
):
    pass

eleza favk(
    a,  # type: A
    *v,  # type: V
    **k,  # type: K
):
    pass

eleza favk(
    a,  # type: A
    /,
    *v,  # type: V
    **k,  # type: K
):
    pass

eleza favk(
    a,  # type: A
    *v,  # type: V
    **k  # type: K
):
    pass
"""


kundi TypeCommentTests(unittest.TestCase):

    lowest = 4  # Lowest minor version supported
    highest = sys.version_info[1]  # Highest minor version

    eleza parse(self, source, feature_version=highest):
        rudisha ast.parse(source, type_comments=True,
                         feature_version=feature_version)

    eleza parse_all(self, source, minver=lowest, maxver=highest, expected_regex=""):
        for version in range(self.lowest, self.highest + 1):
            feature_version = (3, version)
            ikiwa minver <= version <= maxver:
                try:
                    yield self.parse(source, feature_version)
                except SyntaxError as err:
                    raise SyntaxError(str(err) + f" feature_version={feature_version}")
            else:
                with self.assertRaisesRegex(SyntaxError, expected_regex,
                                            msg=f"feature_version={feature_version}"):
                    self.parse(source, feature_version)

    eleza classic_parse(self, source):
        rudisha ast.parse(source)

    eleza test_funcdef(self):
        for tree in self.parse_all(funcdef):
            self.assertEqual(tree.body[0].type_comment, "() -> int")
            self.assertEqual(tree.body[1].type_comment, "() -> None")
        tree = self.classic_parse(funcdef)
        self.assertEqual(tree.body[0].type_comment, None)
        self.assertEqual(tree.body[1].type_comment, None)

    eleza test_asyncdef(self):
        for tree in self.parse_all(asyncdef, minver=5):
            self.assertEqual(tree.body[0].type_comment, "() -> int")
            self.assertEqual(tree.body[1].type_comment, "() -> int")
        tree = self.classic_parse(asyncdef)
        self.assertEqual(tree.body[0].type_comment, None)
        self.assertEqual(tree.body[1].type_comment, None)

    eleza test_asyncvar(self):
        for tree in self.parse_all(asyncvar, maxver=6):
            pass

    eleza test_asynccomp(self):
        for tree in self.parse_all(asynccomp, minver=6):
            pass

    eleza test_matmul(self):
        for tree in self.parse_all(matmul, minver=5):
            pass

    eleza test_fstring(self):
        for tree in self.parse_all(fstring, minver=6):
            pass

    eleza test_underscorednumber(self):
        for tree in self.parse_all(underscorednumber, minver=6):
            pass

    eleza test_redundantdef(self):
        for tree in self.parse_all(redundantdef, maxver=0,
                                expected_regex="^Cannot have two type comments on def"):
            pass

    eleza test_nonasciidef(self):
        for tree in self.parse_all(nonasciidef):
            self.assertEqual(tree.body[0].type_comment, "() -> àçčéñt")

    eleza test_forstmt(self):
        for tree in self.parse_all(forstmt):
            self.assertEqual(tree.body[0].type_comment, "int")
        tree = self.classic_parse(forstmt)
        self.assertEqual(tree.body[0].type_comment, None)

    eleza test_withstmt(self):
        for tree in self.parse_all(withstmt):
            self.assertEqual(tree.body[0].type_comment, "int")
        tree = self.classic_parse(withstmt)
        self.assertEqual(tree.body[0].type_comment, None)

    eleza test_vardecl(self):
        for tree in self.parse_all(vardecl):
            self.assertEqual(tree.body[0].type_comment, "int")
        tree = self.classic_parse(vardecl)
        self.assertEqual(tree.body[0].type_comment, None)

    eleza test_ignores(self):
        for tree in self.parse_all(ignores):
            self.assertEqual(
                [(ti.lineno, ti.tag) for ti in tree.type_ignores],
                [
                    (2, ''),
                    (5, ''),
                    (8, '[excuse]'),
                    (9, '=excuse'),
                    (10, ' [excuse]'),
                    (11, ' whatever'),
                ])
        tree = self.classic_parse(ignores)
        self.assertEqual(tree.type_ignores, [])

    eleza test_longargs(self):
        for tree in self.parse_all(longargs):
            for t in tree.body:
                # The expected args are encoded in the function name
                todo = set(t.name[1:])
                self.assertEqual(len(t.args.args) + len(t.args.posonlyargs),
                                 len(todo) - bool(t.args.vararg) - bool(t.args.kwarg))
                self.assertTrue(t.name.startswith('f'), t.name)
                for index, c in enumerate(t.name[1:]):
                    todo.remove(c)
                    ikiwa c == 'v':
                        arg = t.args.vararg
                    elikiwa c == 'k':
                        arg = t.args.kwarg
                    else:
                        assert 0 <= ord(c) - ord('a') < len(t.args.posonlyargs + t.args.args)
                        ikiwa index < len(t.args.posonlyargs):
                            arg = t.args.posonlyargs[ord(c) - ord('a')]
                        else:
                            arg = t.args.args[ord(c) - ord('a') - len(t.args.posonlyargs)]
                    self.assertEqual(arg.arg, c)  # That's the argument name
                    self.assertEqual(arg.type_comment, arg.arg.upper())
                assert not todo
        tree = self.classic_parse(longargs)
        for t in tree.body:
            for arg in t.args.args + [t.args.vararg, t.args.kwarg]:
                ikiwa arg is not None:
                    self.assertIsNone(arg.type_comment, "%s(%s:%r)" %
                                      (t.name, arg.arg, arg.type_comment))

    eleza test_inappropriate_type_comments(self):
        """Tests for inappropriately-placed type comments.

        These should be silently ignored with type comments off,
        but raise SyntaxError with type comments on.

        This is not meant to be exhaustive.
        """

        eleza check_both_ways(source):
            ast.parse(source, type_comments=False)
            for tree in self.parse_all(source, maxver=0):
                pass

        check_both_ways("pass  # type: int\n")
        check_both_ways("foo()  # type: int\n")
        check_both_ways("x += 1  # type: int\n")
        check_both_ways("while True:  # type: int\n  continue\n")
        check_both_ways("while True:\n  continue  # type: int\n")
        check_both_ways("try:  # type: int\n  pass\nfinally:\n  pass\n")
        check_both_ways("try:\n  pass\nfinally:  # type: int\n  pass\n")
        check_both_ways("pass  # type: ignorewhatever\n")
        check_both_ways("pass  # type: ignoreé\n")

    eleza test_func_type_input(self):

        eleza parse_func_type_input(source):
            rudisha ast.parse(source, "<unknown>", "func_type")

        # Some checks below will crash ikiwa the returned structure is wrong
        tree = parse_func_type_input("() -> int")
        self.assertEqual(tree.argtypes, [])
        self.assertEqual(tree.returns.id, "int")

        tree = parse_func_type_input("(int) -> List[str]")
        self.assertEqual(len(tree.argtypes), 1)
        arg = tree.argtypes[0]
        self.assertEqual(arg.id, "int")
        self.assertEqual(tree.returns.value.id, "List")
        self.assertEqual(tree.returns.slice.value.id, "str")

        tree = parse_func_type_input("(int, *str, **Any) -> float")
        self.assertEqual(tree.argtypes[0].id, "int")
        self.assertEqual(tree.argtypes[1].id, "str")
        self.assertEqual(tree.argtypes[2].id, "Any")
        self.assertEqual(tree.returns.id, "float")

        with self.assertRaises(SyntaxError):
            tree = parse_func_type_input("(int, *str, *Any) -> float")

        with self.assertRaises(SyntaxError):
            tree = parse_func_type_input("(int, **str, Any) -> float")

        with self.assertRaises(SyntaxError):
            tree = parse_func_type_input("(**int, **str) -> float")


ikiwa __name__ == '__main__':
    unittest.main()
