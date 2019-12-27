agiza dis
agiza math
agiza os
agiza unittest
agiza sys
agiza _ast
agiza tempfile
agiza types
kutoka test agiza support
kutoka test.support agiza script_helper, FakePath

kundi TestSpecifics(unittest.TestCase):

    eleza compile_single(self, source):
        compile(source, "<single>", "single")

    eleza assertInvalidSingle(self, source):
        self.assertRaises(SyntaxError, self.compile_single, source)

    eleza test_no_ending_newline(self):
        compile("hi", "<test>", "exec")
        compile("hi\r", "<test>", "exec")

    eleza test_empty(self):
        compile("", "<test>", "exec")

    eleza test_other_newlines(self):
        compile("\r\n", "<test>", "exec")
        compile("\r", "<test>", "exec")
        compile("hi\r\nstuff\r\neleza f():\n    pass\r", "<test>", "exec")
        compile("this_is\rreally_old_mac\releza f():\n    pass", "<test>", "exec")

    eleza test_debug_assignment(self):
        # catch assignments to __debug__
        self.assertRaises(SyntaxError, compile, '__debug__ = 1', '?', 'single')
        agiza builtins
        prev = builtins.__debug__
        setattr(builtins, '__debug__', 'sure')
        self.assertEqual(__debug__, prev)
        setattr(builtins, '__debug__', prev)

    eleza test_argument_handling(self):
        # detect duplicate positional and keyword arguments
        self.assertRaises(SyntaxError, eval, 'lambda a,a:0')
        self.assertRaises(SyntaxError, eval, 'lambda a,a=1:0')
        self.assertRaises(SyntaxError, eval, 'lambda a=1,a=1:0')
        self.assertRaises(SyntaxError, exec, 'eleza f(a, a): pass')
        self.assertRaises(SyntaxError, exec, 'eleza f(a = 0, a = 1): pass')
        self.assertRaises(SyntaxError, exec, 'eleza f(a): global a; a = 1')

    eleza test_syntax_error(self):
        self.assertRaises(SyntaxError, compile, "1+*3", "filename", "exec")

    eleza test_none_keyword_arg(self):
        self.assertRaises(SyntaxError, compile, "f(None=1)", "<string>", "exec")

    eleza test_duplicate_global_local(self):
        self.assertRaises(SyntaxError, exec, 'eleza f(a): global a; a = 1')

    eleza test_exec_with_general_mapping_for_locals(self):

        kundi M:
            "Test mapping interface versus possible calls kutoka eval()."
            eleza __getitem__(self, key):
                ikiwa key == 'a':
                    rudisha 12
                raise KeyError
            eleza __setitem__(self, key, value):
                self.results = (key, value)
            eleza keys(self):
                rudisha list('xyz')

        m = M()
        g = globals()
        exec('z = a', g, m)
        self.assertEqual(m.results, ('z', 12))
        try:
            exec('z = b', g, m)
        except NameError:
            pass
        else:
            self.fail('Did not detect a KeyError')
        exec('z = dir()', g, m)
        self.assertEqual(m.results, ('z', list('xyz')))
        exec('z = globals()', g, m)
        self.assertEqual(m.results, ('z', g))
        exec('z = locals()', g, m)
        self.assertEqual(m.results, ('z', m))
        self.assertRaises(TypeError, exec, 'z = b', m)

        kundi A:
            "Non-mapping"
            pass
        m = A()
        self.assertRaises(TypeError, exec, 'z = a', g, m)

        # Verify that dict subclasses work as well
        kundi D(dict):
            eleza __getitem__(self, key):
                ikiwa key == 'a':
                    rudisha 12
                rudisha dict.__getitem__(self, key)
        d = D()
        exec('z = a', g, d)
        self.assertEqual(d['z'], 12)

    eleza test_extended_arg(self):
        longexpr = 'x = x or ' + '-x' * 2500
        g = {}
        code = '''
eleza f(x):
    %s
    %s
    %s
    %s
    %s
    %s
    %s
    %s
    %s
    %s
    # the expressions above have no effect, x == argument
    while x:
        x -= 1
        # EXTENDED_ARG/JUMP_ABSOLUTE here
    rudisha x
''' % ((longexpr,)*10)
        exec(code, g)
        self.assertEqual(g['f'](5), 0)

    eleza test_argument_order(self):
        self.assertRaises(SyntaxError, exec, 'eleza f(a=1, b): pass')

    eleza test_float_literals(self):
        # testing bad float literals
        self.assertRaises(SyntaxError, eval, "2e")
        self.assertRaises(SyntaxError, eval, "2.0e+")
        self.assertRaises(SyntaxError, eval, "1e-")
        self.assertRaises(SyntaxError, eval, "3-4e/21")

    eleza test_indentation(self):
        # testing compile() of indented block w/o trailing newline"
        s = """
ikiwa 1:
    ikiwa 2:
        pass"""
        compile(s, "<string>", "exec")

    # This test is probably specific to CPython and may not generalize
    # to other implementations.  We are trying to ensure that when
    # the first line of code starts after 256, correct line numbers
    # in tracebacks are still produced.
    eleza test_leading_newlines(self):
        s256 = "".join(["\n"] * 256 + ["spam"])
        co = compile(s256, 'fn', 'exec')
        self.assertEqual(co.co_firstlineno, 257)
        self.assertEqual(co.co_lnotab, bytes())

    eleza test_literals_with_leading_zeroes(self):
        for arg in ["077787", "0xj", "0x.", "0e",  "090000000000000",
                    "080000000000000", "000000000000009", "000000000000008",
                    "0b42", "0BADCAFE", "0o123456789", "0b1.1", "0o4.2",
                    "0b101j2", "0o153j2", "0b100e1", "0o777e1", "0777",
                    "000777", "000000000000007"]:
            self.assertRaises(SyntaxError, eval, arg)

        self.assertEqual(eval("0xff"), 255)
        self.assertEqual(eval("0777."), 777)
        self.assertEqual(eval("0777.0"), 777)
        self.assertEqual(eval("000000000000000000000000000000000000000000000000000777e0"), 777)
        self.assertEqual(eval("0777e1"), 7770)
        self.assertEqual(eval("0e0"), 0)
        self.assertEqual(eval("0000e-012"), 0)
        self.assertEqual(eval("09.5"), 9.5)
        self.assertEqual(eval("0777j"), 777j)
        self.assertEqual(eval("000"), 0)
        self.assertEqual(eval("00j"), 0j)
        self.assertEqual(eval("00.0"), 0)
        self.assertEqual(eval("0e3"), 0)
        self.assertEqual(eval("090000000000000."), 90000000000000.)
        self.assertEqual(eval("090000000000000.0000000000000000000000"), 90000000000000.)
        self.assertEqual(eval("090000000000000e0"), 90000000000000.)
        self.assertEqual(eval("090000000000000e-0"), 90000000000000.)
        self.assertEqual(eval("090000000000000j"), 90000000000000j)
        self.assertEqual(eval("000000000000008."), 8.)
        self.assertEqual(eval("000000000000009."), 9.)
        self.assertEqual(eval("0b101010"), 42)
        self.assertEqual(eval("-0b000000000010"), -2)
        self.assertEqual(eval("0o777"), 511)
        self.assertEqual(eval("-0o0000010"), -8)

    eleza test_unary_minus(self):
        # Verify treatment of unary minus on negative numbers SF bug #660455
        ikiwa sys.maxsize == 2147483647:
            # 32-bit machine
            all_one_bits = '0xffffffff'
            self.assertEqual(eval(all_one_bits), 4294967295)
            self.assertEqual(eval("-" + all_one_bits), -4294967295)
        elikiwa sys.maxsize == 9223372036854775807:
            # 64-bit machine
            all_one_bits = '0xffffffffffffffff'
            self.assertEqual(eval(all_one_bits), 18446744073709551615)
            self.assertEqual(eval("-" + all_one_bits), -18446744073709551615)
        else:
            self.fail("How many bits *does* this machine have???")
        # Verify treatment of constant folding on -(sys.maxsize+1)
        # i.e. -2147483648 on 32 bit platforms.  Should rudisha int.
        self.assertIsInstance(eval("%s" % (-sys.maxsize - 1)), int)
        self.assertIsInstance(eval("%s" % (-sys.maxsize - 2)), int)

    ikiwa sys.maxsize == 9223372036854775807:
        eleza test_32_63_bit_values(self):
            a = +4294967296  # 1 << 32
            b = -4294967296  # 1 << 32
            c = +281474976710656  # 1 << 48
            d = -281474976710656  # 1 << 48
            e = +4611686018427387904  # 1 << 62
            f = -4611686018427387904  # 1 << 62
            g = +9223372036854775807  # 1 << 63 - 1
            h = -9223372036854775807  # 1 << 63 - 1

            for variable in self.test_32_63_bit_values.__code__.co_consts:
                ikiwa variable is not None:
                    self.assertIsInstance(variable, int)

    eleza test_sequence_unpacking_error(self):
        # Verify sequence packing/unpacking with "or".  SF bug #757818
        i,j = (1, -1) or (-1, 1)
        self.assertEqual(i, 1)
        self.assertEqual(j, -1)

    eleza test_none_assignment(self):
        stmts = [
            'None = 0',
            'None += 0',
            '__builtins__.None = 0',
            'eleza None(): pass',
            'kundi None: pass',
            '(a, None) = 0, 0',
            'for None in range(10): pass',
            'eleza f(None): pass',
            'agiza None',
            'agiza x as None',
            'kutoka x agiza None',
            'kutoka x agiza y as None'
        ]
        for stmt in stmts:
            stmt += "\n"
            self.assertRaises(SyntaxError, compile, stmt, 'tmp', 'single')
            self.assertRaises(SyntaxError, compile, stmt, 'tmp', 'exec')

    eleza test_agiza(self):
        succeed = [
            'agiza sys',
            'agiza os, sys',
            'agiza os as bar',
            'agiza os.path as bar',
            'kutoka __future__ agiza nested_scopes, generators',
            'kutoka __future__ agiza (nested_scopes,\ngenerators)',
            'kutoka __future__ agiza (nested_scopes,\ngenerators,)',
            'kutoka sys agiza stdin, stderr, stdout',
            'kutoka sys agiza (stdin, stderr,\nstdout)',
            'kutoka sys agiza (stdin, stderr,\nstdout,)',
            'kutoka sys agiza (stdin\n, stderr, stdout)',
            'kutoka sys agiza (stdin\n, stderr, stdout,)',
            'kutoka sys agiza stdin as si, stdout as so, stderr as se',
            'kutoka sys agiza (stdin as si, stdout as so, stderr as se)',
            'kutoka sys agiza (stdin as si, stdout as so, stderr as se,)',
            ]
        fail = [
            'agiza (os, sys)',
            'agiza (os), (sys)',
            'agiza ((os), (sys))',
            'agiza (sys',
            'agiza sys)',
            'agiza (os,)',
            'agiza os As bar',
            'agiza os.path a bar',
            'kutoka sys agiza stdin As stdout',
            'kutoka sys agiza stdin a stdout',
            'kutoka (sys) agiza stdin',
            'kutoka __future__ agiza (nested_scopes',
            'kutoka __future__ agiza nested_scopes)',
            'kutoka __future__ agiza nested_scopes,\ngenerators',
            'kutoka sys agiza (stdin',
            'kutoka sys agiza stdin)',
            'kutoka sys agiza stdin, stdout,\nstderr',
            'kutoka sys agiza stdin si',
            'kutoka sys agiza stdin,',
            'kutoka sys agiza (*)',
            'kutoka sys agiza (stdin,, stdout, stderr)',
            'kutoka sys agiza (stdin, stdout),',
            ]
        for stmt in succeed:
            compile(stmt, 'tmp', 'exec')
        for stmt in fail:
            self.assertRaises(SyntaxError, compile, stmt, 'tmp', 'exec')

    eleza test_for_distinct_code_objects(self):
        # SF bug 1048870
        eleza f():
            f1 = lambda x=1: x
            f2 = lambda x=2: x
            rudisha f1, f2
        f1, f2 = f()
        self.assertNotEqual(id(f1.__code__), id(f2.__code__))

    eleza test_lambda_doc(self):
        l = lambda: "foo"
        self.assertIsNone(l.__doc__)

    eleza test_encoding(self):
        code = b'# -*- coding: badencoding -*-\npass\n'
        self.assertRaises(SyntaxError, compile, code, 'tmp', 'exec')
        code = '# -*- coding: badencoding -*-\n"\xc2\xa4"\n'
        compile(code, 'tmp', 'exec')
        self.assertEqual(eval(code), '\xc2\xa4')
        code = '"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xc2\xa4')
        code = b'"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xa4')
        code = b'# -*- coding: latin1 -*-\n"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xc2\xa4')
        code = b'# -*- coding: utf-8 -*-\n"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xa4')
        code = b'# -*- coding: iso8859-15 -*-\n"\xc2\xa4"\n'
        self.assertEqual(eval(code), '\xc2\u20ac')
        code = '"""\\\n# -*- coding: iso8859-15 -*-\n\xc2\xa4"""\n'
        self.assertEqual(eval(code), '# -*- coding: iso8859-15 -*-\n\xc2\xa4')
        code = b'"""\\\n# -*- coding: iso8859-15 -*-\n\xc2\xa4"""\n'
        self.assertEqual(eval(code), '# -*- coding: iso8859-15 -*-\n\xa4')

    eleza test_subscripts(self):
        # SF bug 1448804
        # Class to make testing subscript results easy
        kundi str_map(object):
            eleza __init__(self):
                self.data = {}
            eleza __getitem__(self, key):
                rudisha self.data[str(key)]
            eleza __setitem__(self, key, value):
                self.data[str(key)] = value
            eleza __delitem__(self, key):
                del self.data[str(key)]
            eleza __contains__(self, key):
                rudisha str(key) in self.data
        d = str_map()
        # Index
        d[1] = 1
        self.assertEqual(d[1], 1)
        d[1] += 1
        self.assertEqual(d[1], 2)
        del d[1]
        self.assertNotIn(1, d)
        # Tuple of indices
        d[1, 1] = 1
        self.assertEqual(d[1, 1], 1)
        d[1, 1] += 1
        self.assertEqual(d[1, 1], 2)
        del d[1, 1]
        self.assertNotIn((1, 1), d)
        # Simple slice
        d[1:2] = 1
        self.assertEqual(d[1:2], 1)
        d[1:2] += 1
        self.assertEqual(d[1:2], 2)
        del d[1:2]
        self.assertNotIn(slice(1, 2), d)
        # Tuple of simple slices
        d[1:2, 1:2] = 1
        self.assertEqual(d[1:2, 1:2], 1)
        d[1:2, 1:2] += 1
        self.assertEqual(d[1:2, 1:2], 2)
        del d[1:2, 1:2]
        self.assertNotIn((slice(1, 2), slice(1, 2)), d)
        # Extended slice
        d[1:2:3] = 1
        self.assertEqual(d[1:2:3], 1)
        d[1:2:3] += 1
        self.assertEqual(d[1:2:3], 2)
        del d[1:2:3]
        self.assertNotIn(slice(1, 2, 3), d)
        # Tuple of extended slices
        d[1:2:3, 1:2:3] = 1
        self.assertEqual(d[1:2:3, 1:2:3], 1)
        d[1:2:3, 1:2:3] += 1
        self.assertEqual(d[1:2:3, 1:2:3], 2)
        del d[1:2:3, 1:2:3]
        self.assertNotIn((slice(1, 2, 3), slice(1, 2, 3)), d)
        # Ellipsis
        d[...] = 1
        self.assertEqual(d[...], 1)
        d[...] += 1
        self.assertEqual(d[...], 2)
        del d[...]
        self.assertNotIn(Ellipsis, d)
        # Tuple of Ellipses
        d[..., ...] = 1
        self.assertEqual(d[..., ...], 1)
        d[..., ...] += 1
        self.assertEqual(d[..., ...], 2)
        del d[..., ...]
        self.assertNotIn((Ellipsis, Ellipsis), d)

    eleza test_annotation_limit(self):
        # more than 255 annotations, should compile ok
        s = "eleza f(%s): pass"
        s %= ', '.join('a%d:%d' % (i,i) for i in range(300))
        compile(s, '?', 'exec')

    eleza test_mangling(self):
        kundi A:
            eleza f():
                __mangled = 1
                __not_mangled__ = 2
                agiza __mangled_mod
                agiza __package__.module

        self.assertIn("_A__mangled", A.f.__code__.co_varnames)
        self.assertIn("__not_mangled__", A.f.__code__.co_varnames)
        self.assertIn("_A__mangled_mod", A.f.__code__.co_varnames)
        self.assertIn("__package__", A.f.__code__.co_varnames)

    eleza test_compile_ast(self):
        fname = __file__
        ikiwa fname.lower().endswith('pyc'):
            fname = fname[:-1]
        with open(fname, 'r') as f:
            fcontents = f.read()
        sample_code = [
            ['<assign>', 'x = 5'],
            ['<ifblock>', """ikiwa True:\n    pass\n"""],
            ['<forblock>', """for n in [1, 2, 3]:\n    andika(n)\n"""],
            ['<deffunc>', """eleza foo():\n    pass\nfoo()\n"""],
            [fname, fcontents],
        ]

        for fname, code in sample_code:
            co1 = compile(code, '%s1' % fname, 'exec')
            ast = compile(code, '%s2' % fname, 'exec', _ast.PyCF_ONLY_AST)
            self.assertTrue(type(ast) == _ast.Module)
            co2 = compile(ast, '%s3' % fname, 'exec')
            self.assertEqual(co1, co2)
            # the code object's filename comes kutoka the second compilation step
            self.assertEqual(co2.co_filename, '%s3' % fname)

        # raise exception when node type doesn't match with compile mode
        co1 = compile('andika(1)', '<string>', 'exec', _ast.PyCF_ONLY_AST)
        self.assertRaises(TypeError, compile, co1, '<ast>', 'eval')

        # raise exception when node type is no start node
        self.assertRaises(TypeError, compile, _ast.If(), '<ast>', 'exec')

        # raise exception when node has invalid children
        ast = _ast.Module()
        ast.body = [_ast.BoolOp()]
        self.assertRaises(TypeError, compile, ast, '<ast>', 'exec')

    eleza test_dict_evaluation_order(self):
        i = 0

        eleza f():
            nonlocal i
            i += 1
            rudisha i

        d = {f(): f(), f(): f()}
        self.assertEqual(d, {1: 2, 3: 4})

    eleza test_compile_filename(self):
        for filename in 'file.py', b'file.py':
            code = compile('pass', filename, 'exec')
            self.assertEqual(code.co_filename, 'file.py')
        for filename in bytearray(b'file.py'), memoryview(b'file.py'):
            with self.assertWarns(DeprecationWarning):
                code = compile('pass', filename, 'exec')
            self.assertEqual(code.co_filename, 'file.py')
        self.assertRaises(TypeError, compile, 'pass', list(b'file.py'), 'exec')

    @support.cpython_only
    eleza test_same_filename_used(self):
        s = """eleza f(): pass\neleza g(): pass"""
        c = compile(s, "myfile", "exec")
        for obj in c.co_consts:
            ikiwa isinstance(obj, types.CodeType):
                self.assertIs(obj.co_filename, c.co_filename)

    eleza test_single_statement(self):
        self.compile_single("1 + 2")
        self.compile_single("\n1 + 2")
        self.compile_single("1 + 2\n")
        self.compile_single("1 + 2\n\n")
        self.compile_single("1 + 2\t\t\n")
        self.compile_single("1 + 2\t\t\n        ")
        self.compile_single("1 + 2 # one plus two")
        self.compile_single("1; 2")
        self.compile_single("agiza sys; sys")
        self.compile_single("eleza f():\n   pass")
        self.compile_single("while False:\n   pass")
        self.compile_single("ikiwa x:\n   f(x)")
        self.compile_single("ikiwa x:\n   f(x)\nelse:\n   g(x)")
        self.compile_single("kundi T:\n   pass")

    eleza test_bad_single_statement(self):
        self.assertInvalidSingle('1\n2')
        self.assertInvalidSingle('eleza f(): pass')
        self.assertInvalidSingle('a = 13\nb = 187')
        self.assertInvalidSingle('del x\ndel y')
        self.assertInvalidSingle('f()\ng()')
        self.assertInvalidSingle('f()\n# blah\nblah()')
        self.assertInvalidSingle('f()\nxy # blah\nblah()')
        self.assertInvalidSingle('x = 5 # comment\nx = 6\n')

    eleza test_particularly_evil_undecodable(self):
        # Issue 24022
        src = b'0000\x00\n00000000000\n\x00\n\x9e\n'
        with tempfile.TemporaryDirectory() as tmpd:
            fn = os.path.join(tmpd, "bad.py")
            with open(fn, "wb") as fp:
                fp.write(src)
            res = script_helper.run_python_until_end(fn)[0]
        self.assertIn(b"Non-UTF-8", res.err)

    eleza test_yet_more_evil_still_undecodable(self):
        # Issue #25388
        src = b"#\x00\n#\xfd\n"
        with tempfile.TemporaryDirectory() as tmpd:
            fn = os.path.join(tmpd, "bad.py")
            with open(fn, "wb") as fp:
                fp.write(src)
            res = script_helper.run_python_until_end(fn)[0]
        self.assertIn(b"Non-UTF-8", res.err)

    @support.cpython_only
    eleza test_compiler_recursion_limit(self):
        # Expected limit is sys.getrecursionlimit() * the scaling factor
        # in symtable.c (currently 3)
        # We expect to fail *at* that limit, because we use up some of
        # the stack depth limit in the test suite code
        # So we check the expected limit and 75% of that
        # XXX (ncoghlan): duplicating the scaling factor here is a little
        # ugly. Perhaps it should be exposed somewhere...
        fail_depth = sys.getrecursionlimit() * 3
        success_depth = int(fail_depth * 0.75)

        eleza check_limit(prefix, repeated):
            expect_ok = prefix + repeated * success_depth
            self.compile_single(expect_ok)
            broken = prefix + repeated * fail_depth
            details = "Compiling ({!r} + {!r} * {})".format(
                         prefix, repeated, fail_depth)
            with self.assertRaises(RecursionError, msg=details):
                self.compile_single(broken)

        check_limit("a", "()")
        check_limit("a", ".b")
        check_limit("a", "[0]")
        check_limit("a", "*a")

    eleza test_null_terminated(self):
        # The source code is null-terminated internally, but bytes-like
        # objects are accepted, which could be not terminated.
        with self.assertRaisesRegex(ValueError, "cannot contain null"):
            compile("123\x00", "<dummy>", "eval")
        with self.assertRaisesRegex(ValueError, "cannot contain null"):
            compile(memoryview(b"123\x00"), "<dummy>", "eval")
        code = compile(memoryview(b"123\x00")[1:-1], "<dummy>", "eval")
        self.assertEqual(eval(code), 23)
        code = compile(memoryview(b"1234")[1:-1], "<dummy>", "eval")
        self.assertEqual(eval(code), 23)
        code = compile(memoryview(b"$23$")[1:-1], "<dummy>", "eval")
        self.assertEqual(eval(code), 23)

        # Also test when eval() and exec() do the compilation step
        self.assertEqual(eval(memoryview(b"1234")[1:-1]), 23)
        namespace = dict()
        exec(memoryview(b"ax = 123")[1:-1], namespace)
        self.assertEqual(namespace['x'], 12)

    eleza check_constant(self, func, expected):
        for const in func.__code__.co_consts:
            ikiwa repr(const) == repr(expected):
                break
        else:
            self.fail("unable to find constant %r in %r"
                      % (expected, func.__code__.co_consts))

    # Merging equal constants is not a strict requirement for the Python
    # semantics, it's a more an implementation detail.
    @support.cpython_only
    eleza test_merge_constants(self):
        # Issue #25843: compile() must merge constants which are equal
        # and have the same type.

        eleza check_same_constant(const):
            ns = {}
            code = "f1, f2 = lambda: %r, lambda: %r" % (const, const)
            exec(code, ns)
            f1 = ns['f1']
            f2 = ns['f2']
            self.assertIs(f1.__code__, f2.__code__)
            self.check_constant(f1, const)
            self.assertEqual(repr(f1()), repr(const))

        check_same_constant(None)
        check_same_constant(0)
        check_same_constant(0.0)
        check_same_constant(b'abc')
        check_same_constant('abc')

        # Note: "lambda: ..." emits "LOAD_CONST Ellipsis",
        # whereas "lambda: Ellipsis" emits "LOAD_GLOBAL Ellipsis"
        f1, f2 = lambda: ..., lambda: ...
        self.assertIs(f1.__code__, f2.__code__)
        self.check_constant(f1, Ellipsis)
        self.assertEqual(repr(f1()), repr(Ellipsis))

        # Merge constants in tuple or frozenset
        f1, f2 = lambda: "not a name", lambda: ("not a name",)
        f3 = lambda x: x in {("not a name",)}
        self.assertIs(f1.__code__.co_consts[1],
                      f2.__code__.co_consts[1][0])
        self.assertIs(next(iter(f3.__code__.co_consts[1])),
                      f2.__code__.co_consts[1])

        # {0} is converted to a constant frozenset({0}) by the peephole
        # optimizer
        f1, f2 = lambda x: x in {0}, lambda x: x in {0}
        self.assertIs(f1.__code__, f2.__code__)
        self.check_constant(f1, frozenset({0}))
        self.assertTrue(f1(0))

    # This is a regression test for a CPython specific peephole optimizer
    # implementation bug present in a few releases.  It's assertion verifies
    # that peephole optimization was actually done though that isn't an
    # indication of the bugs presence or not (crashing is).
    @support.cpython_only
    eleza test_peephole_opt_unreachable_code_array_access_in_bounds(self):
        """Regression test for issue35193 when run under clang msan."""
        eleza unused_code_at_end():
            rudisha 3
            raise RuntimeError("unreachable")
        # The above function definition will trigger the out of bounds
        # bug in the peephole optimizer as it scans opcodes past the
        # RETURN_VALUE opcode.  This does not always crash an interpreter.
        # When you build with the clang memory sanitizer it reliably aborts.
        self.assertEqual(
            'RETURN_VALUE',
            list(dis.get_instructions(unused_code_at_end))[-1].opname)

    eleza test_dont_merge_constants(self):
        # Issue #25843: compile() must not merge constants which are equal
        # but have a different type.

        eleza check_different_constants(const1, const2):
            ns = {}
            exec("f1, f2 = lambda: %r, lambda: %r" % (const1, const2), ns)
            f1 = ns['f1']
            f2 = ns['f2']
            self.assertIsNot(f1.__code__, f2.__code__)
            self.assertNotEqual(f1.__code__, f2.__code__)
            self.check_constant(f1, const1)
            self.check_constant(f2, const2)
            self.assertEqual(repr(f1()), repr(const1))
            self.assertEqual(repr(f2()), repr(const2))

        check_different_constants(0, 0.0)
        check_different_constants(+0.0, -0.0)
        check_different_constants((0,), (0.0,))
        check_different_constants('a', b'a')
        check_different_constants(('a',), (b'a',))

        # check_different_constants() cannot be used because repr(-0j) is
        # '(-0-0j)', but when '(-0-0j)' is evaluated to 0j: we loose the sign.
        f1, f2 = lambda: +0.0j, lambda: -0.0j
        self.assertIsNot(f1.__code__, f2.__code__)
        self.check_constant(f1, +0.0j)
        self.check_constant(f2, -0.0j)
        self.assertEqual(repr(f1()), repr(+0.0j))
        self.assertEqual(repr(f2()), repr(-0.0j))

        # {0} is converted to a constant frozenset({0}) by the peephole
        # optimizer
        f1, f2 = lambda x: x in {0}, lambda x: x in {0.0}
        self.assertIsNot(f1.__code__, f2.__code__)
        self.check_constant(f1, frozenset({0}))
        self.check_constant(f2, frozenset({0.0}))
        self.assertTrue(f1(0))
        self.assertTrue(f2(0.0))

    eleza test_path_like_objects(self):
        # An implicit test for PyUnicode_FSDecoder().
        compile("42", FakePath("test_compile_pathlike"), "single")

    eleza test_stack_overflow(self):
        # bpo-31113: Stack overflow when compile a long sequence of
        # complex statements.
        compile("ikiwa a: b\n" * 200000, "<dummy>", "exec")

    # Multiple users rely on the fact that CPython does not generate
    # bytecode for dead code blocks. See bpo-37500 for more context.
    @support.cpython_only
    eleza test_dead_blocks_do_not_generate_bytecode(self):
        eleza unused_block_if():
            ikiwa 0:
                rudisha 42

        eleza unused_block_while():
            while 0:
                rudisha 42

        eleza unused_block_if_else():
            ikiwa 1:
                rudisha None
            else:
                rudisha 42

        eleza unused_block_while_else():
            while 1:
                rudisha None
            else:
                rudisha 42

        funcs = [unused_block_if, unused_block_while,
                 unused_block_if_else, unused_block_while_else]

        for func in funcs:
            opcodes = list(dis.get_instructions(func))
            self.assertEqual(2, len(opcodes))
            self.assertEqual('LOAD_CONST', opcodes[0].opname)
            self.assertEqual(None, opcodes[0].argval)
            self.assertEqual('RETURN_VALUE', opcodes[1].opname)


kundi TestExpressionStackSize(unittest.TestCase):
    # These tests check that the computed stack size for a code object
    # stays within reasonable bounds (see issue #21523 for an example
    # dysfunction).
    N = 100

    eleza check_stack_size(self, code):
        # To assert that the alleged stack size is not O(N), we
        # check that it is smaller than log(N).
        ikiwa isinstance(code, str):
            code = compile(code, "<foo>", "single")
        max_size = math.ceil(math.log(len(code.co_code)))
        self.assertLessEqual(code.co_stacksize, max_size)

    eleza test_and(self):
        self.check_stack_size("x and " * self.N + "x")

    eleza test_or(self):
        self.check_stack_size("x or " * self.N + "x")

    eleza test_and_or(self):
        self.check_stack_size("x and x or " * self.N + "x")

    eleza test_chained_comparison(self):
        self.check_stack_size("x < " * self.N + "x")

    eleza test_if_else(self):
        self.check_stack_size("x ikiwa x else " * self.N + "x")

    eleza test_binop(self):
        self.check_stack_size("x + " * self.N + "x")

    eleza test_func_and(self):
        code = "eleza f(x):\n"
        code += "   x and x\n" * self.N
        self.check_stack_size(code)


kundi TestStackSizeStability(unittest.TestCase):
    # Check that repeating certain snippets doesn't increase the stack size
    # beyond what a single snippet requires.

    eleza check_stack_size(self, snippet, async_=False):
        eleza compile_snippet(i):
            ns = {}
            script = """eleza func():\n""" + i * snippet
            ikiwa async_:
                script = "async " + script
            code = compile(script, "<script>", "exec")
            exec(code, ns, ns)
            rudisha ns['func'].__code__

        sizes = [compile_snippet(i).co_stacksize for i in range(2, 5)]
        ikiwa len(set(sizes)) != 1:
            agiza dis, io
            out = io.StringIO()
            dis.dis(compile_snippet(1), file=out)
            self.fail("stack sizes diverge with # of consecutive snippets: "
                      "%s\n%s\n%s" % (sizes, snippet, out.getvalue()))

    eleza test_if(self):
        snippet = """
            ikiwa x:
                a
            """
        self.check_stack_size(snippet)

    eleza test_if_else(self):
        snippet = """
            ikiwa x:
                a
            elikiwa y:
                b
            else:
                c
            """
        self.check_stack_size(snippet)

    eleza test_try_except_bare(self):
        snippet = """
            try:
                a
            except:
                b
            """
        self.check_stack_size(snippet)

    eleza test_try_except_qualified(self):
        snippet = """
            try:
                a
            except ImportError:
                b
            except:
                c
            else:
                d
            """
        self.check_stack_size(snippet)

    eleza test_try_except_as(self):
        snippet = """
            try:
                a
            except ImportError as e:
                b
            except:
                c
            else:
                d
            """
        self.check_stack_size(snippet)

    eleza test_try_finally(self):
        snippet = """
                try:
                    a
                finally:
                    b
            """
        self.check_stack_size(snippet)

    eleza test_with(self):
        snippet = """
            with x as y:
                a
            """
        self.check_stack_size(snippet)

    eleza test_while_else(self):
        snippet = """
            while x:
                a
            else:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for(self):
        snippet = """
            for x in y:
                a
            """
        self.check_stack_size(snippet)

    eleza test_for_else(self):
        snippet = """
            for x in y:
                a
            else:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_break_continue(self):
        snippet = """
            for x in y:
                ikiwa z:
                    break
                elikiwa u:
                    continue
                else:
                    a
            else:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_break_continue_inside_try_finally_block(self):
        snippet = """
            for x in y:
                try:
                    ikiwa z:
                        break
                    elikiwa u:
                        continue
                    else:
                        a
                finally:
                    f
            else:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_break_continue_inside_finally_block(self):
        snippet = """
            for x in y:
                try:
                    t
                finally:
                    ikiwa z:
                        break
                    elikiwa u:
                        continue
                    else:
                        a
            else:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_break_continue_inside_except_block(self):
        snippet = """
            for x in y:
                try:
                    t
                except:
                    ikiwa z:
                        break
                    elikiwa u:
                        continue
                    else:
                        a
            else:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_break_continue_inside_with_block(self):
        snippet = """
            for x in y:
                with c:
                    ikiwa z:
                        break
                    elikiwa u:
                        continue
                    else:
                        a
            else:
                b
            """
        self.check_stack_size(snippet)

    eleza test_return_inside_try_finally_block(self):
        snippet = """
            try:
                ikiwa z:
                    return
                else:
                    a
            finally:
                f
            """
        self.check_stack_size(snippet)

    eleza test_return_inside_finally_block(self):
        snippet = """
            try:
                t
            finally:
                ikiwa z:
                    return
                else:
                    a
            """
        self.check_stack_size(snippet)

    eleza test_return_inside_except_block(self):
        snippet = """
            try:
                t
            except:
                ikiwa z:
                    return
                else:
                    a
            """
        self.check_stack_size(snippet)

    eleza test_return_inside_with_block(self):
        snippet = """
            with c:
                ikiwa z:
                    return
                else:
                    a
            """
        self.check_stack_size(snippet)

    eleza test_async_with(self):
        snippet = """
            async with x as y:
                a
            """
        self.check_stack_size(snippet, async_=True)

    eleza test_async_for(self):
        snippet = """
            async for x in y:
                a
            """
        self.check_stack_size(snippet, async_=True)

    eleza test_async_for_else(self):
        snippet = """
            async for x in y:
                a
            else:
                b
            """
        self.check_stack_size(snippet, async_=True)

    eleza test_for_break_continue_inside_async_with_block(self):
        snippet = """
            for x in y:
                async with c:
                    ikiwa z:
                        break
                    elikiwa u:
                        continue
                    else:
                        a
            else:
                b
            """
        self.check_stack_size(snippet, async_=True)

    eleza test_return_inside_async_with_block(self):
        snippet = """
            async with c:
                ikiwa z:
                    return
                else:
                    a
            """
        self.check_stack_size(snippet, async_=True)


ikiwa __name__ == "__main__":
    unittest.main()
