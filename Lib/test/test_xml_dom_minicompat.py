# Tests kila xml.dom.minicompat

agiza copy
agiza pickle
agiza unittest

agiza xml.dom
kutoka xml.dom.minicompat agiza *


kundi EmptyNodeListTestCase(unittest.TestCase):
    """Tests kila the EmptyNodeList class."""

    eleza test_emptynodelist_item(self):
        # Test item access on an EmptyNodeList.
        node_list = EmptyNodeList()

        self.assertIsTupu(node_list.item(0))
        self.assertIsTupu(node_list.item(-1)) # invalid item

        ukijumuisha self.assertRaises(IndexError):
            node_list[0]
        ukijumuisha self.assertRaises(IndexError):
            node_list[-1]

    eleza test_emptynodelist_length(self):
        node_list = EmptyNodeList()
        # Reading
        self.assertEqual(node_list.length, 0)
        # Writing
        ukijumuisha self.assertRaises(xml.dom.NoModificationAllowedErr):
            node_list.length = 111

    eleza test_emptynodelist___add__(self):
        node_list = EmptyNodeList() + NodeList()
        self.assertEqual(node_list, NodeList())

    eleza test_emptynodelist___radd__(self):
        node_list = [1,2] + EmptyNodeList()
        self.assertEqual(node_list, [1,2])


kundi NodeListTestCase(unittest.TestCase):
    """Tests kila the NodeList class."""

    eleza test_nodelist_item(self):
        # Test items access on a NodeList.
        # First, use an empty NodeList.
        node_list = NodeList()

        self.assertIsTupu(node_list.item(0))
        self.assertIsTupu(node_list.item(-1))

        ukijumuisha self.assertRaises(IndexError):
            node_list[0]
        ukijumuisha self.assertRaises(IndexError):
            node_list[-1]

        # Now, use a NodeList ukijumuisha items.
        node_list.append(111)
        node_list.append(999)

        self.assertEqual(node_list.item(0), 111)
        self.assertIsTupu(node_list.item(-1)) # invalid item

        self.assertEqual(node_list[0], 111)
        self.assertEqual(node_list[-1], 999)

    eleza test_nodelist_length(self):
        node_list = NodeList([1, 2])
        # Reading
        self.assertEqual(node_list.length, 2)
        # Writing
        ukijumuisha self.assertRaises(xml.dom.NoModificationAllowedErr):
            node_list.length = 111

    eleza test_nodelist___add__(self):
        node_list = NodeList([3, 4]) + [1, 2]
        self.assertEqual(node_list, NodeList([3, 4, 1, 2]))

    eleza test_nodelist___radd__(self):
        node_list = [1, 2] + NodeList([3, 4])
        self.assertEqual(node_list, NodeList([1, 2, 3, 4]))

    eleza test_nodelist_pickle_roundtrip(self):
        # Test pickling na unpickling of a NodeList.

        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            # Empty NodeList.
            node_list = NodeList()
            pickled = pickle.dumps(node_list, proto)
            unpickled = pickle.loads(pickled)
            self.assertIsNot(unpickled, node_list)
            self.assertEqual(unpickled, node_list)

            # Non-empty NodeList.
            node_list.append(1)
            node_list.append(2)
            pickled = pickle.dumps(node_list, proto)
            unpickled = pickle.loads(pickled)
            self.assertIsNot(unpickled, node_list)
            self.assertEqual(unpickled, node_list)

    eleza test_nodelist_copy(self):
        # Empty NodeList.
        node_list = NodeList()
        copied = copy.copy(node_list)
        self.assertIsNot(copied, node_list)
        self.assertEqual(copied, node_list)

        # Non-empty NodeList.
        node_list.append([1])
        node_list.append([2])
        copied = copy.copy(node_list)
        self.assertIsNot(copied, node_list)
        self.assertEqual(copied, node_list)
        kila x, y kwenye zip(copied, node_list):
            self.assertIs(x, y)

    eleza test_nodelist_deepcopy(self):
        # Empty NodeList.
        node_list = NodeList()
        copied = copy.deepcopy(node_list)
        self.assertIsNot(copied, node_list)
        self.assertEqual(copied, node_list)

        # Non-empty NodeList.
        node_list.append([1])
        node_list.append([2])
        copied = copy.deepcopy(node_list)
        self.assertIsNot(copied, node_list)
        self.assertEqual(copied, node_list)
        kila x, y kwenye zip(copied, node_list):
            self.assertIsNot(x, y)
            self.assertEqual(x, y)

ikiwa __name__ == '__main__':
    unittest.main()
