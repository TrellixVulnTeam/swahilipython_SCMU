"Test scrolledlist, coverage 38%."

kutoka idlelib.scrolledlist agiza ScrolledList
agiza unittest
kutoka test.support agiza requires
requires('gui')
kutoka tkinter agiza Tk


class ScrolledListTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = Tk()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        del cls.root


    def test_init(self):
        ScrolledList(self.root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
