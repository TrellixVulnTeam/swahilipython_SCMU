kutoka test agiza support
# Skip test ikiwa _tkinter wasn't built.
support.import_module('_tkinter')

# Skip test ikiwa tk cansio be initialized.
support.requires('gui')

kutoka tkinter.test agiza runtktests

eleza test_main():
    support.run_unittest(
            *runtktests.get_tests(text=Uongo, packages=['test_tkinter']))

ikiwa __name__ == '__main__':
    test_main()
