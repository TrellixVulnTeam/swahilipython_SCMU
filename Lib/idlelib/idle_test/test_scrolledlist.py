"Test scrolledlist, coverage 38%."

kutoka idlelib.scrolledlist agiza ScrolledList
agiza unittest
kutoka test.support agiza requires
requires('gui')
kutoka tkinter agiza Tk


kundi ScrolledListTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.root = Tk()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.destroy()
        toa cls.root


    eleza test_init(self):
        ScrolledList(self.root)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
