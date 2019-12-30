agiza unittest
agiza tkinter
kutoka test.support agiza requires, run_unittest
kutoka tkinter.test.support agiza AbstractTkTest

requires('gui')

kundi TextTest(AbstractTkTest, unittest.TestCase):

    eleza setUp(self):
        super().setUp()
        self.text = tkinter.Text(self.root)

    eleza test_debug(self):
        text = self.text
        olddebug = text.debug()
        jaribu:
            text.debug(0)
            self.assertEqual(text.debug(), 0)
            text.debug(1)
            self.assertEqual(text.debug(), 1)
        mwishowe:
            text.debug(olddebug)
            self.assertEqual(text.debug(), olddebug)

    eleza test_search(self):
        text = self.text

        # pattern na index are obligatory arguments.
        self.assertRaises(tkinter.TclError, text.search, Tupu, '1.0')
        self.assertRaises(tkinter.TclError, text.search, 'a', Tupu)
        self.assertRaises(tkinter.TclError, text.search, Tupu, Tupu)

        # Invalid text index.
        self.assertRaises(tkinter.TclError, text.search, '', 0)

        # Check ikiwa we are getting the indices as strings -- you are likely
        # to get Tcl_Obj under Tk 8.5 ikiwa Tkinter doesn't convert it.
        text.insert('1.0', 'hi-test')
        self.assertEqual(text.search('-test', '1.0', 'end'), '1.2')
        self.assertEqual(text.search('test', '1.0', 'end'), '1.3')


tests_gui = (TextTest, )

ikiwa __name__ == "__main__":
    run_unittest(*tests_gui)
