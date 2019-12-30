"""Tests kila distutils.command.check."""
agiza os
agiza textwrap
agiza unittest
kutoka test.support agiza run_unittest

kutoka distutils.command.check agiza check, HAS_DOCUTILS
kutoka distutils.tests agiza support
kutoka distutils.errors agiza DistutilsSetupError

jaribu:
    agiza pygments
except ImportError:
    pygments = Tupu


HERE = os.path.dirname(__file__)


kundi CheckTestCase(support.LoggingSilencer,
                    support.TempdirManager,
                    unittest.TestCase):

    eleza _run(self, metadata=Tupu, cwd=Tupu, **options):
        ikiwa metadata ni Tupu:
            metadata = {}
        ikiwa cwd ni sio Tupu:
            old_dir = os.getcwd()
            os.chdir(cwd)
        pkg_info, dist = self.create_dist(**metadata)
        cmd = check(dist)
        cmd.initialize_options()
        kila name, value kwenye options.items():
            setattr(cmd, name, value)
        cmd.ensure_finalized()
        cmd.run()
        ikiwa cwd ni sio Tupu:
            os.chdir(old_dir)
        rudisha cmd

    eleza test_check_metadata(self):
        # let's run the command ukijumuisha no metadata at all
        # by default, check ni checking the metadata
        # should have some warnings
        cmd = self._run()
        self.assertEqual(cmd._warnings, 2)

        # now let's add the required fields
        # na run it again, to make sure we don't get
        # any warning anymore
        metadata = {'url': 'xxx', 'author': 'xxx',
                    'author_email': 'xxx',
                    'name': 'xxx', 'version': 'xxx'}
        cmd = self._run(metadata)
        self.assertEqual(cmd._warnings, 0)

        # now ukijumuisha the strict mode, we should
        # get an error ikiwa there are missing metadata
        self.assertRaises(DistutilsSetupError, self._run, {}, **{'strict': 1})

        # na of course, no error when all metadata are present
        cmd = self._run(metadata, strict=1)
        self.assertEqual(cmd._warnings, 0)

        # now a test ukijumuisha non-ASCII characters
        metadata = {'url': 'xxx', 'author': '\u00c9ric',
                    'author_email': 'xxx', 'name': 'xxx',
                    'version': 'xxx',
                    'description': 'Something about esszet \u00df',
                    'long_description': 'More things about esszet \u00df'}
        cmd = self._run(metadata)
        self.assertEqual(cmd._warnings, 0)

    @unittest.skipUnless(HAS_DOCUTILS, "won't test without docutils")
    eleza test_check_document(self):
        pkg_info, dist = self.create_dist()
        cmd = check(dist)

        # let's see ikiwa it detects broken rest
        broken_rest = 'title\n===\n\ntest'
        msgs = cmd._check_rst_data(broken_rest)
        self.assertEqual(len(msgs), 1)

        # na non-broken rest
        rest = 'title\n=====\n\ntest'
        msgs = cmd._check_rst_data(rest)
        self.assertEqual(len(msgs), 0)

    @unittest.skipUnless(HAS_DOCUTILS, "won't test without docutils")
    eleza test_check_restructuredtext(self):
        # let's see ikiwa it detects broken rest kwenye long_description
        broken_rest = 'title\n===\n\ntest'
        pkg_info, dist = self.create_dist(long_description=broken_rest)
        cmd = check(dist)
        cmd.check_restructuredtext()
        self.assertEqual(cmd._warnings, 1)

        # let's see ikiwa we have an error ukijumuisha strict=1
        metadata = {'url': 'xxx', 'author': 'xxx',
                    'author_email': 'xxx',
                    'name': 'xxx', 'version': 'xxx',
                    'long_description': broken_rest}
        self.assertRaises(DistutilsSetupError, self._run, metadata,
                          **{'strict': 1, 'restructuredtext': 1})

        # na non-broken rest, including a non-ASCII character to test #12114
        metadata['long_description'] = 'title\n=====\n\ntest \u00df'
        cmd = self._run(metadata, strict=1, restructuredtext=1)
        self.assertEqual(cmd._warnings, 0)

        # check that includes work to test #31292
        metadata['long_description'] = 'title\n=====\n\n.. include:: includetest.rst'
        cmd = self._run(metadata, cwd=HERE, strict=1, restructuredtext=1)
        self.assertEqual(cmd._warnings, 0)

    @unittest.skipUnless(HAS_DOCUTILS, "won't test without docutils")
    eleza test_check_restructuredtext_with_syntax_highlight(self):
        # Don't fail ikiwa there ni a `code` ama `code-block` directive

        example_rst_docs = []
        example_rst_docs.append(textwrap.dedent("""\
            Here's some code:

            .. code:: python

                eleza foo():
                    pass
            """))
        example_rst_docs.append(textwrap.dedent("""\
            Here's some code:

            .. code-block:: python

                eleza foo():
                    pass
            """))

        kila rest_with_code kwenye example_rst_docs:
            pkg_info, dist = self.create_dist(long_description=rest_with_code)
            cmd = check(dist)
            cmd.check_restructuredtext()
            msgs = cmd._check_rst_data(rest_with_code)
            ikiwa pygments ni sio Tupu:
                self.assertEqual(len(msgs), 0)
            isipokua:
                self.assertEqual(len(msgs), 1)
                self.assertEqual(
                    str(msgs[0][1]),
                    'Cannot analyze code. Pygments package sio found.'
                )

    eleza test_check_all(self):

        metadata = {'url': 'xxx', 'author': 'xxx'}
        self.assertRaises(DistutilsSetupError, self._run,
                          {}, **{'strict': 1,
                                 'restructuredtext': 1})

eleza test_suite():
    rudisha unittest.makeSuite(CheckTestCase)

ikiwa __name__ == "__main__":
    run_unittest(test_suite())
