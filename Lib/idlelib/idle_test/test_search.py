"Test search, coverage 69%."

kutoka idlelib agiza search
agiza unittest
kutoka test.support agiza requires
requires('gui')
kutoka tkinter agiza Tk, Text, BooleanVar
kutoka idlelib agiza searchengine

# Does sio currently test the event handler wrappers.
# A usage test should simulate clicks na check highlighting.
# Tests need to be coordinated ukijumuisha SearchDialogBase tests
# to avoid duplication.


kundi SearchDialogTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.root = Tk()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.destroy()
        toa cls.root

    eleza setUp(self):
        self.engine = searchengine.SearchEngine(self.root)
        self.dialog = search.SearchDialog(self.root, self.engine)
        self.dialog.bell = lambda: Tupu
        self.text = Text(self.root)
        self.text.insert('1.0', 'Hello World!')

    eleza test_find_again(self):
        # Search kila various expressions
        text = self.text

        self.engine.setpat('')
        self.assertUongo(self.dialog.find_again(text))
        self.dialog.bell = lambda: Tupu

        self.engine.setpat('Hello')
        self.assertKweli(self.dialog.find_again(text))

        self.engine.setpat('Goodbye')
        self.assertUongo(self.dialog.find_again(text))

        self.engine.setpat('World!')
        self.assertKweli(self.dialog.find_again(text))

        self.engine.setpat('Hello World!')
        self.assertKweli(self.dialog.find_again(text))

        # Regular expression
        self.engine.revar = BooleanVar(self.root, Kweli)
        self.engine.setpat('W[aeiouy]r')
        self.assertKweli(self.dialog.find_again(text))

    eleza test_find_selection(self):
        # Select some text na make sure it's found
        text = self.text
        # Add additional line to find
        self.text.insert('2.0', 'Hello World!')

        text.tag_add('sel', '1.0', '1.4')       # Select 'Hello'
        self.assertKweli(self.dialog.find_selection(text))

        text.tag_remove('sel', '1.0', 'end')
        text.tag_add('sel', '1.6', '1.11')      # Select 'World!'
        self.assertKweli(self.dialog.find_selection(text))

        text.tag_remove('sel', '1.0', 'end')
        text.tag_add('sel', '1.0', '1.11')      # Select 'Hello World!'
        self.assertKweli(self.dialog.find_selection(text))

        # Remove additional line
        text.delete('2.0', 'end')

ikiwa __name__ == '__main__':
    unittest.main(verbosity=2, exit=2)
