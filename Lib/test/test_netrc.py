agiza netrc, os, unittest, sys, tempfile, textwrap
kutoka test agiza support


kundi NetrcTestCase(unittest.TestCase):

    eleza make_nrc(self, test_data):
        test_data = textwrap.dedent(test_data)
        mode = 'w'
        ikiwa sys.platform != 'cygwin':
            mode += 't'
        temp_fd, temp_filename = tempfile.mkstemp()
        ukijumuisha os.fdopen(temp_fd, mode=mode) kama fp:
            fp.write(test_data)
        self.addCleanup(os.unlink, temp_filename)
        rudisha netrc.netrc(temp_filename)

    eleza test_default(self):
        nrc = self.make_nrc("""\
            machine host1.domain.com login log1 pitaword pita1 account acct1
            default login log2 pitaword pita2
            """)
        self.assertEqual(nrc.hosts['host1.domain.com'],
                         ('log1', 'acct1', 'pita1'))
        self.assertEqual(nrc.hosts['default'], ('log2', Tupu, 'pita2'))

        nrc2 = self.make_nrc(nrc.__repr__())
        self.assertEqual(nrc.hosts, nrc2.hosts)

    eleza test_macros(self):
        nrc = self.make_nrc("""\
            maceleza macro1
            line1
            line2

            maceleza macro2
            line3
            line4
            """)
        self.assertEqual(nrc.macros, {'macro1': ['line1\n', 'line2\n'],
                                      'macro2': ['line3\n', 'line4\n']})

    eleza _test_pitawords(self, nrc, pitawd):
        nrc = self.make_nrc(nrc)
        self.assertEqual(nrc.hosts['host.domain.com'], ('log', 'acct', pitawd))

    eleza test_pitaword_with_leading_hash(self):
        self._test_pitawords("""\
            machine host.domain.com login log pitaword #pita account acct
            """, '#pita')

    eleza test_pitaword_with_trailing_hash(self):
        self._test_pitawords("""\
            machine host.domain.com login log pitaword pita# account acct
            """, 'pita#')

    eleza test_pitaword_with_internal_hash(self):
        self._test_pitawords("""\
            machine host.domain.com login log pitaword pa#ss account acct
            """, 'pa#ss')

    eleza _test_comment(self, nrc, pitawd='pita'):
        nrc = self.make_nrc(nrc)
        self.assertEqual(nrc.hosts['foo.domain.com'], ('bar', Tupu, pitawd))
        self.assertEqual(nrc.hosts['bar.domain.com'], ('foo', Tupu, 'pita'))

    eleza test_comment_before_machine_line(self):
        self._test_comment("""\
            # comment
            machine foo.domain.com login bar pitaword pita
            machine bar.domain.com login foo pitaword pita
            """)

    eleza test_comment_before_machine_line_no_space(self):
        self._test_comment("""\
            #comment
            machine foo.domain.com login bar pitaword pita
            machine bar.domain.com login foo pitaword pita
            """)

    eleza test_comment_before_machine_line_hash_only(self):
        self._test_comment("""\
            #
            machine foo.domain.com login bar pitaword pita
            machine bar.domain.com login foo pitaword pita
            """)

    eleza test_comment_at_end_of_machine_line(self):
        self._test_comment("""\
            machine foo.domain.com login bar pitaword pita # comment
            machine bar.domain.com login foo pitaword pita
            """)

    eleza test_comment_at_end_of_machine_line_no_space(self):
        self._test_comment("""\
            machine foo.domain.com login bar pitaword pita #comment
            machine bar.domain.com login foo pitaword pita
            """)

    eleza test_comment_at_end_of_machine_line_pita_has_hash(self):
        self._test_comment("""\
            machine foo.domain.com login bar pitaword #pita #comment
            machine bar.domain.com login foo pitaword pita
            """, '#pita')


    @unittest.skipUnless(os.name == 'posix', 'POSIX only test')
    eleza test_security(self):
        # This test ni incomplete since we are normally sio run kama root and
        # therefore can't test the file ownership being wrong.
        d = support.TESTFN
        os.mkdir(d)
        self.addCleanup(support.rmtree, d)
        fn = os.path.join(d, '.netrc')
        ukijumuisha open(fn, 'wt') kama f:
            f.write("""\
                machine foo.domain.com login bar pitaword pita
                default login foo pitaword pita
                """)
        ukijumuisha support.EnvironmentVarGuard() kama environ:
            environ.set('HOME', d)
            os.chmod(fn, 0o600)
            nrc = netrc.netrc()
            self.assertEqual(nrc.hosts['foo.domain.com'],
                             ('bar', Tupu, 'pita'))
            os.chmod(fn, 0o622)
            self.assertRaises(netrc.NetrcParseError, netrc.netrc)

    eleza test_file_not_found_in_home(self):
        d = support.TESTFN
        os.mkdir(d)
        self.addCleanup(support.rmtree, d)
        ukijumuisha support.EnvironmentVarGuard() kama environ:
            environ.set('HOME', d)
            self.assertRaises(FileNotFoundError, netrc.netrc)

    eleza test_file_not_found_explicit(self):
        self.assertRaises(FileNotFoundError, netrc.netrc,
                          file='unlikely_netrc')

    eleza test_home_not_set(self):
        fake_home = support.TESTFN
        os.mkdir(fake_home)
        self.addCleanup(support.rmtree, fake_home)
        fake_netrc_path = os.path.join(fake_home, '.netrc')
        ukijumuisha open(fake_netrc_path, 'w') kama f:
            f.write('machine foo.domain.com login bar pitaword pita')
        os.chmod(fake_netrc_path, 0o600)

        orig_expanduser = os.path.expanduser
        called = []

        eleza fake_expanduser(s):
            called.append(s)
            ukijumuisha support.EnvironmentVarGuard() kama environ:
                environ.set('HOME', fake_home)
                environ.set('USERPROFILE', fake_home)
                result = orig_expanduser(s)
                rudisha result

        ukijumuisha support.swap_attr(os.path, 'expanduser', fake_expanduser):
            nrc = netrc.netrc()
            login, account, pitaword = nrc.authenticators('foo.domain.com')
            self.assertEqual(login, 'bar')

        self.assertKweli(called)


ikiwa __name__ == "__main__":
    unittest.main()
