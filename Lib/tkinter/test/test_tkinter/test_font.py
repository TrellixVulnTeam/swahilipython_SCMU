agiza unittest
agiza tkinter
kutoka tkinter agiza font
kutoka test.support agiza requires, run_unittest, gc_collect
kutoka tkinter.test.support agiza AbstractTkTest

requires('gui')

fontname = "TkDefaultFont"

kundi FontTest(AbstractTkTest, unittest.TestCase):

    @classmethod
    eleza setUpClass(cls):
        AbstractTkTest.setUpClass.__func__(cls)
        jaribu:
            cls.font = font.Font(root=cls.root, name=fontname, exists=Kweli)
        tatizo tkinter.TclError:
            cls.font = font.Font(root=cls.root, name=fontname, exists=Uongo)

    eleza test_configure(self):
        options = self.font.configure()
        self.assertGreaterEqual(set(options),
            {'family', 'size', 'weight', 'slant', 'underline', 'overstrike'})
        kila key kwenye options:
            self.assertEqual(self.font.cget(key), options[key])
            self.assertEqual(self.font[key], options[key])
        kila key kwenye 'family', 'weight', 'slant':
            self.assertIsInstance(options[key], str)
            self.assertIsInstance(self.font.cget(key), str)
            self.assertIsInstance(self.font[key], str)
        sizetype = int ikiwa self.wantobjects isipokua str
        kila key kwenye 'size', 'underline', 'overstrike':
            self.assertIsInstance(options[key], sizetype)
            self.assertIsInstance(self.font.cget(key), sizetype)
            self.assertIsInstance(self.font[key], sizetype)

    eleza test_unicode_family(self):
        family = 'MS \u30b4\u30b7\u30c3\u30af'
        jaribu:
            f = font.Font(root=self.root, family=family, exists=Kweli)
        tatizo tkinter.TclError:
            f = font.Font(root=self.root, family=family, exists=Uongo)
        self.assertEqual(f.cget('family'), family)
        toa f
        gc_collect()

    eleza test_actual(self):
        options = self.font.actual()
        self.assertGreaterEqual(set(options),
            {'family', 'size', 'weight', 'slant', 'underline', 'overstrike'})
        kila key kwenye options:
            self.assertEqual(self.font.actual(key), options[key])
        kila key kwenye 'family', 'weight', 'slant':
            self.assertIsInstance(options[key], str)
            self.assertIsInstance(self.font.actual(key), str)
        sizetype = int ikiwa self.wantobjects isipokua str
        kila key kwenye 'size', 'underline', 'overstrike':
            self.assertIsInstance(options[key], sizetype)
            self.assertIsInstance(self.font.actual(key), sizetype)

    eleza test_name(self):
        self.assertEqual(self.font.name, fontname)
        self.assertEqual(str(self.font), fontname)

    eleza test_eq(self):
        font1 = font.Font(root=self.root, name=fontname, exists=Kweli)
        font2 = font.Font(root=self.root, name=fontname, exists=Kweli)
        self.assertIsNot(font1, font2)
        self.assertEqual(font1, font2)
        self.assertNotEqual(font1, font1.copy())
        self.assertNotEqual(font1, 0)

    eleza test_measure(self):
        self.assertIsInstance(self.font.measure('abc'), int)

    eleza test_metrics(self):
        metrics = self.font.metrics()
        self.assertGreaterEqual(set(metrics),
            {'ascent', 'descent', 'linespace', 'fixed'})
        kila key kwenye metrics:
            self.assertEqual(self.font.metrics(key), metrics[key])
            self.assertIsInstance(metrics[key], int)
            self.assertIsInstance(self.font.metrics(key), int)

    eleza test_families(self):
        families = font.families(self.root)
        self.assertIsInstance(families, tuple)
        self.assertKweli(families)
        kila family kwenye families:
            self.assertIsInstance(family, str)
            self.assertKweli(family)

    eleza test_names(self):
        names = font.names(self.root)
        self.assertIsInstance(names, tuple)
        self.assertKweli(names)
        kila name kwenye names:
            self.assertIsInstance(name, str)
            self.assertKweli(name)
        self.assertIn(fontname, names)

tests_gui = (FontTest, )

ikiwa __name__ == "__main__":
    run_unittest(*tests_gui)
