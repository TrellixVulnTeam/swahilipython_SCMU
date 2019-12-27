"""Tests for the pindent script in the Tools directory."""

agiza os
agiza sys
agiza unittest
agiza subprocess
agiza textwrap
kutoka test agiza support
kutoka test.support.script_helper agiza assert_python_ok

kutoka test.test_tools agiza scriptsdir, skip_if_missing

skip_if_missing()


kundi PindentTests(unittest.TestCase):
    script = os.path.join(scriptsdir, 'pindent.py')

    eleza assertFileEqual(self, fn1, fn2):
        with open(fn1) as f1, open(fn2) as f2:
            self.assertEqual(f1.readlines(), f2.readlines())

    eleza pindent(self, source, *args):
        with subprocess.Popen(
                (sys.executable, self.script) + args,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                universal_newlines=True) as proc:
            out, err = proc.communicate(source)
        self.assertIsNone(err)
        rudisha out

    eleza lstriplines(self, data):
        rudisha '\n'.join(line.lstrip() for line in data.splitlines()) + '\n'

    eleza test_selftest(self):
        self.maxDiff = None
        with support.temp_dir() as directory:
            data_path = os.path.join(directory, '_test.py')
            with open(self.script) as f:
                closed = f.read()
            with open(data_path, 'w') as f:
                f.write(closed)

            rc, out, err = assert_python_ok(self.script, '-d', data_path)
            self.assertEqual(out, b'')
            self.assertEqual(err, b'')
            backup = data_path + '~'
            self.assertTrue(os.path.exists(backup))
            with open(backup) as f:
                self.assertEqual(f.read(), closed)
            with open(data_path) as f:
                clean = f.read()
            compile(clean, '_test.py', 'exec')
            self.assertEqual(self.pindent(clean, '-c'), closed)
            self.assertEqual(self.pindent(closed, '-d'), clean)

            rc, out, err = assert_python_ok(self.script, '-c', data_path)
            self.assertEqual(out, b'')
            self.assertEqual(err, b'')
            with open(backup) as f:
                self.assertEqual(f.read(), clean)
            with open(data_path) as f:
                self.assertEqual(f.read(), closed)

            broken = self.lstriplines(closed)
            with open(data_path, 'w') as f:
                f.write(broken)
            rc, out, err = assert_python_ok(self.script, '-r', data_path)
            self.assertEqual(out, b'')
            self.assertEqual(err, b'')
            with open(backup) as f:
                self.assertEqual(f.read(), broken)
            with open(data_path) as f:
                indented = f.read()
            compile(indented, '_test.py', 'exec')
            self.assertEqual(self.pindent(broken, '-r'), indented)

    eleza pindent_test(self, clean, closed):
        self.assertEqual(self.pindent(clean, '-c'), closed)
        self.assertEqual(self.pindent(closed, '-d'), clean)
        broken = self.lstriplines(closed)
        self.assertEqual(self.pindent(broken, '-r', '-e', '-s', '4'), closed)

    eleza test_statements(self):
        clean = textwrap.dedent("""\
            ikiwa a:
                pass

            ikiwa a:
                pass
            else:
                pass

            ikiwa a:
                pass
            elif:
                pass
            else:
                pass

            while a:
                break

            while a:
                break
            else:
                pass

            for i in a:
                break

            for i in a:
                break
            else:
                pass

            try:
                pass
            finally:
                pass

            try:
                pass
            except TypeError:
                pass
            except ValueError:
                pass
            else:
                pass

            try:
                pass
            except TypeError:
                pass
            except ValueError:
                pass
            finally:
                pass

            with a:
                pass

            kundi A:
                pass

            eleza f():
                pass
            """)

        closed = textwrap.dedent("""\
            ikiwa a:
                pass
            # end if

            ikiwa a:
                pass
            else:
                pass
            # end if

            ikiwa a:
                pass
            elif:
                pass
            else:
                pass
            # end if

            while a:
                break
            # end while

            while a:
                break
            else:
                pass
            # end while

            for i in a:
                break
            # end for

            for i in a:
                break
            else:
                pass
            # end for

            try:
                pass
            finally:
                pass
            # end try

            try:
                pass
            except TypeError:
                pass
            except ValueError:
                pass
            else:
                pass
            # end try

            try:
                pass
            except TypeError:
                pass
            except ValueError:
                pass
            finally:
                pass
            # end try

            with a:
                pass
            # end with

            kundi A:
                pass
            # end kundi A

            eleza f():
                pass
            # end eleza f
            """)
        self.pindent_test(clean, closed)

    eleza test_multilevel(self):
        clean = textwrap.dedent("""\
            eleza foobar(a, b):
                ikiwa a == b:
                    a = a+1
                elikiwa a < b:
                    b = b-1
                    ikiwa b > a: a = a-1
                else:
                    print 'oops!'
            """)
        closed = textwrap.dedent("""\
            eleza foobar(a, b):
                ikiwa a == b:
                    a = a+1
                elikiwa a < b:
                    b = b-1
                    ikiwa b > a: a = a-1
                    # end if
                else:
                    print 'oops!'
                # end if
            # end eleza foobar
            """)
        self.pindent_test(clean, closed)

    eleza test_preserve_indents(self):
        clean = textwrap.dedent("""\
            ikiwa a:
                     ikiwa b:
                              pass
            """)
        closed = textwrap.dedent("""\
            ikiwa a:
                     ikiwa b:
                              pass
                     # end if
            # end if
            """)
        self.assertEqual(self.pindent(clean, '-c'), closed)
        self.assertEqual(self.pindent(closed, '-d'), clean)
        broken = self.lstriplines(closed)
        self.assertEqual(self.pindent(broken, '-r', '-e', '-s', '9'), closed)
        clean = textwrap.dedent("""\
            ikiwa a:
            \tikiwa b:
            \t\tpass
            """)
        closed = textwrap.dedent("""\
            ikiwa a:
            \tikiwa b:
            \t\tpass
            \t# end if
            # end if
            """)
        self.assertEqual(self.pindent(clean, '-c'), closed)
        self.assertEqual(self.pindent(closed, '-d'), clean)
        broken = self.lstriplines(closed)
        self.assertEqual(self.pindent(broken, '-r'), closed)

    eleza test_escaped_newline(self):
        clean = textwrap.dedent("""\
            class\\
            \\
             A:
               def\
            \\
            f:
                  pass
            """)
        closed = textwrap.dedent("""\
            class\\
            \\
             A:
               def\
            \\
            f:
                  pass
               # end eleza f
            # end kundi A
            """)
        self.assertEqual(self.pindent(clean, '-c'), closed)
        self.assertEqual(self.pindent(closed, '-d'), clean)

    eleza test_empty_line(self):
        clean = textwrap.dedent("""\
            ikiwa a:

                pass
            """)
        closed = textwrap.dedent("""\
            ikiwa a:

                pass
            # end if
            """)
        self.pindent_test(clean, closed)

    eleza test_oneline(self):
        clean = textwrap.dedent("""\
            ikiwa a: pass
            """)
        closed = textwrap.dedent("""\
            ikiwa a: pass
            # end if
            """)
        self.pindent_test(clean, closed)


ikiwa __name__ == '__main__':
    unittest.main()
