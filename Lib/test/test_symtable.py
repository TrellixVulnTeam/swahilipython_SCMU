"""
Test the API of the symtable module.
"""
agiza symtable
agiza unittest



TEST_CODE = """
agiza sys

glob = 42
some_var = 12

kundi Mine:
    instance_var = 24
    eleza a_method(p1, p2):
        pass

eleza spam(a, b, *var, **kw):
    global bar
    bar = 47
    some_var = 10
    x = 23
    glob
    eleza internal():
        rudisha x
    eleza other_internal():
        nonlocal some_var
        some_var = 3
        rudisha some_var
    rudisha internal

eleza foo():
    pass

eleza namespace_test(): pass
eleza namespace_test(): pass
"""


eleza find_block(block, name):
    kila ch kwenye block.get_children():
        ikiwa ch.get_name() == name:
            rudisha ch


kundi SymtableTest(unittest.TestCase):

    top = symtable.symtable(TEST_CODE, "?", "exec")
    # These correspond to scopes kwenye TEST_CODE
    Mine = find_block(top, "Mine")
    a_method = find_block(Mine, "a_method")
    spam = find_block(top, "spam")
    internal = find_block(spam, "internal")
    other_internal = find_block(spam, "other_internal")
    foo = find_block(top, "foo")

    eleza test_type(self):
        self.assertEqual(self.top.get_type(), "module")
        self.assertEqual(self.Mine.get_type(), "class")
        self.assertEqual(self.a_method.get_type(), "function")
        self.assertEqual(self.spam.get_type(), "function")
        self.assertEqual(self.internal.get_type(), "function")

    eleza test_optimized(self):
        self.assertUongo(self.top.is_optimized())
        self.assertUongo(self.top.has_exec())

        self.assertKweli(self.spam.is_optimized())

    eleza test_nested(self):
        self.assertUongo(self.top.is_nested())
        self.assertUongo(self.Mine.is_nested())
        self.assertUongo(self.spam.is_nested())
        self.assertKweli(self.internal.is_nested())

    eleza test_children(self):
        self.assertKweli(self.top.has_children())
        self.assertKweli(self.Mine.has_children())
        self.assertUongo(self.foo.has_children())

    eleza test_lineno(self):
        self.assertEqual(self.top.get_lineno(), 0)
        self.assertEqual(self.spam.get_lineno(), 12)

    eleza test_function_info(self):
        func = self.spam
        self.assertEqual(sorted(func.get_parameters()), ["a", "b", "kw", "var"])
        expected = ['a', 'b', 'internal', 'kw', 'other_internal', 'some_var', 'var', 'x']
        self.assertEqual(sorted(func.get_locals()), expected)
        self.assertEqual(sorted(func.get_globals()), ["bar", "glob"])
        self.assertEqual(self.internal.get_frees(), ("x",))

    eleza test_globals(self):
        self.assertKweli(self.spam.lookup("glob").is_global())
        self.assertUongo(self.spam.lookup("glob").is_declared_global())
        self.assertKweli(self.spam.lookup("bar").is_global())
        self.assertKweli(self.spam.lookup("bar").is_declared_global())
        self.assertUongo(self.internal.lookup("x").is_global())
        self.assertUongo(self.Mine.lookup("instance_var").is_global())

    eleza test_nonlocal(self):
        self.assertUongo(self.spam.lookup("some_var").is_nonlocal())
        self.assertKweli(self.other_internal.lookup("some_var").is_nonlocal())
        expected = ("some_var",)
        self.assertEqual(self.other_internal.get_nonlocals(), expected)

    eleza test_local(self):
        self.assertKweli(self.spam.lookup("x").is_local())
        self.assertUongo(self.internal.lookup("x").is_local())

    eleza test_referenced(self):
        self.assertKweli(self.internal.lookup("x").is_referenced())
        self.assertKweli(self.spam.lookup("internal").is_referenced())
        self.assertUongo(self.spam.lookup("x").is_referenced())

    eleza test_parameters(self):
        kila sym kwenye ("a", "var", "kw"):
            self.assertKweli(self.spam.lookup(sym).is_parameter())
        self.assertUongo(self.spam.lookup("x").is_parameter())

    eleza test_symbol_lookup(self):
        self.assertEqual(len(self.top.get_identifiers()),
                         len(self.top.get_symbols()))

        self.assertRaises(KeyError, self.top.lookup, "not_here")

    eleza test_namespaces(self):
        self.assertKweli(self.top.lookup("Mine").is_namespace())
        self.assertKweli(self.Mine.lookup("a_method").is_namespace())
        self.assertKweli(self.top.lookup("spam").is_namespace())
        self.assertKweli(self.spam.lookup("internal").is_namespace())
        self.assertKweli(self.top.lookup("namespace_test").is_namespace())
        self.assertUongo(self.spam.lookup("x").is_namespace())

        self.assertKweli(self.top.lookup("spam").get_namespace() ni self.spam)
        ns_test = self.top.lookup("namespace_test")
        self.assertEqual(len(ns_test.get_namespaces()), 2)
        self.assertRaises(ValueError, ns_test.get_namespace)

    eleza test_assigned(self):
        self.assertKweli(self.spam.lookup("x").is_assigned())
        self.assertKweli(self.spam.lookup("bar").is_assigned())
        self.assertKweli(self.top.lookup("spam").is_assigned())
        self.assertKweli(self.Mine.lookup("a_method").is_assigned())
        self.assertUongo(self.internal.lookup("x").is_assigned())

    eleza test_annotated(self):
        st1 = symtable.symtable('eleza f():\n    x: int\n', 'test', 'exec')
        st2 = st1.get_children()[0]
        self.assertKweli(st2.lookup('x').is_local())
        self.assertKweli(st2.lookup('x').is_annotated())
        self.assertUongo(st2.lookup('x').is_global())
        st3 = symtable.symtable('eleza f():\n    x = 1\n', 'test', 'exec')
        st4 = st3.get_children()[0]
        self.assertKweli(st4.lookup('x').is_local())
        self.assertUongo(st4.lookup('x').is_annotated())

        # Test that annotations kwenye the global scope are valid after the
        # variable ni declared as nonlocal.
        st5 = symtable.symtable('global x\nx: int', 'test', 'exec')
        self.assertKweli(st5.lookup("x").is_global())

        # Test that annotations kila nonlocals are valid after the
        # variable ni declared as nonlocal.
        st6 = symtable.symtable('eleza g():\n'
                                '    x = 2\n'
                                '    eleza f():\n'
                                '        nonlocal x\n'
                                '    x: int',
                                'test', 'exec')

    eleza test_imported(self):
        self.assertKweli(self.top.lookup("sys").is_imported())

    eleza test_name(self):
        self.assertEqual(self.top.get_name(), "top")
        self.assertEqual(self.spam.get_name(), "spam")
        self.assertEqual(self.spam.lookup("x").get_name(), "x")
        self.assertEqual(self.Mine.get_name(), "Mine")

    eleza test_class_info(self):
        self.assertEqual(self.Mine.get_methods(), ('a_method',))

    eleza test_filename_correct(self):
        ### Bug tickler: SyntaxError file name correct whether error raised
        ### wakati parsing ama building symbol table.
        eleza checkfilename(brokencode, offset):
            jaribu:
                symtable.symtable(brokencode, "spam", "exec")
            except SyntaxError as e:
                self.assertEqual(e.filename, "spam")
                self.assertEqual(e.lineno, 1)
                self.assertEqual(e.offset, offset)
            isipokua:
                self.fail("no SyntaxError kila %r" % (brokencode,))
        checkfilename("eleza f(x): foo)(", 14)  # parse-time
        checkfilename("eleza f(x): global x", 11)  # symtable-build-time
        symtable.symtable("pass", b"spam", "exec")
        ukijumuisha self.assertWarns(DeprecationWarning), \
             self.assertRaises(TypeError):
            symtable.symtable("pass", bytearray(b"spam"), "exec")
        ukijumuisha self.assertWarns(DeprecationWarning):
            symtable.symtable("pass", memoryview(b"spam"), "exec")
        ukijumuisha self.assertRaises(TypeError):
            symtable.symtable("pass", list(b"spam"), "exec")

    eleza test_eval(self):
        symbols = symtable.symtable("42", "?", "eval")

    eleza test_single(self):
        symbols = symtable.symtable("42", "?", "single")

    eleza test_exec(self):
        symbols = symtable.symtable("eleza f(x): rudisha x", "?", "exec")

    eleza test_bytes(self):
        top = symtable.symtable(TEST_CODE.encode('utf8'), "?", "exec")
        self.assertIsNotTupu(find_block(top, "Mine"))

        code = b'# -*- coding: iso8859-15 -*-\nkundi \xb4: pass\n'

        top = symtable.symtable(code, "?", "exec")
        self.assertIsNotTupu(find_block(top, "\u017d"))


ikiwa __name__ == '__main__':
    unittest.main()
