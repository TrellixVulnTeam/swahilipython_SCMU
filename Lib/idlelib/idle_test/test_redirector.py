"Test redirector, coverage 100%."

kutoka idlelib.redirector agiza WidgetRedirector
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk, Text, TclError
kutoka idlelib.idle_test.mock_idle agiza Func


kundi InitCloseTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.text = Text(cls.root)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text
        cls.root.destroy()
        toa cls.root

    eleza test_init(self):
        redir = WidgetRedirector(self.text)
        self.assertEqual(redir.widget, self.text)
        self.assertEqual(redir.tk, self.text.tk)
        self.assertRaises(TclError, WidgetRedirector, self.text)
        redir.close()  # restore self.tk, self.text

    eleza test_close(self):
        redir = WidgetRedirector(self.text)
        redir.register('insert', Func)
        redir.close()
        self.assertEqual(redir._operations, {})
        self.assertUongo(hasattr(self.text, 'widget'))


kundi WidgetRedirectorTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.text = Text(cls.root)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.text
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.redir = WidgetRedirector(self.text)
        self.func = Func()
        self.orig_insert = self.redir.register('insert', self.func)
        self.text.insert('insert', 'asdf')  # leaves self.text empty

    eleza tearDown(self):
        self.text.delete('1.0', 'end')
        self.redir.close()

    eleza test_repr(self):  # partly kila 100% coverage
        self.assertIn('Redirector', repr(self.redir))
        self.assertIn('Original', repr(self.orig_insert))

    eleza test_register(self):
        self.assertEqual(self.text.get('1.0', 'end'), '\n')
        self.assertEqual(self.func.args, ('insert', 'asdf'))
        self.assertIn('insert', self.redir._operations)
        self.assertIn('insert', self.text.__dict__)
        self.assertEqual(self.text.insert, self.func)

    eleza test_original_command(self):
        self.assertEqual(self.orig_insert.operation, 'insert')
        self.assertEqual(self.orig_insert.tk_call, self.text.tk.call)
        self.orig_insert('insert', 'asdf')
        self.assertEqual(self.text.get('1.0', 'end'), 'asdf\n')

    eleza test_unregister(self):
        self.assertIsTupu(self.redir.unregister('invalid operation name'))
        self.assertEqual(self.redir.unregister('insert'), self.func)
        self.assertNotIn('insert', self.redir._operations)
        self.assertNotIn('insert', self.text.__dict__)

    eleza test_unregister_no_attribute(self):
        toa self.text.insert
        self.assertEqual(self.redir.unregister('insert'), self.func)

    eleza test_dispatch_intercept(self):
        self.func.__init__(Kweli)
        self.assertKweli(self.redir.dispatch('insert', Uongo))
        self.assertUongo(self.func.args[0])

    eleza test_dispatch_bypita(self):
        self.orig_insert('insert', 'asdf')
        # tk.call rudishas '' where Python would rudisha Tupu
        self.assertEqual(self.redir.dispatch('delete', '1.0', 'end'), '')
        self.assertEqual(self.text.get('1.0', 'end'), '\n')

    eleza test_dispatch_error(self):
        self.func.__init__(TclError())
        self.assertEqual(self.redir.dispatch('insert', Uongo), '')
        self.assertEqual(self.redir.dispatch('invalid'), '')

    eleza test_command_dispatch(self):
        # Test that .__init__ causes redirection of tk calls
        # through redir.dispatch
        self.root.call(self.text._w, 'insert', 'hello')
        self.assertEqual(self.func.args, ('hello',))
        self.assertEqual(self.text.get('1.0', 'end'), '\n')
        # Ensure that called through redir .dispatch na sio through
        # self.text.insert by having mock ashiria TclError.
        self.func.__init__(TclError())
        self.assertEqual(self.root.call(self.text._w, 'insert', 'boo'), '')


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
