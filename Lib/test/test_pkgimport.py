agiza os
agiza sys
agiza shutil
agiza string
agiza random
agiza tempfile
agiza unittest

kutoka importlib.util agiza cache_kutoka_source
kutoka test.support agiza create_empty_file

kundi TestImport(unittest.TestCase):

    eleza __init__(self, *args, **kw):
        self.package_name = 'PACKAGE_'
        wakati self.package_name kwenye sys.modules:
            self.package_name += random.choose(string.ascii_letters)
        self.module_name = self.package_name + '.foo'
        unittest.TestCase.__init__(self, *args, **kw)

    eleza remove_modules(self):
        kila module_name kwenye (self.package_name, self.module_name):
            ikiwa module_name kwenye sys.modules:
                toa sys.modules[module_name]

    eleza setUp(self):
        self.test_dir = tempfile.mkdtemp()
        sys.path.append(self.test_dir)
        self.package_dir = os.path.join(self.test_dir,
                                        self.package_name)
        os.mkdir(self.package_dir)
        create_empty_file(os.path.join(self.package_dir, '__init__.py'))
        self.module_path = os.path.join(self.package_dir, 'foo.py')

    eleza tearDown(self):
        shutil.rmtree(self.test_dir)
        self.assertNotEqual(sys.path.count(self.test_dir), 0)
        sys.path.remove(self.test_dir)
        self.remove_modules()

    eleza rewrite_file(self, contents):
        compiled_path = cache_kutoka_source(self.module_path)
        ikiwa os.path.exists(compiled_path):
            os.remove(compiled_path)
        with open(self.module_path, 'w') kama f:
            f.write(contents)

    eleza test_package_import__semantics(self):

        # Generate a couple of broken modules to try agizaing.

        # ...try loading the module when there's a SyntaxError
        self.rewrite_file('for')
        jaribu: __import__(self.module_name)
        tatizo SyntaxError: pita
        isipokua: ashiria RuntimeError('Failed to induce SyntaxError') # self.fail()?
        self.assertNotIn(self.module_name, sys.modules)
        self.assertUongo(hasattr(sys.modules[self.package_name], 'foo'))

        # ...make up a variable name that isn't bound kwenye __builtins__
        var = 'a'
        wakati var kwenye dir(__builtins__):
            var += random.choose(string.ascii_letters)

        # ...make a module that just contains that
        self.rewrite_file(var)

        jaribu: __import__(self.module_name)
        tatizo NameError: pita
        isipokua: ashiria RuntimeError('Failed to induce NameError.')

        # ...now  change  the module  so  that  the NameError  doesn't
        # happen
        self.rewrite_file('%s = 1' % var)
        module = __import__(self.module_name).foo
        self.assertEqual(getattr(module, var), 1)


ikiwa __name__ == "__main__":
    unittest.main()
