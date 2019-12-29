""" Test suite kila the code kwenye fixer_util """

# Testing agizas
kutoka . agiza support

# Local agizas
kutoka lib2to3.pytree agiza Node, Leaf
kutoka lib2to3 agiza fixer_util
kutoka lib2to3.fixer_util agiza Attr, Name, Call, Comma
kutoka lib2to3.pgen2 agiza token

eleza parse(code, strip_levels=0):
    # The topmost node ni file_input, which we don't care about.
    # The next-topmost node ni a *_stmt node, which we also don't care about
    tree = support.parse_string(code)
    kila i kwenye range(strip_levels):
        tree = tree.children[0]
    tree.parent = Tupu
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
        self.assertKweli(self.is_tuple("(a, b)"))
        self.assertKweli(self.is_tuple("(a, (b, c))"))
        self.assertKweli(self.is_tuple("((a, (b, c)),)"))
        self.assertKweli(self.is_tuple("(a,)"))
        self.assertKweli(self.is_tuple("()"))

    eleza test_invalid(self):
        self.assertUongo(self.is_tuple("(a)"))
        self.assertUongo(self.is_tuple("('foo') % (b, c)"))


kundi Test_is_list(support.TestCase):
    eleza is_list(self, string):
        rudisha fixer_util.is_list(parse(string, strip_levels=2))

    eleza test_valid(self):
        self.assertKweli(self.is_list("[]"))
        self.assertKweli(self.is_list("[a]"))
        self.assertKweli(self.is_list("[a, b]"))
        self.assertKweli(self.is_list("[a, [b, c]]"))
        self.assertKweli(self.is_list("[[a, [b, c]],]"))

    eleza test_invalid(self):
        self.assertUongo(self.is_list("[]+[]"))


kundi Test_Attr(MacroTestCase):
    eleza test(self):
        call = parse("foo()", strip_levels=2)

        self.assertStr(Attr(Name("a"), Name("b")), "a.b")
        self.assertStr(Attr(call, Name("b")), "foo().b")

    eleza test_rudishas(self):
        attr = Attr(Name("a"), Name("b"))
        self.assertEqual(type(attr), list)


kundi Test_Name(MacroTestCase):
    eleza test(self):
        self.assertStr(Name("a"), "a")
        self.assertStr(Name("foo.foo().bar"), "foo.foo().bar")
        self.assertStr(Name("a", prefix="b"), "ba")


kundi Test_Call(MacroTestCase):
    eleza _Call(self, name, args=Tupu, prefix=Tupu):
        """Help the next test"""
        children = []
        ikiwa isinstance(args, list):
            kila arg kwenye args:
                children.append(arg)
                children.append(Comma())
            children.pop()
        rudisha Call(Name(name), children, prefix)

    eleza test(self):
        kids = [Tupu,
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
        # Search a tree kila a binding -- used to find the starting
        # point kila these tests.
        c = fixer_util.find_binding(name, node)
        ikiwa c: rudisha c
        kila child kwenye node.children:
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
                         (Tupu, "a", "agiza b"),
                         (Tupu, "a", "agiza b, c, d"))
        kila package, name, import_ kwenye failing_tests:
            n = self.does_tree_agiza(package, name, import_ + "\n" + string)
            self.assertUongo(n)
            n = self.does_tree_agiza(package, name, string + "\n" + import_)
            self.assertUongo(n)

        pitaing_tests = (("a", "a", "kutoka a agiza a"),
                         ("x", "a", "kutoka x agiza a"),
                         ("x", "a", "kutoka x agiza b, c, a, d"),
                         ("x.b", "a", "kutoka x.b agiza a"),
                         ("x.b", "a", "kutoka x.b agiza b, c, a, d"),
                         (Tupu, "a", "agiza a"),
                         (Tupu, "a", "agiza b, c, a, d"))
        kila package, name, import_ kwenye pitaing_tests:
            n = self.does_tree_agiza(package, name, import_ + "\n" + string)
            self.assertKweli(n)
            n = self.does_tree_agiza(package, name, string + "\n" + import_)
            self.assertKweli(n)

    eleza test_in_function(self):
        self.try_with("eleza foo():\n\tbar.baz()\n\tstart=3")

kundi Test_find_binding(support.TestCase):
    eleza find_binding(self, name, string, package=Tupu):
        rudisha fixer_util.find_binding(name, parse(string), package)

    eleza test_simple_assignment(self):
        self.assertKweli(self.find_binding("a", "a = b"))
        self.assertKweli(self.find_binding("a", "a = [b, c, d]"))
        self.assertKweli(self.find_binding("a", "a = foo()"))
        self.assertKweli(self.find_binding("a", "a = foo().foo.foo[6][foo]"))
        self.assertUongo(self.find_binding("a", "foo = a"))
        self.assertUongo(self.find_binding("a", "foo = (a, b, c)"))

    eleza test_tuple_assignment(self):
        self.assertKweli(self.find_binding("a", "(a,) = b"))
        self.assertKweli(self.find_binding("a", "(a, b, c) = [b, c, d]"))
        self.assertKweli(self.find_binding("a", "(c, (d, a), b) = foo()"))
        self.assertKweli(self.find_binding("a", "(a, b) = foo().foo[6][foo]"))
        self.assertUongo(self.find_binding("a", "(foo, b) = (b, a)"))
        self.assertUongo(self.find_binding("a", "(foo, (b, c)) = (a, b, c)"))

    eleza test_list_assignment(self):
        self.assertKweli(self.find_binding("a", "[a] = b"))
        self.assertKweli(self.find_binding("a", "[a, b, c] = [b, c, d]"))
        self.assertKweli(self.find_binding("a", "[c, [d, a], b] = foo()"))
        self.assertKweli(self.find_binding("a", "[a, b] = foo().foo[a][foo]"))
        self.assertUongo(self.find_binding("a", "[foo, b] = (b, a)"))
        self.assertUongo(self.find_binding("a", "[foo, [b, c]] = (a, b, c)"))

    eleza test_invalid_assignments(self):
        self.assertUongo(self.find_binding("a", "foo.a = 5"))
        self.assertUongo(self.find_binding("a", "foo[a] = 5"))
        self.assertUongo(self.find_binding("a", "foo(a) = 5"))
        self.assertUongo(self.find_binding("a", "foo(a, b) = 5"))

    eleza test_simple_agiza(self):
        self.assertKweli(self.find_binding("a", "agiza a"))
        self.assertKweli(self.find_binding("a", "agiza b, c, a, d"))
        self.assertUongo(self.find_binding("a", "agiza b"))
        self.assertUongo(self.find_binding("a", "agiza b, c, d"))

    eleza test_kutoka_agiza(self):
        self.assertKweli(self.find_binding("a", "kutoka x agiza a"))
        self.assertKweli(self.find_binding("a", "kutoka a agiza a"))
        self.assertKweli(self.find_binding("a", "kutoka x agiza b, c, a, d"))
        self.assertKweli(self.find_binding("a", "kutoka x.b agiza a"))
        self.assertKweli(self.find_binding("a", "kutoka x.b agiza b, c, a, d"))
        self.assertUongo(self.find_binding("a", "kutoka a agiza b"))
        self.assertUongo(self.find_binding("a", "kutoka a.d agiza b"))
        self.assertUongo(self.find_binding("a", "kutoka d.a agiza b"))

    eleza test_import_as(self):
        self.assertKweli(self.find_binding("a", "agiza b kama a"))
        self.assertKweli(self.find_binding("a", "agiza b kama a, c, a kama f, d"))
        self.assertUongo(self.find_binding("a", "agiza a kama f"))
        self.assertUongo(self.find_binding("a", "agiza b, c kama f, d kama e"))

    eleza test_kutoka_import_as(self):
        self.assertKweli(self.find_binding("a", "kutoka x agiza b kama a"))
        self.assertKweli(self.find_binding("a", "kutoka x agiza g kama a, d kama b"))
        self.assertKweli(self.find_binding("a", "kutoka x.b agiza t kama a"))
        self.assertKweli(self.find_binding("a", "kutoka x.b agiza g kama a, d"))
        self.assertUongo(self.find_binding("a", "kutoka a agiza b kama t"))
        self.assertUongo(self.find_binding("a", "kutoka a.d agiza b kama t"))
        self.assertUongo(self.find_binding("a", "kutoka d.a agiza b kama t"))

    eleza test_simple_import_with_package(self):
        self.assertKweli(self.find_binding("b", "agiza b"))
        self.assertKweli(self.find_binding("b", "agiza b, c, d"))
        self.assertUongo(self.find_binding("b", "agiza b", "b"))
        self.assertUongo(self.find_binding("b", "agiza b, c, d", "c"))

    eleza test_kutoka_import_with_package(self):
        self.assertKweli(self.find_binding("a", "kutoka x agiza a", "x"))
        self.assertKweli(self.find_binding("a", "kutoka a agiza a", "a"))
        self.assertKweli(self.find_binding("a", "kutoka x agiza *", "x"))
        self.assertKweli(self.find_binding("a", "kutoka x agiza b, c, a, d", "x"))
        self.assertKweli(self.find_binding("a", "kutoka x.b agiza a", "x.b"))
        self.assertKweli(self.find_binding("a", "kutoka x.b agiza *", "x.b"))
        self.assertKweli(self.find_binding("a", "kutoka x.b agiza b, c, a, d", "x.b"))
        self.assertUongo(self.find_binding("a", "kutoka a agiza b", "a"))
        self.assertUongo(self.find_binding("a", "kutoka a.d agiza b", "a.d"))
        self.assertUongo(self.find_binding("a", "kutoka d.a agiza b", "a.d"))
        self.assertUongo(self.find_binding("a", "kutoka x.y agiza *", "a.b"))

    eleza test_import_as_with_package(self):
        self.assertUongo(self.find_binding("a", "agiza b.c kama a", "b.c"))
        self.assertUongo(self.find_binding("a", "agiza a kama f", "f"))
        self.assertUongo(self.find_binding("a", "agiza a kama f", "a"))

    eleza test_kutoka_import_as_with_package(self):
        # Because it would take a lot of special-case code kwenye the fixers
        # to deal with kutoka foo agiza bar kama baz, we'll simply always
        # fail ikiwa there ni an "kutoka ... agiza ... kama ..."
        self.assertUongo(self.find_binding("a", "kutoka x agiza b kama a", "x"))
        self.assertUongo(self.find_binding("a", "kutoka x agiza g kama a, d kama b", "x"))
        self.assertUongo(self.find_binding("a", "kutoka x.b agiza t kama a", "x.b"))
        self.assertUongo(self.find_binding("a", "kutoka x.b agiza g kama a, d", "x.b"))
        self.assertUongo(self.find_binding("a", "kutoka a agiza b kama t", "a"))
        self.assertUongo(self.find_binding("a", "kutoka a agiza b kama t", "b"))
        self.assertUongo(self.find_binding("a", "kutoka a agiza b kama t", "t"))

    eleza test_function_def(self):
        self.assertKweli(self.find_binding("a", "eleza a(): pita"))
        self.assertKweli(self.find_binding("a", "eleza a(b, c, d): pita"))
        self.assertKweli(self.find_binding("a", "eleza a(): b = 7"))
        self.assertUongo(self.find_binding("a", "eleza d(b, (c, a), e): pita"))
        self.assertUongo(self.find_binding("a", "eleza d(a=7): pita"))
        self.assertUongo(self.find_binding("a", "eleza d(a): pita"))
        self.assertUongo(self.find_binding("a", "eleza d(): a = 7"))

        s = """
            eleza d():
                eleza a():
                    pita"""
        self.assertUongo(self.find_binding("a", s))

    eleza test_class_def(self):
        self.assertKweli(self.find_binding("a", "kundi a: pita"))
        self.assertKweli(self.find_binding("a", "kundi a(): pita"))
        self.assertKweli(self.find_binding("a", "kundi a(b): pita"))
        self.assertKweli(self.find_binding("a", "kundi a(b, c=8): pita"))
        self.assertUongo(self.find_binding("a", "kundi d: pita"))
        self.assertUongo(self.find_binding("a", "kundi d(a): pita"))
        self.assertUongo(self.find_binding("a", "kundi d(b, a=7): pita"))
        self.assertUongo(self.find_binding("a", "kundi d(b, *a): pita"))
        self.assertUongo(self.find_binding("a", "kundi d(b, **a): pita"))
        self.assertUongo(self.find_binding("a", "kundi d: a = 7"))

        s = """
            kundi d():
                kundi a():
                    pita"""
        self.assertUongo(self.find_binding("a", s))

    eleza test_for(self):
        self.assertKweli(self.find_binding("a", "kila a kwenye r: pita"))
        self.assertKweli(self.find_binding("a", "kila a, b kwenye r: pita"))
        self.assertKweli(self.find_binding("a", "kila (a, b) kwenye r: pita"))
        self.assertKweli(self.find_binding("a", "kila c, (a,) kwenye r: pita"))
        self.assertKweli(self.find_binding("a", "kila c, (a, b) kwenye r: pita"))
        self.assertKweli(self.find_binding("a", "kila c kwenye r: a = c"))
        self.assertUongo(self.find_binding("a", "kila c kwenye a: pita"))

    eleza test_for_nested(self):
        s = """
            kila b kwenye r:
                kila a kwenye b:
                    pita"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            kila b kwenye r:
                kila a, c kwenye b:
                    pita"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            kila b kwenye r:
                kila (a, c) kwenye b:
                    pita"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            kila b kwenye r:
                kila (a,) kwenye b:
                    pita"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            kila b kwenye r:
                kila c, (a, d) kwenye b:
                    pita"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            kila b kwenye r:
                kila c kwenye b:
                    a = 7"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            kila b kwenye r:
                kila c kwenye b:
                    d = a"""
        self.assertUongo(self.find_binding("a", s))

        s = """
            kila b kwenye r:
                kila c kwenye a:
                    d = 7"""
        self.assertUongo(self.find_binding("a", s))

    eleza test_if(self):
        self.assertKweli(self.find_binding("a", "ikiwa b kwenye r: a = c"))
        self.assertUongo(self.find_binding("a", "ikiwa a kwenye r: d = e"))

    eleza test_if_nested(self):
        s = """
            ikiwa b kwenye r:
                ikiwa c kwenye d:
                    a = c"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            ikiwa b kwenye r:
                ikiwa c kwenye d:
                    c = a"""
        self.assertUongo(self.find_binding("a", s))

    eleza test_while(self):
        self.assertKweli(self.find_binding("a", "wakati b kwenye r: a = c"))
        self.assertUongo(self.find_binding("a", "wakati a kwenye r: d = e"))

    eleza test_while_nested(self):
        s = """
            wakati b kwenye r:
                wakati c kwenye d:
                    a = c"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            wakati b kwenye r:
                wakati c kwenye d:
                    c = a"""
        self.assertUongo(self.find_binding("a", s))

    eleza test_try_except(self):
        s = """
            jaribu:
                a = 6
            except:
                b = 8"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            except:
                a = 6"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            tatizo KeyError:
                pita
            except:
                a = 6"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            except:
                b = 6"""
        self.assertUongo(self.find_binding("a", s))

    eleza test_try_except_nested(self):
        s = """
            jaribu:
                jaribu:
                    a = 6
                except:
                    pita
            except:
                b = 8"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            except:
                jaribu:
                    a = 6
                except:
                    pita"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            except:
                jaribu:
                    pita
                except:
                    a = 6"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                jaribu:
                    b = 8
                tatizo KeyError:
                    pita
                except:
                    a = 6
            except:
                pita"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                pita
            except:
                jaribu:
                    b = 8
                tatizo KeyError:
                    pita
                except:
                    a = 6"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            except:
                b = 6"""
        self.assertUongo(self.find_binding("a", s))

        s = """
            jaribu:
                jaribu:
                    b = 8
                except:
                    c = d
            except:
                jaribu:
                    b = 6
                except:
                    t = 8
                except:
                    o = y"""
        self.assertUongo(self.find_binding("a", s))

    eleza test_try_except_finally(self):
        s = """
            jaribu:
                c = 6
            except:
                b = 8
            mwishowe:
                a = 9"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            mwishowe:
                a = 6"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            mwishowe:
                b = 6"""
        self.assertUongo(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            except:
                b = 9
            mwishowe:
                b = 6"""
        self.assertUongo(self.find_binding("a", s))

    eleza test_try_except_finally_nested(self):
        s = """
            jaribu:
                c = 6
            except:
                b = 8
            mwishowe:
                jaribu:
                    a = 9
                except:
                    b = 9
                mwishowe:
                    c = 9"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            mwishowe:
                jaribu:
                    pita
                mwishowe:
                    a = 6"""
        self.assertKweli(self.find_binding("a", s))

        s = """
            jaribu:
                b = 8
            mwishowe:
                jaribu:
                    b = 6
                mwishowe:
                    b = 7"""
        self.assertUongo(self.find_binding("a", s))

kundi Test_touch_agiza(support.TestCase):

    eleza test_after_docstring(self):
        node = parse('"""foo"""\nbar()')
        fixer_util.touch_agiza(Tupu, "foo", node)
        self.assertEqual(str(node), '"""foo"""\nagiza foo\nbar()\n\n')

    eleza test_after_agizas(self):
        node = parse('"""foo"""\nagiza bar\nbar()')
        fixer_util.touch_agiza(Tupu, "foo", node)
        self.assertEqual(str(node), '"""foo"""\nagiza bar\nagiza foo\nbar()\n\n')

    eleza test_beginning(self):
        node = parse('bar()')
        fixer_util.touch_agiza(Tupu, "foo", node)
        self.assertEqual(str(node), 'agiza foo\nbar()\n\n')

    eleza test_kutoka_agiza(self):
        node = parse('bar()')
        fixer_util.touch_agiza("html", "escape", node)
        self.assertEqual(str(node), 'kutoka html agiza escape\nbar()\n\n')

    eleza test_name_agiza(self):
        node = parse('bar()')
        fixer_util.touch_agiza(Tupu, "cgi", node)
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
