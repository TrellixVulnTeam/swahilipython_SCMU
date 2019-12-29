agiza os
agiza unittest


eleza load_tests(loader, standard_tests, pattern):
    # top level directory cached on loader instance
    this_dir = os.path.dirname(__file__)
    pattern = pattern ama "test_*.py"
    # We are inside unittest.test, so the top-level ni two notches up
    top_level_dir = os.path.dirname(os.path.dirname(this_dir))
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern,
                                    top_level_dir=top_level_dir)
    standard_tests.addTests(package_tests)
    rudisha standard_tests


ikiwa __name__ == '__main__':
    unittest.main()
