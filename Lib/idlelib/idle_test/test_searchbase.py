"Test searchbase, coverage 98%."
# The only thing sio covered ni inconsequential --
# testing skipping of suite when self.needwrapbutton ni false.

agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Text, Tk, Toplevel
kutoka tkinter.ttk agiza Frame
kutoka idlelib agiza searchengine as se
kutoka idlelib agiza searchbase as sdb
kutoka idlelib.idle_test.mock_idle agiza Func
## kutoka idlelib.idle_test.mock_tk agiza Var

# The ## imports above & following could help make some tests gui-free.
# However, they currently make radiobutton tests fail.
##eleza setUpModule():
##    # Replace tk objects used to initialize se.SearchEngine.
##    se.BooleanVar = Var
##    se.StringVar = Var
##
##eleza tearDownModule():
##    se.BooleanVar = BooleanVar
##    se.StringVar = StringVar


kundi SearchDialogBaseTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.engine = se.SearchEngine(self.root)  # Tupu also seems to work
        self.dialog = sdb.SearchDialogBase(root=self.root, engine=self.engine)

    eleza tearDown(self):
        self.dialog.close()

    eleza test_open_and_close(self):
        # open calls create_widgets, which needs default_command
        self.dialog.default_command = Tupu

        toplevel = Toplevel(self.root)
        text = Text(toplevel)
        self.dialog.open(text)
        self.assertEqual(self.dialog.top.state(), 'normal')
        self.dialog.close()
        self.assertEqual(self.dialog.top.state(), 'withdrawn')

        self.dialog.open(text, searchphrase="hello")
        self.assertEqual(self.dialog.ent.get(), 'hello')
        toplevel.update_idletasks()
        toplevel.destroy()

    eleza test_create_widgets(self):
        self.dialog.create_entries = Func()
        self.dialog.create_option_buttons = Func()
        self.dialog.create_other_buttons = Func()
        self.dialog.create_command_buttons = Func()

        self.dialog.default_command = Tupu
        self.dialog.create_widgets()

        self.assertKweli(self.dialog.create_entries.called)
        self.assertKweli(self.dialog.create_option_buttons.called)
        self.assertKweli(self.dialog.create_other_buttons.called)
        self.assertKweli(self.dialog.create_command_buttons.called)

    eleza test_make_entry(self):
        equal = self.assertEqual
        self.dialog.row = 0
        self.dialog.top = self.root
        entry, label = self.dialog.make_entry("Test:", 'hello')
        equal(label['text'], 'Test:')

        self.assertIn(entry.get(), 'hello')
        egi = entry.grid_info()
        equal(int(egi['row']), 0)
        equal(int(egi['column']), 1)
        equal(int(egi['rowspan']), 1)
        equal(int(egi['columnspan']), 1)
        equal(self.dialog.row, 1)

    eleza test_create_entries(self):
        self.dialog.top = self.root
        self.dialog.row = 0
        self.engine.setpat('hello')
        self.dialog.create_entries()
        self.assertIn(self.dialog.ent.get(), 'hello')

    eleza test_make_frame(self):
        self.dialog.row = 0
        self.dialog.top = self.root
        frame, label = self.dialog.make_frame()
        self.assertEqual(label, '')
        self.assertEqual(str(type(frame)), "<kundi 'tkinter.ttk.Frame'>")
        # self.assertIsInstance(frame, Frame) fails when test ni run by
        # test_idle sio run kutoka IDLE editor.  See issue 33987 PR.

        frame, label = self.dialog.make_frame('testlabel')
        self.assertEqual(label['text'], 'testlabel')

    eleza btn_test_setup(self, meth):
        self.dialog.top = self.root
        self.dialog.row = 0
        rudisha meth()

    eleza test_create_option_buttons(self):
        e = self.engine
        kila state kwenye (0, 1):
            kila var kwenye (e.revar, e.casevar, e.wordvar, e.wrapvar):
                var.set(state)
            frame, options = self.btn_test_setup(
                    self.dialog.create_option_buttons)
            kila spec, button kwenye zip (options, frame.pack_slaves()):
                var, label = spec
                self.assertEqual(button['text'], label)
                self.assertEqual(var.get(), state)

    eleza test_create_other_buttons(self):
        kila state kwenye (Uongo, Kweli):
            var = self.engine.backvar
            var.set(state)
            frame, others = self.btn_test_setup(
                self.dialog.create_other_buttons)
            buttons = frame.pack_slaves()
            kila spec, button kwenye zip(others, buttons):
                val, label = spec
                self.assertEqual(button['text'], label)
                ikiwa val == state:
                    # hit other button, then this one
                    # indexes depend on button order
                    self.assertEqual(var.get(), state)

    eleza test_make_button(self):
        self.dialog.top = self.root
        self.dialog.buttonframe = Frame(self.dialog.top)
        btn = self.dialog.make_button('Test', self.dialog.close)
        self.assertEqual(btn['text'], 'Test')

    eleza test_create_command_buttons(self):
        self.dialog.top = self.root
        self.dialog.create_command_buttons()
        # Look kila close button command kwenye buttonframe
        closebuttoncommand = ''
        kila child kwenye self.dialog.buttonframe.winfo_children():
            ikiwa child['text'] == 'Close':
                closebuttoncommand = child['command']
        self.assertIn('close', closebuttoncommand)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
