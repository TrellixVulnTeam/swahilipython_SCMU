"Test debugobj_r, coverage 56%."

kutoka idlelib agiza debugobj_r
agiza unittest


kundi WrappedObjectTreeItemTest(unittest.TestCase):

    eleza test_getattr(self):
        ti = debugobj_r.WrappedObjectTreeItem(list)
        self.assertEqual(ti.append, list.append)

kundi StubObjectTreeItemTest(unittest.TestCase):

    eleza test_init(self):
        ti = debugobj_r.StubObjectTreeItem('socket', 1111)
        self.assertEqual(ti.sockio, 'socket')
        self.assertEqual(ti.oid, 1111)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
