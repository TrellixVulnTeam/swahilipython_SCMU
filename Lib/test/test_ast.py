agiza ast
agiza dis
agiza os
agiza sys
agiza unittest
agiza warnings
agiza weakref
kutoka textwrap agiza dedent

kutoka test agiza support

eleza to_tuple(t):
    ikiwa t ni Tupu ama isinstance(t, (str, int, complex)):
        rudisha t
    lasivyo isinstance(t, list):
        rudisha [to_tuple(e) kila e kwenye t]
    result = [t.__class__.__name__]
    ikiwa hasattr(t, 'lineno') na hasattr(t, 'col_offset'):
        result.append((t.lineno, t.col_offset))
    ikiwa t._fields ni Tupu:
        rudisha tuple(result)
    kila f kwenye t._fields:
        result.append(to_tuple(getattr(t, f)))
    rudisha tuple(result)


# These tests are compiled through "exec"
# There should be at least one test per statement
exec_tests = [
    # Tupu
    "Tupu",
    # Module docstring
    "'module docstring'",
    # FunctionDef
    "eleza f(): pita",
    # FunctionDef ukijumuisha docstring
    "eleza f(): 'function docstring'",
    # FunctionDef ukijumuisha arg
    "eleza f(a): pita",
    # FunctionDef ukijumuisha arg na default value
    "eleza f(a=0): pita",
    # FunctionDef ukijumuisha varargs
    "eleza f(*args): pita",
    # FunctionDef ukijumuisha kwargs
    "eleza f(**kwargs): pita",
    # FunctionDef ukijumuisha all kind of args na docstring
    "eleza f(a, b=1, c=Tupu, d=[], e={}, *args, f=42, **kwargs): 'doc kila f()'",
    # ClassDef
    "kundi C:pita",
    # ClassDef ukijumuisha docstring
    "kundi C: 'docstring kila kundi C'",
    # ClassDef, new style class
    "kundi C(object): pita",
    # Return
    "eleza f():rudisha 1",
    # Delete
    "toa v",
    # Assign
    "v = 1",
    "a,b = c",
    "(a,b) = c",
    "[a,b] = c",
    # AugAssign
    "v += 1",
    # For
    "kila v kwenye v:pita",
    # While
    "wakati v:pita",
    # If
    "ikiwa v:pita",
    # With
    "ukijumuisha x kama y: pita",
    "ukijumuisha x kama y, z kama q: pita",
    # Raise
    "ashiria Exception('string')",
    # TryExcept
    "jaribu:\n  pita\ntatizo Exception:\n  pita",
    # TryFinally
    "jaribu:\n  pita\nmwishowe:\n  pita",
    # Assert
    "assert v",
    # Import
    "agiza sys",
    # ImportFrom
    "kutoka sys agiza v",
    # Global
    "global v",
    # Expr
    "1",
    # Pass,
    "pita",
    # Break
    "kila v kwenye v:koma",
    # Continue
    "kila v kwenye v:endelea",
    # kila statements ukijumuisha naked tuples (see http://bugs.python.org/issue6704)
    "kila a,b kwenye c: pita",
    "kila (a,b) kwenye c: pita",
    "kila [a,b] kwenye c: pita",
    # Multiline generator expression (test kila .lineno & .col_offset)
    """(
    (
    Aa
    ,
       Bb
    )
    for
    Aa
    ,
    Bb kwenye Cc
    )""",
    # dictcomp
    "{a : b kila w kwenye x kila m kwenye p ikiwa g}",
    # dictcomp ukijumuisha naked tuple
    "{a : b kila v,w kwenye x}",
    # setcomp
    "{r kila l kwenye x ikiwa g}",
    # setcomp ukijumuisha naked tuple
    "{r kila l,m kwenye x}",
    # AsyncFunctionDef
    "async eleza f():\n 'async function'\n await something()",
    # AsyncFor
    "async eleza f():\n async kila e kwenye i: 1\n isipokua: 2",
    # AsyncWith
    "async eleza f():\n async ukijumuisha a kama b: 1",
    # PEP 448: Additional Unpacking Generalizations
    "{**{1:2}, 2:3}",
    "{*{1, 2}, 3}",
    # Asynchronous comprehensions
    "async eleza f():\n [i async kila b kwenye c]",
    # Decorated FunctionDef
    "@deco1\n@deco2()\neleza f(): pita",
    # Decorated AsyncFunctionDef
    "@deco1\n@deco2()\nasync eleza f(): pita",
    # Decorated ClassDef
    "@deco1\n@deco2()\nkundi C: pita",
    # Decorator ukijumuisha generator argument
    "@deco(a kila a kwenye b)\neleza f(): pita",
    # Simple assignment expression
    "(a := 1)",
    # Positional-only arguments
    "eleza f(a, /,): pita",
    "eleza f(a, /, c, d, e): pita",
    "eleza f(a, /, c, *, d, e): pita",
    "eleza f(a, /, c, *, d, e, **kwargs): pita",
    # Positional-only arguments ukijumuisha defaults
    "eleza f(a=1, /,): pita",
    "eleza f(a=1, /, b=2, c=4): pita",
    "eleza f(a=1, /, b=2, *, c=4): pita",
    "eleza f(a=1, /, b=2, *, c): pita",
    "eleza f(a=1, /, b=2, *, c=4, **kwargs): pita",
    "eleza f(a=1, /, b=2, *, c, **kwargs): pita",

]

# These are compiled through "single"
# because of overlap ukijumuisha "eval", it just tests what
# can't be tested ukijumuisha "eval"
single_tests = [
    "1+2"
]

# These are compiled through "eval"
# It should test all expressions
eval_tests = [
  # Tupu
  "Tupu",
  # BoolOp
  "a na b",
  # BinOp
  "a + b",
  # UnaryOp
  "not v",
  # Lambda
  "lambda:Tupu",
  # Dict
  "{ 1:2 }",
  # Empty dict
  "{}",
  # Set
  "{Tupu,}",
  # Multiline dict (test kila .lineno & .col_offset)
  """{
      1
        :
          2
     }""",
  # ListComp
  "[a kila b kwenye c ikiwa d]",
  # GeneratorExp
  "(a kila b kwenye c ikiwa d)",
  # Comprehensions ukijumuisha multiple kila targets
  "[(a,b) kila a,b kwenye c]",
  "[(a,b) kila (a,b) kwenye c]",
  "[(a,b) kila [a,b] kwenye c]",
  "{(a,b) kila a,b kwenye c}",
  "{(a,b) kila (a,b) kwenye c}",
  "{(a,b) kila [a,b] kwenye c}",
  "((a,b) kila a,b kwenye c)",
  "((a,b) kila (a,b) kwenye c)",
  "((a,b) kila [a,b] kwenye c)",
  # Yield - tuma expressions can't work outside a function
  #
  # Compare
  "1 < 2 < 3",
  # Call
  "f(1,2,c=3,*d,**e)",
  # Call ukijumuisha a generator argument
  "f(a kila a kwenye b)",
  # Num
  "10",
  # Str
  "'string'",
  # Attribute
  "a.b",
  # Subscript
  "a[b:c]",
  # Name
  "v",
  # List
  "[1,2,3]",
  # Empty list
  "[]",
  # Tuple
  "1,2,3",
  # Tuple
  "(1,2,3)",
  # Empty tuple
  "()",
  # Combination
  "a.b.c.d(a.b[1:2])",

]

# TODO: expr_context, slice, boolop, operator, unaryop, cmpop, comprehension
# excepthandler, arguments, keywords, alias

kundi AST_Tests(unittest.TestCase):

    eleza _assertKweliorder(self, ast_node, parent_pos):
        ikiwa sio isinstance(ast_node, ast.AST) ama ast_node._fields ni Tupu:
            return
        ikiwa isinstance(ast_node, (ast.expr, ast.stmt, ast.excepthandler)):
            node_pos = (ast_node.lineno, ast_node.col_offset)
            self.assertGreaterEqual(node_pos, parent_pos)
            parent_pos = (ast_node.lineno, ast_node.col_offset)
        kila name kwenye ast_node._fields:
            value = getattr(ast_node, name)
            ikiwa isinstance(value, list):
                first_pos = parent_pos
                ikiwa value na name == 'decorator_list':
                    first_pos = (value[0].lineno, value[0].col_offset)
                kila child kwenye value:
                    self._assertKweliorder(child, first_pos)
            lasivyo value ni sio Tupu:
                self._assertKweliorder(value, parent_pos)

    eleza test_AST_objects(self):
        x = ast.AST()
        self.assertEqual(x._fields, ())
        x.foobar = 42
        self.assertEqual(x.foobar, 42)
        self.assertEqual(x.__dict__["foobar"], 42)

        ukijumuisha self.assertRaises(AttributeError):
            x.vararg

        ukijumuisha self.assertRaises(TypeError):
            # "_ast.AST constructor takes 0 positional arguments"
            ast.AST(2)

    eleza test_AST_garbage_collection(self):
        kundi X:
            pita
        a = ast.AST()
        a.x = X()
        a.x.a = a
        ref = weakref.ref(a.x)
        toa a
        support.gc_collect()
        self.assertIsTupu(ref())

    eleza test_snippets(self):
        kila input, output, kind kwenye ((exec_tests, exec_results, "exec"),
                                    (single_tests, single_results, "single"),
                                    (eval_tests, eval_results, "eval")):
            kila i, o kwenye zip(input, output):
                ukijumuisha self.subTest(action="parsing", input=i):
                    ast_tree = compile(i, "?", kind, ast.PyCF_ONLY_AST)
                    self.assertEqual(to_tuple(ast_tree), o)
                    self._assertKweliorder(ast_tree, (0, 0))
                ukijumuisha self.subTest(action="compiling", input=i, kind=kind):
                    compile(ast_tree, "?", kind)

    eleza test_ast_validation(self):
        # compile() ni the only function that calls PyAST_Validate
        snippets_to_validate = exec_tests + single_tests + eval_tests
        kila snippet kwenye snippets_to_validate:
            tree = ast.parse(snippet)
            compile(tree, '<string>', 'exec')

    eleza test_slice(self):
        slc = ast.parse("x[::]").body[0].value.slice
        self.assertIsTupu(slc.upper)
        self.assertIsTupu(slc.lower)
        self.assertIsTupu(slc.step)

    eleza test_from_import(self):
        im = ast.parse("kutoka . agiza y").body[0]
        self.assertIsTupu(im.module)

    eleza test_non_interned_future_from_ast(self):
        mod = ast.parse("kutoka __future__ agiza division")
        self.assertIsInstance(mod.body[0], ast.ImportFrom)
        mod.body[0].module = " __future__ ".strip()
        compile(mod, "<test>", "exec")

    eleza test_base_classes(self):
        self.assertKweli(issubclass(ast.For, ast.stmt))
        self.assertKweli(issubclass(ast.Name, ast.expr))
        self.assertKweli(issubclass(ast.stmt, ast.AST))
        self.assertKweli(issubclass(ast.expr, ast.AST))
        self.assertKweli(issubclass(ast.comprehension, ast.AST))
        self.assertKweli(issubclass(ast.Gt, ast.AST))

    eleza test_field_attr_existence(self):
        kila name, item kwenye ast.__dict__.items():
            ikiwa isinstance(item, type) na name != 'AST' na name[0].isupper():
                x = item()
                ikiwa isinstance(x, ast.AST):
                    self.assertEqual(type(x._fields), tuple)

    eleza test_arguments(self):
        x = ast.arguments()
        self.assertEqual(x._fields, ('posonlyargs', 'args', 'vararg', 'kwonlyargs',
                                     'kw_defaults', 'kwarg', 'defaults'))

        ukijumuisha self.assertRaises(AttributeError):
            x.vararg

        x = ast.arguments(*range(1, 8))
        self.assertEqual(x.vararg, 3)

    eleza test_field_attr_writable(self):
        x = ast.Num()
        # We can assign to _fields
        x._fields = 666
        self.assertEqual(x._fields, 666)

    eleza test_classattrs(self):
        x = ast.Num()
        self.assertEqual(x._fields, ('value', 'kind'))

        ukijumuisha self.assertRaises(AttributeError):
            x.value

        ukijumuisha self.assertRaises(AttributeError):
            x.n

        x = ast.Num(42)
        self.assertEqual(x.value, 42)
        self.assertEqual(x.n, 42)

        ukijumuisha self.assertRaises(AttributeError):
            x.lineno

        ukijumuisha self.assertRaises(AttributeError):
            x.foobar

        x = ast.Num(lineno=2)
        self.assertEqual(x.lineno, 2)

        x = ast.Num(42, lineno=0)
        self.assertEqual(x.lineno, 0)
        self.assertEqual(x._fields, ('value', 'kind'))
        self.assertEqual(x.value, 42)
        self.assertEqual(x.n, 42)

        self.assertRaises(TypeError, ast.Num, 1, Tupu, 2)
        self.assertRaises(TypeError, ast.Num, 1, Tupu, 2, lineno=0)

        self.assertEqual(ast.Num(42).n, 42)
        self.assertEqual(ast.Num(4.25).n, 4.25)
        self.assertEqual(ast.Num(4.25j).n, 4.25j)
        self.assertEqual(ast.Str('42').s, '42')
        self.assertEqual(ast.Bytes(b'42').s, b'42')
        self.assertIs(ast.NameConstant(Kweli).value, Kweli)
        self.assertIs(ast.NameConstant(Uongo).value, Uongo)
        self.assertIs(ast.NameConstant(Tupu).value, Tupu)

        self.assertEqual(ast.Constant(42).value, 42)
        self.assertEqual(ast.Constant(4.25).value, 4.25)
        self.assertEqual(ast.Constant(4.25j).value, 4.25j)
        self.assertEqual(ast.Constant('42').value, '42')
        self.assertEqual(ast.Constant(b'42').value, b'42')
        self.assertIs(ast.Constant(Kweli).value, Kweli)
        self.assertIs(ast.Constant(Uongo).value, Uongo)
        self.assertIs(ast.Constant(Tupu).value, Tupu)
        self.assertIs(ast.Constant(...).value, ...)

    eleza test_realtype(self):
        self.assertEqual(type(ast.Num(42)), ast.Constant)
        self.assertEqual(type(ast.Num(4.25)), ast.Constant)
        self.assertEqual(type(ast.Num(4.25j)), ast.Constant)
        self.assertEqual(type(ast.Str('42')), ast.Constant)
        self.assertEqual(type(ast.Bytes(b'42')), ast.Constant)
        self.assertEqual(type(ast.NameConstant(Kweli)), ast.Constant)
        self.assertEqual(type(ast.NameConstant(Uongo)), ast.Constant)
        self.assertEqual(type(ast.NameConstant(Tupu)), ast.Constant)
        self.assertEqual(type(ast.Ellipsis()), ast.Constant)

    eleza test_isinstance(self):
        self.assertKweli(isinstance(ast.Num(42), ast.Num))
        self.assertKweli(isinstance(ast.Num(4.2), ast.Num))
        self.assertKweli(isinstance(ast.Num(4.2j), ast.Num))
        self.assertKweli(isinstance(ast.Str('42'), ast.Str))
        self.assertKweli(isinstance(ast.Bytes(b'42'), ast.Bytes))
        self.assertKweli(isinstance(ast.NameConstant(Kweli), ast.NameConstant))
        self.assertKweli(isinstance(ast.NameConstant(Uongo), ast.NameConstant))
        self.assertKweli(isinstance(ast.NameConstant(Tupu), ast.NameConstant))
        self.assertKweli(isinstance(ast.Ellipsis(), ast.Ellipsis))

        self.assertKweli(isinstance(ast.Constant(42), ast.Num))
        self.assertKweli(isinstance(ast.Constant(4.2), ast.Num))
        self.assertKweli(isinstance(ast.Constant(4.2j), ast.Num))
        self.assertKweli(isinstance(ast.Constant('42'), ast.Str))
        self.assertKweli(isinstance(ast.Constant(b'42'), ast.Bytes))
        self.assertKweli(isinstance(ast.Constant(Kweli), ast.NameConstant))
        self.assertKweli(isinstance(ast.Constant(Uongo), ast.NameConstant))
        self.assertKweli(isinstance(ast.Constant(Tupu), ast.NameConstant))
        self.assertKweli(isinstance(ast.Constant(...), ast.Ellipsis))

        self.assertUongo(isinstance(ast.Str('42'), ast.Num))
        self.assertUongo(isinstance(ast.Num(42), ast.Str))
        self.assertUongo(isinstance(ast.Str('42'), ast.Bytes))
        self.assertUongo(isinstance(ast.Num(42), ast.NameConstant))
        self.assertUongo(isinstance(ast.Num(42), ast.Ellipsis))
        self.assertUongo(isinstance(ast.NameConstant(Kweli), ast.Num))
        self.assertUongo(isinstance(ast.NameConstant(Uongo), ast.Num))

        self.assertUongo(isinstance(ast.Constant('42'), ast.Num))
        self.assertUongo(isinstance(ast.Constant(42), ast.Str))
        self.assertUongo(isinstance(ast.Constant('42'), ast.Bytes))
        self.assertUongo(isinstance(ast.Constant(42), ast.NameConstant))
        self.assertUongo(isinstance(ast.Constant(42), ast.Ellipsis))
        self.assertUongo(isinstance(ast.Constant(Kweli), ast.Num))
        self.assertUongo(isinstance(ast.Constant(Uongo), ast.Num))

        self.assertUongo(isinstance(ast.Constant(), ast.Num))
        self.assertUongo(isinstance(ast.Constant(), ast.Str))
        self.assertUongo(isinstance(ast.Constant(), ast.Bytes))
        self.assertUongo(isinstance(ast.Constant(), ast.NameConstant))
        self.assertUongo(isinstance(ast.Constant(), ast.Ellipsis))

        kundi S(str): pita
        self.assertKweli(isinstance(ast.Constant(S('42')), ast.Str))
        self.assertUongo(isinstance(ast.Constant(S('42')), ast.Num))

    eleza test_subclasses(self):
        kundi N(ast.Num):
            eleza __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.z = 'spam'
        kundi N2(ast.Num):
            pita

        n = N(42)
        self.assertEqual(n.n, 42)
        self.assertEqual(n.z, 'spam')
        self.assertEqual(type(n), N)
        self.assertKweli(isinstance(n, N))
        self.assertKweli(isinstance(n, ast.Num))
        self.assertUongo(isinstance(n, N2))
        self.assertUongo(isinstance(ast.Num(42), N))
        n = N(n=42)
        self.assertEqual(n.n, 42)
        self.assertEqual(type(n), N)

    eleza test_module(self):
        body = [ast.Num(42)]
        x = ast.Module(body, [])
        self.assertEqual(x.body, body)

    eleza test_nodeclasses(self):
        # Zero arguments constructor explicitly allowed
        x = ast.BinOp()
        self.assertEqual(x._fields, ('left', 'op', 'right'))

        # Random attribute allowed too
        x.foobarbaz = 5
        self.assertEqual(x.foobarbaz, 5)

        n1 = ast.Num(1)
        n3 = ast.Num(3)
        addop = ast.Add()
        x = ast.BinOp(n1, addop, n3)
        self.assertEqual(x.left, n1)
        self.assertEqual(x.op, addop)
        self.assertEqual(x.right, n3)

        x = ast.BinOp(1, 2, 3)
        self.assertEqual(x.left, 1)
        self.assertEqual(x.op, 2)
        self.assertEqual(x.right, 3)

        x = ast.BinOp(1, 2, 3, lineno=0)
        self.assertEqual(x.left, 1)
        self.assertEqual(x.op, 2)
        self.assertEqual(x.right, 3)
        self.assertEqual(x.lineno, 0)

        # node raises exception when given too many arguments
        self.assertRaises(TypeError, ast.BinOp, 1, 2, 3, 4)
        # node raises exception when given too many arguments
        self.assertRaises(TypeError, ast.BinOp, 1, 2, 3, 4, lineno=0)

        # can set attributes through kwargs too
        x = ast.BinOp(left=1, op=2, right=3, lineno=0)
        self.assertEqual(x.left, 1)
        self.assertEqual(x.op, 2)
        self.assertEqual(x.right, 3)
        self.assertEqual(x.lineno, 0)

        # Random kwargs also allowed
        x = ast.BinOp(1, 2, 3, foobarbaz=42)
        self.assertEqual(x.foobarbaz, 42)

    eleza test_no_fields(self):
        # this used to fail because Sub._fields was Tupu
        x = ast.Sub()
        self.assertEqual(x._fields, ())

    eleza test_pickling(self):
        agiza pickle
        mods = [pickle]
        jaribu:
            agiza cPickle
            mods.append(cPickle)
        tatizo ImportError:
            pita
        protocols = [0, 1, 2]
        kila mod kwenye mods:
            kila protocol kwenye protocols:
                kila ast kwenye (compile(i, "?", "exec", 0x400) kila i kwenye exec_tests):
                    ast2 = mod.loads(mod.dumps(ast, protocol))
                    self.assertEqual(to_tuple(ast2), to_tuple(ast))

    eleza test_invalid_sum(self):
        pos = dict(lineno=2, col_offset=3)
        m = ast.Module([ast.Expr(ast.expr(**pos), **pos)], [])
        ukijumuisha self.assertRaises(TypeError) kama cm:
            compile(m, "<test>", "exec")
        self.assertIn("but got <_ast.expr", str(cm.exception))

    eleza test_invalid_identitifer(self):
        m = ast.Module([ast.Expr(ast.Name(42, ast.Load()))], [])
        ast.fix_missing_locations(m)
        ukijumuisha self.assertRaises(TypeError) kama cm:
            compile(m, "<test>", "exec")
        self.assertIn("identifier must be of type str", str(cm.exception))

    eleza test_empty_tuma_from(self):
        # Issue 16546: tuma kutoka value ni sio optional.
        empty_tuma_kutoka = ast.parse("eleza f():\n tuma kutoka g()")
        empty_tuma_from.body[0].body[0].value.value = Tupu
        ukijumuisha self.assertRaises(ValueError) kama cm:
            compile(empty_tuma_from, "<test>", "exec")
        self.assertIn("field value ni required", str(cm.exception))

    @support.cpython_only
    eleza test_issue31592(self):
        # There shouldn't be an assertion failure kwenye case of a bad
        # unicodedata.normalize().
        agiza unicodedata
        eleza bad_normalize(*args):
            rudisha Tupu
        ukijumuisha support.swap_attr(unicodedata, 'normalize', bad_normalize):
            self.assertRaises(TypeError, ast.parse, '\u03D5')

    eleza test_issue18374_binop_col_offset(self):
        tree = ast.parse('4+5+6+7')
        parent_binop = tree.body[0].value
        child_binop = parent_binop.left
        grandchild_binop = child_binop.left
        self.assertEqual(parent_binop.col_offset, 0)
        self.assertEqual(parent_binop.end_col_offset, 7)
        self.assertEqual(child_binop.col_offset, 0)
        self.assertEqual(child_binop.end_col_offset, 5)
        self.assertEqual(grandchild_binop.col_offset, 0)
        self.assertEqual(grandchild_binop.end_col_offset, 3)

        tree = ast.parse('4+5-\\\n 6-7')
        parent_binop = tree.body[0].value
        child_binop = parent_binop.left
        grandchild_binop = child_binop.left
        self.assertEqual(parent_binop.col_offset, 0)
        self.assertEqual(parent_binop.lineno, 1)
        self.assertEqual(parent_binop.end_col_offset, 4)
        self.assertEqual(parent_binop.end_lineno, 2)

        self.assertEqual(child_binop.col_offset, 0)
        self.assertEqual(child_binop.lineno, 1)
        self.assertEqual(child_binop.end_col_offset, 2)
        self.assertEqual(child_binop.end_lineno, 2)

        self.assertEqual(grandchild_binop.col_offset, 0)
        self.assertEqual(grandchild_binop.lineno, 1)
        self.assertEqual(grandchild_binop.end_col_offset, 3)
        self.assertEqual(grandchild_binop.end_lineno, 1)

kundi ASTHelpers_Test(unittest.TestCase):
    maxDiff = Tupu

    eleza test_parse(self):
        a = ast.parse('foo(1 + 1)')
        b = compile('foo(1 + 1)', '<unknown>', 'exec', ast.PyCF_ONLY_AST)
        self.assertEqual(ast.dump(a), ast.dump(b))

    eleza test_parse_in_error(self):
        jaribu:
            1/0
        tatizo Exception:
            ukijumuisha self.assertRaises(SyntaxError) kama e:
                ast.literal_eval(r"'\U'")
            self.assertIsNotTupu(e.exception.__context__)

    eleza test_dump(self):
        node = ast.parse('spam(eggs, "and cheese")')
        self.assertEqual(ast.dump(node),
            "Module(body=[Expr(value=Call(func=Name(id='spam', ctx=Load()), "
            "args=[Name(id='eggs', ctx=Load()), Constant(value='and cheese', kind=Tupu)], "
            "keywords=[]))], type_ignores=[])"
        )
        self.assertEqual(ast.dump(node, annotate_fields=Uongo),
            "Module([Expr(Call(Name('spam', Load()), [Name('eggs', Load()), "
            "Constant('and cheese', Tupu)], []))], [])"
        )
        self.assertEqual(ast.dump(node, include_attributes=Kweli),
            "Module(body=[Expr(value=Call(func=Name(id='spam', ctx=Load(), "
            "lineno=1, col_offset=0, end_lineno=1, end_col_offset=4), "
            "args=[Name(id='eggs', ctx=Load(), lineno=1, col_offset=5, "
            "end_lineno=1, end_col_offset=9), Constant(value='and cheese', kind=Tupu, "
            "lineno=1, col_offset=11, end_lineno=1, end_col_offset=23)], keywords=[], "
            "lineno=1, col_offset=0, end_lineno=1, end_col_offset=24), "
            "lineno=1, col_offset=0, end_lineno=1, end_col_offset=24)], type_ignores=[])"
        )

    eleza test_dump_incomplete(self):
        node = ast.Raise(lineno=3, col_offset=4)
        self.assertEqual(ast.dump(node),
            "Raise()"
        )
        self.assertEqual(ast.dump(node, include_attributes=Kweli),
            "Raise(lineno=3, col_offset=4)"
        )
        node = ast.Raise(exc=ast.Name(id='e', ctx=ast.Load()), lineno=3, col_offset=4)
        self.assertEqual(ast.dump(node),
            "Raise(exc=Name(id='e', ctx=Load()))"
        )
        self.assertEqual(ast.dump(node, annotate_fields=Uongo),
            "Raise(Name('e', Load()))"
        )
        self.assertEqual(ast.dump(node, include_attributes=Kweli),
            "Raise(exc=Name(id='e', ctx=Load()), lineno=3, col_offset=4)"
        )
        self.assertEqual(ast.dump(node, annotate_fields=Uongo, include_attributes=Kweli),
            "Raise(Name('e', Load()), lineno=3, col_offset=4)"
        )
        node = ast.Raise(cause=ast.Name(id='e', ctx=ast.Load()))
        self.assertEqual(ast.dump(node),
            "Raise(cause=Name(id='e', ctx=Load()))"
        )
        self.assertEqual(ast.dump(node, annotate_fields=Uongo),
            "Raise(cause=Name('e', Load()))"
        )

    eleza test_copy_location(self):
        src = ast.parse('1 + 1', mode='eval')
        src.body.right = ast.copy_location(ast.Num(2), src.body.right)
        self.assertEqual(ast.dump(src, include_attributes=Kweli),
            'Expression(body=BinOp(left=Constant(value=1, kind=Tupu, lineno=1, col_offset=0, '
            'end_lineno=1, end_col_offset=1), op=Add(), right=Constant(value=2, '
            'lineno=1, col_offset=4, end_lineno=1, end_col_offset=5), lineno=1, '
            'col_offset=0, end_lineno=1, end_col_offset=5))'
        )

    eleza test_fix_missing_locations(self):
        src = ast.parse('write("spam")')
        src.body.append(ast.Expr(ast.Call(ast.Name('spam', ast.Load()),
                                          [ast.Str('eggs')], [])))
        self.assertEqual(src, ast.fix_missing_locations(src))
        self.maxDiff = Tupu
        self.assertEqual(ast.dump(src, include_attributes=Kweli),
            "Module(body=[Expr(value=Call(func=Name(id='write', ctx=Load(), "
            "lineno=1, col_offset=0, end_lineno=1, end_col_offset=5), "
            "args=[Constant(value='spam', kind=Tupu, lineno=1, col_offset=6, end_lineno=1, "
            "end_col_offset=12)], keywords=[], lineno=1, col_offset=0, end_lineno=1, "
            "end_col_offset=13), lineno=1, col_offset=0, end_lineno=1, "
            "end_col_offset=13), Expr(value=Call(func=Name(id='spam', ctx=Load(), "
            "lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), "
            "args=[Constant(value='eggs', lineno=1, col_offset=0, end_lineno=1, "
            "end_col_offset=0)], keywords=[], lineno=1, col_offset=0, end_lineno=1, "
            "end_col_offset=0), lineno=1, col_offset=0, end_lineno=1, end_col_offset=0)], "
            "type_ignores=[])"
        )

    eleza test_increment_lineno(self):
        src = ast.parse('1 + 1', mode='eval')
        self.assertEqual(ast.increment_lineno(src, n=3), src)
        self.assertEqual(ast.dump(src, include_attributes=Kweli),
            'Expression(body=BinOp(left=Constant(value=1, kind=Tupu, lineno=4, col_offset=0, '
            'end_lineno=4, end_col_offset=1), op=Add(), right=Constant(value=1, kind=Tupu, '
            'lineno=4, col_offset=4, end_lineno=4, end_col_offset=5), lineno=4, '
            'col_offset=0, end_lineno=4, end_col_offset=5))'
        )
        # issue10869: do sio increment lineno of root twice
        src = ast.parse('1 + 1', mode='eval')
        self.assertEqual(ast.increment_lineno(src.body, n=3), src.body)
        self.assertEqual(ast.dump(src, include_attributes=Kweli),
            'Expression(body=BinOp(left=Constant(value=1, kind=Tupu, lineno=4, col_offset=0, '
            'end_lineno=4, end_col_offset=1), op=Add(), right=Constant(value=1, kind=Tupu, '
            'lineno=4, col_offset=4, end_lineno=4, end_col_offset=5), lineno=4, '
            'col_offset=0, end_lineno=4, end_col_offset=5))'
        )

    eleza test_iter_fields(self):
        node = ast.parse('foo()', mode='eval')
        d = dict(ast.iter_fields(node.body))
        self.assertEqual(d.pop('func').id, 'foo')
        self.assertEqual(d, {'keywords': [], 'args': []})

    eleza test_iter_child_nodes(self):
        node = ast.parse("spam(23, 42, eggs='leek')", mode='eval')
        self.assertEqual(len(list(ast.iter_child_nodes(node.body))), 4)
        iterator = ast.iter_child_nodes(node.body)
        self.assertEqual(next(iterator).id, 'spam')
        self.assertEqual(next(iterator).value, 23)
        self.assertEqual(next(iterator).value, 42)
        self.assertEqual(ast.dump(next(iterator)),
            "keyword(arg='eggs', value=Constant(value='leek', kind=Tupu))"
        )

    eleza test_get_docstring(self):
        node = ast.parse('"""line one\n  line two"""')
        self.assertEqual(ast.get_docstring(node),
                         'line one\nline two')

        node = ast.parse('kundi foo:\n  """line one\n  line two"""')
        self.assertEqual(ast.get_docstring(node.body[0]),
                         'line one\nline two')

        node = ast.parse('eleza foo():\n  """line one\n  line two"""')
        self.assertEqual(ast.get_docstring(node.body[0]),
                         'line one\nline two')

        node = ast.parse('async eleza foo():\n  """spam\n  ham"""')
        self.assertEqual(ast.get_docstring(node.body[0]), 'spam\nham')

    eleza test_get_docstring_none(self):
        self.assertIsTupu(ast.get_docstring(ast.parse('')))
        node = ast.parse('x = "not docstring"')
        self.assertIsTupu(ast.get_docstring(node))
        node = ast.parse('eleza foo():\n  pita')
        self.assertIsTupu(ast.get_docstring(node))

        node = ast.parse('kundi foo:\n  pita')
        self.assertIsTupu(ast.get_docstring(node.body[0]))
        node = ast.parse('kundi foo:\n  x = "not docstring"')
        self.assertIsTupu(ast.get_docstring(node.body[0]))
        node = ast.parse('kundi foo:\n  eleza bar(self): pita')
        self.assertIsTupu(ast.get_docstring(node.body[0]))

        node = ast.parse('eleza foo():\n  pita')
        self.assertIsTupu(ast.get_docstring(node.body[0]))
        node = ast.parse('eleza foo():\n  x = "not docstring"')
        self.assertIsTupu(ast.get_docstring(node.body[0]))

        node = ast.parse('async eleza foo():\n  pita')
        self.assertIsTupu(ast.get_docstring(node.body[0]))
        node = ast.parse('async eleza foo():\n  x = "not docstring"')
        self.assertIsTupu(ast.get_docstring(node.body[0]))

    eleza test_multi_line_docstring_col_offset_and_lineno_issue16806(self):
        node = ast.parse(
            '"""line one\nline two"""\n\n'
            'eleza foo():\n  """line one\n  line two"""\n\n'
            '  eleza bar():\n    """line one\n    line two"""\n'
            '  """line one\n  line two"""\n'
            '"""line one\nline two"""\n\n'
        )
        self.assertEqual(node.body[0].col_offset, 0)
        self.assertEqual(node.body[0].lineno, 1)
        self.assertEqual(node.body[1].body[0].col_offset, 2)
        self.assertEqual(node.body[1].body[0].lineno, 5)
        self.assertEqual(node.body[1].body[1].body[0].col_offset, 4)
        self.assertEqual(node.body[1].body[1].body[0].lineno, 9)
        self.assertEqual(node.body[1].body[2].col_offset, 2)
        self.assertEqual(node.body[1].body[2].lineno, 11)
        self.assertEqual(node.body[2].col_offset, 0)
        self.assertEqual(node.body[2].lineno, 13)

    eleza test_literal_eval(self):
        self.assertEqual(ast.literal_eval('[1, 2, 3]'), [1, 2, 3])
        self.assertEqual(ast.literal_eval('{"foo": 42}'), {"foo": 42})
        self.assertEqual(ast.literal_eval('(Kweli, Uongo, Tupu)'), (Kweli, Uongo, Tupu))
        self.assertEqual(ast.literal_eval('{1, 2, 3}'), {1, 2, 3})
        self.assertEqual(ast.literal_eval('b"hi"'), b"hi")
        self.assertRaises(ValueError, ast.literal_eval, 'foo()')
        self.assertEqual(ast.literal_eval('6'), 6)
        self.assertEqual(ast.literal_eval('+6'), 6)
        self.assertEqual(ast.literal_eval('-6'), -6)
        self.assertEqual(ast.literal_eval('3.25'), 3.25)
        self.assertEqual(ast.literal_eval('+3.25'), 3.25)
        self.assertEqual(ast.literal_eval('-3.25'), -3.25)
        self.assertEqual(repr(ast.literal_eval('-0.0')), '-0.0')
        self.assertRaises(ValueError, ast.literal_eval, '++6')
        self.assertRaises(ValueError, ast.literal_eval, '+Kweli')
        self.assertRaises(ValueError, ast.literal_eval, '2+3')

    eleza test_literal_eval_complex(self):
        # Issue #4907
        self.assertEqual(ast.literal_eval('6j'), 6j)
        self.assertEqual(ast.literal_eval('-6j'), -6j)
        self.assertEqual(ast.literal_eval('6.75j'), 6.75j)
        self.assertEqual(ast.literal_eval('-6.75j'), -6.75j)
        self.assertEqual(ast.literal_eval('3+6j'), 3+6j)
        self.assertEqual(ast.literal_eval('-3+6j'), -3+6j)
        self.assertEqual(ast.literal_eval('3-6j'), 3-6j)
        self.assertEqual(ast.literal_eval('-3-6j'), -3-6j)
        self.assertEqual(ast.literal_eval('3.25+6.75j'), 3.25+6.75j)
        self.assertEqual(ast.literal_eval('-3.25+6.75j'), -3.25+6.75j)
        self.assertEqual(ast.literal_eval('3.25-6.75j'), 3.25-6.75j)
        self.assertEqual(ast.literal_eval('-3.25-6.75j'), -3.25-6.75j)
        self.assertEqual(ast.literal_eval('(3+6j)'), 3+6j)
        self.assertRaises(ValueError, ast.literal_eval, '-6j+3')
        self.assertRaises(ValueError, ast.literal_eval, '-6j+3j')
        self.assertRaises(ValueError, ast.literal_eval, '3+-6j')
        self.assertRaises(ValueError, ast.literal_eval, '3+(0+6j)')
        self.assertRaises(ValueError, ast.literal_eval, '-(3+6j)')

    eleza test_bad_integer(self):
        # issue13436: Bad error message ukijumuisha invalid numeric values
        body = [ast.ImportFrom(module='time',
                               names=[ast.alias(name='sleep')],
                               level=Tupu,
                               lineno=Tupu, col_offset=Tupu)]
        mod = ast.Module(body, [])
        ukijumuisha self.assertRaises(ValueError) kama cm:
            compile(mod, 'test', 'exec')
        self.assertIn("invalid integer value: Tupu", str(cm.exception))

    eleza test_level_as_none(self):
        body = [ast.ImportFrom(module='time',
                               names=[ast.alias(name='sleep')],
                               level=Tupu,
                               lineno=0, col_offset=0)]
        mod = ast.Module(body, [])
        code = compile(mod, 'test', 'exec')
        ns = {}
        exec(code, ns)
        self.assertIn('sleep', ns)


kundi ASTValidatorTests(unittest.TestCase):

    eleza mod(self, mod, msg=Tupu, mode="exec", *, exc=ValueError):
        mod.lineno = mod.col_offset = 0
        ast.fix_missing_locations(mod)
        ikiwa msg ni Tupu:
            compile(mod, "<test>", mode)
        isipokua:
            ukijumuisha self.assertRaises(exc) kama cm:
                compile(mod, "<test>", mode)
            self.assertIn(msg, str(cm.exception))

    eleza expr(self, node, msg=Tupu, *, exc=ValueError):
        mod = ast.Module([ast.Expr(node)], [])
        self.mod(mod, msg, exc=exc)

    eleza stmt(self, stmt, msg=Tupu):
        mod = ast.Module([stmt], [])
        self.mod(mod, msg)

    eleza test_module(self):
        m = ast.Interactive([ast.Expr(ast.Name("x", ast.Store()))])
        self.mod(m, "must have Load context", "single")
        m = ast.Expression(ast.Name("x", ast.Store()))
        self.mod(m, "must have Load context", "eval")

    eleza _check_arguments(self, fac, check):
        eleza arguments(args=Tupu, posonlyargs=Tupu, vararg=Tupu,
                      kwonlyargs=Tupu, kwarg=Tupu,
                      defaults=Tupu, kw_defaults=Tupu):
            ikiwa args ni Tupu:
                args = []
            ikiwa posonlyargs ni Tupu:
                posonlyargs = []
            ikiwa kwonlyargs ni Tupu:
                kwonlyargs = []
            ikiwa defaults ni Tupu:
                defaults = []
            ikiwa kw_defaults ni Tupu:
                kw_defaults = []
            args = ast.arguments(args, posonlyargs, vararg, kwonlyargs,
                                 kw_defaults, kwarg, defaults)
            rudisha fac(args)
        args = [ast.arg("x", ast.Name("x", ast.Store()))]
        check(arguments(args=args), "must have Load context")
        check(arguments(posonlyargs=args), "must have Load context")
        check(arguments(kwonlyargs=args), "must have Load context")
        check(arguments(defaults=[ast.Num(3)]),
                       "more positional defaults than args")
        check(arguments(kw_defaults=[ast.Num(4)]),
                       "length of kwonlyargs ni sio the same kama kw_defaults")
        args = [ast.arg("x", ast.Name("x", ast.Load()))]
        check(arguments(args=args, defaults=[ast.Name("x", ast.Store())]),
                       "must have Load context")
        args = [ast.arg("a", ast.Name("x", ast.Load())),
                ast.arg("b", ast.Name("y", ast.Load()))]
        check(arguments(kwonlyargs=args,
                          kw_defaults=[Tupu, ast.Name("x", ast.Store())]),
                          "must have Load context")

    eleza test_funcdef(self):
        a = ast.arguments([], [], Tupu, [], [], Tupu, [])
        f = ast.FunctionDef("x", a, [], [], Tupu)
        self.stmt(f, "empty body on FunctionDef")
        f = ast.FunctionDef("x", a, [ast.Pass()], [ast.Name("x", ast.Store())],
                            Tupu)
        self.stmt(f, "must have Load context")
        f = ast.FunctionDef("x", a, [ast.Pass()], [],
                            ast.Name("x", ast.Store()))
        self.stmt(f, "must have Load context")
        eleza fac(args):
            rudisha ast.FunctionDef("x", args, [ast.Pass()], [], Tupu)
        self._check_arguments(fac, self.stmt)

    eleza test_classdef(self):
        eleza cls(bases=Tupu, keywords=Tupu, body=Tupu, decorator_list=Tupu):
            ikiwa bases ni Tupu:
                bases = []
            ikiwa keywords ni Tupu:
                keywords = []
            ikiwa body ni Tupu:
                body = [ast.Pass()]
            ikiwa decorator_list ni Tupu:
                decorator_list = []
            rudisha ast.ClassDef("myclass", bases, keywords,
                                body, decorator_list)
        self.stmt(cls(bases=[ast.Name("x", ast.Store())]),
                  "must have Load context")
        self.stmt(cls(keywords=[ast.keyword("x", ast.Name("x", ast.Store()))]),
                  "must have Load context")
        self.stmt(cls(body=[]), "empty body on ClassDef")
        self.stmt(cls(body=[Tupu]), "Tupu disallowed")
        self.stmt(cls(decorator_list=[ast.Name("x", ast.Store())]),
                  "must have Load context")

    eleza test_delete(self):
        self.stmt(ast.Delete([]), "empty targets on Delete")
        self.stmt(ast.Delete([Tupu]), "Tupu disallowed")
        self.stmt(ast.Delete([ast.Name("x", ast.Load())]),
                  "must have Del context")

    eleza test_assign(self):
        self.stmt(ast.Assign([], ast.Num(3)), "empty targets on Assign")
        self.stmt(ast.Assign([Tupu], ast.Num(3)), "Tupu disallowed")
        self.stmt(ast.Assign([ast.Name("x", ast.Load())], ast.Num(3)),
                  "must have Store context")
        self.stmt(ast.Assign([ast.Name("x", ast.Store())],
                                ast.Name("y", ast.Store())),
                  "must have Load context")

    eleza test_augassign(self):
        aug = ast.AugAssign(ast.Name("x", ast.Load()), ast.Add(),
                            ast.Name("y", ast.Load()))
        self.stmt(aug, "must have Store context")
        aug = ast.AugAssign(ast.Name("x", ast.Store()), ast.Add(),
                            ast.Name("y", ast.Store()))
        self.stmt(aug, "must have Load context")

    eleza test_for(self):
        x = ast.Name("x", ast.Store())
        y = ast.Name("y", ast.Load())
        p = ast.Pass()
        self.stmt(ast.For(x, y, [], []), "empty body on For")
        self.stmt(ast.For(ast.Name("x", ast.Load()), y, [p], []),
                  "must have Store context")
        self.stmt(ast.For(x, ast.Name("y", ast.Store()), [p], []),
                  "must have Load context")
        e = ast.Expr(ast.Name("x", ast.Store()))
        self.stmt(ast.For(x, y, [e], []), "must have Load context")
        self.stmt(ast.For(x, y, [p], [e]), "must have Load context")

    eleza test_while(self):
        self.stmt(ast.While(ast.Num(3), [], []), "empty body on While")
        self.stmt(ast.While(ast.Name("x", ast.Store()), [ast.Pass()], []),
                  "must have Load context")
        self.stmt(ast.While(ast.Num(3), [ast.Pass()],
                             [ast.Expr(ast.Name("x", ast.Store()))]),
                             "must have Load context")

    eleza test_if(self):
        self.stmt(ast.If(ast.Num(3), [], []), "empty body on If")
        i = ast.If(ast.Name("x", ast.Store()), [ast.Pass()], [])
        self.stmt(i, "must have Load context")
        i = ast.If(ast.Num(3), [ast.Expr(ast.Name("x", ast.Store()))], [])
        self.stmt(i, "must have Load context")
        i = ast.If(ast.Num(3), [ast.Pass()],
                   [ast.Expr(ast.Name("x", ast.Store()))])
        self.stmt(i, "must have Load context")

    eleza test_with(self):
        p = ast.Pass()
        self.stmt(ast.With([], [p]), "empty items on With")
        i = ast.withitem(ast.Num(3), Tupu)
        self.stmt(ast.With([i], []), "empty body on With")
        i = ast.withitem(ast.Name("x", ast.Store()), Tupu)
        self.stmt(ast.With([i], [p]), "must have Load context")
        i = ast.withitem(ast.Num(3), ast.Name("x", ast.Load()))
        self.stmt(ast.With([i], [p]), "must have Store context")

    eleza test_raise(self):
        r = ast.Raise(Tupu, ast.Num(3))
        self.stmt(r, "Raise ukijumuisha cause but no exception")
        r = ast.Raise(ast.Name("x", ast.Store()), Tupu)
        self.stmt(r, "must have Load context")
        r = ast.Raise(ast.Num(4), ast.Name("x", ast.Store()))
        self.stmt(r, "must have Load context")

    eleza test_try(self):
        p = ast.Pass()
        t = ast.Try([], [], [], [p])
        self.stmt(t, "empty body on Try")
        t = ast.Try([ast.Expr(ast.Name("x", ast.Store()))], [], [], [p])
        self.stmt(t, "must have Load context")
        t = ast.Try([p], [], [], [])
        self.stmt(t, "Try has neither tatizo handlers nor finalbody")
        t = ast.Try([p], [], [p], [p])
        self.stmt(t, "Try has orelse but no tatizo handlers")
        t = ast.Try([p], [ast.ExceptHandler(Tupu, "x", [])], [], [])
        self.stmt(t, "empty body on ExceptHandler")
        e = [ast.ExceptHandler(ast.Name("x", ast.Store()), "y", [p])]
        self.stmt(ast.Try([p], e, [], []), "must have Load context")
        e = [ast.ExceptHandler(Tupu, "x", [p])]
        t = ast.Try([p], e, [ast.Expr(ast.Name("x", ast.Store()))], [p])
        self.stmt(t, "must have Load context")
        t = ast.Try([p], e, [p], [ast.Expr(ast.Name("x", ast.Store()))])
        self.stmt(t, "must have Load context")

    eleza test_assert(self):
        self.stmt(ast.Assert(ast.Name("x", ast.Store()), Tupu),
                  "must have Load context")
        assrt = ast.Assert(ast.Name("x", ast.Load()),
                           ast.Name("y", ast.Store()))
        self.stmt(assrt, "must have Load context")

    eleza test_import(self):
        self.stmt(ast.Import([]), "empty names on Import")

    eleza test_importfrom(self):
        imp = ast.ImportFrom(Tupu, [ast.alias("x", Tupu)], -42)
        self.stmt(imp, "Negative ImportFrom level")
        self.stmt(ast.ImportFrom(Tupu, [], 0), "empty names on ImportFrom")

    eleza test_global(self):
        self.stmt(ast.Global([]), "empty names on Global")

    eleza test_nonlocal(self):
        self.stmt(ast.Nonlocal([]), "empty names on Nonlocal")

    eleza test_expr(self):
        e = ast.Expr(ast.Name("x", ast.Store()))
        self.stmt(e, "must have Load context")

    eleza test_boolop(self):
        b = ast.BoolOp(ast.And(), [])
        self.expr(b, "less than 2 values")
        b = ast.BoolOp(ast.And(), [ast.Num(3)])
        self.expr(b, "less than 2 values")
        b = ast.BoolOp(ast.And(), [ast.Num(4), Tupu])
        self.expr(b, "Tupu disallowed")
        b = ast.BoolOp(ast.And(), [ast.Num(4), ast.Name("x", ast.Store())])
        self.expr(b, "must have Load context")

    eleza test_unaryop(self):
        u = ast.UnaryOp(ast.Not(), ast.Name("x", ast.Store()))
        self.expr(u, "must have Load context")

    eleza test_lambda(self):
        a = ast.arguments([], [], Tupu, [], [], Tupu, [])
        self.expr(ast.Lambda(a, ast.Name("x", ast.Store())),
                  "must have Load context")
        eleza fac(args):
            rudisha ast.Lambda(args, ast.Name("x", ast.Load()))
        self._check_arguments(fac, self.expr)

    eleza test_ifexp(self):
        l = ast.Name("x", ast.Load())
        s = ast.Name("y", ast.Store())
        kila args kwenye (s, l, l), (l, s, l), (l, l, s):
            self.expr(ast.IfExp(*args), "must have Load context")

    eleza test_dict(self):
        d = ast.Dict([], [ast.Name("x", ast.Load())])
        self.expr(d, "same number of keys kama values")
        d = ast.Dict([ast.Name("x", ast.Load())], [Tupu])
        self.expr(d, "Tupu disallowed")

    eleza test_set(self):
        self.expr(ast.Set([Tupu]), "Tupu disallowed")
        s = ast.Set([ast.Name("x", ast.Store())])
        self.expr(s, "must have Load context")

    eleza _check_comprehension(self, fac):
        self.expr(fac([]), "comprehension ukijumuisha no generators")
        g = ast.comprehension(ast.Name("x", ast.Load()),
                              ast.Name("x", ast.Load()), [], 0)
        self.expr(fac([g]), "must have Store context")
        g = ast.comprehension(ast.Name("x", ast.Store()),
                              ast.Name("x", ast.Store()), [], 0)
        self.expr(fac([g]), "must have Load context")
        x = ast.Name("x", ast.Store())
        y = ast.Name("y", ast.Load())
        g = ast.comprehension(x, y, [Tupu], 0)
        self.expr(fac([g]), "Tupu disallowed")
        g = ast.comprehension(x, y, [ast.Name("x", ast.Store())], 0)
        self.expr(fac([g]), "must have Load context")

    eleza _simple_comp(self, fac):
        g = ast.comprehension(ast.Name("x", ast.Store()),
                              ast.Name("x", ast.Load()), [], 0)
        self.expr(fac(ast.Name("x", ast.Store()), [g]),
                  "must have Load context")
        eleza wrap(gens):
            rudisha fac(ast.Name("x", ast.Store()), gens)
        self._check_comprehension(wrap)

    eleza test_listcomp(self):
        self._simple_comp(ast.ListComp)

    eleza test_setcomp(self):
        self._simple_comp(ast.SetComp)

    eleza test_generatorexp(self):
        self._simple_comp(ast.GeneratorExp)

    eleza test_dictcomp(self):
        g = ast.comprehension(ast.Name("y", ast.Store()),
                              ast.Name("p", ast.Load()), [], 0)
        c = ast.DictComp(ast.Name("x", ast.Store()),
                         ast.Name("y", ast.Load()), [g])
        self.expr(c, "must have Load context")
        c = ast.DictComp(ast.Name("x", ast.Load()),
                         ast.Name("y", ast.Store()), [g])
        self.expr(c, "must have Load context")
        eleza factory(comps):
            k = ast.Name("x", ast.Load())
            v = ast.Name("y", ast.Load())
            rudisha ast.DictComp(k, v, comps)
        self._check_comprehension(factory)

    eleza test_tuma(self):
        self.expr(ast.Yield(ast.Name("x", ast.Store())), "must have Load")
        self.expr(ast.YieldFrom(ast.Name("x", ast.Store())), "must have Load")

    eleza test_compare(self):
        left = ast.Name("x", ast.Load())
        comp = ast.Compare(left, [ast.In()], [])
        self.expr(comp, "no comparators")
        comp = ast.Compare(left, [ast.In()], [ast.Num(4), ast.Num(5)])
        self.expr(comp, "different number of comparators na operands")
        comp = ast.Compare(ast.Num("blah"), [ast.In()], [left])
        self.expr(comp)
        comp = ast.Compare(left, [ast.In()], [ast.Num("blah")])
        self.expr(comp)

    eleza test_call(self):
        func = ast.Name("x", ast.Load())
        args = [ast.Name("y", ast.Load())]
        keywords = [ast.keyword("w", ast.Name("z", ast.Load()))]
        call = ast.Call(ast.Name("x", ast.Store()), args, keywords)
        self.expr(call, "must have Load context")
        call = ast.Call(func, [Tupu], keywords)
        self.expr(call, "Tupu disallowed")
        bad_keywords = [ast.keyword("w", ast.Name("z", ast.Store()))]
        call = ast.Call(func, args, bad_keywords)
        self.expr(call, "must have Load context")

    eleza test_num(self):
        kundi subint(int):
            pita
        kundi subfloat(float):
            pita
        kundi subcomplex(complex):
            pita
        kila obj kwenye "0", "hello":
            self.expr(ast.Num(obj))
        kila obj kwenye subint(), subfloat(), subcomplex():
            self.expr(ast.Num(obj), "invalid type", exc=TypeError)

    eleza test_attribute(self):
        attr = ast.Attribute(ast.Name("x", ast.Store()), "y", ast.Load())
        self.expr(attr, "must have Load context")

    eleza test_subscript(self):
        sub = ast.Subscript(ast.Name("x", ast.Store()), ast.Index(ast.Num(3)),
                            ast.Load())
        self.expr(sub, "must have Load context")
        x = ast.Name("x", ast.Load())
        sub = ast.Subscript(x, ast.Index(ast.Name("y", ast.Store())),
                            ast.Load())
        self.expr(sub, "must have Load context")
        s = ast.Name("x", ast.Store())
        kila args kwenye (s, Tupu, Tupu), (Tupu, s, Tupu), (Tupu, Tupu, s):
            sl = ast.Slice(*args)
            self.expr(ast.Subscript(x, sl, ast.Load()),
                      "must have Load context")
        sl = ast.ExtSlice([])
        self.expr(ast.Subscript(x, sl, ast.Load()), "empty dims on ExtSlice")
        sl = ast.ExtSlice([ast.Index(s)])
        self.expr(ast.Subscript(x, sl, ast.Load()), "must have Load context")

    eleza test_starred(self):
        left = ast.List([ast.Starred(ast.Name("x", ast.Load()), ast.Store())],
                        ast.Store())
        assign = ast.Assign([left], ast.Num(4))
        self.stmt(assign, "must have Store context")

    eleza _sequence(self, fac):
        self.expr(fac([Tupu], ast.Load()), "Tupu disallowed")
        self.expr(fac([ast.Name("x", ast.Store())], ast.Load()),
                  "must have Load context")

    eleza test_list(self):
        self._sequence(ast.List)

    eleza test_tuple(self):
        self._sequence(ast.Tuple)

    eleza test_nameconstant(self):
        self.expr(ast.NameConstant(4))

    eleza test_stdlib_validates(self):
        stdlib = os.path.dirname(ast.__file__)
        tests = [fn kila fn kwenye os.listdir(stdlib) ikiwa fn.endswith(".py")]
        tests.extend(["test/test_grammar.py", "test/test_unpack_ex.py"])
        kila module kwenye tests:
            ukijumuisha self.subTest(module):
                fn = os.path.join(stdlib, module)
                ukijumuisha open(fn, "r", encoding="utf-8") kama fp:
                    source = fp.read()
                mod = ast.parse(source, fn)
                compile(mod, fn, "exec")


kundi ConstantTests(unittest.TestCase):
    """Tests on the ast.Constant node type."""

    eleza compile_constant(self, value):
        tree = ast.parse("x = 123")

        node = tree.body[0].value
        new_node = ast.Constant(value=value)
        ast.copy_location(new_node, node)
        tree.body[0].value = new_node

        code = compile(tree, "<string>", "exec")

        ns = {}
        exec(code, ns)
        rudisha ns['x']

    eleza test_validation(self):
        ukijumuisha self.assertRaises(TypeError) kama cm:
            self.compile_constant([1, 2, 3])
        self.assertEqual(str(cm.exception),
                         "got an invalid type kwenye Constant: list")

    eleza test_singletons(self):
        kila const kwenye (Tupu, Uongo, Kweli, Ellipsis, b'', frozenset()):
            ukijumuisha self.subTest(const=const):
                value = self.compile_constant(const)
                self.assertIs(value, const)

    eleza test_values(self):
        nested_tuple = (1,)
        nested_frozenset = frozenset({1})
        kila level kwenye range(3):
            nested_tuple = (nested_tuple, 2)
            nested_frozenset = frozenset({nested_frozenset, 2})
        values = (123, 123.0, 123j,
                  "unicode", b'bytes',
                  tuple("tuple"), frozenset("frozenset"),
                  nested_tuple, nested_frozenset)
        kila value kwenye values:
            ukijumuisha self.subTest(value=value):
                result = self.compile_constant(value)
                self.assertEqual(result, value)

    eleza test_assign_to_constant(self):
        tree = ast.parse("x = 1")

        target = tree.body[0].targets[0]
        new_target = ast.Constant(value=1)
        ast.copy_location(new_target, target)
        tree.body[0].targets[0] = new_target

        ukijumuisha self.assertRaises(ValueError) kama cm:
            compile(tree, "string", "exec")
        self.assertEqual(str(cm.exception),
                         "expression which can't be assigned "
                         "to kwenye Store context")

    eleza test_get_docstring(self):
        tree = ast.parse("'docstring'\nx = 1")
        self.assertEqual(ast.get_docstring(tree), 'docstring')

    eleza get_load_const(self, tree):
        # Compile to bytecode, disassemble na get parameter of LOAD_CONST
        # instructions
        co = compile(tree, '<string>', 'exec')
        consts = []
        kila instr kwenye dis.get_instructions(co):
            ikiwa instr.opname == 'LOAD_CONST':
                consts.append(instr.argval)
        rudisha consts

    @support.cpython_only
    eleza test_load_const(self):
        consts = [Tupu,
                  Kweli, Uongo,
                  124,
                  2.0,
                  3j,
                  "unicode",
                  b'bytes',
                  (1, 2, 3)]

        code = '\n'.join(['x={!r}'.format(const) kila const kwenye consts])
        code += '\nx = ...'
        consts.extend((Ellipsis, Tupu))

        tree = ast.parse(code)
        self.assertEqual(self.get_load_const(tree),
                         consts)

        # Replace expression nodes ukijumuisha constants
        kila assign, const kwenye zip(tree.body, consts):
            assert isinstance(assign, ast.Assign), ast.dump(assign)
            new_node = ast.Constant(value=const)
            ast.copy_location(new_node, assign.value)
            assign.value = new_node

        self.assertEqual(self.get_load_const(tree),
                         consts)

    eleza test_literal_eval(self):
        tree = ast.parse("1 + 2")
        binop = tree.body[0].value

        new_left = ast.Constant(value=10)
        ast.copy_location(new_left, binop.left)
        binop.left = new_left

        new_right = ast.Constant(value=20j)
        ast.copy_location(new_right, binop.right)
        binop.right = new_right

        self.assertEqual(ast.literal_eval(binop), 10+20j)

    eleza test_string_kind(self):
        c = ast.parse('"x"', mode='eval').body
        self.assertEqual(c.value, "x")
        self.assertEqual(c.kind, Tupu)

        c = ast.parse('u"x"', mode='eval').body
        self.assertEqual(c.value, "x")
        self.assertEqual(c.kind, "u")

        c = ast.parse('r"x"', mode='eval').body
        self.assertEqual(c.value, "x")
        self.assertEqual(c.kind, Tupu)

        c = ast.parse('b"x"', mode='eval').body
        self.assertEqual(c.value, b"x")
        self.assertEqual(c.kind, Tupu)


kundi EndPositionTests(unittest.TestCase):
    """Tests kila end position of AST nodes.

    Testing end positions of nodes requires a bit of extra care
    because of how LL parsers work.
    """
    eleza _check_end_pos(self, ast_node, end_lineno, end_col_offset):
        self.assertEqual(ast_node.end_lineno, end_lineno)
        self.assertEqual(ast_node.end_col_offset, end_col_offset)

    eleza _check_content(self, source, ast_node, content):
        self.assertEqual(ast.get_source_segment(source, ast_node), content)

    eleza _parse_value(self, s):
        # Use duck-typing to support both single expression
        # na a right hand side of an assignment statement.
        rudisha ast.parse(s).body[0].value

    eleza test_lambda(self):
        s = 'lambda x, *y: Tupu'
        lam = self._parse_value(s)
        self._check_content(s, lam.body, 'Tupu')
        self._check_content(s, lam.args.args[0], 'x')
        self._check_content(s, lam.args.vararg, 'y')

    eleza test_func_def(self):
        s = dedent('''
            eleza func(x: int,
                     *args: str,
                     z: float = 0,
                     **kwargs: Any) -> bool:
                rudisha Kweli
            ''').strip()
        feleza = ast.parse(s).body[0]
        self._check_end_pos(fdef, 5, 15)
        self._check_content(s, fdef.body[0], 'rudisha Kweli')
        self._check_content(s, fdef.args.args[0], 'x: int')
        self._check_content(s, fdef.args.args[0].annotation, 'int')
        self._check_content(s, fdef.args.kwarg, 'kwargs: Any')
        self._check_content(s, fdef.args.kwarg.annotation, 'Any')

    eleza test_call(self):
        s = 'func(x, y=2, **kw)'
        call = self._parse_value(s)
        self._check_content(s, call.func, 'func')
        self._check_content(s, call.keywords[0].value, '2')
        self._check_content(s, call.keywords[1].value, 'kw')

    eleza test_call_noargs(self):
        s = 'x[0]()'
        call = self._parse_value(s)
        self._check_content(s, call.func, 'x[0]')
        self._check_end_pos(call, 1, 6)

    eleza test_class_def(self):
        s = dedent('''
            kundi C(A, B):
                x: int = 0
        ''').strip()
        celeza = ast.parse(s).body[0]
        self._check_end_pos(cdef, 2, 14)
        self._check_content(s, cdef.bases[1], 'B')
        self._check_content(s, cdef.body[0], 'x: int = 0')

    eleza test_class_kw(self):
        s = 'kundi S(metaclass=abc.ABCMeta): pita'
        celeza = ast.parse(s).body[0]
        self._check_content(s, cdef.keywords[0].value, 'abc.ABCMeta')

    eleza test_multi_line_str(self):
        s = dedent('''
            x = """Some multi-line text.

            It goes on starting kutoka same indent."""
        ''').strip()
        assign = ast.parse(s).body[0]
        self._check_end_pos(assign, 3, 40)
        self._check_end_pos(assign.value, 3, 40)

    eleza test_endelead_str(self):
        s = dedent('''
            x = "first part" \\
            "second part"
        ''').strip()
        assign = ast.parse(s).body[0]
        self._check_end_pos(assign, 2, 13)
        self._check_end_pos(assign.value, 2, 13)

    eleza test_suites(self):
        # We intentionally put these into the same string to check
        # that empty lines are sio part of the suite.
        s = dedent('''
            wakati Kweli:
                pita

            ikiwa one():
                x = Tupu
            lasivyo other():
                y = Tupu
            isipokua:
                z = Tupu

            kila x, y kwenye stuff:
                assert Kweli

            jaribu:
                ashiria RuntimeError
            tatizo TypeError kama e:
                pita

            pita
        ''').strip()
        mod = ast.parse(s)
        while_loop = mod.body[0]
        if_stmt = mod.body[1]
        for_loop = mod.body[2]
        try_stmt = mod.body[3]
        pita_stmt = mod.body[4]

        self._check_end_pos(while_loop, 2, 8)
        self._check_end_pos(if_stmt, 9, 12)
        self._check_end_pos(for_loop, 12, 15)
        self._check_end_pos(try_stmt, 17, 8)
        self._check_end_pos(pita_stmt, 19, 4)

        self._check_content(s, while_loop.test, 'Kweli')
        self._check_content(s, if_stmt.body[0], 'x = Tupu')
        self._check_content(s, if_stmt.orelse[0].test, 'other()')
        self._check_content(s, for_loop.target, 'x, y')
        self._check_content(s, try_stmt.body[0], 'ashiria RuntimeError')
        self._check_content(s, try_stmt.handlers[0].type, 'TypeError')

    eleza test_fstring(self):
        s = 'x = f"abc {x + y} abc"'
        fstr = self._parse_value(s)
        binop = fstr.values[1].value
        self._check_content(s, binop, 'x + y')

    eleza test_fstring_multi_line(self):
        s = dedent('''
            f"""Some multi-line text.
            {
            arg_one
            +
            arg_two
            }
            It goes on..."""
        ''').strip()
        fstr = self._parse_value(s)
        binop = fstr.values[1].value
        self._check_end_pos(binop, 5, 7)
        self._check_content(s, binop.left, 'arg_one')
        self._check_content(s, binop.right, 'arg_two')

    eleza test_import_from_multi_line(self):
        s = dedent('''
            kutoka x.y.z agiza (
                a, b, c kama c
            )
        ''').strip()
        imp = ast.parse(s).body[0]
        self._check_end_pos(imp, 3, 1)

    eleza test_slices(self):
        s1 = 'f()[1, 2] [0]'
        s2 = 'x[ a.b: c.d]'
        sm = dedent('''
            x[ a.b: f () ,
               g () : c.d
              ]
        ''').strip()
        i1, i2, im = map(self._parse_value, (s1, s2, sm))
        self._check_content(s1, i1.value, 'f()[1, 2]')
        self._check_content(s1, i1.value.slice.value, '1, 2')
        self._check_content(s2, i2.slice.lower, 'a.b')
        self._check_content(s2, i2.slice.upper, 'c.d')
        self._check_content(sm, im.slice.dims[0].upper, 'f ()')
        self._check_content(sm, im.slice.dims[1].lower, 'g ()')
        self._check_end_pos(im, 3, 3)

    eleza test_binop(self):
        s = dedent('''
            (1 * 2 + (3 ) +
                 4
            )
        ''').strip()
        binop = self._parse_value(s)
        self._check_end_pos(binop, 2, 6)
        self._check_content(s, binop.right, '4')
        self._check_content(s, binop.left, '1 * 2 + (3 )')
        self._check_content(s, binop.left.right, '3')

    eleza test_boolop(self):
        s = dedent('''
            ikiwa (one_condition na
                    (other_condition ama yet_another_one)):
                pita
        ''').strip()
        bop = ast.parse(s).body[0].test
        self._check_end_pos(bop, 2, 44)
        self._check_content(s, bop.values[1],
                            'other_condition ama yet_another_one')

    eleza test_tuples(self):
        s1 = 'x = () ;'
        s2 = 'x = 1 , ;'
        s3 = 'x = (1 , 2 ) ;'
        sm = dedent('''
            x = (
                a, b,
            )
        ''').strip()
        t1, t2, t3, tm = map(self._parse_value, (s1, s2, s3, sm))
        self._check_content(s1, t1, '()')
        self._check_content(s2, t2, '1 ,')
        self._check_content(s3, t3, '(1 , 2 )')
        self._check_end_pos(tm, 3, 1)

    eleza test_attribute_spaces(self):
        s = 'func(x. y .z)'
        call = self._parse_value(s)
        self._check_content(s, call, s)
        self._check_content(s, call.args[0], 'x. y .z')

    eleza test_displays(self):
        s1 = '[{}, {1, }, {1, 2,} ]'
        s2 = '{a: b, f (): g () ,}'
        c1 = self._parse_value(s1)
        c2 = self._parse_value(s2)
        self._check_content(s1, c1.elts[0], '{}')
        self._check_content(s1, c1.elts[1], '{1, }')
        self._check_content(s1, c1.elts[2], '{1, 2,}')
        self._check_content(s2, c2.keys[1], 'f ()')
        self._check_content(s2, c2.values[1], 'g ()')

    eleza test_comprehensions(self):
        s = dedent('''
            x = [{x kila x, y kwenye stuff
                  ikiwa cond.x} kila stuff kwenye things]
        ''').strip()
        cmp = self._parse_value(s)
        self._check_end_pos(cmp, 2, 37)
        self._check_content(s, cmp.generators[0].iter, 'things')
        self._check_content(s, cmp.elt.generators[0].iter, 'stuff')
        self._check_content(s, cmp.elt.generators[0].ifs[0], 'cond.x')
        self._check_content(s, cmp.elt.generators[0].target, 'x, y')

    eleza test_tuma_await(self):
        s = dedent('''
            async eleza f():
                tuma x
                await y
        ''').strip()
        feleza = ast.parse(s).body[0]
        self._check_content(s, fdef.body[0].value, 'tuma x')
        self._check_content(s, fdef.body[1].value, 'await y')

    eleza test_source_segment_multi(self):
        s_orig = dedent('''
            x = (
                a, b,
            ) + ()
        ''').strip()
        s_tuple = dedent('''
            (
                a, b,
            )
        ''').strip()
        binop = self._parse_value(s_orig)
        self.assertEqual(ast.get_source_segment(s_orig, binop.left), s_tuple)

    eleza test_source_segment_padded(self):
        s_orig = dedent('''
            kundi C:
                eleza fun(self) -> Tupu:
                    "ЖЖЖЖЖ"
        ''').strip()
        s_method = '    eleza fun(self) -> Tupu:\n' \
                   '        "ЖЖЖЖЖ"'
        celeza = ast.parse(s_orig).body[0]
        self.assertEqual(ast.get_source_segment(s_orig, cdef.body[0], padded=Kweli),
                         s_method)

    eleza test_source_segment_endings(self):
        s = 'v = 1\r\nw = 1\nx = 1\n\ry = 1\rz = 1\r\n'
        v, w, x, y, z = ast.parse(s).body
        self._check_content(s, v, 'v = 1')
        self._check_content(s, w, 'w = 1')
        self._check_content(s, x, 'x = 1')
        self._check_content(s, y, 'y = 1')
        self._check_content(s, z, 'z = 1')

    eleza test_source_segment_tabs(self):
        s = dedent('''
            kundi C:
              \t\f  eleza fun(self) -> Tupu:
              \t\f      pita
        ''').strip()
        s_method = '  \t\f  eleza fun(self) -> Tupu:\n' \
                   '  \t\f      pita'

        celeza = ast.parse(s).body[0]
        self.assertEqual(ast.get_source_segment(s, cdef.body[0], padded=Kweli), s_method)


kundi NodeVisitorTests(unittest.TestCase):
    eleza test_old_constant_nodes(self):
        kundi Visitor(ast.NodeVisitor):
            eleza visit_Num(self, node):
                log.append((node.lineno, 'Num', node.n))
            eleza visit_Str(self, node):
                log.append((node.lineno, 'Str', node.s))
            eleza visit_Bytes(self, node):
                log.append((node.lineno, 'Bytes', node.s))
            eleza visit_NameConstant(self, node):
                log.append((node.lineno, 'NameConstant', node.value))
            eleza visit_Ellipsis(self, node):
                log.append((node.lineno, 'Ellipsis', ...))
        mod = ast.parse(dedent('''\
            i = 42
            f = 4.25
            c = 4.25j
            s = 'string'
            b = b'bytes'
            t = Kweli
            n = Tupu
            e = ...
            '''))
        visitor = Visitor()
        log = []
        ukijumuisha warnings.catch_warnings(record=Kweli) kama wlog:
            warnings.filterwarnings('always', '', PendingDeprecationWarning)
            visitor.visit(mod)
        self.assertEqual(log, [
            (1, 'Num', 42),
            (2, 'Num', 4.25),
            (3, 'Num', 4.25j),
            (4, 'Str', 'string'),
            (5, 'Bytes', b'bytes'),
            (6, 'NameConstant', Kweli),
            (7, 'NameConstant', Tupu),
            (8, 'Ellipsis', ...),
        ])
        self.assertEqual([str(w.message) kila w kwenye wlog], [
            'visit_Num ni deprecated; add visit_Constant',
            'visit_Num ni deprecated; add visit_Constant',
            'visit_Num ni deprecated; add visit_Constant',
            'visit_Str ni deprecated; add visit_Constant',
            'visit_Bytes ni deprecated; add visit_Constant',
            'visit_NameConstant ni deprecated; add visit_Constant',
            'visit_NameConstant ni deprecated; add visit_Constant',
            'visit_Ellipsis ni deprecated; add visit_Constant',
        ])


eleza main():
    ikiwa __name__ != '__main__':
        return
    ikiwa sys.argv[1:] == ['-g']:
        kila statements, kind kwenye ((exec_tests, "exec"), (single_tests, "single"),
                                 (eval_tests, "eval")):
            andika(kind+"_results = [")
            kila statement kwenye statements:
                tree = ast.parse(statement, "?", kind)
                andika("%r," % (to_tuple(tree),))
            andika("]")
        andika("main()")
        ashiria SystemExit
    unittest.main()

#### EVERYTHING BELOW IS GENERATED BY python Lib/test/test_ast.py -g  #####
exec_results = [
('Module', [('Expr', (1, 0), ('Constant', (1, 0), Tupu, Tupu))], []),
('Module', [('Expr', (1, 0), ('Constant', (1, 0), 'module docstring', Tupu))], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('Pass', (1, 9))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('Expr', (1, 9), ('Constant', (1, 9), 'function docstring', Tupu))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], [('arg', (1, 6), 'a', Tupu, Tupu)], Tupu, [], [], Tupu, []), [('Pass', (1, 10))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], [('arg', (1, 6), 'a', Tupu, Tupu)], Tupu, [], [], Tupu, [('Constant', (1, 8), 0, Tupu)]), [('Pass', (1, 12))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], [], ('arg', (1, 7), 'args', Tupu, Tupu), [], [], Tupu, []), [('Pass', (1, 14))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], [], Tupu, [], [], ('arg', (1, 8), 'kwargs', Tupu, Tupu), []), [('Pass', (1, 17))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], [('arg', (1, 6), 'a', Tupu, Tupu), ('arg', (1, 9), 'b', Tupu, Tupu), ('arg', (1, 14), 'c', Tupu, Tupu), ('arg', (1, 22), 'd', Tupu, Tupu), ('arg', (1, 28), 'e', Tupu, Tupu)], ('arg', (1, 35), 'args', Tupu, Tupu), [('arg', (1, 41), 'f', Tupu, Tupu)], [('Constant', (1, 43), 42, Tupu)], ('arg', (1, 49), 'kwargs', Tupu, Tupu), [('Constant', (1, 11), 1, Tupu), ('Constant', (1, 16), Tupu, Tupu), ('List', (1, 24), [], ('Load',)), ('Dict', (1, 30), [], [])]), [('Expr', (1, 58), ('Constant', (1, 58), 'doc kila f()', Tupu))], [], Tupu, Tupu)], []),
('Module', [('ClassDef', (1, 0), 'C', [], [], [('Pass', (1, 8))], [])], []),
('Module', [('ClassDef', (1, 0), 'C', [], [], [('Expr', (1, 9), ('Constant', (1, 9), 'docstring kila kundi C', Tupu))], [])], []),
('Module', [('ClassDef', (1, 0), 'C', [('Name', (1, 8), 'object', ('Load',))], [], [('Pass', (1, 17))], [])], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('Return', (1, 8), ('Constant', (1, 15), 1, Tupu))], [], Tupu, Tupu)], []),
('Module', [('Delete', (1, 0), [('Name', (1, 4), 'v', ('Del',))])], []),
('Module', [('Assign', (1, 0), [('Name', (1, 0), 'v', ('Store',))], ('Constant', (1, 4), 1, Tupu), Tupu)], []),
('Module', [('Assign', (1, 0), [('Tuple', (1, 0), [('Name', (1, 0), 'a', ('Store',)), ('Name', (1, 2), 'b', ('Store',))], ('Store',))], ('Name', (1, 6), 'c', ('Load',)), Tupu)], []),
('Module', [('Assign', (1, 0), [('Tuple', (1, 0), [('Name', (1, 1), 'a', ('Store',)), ('Name', (1, 3), 'b', ('Store',))], ('Store',))], ('Name', (1, 8), 'c', ('Load',)), Tupu)], []),
('Module', [('Assign', (1, 0), [('List', (1, 0), [('Name', (1, 1), 'a', ('Store',)), ('Name', (1, 3), 'b', ('Store',))], ('Store',))], ('Name', (1, 8), 'c', ('Load',)), Tupu)], []),
('Module', [('AugAssign', (1, 0), ('Name', (1, 0), 'v', ('Store',)), ('Add',), ('Constant', (1, 5), 1, Tupu))], []),
('Module', [('For', (1, 0), ('Name', (1, 4), 'v', ('Store',)), ('Name', (1, 9), 'v', ('Load',)), [('Pass', (1, 11))], [], Tupu)], []),
('Module', [('While', (1, 0), ('Name', (1, 6), 'v', ('Load',)), [('Pass', (1, 8))], [])], []),
('Module', [('If', (1, 0), ('Name', (1, 3), 'v', ('Load',)), [('Pass', (1, 5))], [])], []),
('Module', [('With', (1, 0), [('withitem', ('Name', (1, 5), 'x', ('Load',)), ('Name', (1, 10), 'y', ('Store',)))], [('Pass', (1, 13))], Tupu)], []),
('Module', [('With', (1, 0), [('withitem', ('Name', (1, 5), 'x', ('Load',)), ('Name', (1, 10), 'y', ('Store',))), ('withitem', ('Name', (1, 13), 'z', ('Load',)), ('Name', (1, 18), 'q', ('Store',)))], [('Pass', (1, 21))], Tupu)], []),
('Module', [('Raise', (1, 0), ('Call', (1, 6), ('Name', (1, 6), 'Exception', ('Load',)), [('Constant', (1, 16), 'string', Tupu)], []), Tupu)], []),
('Module', [('Try', (1, 0), [('Pass', (2, 2))], [('ExceptHandler', (3, 0), ('Name', (3, 7), 'Exception', ('Load',)), Tupu, [('Pass', (4, 2))])], [], [])], []),
('Module', [('Try', (1, 0), [('Pass', (2, 2))], [], [], [('Pass', (4, 2))])], []),
('Module', [('Assert', (1, 0), ('Name', (1, 7), 'v', ('Load',)), Tupu)], []),
('Module', [('Import', (1, 0), [('alias', 'sys', Tupu)])], []),
('Module', [('ImportFrom', (1, 0), 'sys', [('alias', 'v', Tupu)], 0)], []),
('Module', [('Global', (1, 0), ['v'])], []),
('Module', [('Expr', (1, 0), ('Constant', (1, 0), 1, Tupu))], []),
('Module', [('Pass', (1, 0))], []),
('Module', [('For', (1, 0), ('Name', (1, 4), 'v', ('Store',)), ('Name', (1, 9), 'v', ('Load',)), [('Break', (1, 11))], [], Tupu)], []),
('Module', [('For', (1, 0), ('Name', (1, 4), 'v', ('Store',)), ('Name', (1, 9), 'v', ('Load',)), [('Continue', (1, 11))], [], Tupu)], []),
('Module', [('For', (1, 0), ('Tuple', (1, 4), [('Name', (1, 4), 'a', ('Store',)), ('Name', (1, 6), 'b', ('Store',))], ('Store',)), ('Name', (1, 11), 'c', ('Load',)), [('Pass', (1, 14))], [], Tupu)], []),
('Module', [('For', (1, 0), ('Tuple', (1, 4), [('Name', (1, 5), 'a', ('Store',)), ('Name', (1, 7), 'b', ('Store',))], ('Store',)), ('Name', (1, 13), 'c', ('Load',)), [('Pass', (1, 16))], [], Tupu)], []),
('Module', [('For', (1, 0), ('List', (1, 4), [('Name', (1, 5), 'a', ('Store',)), ('Name', (1, 7), 'b', ('Store',))], ('Store',)), ('Name', (1, 13), 'c', ('Load',)), [('Pass', (1, 16))], [], Tupu)], []),
('Module', [('Expr', (1, 0), ('GeneratorExp', (1, 0), ('Tuple', (2, 4), [('Name', (3, 4), 'Aa', ('Load',)), ('Name', (5, 7), 'Bb', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (8, 4), [('Name', (8, 4), 'Aa', ('Store',)), ('Name', (10, 4), 'Bb', ('Store',))], ('Store',)), ('Name', (10, 10), 'Cc', ('Load',)), [], 0)]))], []),
('Module', [('Expr', (1, 0), ('DictComp', (1, 0), ('Name', (1, 1), 'a', ('Load',)), ('Name', (1, 5), 'b', ('Load',)), [('comprehension', ('Name', (1, 11), 'w', ('Store',)), ('Name', (1, 16), 'x', ('Load',)), [], 0), ('comprehension', ('Name', (1, 22), 'm', ('Store',)), ('Name', (1, 27), 'p', ('Load',)), [('Name', (1, 32), 'g', ('Load',))], 0)]))], []),
('Module', [('Expr', (1, 0), ('DictComp', (1, 0), ('Name', (1, 1), 'a', ('Load',)), ('Name', (1, 5), 'b', ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 11), 'v', ('Store',)), ('Name', (1, 13), 'w', ('Store',))], ('Store',)), ('Name', (1, 18), 'x', ('Load',)), [], 0)]))], []),
('Module', [('Expr', (1, 0), ('SetComp', (1, 0), ('Name', (1, 1), 'r', ('Load',)), [('comprehension', ('Name', (1, 7), 'l', ('Store',)), ('Name', (1, 12), 'x', ('Load',)), [('Name', (1, 17), 'g', ('Load',))], 0)]))], []),
('Module', [('Expr', (1, 0), ('SetComp', (1, 0), ('Name', (1, 1), 'r', ('Load',)), [('comprehension', ('Tuple', (1, 7), [('Name', (1, 7), 'l', ('Store',)), ('Name', (1, 9), 'm', ('Store',))], ('Store',)), ('Name', (1, 14), 'x', ('Load',)), [], 0)]))], []),
('Module', [('AsyncFunctionDef', (1, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('Expr', (2, 1), ('Constant', (2, 1), 'async function', Tupu)), ('Expr', (3, 1), ('Await', (3, 1), ('Call', (3, 7), ('Name', (3, 7), 'something', ('Load',)), [], [])))], [], Tupu, Tupu)], []),
('Module', [('AsyncFunctionDef', (1, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('AsyncFor', (2, 1), ('Name', (2, 11), 'e', ('Store',)), ('Name', (2, 16), 'i', ('Load',)), [('Expr', (2, 19), ('Constant', (2, 19), 1, Tupu))], [('Expr', (3, 7), ('Constant', (3, 7), 2, Tupu))], Tupu)], [], Tupu, Tupu)], []),
('Module', [('AsyncFunctionDef', (1, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('AsyncWith', (2, 1), [('withitem', ('Name', (2, 12), 'a', ('Load',)), ('Name', (2, 17), 'b', ('Store',)))], [('Expr', (2, 20), ('Constant', (2, 20), 1, Tupu))], Tupu)], [], Tupu, Tupu)], []),
('Module', [('Expr', (1, 0), ('Dict', (1, 0), [Tupu, ('Constant', (1, 10), 2, Tupu)], [('Dict', (1, 3), [('Constant', (1, 4), 1, Tupu)], [('Constant', (1, 6), 2, Tupu)]), ('Constant', (1, 12), 3, Tupu)]))], []),
('Module', [('Expr', (1, 0), ('Set', (1, 0), [('Starred', (1, 1), ('Set', (1, 2), [('Constant', (1, 3), 1, Tupu), ('Constant', (1, 6), 2, Tupu)]), ('Load',)), ('Constant', (1, 10), 3, Tupu)]))], []),
('Module', [('AsyncFunctionDef', (1, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('Expr', (2, 1), ('ListComp', (2, 1), ('Name', (2, 2), 'i', ('Load',)), [('comprehension', ('Name', (2, 14), 'b', ('Store',)), ('Name', (2, 19), 'c', ('Load',)), [], 1)]))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (3, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('Pass', (3, 9))], [('Name', (1, 1), 'deco1', ('Load',)), ('Call', (2, 0), ('Name', (2, 1), 'deco2', ('Load',)), [], [])], Tupu, Tupu)], []),
('Module', [('AsyncFunctionDef', (3, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('Pass', (3, 15))], [('Name', (1, 1), 'deco1', ('Load',)), ('Call', (2, 0), ('Name', (2, 1), 'deco2', ('Load',)), [], [])], Tupu, Tupu)], []),
('Module', [('ClassDef', (3, 0), 'C', [], [], [('Pass', (3, 9))], [('Name', (1, 1), 'deco1', ('Load',)), ('Call', (2, 0), ('Name', (2, 1), 'deco2', ('Load',)), [], [])])], []),
('Module', [('FunctionDef', (2, 0), 'f', ('arguments', [], [], Tupu, [], [], Tupu, []), [('Pass', (2, 9))], [('Call', (1, 1), ('Name', (1, 1), 'deco', ('Load',)), [('GeneratorExp', (1, 5), ('Name', (1, 6), 'a', ('Load',)), [('comprehension', ('Name', (1, 12), 'a', ('Store',)), ('Name', (1, 17), 'b', ('Load',)), [], 0)])], [])], Tupu, Tupu)], []),
('Module', [('Expr', (1, 0), ('NamedExpr', (1, 1), ('Name', (1, 1), 'a', ('Store',)), ('Constant', (1, 6), 1, Tupu)))], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [], Tupu, [], [], Tupu, []), [('Pass', (1, 14))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [('arg', (1, 12), 'c', Tupu, Tupu), ('arg', (1, 15), 'd', Tupu, Tupu), ('arg', (1, 18), 'e', Tupu, Tupu)], Tupu, [], [], Tupu, []), [('Pass', (1, 22))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [('arg', (1, 12), 'c', Tupu, Tupu)], Tupu, [('arg', (1, 18), 'd', Tupu, Tupu), ('arg', (1, 21), 'e', Tupu, Tupu)], [Tupu, Tupu], Tupu, []), [('Pass', (1, 25))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [('arg', (1, 12), 'c', Tupu, Tupu)], Tupu, [('arg', (1, 18), 'd', Tupu, Tupu), ('arg', (1, 21), 'e', Tupu, Tupu)], [Tupu, Tupu], ('arg', (1, 26), 'kwargs', Tupu, Tupu), []), [('Pass', (1, 35))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [], Tupu, [], [], Tupu, [('Constant', (1, 8), 1, Tupu)]), [('Pass', (1, 16))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [('arg', (1, 14), 'b', Tupu, Tupu), ('arg', (1, 19), 'c', Tupu, Tupu)], Tupu, [], [], Tupu, [('Constant', (1, 8), 1, Tupu), ('Constant', (1, 16), 2, Tupu), ('Constant', (1, 21), 4, Tupu)]), [('Pass', (1, 25))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [('arg', (1, 14), 'b', Tupu, Tupu)], Tupu, [('arg', (1, 22), 'c', Tupu, Tupu)], [('Constant', (1, 24), 4, Tupu)], Tupu, [('Constant', (1, 8), 1, Tupu), ('Constant', (1, 16), 2, Tupu)]), [('Pass', (1, 28))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [('arg', (1, 14), 'b', Tupu, Tupu)], Tupu, [('arg', (1, 22), 'c', Tupu, Tupu)], [Tupu], Tupu, [('Constant', (1, 8), 1, Tupu), ('Constant', (1, 16), 2, Tupu)]), [('Pass', (1, 26))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [('arg', (1, 14), 'b', Tupu, Tupu)], Tupu, [('arg', (1, 22), 'c', Tupu, Tupu)], [('Constant', (1, 24), 4, Tupu)], ('arg', (1, 29), 'kwargs', Tupu, Tupu), [('Constant', (1, 8), 1, Tupu), ('Constant', (1, 16), 2, Tupu)]), [('Pass', (1, 38))], [], Tupu, Tupu)], []),
('Module', [('FunctionDef', (1, 0), 'f', ('arguments', [('arg', (1, 6), 'a', Tupu, Tupu)], [('arg', (1, 14), 'b', Tupu, Tupu)], Tupu, [('arg', (1, 22), 'c', Tupu, Tupu)], [Tupu], ('arg', (1, 27), 'kwargs', Tupu, Tupu), [('Constant', (1, 8), 1, Tupu), ('Constant', (1, 16), 2, Tupu)]), [('Pass', (1, 36))], [], Tupu, Tupu)], []),
]
single_results = [
('Interactive', [('Expr', (1, 0), ('BinOp', (1, 0), ('Constant', (1, 0), 1, Tupu), ('Add',), ('Constant', (1, 2), 2, Tupu)))]),
]
eval_results = [
('Expression', ('Constant', (1, 0), Tupu, Tupu)),
('Expression', ('BoolOp', (1, 0), ('And',), [('Name', (1, 0), 'a', ('Load',)), ('Name', (1, 6), 'b', ('Load',))])),
('Expression', ('BinOp', (1, 0), ('Name', (1, 0), 'a', ('Load',)), ('Add',), ('Name', (1, 4), 'b', ('Load',)))),
('Expression', ('UnaryOp', (1, 0), ('Not',), ('Name', (1, 4), 'v', ('Load',)))),
('Expression', ('Lambda', (1, 0), ('arguments', [], [], Tupu, [], [], Tupu, []), ('Constant', (1, 7), Tupu, Tupu))),
('Expression', ('Dict', (1, 0), [('Constant', (1, 2), 1, Tupu)], [('Constant', (1, 4), 2, Tupu)])),
('Expression', ('Dict', (1, 0), [], [])),
('Expression', ('Set', (1, 0), [('Constant', (1, 1), Tupu, Tupu)])),
('Expression', ('Dict', (1, 0), [('Constant', (2, 6), 1, Tupu)], [('Constant', (4, 10), 2, Tupu)])),
('Expression', ('ListComp', (1, 0), ('Name', (1, 1), 'a', ('Load',)), [('comprehension', ('Name', (1, 7), 'b', ('Store',)), ('Name', (1, 12), 'c', ('Load',)), [('Name', (1, 17), 'd', ('Load',))], 0)])),
('Expression', ('GeneratorExp', (1, 0), ('Name', (1, 1), 'a', ('Load',)), [('comprehension', ('Name', (1, 7), 'b', ('Store',)), ('Name', (1, 12), 'c', ('Load',)), [('Name', (1, 17), 'd', ('Load',))], 0)])),
('Expression', ('ListComp', (1, 0), ('Tuple', (1, 1), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 11), 'a', ('Store',)), ('Name', (1, 13), 'b', ('Store',))], ('Store',)), ('Name', (1, 18), 'c', ('Load',)), [], 0)])),
('Expression', ('ListComp', (1, 0), ('Tuple', (1, 1), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 12), 'a', ('Store',)), ('Name', (1, 14), 'b', ('Store',))], ('Store',)), ('Name', (1, 20), 'c', ('Load',)), [], 0)])),
('Expression', ('ListComp', (1, 0), ('Tuple', (1, 1), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('List', (1, 11), [('Name', (1, 12), 'a', ('Store',)), ('Name', (1, 14), 'b', ('Store',))], ('Store',)), ('Name', (1, 20), 'c', ('Load',)), [], 0)])),
('Expression', ('SetComp', (1, 0), ('Tuple', (1, 1), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 11), 'a', ('Store',)), ('Name', (1, 13), 'b', ('Store',))], ('Store',)), ('Name', (1, 18), 'c', ('Load',)), [], 0)])),
('Expression', ('SetComp', (1, 0), ('Tuple', (1, 1), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 12), 'a', ('Store',)), ('Name', (1, 14), 'b', ('Store',))], ('Store',)), ('Name', (1, 20), 'c', ('Load',)), [], 0)])),
('Expression', ('SetComp', (1, 0), ('Tuple', (1, 1), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('List', (1, 11), [('Name', (1, 12), 'a', ('Store',)), ('Name', (1, 14), 'b', ('Store',))], ('Store',)), ('Name', (1, 20), 'c', ('Load',)), [], 0)])),
('Expression', ('GeneratorExp', (1, 0), ('Tuple', (1, 1), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 11), 'a', ('Store',)), ('Name', (1, 13), 'b', ('Store',))], ('Store',)), ('Name', (1, 18), 'c', ('Load',)), [], 0)])),
('Expression', ('GeneratorExp', (1, 0), ('Tuple', (1, 1), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('Tuple', (1, 11), [('Name', (1, 12), 'a', ('Store',)), ('Name', (1, 14), 'b', ('Store',))], ('Store',)), ('Name', (1, 20), 'c', ('Load',)), [], 0)])),
('Expression', ('GeneratorExp', (1, 0), ('Tuple', (1, 1), [('Name', (1, 2), 'a', ('Load',)), ('Name', (1, 4), 'b', ('Load',))], ('Load',)), [('comprehension', ('List', (1, 11), [('Name', (1, 12), 'a', ('Store',)), ('Name', (1, 14), 'b', ('Store',))], ('Store',)), ('Name', (1, 20), 'c', ('Load',)), [], 0)])),
('Expression', ('Compare', (1, 0), ('Constant', (1, 0), 1, Tupu), [('Lt',), ('Lt',)], [('Constant', (1, 4), 2, Tupu), ('Constant', (1, 8), 3, Tupu)])),
('Expression', ('Call', (1, 0), ('Name', (1, 0), 'f', ('Load',)), [('Constant', (1, 2), 1, Tupu), ('Constant', (1, 4), 2, Tupu), ('Starred', (1, 10), ('Name', (1, 11), 'd', ('Load',)), ('Load',))], [('keyword', 'c', ('Constant', (1, 8), 3, Tupu)), ('keyword', Tupu, ('Name', (1, 15), 'e', ('Load',)))])),
('Expression', ('Call', (1, 0), ('Name', (1, 0), 'f', ('Load',)), [('GeneratorExp', (1, 1), ('Name', (1, 2), 'a', ('Load',)), [('comprehension', ('Name', (1, 8), 'a', ('Store',)), ('Name', (1, 13), 'b', ('Load',)), [], 0)])], [])),
('Expression', ('Constant', (1, 0), 10, Tupu)),
('Expression', ('Constant', (1, 0), 'string', Tupu)),
('Expression', ('Attribute', (1, 0), ('Name', (1, 0), 'a', ('Load',)), 'b', ('Load',))),
('Expression', ('Subscript', (1, 0), ('Name', (1, 0), 'a', ('Load',)), ('Slice', ('Name', (1, 2), 'b', ('Load',)), ('Name', (1, 4), 'c', ('Load',)), Tupu), ('Load',))),
('Expression', ('Name', (1, 0), 'v', ('Load',))),
('Expression', ('List', (1, 0), [('Constant', (1, 1), 1, Tupu), ('Constant', (1, 3), 2, Tupu), ('Constant', (1, 5), 3, Tupu)], ('Load',))),
('Expression', ('List', (1, 0), [], ('Load',))),
('Expression', ('Tuple', (1, 0), [('Constant', (1, 0), 1, Tupu), ('Constant', (1, 2), 2, Tupu), ('Constant', (1, 4), 3, Tupu)], ('Load',))),
('Expression', ('Tuple', (1, 0), [('Constant', (1, 1), 1, Tupu), ('Constant', (1, 3), 2, Tupu), ('Constant', (1, 5), 3, Tupu)], ('Load',))),
('Expression', ('Tuple', (1, 0), [], ('Load',))),
('Expression', ('Call', (1, 0), ('Attribute', (1, 0), ('Attribute', (1, 0), ('Attribute', (1, 0), ('Name', (1, 0), 'a', ('Load',)), 'b', ('Load',)), 'c', ('Load',)), 'd', ('Load',)), [('Subscript', (1, 8), ('Attribute', (1, 8), ('Name', (1, 8), 'a', ('Load',)), 'b', ('Load',)), ('Slice', ('Constant', (1, 12), 1, Tupu), ('Constant', (1, 14), 2, Tupu), Tupu), ('Load',))], [])),
]
main()
