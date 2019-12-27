# Test packages (dotted-name agiza)

agiza sys
agiza os
agiza tempfile
agiza textwrap
agiza unittest


# Helpers to create and destroy hierarchies.

eleza cleanout(root):
    names = os.listdir(root)
    for name in names:
        fullname = os.path.join(root, name)
        ikiwa os.path.isdir(fullname) and not os.path.islink(fullname):
            cleanout(fullname)
        else:
            os.remove(fullname)
    os.rmdir(root)

eleza fixdir(lst):
    ikiwa "__builtins__" in lst:
        lst.remove("__builtins__")
    ikiwa "__initializing__" in lst:
        lst.remove("__initializing__")
    rudisha lst


# XXX Things to test
#
# agiza package without __init__
# agiza package with __init__
# __init__ agizaing submodule
# __init__ agizaing global module
# __init__ defining variables
# submodule agizaing other submodule
# submodule agizaing global module
# submodule agiza submodule via global name
# kutoka package agiza submodule
# kutoka package agiza subpackage
# kutoka package agiza variable (defined in __init__)
# kutoka package agiza * (defined in __init__)


kundi TestPkg(unittest.TestCase):

    eleza setUp(self):
        self.root = None
        self.pkgname = None
        self.syspath = list(sys.path)
        self.modules_to_cleanup = set()  # Populated by mkhier().

    eleza tearDown(self):
        sys.path[:] = self.syspath
        for modulename in self.modules_to_cleanup:
            ikiwa modulename in sys.modules:
                del sys.modules[modulename]
        ikiwa self.root: # Only clean ikiwa the test was actually run
            cleanout(self.root)

        # delete all modules concerning the tested hierarchy
        ikiwa self.pkgname:
            modules = [name for name in sys.modules
                       ikiwa self.pkgname in name.split('.')]
            for name in modules:
                del sys.modules[name]

    eleza run_code(self, code):
        exec(textwrap.dedent(code), globals(), {"self": self})

    eleza mkhier(self, descr):
        root = tempfile.mkdtemp()
        sys.path.insert(0, root)
        ikiwa not os.path.isdir(root):
            os.mkdir(root)
        for name, contents in descr:
            comps = name.split()
            self.modules_to_cleanup.add('.'.join(comps))
            fullname = root
            for c in comps:
                fullname = os.path.join(fullname, c)
            ikiwa contents is None:
                os.mkdir(fullname)
            else:
                with open(fullname, "w") as f:
                    f.write(contents)
                    ikiwa not contents.endswith('\n'):
                        f.write('\n')
        self.root = root
        # package name is the name of the first item
        self.pkgname = descr[0][0]

    eleza test_1(self):
        hier = [("t1", None), ("t1 __init__.py", "")]
        self.mkhier(hier)
        agiza t1

    eleza test_2(self):
        hier = [
         ("t2", None),
         ("t2 __init__.py", "'doc for t2'"),
         ("t2 sub", None),
         ("t2 sub __init__.py", ""),
         ("t2 sub subsub", None),
         ("t2 sub subsub __init__.py", "spam = 1"),
        ]
        self.mkhier(hier)

        agiza t2.sub
        agiza t2.sub.subsub
        self.assertEqual(t2.__name__, "t2")
        self.assertEqual(t2.sub.__name__, "t2.sub")
        self.assertEqual(t2.sub.subsub.__name__, "t2.sub.subsub")

        # This exec crap is needed because Py3k forbids 'agiza *' outside
        # of module-scope and __import__() is insufficient for what we need.
        s = """
            agiza t2
            kutoka t2 agiza *
            self.assertEqual(dir(), ['self', 'sub', 't2'])
            """
        self.run_code(s)

        kutoka t2 agiza sub
        kutoka t2.sub agiza subsub
        kutoka t2.sub.subsub agiza spam
        self.assertEqual(sub.__name__, "t2.sub")
        self.assertEqual(subsub.__name__, "t2.sub.subsub")
        self.assertEqual(sub.subsub.__name__, "t2.sub.subsub")
        for name in ['spam', 'sub', 'subsub', 't2']:
            self.assertTrue(locals()["name"], "Failed to agiza %s" % name)

        agiza t2.sub
        agiza t2.sub.subsub
        self.assertEqual(t2.__name__, "t2")
        self.assertEqual(t2.sub.__name__, "t2.sub")
        self.assertEqual(t2.sub.subsub.__name__, "t2.sub.subsub")

        s = """
            kutoka t2 agiza *
            self.assertEqual(dir(), ['self', 'sub'])
            """
        self.run_code(s)

    eleza test_3(self):
        hier = [
                ("t3", None),
                ("t3 __init__.py", ""),
                ("t3 sub", None),
                ("t3 sub __init__.py", ""),
                ("t3 sub subsub", None),
                ("t3 sub subsub __init__.py", "spam = 1"),
               ]
        self.mkhier(hier)

        agiza t3.sub.subsub
        self.assertEqual(t3.__name__, "t3")
        self.assertEqual(t3.sub.__name__, "t3.sub")
        self.assertEqual(t3.sub.subsub.__name__, "t3.sub.subsub")

    eleza test_4(self):
        hier = [
        ("t4.py", "raise RuntimeError('Shouldnt load t4.py')"),
        ("t4", None),
        ("t4 __init__.py", ""),
        ("t4 sub.py", "raise RuntimeError('Shouldnt load sub.py')"),
        ("t4 sub", None),
        ("t4 sub __init__.py", ""),
        ("t4 sub subsub.py",
         "raise RuntimeError('Shouldnt load subsub.py')"),
        ("t4 sub subsub", None),
        ("t4 sub subsub __init__.py", "spam = 1"),
               ]
        self.mkhier(hier)

        s = """
            kutoka t4.sub.subsub agiza *
            self.assertEqual(spam, 1)
            """
        self.run_code(s)

    eleza test_5(self):
        hier = [
        ("t5", None),
        ("t5 __init__.py", "agiza t5.foo"),
        ("t5 string.py", "spam = 1"),
        ("t5 foo.py",
         "kutoka . agiza string; assert string.spam == 1"),
         ]
        self.mkhier(hier)

        agiza t5
        s = """
            kutoka t5 agiza *
            self.assertEqual(dir(), ['foo', 'self', 'string', 't5'])
            """
        self.run_code(s)

        agiza t5
        self.assertEqual(fixdir(dir(t5)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__path__', '__spec__',
                          'foo', 'string', 't5'])
        self.assertEqual(fixdir(dir(t5.foo)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__spec__', 'string'])
        self.assertEqual(fixdir(dir(t5.string)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__spec__', 'spam'])

    eleza test_6(self):
        hier = [
                ("t6", None),
                ("t6 __init__.py",
                 "__all__ = ['spam', 'ham', 'eggs']"),
                ("t6 spam.py", ""),
                ("t6 ham.py", ""),
                ("t6 eggs.py", ""),
               ]
        self.mkhier(hier)

        agiza t6
        self.assertEqual(fixdir(dir(t6)),
                         ['__all__', '__cached__', '__doc__', '__file__',
                          '__loader__', '__name__', '__package__', '__path__',
                          '__spec__'])
        s = """
            agiza t6
            kutoka t6 agiza *
            self.assertEqual(fixdir(dir(t6)),
                             ['__all__', '__cached__', '__doc__', '__file__',
                              '__loader__', '__name__', '__package__',
                              '__path__', '__spec__', 'eggs', 'ham', 'spam'])
            self.assertEqual(dir(), ['eggs', 'ham', 'self', 'spam', 't6'])
            """
        self.run_code(s)

    eleza test_7(self):
        hier = [
                ("t7.py", ""),
                ("t7", None),
                ("t7 __init__.py", ""),
                ("t7 sub.py",
                 "raise RuntimeError('Shouldnt load sub.py')"),
                ("t7 sub", None),
                ("t7 sub __init__.py", ""),
                ("t7 sub .py",
                 "raise RuntimeError('Shouldnt load subsub.py')"),
                ("t7 sub subsub", None),
                ("t7 sub subsub __init__.py",
                 "spam = 1"),
               ]
        self.mkhier(hier)


        t7, sub, subsub = None, None, None
        agiza t7 as tas
        self.assertEqual(fixdir(dir(tas)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__path__', '__spec__'])
        self.assertFalse(t7)
        kutoka t7 agiza sub as subpar
        self.assertEqual(fixdir(dir(subpar)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__path__', '__spec__'])
        self.assertFalse(t7)
        self.assertFalse(sub)
        kutoka t7.sub agiza subsub as subsubsub
        self.assertEqual(fixdir(dir(subsubsub)),
                         ['__cached__', '__doc__', '__file__', '__loader__',
                          '__name__', '__package__', '__path__', '__spec__',
                          'spam'])
        self.assertFalse(t7)
        self.assertFalse(sub)
        self.assertFalse(subsub)
        kutoka t7.sub.subsub agiza spam as ham
        self.assertEqual(ham, 1)
        self.assertFalse(t7)
        self.assertFalse(sub)
        self.assertFalse(subsub)

    @unittest.skipIf(sys.flags.optimize >= 2,
                     "Docstrings are omitted with -O2 and above")
    eleza test_8(self):
        hier = [
                ("t8", None),
                ("t8 __init__"+os.extsep+"py", "'doc for t8'"),
               ]
        self.mkhier(hier)

        agiza t8
        self.assertEqual(t8.__doc__, "doc for t8")

ikiwa __name__ == "__main__":
    unittest.main()
