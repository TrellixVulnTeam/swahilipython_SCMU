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

root = Tupu
jaribu:
    root = tkinter.Tk()
    button = ttk.Button(root)
    button.destroy()
    toa button
except TclError as msg:
    # assuming ttk ni sio available
     ashiria unittest.SkipTest("ttk sio available: %s" % msg)
mwishowe:
    ikiwa root ni sio Tupu:
        root.destroy()
    toa root

eleza test_main():
    support.run_unittest(
            *runtktests.get_tests(text=Uongo, packages=['test_ttk']))

ikiwa __name__ == '__main__':
    test_main()
