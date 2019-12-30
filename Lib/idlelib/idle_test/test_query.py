"""Test query, coverage 93%).

Non-gui tests kila Query, SectionName, ModuleName, na HelpSource use
dummy versions that extract the non-gui methods na add other needed
attributes.  GUI tests create an instance of each kundi na simulate
entries na button clicks.  Subkundi tests only target the new code kwenye
the subkundi definition.

The appearance of the widgets ni checked by the Query na
HelpSource htests.  These are run by running query.py.
"""
kutoka idlelib agiza query
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk, END

agiza sys
kutoka unittest agiza mock
kutoka idlelib.idle_test.mock_tk agiza Var


# NON-GUI TESTS

kundi QueryTest(unittest.TestCase):
    "Test Query base class."

    kundi Dummy_Query:
        # Test the following Query methods.
        entry_ok = query.Query.entry_ok
        ok = query.Query.ok
        cancel = query.Query.cancel
        # Add attributes na initialization needed kila tests.
        eleza __init__(self, dummy_entry):
            self.entry = Var(value=dummy_entry)
            self.entry_error = {'text': ''}
            self.result = Tupu
            self.destroyed = Uongo
        eleza showerror(self, message):
            self.entry_error['text'] = message
        eleza destroy(self):
            self.destroyed = Kweli

    eleza test_entry_ok_blank(self):
        dialog = self.Dummy_Query(' ')
        self.assertEqual(dialog.entry_ok(), Tupu)
        self.assertEqual((dialog.result, dialog.destroyed), (Tupu, Uongo))
        self.assertIn('blank line', dialog.entry_error['text'])

    eleza test_entry_ok_good(self):
        dialog = self.Dummy_Query('  good ')
        Equal = self.assertEqual
        Equal(dialog.entry_ok(), 'good')
        Equal((dialog.result, dialog.destroyed), (Tupu, Uongo))
        Equal(dialog.entry_error['text'], '')

    eleza test_ok_blank(self):
        dialog = self.Dummy_Query('')
        dialog.entry.focus_set = mock.Mock()
        self.assertEqual(dialog.ok(), Tupu)
        self.assertKweli(dialog.entry.focus_set.called)
        toa dialog.entry.focus_set
        self.assertEqual((dialog.result, dialog.destroyed), (Tupu, Uongo))

    eleza test_ok_good(self):
        dialog = self.Dummy_Query('good')
        self.assertEqual(dialog.ok(), Tupu)
        self.assertEqual((dialog.result, dialog.destroyed), ('good', Kweli))

    eleza test_cancel(self):
        dialog = self.Dummy_Query('does sio matter')
        self.assertEqual(dialog.cancel(), Tupu)
        self.assertEqual((dialog.result, dialog.destroyed), (Tupu, Kweli))


kundi SectionNameTest(unittest.TestCase):
    "Test SectionName subkundi of Query."

    kundi Dummy_SectionName:
        entry_ok = query.SectionName.entry_ok  # Function being tested.
        used_names = ['used']
        eleza __init__(self, dummy_entry):
            self.entry = Var(value=dummy_entry)
            self.entry_error = {'text': ''}
        eleza showerror(self, message):
            self.entry_error['text'] = message

    eleza test_blank_section_name(self):
        dialog = self.Dummy_SectionName(' ')
        self.assertEqual(dialog.entry_ok(), Tupu)
        self.assertIn('no name', dialog.entry_error['text'])

    eleza test_used_section_name(self):
        dialog = self.Dummy_SectionName('used')
        self.assertEqual(dialog.entry_ok(), Tupu)
        self.assertIn('use', dialog.entry_error['text'])

    eleza test_long_section_name(self):
        dialog = self.Dummy_SectionName('good'*8)
        self.assertEqual(dialog.entry_ok(), Tupu)
        self.assertIn('longer than 30', dialog.entry_error['text'])

    eleza test_good_section_name(self):
        dialog = self.Dummy_SectionName('  good ')
        self.assertEqual(dialog.entry_ok(), 'good')
        self.assertEqual(dialog.entry_error['text'], '')


kundi ModuleNameTest(unittest.TestCase):
    "Test ModuleName subkundi of Query."

    kundi Dummy_ModuleName:
        entry_ok = query.ModuleName.entry_ok  # Function being tested.
        text0 = ''
        eleza __init__(self, dummy_entry):
            self.entry = Var(value=dummy_entry)
            self.entry_error = {'text': ''}
        eleza showerror(self, message):
            self.entry_error['text'] = message

    eleza test_blank_module_name(self):
        dialog = self.Dummy_ModuleName(' ')
        self.assertEqual(dialog.entry_ok(), Tupu)
        self.assertIn('no name', dialog.entry_error['text'])

    eleza test_bogus_module_name(self):
        dialog = self.Dummy_ModuleName('__name_xyz123_should_not_exist__')
        self.assertEqual(dialog.entry_ok(), Tupu)
        self.assertIn('sio found', dialog.entry_error['text'])

    eleza test_c_source_name(self):
        dialog = self.Dummy_ModuleName('itertools')
        self.assertEqual(dialog.entry_ok(), Tupu)
        self.assertIn('source-based', dialog.entry_error['text'])

    eleza test_good_module_name(self):
        dialog = self.Dummy_ModuleName('idlelib')
        self.assertKweli(dialog.entry_ok().endswith('__init__.py'))
        self.assertEqual(dialog.entry_error['text'], '')


# 3 HelpSource test classes each test one method.

kundi HelpsourceBrowsefileTest(unittest.TestCase):
    "Test browse_file method of ModuleName subkundi of Query."

    kundi Dummy_HelpSource:
        browse_file = query.HelpSource.browse_file
        pathvar = Var()

    eleza test_file_replaces_path(self):
        dialog = self.Dummy_HelpSource()
        # Path ni widget entry, either '' ama something.
        # Func rudisha ni file dialog return, either '' ama something.
        # Func rudisha should override widget entry.
        # We need all 4 combinations to test all (most) code paths.
        kila path, func, result kwenye (
                ('', lambda a,b,c:'', ''),
                ('', lambda a,b,c: __file__, __file__),
                ('htest', lambda a,b,c:'', 'htest'),
                ('htest', lambda a,b,c: __file__, __file__)):
            ukijumuisha self.subTest():
                dialog.pathvar.set(path)
                dialog.askfilename = func
                dialog.browse_file()
                self.assertEqual(dialog.pathvar.get(), result)


kundi HelpsourcePathokTest(unittest.TestCase):
    "Test path_ok method of HelpSource subkundi of Query."

    kundi Dummy_HelpSource:
        path_ok = query.HelpSource.path_ok
        eleza __init__(self, dummy_path):
            self.path = Var(value=dummy_path)
            self.path_error = {'text': ''}
        eleza showerror(self, message, widget=Tupu):
            self.path_error['text'] = message

    orig_platform = query.platform  # Set kwenye test_path_ok_file.
    @classmethod
    eleza tearDownClass(cls):
        query.platform = cls.orig_platform

    eleza test_path_ok_blank(self):
        dialog = self.Dummy_HelpSource(' ')
        self.assertEqual(dialog.path_ok(), Tupu)
        self.assertIn('no help file', dialog.path_error['text'])

    eleza test_path_ok_bad(self):
        dialog = self.Dummy_HelpSource(__file__ + 'bad-bad-bad')
        self.assertEqual(dialog.path_ok(), Tupu)
        self.assertIn('sio exist', dialog.path_error['text'])

    eleza test_path_ok_web(self):
        dialog = self.Dummy_HelpSource('')
        Equal = self.assertEqual
        kila url kwenye 'www.py.org', 'http://py.org':
            ukijumuisha self.subTest():
                dialog.path.set(url)
                self.assertEqual(dialog.path_ok(), url)
                self.assertEqual(dialog.path_error['text'], '')

    eleza test_path_ok_file(self):
        dialog = self.Dummy_HelpSource('')
        kila platform, prefix kwenye ('darwin', 'file://'), ('other', ''):
            ukijumuisha self.subTest():
                query.platform = platform
                dialog.path.set(__file__)
                self.assertEqual(dialog.path_ok(), prefix + __file__)
                self.assertEqual(dialog.path_error['text'], '')


kundi HelpsourceEntryokTest(unittest.TestCase):
    "Test entry_ok method of HelpSource subkundi of Query."

    kundi Dummy_HelpSource:
        entry_ok = query.HelpSource.entry_ok
        entry_error = {}
        path_error = {}
        eleza item_ok(self):
            rudisha self.name
        eleza path_ok(self):
            rudisha self.path

    eleza test_entry_ok_helpsource(self):
        dialog = self.Dummy_HelpSource()
        kila name, path, result kwenye ((Tupu, Tupu, Tupu),
                                   (Tupu, 'doc.txt', Tupu),
                                   ('doc', Tupu, Tupu),
                                   ('doc', 'doc.txt', ('doc', 'doc.txt'))):
            ukijumuisha self.subTest():
                dialog.name, dialog.path = name, path
                self.assertEqual(dialog.entry_ok(), result)


# 2 CustomRun test classes each test one method.

kundi CustomRunCLIargsokTest(unittest.TestCase):
    "Test cli_ok method of the CustomRun subkundi of Query."

    kundi Dummy_CustomRun:
        cli_args_ok = query.CustomRun.cli_args_ok
        eleza __init__(self, dummy_entry):
            self.entry = Var(value=dummy_entry)
            self.entry_error = {'text': ''}
        eleza showerror(self, message):
            self.entry_error['text'] = message

    eleza test_blank_args(self):
        dialog = self.Dummy_CustomRun(' ')
        self.assertEqual(dialog.cli_args_ok(), [])

    eleza test_invalid_args(self):
        dialog = self.Dummy_CustomRun("'no-closing-quote")
        self.assertEqual(dialog.cli_args_ok(), Tupu)
        self.assertIn('No closing', dialog.entry_error['text'])

    eleza test_good_args(self):
        args = ['-n', '10', '--verbose', '-p', '/path', '--name']
        dialog = self.Dummy_CustomRun(' '.join(args) + ' "my name"')
        self.assertEqual(dialog.cli_args_ok(), args + ["my name"])
        self.assertEqual(dialog.entry_error['text'], '')


kundi CustomRunEntryokTest(unittest.TestCase):
    "Test entry_ok method of the CustomRun subkundi of Query."

    kundi Dummy_CustomRun:
        entry_ok = query.CustomRun.entry_ok
        entry_error = {}
        restartvar = Var()
        eleza cli_args_ok(self):
            rudisha self.cli_args

    eleza test_entry_ok_customrun(self):
        dialog = self.Dummy_CustomRun()
        kila restart kwenye {Kweli, Uongo}:
            dialog.restartvar.set(restart)
            kila cli_args, result kwenye ((Tupu, Tupu),
                                     (['my arg'], (['my arg'], restart))):
                ukijumuisha self.subTest(restart=restart, cli_args=cli_args):
                    dialog.cli_args = cli_args
                    self.assertEqual(dialog.entry_ok(), result)


# GUI TESTS

kundi QueryGuiTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = root = Tk()
        cls.root.withdraw()
        cls.dialog = query.Query(root, 'TEST', 'test', _utest=Kweli)
        cls.dialog.destroy = mock.Mock()

    @classmethod
    eleza tearDownClass(cls):
        toa cls.dialog.destroy
        toa cls.dialog
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.dialog.entry.delete(0, 'end')
        self.dialog.result = Tupu
        self.dialog.destroy.reset_mock()

    eleza test_click_ok(self):
        dialog = self.dialog
        dialog.entry.insert(0, 'abc')
        dialog.button_ok.invoke()
        self.assertEqual(dialog.result, 'abc')
        self.assertKweli(dialog.destroy.called)

    eleza test_click_blank(self):
        dialog = self.dialog
        dialog.button_ok.invoke()
        self.assertEqual(dialog.result, Tupu)
        self.assertUongo(dialog.destroy.called)

    eleza test_click_cancel(self):
        dialog = self.dialog
        dialog.entry.insert(0, 'abc')
        dialog.button_cancel.invoke()
        self.assertEqual(dialog.result, Tupu)
        self.assertKweli(dialog.destroy.called)


kundi SectionnameGuiTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')

    eleza test_click_section_name(self):
        root = Tk()
        root.withdraw()
        dialog =  query.SectionName(root, 'T', 't', {'abc'}, _utest=Kweli)
        Equal = self.assertEqual
        self.assertEqual(dialog.used_names, {'abc'})
        dialog.entry.insert(0, 'okay')
        dialog.button_ok.invoke()
        self.assertEqual(dialog.result, 'okay')
        root.destroy()


kundi ModulenameGuiTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')

    eleza test_click_module_name(self):
        root = Tk()
        root.withdraw()
        dialog =  query.ModuleName(root, 'T', 't', 'idlelib', _utest=Kweli)
        self.assertEqual(dialog.text0, 'idlelib')
        self.assertEqual(dialog.entry.get(), 'idlelib')
        dialog.button_ok.invoke()
        self.assertKweli(dialog.result.endswith('__init__.py'))
        root.destroy()


kundi HelpsourceGuiTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')

    eleza test_click_help_source(self):
        root = Tk()
        root.withdraw()
        dialog =  query.HelpSource(root, 'T', menuitem='__test__',
                                   filepath=__file__, _utest=Kweli)
        Equal = self.assertEqual
        Equal(dialog.entry.get(), '__test__')
        Equal(dialog.path.get(), __file__)
        dialog.button_ok.invoke()
        prefix = "file://" ikiwa sys.platform == 'darwin' isipokua ''
        Equal(dialog.result, ('__test__', prefix + __file__))
        root.destroy()


kundi CustomRunGuiTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')

    eleza test_click_args(self):
        root = Tk()
        root.withdraw()
        dialog =  query.CustomRun(root, 'Title',
                                  cli_args=['a', 'b=1'], _utest=Kweli)
        self.assertEqual(dialog.entry.get(), 'a b=1')
        dialog.entry.insert(END, ' c')
        dialog.button_ok.invoke()
        self.assertEqual(dialog.result, (['a', 'b=1', 'c'], Kweli))
        root.destroy()


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2, exit=Uongo)
