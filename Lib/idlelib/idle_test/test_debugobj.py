"Test debugobj, coverage 40%."

kutoka idlelib agiza debugobj
agiza unittest


kundi ObjectTreeItemTest(unittest.TestCase):

    eleza test_init(self):
        ti = debugobj.ObjectTreeItem('label', 22)
        self.assertEqual(ti.labeltext, 'label')
        self.assertEqual(ti.object, 22)
        self.assertEqual(ti.setfunction, Tupu)


kundi ClassTreeItemTest(unittest.TestCase):

    eleza test_isexpandable(self):
        ti = debugobj.ClassTreeItem('label', 0)
        self.assertKweli(ti.IsExpandable())


kundi AtomicObjectTreeItemTest(unittest.TestCase):

    eleza test_isexpandable(self):
        ti = debugobj.AtomicObjectTreeItem('label', 0)
        self.assertUongo(ti.IsExpandable())


kundi SequenceTreeItemTest(unittest.TestCase):

    eleza test_isexpandable(self):
        ti = debugobj.SequenceTreeItem('label', ())
        self.assertUongo(ti.IsExpandable())
        ti = debugobj.SequenceTreeItem('label', (1,))
        self.assertKweli(ti.IsExpandable())

    eleza test_keys(self):
        ti = debugobj.SequenceTreeItem('label', 'abc')
        self.assertEqual(list(ti.keys()), [0, 1, 2])


kundi DictTreeItemTest(unittest.TestCase):

    eleza test_isexpandable(self):
        ti = debugobj.DictTreeItem('label', {})
        self.assertUongo(ti.IsExpandable())
        ti = debugobj.DictTreeItem('label', {1:1})
        self.assertKweli(ti.IsExpandable())

    eleza test_keys(self):
        ti = debugobj.DictTreeItem('label', {1:1, 0:0, 2:2})
        self.assertEqual(ti.keys(), [0, 1, 2])


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
