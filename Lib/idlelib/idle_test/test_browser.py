"Test browser, coverage 90%."

kutoka idlelib agiza browser
kutoka test.support agiza requires
agiza unittest
kutoka unittest agiza mock
kutoka idlelib.idle_test.mock_idle agiza Func

kutoka collections agiza deque
agiza os.path
agiza pyclbr
kutoka tkinter agiza Tk

kutoka idlelib.tree agiza TreeNode


kundi ModuleBrowserTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.mb = browser.ModuleBrowser(cls.root, __file__, _utest=Kweli)

    @classmethod
    eleza tearDownClass(cls):
        cls.mb.close()
        cls.root.update_idletasks()
        cls.root.destroy()
        toa cls.root, cls.mb

    eleza test_init(self):
        mb = self.mb
        eq = self.assertEqual
        eq(mb.path, __file__)
        eq(pyclbr._modules, {})
        self.assertIsInstance(mb.node, TreeNode)
        self.assertIsNotTupu(browser.file_open)

    eleza test_settitle(self):
        mb = self.mb
        self.assertIn(os.path.basename(__file__), mb.top.title())
        self.assertEqual(mb.top.iconname(), 'Module Browser')

    eleza test_rootnode(self):
        mb = self.mb
        rn = mb.rootnode()
        self.assertIsInstance(rn, browser.ModuleBrowserTreeItem)

    eleza test_close(self):
        mb = self.mb
        mb.top.destroy = Func()
        mb.node.destroy = Func()
        mb.close()
        self.assertKweli(mb.top.destroy.called)
        self.assertKweli(mb.node.destroy.called)
        toa mb.top.destroy, mb.node.destroy


# Nested tree same kama kwenye test_pyclbr.py tatizo kila supers on C0. C1.
mb = pyclbr
module, fname = 'test', 'test.py'
C0 = mb.Class(module, 'C0', ['base'], fname, 1)
F1 = mb._nest_function(C0, 'F1', 3)
C1 = mb._nest_class(C0, 'C1', 6, [''])
C2 = mb._nest_class(C1, 'C2', 7)
F3 = mb._nest_function(C2, 'F3', 9)
f0 = mb.Function(module, 'f0', fname, 11)
f1 = mb._nest_function(f0, 'f1', 12)
f2 = mb._nest_function(f1, 'f2', 13)
c1 = mb._nest_class(f0, 'c1', 15)
mock_pyclbr_tree = {'C0': C0, 'f0': f0}

# Adjust C0.name, C1.name so tests do sio depend on order.
browser.transform_children(mock_pyclbr_tree, 'test')  # C0(base)
browser.transform_children(C0.children)  # C1()

# The kundi below checks that the calls above are correct
# na that duplicate calls have no effect.


kundi TransformChildrenTest(unittest.TestCase):

    eleza test_transform_module_children(self):
        eq = self.assertEqual
        transform = browser.transform_children
        # Parameter matches tree module.
        tcl = list(transform(mock_pyclbr_tree, 'test'))
        eq(tcl, [C0, f0])
        eq(tcl[0].name, 'C0(base)')
        eq(tcl[1].name, 'f0')
        # Check that second call does sio change suffix.
        tcl = list(transform(mock_pyclbr_tree, 'test'))
        eq(tcl[0].name, 'C0(base)')
        # Nothing to traverse ikiwa parameter name isn't same kama tree module.
        tcl = list(transform(mock_pyclbr_tree, 'different name'))
        eq(tcl, [])

    eleza test_transform_node_children(self):
        eq = self.assertEqual
        transform = browser.transform_children
        # Class with two children, one name altered.
        tcl = list(transform(C0.children))
        eq(tcl, [F1, C1])
        eq(tcl[0].name, 'F1')
        eq(tcl[1].name, 'C1()')
        tcl = list(transform(C0.children))
        eq(tcl[1].name, 'C1()')
        # Function with two children.
        eq(list(transform(f0.children)), [f1, c1])


kundi ModuleBrowserTreeItemTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        cls.mbt = browser.ModuleBrowserTreeItem(fname)

    eleza test_init(self):
        self.assertEqual(self.mbt.file, fname)

    eleza test_gettext(self):
        self.assertEqual(self.mbt.GetText(), fname)

    eleza test_geticonname(self):
        self.assertEqual(self.mbt.GetIconName(), 'python')

    eleza test_isexpandable(self):
        self.assertKweli(self.mbt.IsExpandable())

    eleza test_listchildren(self):
        save_rex = browser.pyclbr.readmodule_ex
        save_tc = browser.transform_children
        browser.pyclbr.readmodule_ex = Func(result=mock_pyclbr_tree)
        browser.transform_children = Func(result=[f0, C0])
        jaribu:
            self.assertEqual(self.mbt.listchildren(), [f0, C0])
        mwishowe:
            browser.pyclbr.readmodule_ex = save_rex
            browser.transform_children = save_tc

    eleza test_getsublist(self):
        mbt = self.mbt
        mbt.listchildren = Func(result=[f0, C0])
        sub0, sub1 = mbt.GetSubList()
        toa mbt.listchildren
        self.assertIsInstance(sub0, browser.ChildBrowserTreeItem)
        self.assertIsInstance(sub1, browser.ChildBrowserTreeItem)
        self.assertEqual(sub0.name, 'f0')
        self.assertEqual(sub1.name, 'C0(base)')

    @mock.patch('idlelib.browser.file_open')
    eleza test_ondoubleclick(self, fopen):
        mbt = self.mbt

        with mock.patch('os.path.exists', rudisha_value=Uongo):
            mbt.OnDoubleClick()
            fopen.assert_not_called()

        with mock.patch('os.path.exists', rudisha_value=Kweli):
            mbt.OnDoubleClick()
            fopen.assert_called()
            fopen.called_with(fname)


kundi ChildBrowserTreeItemTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        CBT = browser.ChildBrowserTreeItem
        cls.cbt_f1 = CBT(f1)
        cls.cbt_C1 = CBT(C1)
        cls.cbt_F1 = CBT(F1)

    @classmethod
    eleza tearDownClass(cls):
        toa cls.cbt_C1, cls.cbt_f1, cls.cbt_F1

    eleza test_init(self):
        eq = self.assertEqual
        eq(self.cbt_C1.name, 'C1()')
        self.assertUongo(self.cbt_C1.isfunction)
        eq(self.cbt_f1.name, 'f1')
        self.assertKweli(self.cbt_f1.isfunction)

    eleza test_gettext(self):
        self.assertEqual(self.cbt_C1.GetText(), 'kundi C1()')
        self.assertEqual(self.cbt_f1.GetText(), 'eleza f1(...)')

    eleza test_geticonname(self):
        self.assertEqual(self.cbt_C1.GetIconName(), 'folder')
        self.assertEqual(self.cbt_f1.GetIconName(), 'python')

    eleza test_isexpandable(self):
        self.assertKweli(self.cbt_C1.IsExpandable())
        self.assertKweli(self.cbt_f1.IsExpandable())
        self.assertUongo(self.cbt_F1.IsExpandable())

    eleza test_getsublist(self):
        eq = self.assertEqual
        CBT = browser.ChildBrowserTreeItem

        f1sublist = self.cbt_f1.GetSubList()
        self.assertIsInstance(f1sublist[0], CBT)
        eq(len(f1sublist), 1)
        eq(f1sublist[0].name, 'f2')

        eq(self.cbt_F1.GetSubList(), [])

    @mock.patch('idlelib.browser.file_open')
    eleza test_ondoubleclick(self, fopen):
        goto = fopen.rudisha_value.gotoline = mock.Mock()
        self.cbt_F1.OnDoubleClick()
        fopen.assert_called()
        goto.assert_called()
        goto.assert_called_with(self.cbt_F1.obj.lineno)
        # Failure test would have to ashiria OSError ama AttributeError.


kundi NestedChildrenTest(unittest.TestCase):
    "Test that all the nodes kwenye a nested tree are added to the BrowserTree."

    eleza test_nested(self):
        queue = deque()
        actual_names = []
        # The tree items are processed kwenye breadth first order.
        # Verify that processing each sublist hits every node and
        # kwenye the right order.
        expected_names = ['f0', 'C0(base)',
                          'f1', 'c1', 'F1', 'C1()',
                          'f2', 'C2',
                          'F3']
        CBT = browser.ChildBrowserTreeItem
        queue.extend((CBT(f0), CBT(C0)))
        wakati queue:
            cb = queue.popleft()
            sublist = cb.GetSubList()
            queue.extend(sublist)
            self.assertIn(cb.name, cb.GetText())
            self.assertIn(cb.GetIconName(), ('python', 'folder'))
            self.assertIs(cb.IsExpandable(), sublist != [])
            actual_names.append(cb.name)
        self.assertEqual(actual_names, expected_names)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2)
