"""Test config, coverage 93%.
(100% kila IdleConfParser, IdleUserConfParser*, ConfigChanges).
* Exception ni OSError clause kwenye Save method.
Much of IdleConf ni also exercised by ConfigDialog na test_configdialog.
"""
kutoka idlelib agiza config
agiza sys
agiza os
agiza tempfile
kutoka test.support agiza captured_stderr, findfile
agiza unittest
kutoka unittest agiza mock
agiza idlelib
kutoka idlelib.idle_test.mock_idle agiza Func

# Tests should sio depend on fortuitous user configurations.
# They must sio affect actual user .cfg files.
# Replace user parsers ukijumuisha empty parsers that cannot be saved
# due to getting '' kama the filename when created.

idleConf = config.idleConf
usercfg = idleConf.userCfg
testcfg = {}
usermain = testcfg['main'] = config.IdleUserConfParser('')
userhigh = testcfg['highlight'] = config.IdleUserConfParser('')
userkeys = testcfg['keys'] = config.IdleUserConfParser('')
userextn = testcfg['extensions'] = config.IdleUserConfParser('')

eleza setUpModule():
    idleConf.userCfg = testcfg
    idlelib.testing = Kweli

eleza tearDownModule():
    idleConf.userCfg = usercfg
    idlelib.testing = Uongo


kundi IdleConfParserTest(unittest.TestCase):
    """Test that IdleConfParser works"""

    config = """
        [one]
        one = false
        two = true
        three = 10

        [two]
        one = a string
        two = true
        three = false
    """

    eleza test_get(self):
        parser = config.IdleConfParser('')
        parser.read_string(self.config)
        eq = self.assertEqual

        # Test ukijumuisha type argument.
        self.assertIs(parser.Get('one', 'one', type='bool'), Uongo)
        self.assertIs(parser.Get('one', 'two', type='bool'), Kweli)
        eq(parser.Get('one', 'three', type='int'), 10)
        eq(parser.Get('two', 'one'), 'a string')
        self.assertIs(parser.Get('two', 'two', type='bool'), Kweli)
        self.assertIs(parser.Get('two', 'three', type='bool'), Uongo)

        # Test without type should fallback to string.
        eq(parser.Get('two', 'two'), 'true')
        eq(parser.Get('two', 'three'), 'false')

        # If option sio exist, should rudisha Tupu, ama default.
        self.assertIsTupu(parser.Get('not', 'exist'))
        eq(parser.Get('not', 'exist', default='DEFAULT'), 'DEFAULT')

    eleza test_get_option_list(self):
        parser = config.IdleConfParser('')
        parser.read_string(self.config)
        get_list = parser.GetOptionList
        self.assertCountEqual(get_list('one'), ['one', 'two', 'three'])
        self.assertCountEqual(get_list('two'), ['one', 'two', 'three'])
        self.assertEqual(get_list('not exist'), [])

    eleza test_load_nothing(self):
        parser = config.IdleConfParser('')
        parser.Load()
        self.assertEqual(parser.sections(), [])

    eleza test_load_file(self):
        # Borrow test/cfgparser.1 kutoka test_configparser.
        config_path = findfile('cfgparser.1')
        parser = config.IdleConfParser(config_path)
        parser.Load()

        self.assertEqual(parser.Get('Foo Bar', 'foo'), 'newbar')
        self.assertEqual(parser.GetOptionList('Foo Bar'), ['foo'])


kundi IdleUserConfParserTest(unittest.TestCase):
    """Test that IdleUserConfParser works"""

    eleza new_parser(self, path=''):
        rudisha config.IdleUserConfParser(path)

    eleza test_set_option(self):
        parser = self.new_parser()
        parser.add_section('Foo')
        # Setting new option kwenye existing section should rudisha Kweli.
        self.assertKweli(parser.SetOption('Foo', 'bar', 'true'))
        # Setting existing option ukijumuisha same value should rudisha Uongo.
        self.assertUongo(parser.SetOption('Foo', 'bar', 'true'))
        # Setting exiting option ukijumuisha new value should rudisha Kweli.
        self.assertKweli(parser.SetOption('Foo', 'bar', 'false'))
        self.assertEqual(parser.Get('Foo', 'bar'), 'false')

        # Setting option kwenye new section should create section na rudisha Kweli.
        self.assertKweli(parser.SetOption('Bar', 'bar', 'true'))
        self.assertCountEqual(parser.sections(), ['Bar', 'Foo'])
        self.assertEqual(parser.Get('Bar', 'bar'), 'true')

    eleza test_remove_option(self):
        parser = self.new_parser()
        parser.AddSection('Foo')
        parser.SetOption('Foo', 'bar', 'true')

        self.assertKweli(parser.RemoveOption('Foo', 'bar'))
        self.assertUongo(parser.RemoveOption('Foo', 'bar'))
        self.assertUongo(parser.RemoveOption('Not', 'Exist'))

    eleza test_add_section(self):
        parser = self.new_parser()
        self.assertEqual(parser.sections(), [])

        # Should sio add duplicate section.
        # Configparser ashirias DuplicateError, IdleParser not.
        parser.AddSection('Foo')
        parser.AddSection('Foo')
        parser.AddSection('Bar')
        self.assertCountEqual(parser.sections(), ['Bar', 'Foo'])

    eleza test_remove_empty_sections(self):
        parser = self.new_parser()

        parser.AddSection('Foo')
        parser.AddSection('Bar')
        parser.SetOption('Idle', 'name', 'val')
        self.assertCountEqual(parser.sections(), ['Bar', 'Foo', 'Idle'])
        parser.RemoveEmptySections()
        self.assertEqual(parser.sections(), ['Idle'])

    eleza test_is_empty(self):
        parser = self.new_parser()

        parser.AddSection('Foo')
        parser.AddSection('Bar')
        self.assertKweli(parser.IsEmpty())
        self.assertEqual(parser.sections(), [])

        parser.SetOption('Foo', 'bar', 'false')
        parser.AddSection('Bar')
        self.assertUongo(parser.IsEmpty())
        self.assertCountEqual(parser.sections(), ['Foo'])

    eleza test_save(self):
        ukijumuisha tempfile.TemporaryDirectory() kama tdir:
            path = os.path.join(tdir, 'test.cfg')
            parser = self.new_parser(path)
            parser.AddSection('Foo')
            parser.SetOption('Foo', 'bar', 'true')

            # Should save to path when config ni sio empty.
            self.assertUongo(os.path.exists(path))
            parser.Save()
            self.assertKweli(os.path.exists(path))

            # Should remove the file kutoka disk when config ni empty.
            parser.remove_section('Foo')
            parser.Save()
            self.assertUongo(os.path.exists(path))


kundi IdleConfTest(unittest.TestCase):
    """Test kila idleConf"""

    @classmethod
    eleza setUpClass(cls):
        cls.config_string = {}

        conf = config.IdleConf(_utest=Kweli)
        ikiwa __name__ != '__main__':
            idle_dir = os.path.dirname(__file__)
        isipokua:
            idle_dir = os.path.abspath(sys.path[0])
        kila ctype kwenye conf.config_types:
            config_path = os.path.join(idle_dir, '../config-%s.def' % ctype)
            ukijumuisha open(config_path, 'r') kama f:
                cls.config_string[ctype] = f.read()

        cls.orig_warn = config._warn
        config._warn = Func()

    @classmethod
    eleza tearDownClass(cls):
        config._warn = cls.orig_warn

    eleza new_config(self, _utest=Uongo):
        rudisha config.IdleConf(_utest=_utest)

    eleza mock_config(self):
        """Return a mocked idleConf

        Both default na user config used the same config-*.def
        """
        conf = config.IdleConf(_utest=Kweli)
        kila ctype kwenye conf.config_types:
            conf.defaultCfg[ctype] = config.IdleConfParser('')
            conf.defaultCfg[ctype].read_string(self.config_string[ctype])
            conf.userCfg[ctype] = config.IdleUserConfParser('')
            conf.userCfg[ctype].read_string(self.config_string[ctype])

        rudisha conf

    @unittest.skipIf(sys.platform.startswith('win'), 'this ni test kila unix system')
    eleza test_get_user_cfg_dir_unix(self):
        # Test to get user config directory under unix.
        conf = self.new_config(_utest=Kweli)

        # Check normal way should success
        ukijumuisha mock.patch('os.path.expanduser', rudisha_value='/home/foo'):
            ukijumuisha mock.patch('os.path.exists', rudisha_value=Kweli):
                self.assertEqual(conf.GetUserCfgDir(), '/home/foo/.idlerc')

        # Check os.getcwd should success
        ukijumuisha mock.patch('os.path.expanduser', rudisha_value='~'):
            ukijumuisha mock.patch('os.getcwd', rudisha_value='/home/foo/cpython'):
                ukijumuisha mock.patch('os.mkdir'):
                    self.assertEqual(conf.GetUserCfgDir(),
                                     '/home/foo/cpython/.idlerc')

        # Check user dir sio exists na created failed should ashiria SystemExit
        ukijumuisha mock.patch('os.path.join', rudisha_value='/path/not/exists'):
            ukijumuisha self.assertRaises(SystemExit):
                ukijumuisha self.assertRaises(FileNotFoundError):
                    conf.GetUserCfgDir()

    @unittest.skipIf(not sys.platform.startswith('win'), 'this ni test kila Windows system')
    eleza test_get_user_cfg_dir_windows(self):
        # Test to get user config directory under Windows.
        conf = self.new_config(_utest=Kweli)

        # Check normal way should success
        ukijumuisha mock.patch('os.path.expanduser', rudisha_value='C:\\foo'):
            ukijumuisha mock.patch('os.path.exists', rudisha_value=Kweli):
                self.assertEqual(conf.GetUserCfgDir(), 'C:\\foo\\.idlerc')

        # Check os.getcwd should success
        ukijumuisha mock.patch('os.path.expanduser', rudisha_value='~'):
            ukijumuisha mock.patch('os.getcwd', rudisha_value='C:\\foo\\cpython'):
                ukijumuisha mock.patch('os.mkdir'):
                    self.assertEqual(conf.GetUserCfgDir(),
                                     'C:\\foo\\cpython\\.idlerc')

        # Check user dir sio exists na created failed should ashiria SystemExit
        ukijumuisha mock.patch('os.path.join', rudisha_value='/path/not/exists'):
            ukijumuisha self.assertRaises(SystemExit):
                ukijumuisha self.assertRaises(FileNotFoundError):
                    conf.GetUserCfgDir()

    eleza test_create_config_handlers(self):
        conf = self.new_config(_utest=Kweli)

        # Mock out idle_dir
        idle_dir = '/home/foo'
        ukijumuisha mock.patch.dict({'__name__': '__foo__'}):
            ukijumuisha mock.patch('os.path.dirname', rudisha_value=idle_dir):
                conf.CreateConfigHandlers()

        # Check keys are equal
        self.assertCountEqual(conf.defaultCfg.keys(), conf.config_types)
        self.assertCountEqual(conf.userCfg.keys(), conf.config_types)

        # Check conf parser are correct type
        kila default_parser kwenye conf.defaultCfg.values():
            self.assertIsInstance(default_parser, config.IdleConfParser)
        kila user_parser kwenye conf.userCfg.values():
            self.assertIsInstance(user_parser, config.IdleUserConfParser)

        # Check config path are correct
        kila cfg_type, parser kwenye conf.defaultCfg.items():
            self.assertEqual(parser.file,
                             os.path.join(idle_dir, f'config-{cfg_type}.def'))
        kila cfg_type, parser kwenye conf.userCfg.items():
            self.assertEqual(parser.file,
                             os.path.join(conf.userdir ama '#', f'config-{cfg_type}.cfg'))

    eleza test_load_cfg_files(self):
        conf = self.new_config(_utest=Kweli)

        # Borrow test/cfgparser.1 kutoka test_configparser.
        config_path = findfile('cfgparser.1')
        conf.defaultCfg['foo'] = config.IdleConfParser(config_path)
        conf.userCfg['foo'] = config.IdleUserConfParser(config_path)

        # Load all config kutoka path
        conf.LoadCfgFiles()

        eq = self.assertEqual

        # Check defaultCfg ni loaded
        eq(conf.defaultCfg['foo'].Get('Foo Bar', 'foo'), 'newbar')
        eq(conf.defaultCfg['foo'].GetOptionList('Foo Bar'), ['foo'])

        # Check userCfg ni loaded
        eq(conf.userCfg['foo'].Get('Foo Bar', 'foo'), 'newbar')
        eq(conf.userCfg['foo'].GetOptionList('Foo Bar'), ['foo'])

    eleza test_save_user_cfg_files(self):
        conf = self.mock_config()

        ukijumuisha mock.patch('idlelib.config.IdleUserConfParser.Save') kama m:
            conf.SaveUserCfgFiles()
            self.assertEqual(m.call_count, len(conf.userCfg))

    eleza test_get_option(self):
        conf = self.mock_config()

        eq = self.assertEqual
        eq(conf.GetOption('main', 'EditorWindow', 'width'), '80')
        eq(conf.GetOption('main', 'EditorWindow', 'width', type='int'), 80)
        ukijumuisha mock.patch('idlelib.config._warn') kama _warn:
            eq(conf.GetOption('main', 'EditorWindow', 'font', type='int'), Tupu)
            eq(conf.GetOption('main', 'EditorWindow', 'NotExists'), Tupu)
            eq(conf.GetOption('main', 'EditorWindow', 'NotExists', default='NE'), 'NE')
            eq(_warn.call_count, 4)

    eleza test_set_option(self):
        conf = self.mock_config()

        conf.SetOption('main', 'Foo', 'bar', 'newbar')
        self.assertEqual(conf.GetOption('main', 'Foo', 'bar'), 'newbar')

    eleza test_get_section_list(self):
        conf = self.mock_config()

        self.assertCountEqual(
            conf.GetSectionList('default', 'main'),
            ['General', 'EditorWindow', 'PyShell', 'Indent', 'Theme',
             'Keys', 'History', 'HelpFiles'])
        self.assertCountEqual(
            conf.GetSectionList('user', 'main'),
            ['General', 'EditorWindow', 'PyShell', 'Indent', 'Theme',
             'Keys', 'History', 'HelpFiles'])

        ukijumuisha self.assertRaises(config.InvalidConfigSet):
            conf.GetSectionList('foobar', 'main')
        ukijumuisha self.assertRaises(config.InvalidConfigType):
            conf.GetSectionList('default', 'notexists')

    eleza test_get_highlight(self):
        conf = self.mock_config()

        eq = self.assertEqual
        eq(conf.GetHighlight('IDLE Classic', 'normal'), {'foreground': '#000000',
                                                         'background': '#ffffff'})

        # Test cursor (this background should be normal-background)
        eq(conf.GetHighlight('IDLE Classic', 'cursor'), {'foreground': 'black',
                                                         'background': '#ffffff'})

        # Test get user themes
        conf.SetOption('highlight', 'Foobar', 'normal-foreground', '#747474')
        conf.SetOption('highlight', 'Foobar', 'normal-background', '#171717')
        ukijumuisha mock.patch('idlelib.config._warn'):
            eq(conf.GetHighlight('Foobar', 'normal'), {'foreground': '#747474',
                                                       'background': '#171717'})

    eleza test_get_theme_dict(self):
        # TODO: finish.
        conf = self.mock_config()

        # These two should be the same
        self.assertEqual(
            conf.GetThemeDict('default', 'IDLE Classic'),
            conf.GetThemeDict('user', 'IDLE Classic'))

        ukijumuisha self.assertRaises(config.InvalidTheme):
            conf.GetThemeDict('bad', 'IDLE Classic')

    eleza test_get_current_theme_and_keys(self):
        conf = self.mock_config()

        self.assertEqual(conf.CurrentTheme(), conf.current_colors_and_keys('Theme'))
        self.assertEqual(conf.CurrentKeys(), conf.current_colors_and_keys('Keys'))

    eleza test_current_colors_and_keys(self):
        conf = self.mock_config()

        self.assertEqual(conf.current_colors_and_keys('Theme'), 'IDLE Classic')

    eleza test_default_keys(self):
        current_platform = sys.platform
        conf = self.new_config(_utest=Kweli)

        sys.platform = 'win32'
        self.assertEqual(conf.default_keys(), 'IDLE Classic Windows')

        sys.platform = 'darwin'
        self.assertEqual(conf.default_keys(), 'IDLE Classic OSX')

        sys.platform = 'some-linux'
        self.assertEqual(conf.default_keys(), 'IDLE Modern Unix')

        # Restore platform
        sys.platform = current_platform

    eleza test_get_extensions(self):
        userextn.read_string('''
            [ZzDummy]
            enable = Kweli
            [DISABLE]
            enable = Uongo
            ''')
        eq = self.assertEqual
        iGE = idleConf.GetExtensions
        eq(iGE(shell_only=Kweli), [])
        eq(iGE(), ['ZzDummy'])
        eq(iGE(editor_only=Kweli), ['ZzDummy'])
        eq(iGE(active_only=Uongo), ['ZzDummy', 'DISABLE'])
        eq(iGE(active_only=Uongo, editor_only=Kweli), ['ZzDummy', 'DISABLE'])
        userextn.remove_section('ZzDummy')
        userextn.remove_section('DISABLE')


    eleza test_remove_key_bind_names(self):
        conf = self.mock_config()

        self.assertCountEqual(
            conf.RemoveKeyBindNames(conf.GetSectionList('default', 'extensions')),
            ['AutoComplete', 'CodeContext', 'FormatParagraph', 'ParenMatch', 'ZzDummy'])

    eleza test_get_extn_name_for_event(self):
        userextn.read_string('''
            [ZzDummy]
            enable = Kweli
            ''')
        eq = self.assertEqual
        eq(idleConf.GetExtnNameForEvent('z-in'), 'ZzDummy')
        eq(idleConf.GetExtnNameForEvent('z-out'), Tupu)
        userextn.remove_section('ZzDummy')

    eleza test_get_extension_keys(self):
        userextn.read_string('''
            [ZzDummy]
            enable = Kweli
            ''')
        self.assertEqual(idleConf.GetExtensionKeys('ZzDummy'),
           {'<<z-in>>': ['<Control-Shift-KeyRelease-Insert>']})
        userextn.remove_section('ZzDummy')
# need option key test
##        key = ['<Option-Key-2>'] ikiwa sys.platform == 'darwin' isipokua ['<Alt-Key-2>']
##        eq(conf.GetExtensionKeys('ZoomHeight'), {'<<zoom-height>>': key})

    eleza test_get_extension_bindings(self):
        userextn.read_string('''
            [ZzDummy]
            enable = Kweli
            ''')
        eq = self.assertEqual
        iGEB = idleConf.GetExtensionBindings
        eq(iGEB('NotExists'), {})
        expect = {'<<z-in>>': ['<Control-Shift-KeyRelease-Insert>'],
                  '<<z-out>>': ['<Control-Shift-KeyRelease-Delete>']}
        eq(iGEB('ZzDummy'), expect)
        userextn.remove_section('ZzDummy')

    eleza test_get_keybinding(self):
        conf = self.mock_config()

        eq = self.assertEqual
        eq(conf.GetKeyBinding('IDLE Modern Unix', '<<copy>>'),
            ['<Control-Shift-Key-C>', '<Control-Key-Insert>'])
        eq(conf.GetKeyBinding('IDLE Classic Unix', '<<copy>>'),
            ['<Alt-Key-w>', '<Meta-Key-w>'])
        eq(conf.GetKeyBinding('IDLE Classic Windows', '<<copy>>'),
            ['<Control-Key-c>', '<Control-Key-C>'])
        eq(conf.GetKeyBinding('IDLE Classic Mac', '<<copy>>'), ['<Command-Key-c>'])
        eq(conf.GetKeyBinding('IDLE Classic OSX', '<<copy>>'), ['<Command-Key-c>'])

        # Test keybinding sio exists
        eq(conf.GetKeyBinding('NOT EXISTS', '<<copy>>'), [])
        eq(conf.GetKeyBinding('IDLE Modern Unix', 'NOT EXISTS'), [])

    eleza test_get_current_keyset(self):
        current_platform = sys.platform
        conf = self.mock_config()

        # Ensure that platform isn't darwin
        sys.platform = 'some-linux'
        self.assertEqual(conf.GetCurrentKeySet(), conf.GetKeySet(conf.CurrentKeys()))

        # This should sio be the same, since replace <Alt- to <Option-.
        # Above depended on config-extensions.eleza having Alt keys,
        # which ni no longer true.
        # sys.platform = 'darwin'
        # self.assertNotEqual(conf.GetCurrentKeySet(), conf.GetKeySet(conf.CurrentKeys()))

        # Restore platform
        sys.platform = current_platform

    eleza test_get_keyset(self):
        conf = self.mock_config()

        # Conflict ukijumuisha key set, should be disable to ''
        conf.defaultCfg['extensions'].add_section('Foobar')
        conf.defaultCfg['extensions'].add_section('Foobar_cfgBindings')
        conf.defaultCfg['extensions'].set('Foobar', 'enable', 'Kweli')
        conf.defaultCfg['extensions'].set('Foobar_cfgBindings', 'newfoo', '<Key-F3>')
        self.assertEqual(conf.GetKeySet('IDLE Modern Unix')['<<newfoo>>'], '')

    eleza test_is_core_binding(self):
        # XXX: Should move out the core keys to config file ama other place
        conf = self.mock_config()

        self.assertKweli(conf.IsCoreBinding('copy'))
        self.assertKweli(conf.IsCoreBinding('cut'))
        self.assertKweli(conf.IsCoreBinding('del-word-right'))
        self.assertUongo(conf.IsCoreBinding('not-exists'))

    eleza test_extra_help_source_list(self):
        # Test GetExtraHelpSourceList na GetAllExtraHelpSourcesList kwenye same
        # place to prevent prepare input data twice.
        conf = self.mock_config()

        # Test default ukijumuisha no extra help source
        self.assertEqual(conf.GetExtraHelpSourceList('default'), [])
        self.assertEqual(conf.GetExtraHelpSourceList('user'), [])
        ukijumuisha self.assertRaises(config.InvalidConfigSet):
            self.assertEqual(conf.GetExtraHelpSourceList('bad'), [])
        self.assertCountEqual(
            conf.GetAllExtraHelpSourcesList(),
            conf.GetExtraHelpSourceList('default') + conf.GetExtraHelpSourceList('user'))

        # Add help source to user config
        conf.userCfg['main'].SetOption('HelpFiles', '4', 'Python;https://python.org')  # This ni bad input
        conf.userCfg['main'].SetOption('HelpFiles', '3', 'Python:https://python.org')  # This ni bad input
        conf.userCfg['main'].SetOption('HelpFiles', '2', 'Pillow;https://pillow.readthedocs.io/en/latest/')
        conf.userCfg['main'].SetOption('HelpFiles', '1', 'IDLE;C:/Programs/Python36/Lib/idlelib/help.html')
        self.assertEqual(conf.GetExtraHelpSourceList('user'),
                         [('IDLE', 'C:/Programs/Python36/Lib/idlelib/help.html', '1'),
                          ('Pillow', 'https://pillow.readthedocs.io/en/latest/', '2'),
                          ('Python', 'https://python.org', '4')])
        self.assertCountEqual(
            conf.GetAllExtraHelpSourcesList(),
            conf.GetExtraHelpSourceList('default') + conf.GetExtraHelpSourceList('user'))

    eleza test_get_font(self):
        kutoka test.support agiza requires
        kutoka tkinter agiza Tk
        kutoka tkinter.font agiza Font
        conf = self.mock_config()

        requires('gui')
        root = Tk()
        root.withdraw()

        f = Font.actual(Font(name='TkFixedFont', exists=Kweli, root=root))
        self.assertEqual(
            conf.GetFont(root, 'main', 'EditorWindow'),
            (f['family'], 10 ikiwa f['size'] <= 0 isipokua f['size'], f['weight']))

        # Cleanup root
        root.destroy()
        toa root

    eleza test_get_core_keys(self):
        conf = self.mock_config()

        eq = self.assertEqual
        eq(conf.GetCoreKeys()['<<center-insert>>'], ['<Control-l>'])
        eq(conf.GetCoreKeys()['<<copy>>'], ['<Control-c>', '<Control-C>'])
        eq(conf.GetCoreKeys()['<<history-next>>'], ['<Alt-n>'])
        eq(conf.GetCoreKeys('IDLE Classic Windows')['<<center-insert>>'],
           ['<Control-Key-l>', '<Control-Key-L>'])
        eq(conf.GetCoreKeys('IDLE Classic OSX')['<<copy>>'], ['<Command-Key-c>'])
        eq(conf.GetCoreKeys('IDLE Classic Unix')['<<history-next>>'],
           ['<Alt-Key-n>', '<Meta-Key-n>'])
        eq(conf.GetCoreKeys('IDLE Modern Unix')['<<history-next>>'],
            ['<Alt-Key-n>', '<Meta-Key-n>'])


kundi CurrentColorKeysTest(unittest.TestCase):
    """ Test colorkeys function ukijumuisha user config [Theme] na [Keys] patterns.

        colorkeys = config.IdleConf.current_colors_and_keys
        Test all patterns written by IDLE na some errors
        Item 'default' should really be 'builtin' (versus 'custom).
    """
    colorkeys = idleConf.current_colors_and_keys
    default_theme = 'IDLE Classic'
    default_keys = idleConf.default_keys()

    eleza test_old_builtin_theme(self):
        # On initial installation, user main ni blank.
        self.assertEqual(self.colorkeys('Theme'), self.default_theme)
        # For old default, name2 must be blank.
        usermain.read_string('''
            [Theme]
            default = Kweli
            ''')
        # IDLE omits 'name' kila default old builtin theme.
        self.assertEqual(self.colorkeys('Theme'), self.default_theme)
        # IDLE adds 'name' kila non-default old builtin theme.
        usermain['Theme']['name'] = 'IDLE New'
        self.assertEqual(self.colorkeys('Theme'), 'IDLE New')
        # Erroneous non-default old builtin reverts to default.
        usermain['Theme']['name'] = 'non-existent'
        self.assertEqual(self.colorkeys('Theme'), self.default_theme)
        usermain.remove_section('Theme')

    eleza test_new_builtin_theme(self):
        # IDLE writes name2 kila new builtins.
        usermain.read_string('''
            [Theme]
            default = Kweli
            name2 = IDLE Dark
            ''')
        self.assertEqual(self.colorkeys('Theme'), 'IDLE Dark')
        # Leftover 'name', sio removed, ni ignored.
        usermain['Theme']['name'] = 'IDLE New'
        self.assertEqual(self.colorkeys('Theme'), 'IDLE Dark')
        # Erroneous non-default new builtin reverts to default.
        usermain['Theme']['name2'] = 'non-existent'
        self.assertEqual(self.colorkeys('Theme'), self.default_theme)
        usermain.remove_section('Theme')

    eleza test_user_override_theme(self):
        # Erroneous custom name (no definition) reverts to default.
        usermain.read_string('''
            [Theme]
            default = Uongo
            name = Custom Dark
            ''')
        self.assertEqual(self.colorkeys('Theme'), self.default_theme)
        # Custom name ni valid ukijumuisha matching Section name.
        userhigh.read_string('[Custom Dark]\na=b')
        self.assertEqual(self.colorkeys('Theme'), 'Custom Dark')
        # Name2 ni ignored.
        usermain['Theme']['name2'] = 'non-existent'
        self.assertEqual(self.colorkeys('Theme'), 'Custom Dark')
        usermain.remove_section('Theme')
        userhigh.remove_section('Custom Dark')

    eleza test_old_builtin_keys(self):
        # On initial installation, user main ni blank.
        self.assertEqual(self.colorkeys('Keys'), self.default_keys)
        # For old default, name2 must be blank, name ni always used.
        usermain.read_string('''
            [Keys]
            default = Kweli
            name = IDLE Classic Unix
            ''')
        self.assertEqual(self.colorkeys('Keys'), 'IDLE Classic Unix')
        # Erroneous non-default old builtin reverts to default.
        usermain['Keys']['name'] = 'non-existent'
        self.assertEqual(self.colorkeys('Keys'), self.default_keys)
        usermain.remove_section('Keys')

    eleza test_new_builtin_keys(self):
        # IDLE writes name2 kila new builtins.
        usermain.read_string('''
            [Keys]
            default = Kweli
            name2 = IDLE Modern Unix
            ''')
        self.assertEqual(self.colorkeys('Keys'), 'IDLE Modern Unix')
        # Leftover 'name', sio removed, ni ignored.
        usermain['Keys']['name'] = 'IDLE Classic Unix'
        self.assertEqual(self.colorkeys('Keys'), 'IDLE Modern Unix')
        # Erroneous non-default new builtin reverts to default.
        usermain['Keys']['name2'] = 'non-existent'
        self.assertEqual(self.colorkeys('Keys'), self.default_keys)
        usermain.remove_section('Keys')

    eleza test_user_override_keys(self):
        # Erroneous custom name (no definition) reverts to default.
        usermain.read_string('''
            [Keys]
            default = Uongo
            name = Custom Keys
            ''')
        self.assertEqual(self.colorkeys('Keys'), self.default_keys)
        # Custom name ni valid ukijumuisha matching Section name.
        userkeys.read_string('[Custom Keys]\na=b')
        self.assertEqual(self.colorkeys('Keys'), 'Custom Keys')
        # Name2 ni ignored.
        usermain['Keys']['name2'] = 'non-existent'
        self.assertEqual(self.colorkeys('Keys'), 'Custom Keys')
        usermain.remove_section('Keys')
        userkeys.remove_section('Custom Keys')


kundi ChangesTest(unittest.TestCase):

    empty = {'main':{}, 'highlight':{}, 'keys':{}, 'extensions':{}}

    eleza load(self):  # Test_add_option verifies that this works.
        changes = self.changes
        changes.add_option('main', 'Msec', 'mitem', 'mval')
        changes.add_option('highlight', 'Hsec', 'hitem', 'hval')
        changes.add_option('keys', 'Ksec', 'kitem', 'kval')
        rudisha changes

    loaded = {'main': {'Msec': {'mitem': 'mval'}},
              'highlight': {'Hsec': {'hitem': 'hval'}},
              'keys': {'Ksec': {'kitem':'kval'}},
              'extensions': {}}

    eleza setUp(self):
        self.changes = config.ConfigChanges()

    eleza test_init(self):
        self.assertEqual(self.changes, self.empty)

    eleza test_add_option(self):
        changes = self.load()
        self.assertEqual(changes, self.loaded)
        changes.add_option('main', 'Msec', 'mitem', 'mval')
        self.assertEqual(changes, self.loaded)

    eleza test_save_option(self):  # Static function does sio touch changes.
        save_option = self.changes.save_option
        self.assertKweli(save_option('main', 'Indent', 'what', '0'))
        self.assertUongo(save_option('main', 'Indent', 'what', '0'))
        self.assertEqual(usermain['Indent']['what'], '0')

        self.assertKweli(save_option('main', 'Indent', 'use-spaces', '0'))
        self.assertEqual(usermain['Indent']['use-spaces'], '0')
        self.assertKweli(save_option('main', 'Indent', 'use-spaces', '1'))
        self.assertUongo(usermain.has_option('Indent', 'use-spaces'))
        usermain.remove_section('Indent')

    eleza test_save_added(self):
        changes = self.load()
        self.assertKweli(changes.save_all())
        self.assertEqual(usermain['Msec']['mitem'], 'mval')
        self.assertEqual(userhigh['Hsec']['hitem'], 'hval')
        self.assertEqual(userkeys['Ksec']['kitem'], 'kval')
        changes.add_option('main', 'Msec', 'mitem', 'mval')
        self.assertUongo(changes.save_all())
        usermain.remove_section('Msec')
        userhigh.remove_section('Hsec')
        userkeys.remove_section('Ksec')

    eleza test_save_help(self):
        # Any change to HelpFiles overwrites entire section.
        changes = self.changes
        changes.save_option('main', 'HelpFiles', 'IDLE', 'idledoc')
        changes.add_option('main', 'HelpFiles', 'ELDI', 'codeldi')
        changes.save_all()
        self.assertUongo(usermain.has_option('HelpFiles', 'IDLE'))
        self.assertKweli(usermain.has_option('HelpFiles', 'ELDI'))

    eleza test_save_default(self):  # Cover 2nd na 3rd false branches.
        changes = self.changes
        changes.add_option('main', 'Indent', 'use-spaces', '1')
        # save_option rudishas Uongo; cfg_type_changed remains Uongo.

    # TODO: test that save_all calls usercfg Saves.

    eleza test_delete_section(self):
        changes = self.load()
        changes.delete_section('main', 'fake')  # Test no exception.
        self.assertEqual(changes, self.loaded)  # Test nothing deleted.
        kila cfgtype, section kwenye (('main', 'Msec'), ('keys', 'Ksec')):
            testcfg[cfgtype].SetOption(section, 'name', 'value')
            changes.delete_section(cfgtype, section)
            ukijumuisha self.assertRaises(KeyError):
                changes[cfgtype][section]  # Test section gone kutoka changes
                testcfg[cfgtype][section]  # na kutoka mock userCfg.
        # TODO test kila save call.

    eleza test_clear(self):
        changes = self.load()
        changes.clear()
        self.assertEqual(changes, self.empty)


kundi WarningTest(unittest.TestCase):

    eleza test_warn(self):
        Equal = self.assertEqual
        config._warned = set()
        ukijumuisha captured_stderr() kama stderr:
            config._warn('warning', 'key')
        Equal(config._warned, {('warning','key')})
        Equal(stderr.getvalue(), 'warning'+'\n')
        ukijumuisha captured_stderr() kama stderr:
            config._warn('warning', 'key')
        Equal(stderr.getvalue(), '')
        ukijumuisha captured_stderr() kama stderr:
            config._warn('warn2', 'yek')
        Equal(config._warned, {('warning','key'), ('warn2','yek')})
        Equal(stderr.getvalue(), 'warn2'+'\n')


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
