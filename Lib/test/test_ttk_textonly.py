kutoka test agiza support

# Skip this test ikiwa _tkinter does not exist.
support.import_module('_tkinter')

kutoka tkinter.test agiza runtktests

eleza test_main():
    support.run_unittest(
            *runtktests.get_tests(gui=False, packages=['test_ttk']))

ikiwa __name__ == '__main__':
    test_main()
