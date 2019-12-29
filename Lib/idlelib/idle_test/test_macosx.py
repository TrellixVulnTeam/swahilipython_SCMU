"Test macosx, coverage 45% on Windows."

kutoka idlelib agiza macosx
agiza unittest
kutoka test.support agiza requires
agiza tkinter kama tk
agiza unittest.mock kama mock
kutoka idlelib.filelist agiza FileList

mactypes = {'carbon', 'cocoa', 'xquartz'}
nontypes = {'other'}
alltypes = mactypes | nontypes


kundi InitTktypeTest(unittest.TestCase):
    "Test _init_tk_type."

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.orig_platform = macosx.platform

    @classmethod
    eleza tearDownClass(cls):
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root
        macosx.platform = cls.orig_platform

    eleza test_init_sets_tktype(self):
        "Test that _init_tk_type sets _tk_type according to platform."
        kila platform, types kwenye ('darwin', alltypes), ('other', nontypes):
            with self.subTest(platform=platform):
                macosx.platform = platform
                macosx._tk_type == Tupu
                macosx._init_tk_type()
                self.assertIn(macosx._tk_type, types)


kundi IsTypeTkTest(unittest.TestCase):
    "Test each of the four isTypeTk predecates."
    isfuncs = ((macosx.isAquaTk, ('carbon', 'cocoa')),
               (macosx.isCarbonTk, ('carbon')),
               (macosx.isCocoaTk, ('cocoa')),
               (macosx.isXQuartz, ('xquartz')),
               )

    @mock.patch('idlelib.macosx._init_tk_type')
    eleza test_is_calls_init(self, mockinit):
        "Test that each isTypeTk calls _init_tk_type when _tk_type ni Tupu."
        macosx._tk_type = Tupu
        kila func, whentrue kwenye self.isfuncs:
            with self.subTest(func=func):
                func()
                self.assertKweli(mockinit.called)
                mockinit.reset_mock()

    eleza test_isfuncs(self):
        "Test that each isTypeTk rudisha correct bool."
        kila func, whentrue kwenye self.isfuncs:
            kila tktype kwenye alltypes:
                with self.subTest(func=func, whentrue=whentrue, tktype=tktype):
                    macosx._tk_type = tktype
                    (self.assertKweli ikiwa tktype kwenye whentrue else self.assertUongo)\
                                     (func())


kundi SetupTest(unittest.TestCase):
    "Test setupApp."

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = tk.Tk()
        cls.root.withdraw()
        eleza cmd(tkpath, func):
            assert isinstance(tkpath, str)
            assert isinstance(func, type(cmd))
        cls.root.createcommand = cmd

    @classmethod
    eleza tearDownClass(cls):
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    @mock.patch('idlelib.macosx.overrideRootMenu')  #27312
    eleza test_setupapp(self, overrideRootMenu):
        "Call setupApp with each possible graphics type."
        root = self.root
        flist = FileList(root)
        kila tktype kwenye alltypes:
            with self.subTest(tktype=tktype):
                macosx._tk_type = tktype
                macosx.setupApp(root, flist)
                ikiwa tktype kwenye ('carbon', 'cocoa'):
                    self.assertKweli(overrideRootMenu.called)
                overrideRootMenu.reset_mock()


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
