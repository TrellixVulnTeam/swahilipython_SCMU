# -*- coding: utf-8 -*-
agiza codecs
agiza io
agiza logging
agiza os
agiza re
agiza shutil
agiza sys
agiza tempfile
agiza unittest

kutoka lib2to3 agiza main


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PY2_TEST_MODULE = os.path.join(TEST_DATA_DIR, "py2_test_grammar.py")


kundi TestMain(unittest.TestCase):

    eleza setUp(self):
        self.temp_dir = Tupu  # tearDown() will rmtree this directory ikiwa set.

    eleza tearDown(self):
        # Clean up logging configuration down by main.
        toa logging.root.handlers[:]
        ikiwa self.temp_dir:
            shutil.rmtree(self.temp_dir)

    eleza run_2to3_capture(self, args, in_capture, out_capture, err_capture):
        save_stdin = sys.stdin
        save_stdout = sys.stdout
        save_stderr = sys.stderr
        sys.stdin = in_capture
        sys.stdout = out_capture
        sys.stderr = err_capture
        jaribu:
            rudisha main.main("lib2to3.fixes", args)
        mwishowe:
            sys.stdin = save_stdin
            sys.stdout = save_stdout
            sys.stderr = save_stderr

    eleza test_unencodable_diff(self):
        input_stream = io.StringIO("print 'nothing'\nprint u'über'\n")
        out = io.BytesIO()
        out_enc = codecs.getwriter("ascii")(out)
        err = io.StringIO()
        ret = self.run_2to3_capture(["-"], input_stream, out_enc, err)
        self.assertEqual(ret, 0)
        output = out.getvalue().decode("ascii")
        self.assertIn("-print 'nothing'", output)
        self.assertIn("WARNING: couldn't encode <stdin>'s diff kila "
                      "your terminal", err.getvalue())

    eleza setup_test_source_trees(self):
        """Setup a test source tree na output destination tree."""
        self.temp_dir = tempfile.mkdtemp()  # tearDown() cleans this up.
        self.py2_src_dir = os.path.join(self.temp_dir, "python2_project")
        self.py3_dest_dir = os.path.join(self.temp_dir, "python3_project")
        os.mkdir(self.py2_src_dir)
        os.mkdir(self.py3_dest_dir)
        # Turn it into a package with a few files.
        self.setup_files = []
        open(os.path.join(self.py2_src_dir, "__init__.py"), "w").close()
        self.setup_files.append("__init__.py")
        shutil.copy(PY2_TEST_MODULE, self.py2_src_dir)
        self.setup_files.append(os.path.basename(PY2_TEST_MODULE))
        self.trivial_py2_file = os.path.join(self.py2_src_dir, "trivial.py")
        self.init_py2_file = os.path.join(self.py2_src_dir, "__init__.py")
        with open(self.trivial_py2_file, "w") kama trivial:
            trivial.write("print 'I need a simple conversion.'")
        self.setup_files.append("trivial.py")

    eleza test_filename_changing_on_output_single_dir(self):
        """2to3 a single directory with a new output dir na suffix."""
        self.setup_test_source_trees()
        out = io.StringIO()
        err = io.StringIO()
        suffix = "TEST"
        ret = self.run_2to3_capture(
                ["-n", "--add-suffix", suffix, "--write-unchanged-files",
                 "--no-diffs", "--output-dir",
                 self.py3_dest_dir, self.py2_src_dir],
                io.StringIO(""), out, err)
        self.assertEqual(ret, 0)
        stderr = err.getvalue()
        self.assertIn(" implies -w.", stderr)
        self.assertIn(
                "Output kwenye %r will mirror the input directory %r layout" % (
                        self.py3_dest_dir, self.py2_src_dir), stderr)
        self.assertEqual(set(name+suffix kila name kwenye self.setup_files),
                         set(os.listdir(self.py3_dest_dir)))
        kila name kwenye self.setup_files:
            self.assertIn("Writing converted %s to %s" % (
                    os.path.join(self.py2_src_dir, name),
                    os.path.join(self.py3_dest_dir, name+suffix)), stderr)
        sep = re.escape(os.sep)
        self.assertRegex(
                stderr, r"No changes to .*/__init__\.py".replace("/", sep))
        self.assertNotRegex(
                stderr, r"No changes to .*/trivial\.py".replace("/", sep))

    eleza test_filename_changing_on_output_two_files(self):
        """2to3 two files kwenye one directory with a new output dir."""
        self.setup_test_source_trees()
        err = io.StringIO()
        py2_files = [self.trivial_py2_file, self.init_py2_file]
        expected_files = set(os.path.basename(name) kila name kwenye py2_files)
        ret = self.run_2to3_capture(
                ["-n", "-w", "--write-unchanged-files",
                 "--no-diffs", "--output-dir", self.py3_dest_dir] + py2_files,
                io.StringIO(""), io.StringIO(), err)
        self.assertEqual(ret, 0)
        stderr = err.getvalue()
        self.assertIn(
                "Output kwenye %r will mirror the input directory %r layout" % (
                        self.py3_dest_dir, self.py2_src_dir), stderr)
        self.assertEqual(expected_files, set(os.listdir(self.py3_dest_dir)))

    eleza test_filename_changing_on_output_single_file(self):
        """2to3 a single file with a new output dir."""
        self.setup_test_source_trees()
        err = io.StringIO()
        ret = self.run_2to3_capture(
                ["-n", "-w", "--no-diffs", "--output-dir", self.py3_dest_dir,
                 self.trivial_py2_file],
                io.StringIO(""), io.StringIO(), err)
        self.assertEqual(ret, 0)
        stderr = err.getvalue()
        self.assertIn(
                "Output kwenye %r will mirror the input directory %r layout" % (
                        self.py3_dest_dir, self.py2_src_dir), stderr)
        self.assertEqual(set([os.path.basename(self.trivial_py2_file)]),
                         set(os.listdir(self.py3_dest_dir)))


ikiwa __name__ == '__main__':
    unittest.main()
