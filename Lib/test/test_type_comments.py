agiza ast
agiza sys
agiza unittest


funceleza = """\
eleza foo():
    # type: () -> int
    pita

eleza bar():  # type: () -> Tupu
    pita
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
    [x async kila x kwenye xs]
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
    pita
"""

forstmt = """\
kila a kwenye []:  # type: int
    pita
"""

withstmt = """\
ukijumuisha context() kama a:  # type: int
    pita
"""

vardecl = """\
a = 0  # type: int
"""

ignores = """\
eleza foo():
    pita  # type: ignore

eleza bar():
    x = 1  # type: ignore

eleza baz():
    pita  # type: ignore[excuse]
    pita  # type: ignore=excuse
    pita  # type: ignore [excuse]
    x = 1  # type: ignore whatever
"""

# Test kila long-form type-comments kwenye arguments.  A test function
# named 'fabvk' would have two positional args, a na b, plus a
# var-arg *v, plus a kw-arg **k.  It ni verified kwenye test_longargs()
# that it has exactly these arguments, no more, no fewer.
longargs = """\
eleza fa(
    a = 1,  # type: A
):
    pita

eleza fa(
    a = 1  # type: A
):
    pita

eleza fa(
    a = 1,  # type: A
    /
):
    pita

eleza fab(
    a,  # type: A
    b,  # type: B
):
    pita

eleza fab(
    a,  # type: A
    /,
    b,  # type: B
):
    pita

eleza fab(
    a,  # type: A
    b   # type: B
):
    pita

eleza fv(
    *v,  # type: V
):
    pita

eleza fv(
    *v  # type: V
):
    pita

eleza fk(
    **k,  # type: K
):
    pita

eleza fk(
    **k  # type: K
):
    pita

eleza fvk(
    *v,  # type: V
    **k,  # type: K
):
    pita

eleza fvk(
    *v,  # type: V
    **k  # type: K
):
    pita

eleza fav(
    a,  # type: A
    *v,  # type: V
):
    pita

eleza fav(
    a,  # type: A
    /,
    *v,  # type: V
):
    pita

eleza fav(
    a,  # type: A
    *v  # type: V
):
    pita

eleza fak(
    a,  # type: A
    **k,  # type: K
):
    pita

eleza fak(
    a,  # type: A
    /,
    **k,  # type: K
):
    pita

eleza fak(
    a,  # type: A
    **k  # type: K
):
    pita

eleza favk(
    a,  # type: A
    *v,  # type: V
    **k,  # type: K
):
    pita

eleza favk(
    a,  # type: A
    /,
    *v,  # type: V
    **k,  # type: K
):
    pita

eleza favk(
    a,  # type: A
    *v,  # type: V
    **k  # type: K
):
    pita
"""


kundi TypeCommentTests(unittest.TestCase):

    lowest = 4  # Lowest minor version supported
    highest = sys.version_info[1]  # Highest minor version

    eleza parse(self, source, feature_version=highest):
        rudisha ast.parse(source, type_comments=Kweli,
                         feature_version=feature_version)

    eleza parse_all(self, source, minver=lowest, maxver=highest, expected_regex=""):
        kila version kwenye range(self.lowest, self.highest + 1):
            feature_version = (3, version)
            ikiwa minver <= version <= maxver:
                jaribu:
                    tuma self.parse(source, feature_version)
                tatizo SyntaxError kama err:
                    ashiria SyntaxError(str(err) + f" feature_version={feature_version}")
            isipokua:
                ukijumuisha self.assertRaisesRegex(SyntaxError, expected_regex,
                                            msg=f"feature_version={feature_version}"):
                    self.parse(source, feature_version)

    eleza classic_parse(self, source):
        rudisha ast.parse(source)

    eleza test_funcdef(self):
        kila tree kwenye self.parse_all(funcdef):
            self.assertEqual(tree.body[0].type_comment, "() -> int")
            self.assertEqual(tree.body[1].type_comment, "() -> Tupu")
        tree = self.classic_parse(funcdef)
        self.assertEqual(tree.body[0].type_comment, Tupu)
        self.assertEqual(tree.body[1].type_comment, Tupu)

    eleza test_asyncdef(self):
        kila tree kwenye self.parse_all(asyncdef, minver=5):
            self.assertEqual(tree.body[0].type_comment, "() -> int")
            self.assertEqual(tree.body[1].type_comment, "() -> int")
        tree = self.classic_parse(asyncdef)
        self.assertEqual(tree.body[0].type_comment, Tupu)
        self.assertEqual(tree.body[1].type_comment, Tupu)

    eleza test_asyncvar(self):
        kila tree kwenye self.parse_all(asyncvar, maxver=6):
            pita

    eleza test_asynccomp(self):
        kila tree kwenye self.parse_all(asynccomp, minver=6):
            pita

    eleza test_matmul(self):
        kila tree kwenye self.parse_all(matmul, minver=5):
            pita

    eleza test_fstring(self):
        kila tree kwenye self.parse_all(fstring, minver=6):
            pita

    eleza test_underscorednumber(self):
        kila tree kwenye self.parse_all(underscorednumber, minver=6):
            pita

    eleza test_redundantdef(self):
        kila tree kwenye self.parse_all(redundantdef, maxver=0,
                                expected_regex="^Cansio have two type comments on def"):
            pita

    eleza test_nonasciidef(self):
        kila tree kwenye self.parse_all(nonasciidef):
            self.assertEqual(tree.body[0].type_comment, "() -> àçčéñt")

    eleza test_forstmt(self):
        kila tree kwenye self.parse_all(forstmt):
            self.assertEqual(tree.body[0].type_comment, "int")
        tree = self.classic_parse(forstmt)
        self.assertEqual(tree.body[0].type_comment, Tupu)

    eleza test_withstmt(self):
        kila tree kwenye self.parse_all(withstmt):
            self.assertEqual(tree.body[0].type_comment, "int")
        tree = self.classic_parse(withstmt)
        self.assertEqual(tree.body[0].type_comment, Tupu)

    eleza test_vardecl(self):
        kila tree kwenye self.parse_all(vardecl):
            self.assertEqual(tree.body[0].type_comment, "int")
        tree = self.classic_parse(vardecl)
        self.assertEqual(tree.body[0].type_comment, Tupu)

    eleza test_ignores(self):
        kila tree kwenye self.parse_all(ignores):
            self.assertEqual(
                [(ti.lineno, ti.tag) kila ti kwenye tree.type_ignores],
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
        kila tree kwenye self.parse_all(longargs):
            kila t kwenye tree.body:
                # The expected args are encoded kwenye the function name
                todo = set(t.name[1:])
                self.assertEqual(len(t.args.args) + len(t.args.posonlyargs),
                                 len(todo) - bool(t.args.vararg) - bool(t.args.kwarg))
                self.assertKweli(t.name.startswith('f'), t.name)
                kila index, c kwenye enumerate(t.name[1:]):
                    todo.remove(c)
                    ikiwa c == 'v':
                        arg = t.args.vararg
                    lasivyo c == 'k':
                        arg = t.args.kwarg
                    isipokua:
                        assert 0 <= ord(c) - ord('a') < len(t.args.posonlyargs + t.args.args)
                        ikiwa index < len(t.args.posonlyargs):
                            arg = t.args.posonlyargs[ord(c) - ord('a')]
                        isipokua:
                            arg = t.args.args[ord(c) - ord('a') - len(t.args.posonlyargs)]
                    self.assertEqual(arg.arg, c)  # That's the argument name
                    self.assertEqual(arg.type_comment, arg.arg.upper())
                assert sio todo
        tree = self.classic_parse(longargs)
        kila t kwenye tree.body:
            kila arg kwenye t.args.args + [t.args.vararg, t.args.kwarg]:
                ikiwa arg ni sio Tupu:
                    self.assertIsTupu(arg.type_comment, "%s(%s:%r)" %
                                      (t.name, arg.arg, arg.type_comment))

    eleza test_inappropriate_type_comments(self):
        """Tests kila inappropriately-placed type comments.

        These should be silently ignored ukijumuisha type comments off,
        but ashiria SyntaxError ukijumuisha type comments on.

        This ni sio meant to be exhaustive.
        """

        eleza check_both_ways(source):
            ast.parse(source, type_comments=Uongo)
            kila tree kwenye self.parse_all(source, maxver=0):
                pita

        check_both_ways("pita  # type: int\n")
        check_both_ways("foo()  # type: int\n")
        check_both_ways("x += 1  # type: int\n")
        check_both_ways("wakati Kweli:  # type: int\n  endelea\n")
        check_both_ways("wakati Kweli:\n  endelea  # type: int\n")
        check_both_ways("jaribu:  # type: int\n  pita\nmwishowe:\n  pita\n")
        check_both_ways("jaribu:\n  pita\nmwishowe:  # type: int\n  pita\n")
        check_both_ways("pita  # type: ignorewhatever\n")
        check_both_ways("pita  # type: ignoreé\n")

    eleza test_func_type_uliza(self):

        eleza parse_func_type_uliza(source):
            rudisha ast.parse(source, "<unknown>", "func_type")

        # Some checks below will crash ikiwa the returned structure ni wrong
        tree = parse_func_type_uliza("() -> int")
        self.assertEqual(tree.argtypes, [])
        self.assertEqual(tree.returns.id, "int")

        tree = parse_func_type_uliza("(int) -> List[str]")
        self.assertEqual(len(tree.argtypes), 1)
        arg = tree.argtypes[0]
        self.assertEqual(arg.id, "int")
        self.assertEqual(tree.returns.value.id, "List")
        self.assertEqual(tree.returns.slice.value.id, "str")

        tree = parse_func_type_uliza("(int, *str, **Any) -> float")
        self.assertEqual(tree.argtypes[0].id, "int")
        self.assertEqual(tree.argtypes[1].id, "str")
        self.assertEqual(tree.argtypes[2].id, "Any")
        self.assertEqual(tree.returns.id, "float")

        ukijumuisha self.assertRaises(SyntaxError):
            tree = parse_func_type_uliza("(int, *str, *Any) -> float")

        ukijumuisha self.assertRaises(SyntaxError):
            tree = parse_func_type_uliza("(int, **str, Any) -> float")

        ukijumuisha self.assertRaises(SyntaxError):
            tree = parse_func_type_uliza("(**int, **str) -> float")


ikiwa __name__ == '__main__':
    unittest.main()
