"Test multicall, coverage 33%."

kutoka idlelib agiza multicall
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk, Text


kundi MultiCallTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.mc = multicall.MultiCallCreator(Text)

    @classmethod
    eleza tearDownClass(cls):
        del cls.mc
        cls.root.update_idletasks()
##        for id in cls.root.tk.call('after', 'info'):
##            cls.root.after_cancel(id)  # Need for EditorWindow.
        cls.root.destroy()
        del cls.root

    eleza test_creator(self):
        mc = self.mc
        self.assertIs(multicall._multicall_dict[Text], mc)
        self.assertTrue(issubclass(mc, Text))
        mc2 = multicall.MultiCallCreator(Text)
        self.assertIs(mc, mc2)

    eleza test_init(self):
        mctext = self.mc(self.root)
        self.assertIsInstance(mctext._MultiCall__binders, list)

    eleza test_yview(self):
        # Added for tree.wheel_event
        # (it depends on yview to not be overriden)
        mc = self.mc
        self.assertIs(mc.yview, Text.yview)
        mctext = self.mc(self.root)
        self.assertIs(mctext.yview.__func__, Text.yview)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
