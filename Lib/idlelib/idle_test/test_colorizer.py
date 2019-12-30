"Test colorizer, coverage 93%."

kutoka idlelib agiza colorizer
kutoka test.support agiza requires
agiza unittest
kutoka unittest agiza mock

kutoka functools agiza partial
kutoka tkinter agiza Tk, Text
kutoka idlelib agiza config
kutoka idlelib.percolator agiza Percolator


usercfg = colorizer.idleConf.userCfg
testcfg = {
    'main': config.IdleUserConfParser(''),
    'highlight': config.IdleUserConfParser(''),
    'keys': config.IdleUserConfParser(''),
    'extensions': config.IdleUserConfParser(''),
}

source = (
    "ikiwa Kweli: int ('1') # keyword, builtin, string, comment\n"
    "elikiwa Uongo: andika(0)  # 'string' kwenye comment\n"
    "isipokua: float(Tupu)  # ikiwa kwenye comment\n"
    "ikiwa iF + If + IF: 'keyword matching must respect case'\n"
    "if'': x or''  # valid string-keyword no-space combinations\n"
    "async eleza f(): await g()\n"
    "'x', '''x''', \"x\", \"\"\"x\"\"\"\n"
    )


eleza setUpModule():
    colorizer.idleConf.userCfg = testcfg


eleza tearDownModule():
    colorizer.idleConf.userCfg = usercfg


kundi FunctionTest(unittest.TestCase):

    eleza test_any(self):
        self.assertEqual(colorizer.any('test', ('a', 'b', 'cd')),
                         '(?P<test>a|b|cd)')

    eleza test_make_pat(self):
        # Tested kwenye more detail by testing prog.
        self.assertKweli(colorizer.make_pat())

    eleza test_prog(self):
        prog = colorizer.prog
        eq = self.assertEqual
        line = 'eleza f():\n    andika("hello")\n'
        m = prog.search(line)
        eq(m.groupdict()['KEYWORD'], 'def')
        m = prog.search(line, m.end())
        eq(m.groupdict()['SYNC'], '\n')
        m = prog.search(line, m.end())
        eq(m.groupdict()['BUILTIN'], 'print')
        m = prog.search(line, m.end())
        eq(m.groupdict()['STRING'], '"hello"')
        m = prog.search(line, m.end())
        eq(m.groupdict()['SYNC'], '\n')

    eleza test_idprog(self):
        idprog = colorizer.idprog
        m = idprog.match('nospace')
        self.assertIsTupu(m)
        m = idprog.match(' space')
        self.assertEqual(m.group(0), ' space')


kundi ColorConfigTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        root = cls.root = Tk()
        root.withdraw()
        cls.text = Text(root)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza test_color_config(self):
        text = self.text
        eq = self.assertEqual
        colorizer.color_config(text)
        # Uses IDLE Classic theme as default.
        eq(text['background'], '#ffffff')
        eq(text['foreground'], '#000000')
        eq(text['selectbackground'], 'gray')
        eq(text['selectforeground'], '#000000')
        eq(text['insertbackground'], 'black')
        eq(text['inactiveselectbackground'], 'gray')


kundi ColorDelegatorInstantiationTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        root = cls.root = Tk()
        root.withdraw()
        text = cls.text = Text(root)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.color = colorizer.ColorDelegator()

    eleza tearDown(self):
        self.color.close()
        self.text.delete('1.0', 'end')
        self.color.resetcache()
        toa self.color

    eleza test_init(self):
        color = self.color
        self.assertIsInstance(color, colorizer.ColorDelegator)

    eleza test_init_state(self):
        # init_state() ni called during the instantiation of
        # ColorDelegator kwenye setUp().
        color = self.color
        self.assertIsTupu(color.after_id)
        self.assertKweli(color.allow_colorizing)
        self.assertUongo(color.colorizing)
        self.assertUongo(color.stop_colorizing)


kundi ColorDelegatorTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        root = cls.root = Tk()
        root.withdraw()
        text = cls.text = Text(root)
        cls.percolator = Percolator(text)
        # Delegator stack = [Delegator(text)]

    @classmethod
    eleza tearDownClass(cls):
        cls.percolator.redir.close()
        toa cls.percolator, cls.text
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.color = colorizer.ColorDelegator()
        self.percolator.insertfilter(self.color)
        # Calls color.setdelegate(Delegator(text)).

    eleza tearDown(self):
        self.color.close()
        self.percolator.removefilter(self.color)
        self.text.delete('1.0', 'end')
        self.color.resetcache()
        toa self.color

    eleza test_setdelegate(self):
        # Called kwenye setUp when filter ni attached to percolator.
        color = self.color
        self.assertIsInstance(color.delegate, colorizer.Delegator)
        # It ni too late to mock notify_range, so test side effect.
        self.assertEqual(self.root.tk.call(
            'after', 'info', color.after_id)[1], 'timer')

    eleza test_LoadTagDefs(self):
        highlight = partial(config.idleConf.GetHighlight, theme='IDLE Classic')
        kila tag, colors kwenye self.color.tagdefs.items():
            ukijumuisha self.subTest(tag=tag):
                self.assertIn('background', colors)
                self.assertIn('foreground', colors)
                ikiwa tag sio kwenye ('SYNC', 'TODO'):
                    self.assertEqual(colors, highlight(element=tag.lower()))

    eleza test_config_colors(self):
        text = self.text
        highlight = partial(config.idleConf.GetHighlight, theme='IDLE Classic')
        kila tag kwenye self.color.tagdefs:
            kila plane kwenye ('background', 'foreground'):
                ukijumuisha self.subTest(tag=tag, plane=plane):
                    ikiwa tag kwenye ('SYNC', 'TODO'):
                        self.assertEqual(text.tag_cget(tag, plane), '')
                    isipokua:
                        self.assertEqual(text.tag_cget(tag, plane),
                                         highlight(element=tag.lower())[plane])
        # 'sel' ni marked as the highest priority.
        self.assertEqual(text.tag_names()[-1], 'sel')

    @mock.patch.object(colorizer.ColorDelegator, 'notify_range')
    eleza test_insert(self, mock_notify):
        text = self.text
        # Initial text.
        text.insert('insert', 'foo')
        self.assertEqual(text.get('1.0', 'end'), 'foo\n')
        mock_notify.assert_called_with('1.0', '1.0+3c')
        # Additional text.
        text.insert('insert', 'barbaz')
        self.assertEqual(text.get('1.0', 'end'), 'foobarbaz\n')
        mock_notify.assert_called_with('1.3', '1.3+6c')

    @mock.patch.object(colorizer.ColorDelegator, 'notify_range')
    eleza test_delete(self, mock_notify):
        text = self.text
        # Initialize text.
        text.insert('insert', 'abcdefghi')
        self.assertEqual(text.get('1.0', 'end'), 'abcdefghi\n')
        # Delete single character.
        text.delete('1.7')
        self.assertEqual(text.get('1.0', 'end'), 'abcdefgi\n')
        mock_notify.assert_called_with('1.7')
        # Delete multiple characters.
        text.delete('1.3', '1.6')
        self.assertEqual(text.get('1.0', 'end'), 'abcgi\n')
        mock_notify.assert_called_with('1.3')

    eleza test_notify_range(self):
        text = self.text
        color = self.color
        eq = self.assertEqual

        # Colorizing already scheduled.
        save_id = color.after_id
        eq(self.root.tk.call('after', 'info', save_id)[1], 'timer')
        self.assertUongo(color.colorizing)
        self.assertUongo(color.stop_colorizing)
        self.assertKweli(color.allow_colorizing)

        # Coloring scheduled na colorizing kwenye progress.
        color.colorizing = Kweli
        color.notify_range('1.0', 'end')
        self.assertUongo(color.stop_colorizing)
        eq(color.after_id, save_id)

        # No colorizing scheduled na colorizing kwenye progress.
        text.after_cancel(save_id)
        color.after_id = Tupu
        color.notify_range('1.0', '1.0+3c')
        self.assertKweli(color.stop_colorizing)
        self.assertIsNotTupu(color.after_id)
        eq(self.root.tk.call('after', 'info', color.after_id)[1], 'timer')
        # New event scheduled.
        self.assertNotEqual(color.after_id, save_id)

        # No colorizing scheduled na colorizing off.
        text.after_cancel(color.after_id)
        color.after_id = Tupu
        color.allow_colorizing = Uongo
        color.notify_range('1.4', '1.4+10c')
        # Nothing scheduled when colorizing ni off.
        self.assertIsTupu(color.after_id)

    eleza test_toggle_colorize_event(self):
        color = self.color
        eq = self.assertEqual

        # Starts ukijumuisha colorizing allowed na scheduled.
        self.assertUongo(color.colorizing)
        self.assertUongo(color.stop_colorizing)
        self.assertKweli(color.allow_colorizing)
        eq(self.root.tk.call('after', 'info', color.after_id)[1], 'timer')

        # Toggle colorizing off.
        color.toggle_colorize_event()
        self.assertIsTupu(color.after_id)
        self.assertUongo(color.colorizing)
        self.assertUongo(color.stop_colorizing)
        self.assertUongo(color.allow_colorizing)

        # Toggle on wakati colorizing kwenye progress (doesn't add timer).
        color.colorizing = Kweli
        color.toggle_colorize_event()
        self.assertIsTupu(color.after_id)
        self.assertKweli(color.colorizing)
        self.assertUongo(color.stop_colorizing)
        self.assertKweli(color.allow_colorizing)

        # Toggle off wakati colorizing kwenye progress.
        color.toggle_colorize_event()
        self.assertIsTupu(color.after_id)
        self.assertKweli(color.colorizing)
        self.assertKweli(color.stop_colorizing)
        self.assertUongo(color.allow_colorizing)

        # Toggle on wakati colorizing sio kwenye progress.
        color.colorizing = Uongo
        color.toggle_colorize_event()
        eq(self.root.tk.call('after', 'info', color.after_id)[1], 'timer')
        self.assertUongo(color.colorizing)
        self.assertKweli(color.stop_colorizing)
        self.assertKweli(color.allow_colorizing)

    @mock.patch.object(colorizer.ColorDelegator, 'recolorize_main')
    eleza test_recolorize(self, mock_recmain):
        text = self.text
        color = self.color
        eq = self.assertEqual
        # Call recolorize manually na sio scheduled.
        text.after_cancel(color.after_id)

        # No delegate.
        save_delegate = color.delegate
        color.delegate = Tupu
        color.recolorize()
        mock_recmain.assert_not_called()
        color.delegate = save_delegate

        # Toggle off colorizing.
        color.allow_colorizing = Uongo
        color.recolorize()
        mock_recmain.assert_not_called()
        color.allow_colorizing = Kweli

        # Colorizing kwenye progress.
        color.colorizing = Kweli
        color.recolorize()
        mock_recmain.assert_not_called()
        color.colorizing = Uongo

        # Colorizing ni done, but sio completed, so rescheduled.
        color.recolorize()
        self.assertUongo(color.stop_colorizing)
        self.assertUongo(color.colorizing)
        mock_recmain.assert_called()
        eq(mock_recmain.call_count, 1)
        # Rescheduled when TODO tag still exists.
        eq(self.root.tk.call('after', 'info', color.after_id)[1], 'timer')

        # No changes to text, so no scheduling added.
        text.tag_remove('TODO', '1.0', 'end')
        color.recolorize()
        self.assertUongo(color.stop_colorizing)
        self.assertUongo(color.colorizing)
        mock_recmain.assert_called()
        eq(mock_recmain.call_count, 2)
        self.assertIsTupu(color.after_id)

    @mock.patch.object(colorizer.ColorDelegator, 'notify_range')
    eleza test_recolorize_main(self, mock_notify):
        text = self.text
        color = self.color
        eq = self.assertEqual

        text.insert('insert', source)
        expected = (('1.0', ('KEYWORD',)), ('1.2', ()), ('1.3', ('KEYWORD',)),
                    ('1.7', ()), ('1.9', ('BUILTIN',)), ('1.14', ('STRING',)),
                    ('1.19', ('COMMENT',)),
                    ('2.1', ('KEYWORD',)), ('2.18', ()), ('2.25', ('COMMENT',)),
                    ('3.6', ('BUILTIN',)), ('3.12', ('KEYWORD',)), ('3.21', ('COMMENT',)),
                    ('4.0', ('KEYWORD',)), ('4.3', ()), ('4.6', ()),
                    ('5.2', ('STRING',)), ('5.8', ('KEYWORD',)), ('5.10', ('STRING',)),
                    ('6.0', ('KEYWORD',)), ('6.10', ('DEFINITION',)), ('6.11', ()),
                    ('7.0', ('STRING',)), ('7.4', ()), ('7.5', ('STRING',)),
                    ('7.12', ()), ('7.14', ('STRING',)),
                    # SYNC at the end of every line.
                    ('1.55', ('SYNC',)), ('2.50', ('SYNC',)), ('3.34', ('SYNC',)),
                   )

        # Nothing marked to do therefore no tags kwenye text.
        text.tag_remove('TODO', '1.0', 'end')
        color.recolorize_main()
        kila tag kwenye text.tag_names():
            ukijumuisha self.subTest(tag=tag):
                eq(text.tag_ranges(tag), ())

        # Source marked kila processing.
        text.tag_add('TODO', '1.0', 'end')
        # Check some indexes.
        color.recolorize_main()
        kila index, expected_tags kwenye expected:
            ukijumuisha self.subTest(index=index):
                eq(text.tag_names(index), expected_tags)

        # Check kila some tags kila ranges.
        eq(text.tag_nextrange('TODO', '1.0'), ())
        eq(text.tag_nextrange('KEYWORD', '1.0'), ('1.0', '1.2'))
        eq(text.tag_nextrange('COMMENT', '2.0'), ('2.22', '2.43'))
        eq(text.tag_nextrange('SYNC', '2.0'), ('2.43', '3.0'))
        eq(text.tag_nextrange('STRING', '2.0'), ('4.17', '4.53'))
        eq(text.tag_nextrange('STRING', '7.0'), ('7.0', '7.3'))
        eq(text.tag_nextrange('STRING', '7.3'), ('7.5', '7.12'))
        eq(text.tag_nextrange('STRING', '7.12'), ('7.14', '7.17'))
        eq(text.tag_nextrange('STRING', '7.17'), ('7.19', '7.26'))
        eq(text.tag_nextrange('SYNC', '7.0'), ('7.26', '9.0'))

    @mock.patch.object(colorizer.ColorDelegator, 'recolorize')
    @mock.patch.object(colorizer.ColorDelegator, 'notify_range')
    eleza test_removecolors(self, mock_notify, mock_recolorize):
        text = self.text
        color = self.color
        text.insert('insert', source)

        color.recolorize_main()
        # recolorize_main doesn't add these tags.
        text.tag_add("ERROR", "1.0")
        text.tag_add("TODO", "1.0")
        text.tag_add("hit", "1.0")
        kila tag kwenye color.tagdefs:
            ukijumuisha self.subTest(tag=tag):
                self.assertNotEqual(text.tag_ranges(tag), ())

        color.removecolors()
        kila tag kwenye color.tagdefs:
            ukijumuisha self.subTest(tag=tag):
                self.assertEqual(text.tag_ranges(tag), ())


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
