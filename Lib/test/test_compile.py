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
        compile("hi\r\nstuff\r\neleza f():\n    pita\r", "<test>", "exec")
        compile("this_is\rreally_old_mac\releza f():\n    pita", "<test>", "exec")

    eleza test_debug_assignment(self):
        # catch assignments to __debug__
        self.assertRaises(SyntaxError, compile, '__debug__ = 1', '?', 'single')
        agiza builtins
        prev = builtins.__debug__
        setattr(builtins, '__debug__', 'sure')
        self.assertEqual(__debug__, prev)
        setattr(builtins, '__debug__', prev)

    eleza test_argument_handling(self):
        # detect duplicate positional na keyword arguments
        self.assertRaises(SyntaxError, eval, 'lambda a,a:0')
        self.assertRaises(SyntaxError, eval, 'lambda a,a=1:0')
        self.assertRaises(SyntaxError, eval, 'lambda a=1,a=1:0')
        self.assertRaises(SyntaxError, exec, 'eleza f(a, a): pita')
        self.assertRaises(SyntaxError, exec, 'eleza f(a = 0, a = 1): pita')
        self.assertRaises(SyntaxError, exec, 'eleza f(a): global a; a = 1')

    eleza test_syntax_error(self):
        self.assertRaises(SyntaxError, compile, "1+*3", "filename", "exec")

    eleza test_none_keyword_arg(self):
        self.assertRaises(SyntaxError, compile, "f(Tupu=1)", "<string>", "exec")

    eleza test_duplicate_global_local(self):
        self.assertRaises(SyntaxError, exec, 'eleza f(a): global a; a = 1')

    eleza test_exec_with_general_mapping_for_locals(self):

        kundi M:
            "Test mapping interface versus possible calls kutoka eval()."
            eleza __getitem__(self, key):
                ikiwa key == 'a':
                    rudisha 12
                ashiria KeyError
            eleza __setitem__(self, key, value):
                self.results = (key, value)
            eleza keys(self):
                rudisha list('xyz')

        m = M()
        g = globals()
        exec('z = a', g, m)
        self.assertEqual(m.results, ('z', 12))
        jaribu:
            exec('z = b', g, m)
        tatizo NameError:
            pita
        isipokua:
            self.fail('Did sio detect a KeyError')
        exec('z = dir()', g, m)
        self.assertEqual(m.results, ('z', list('xyz')))
        exec('z = globals()', g, m)
        self.assertEqual(m.results, ('z', g))
        exec('z = locals()', g, m)
        self.assertEqual(m.results, ('z', m))
        self.assertRaises(TypeError, exec, 'z = b', m)

        kundi A:
            "Non-mapping"
            pita
        m = A()
        self.assertRaises(TypeError, exec, 'z = a', g, m)

        # Verify that dict subclasses work kama well
        kundi D(dict):
            eleza __getitem__(self, key):
                ikiwa key == 'a':
                    rudisha 12
                rudisha dict.__getitem__(self, key)
        d = D()
        exec('z = a', g, d)
        self.assertEqual(d['z'], 12)

    eleza test_extended_arg(self):
        longexpr = 'x = x ama ' + '-x' * 2500
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
    wakati x:
        x -= 1
        # EXTENDED_ARG/JUMP_ABSOLUTE here
    rudisha x
''' % ((longexpr,)*10)
        exec(code, g)
        self.assertEqual(g['f'](5), 0)

    eleza test_argument_order(self):
        self.assertRaises(SyntaxError, exec, 'eleza f(a=1, b): pita')

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
        pita"""
        compile(s, "<string>", "exec")

    # This test ni probably specific to CPython na may sio generalize
    # to other implementations.  We are trying to ensure that when
    # the first line of code starts after 256, correct line numbers
    # kwenye tracebacks are still produced.
    eleza test_leading_newlines(self):
        s256 = "".join(["\n"] * 256 + ["spam"])
        co = compile(s256, 'fn', 'exec')
        self.assertEqual(co.co_firstlineno, 257)
        self.assertEqual(co.co_lnotab, bytes())

    eleza test_literals_with_leading_zeroes(self):
        kila arg kwenye ["077787", "0xj", "0x.", "0e",  "090000000000000",
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
        lasivyo sys.maxsize == 9223372036854775807:
            # 64-bit machine
            all_one_bits = '0xffffffffffffffff'
            self.assertEqual(eval(all_one_bits), 18446744073709551615)
            self.assertEqual(eval("-" + all_one_bits), -18446744073709551615)
        isipokua:
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

            kila variable kwenye self.test_32_63_bit_values.__code__.co_consts:
                ikiwa variable ni sio Tupu:
                    self.assertIsInstance(variable, int)

    eleza test_sequence_unpacking_error(self):
        # Verify sequence packing/unpacking ukijumuisha "or".  SF bug #757818
        i,j = (1, -1) ama (-1, 1)
        self.assertEqual(i, 1)
        self.assertEqual(j, -1)

    eleza test_none_assignment(self):
        stmts = [
            'Tupu = 0',
            'Tupu += 0',
            '__builtins__.Tupu = 0',
            'eleza Tupu(): pita',
            'kundi Tupu: pita',
            '(a, Tupu) = 0, 0',
            'kila Tupu kwenye range(10): pita',
            'eleza f(Tupu): pita',
            'agiza Tupu',
            'agiza x kama Tupu',
            'kutoka x agiza Tupu',
            'kutoka x agiza y kama Tupu'
        ]
        kila stmt kwenye stmts:
            stmt += "\n"
            self.assertRaises(SyntaxError, compile, stmt, 'tmp', 'single')
            self.assertRaises(SyntaxError, compile, stmt, 'tmp', 'exec')

    eleza test_import(self):
        succeed = [
            'agiza sys',
            'agiza os, sys',
            'agiza os kama bar',
            'agiza os.path kama bar',
            'kutoka __future__ agiza nested_scopes, generators',
            'kutoka __future__ agiza (nested_scopes,\ngenerators)',
            'kutoka __future__ agiza (nested_scopes,\ngenerators,)',
            'kutoka sys agiza stdin, stderr, stdout',
            'kutoka sys agiza (stdin, stderr,\nstdout)',
            'kutoka sys agiza (stdin, stderr,\nstdout,)',
            'kutoka sys agiza (stdin\n, stderr, stdout)',
            'kutoka sys agiza (stdin\n, stderr, stdout,)',
            'kutoka sys agiza stdin kama si, stdout kama so, stderr kama se',
            'kutoka sys agiza (stdin kama si, stdout kama so, stderr kama se)',
            'kutoka sys agiza (stdin kama si, stdout kama so, stderr kama se,)',
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
        kila stmt kwenye succeed:
            compile(stmt, 'tmp', 'exec')
        kila stmt kwenye fail:
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
        self.assertIsTupu(l.__doc__)

    eleza test_encoding(self):
        code = b'# -*- coding: badencoding -*-\npita\n'
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
                toa self.data[str(key)]
            eleza __contains__(self, key):
                rudisha str(key) kwenye self.data
        d = str_map()
        # Index
        d[1] = 1
        self.assertEqual(d[1], 1)
        d[1] += 1
        self.assertEqual(d[1], 2)
        toa d[1]
        self.assertNotIn(1, d)
        # Tuple of indices
        d[1, 1] = 1
        self.assertEqual(d[1, 1], 1)
        d[1, 1] += 1
        self.assertEqual(d[1, 1], 2)
        toa d[1, 1]
        self.assertNotIn((1, 1), d)
        # Simple slice
        d[1:2] = 1
        self.assertEqual(d[1:2], 1)
        d[1:2] += 1
        self.assertEqual(d[1:2], 2)
        toa d[1:2]
        self.assertNotIn(slice(1, 2), d)
        # Tuple of simple slices
        d[1:2, 1:2] = 1
        self.assertEqual(d[1:2, 1:2], 1)
        d[1:2, 1:2] += 1
        self.assertEqual(d[1:2, 1:2], 2)
        toa d[1:2, 1:2]
        self.assertNotIn((slice(1, 2), slice(1, 2)), d)
        # Extended slice
        d[1:2:3] = 1
        self.assertEqual(d[1:2:3], 1)
        d[1:2:3] += 1
        self.assertEqual(d[1:2:3], 2)
        toa d[1:2:3]
        self.assertNotIn(slice(1, 2, 3), d)
        # Tuple of extended slices
        d[1:2:3, 1:2:3] = 1
        self.assertEqual(d[1:2:3, 1:2:3], 1)
        d[1:2:3, 1:2:3] += 1
        self.assertEqual(d[1:2:3, 1:2:3], 2)
        toa d[1:2:3, 1:2:3]
        self.assertNotIn((slice(1, 2, 3), slice(1, 2, 3)), d)
        # Ellipsis
        d[...] = 1
        self.assertEqual(d[...], 1)
        d[...] += 1
        self.assertEqual(d[...], 2)
        toa d[...]
        self.assertNotIn(Ellipsis, d)
        # Tuple of Ellipses
        d[..., ...] = 1
        self.assertEqual(d[..., ...], 1)
        d[..., ...] += 1
        self.assertEqual(d[..., ...], 2)
        toa d[..., ...]
        self.assertNotIn((Ellipsis, Ellipsis), d)

    eleza test_annotation_limit(self):
        # more than 255 annotations, should compile ok
        s = "eleza f(%s): pita"
        s %= ', '.join('a%d:%d' % (i,i) kila i kwenye range(300))
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
        ukijumuisha open(fname, 'r') kama f:
            fcontents = f.read()
        sample_code = [
            ['<assign>', 'x = 5'],
            ['<ifblock>', """ikiwa Kweli:\n    pita\n"""],
            ['<forblock>', """kila n kwenye [1, 2, 3]:\n    andika(n)\n"""],
            ['<deffunc>', """eleza foo():\n    pita\nfoo()\n"""],
            [fname, fcontents],
        ]

        kila fname, code kwenye sample_code:
            co1 = compile(code, '%s1' % fname, 'exec')
            ast = compile(code, '%s2' % fname, 'exec', _ast.PyCF_ONLY_AST)
            self.assertKweli(type(ast) == _ast.Module)
            co2 = compile(ast, '%s3' % fname, 'exec')
            self.assertEqual(co1, co2)
            # the code object's filename comes kutoka the second compilation step
            self.assertEqual(co2.co_filename, '%s3' % fname)

        # ashiria exception when node type doesn't match ukijumuisha compile mode
        co1 = compile('andika(1)', '<string>', 'exec', _ast.PyCF_ONLY_AST)
        self.assertRaises(TypeError, compile, co1, '<ast>', 'eval')

        # ashiria exception when node type ni no start node
        self.assertRaises(TypeError, compile, _ast.If(), '<ast>', 'exec')

        # ashiria exception when node has invalid children
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
        kila filename kwenye 'file.py', b'file.py':
            code = compile('pita', filename, 'exec')
            self.assertEqual(code.co_filename, 'file.py')
        kila filename kwenye bytearray(b'file.py'), memoryview(b'file.py'):
            ukijumuisha self.assertWarns(DeprecationWarning):
                code = compile('pita', filename, 'exec')
            self.assertEqual(code.co_filename, 'file.py')
        self.assertRaises(TypeError, compile, 'pita', list(b'file.py'), 'exec')

    @support.cpython_only
    eleza test_same_filename_used(self):
        s = """eleza f(): pita\neleza g(): pita"""
        c = compile(s, "myfile", "exec")
        kila obj kwenye c.co_consts:
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
        self.compile_single("eleza f():\n   pita")
        self.compile_single("wakati Uongo:\n   pita")
        self.compile_single("ikiwa x:\n   f(x)")
        self.compile_single("ikiwa x:\n   f(x)\nisipokua:\n   g(x)")
        self.compile_single("kundi T:\n   pita")

    eleza test_bad_single_statement(self):
        self.assertInvalidSingle('1\n2')
        self.assertInvalidSingle('eleza f(): pita')
        self.assertInvalidSingle('a = 13\nb = 187')
        self.assertInvalidSingle('toa x\ntoa y')
        self.assertInvalidSingle('f()\ng()')
        self.assertInvalidSingle('f()\n# blah\nblah()')
        self.assertInvalidSingle('f()\nxy # blah\nblah()')
        self.assertInvalidSingle('x = 5 # comment\nx = 6\n')

    eleza test_particularly_evil_undecodable(self):
        # Issue 24022
        src = b'0000\x00\n00000000000\n\x00\n\x9e\n'
        ukijumuisha tempfile.TemporaryDirectory() kama tmpd:
            fn = os.path.join(tmpd, "bad.py")
            ukijumuisha open(fn, "wb") kama fp:
                fp.write(src)
            res = script_helper.run_python_until_end(fn)[0]
        self.assertIn(b"Non-UTF-8", res.err)

    eleza test_yet_more_evil_still_undecodable(self):
        # Issue #25388
        src = b"#\x00\n#\xfd\n"
        ukijumuisha tempfile.TemporaryDirectory() kama tmpd:
            fn = os.path.join(tmpd, "bad.py")
            ukijumuisha open(fn, "wb") kama fp:
                fp.write(src)
            res = script_helper.run_python_until_end(fn)[0]
        self.assertIn(b"Non-UTF-8", res.err)

    @support.cpython_only
    eleza test_compiler_recursion_limit(self):
        # Expected limit ni sys.getrecursionlimit() * the scaling factor
        # kwenye symtable.c (currently 3)
        # We expect to fail *at* that limit, because we use up some of
        # the stack depth limit kwenye the test suite code
        # So we check the expected limit na 75% of that
        # XXX (ncoghlan): duplicating the scaling factor here ni a little
        # ugly. Perhaps it should be exposed somewhere...
        fail_depth = sys.getrecursionlimit() * 3
        success_depth = int(fail_depth * 0.75)

        eleza check_limit(prefix, repeated):
            expect_ok = prefix + repeated * success_depth
            self.compile_single(expect_ok)
            broken = prefix + repeated * fail_depth
            details = "Compiling ({!r} + {!r} * {})".format(
                         prefix, repeated, fail_depth)
            ukijumuisha self.assertRaises(RecursionError, msg=details):
                self.compile_single(broken)

        check_limit("a", "()")
        check_limit("a", ".b")
        check_limit("a", "[0]")
        check_limit("a", "*a")

    eleza test_null_terminated(self):
        # The source code ni null-terminated internally, but bytes-like
        # objects are accepted, which could be sio terminated.
        ukijumuisha self.assertRaisesRegex(ValueError, "cannot contain null"):
            compile("123\x00", "<dummy>", "eval")
        ukijumuisha self.assertRaisesRegex(ValueError, "cannot contain null"):
            compile(memoryview(b"123\x00"), "<dummy>", "eval")
        code = compile(memoryview(b"123\x00")[1:-1], "<dummy>", "eval")
        self.assertEqual(eval(code), 23)
        code = compile(memoryview(b"1234")[1:-1], "<dummy>", "eval")
        self.assertEqual(eval(code), 23)
        code = compile(memoryview(b"$23$")[1:-1], "<dummy>", "eval")
        self.assertEqual(eval(code), 23)

        # Also test when eval() na exec() do the compilation step
        self.assertEqual(eval(memoryview(b"1234")[1:-1]), 23)
        namespace = dict()
        exec(memoryview(b"ax = 123")[1:-1], namespace)
        self.assertEqual(namespace['x'], 12)

    eleza check_constant(self, func, expected):
        kila const kwenye func.__code__.co_consts:
            ikiwa repr(const) == repr(expected):
                koma
        isipokua:
            self.fail("unable to find constant %r kwenye %r"
                      % (expected, func.__code__.co_consts))

    # Merging equal constants ni sio a strict requirement kila the Python
    # semantics, it's a more an implementation detail.
    @support.cpython_only
    eleza test_merge_constants(self):
        # Issue #25843: compile() must merge constants which are equal
        # na have the same type.

        eleza check_same_constant(const):
            ns = {}
            code = "f1, f2 = lambda: %r, lambda: %r" % (const, const)
            exec(code, ns)
            f1 = ns['f1']
            f2 = ns['f2']
            self.assertIs(f1.__code__, f2.__code__)
            self.check_constant(f1, const)
            self.assertEqual(repr(f1()), repr(const))

        check_same_constant(Tupu)
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

        # Merge constants kwenye tuple ama frozenset
        f1, f2 = lambda: "sio a name", lambda: ("sio a name",)
        f3 = lambda x: x kwenye {("sio a name",)}
        self.assertIs(f1.__code__.co_consts[1],
                      f2.__code__.co_consts[1][0])
        self.assertIs(next(iter(f3.__code__.co_consts[1])),
                      f2.__code__.co_consts[1])

        # {0} ni converted to a constant frozenset({0}) by the peephole
        # optimizer
        f1, f2 = lambda x: x kwenye {0}, lambda x: x kwenye {0}
        self.assertIs(f1.__code__, f2.__code__)
        self.check_constant(f1, frozenset({0}))
        self.assertKweli(f1(0))

    # This ni a regression test kila a CPython specific peephole optimizer
    # implementation bug present kwenye a few releases.  It's assertion verifies
    # that peephole optimization was actually done though that isn't an
    # indication of the bugs presence ama sio (crashing is).
    @support.cpython_only
    eleza test_peephole_opt_unreachable_code_array_access_in_bounds(self):
        """Regression test kila issue35193 when run under clang msan."""
        eleza unused_code_at_end():
            rudisha 3
            ashiria RuntimeError("unreachable")
        # The above function definition will trigger the out of bounds
        # bug kwenye the peephole optimizer kama it scans opcodes past the
        # RETURN_VALUE opcode.  This does sio always crash an interpreter.
        # When you build ukijumuisha the clang memory sanitizer it reliably aborts.
        self.assertEqual(
            'RETURN_VALUE',
            list(dis.get_instructions(unused_code_at_end))[-1].opname)

    eleza test_dont_merge_constants(self):
        # Issue #25843: compile() must sio merge constants which are equal
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
        # '(-0-0j)', but when '(-0-0j)' ni evaluated to 0j: we loose the sign.
        f1, f2 = lambda: +0.0j, lambda: -0.0j
        self.assertIsNot(f1.__code__, f2.__code__)
        self.check_constant(f1, +0.0j)
        self.check_constant(f2, -0.0j)
        self.assertEqual(repr(f1()), repr(+0.0j))
        self.assertEqual(repr(f2()), repr(-0.0j))

        # {0} ni converted to a constant frozenset({0}) by the peephole
        # optimizer
        f1, f2 = lambda x: x kwenye {0}, lambda x: x kwenye {0.0}
        self.assertIsNot(f1.__code__, f2.__code__)
        self.check_constant(f1, frozenset({0}))
        self.check_constant(f2, frozenset({0.0}))
        self.assertKweli(f1(0))
        self.assertKweli(f2(0.0))

    eleza test_path_like_objects(self):
        # An implicit test kila PyUnicode_FSDecoder().
        compile("42", FakePath("test_compile_pathlike"), "single")

    eleza test_stack_overflow(self):
        # bpo-31113: Stack overflow when compile a long sequence of
        # complex statements.
        compile("ikiwa a: b\n" * 200000, "<dummy>", "exec")

    # Multiple users rely on the fact that CPython does sio generate
    # bytecode kila dead code blocks. See bpo-37500 kila more context.
    @support.cpython_only
    eleza test_dead_blocks_do_not_generate_bytecode(self):
        eleza unused_block_if():
            ikiwa 0:
                rudisha 42

        eleza unused_block_while():
            wakati 0:
                rudisha 42

        eleza unused_block_if_else():
            ikiwa 1:
                rudisha Tupu
            isipokua:
                rudisha 42

        eleza unused_block_while_else():
            wakati 1:
                rudisha Tupu
            isipokua:
                rudisha 42

        funcs = [unused_block_if, unused_block_while,
                 unused_block_if_else, unused_block_while_else]

        kila func kwenye funcs:
            opcodes = list(dis.get_instructions(func))
            self.assertEqual(2, len(opcodes))
            self.assertEqual('LOAD_CONST', opcodes[0].opname)
            self.assertEqual(Tupu, opcodes[0].argval)
            self.assertEqual('RETURN_VALUE', opcodes[1].opname)


kundi TestExpressionStackSize(unittest.TestCase):
    # These tests check that the computed stack size kila a code object
    # stays within reasonable bounds (see issue #21523 kila an example
    # dysfunction).
    N = 100

    eleza check_stack_size(self, code):
        # To assert that the alleged stack size ni sio O(N), we
        # check that it ni smaller than log(N).
        ikiwa isinstance(code, str):
            code = compile(code, "<foo>", "single")
        max_size = math.ceil(math.log(len(code.co_code)))
        self.assertLessEqual(code.co_stacksize, max_size)

    eleza test_and(self):
        self.check_stack_size("x na " * self.N + "x")

    eleza test_or(self):
        self.check_stack_size("x ama " * self.N + "x")

    eleza test_and_or(self):
        self.check_stack_size("x na x ama " * self.N + "x")

    eleza test_chained_comparison(self):
        self.check_stack_size("x < " * self.N + "x")

    eleza test_if_else(self):
        self.check_stack_size("x ikiwa x isipokua " * self.N + "x")

    eleza test_binop(self):
        self.check_stack_size("x + " * self.N + "x")

    eleza test_func_and(self):
        code = "eleza f(x):\n"
        code += "   x na x\n" * self.N
        self.check_stack_size(code)


kundi TestStackSizeStability(unittest.TestCase):
    # Check that repeating certain snippets doesn't increase the stack size
    # beyond what a single snippet requires.

    eleza check_stack_size(self, snippet, async_=Uongo):
        eleza compile_snippet(i):
            ns = {}
            script = """eleza func():\n""" + i * snippet
            ikiwa async_:
                script = "async " + script
            code = compile(script, "<script>", "exec")
            exec(code, ns, ns)
            rudisha ns['func'].__code__

        sizes = [compile_snippet(i).co_stacksize kila i kwenye range(2, 5)]
        ikiwa len(set(sizes)) != 1:
            agiza dis, io
            out = io.StringIO()
            dis.dis(compile_snippet(1), file=out)
            self.fail("stack sizes diverge ukijumuisha # of consecutive snippets: "
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
            lasivyo y:
                b
            isipokua:
                c
            """
        self.check_stack_size(snippet)

    eleza test_try_except_bare(self):
        snippet = """
            jaribu:
                a
            tatizo:
                b
            """
        self.check_stack_size(snippet)

    eleza test_try_except_qualified(self):
        snippet = """
            jaribu:
                a
            tatizo ImportError:
                b
            tatizo:
                c
            isipokua:
                d
            """
        self.check_stack_size(snippet)

    eleza test_try_except_as(self):
        snippet = """
            jaribu:
                a
            tatizo ImportError kama e:
                b
            tatizo:
                c
            isipokua:
                d
            """
        self.check_stack_size(snippet)

    eleza test_try_finally(self):
        snippet = """
                jaribu:
                    a
                mwishowe:
                    b
            """
        self.check_stack_size(snippet)

    eleza test_with(self):
        snippet = """
            ukijumuisha x kama y:
                a
            """
        self.check_stack_size(snippet)

    eleza test_while_else(self):
        snippet = """
            wakati x:
                a
            isipokua:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for(self):
        snippet = """
            kila x kwenye y:
                a
            """
        self.check_stack_size(snippet)

    eleza test_for_else(self):
        snippet = """
            kila x kwenye y:
                a
            isipokua:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_koma_endelea(self):
        snippet = """
            kila x kwenye y:
                ikiwa z:
                    koma
                lasivyo u:
                    endelea
                isipokua:
                    a
            isipokua:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_koma_endelea_inside_try_finally_block(self):
        snippet = """
            kila x kwenye y:
                jaribu:
                    ikiwa z:
                        koma
                    lasivyo u:
                        endelea
                    isipokua:
                        a
                mwishowe:
                    f
            isipokua:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_koma_endelea_inside_finally_block(self):
        snippet = """
            kila x kwenye y:
                jaribu:
                    t
                mwishowe:
                    ikiwa z:
                        koma
                    lasivyo u:
                        endelea
                    isipokua:
                        a
            isipokua:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_koma_endelea_inside_except_block(self):
        snippet = """
            kila x kwenye y:
                jaribu:
                    t
                tatizo:
                    ikiwa z:
                        koma
                    lasivyo u:
                        endelea
                    isipokua:
                        a
            isipokua:
                b
            """
        self.check_stack_size(snippet)

    eleza test_for_koma_endelea_inside_with_block(self):
        snippet = """
            kila x kwenye y:
                ukijumuisha c:
                    ikiwa z:
                        koma
                    lasivyo u:
                        endelea
                    isipokua:
                        a
            isipokua:
                b
            """
        self.check_stack_size(snippet)

    eleza test_return_inside_try_finally_block(self):
        snippet = """
            jaribu:
                ikiwa z:
                    rudisha
                isipokua:
                    a
            mwishowe:
                f
            """
        self.check_stack_size(snippet)

    eleza test_return_inside_finally_block(self):
        snippet = """
            jaribu:
                t
            mwishowe:
                ikiwa z:
                    rudisha
                isipokua:
                    a
            """
        self.check_stack_size(snippet)

    eleza test_return_inside_except_block(self):
        snippet = """
            jaribu:
                t
            tatizo:
                ikiwa z:
                    rudisha
                isipokua:
                    a
            """
        self.check_stack_size(snippet)

    eleza test_return_inside_with_block(self):
        snippet = """
            ukijumuisha c:
                ikiwa z:
                    rudisha
                isipokua:
                    a
            """
        self.check_stack_size(snippet)

    eleza test_async_with(self):
        snippet = """
            async ukijumuisha x kama y:
                a
            """
        self.check_stack_size(snippet, async_=Kweli)

    eleza test_async_for(self):
        snippet = """
            async kila x kwenye y:
                a
            """
        self.check_stack_size(snippet, async_=Kweli)

    eleza test_async_for_else(self):
        snippet = """
            async kila x kwenye y:
                a
            isipokua:
                b
            """
        self.check_stack_size(snippet, async_=Kweli)

    eleza test_for_koma_endelea_inside_async_with_block(self):
        snippet = """
            kila x kwenye y:
                async ukijumuisha c:
                    ikiwa z:
                        koma
                    lasivyo u:
                        endelea
                    isipokua:
                        a
            isipokua:
                b
            """
        self.check_stack_size(snippet, async_=Kweli)

    eleza test_return_inside_async_with_block(self):
        snippet = """
            async ukijumuisha c:
                ikiwa z:
                    rudisha
                isipokua:
                    a
            """
        self.check_stack_size(snippet, async_=Kweli)


ikiwa __name__ == "__main__":
    unittest.main()
