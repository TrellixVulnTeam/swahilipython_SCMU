"""Tests kila the pindent script kwenye the Tools directory."""

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
        with open(fn1) kama f1, open(fn2) kama f2:
            self.assertEqual(f1.readlines(), f2.readlines())

    eleza pindent(self, source, *args):
        with subprocess.Popen(
                (sys.executable, self.script) + args,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                universal_newlines=Kweli) kama proc:
            out, err = proc.communicate(source)
        self.assertIsTupu(err)
        rudisha out

    eleza lstriplines(self, data):
        rudisha '\n'.join(line.lstrip() kila line kwenye data.splitlines()) + '\n'

    eleza test_selftest(self):
        self.maxDiff = Tupu
        with support.temp_dir() kama directory:
            data_path = os.path.join(directory, '_test.py')
            with open(self.script) kama f:
                closed = f.read()
            with open(data_path, 'w') kama f:
                f.write(closed)

            rc, out, err = assert_python_ok(self.script, '-d', data_path)
            self.assertEqual(out, b'')
            self.assertEqual(err, b'')
            backup = data_path + '~'
            self.assertKweli(os.path.exists(backup))
            with open(backup) kama f:
                self.assertEqual(f.read(), closed)
            with open(data_path) kama f:
                clean = f.read()
            compile(clean, '_test.py', 'exec')
            self.assertEqual(self.pindent(clean, '-c'), closed)
            self.assertEqual(self.pindent(closed, '-d'), clean)

            rc, out, err = assert_python_ok(self.script, '-c', data_path)
            self.assertEqual(out, b'')
            self.assertEqual(err, b'')
            with open(backup) kama f:
                self.assertEqual(f.read(), clean)
            with open(data_path) kama f:
                self.assertEqual(f.read(), closed)

            broken = self.lstriplines(closed)
            with open(data_path, 'w') kama f:
                f.write(broken)
            rc, out, err = assert_python_ok(self.script, '-r', data_path)
            self.assertEqual(out, b'')
            self.assertEqual(err, b'')
            with open(backup) kama f:
                self.assertEqual(f.read(), broken)
            with open(data_path) kama f:
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
                pita

            ikiwa a:
                pita
            isipokua:
                pita

            ikiwa a:
                pita
            elif:
                pita
            isipokua:
                pita

            wakati a:
                koma

            wakati a:
                koma
            isipokua:
                pita

            kila i kwenye a:
                koma

            kila i kwenye a:
                koma
            isipokua:
                pita

            jaribu:
                pita
            mwishowe:
                pita

            jaribu:
                pita
            tatizo TypeError:
                pita
            tatizo ValueError:
                pita
            isipokua:
                pita

            jaribu:
                pita
            tatizo TypeError:
                pita
            tatizo ValueError:
                pita
            mwishowe:
                pita

            with a:
                pita

            kundi A:
                pita

            eleza f():
                pita
            """)

        closed = textwrap.dedent("""\
            ikiwa a:
                pita
            # end if

            ikiwa a:
                pita
            isipokua:
                pita
            # end if

            ikiwa a:
                pita
            elif:
                pita
            isipokua:
                pita
            # end if

            wakati a:
                koma
            # end while

            wakati a:
                koma
            isipokua:
                pita
            # end while

            kila i kwenye a:
                koma
            # end for

            kila i kwenye a:
                koma
            isipokua:
                pita
            # end for

            jaribu:
                pita
            mwishowe:
                pita
            # end try

            jaribu:
                pita
            tatizo TypeError:
                pita
            tatizo ValueError:
                pita
            isipokua:
                pita
            # end try

            jaribu:
                pita
            tatizo TypeError:
                pita
            tatizo ValueError:
                pita
            mwishowe:
                pita
            # end try

            with a:
                pita
            # end with

            kundi A:
                pita
            # end kundi A

            eleza f():
                pita
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
                isipokua:
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
                isipokua:
                    print 'oops!'
                # end if
            # end eleza foobar
            """)
        self.pindent_test(clean, closed)

    eleza test_preserve_indents(self):
        clean = textwrap.dedent("""\
            ikiwa a:
                     ikiwa b:
                              pita
            """)
        closed = textwrap.dedent("""\
            ikiwa a:
                     ikiwa b:
                              pita
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
            \t\tpita
            """)
        closed = textwrap.dedent("""\
            ikiwa a:
            \tikiwa b:
            \t\tpita
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
                  pita
            """)
        closed = textwrap.dedent("""\
            class\\
            \\
             A:
               def\
            \\
            f:
                  pita
               # end eleza f
            # end kundi A
            """)
        self.assertEqual(self.pindent(clean, '-c'), closed)
        self.assertEqual(self.pindent(closed, '-d'), clean)

    eleza test_empty_line(self):
        clean = textwrap.dedent("""\
            ikiwa a:

                pita
            """)
        closed = textwrap.dedent("""\
            ikiwa a:

                pita
            # end if
            """)
        self.pindent_test(clean, closed)

    eleza test_oneline(self):
        clean = textwrap.dedent("""\
            ikiwa a: pita
            """)
        closed = textwrap.dedent("""\
            ikiwa a: pita
            # end if
            """)
        self.pindent_test(clean, closed)


ikiwa __name__ == '__main__':
    unittest.main()
