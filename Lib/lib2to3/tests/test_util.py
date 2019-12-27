""" Test suite for the code in fixer_util """

# Testing agizas
kutoka . agiza support

# Local agizas
kutoka lib2to3.pytree agiza Node, Leaf
kutoka lib2to3 agiza fixer_util
kutoka lib2to3.fixer_util agiza Attr, Name, Call, Comma
kutoka lib2to3.pgen2 agiza token

eleza parse(code, strip_levels=0):
    # The topmost node is file_input, which we don't care about.
    # The next-topmost node is a *_stmt node, which we also don't care about
    tree = support.parse_string(code)
    for i in range(strip_levels):
        tree = tree.children[0]
    tree.parent = None
    rudisha tree

kundi MacroTestCase(support.TestCase):
    eleza assertStr(self, node, string):
        ikiwa isinstance(node, (tuple, list)):
            node = Node(fixer_util.syms.simple_stmt, node)
        self.assertEqual(str(node), string)


kundi Test_is_tuple(support.TestCase):
    eleza is_tuple(self, string):
        rudisha fixer_util.is_tuple(parse(string, strip_levels=2))

    eleza test_valid(self):
        self.assertTrue(self.is_tuple("(a, b)"))
        self.assertTrue(self.is_tuple("(a, (b, c))"))
        self.assertTrue(self.is_tuple("((a, (b, c)),)"))
        self.assertTrue(self.is_tuple("(a,)"))
        self.assertTrue(self.is_tuple("()"))

    eleza test_invalid(self):
        self.assertFalse(self.is_tuple("(a)"))
        self.assertFalse(self.is_tuple("('foo') % (b, c)"))


kundi Test_is_list(support.TestCase):
    eleza is_list(self, string):
        rudisha fixer_util.is_list(parse(string, strip_levels=2))

    eleza test_valid(self):
        self.assertTrue(self.is_list("[]"))
        self.assertTrue(self.is_list("[a]"))
        self.assertTrue(self.is_list("[a, b]"))
        self.assertTrue(self.is_list("[a, [b, c]]"))
        self.assertTrue(self.is_list("[[a, [b, c]],]"))

    eleza test_invalid(self):
        self.assertFalse(self.is_list("[]+[]"))


kundi Test_Attr(MacroTestCase):
    eleza test(self):
        call = parse("foo()", strip_levels=2)

        self.assertStr(Attr(Name("a"), Name("b")), "a.b")
        self.assertStr(Attr(call, Name("b")), "foo().b")

    eleza test_returns(self):
        attr = Attr(Name("a"), Name("b"))
        self.assertEqual(type(attr), list)


kundi Test_Name(MacroTestCase):
    eleza test(self):
        self.assertStr(Name("a"), "a")
        self.assertStr(Name("foo.foo().bar"), "foo.foo().bar")
        self.assertStr(Name("a", prefix="b"), "ba")


kundi Test_Call(MacroTestCase):
    eleza _Call(self, name, args=None, prefix=None):
        """Help the next test"""
        children = []
        ikiwa isinstance(args, list):
            for arg in args:
                children.append(arg)
                children.append(Comma())
            children.pop()
        rudisha Call(Name(name), children, prefix)

    eleza test(self):
        kids = [None,
                [Leaf(token.NUMBER, 1), Leaf(token.NUMBER, 2),
                 Leaf(token.NUMBER, 3)],
                [Leaf(token.NUMBER, 1), Leaf(token.NUMBER, 3),
                 Leaf(token.NUMBER, 2), Leaf(token.NUMBER, 4)],
                [Leaf(token.STRING, "b"), Leaf(token.STRING, "j", prefix=" ")]
                ]
        self.assertStr(self._Call("A"), "A()")
        self.assertStr(self._Call("b", kids[1]), "b(1,2,3)")
        self.assertStr(self._Call("a.b().c", kids[2]), "a.b().c(1,3,2,4)")
        self.assertStr(self._Call("d", kids[3], prefix=" "), " d(b, j)")


kundi Test_does_tree_agiza(support.TestCase):
    eleza _find_bind_rec(self, name, node):
        # Search a tree for a binding -- used to find the starting
        # point for these tests.
        c = fixer_util.find_binding(name, node)
        ikiwa c: rudisha c
        for child in node.children:
            c = self._find_bind_rec(name, child)
            ikiwa c: rudisha c

    eleza does_tree_agiza(self, package, name, string):
        node = parse(string)
        # Find the binding of start -- that's what we'll go kutoka
        node = self._find_bind_rec('start', node)
        rudisha fixer_util.does_tree_agiza(package, name, node)

    eleza try_with(self, string):
        failing_tests = (("a", "a", "kutoka a agiza b"),
                         ("a.d", "a", "kutoka a.d agiza b"),
                         ("d.a", "a", "kutoka d.a agiza b"),
                         (None, "a", "agiza b"),
                         (None, "a", "agiza b, c, d"))
        for package, name, import_ in failing_tests:
            n = self.does_tree_agiza(package, name, import_ + "\n" + string)
            self.assertFalse(n)
            n = self.does_tree_agiza(package, name, string + "\n" + import_)
            self.assertFalse(n)

        passing_tests = (("a", "a", "kutoka a agiza a"),
                         ("x", "a", "kutoka x agiza a"),
                         ("x", "a", "kutoka x agiza b, c, a, d"),
                         ("x.b", "a", "kutoka x.b agiza a"),
                         ("x.b", "a", "kutoka x.b agiza b, c, a, d"),
                         (None, "a", "agiza a"),
                         (None, "a", "agiza b, c, a, d"))
        for package, name, import_ in passing_tests:
            n = self.does_tree_agiza(package, name, import_ + "\n" + string)
            self.assertTrue(n)
            n = self.does_tree_agiza(package, name, string + "\n" + import_)
            self.assertTrue(n)

    eleza test_in_function(self):
        self.try_with("eleza foo():\n\tbar.baz()\n\tstart=3")

kundi Test_find_binding(support.TestCase):
    eleza find_binding(self, name, string, package=None):
        rudisha fixer_util.find_binding(name, parse(string), package)

    eleza test_simple_assignment(self):
        self.assertTrue(self.find_binding("a", "a = b"))
        self.assertTrue(self.find_binding("a", "a = [b, c, d]"))
        self.assertTrue(self.find_binding("a", "a = foo()"))
        self.assertTrue(self.find_binding("a", "a = foo().foo.foo[6][foo]"))
        self.assertFalse(self.find_binding("a", "foo = a"))
        self.assertFalse(self.find_binding("a", "foo = (a, b, c)"))

    eleza test_tuple_assignment(self):
        self.assertTrue(self.find_binding("a", "(a,) = b"))
        self.assertTrue(self.find_binding("a", "(a, b, c) = [b, c, d]"))
        self.assertTrue(self.find_binding("a", "(c, (d, a), b) = foo()"))
        self.assertTrue(self.find_binding("a", "(a, b) = foo().foo[6][foo]"))
        self.assertFalse(self.find_binding("a", "(foo, b) = (b, a)"))
        self.assertFalse(self.find_binding("a", "(foo, (b, c)) = (a, b, c)"))

    eleza test_list_assignment(self):
        self.assertTrue(self.find_binding("a", "[a] = b"))
        self.assertTrue(self.find_binding("a", "[a, b, c] = [b, c, d]"))
        self.assertTrue(self.find_binding("a", "[c, [d, a], b] = foo()"))
        self.assertTrue(self.find_binding("a", "[a, b] = foo().foo[a][foo]"))
        self.assertFalse(self.find_binding("a", "[foo, b] = (b, a)"))
        self.assertFalse(self.find_binding("a", "[foo, [b, c]] = (a, b, c)"))

    eleza test_invalid_assignments(self):
        self.assertFalse(self.find_binding("a", "foo.a = 5"))
        self.assertFalse(self.find_binding("a", "foo[a] = 5"))
        self.assertFalse(self.find_binding("a", "foo(a) = 5"))
        self.assertFalse(self.find_binding("a", "foo(a, b) = 5"))

    eleza test_simple_agiza(self):
        self.assertTrue(self.find_binding("a", "agiza a"))
        self.assertTrue(self.find_binding("a", "agiza b, c, a, d"))
        self.assertFalse(self.find_binding("a", "agiza b"))
        self.assertFalse(self.find_binding("a", "agiza b, c, d"))

    eleza test_kutoka_agiza(self):
        self.assertTrue(self.find_binding("a", "kutoka x agiza a"))
        self.assertTrue(self.find_binding("a", "kutoka a agiza a"))
        self.assertTrue(self.find_binding("a", "kutoka x agiza b, c, a, d"))
        self.assertTrue(self.find_binding("a", "kutoka x.b agiza a"))
        self.assertTrue(self.find_binding("a", "kutoka x.b agiza b, c, a, d"))
        self.assertFalse(self.find_binding("a", "kutoka a agiza b"))
        self.assertFalse(self.find_binding("a", "kutoka a.d agiza b"))
        self.assertFalse(self.find_binding("a", "kutoka d.a agiza b"))

    eleza test_import_as(self):
        self.assertTrue(self.find_binding("a", "agiza b as a"))
        self.assertTrue(self.find_binding("a", "agiza b as a, c, a as f, d"))
        self.assertFalse(self.find_binding("a", "agiza a as f"))
        self.assertFalse(self.find_binding("a", "agiza b, c as f, d as e"))

    eleza test_kutoka_import_as(self):
        self.assertTrue(self.find_binding("a", "kutoka x agiza b as a"))
        self.assertTrue(self.find_binding("a", "kutoka x agiza g as a, d as b"))
        self.assertTrue(self.find_binding("a", "kutoka x.b agiza t as a"))
        self.assertTrue(self.find_binding("a", "kutoka x.b agiza g as a, d"))
        self.assertFalse(self.find_binding("a", "kutoka a agiza b as t"))
        self.assertFalse(self.find_binding("a", "kutoka a.d agiza b as t"))
        self.assertFalse(self.find_binding("a", "kutoka d.a agiza b as t"))

    eleza test_simple_import_with_package(self):
        self.assertTrue(self.find_binding("b", "agiza b"))
        self.assertTrue(self.find_binding("b", "agiza b, c, d"))
        self.assertFalse(self.find_binding("b", "agiza b", "b"))
        self.assertFalse(self.find_binding("b", "agiza b, c, d", "c"))

    eleza test_kutoka_import_with_package(self):
        self.assertTrue(self.find_binding("a", "kutoka x agiza a", "x"))
        self.assertTrue(self.find_binding("a", "kutoka a agiza a", "a"))
        self.assertTrue(self.find_binding("a", "kutoka x agiza *", "x"))
        self.assertTrue(self.find_binding("a", "kutoka x agiza b, c, a, d", "x"))
        self.assertTrue(self.find_binding("a", "kutoka x.b agiza a", "x.b"))
        self.assertTrue(self.find_binding("a", "kutoka x.b agiza *", "x.b"))
        self.assertTrue(self.find_binding("a", "kutoka x.b agiza b, c, a, d", "x.b"))
        self.assertFalse(self.find_binding("a", "kutoka a agiza b", "a"))
        self.assertFalse(self.find_binding("a", "kutoka a.d agiza b", "a.d"))
        self.assertFalse(self.find_binding("a", "kutoka d.a agiza b", "a.d"))
        self.assertFalse(self.find_binding("a", "kutoka x.y agiza *", "a.b"))

    eleza test_import_as_with_package(self):
        self.assertFalse(self.find_binding("a", "agiza b.c as a", "b.c"))
        self.assertFalse(self.find_binding("a", "agiza a as f", "f"))
        self.assertFalse(self.find_binding("a", "agiza a as f", "a"))

    eleza test_kutoka_import_as_with_package(self):
        # Because it would take a lot of special-case code in the fixers
        # to deal with kutoka foo agiza bar as baz, we'll simply always
        # fail ikiwa there is an "kutoka ... agiza ... as ..."
        self.assertFalse(self.find_binding("a", "kutoka x agiza b as a", "x"))
        self.assertFalse(self.find_binding("a", "kutoka x agiza g as a, d as b", "x"))
        self.assertFalse(self.find_binding("a", "kutoka x.b agiza t as a", "x.b"))
        self.assertFalse(self.find_binding("a", "kutoka x.b agiza g as a, d", "x.b"))
        self.assertFalse(self.find_binding("a", "kutoka a agiza b as t", "a"))
        self.assertFalse(self.find_binding("a", "kutoka a agiza b as t", "b"))
        self.assertFalse(self.find_binding("a", "kutoka a agiza b as t", "t"))

    eleza test_function_def(self):
        self.assertTrue(self.find_binding("a", "eleza a(): pass"))
        self.assertTrue(self.find_binding("a", "eleza a(b, c, d): pass"))
        self.assertTrue(self.find_binding("a", "eleza a(): b = 7"))
        self.assertFalse(self.find_binding("a", "eleza d(b, (c, a), e): pass"))
        self.assertFalse(self.find_binding("a", "eleza d(a=7): pass"))
        self.assertFalse(self.find_binding("a", "eleza d(a): pass"))
        self.assertFalse(self.find_binding("a", "eleza d(): a = 7"))

        s = """
            eleza d():
                eleza a():
                    pass"""
        self.assertFalse(self.find_binding("a", s))

    eleza test_class_def(self):
        self.assertTrue(self.find_binding("a", "kundi a: pass"))
        self.assertTrue(self.find_binding("a", "kundi a(): pass"))
        self.assertTrue(self.find_binding("a", "kundi a(b): pass"))
        self.assertTrue(self.find_binding("a", "kundi a(b, c=8): pass"))
        self.assertFalse(self.find_binding("a", "kundi d: pass"))
        self.assertFalse(self.find_binding("a", "kundi d(a): pass"))
        self.assertFalse(self.find_binding("a", "kundi d(b, a=7): pass"))
        self.assertFalse(self.find_binding("a", "kundi d(b, *a): pass"))
        self.assertFalse(self.find_binding("a", "kundi d(b, **a): pass"))
        self.assertFalse(self.find_binding("a", "kundi d: a = 7"))

        s = """
            kundi d():
                kundi a():
                    pass"""
        self.assertFalse(self.find_binding("a", s))

    eleza test_for(self):
        self.assertTrue(self.find_binding("a", "for a in r: pass"))
        self.assertTrue(self.find_binding("a", "for a, b in r: pass"))
        self.assertTrue(self.find_binding("a", "for (a, b) in r: pass"))
        self.assertTrue(self.find_binding("a", "for c, (a,) in r: pass"))
        self.assertTrue(self.find_binding("a", "for c, (a, b) in r: pass"))
        self.assertTrue(self.find_binding("a", "for c in r: a = c"))
        self.assertFalse(self.find_binding("a", "for c in a: pass"))

    eleza test_for_nested(self):
        s = """
            for b in r:
                for a in b:
                    pass"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            for b in r:
                for a, c in b:
                    pass"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            for b in r:
                for (a, c) in b:
                    pass"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            for b in r:
                for (a,) in b:
                    pass"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            for b in r:
                for c, (a, d) in b:
                    pass"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            for b in r:
                for c in b:
                    a = 7"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            for b in r:
                for c in b:
                    d = a"""
        self.assertFalse(self.find_binding("a", s))

        s = """
            for b in r:
                for c in a:
                    d = 7"""
        self.assertFalse(self.find_binding("a", s))

    eleza test_if(self):
        self.assertTrue(self.find_binding("a", "ikiwa b in r: a = c"))
        self.assertFalse(self.find_binding("a", "ikiwa a in r: d = e"))

    eleza test_if_nested(self):
        s = """
            ikiwa b in r:
                ikiwa c in d:
                    a = c"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            ikiwa b in r:
                ikiwa c in d:
                    c = a"""
        self.assertFalse(self.find_binding("a", s))

    eleza test_while(self):
        self.assertTrue(self.find_binding("a", "while b in r: a = c"))
        self.assertFalse(self.find_binding("a", "while a in r: d = e"))

    eleza test_while_nested(self):
        s = """
            while b in r:
                while c in d:
                    a = c"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            while b in r:
                while c in d:
                    c = a"""
        self.assertFalse(self.find_binding("a", s))

    eleza test_try_except(self):
        s = """
            try:
                a = 6
            except:
                b = 8"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            except:
                a = 6"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            except KeyError:
                pass
            except:
                a = 6"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            except:
                b = 6"""
        self.assertFalse(self.find_binding("a", s))

    eleza test_try_except_nested(self):
        s = """
            try:
                try:
                    a = 6
                except:
                    pass
            except:
                b = 8"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            except:
                try:
                    a = 6
                except:
                    pass"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            except:
                try:
                    pass
                except:
                    a = 6"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                try:
                    b = 8
                except KeyError:
                    pass
                except:
                    a = 6
            except:
                pass"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                pass
            except:
                try:
                    b = 8
                except KeyError:
                    pass
                except:
                    a = 6"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            except:
                b = 6"""
        self.assertFalse(self.find_binding("a", s))

        s = """
            try:
                try:
                    b = 8
                except:
                    c = d
            except:
                try:
                    b = 6
                except:
                    t = 8
                except:
                    o = y"""
        self.assertFalse(self.find_binding("a", s))

    eleza test_try_except_finally(self):
        s = """
            try:
                c = 6
            except:
                b = 8
            finally:
                a = 9"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            finally:
                a = 6"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            finally:
                b = 6"""
        self.assertFalse(self.find_binding("a", s))

        s = """
            try:
                b = 8
            except:
                b = 9
            finally:
                b = 6"""
        self.assertFalse(self.find_binding("a", s))

    eleza test_try_except_finally_nested(self):
        s = """
            try:
                c = 6
            except:
                b = 8
            finally:
                try:
                    a = 9
                except:
                    b = 9
                finally:
                    c = 9"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            finally:
                try:
                    pass
                finally:
                    a = 6"""
        self.assertTrue(self.find_binding("a", s))

        s = """
            try:
                b = 8
            finally:
                try:
                    b = 6
                finally:
                    b = 7"""
        self.assertFalse(self.find_binding("a", s))

kundi Test_touch_agiza(support.TestCase):

    eleza test_after_docstring(self):
        node = parse('"""foo"""\nbar()')
        fixer_util.touch_agiza(None, "foo", node)
        self.assertEqual(str(node), '"""foo"""\nagiza foo\nbar()\n\n')

    eleza test_after_agizas(self):
        node = parse('"""foo"""\nagiza bar\nbar()')
        fixer_util.touch_agiza(None, "foo", node)
        self.assertEqual(str(node), '"""foo"""\nagiza bar\nagiza foo\nbar()\n\n')

    eleza test_beginning(self):
        node = parse('bar()')
        fixer_util.touch_agiza(None, "foo", node)
        self.assertEqual(str(node), 'agiza foo\nbar()\n\n')

    eleza test_kutoka_agiza(self):
        node = parse('bar()')
        fixer_util.touch_agiza("html", "escape", node)
        self.assertEqual(str(node), 'kutoka html agiza escape\nbar()\n\n')

    eleza test_name_agiza(self):
        node = parse('bar()')
        fixer_util.touch_agiza(None, "cgi", node)
        self.assertEqual(str(node), 'agiza cgi\nbar()\n\n')

kundi Test_find_indentation(support.TestCase):

    eleza test_nothing(self):
        fi = fixer_util.find_indentation
        node = parse("node()")
        self.assertEqual(fi(node), "")
        node = parse("")
        self.assertEqual(fi(node), "")

    eleza test_simple(self):
        fi = fixer_util.find_indentation
        node = parse("eleza f():\n    x()")
        self.assertEqual(fi(node), "")
        self.assertEqual(fi(node.children[0].children[4].children[2]), "    ")
        node = parse("eleza f():\n    x()\n    y()")
        self.assertEqual(fi(node.children[0].children[4].children[4]), "    ")
