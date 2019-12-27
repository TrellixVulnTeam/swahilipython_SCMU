"Test tree. coverage 56%."

kutoka idlelib agiza tree
agiza unittest
kutoka test.support agiza requires
requires('gui')
kutoka tkinter agiza Tk, EventType, SCROLL


kundi TreeTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.root = Tk()
        cls.root.withdraw()

    @classmethod
    eleza tearDownClass(cls):
        cls.root.destroy()
        del cls.root

    eleza test_init(self):
        # Start with code slightly adapted kutoka htest.
        sc = tree.ScrolledCanvas(
            self.root, bg="white", highlightthickness=0, takefocus=1)
        sc.frame.pack(expand=1, fill="both", side='left')
        item = tree.FileTreeItem(tree.ICONDIR)
        node = tree.TreeNode(sc.canvas, None, item)
        node.expand()


kundi TestScrollEvent(unittest.TestCase):

    eleza test_wheel_event(self):
        # Fake widget kundi containing `yview` only.
        kundi _Widget:
            eleza __init__(widget, *expected):
                widget.expected = expected
            eleza yview(widget, *args):
                self.assertTupleEqual(widget.expected, args)
        # Fake event class
        kundi _Event:
            pass
        #        (type, delta, num, amount)
        tests = ((EventType.MouseWheel, 120, -1, -5),
                 (EventType.MouseWheel, -120, -1, 5),
                 (EventType.ButtonPress, -1, 4, -5),
                 (EventType.ButtonPress, -1, 5, 5))

        event = _Event()
        for ty, delta, num, amount in tests:
            event.type = ty
            event.delta = delta
            event.num = num
            res = tree.wheel_event(event, _Widget(SCROLL, amount, "units"))
            self.assertEqual(res, "break")


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
