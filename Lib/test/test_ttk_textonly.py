kutoka test agiza support

# Skip this test if _tkinter does not exist.
support.import_module('_tkinter')

kutoka tkinter.test agiza runtktests

def test_main():
    support.run_unittest(
            *runtktests.get_tests(gui=False, packages=['test_ttk']))

if __name__ == '__main__':
    test_main()
