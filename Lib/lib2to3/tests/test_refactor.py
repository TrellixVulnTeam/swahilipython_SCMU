"""
Unit tests kila refactor.py.
"""

agiza sys
agiza os
agiza codecs
agiza io
agiza re
agiza tempfile
agiza shutil
agiza unittest

kutoka lib2to3 agiza refactor, pygram, fixer_base
kutoka lib2to3.pgen2 agiza token


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIXER_DIR = os.path.join(TEST_DATA_DIR, "fixers")

sys.path.append(FIXER_DIR)
jaribu:
    _DEFAULT_FIXERS = refactor.get_fixers_from_package("myfixes")
mwishowe:
    sys.path.pop()

_2TO3_FIXERS = refactor.get_fixers_from_package("lib2to3.fixes")

kundi TestRefactoringTool(unittest.TestCase):

    eleza setUp(self):
        sys.path.append(FIXER_DIR)

    eleza tearDown(self):
        sys.path.pop()

    eleza check_instances(self, instances, classes):
        kila inst, cls kwenye zip(instances, classes):
            ikiwa sio isinstance(inst, cls):
                self.fail("%s are sio instances of %s" % instances, classes)

    eleza rt(self, options=Tupu, fixers=_DEFAULT_FIXERS, explicit=Tupu):
        rudisha refactor.RefactoringTool(fixers, options, explicit)

    eleza test_print_function_option(self):
        rt = self.rt({"print_function" : Kweli})
        self.assertIs(rt.grammar, pygram.python_grammar_no_print_statement)
        self.assertIs(rt.driver.grammar,
                      pygram.python_grammar_no_print_statement)

    eleza test_write_unchanged_files_option(self):
        rt = self.rt()
        self.assertUongo(rt.write_unchanged_files)
        rt = self.rt({"write_unchanged_files" : Kweli})
        self.assertKweli(rt.write_unchanged_files)

    eleza test_fixer_loading_helpers(self):
        contents = ["explicit", "first", "last", "parrot", "preorder"]
        non_prefixed = refactor.get_all_fix_names("myfixes")
        prefixed = refactor.get_all_fix_names("myfixes", Uongo)
        full_names = refactor.get_fixers_from_package("myfixes")
        self.assertEqual(prefixed, ["fix_" + name kila name kwenye contents])
        self.assertEqual(non_prefixed, contents)
        self.assertEqual(full_names,
                         ["myfixes.fix_" + name kila name kwenye contents])

    eleza test_detect_future_features(self):
        run = refactor._detect_future_features
        fs = frozenset
        empty = fs()
        self.assertEqual(run(""), empty)
        self.assertEqual(run("kutoka __future__ agiza print_function"),
                         fs(("print_function",)))
        self.assertEqual(run("kutoka __future__ agiza generators"),
                         fs(("generators",)))
        self.assertEqual(run("kutoka __future__ agiza generators, feature"),
                         fs(("generators", "feature")))
        inp = "kutoka __future__ agiza generators, print_function"
        self.assertEqual(run(inp), fs(("generators", "print_function")))
        inp ="kutoka __future__ agiza print_function, generators"
        self.assertEqual(run(inp), fs(("print_function", "generators")))
        inp = "kutoka __future__ agiza (print_function,)"
        self.assertEqual(run(inp), fs(("print_function",)))
        inp = "kutoka __future__ agiza (generators, print_function)"
        self.assertEqual(run(inp), fs(("generators", "print_function")))
        inp = "kutoka __future__ agiza (generators, nested_scopes)"
        self.assertEqual(run(inp), fs(("generators", "nested_scopes")))
        inp = """kutoka __future__ agiza generators
kutoka __future__ agiza print_function"""
        self.assertEqual(run(inp), fs(("generators", "print_function")))
        invalid = ("from",
                   "kutoka 4",
                   "kutoka x",
                   "kutoka x 5",
                   "kutoka x im",
                   "kutoka x import",
                   "kutoka x agiza 4",
                   )
        kila inp kwenye invalid:
            self.assertEqual(run(inp), empty)
        inp = "'docstring'\nkutoka __future__ agiza print_function"
        self.assertEqual(run(inp), fs(("print_function",)))
        inp = "'docstring'\n'somng'\nkutoka __future__ agiza print_function"
        self.assertEqual(run(inp), empty)
        inp = "# comment\nkutoka __future__ agiza print_function"
        self.assertEqual(run(inp), fs(("print_function",)))
        inp = "# comment\n'doc'\nkutoka __future__ agiza print_function"
        self.assertEqual(run(inp), fs(("print_function",)))
        inp = "kundi x: pita\nkutoka __future__ agiza print_function"
        self.assertEqual(run(inp), empty)

    eleza test_get_headnode_dict(self):
        kundi TupuFix(fixer_base.BaseFix):
            pita

        kundi FileInputFix(fixer_base.BaseFix):
            PATTERN = "file_input< any * >"

        kundi SimpleFix(fixer_base.BaseFix):
            PATTERN = "'name'"

        no_head = TupuFix({}, [])
        with_head = FileInputFix({}, [])
        simple = SimpleFix({}, [])
        d = refactor._get_headnode_dict([no_head, with_head, simple])
        top_fixes = d.pop(pygram.python_symbols.file_input)
        self.assertEqual(top_fixes, [with_head, no_head])
        name_fixes = d.pop(token.NAME)
        self.assertEqual(name_fixes, [simple, no_head])
        kila fixes kwenye d.values():
            self.assertEqual(fixes, [no_head])

    eleza test_fixer_loading(self):
        kutoka myfixes.fix_first agiza FixFirst
        kutoka myfixes.fix_last agiza FixLast
        kutoka myfixes.fix_parrot agiza FixParrot
        kutoka myfixes.fix_preorder agiza FixPreorder

        rt = self.rt()
        pre, post = rt.get_fixers()

        self.check_instances(pre, [FixPreorder])
        self.check_instances(post, [FixFirst, FixParrot, FixLast])

    eleza test_naughty_fixers(self):
        self.assertRaises(ImportError, self.rt, fixers=["not_here"])
        self.assertRaises(refactor.FixerError, self.rt, fixers=["no_fixer_cls"])
        self.assertRaises(refactor.FixerError, self.rt, fixers=["bad_order"])

    eleza test_refactor_string(self):
        rt = self.rt()
        input = "eleza parrot(): pita\n\n"
        tree = rt.refactor_string(input, "<test>")
        self.assertNotEqual(str(tree), input)

        input = "eleza f(): pita\n\n"
        tree = rt.refactor_string(input, "<test>")
        self.assertEqual(str(tree), input)

    eleza test_refactor_stdin(self):

        kundi MyRT(refactor.RefactoringTool):

            eleza print_output(self, old_text, new_text, filename, equal):
                results.extend([old_text, new_text, filename, equal])

        results = []
        rt = MyRT(_DEFAULT_FIXERS)
        save = sys.stdin
        sys.stdin = io.StringIO("eleza parrot(): pita\n\n")
        jaribu:
            rt.refactor_stdin()
        mwishowe:
            sys.stdin = save
        expected = ["eleza parrot(): pita\n\n",
                    "eleza cheese(): pita\n\n",
                    "<stdin>", Uongo]
        self.assertEqual(results, expected)

    eleza check_file_refactoring(self, test_file, fixers=_2TO3_FIXERS,
                               options=Tupu, mock_log_debug=Tupu,
                               actually_write=Kweli):
        test_file = self.init_test_file(test_file)
        old_contents = self.read_file(test_file)
        rt = self.rt(fixers=fixers, options=options)
        ikiwa mock_log_debug:
            rt.log_debug = mock_log_debug

        rt.refactor_file(test_file)
        self.assertEqual(old_contents, self.read_file(test_file))

        ikiwa sio actually_write:
            return
        rt.refactor_file(test_file, Kweli)
        new_contents = self.read_file(test_file)
        self.assertNotEqual(old_contents, new_contents)
        rudisha new_contents

    eleza init_test_file(self, test_file):
        tmpdir = tempfile.mkdtemp(prefix="2to3-test_refactor")
        self.addCleanup(shutil.rmtree, tmpdir)
        shutil.copy(test_file, tmpdir)
        test_file = os.path.join(tmpdir, os.path.basename(test_file))
        os.chmod(test_file, 0o644)
        rudisha test_file

    eleza read_file(self, test_file):
        ukijumuisha open(test_file, "rb") kama fp:
            rudisha fp.read()

    eleza refactor_file(self, test_file, fixers=_2TO3_FIXERS):
        test_file = self.init_test_file(test_file)
        old_contents = self.read_file(test_file)
        rt = self.rt(fixers=fixers)
        rt.refactor_file(test_file, Kweli)
        new_contents = self.read_file(test_file)
        rudisha old_contents, new_contents

    eleza test_refactor_file(self):
        test_file = os.path.join(FIXER_DIR, "parrot_example.py")
        self.check_file_refactoring(test_file, _DEFAULT_FIXERS)

    eleza test_refactor_file_write_unchanged_file(self):
        test_file = os.path.join(FIXER_DIR, "parrot_example.py")
        debug_messages = []
        eleza recording_log_debug(msg, *args):
            debug_messages.append(msg % args)
        self.check_file_refactoring(test_file, fixers=(),
                                    options={"write_unchanged_files": Kweli},
                                    mock_log_debug=recording_log_debug,
                                    actually_write=Uongo)
        # Testing that it logged this message when write=Uongo was pitaed is
        # sufficient to see that it did sio bail early after "No changes".
        message_regex = r"Not writing changes to .*%s" % \
                re.escape(os.sep + os.path.basename(test_file))
        kila message kwenye debug_messages:
            ikiwa "Not writing changes" kwenye message:
                self.assertRegex(message, message_regex)
                koma
        isipokua:
            self.fail("%r sio matched kwenye %r" % (message_regex, debug_messages))

    eleza test_refactor_dir(self):
        eleza check(structure, expected):
            eleza mock_refactor_file(self, f, *args):
                got.append(f)
            save_func = refactor.RefactoringTool.refactor_file
            refactor.RefactoringTool.refactor_file = mock_refactor_file
            rt = self.rt()
            got = []
            dir = tempfile.mkdtemp(prefix="2to3-test_refactor")
            jaribu:
                os.mkdir(os.path.join(dir, "a_dir"))
                kila fn kwenye structure:
                    open(os.path.join(dir, fn), "wb").close()
                rt.refactor_dir(dir)
            mwishowe:
                refactor.RefactoringTool.refactor_file = save_func
                shutil.rmtree(dir)
            self.assertEqual(got,
                             [os.path.join(dir, path) kila path kwenye expected])
        check([], [])
        tree = ["nothing",
                "hi.py",
                ".dumb",
                ".after.py",
                "notpy.npy",
                "sappy"]
        expected = ["hi.py"]
        check(tree, expected)
        tree = ["hi.py",
                os.path.join("a_dir", "stuff.py")]
        check(tree, tree)

    eleza test_file_encoding(self):
        fn = os.path.join(TEST_DATA_DIR, "different_encoding.py")
        self.check_file_refactoring(fn)

    eleza test_false_file_encoding(self):
        fn = os.path.join(TEST_DATA_DIR, "false_encoding.py")
        data = self.check_file_refactoring(fn)

    eleza test_bom(self):
        fn = os.path.join(TEST_DATA_DIR, "bom.py")
        data = self.check_file_refactoring(fn)
        self.assertKweli(data.startswith(codecs.BOM_UTF8))

    eleza test_crlf_newlines(self):
        old_sep = os.linesep
        os.linesep = "\r\n"
        jaribu:
            fn = os.path.join(TEST_DATA_DIR, "crlf.py")
            fixes = refactor.get_fixers_from_package("lib2to3.fixes")
            self.check_file_refactoring(fn, fixes)
        mwishowe:
            os.linesep = old_sep

    eleza test_crlf_unchanged(self):
        fn = os.path.join(TEST_DATA_DIR, "crlf.py")
        old, new = self.refactor_file(fn)
        self.assertIn(b"\r\n", old)
        self.assertIn(b"\r\n", new)
        self.assertNotIn(b"\r\r\n", new)

    eleza test_refactor_docstring(self):
        rt = self.rt()

        doc = """
>>> example()
42
"""
        out = rt.refactor_docstring(doc, "<test>")
        self.assertEqual(out, doc)

        doc = """
>>> eleza parrot():
...      rudisha 43
"""
        out = rt.refactor_docstring(doc, "<test>")
        self.assertNotEqual(out, doc)

    eleza test_explicit(self):
        kutoka myfixes.fix_explicit agiza FixExplicit

        rt = self.rt(fixers=["myfixes.fix_explicit"])
        self.assertEqual(len(rt.post_order), 0)

        rt = self.rt(explicit=["myfixes.fix_explicit"])
        kila fix kwenye rt.post_order:
            ikiwa isinstance(fix, FixExplicit):
                koma
        isipokua:
            self.fail("explicit fixer sio loaded")
