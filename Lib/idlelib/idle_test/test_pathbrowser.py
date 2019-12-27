"Test pathbrowser, coverage 95%."

kutoka idlelib agiza pathbrowser
agiza unittest
kutoka test.support agiza requires
kutoka tkinter agiza Tk

agiza os.path
agiza pyclbr  # for _modules
agiza sys  # for sys.path

kutoka idlelib.idle_test.mock_idle agiza Func
agiza idlelib  # for __file__
kutoka idlelib agiza browser
kutoka idlelib.tree agiza TreeNode


kundi PathBrowserTest(unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        requires('gui')
        cls.root = Tk()
        cls.root.withdraw()
        cls.pb = pathbrowser.PathBrowser(cls.root, _utest=True)

    @classmethod
    eleza tearDownClass(cls):
        cls.pb.close()
        cls.root.update_idletasks()
        cls.root.destroy()
        del cls.root, cls.pb

    eleza test_init(self):
        pb = self.pb
        eq = self.assertEqual
        eq(pb.master, self.root)
        eq(pyclbr._modules, {})
        self.assertIsInstance(pb.node, TreeNode)
        self.assertIsNotNone(browser.file_open)

    eleza test_settitle(self):
        pb = self.pb
        self.assertEqual(pb.top.title(), 'Path Browser')
        self.assertEqual(pb.top.iconname(), 'Path Browser')

    eleza test_rootnode(self):
        pb = self.pb
        rn = pb.rootnode()
        self.assertIsInstance(rn, pathbrowser.PathBrowserTreeItem)

    eleza test_close(self):
        pb = self.pb
        pb.top.destroy = Func()
        pb.node.destroy = Func()
        pb.close()
        self.assertTrue(pb.top.destroy.called)
        self.assertTrue(pb.node.destroy.called)
        del pb.top.destroy, pb.node.destroy


kundi DirBrowserTreeItemTest(unittest.TestCase):

    eleza test_DirBrowserTreeItem(self):
        # Issue16226 - make sure that getting a sublist works
        d = pathbrowser.DirBrowserTreeItem('')
        d.GetSubList()
        self.assertEqual('', d.GetText())

        dir = os.path.split(os.path.abspath(idlelib.__file__))[0]
        self.assertEqual(d.ispackagedir(dir), True)
        self.assertEqual(d.ispackagedir(dir + '/Icons'), False)


kundi PathBrowserTreeItemTest(unittest.TestCase):

    eleza test_PathBrowserTreeItem(self):
        p = pathbrowser.PathBrowserTreeItem()
        self.assertEqual(p.GetText(), 'sys.path')
        sub = p.GetSubList()
        self.assertEqual(len(sub), len(sys.path))
        self.assertEqual(type(sub[0]), pathbrowser.DirBrowserTreeItem)


ikiwa __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
