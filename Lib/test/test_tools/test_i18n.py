"""Tests to cover the Tools/i18n package"""

agiza os
agiza sys
agiza unittest
kutoka textwrap agiza dedent

kutoka test.support.script_helper agiza assert_python_ok
kutoka test.test_tools agiza skip_if_missing, toolsdir
kutoka test.support agiza temp_cwd, temp_dir


skip_if_missing()


kundi Test_pygettext(unittest.TestCase):
    """Tests kila the pygettext.py tool"""

    script = os.path.join(toolsdir,'i18n', 'pygettext.py')

    eleza get_header(self, data):
        """ utility: rudisha the header of a .po file kama a dictionary """
        headers = {}
        kila line kwenye data.split('\n'):
            ikiwa sio line ama line.startswith(('#', 'msgid','msgstr')):
                endelea
            line = line.strip('"')
            key, val = line.split(':',1)
            headers[key] = val.strip()
        rudisha headers

    eleza get_msgids(self, data):
        """ utility: rudisha all msgids kwenye .po file kama a list of strings """
        msgids = []
        reading_msgid = Uongo
        cur_msgid = []
        kila line kwenye data.split('\n'):
            ikiwa reading_msgid:
                ikiwa line.startswith('"'):
                    cur_msgid.append(line.strip('"'))
                isipokua:
                    msgids.append('\n'.join(cur_msgid))
                    cur_msgid = []
                    reading_msgid = Uongo
                    endelea
            ikiwa line.startswith('msgid '):
                line = line[len('msgid '):]
                cur_msgid.append(line.strip('"'))
                reading_msgid = Kweli
        isipokua:
            ikiwa reading_msgid:
                msgids.append('\n'.join(cur_msgid))

        rudisha msgids

    eleza extract_docstrings_kutoka_str(self, module_content):
        """ utility: rudisha all msgids extracted kutoka module_content """
        filename = 'test_docstrings.py'
        with temp_cwd(Tupu) kama cwd:
            with open(filename, 'w') kama fp:
                fp.write(module_content)
            assert_python_ok(self.script, '-D', filename)
            with open('messages.pot') kama fp:
                data = fp.read()
        rudisha self.get_msgids(data)

    eleza test_header(self):
        """Make sure the required fields are kwenye the header, according to:
           http://www.gnu.org/software/gettext/manual/gettext.html#Header-Entry
        """
        with temp_cwd(Tupu) kama cwd:
            assert_python_ok(self.script)
            with open('messages.pot') kama fp:
                data = fp.read()
            header = self.get_header(data)

            self.assertIn("Project-Id-Version", header)
            self.assertIn("POT-Creation-Date", header)
            self.assertIn("PO-Revision-Date", header)
            self.assertIn("Last-Translator", header)
            self.assertIn("Language-Team", header)
            self.assertIn("MIME-Version", header)
            self.assertIn("Content-Type", header)
            self.assertIn("Content-Transfer-Encoding", header)
            self.assertIn("Generated-By", header)

            # sio clear ikiwa these should be required kwenye POT (template) files
            #self.assertIn("Report-Msgid-Bugs-To", header)
            #self.assertIn("Language", header)

            #"Plural-Forms" ni optional

    @unittest.skipIf(sys.platform.startswith('aix'),
                     'bpo-29972: broken test on AIX')
    eleza test_POT_Creation_Date(self):
        """ Match the date format kutoka xgettext kila POT-Creation-Date """
        kutoka datetime agiza datetime
        with temp_cwd(Tupu) kama cwd:
            assert_python_ok(self.script)
            with open('messages.pot') kama fp:
                data = fp.read()
            header = self.get_header(data)
            creationDate = header['POT-Creation-Date']

            # peel off the escaped newline at the end of string
            ikiwa creationDate.endswith('\\n'):
                creationDate = creationDate[:-len('\\n')]

            # This will ashiria ikiwa the date format does sio exactly match.
            datetime.strptime(creationDate, '%Y-%m-%d %H:%M%z')

    eleza test_funcdocstring(self):
        kila doc kwenye ('"""doc"""', "r'''doc'''", "R'doc'", 'u"doc"'):
            with self.subTest(doc):
                msgids = self.extract_docstrings_kutoka_str(dedent('''\
                eleza foo(bar):
                    %s
                ''' % doc))
                self.assertIn('doc', msgids)

    eleza test_funcdocstring_bytes(self):
        msgids = self.extract_docstrings_kutoka_str(dedent('''\
        eleza foo(bar):
            b"""doc"""
        '''))
        self.assertUongo([msgid kila msgid kwenye msgids ikiwa 'doc' kwenye msgid])

    eleza test_funcdocstring_fstring(self):
        msgids = self.extract_docstrings_kutoka_str(dedent('''\
        eleza foo(bar):
            f"""doc"""
        '''))
        self.assertUongo([msgid kila msgid kwenye msgids ikiwa 'doc' kwenye msgid])

    eleza test_classdocstring(self):
        kila doc kwenye ('"""doc"""', "r'''doc'''", "R'doc'", 'u"doc"'):
            with self.subTest(doc):
                msgids = self.extract_docstrings_kutoka_str(dedent('''\
                kundi C:
                    %s
                ''' % doc))
                self.assertIn('doc', msgids)

    eleza test_classdocstring_bytes(self):
        msgids = self.extract_docstrings_kutoka_str(dedent('''\
        kundi C:
            b"""doc"""
        '''))
        self.assertUongo([msgid kila msgid kwenye msgids ikiwa 'doc' kwenye msgid])

    eleza test_classdocstring_fstring(self):
        msgids = self.extract_docstrings_kutoka_str(dedent('''\
        kundi C:
            f"""doc"""
        '''))
        self.assertUongo([msgid kila msgid kwenye msgids ikiwa 'doc' kwenye msgid])

    eleza test_msgid(self):
        msgids = self.extract_docstrings_kutoka_str(
                '''_("""doc""" r'str' u"ing")''')
        self.assertIn('docstring', msgids)

    eleza test_msgid_bytes(self):
        msgids = self.extract_docstrings_kutoka_str('_(b"""doc""")')
        self.assertUongo([msgid kila msgid kwenye msgids ikiwa 'doc' kwenye msgid])

    eleza test_msgid_fstring(self):
        msgids = self.extract_docstrings_kutoka_str('_(f"""doc""")')
        self.assertUongo([msgid kila msgid kwenye msgids ikiwa 'doc' kwenye msgid])

    eleza test_funcdocstring_annotated_args(self):
        """ Test docstrings kila functions with annotated args """
        msgids = self.extract_docstrings_kutoka_str(dedent('''\
        eleza foo(bar: str):
            """doc"""
        '''))
        self.assertIn('doc', msgids)

    eleza test_funcdocstring_annotated_rudisha(self):
        """ Test docstrings kila functions with annotated rudisha type """
        msgids = self.extract_docstrings_kutoka_str(dedent('''\
        eleza foo(bar) -> str:
            """doc"""
        '''))
        self.assertIn('doc', msgids)

    eleza test_funcdocstring_defvalue_args(self):
        """ Test docstring kila functions with default arg values """
        msgids = self.extract_docstrings_kutoka_str(dedent('''\
        eleza foo(bar=()):
            """doc"""
        '''))
        self.assertIn('doc', msgids)

    eleza test_funcdocstring_multiple_funcs(self):
        """ Test docstring extraction kila multiple functions combining
        annotated args, annotated rudisha types na default arg values
        """
        msgids = self.extract_docstrings_kutoka_str(dedent('''\
        eleza foo1(bar: tuple=()) -> str:
            """doc1"""

        eleza foo2(bar: List[1:2]) -> (lambda x: x):
            """doc2"""

        eleza foo3(bar: 'func'=lambda x: x) -> {1: 2}:
            """doc3"""
        '''))
        self.assertIn('doc1', msgids)
        self.assertIn('doc2', msgids)
        self.assertIn('doc3', msgids)

    eleza test_classdocstring_early_colon(self):
        """ Test docstring extraction kila a kundi with colons occurring within
        the parentheses.
        """
        msgids = self.extract_docstrings_kutoka_str(dedent('''\
        kundi D(L[1:2], F({1: 2}), metaclass=M(lambda x: x)):
            """doc"""
        '''))
        self.assertIn('doc', msgids)

    eleza test_files_list(self):
        """Make sure the directories are inspected kila source files
           bpo-31920
        """
        text1 = 'Text to translate1'
        text2 = 'Text to translate2'
        text3 = 'Text to ignore'
        with temp_cwd(Tupu), temp_dir(Tupu) kama sdir:
            os.mkdir(os.path.join(sdir, 'pypkg'))
            with open(os.path.join(sdir, 'pypkg', 'pymod.py'), 'w') kama sfile:
                sfile.write(f'_({text1!r})')
            os.mkdir(os.path.join(sdir, 'pkg.py'))
            with open(os.path.join(sdir, 'pkg.py', 'pymod2.py'), 'w') kama sfile:
                sfile.write(f'_({text2!r})')
            os.mkdir(os.path.join(sdir, 'CVS'))
            with open(os.path.join(sdir, 'CVS', 'pymod3.py'), 'w') kama sfile:
                sfile.write(f'_({text3!r})')
            assert_python_ok(self.script, sdir)
            with open('messages.pot') kama fp:
                data = fp.read()
            self.assertIn(f'msgid "{text1}"', data)
            self.assertIn(f'msgid "{text2}"', data)
            self.assertNotIn(text3, data)
