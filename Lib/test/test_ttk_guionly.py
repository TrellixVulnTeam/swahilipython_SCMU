agiza unittest
kutoka test agiza support

# Skip this test ikiwa _tkinter wasn't built.
support.import_module('_tkinter')

# Skip test ikiwa tk cannot be initialized.
support.requires('gui')

agiza tkinter
kutoka _tkinter agiza TclError
kutoka tkinter agiza ttk
kutoka tkinter.test agiza runtktests

root = None
try:
    root = tkinter.Tk()
    button = ttk.Button(root)
    button.destroy()
    del button
except TclError as msg:
    # assuming ttk is not available
    raise unittest.SkipTest("ttk not available: %s" % msg)
finally:
    ikiwa root is not None:
        root.destroy()
    del root

eleza test_main():
    support.run_unittest(
            *runtktests.get_tests(text=False, packages=['test_ttk']))

ikiwa __name__ == '__main__':
    test_main()
