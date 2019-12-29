"idlelib.filelist"

agiza os
kutoka tkinter agiza messagebox kama tkMessageBox


kundi FileList:

    # N.B. this agiza overridden kwenye PyShellFileList.
    kutoka idlelib.editor agiza EditorWindow

    eleza __init__(self, root):
        self.root = root
        self.dict = {}
        self.inversedict = {}
        self.vars = {} # For EditorWindow.getrawvar (shared Tcl variables)

    eleza open(self, filename, action=Tupu):
        assert filename
        filename = self.canonize(filename)
        ikiwa os.path.isdir(filename):
            # This can happen when bad filename ni pitaed on command line:
            tkMessageBox.showerror(
                "File Error",
                "%r ni a directory." % (filename,),
                master=self.root)
            rudisha Tupu
        key = os.path.normcase(filename)
        ikiwa key kwenye self.dict:
            edit = self.dict[key]
            edit.top.wakeup()
            rudisha edit
        ikiwa action:
            # Don't create window, perform 'action', e.g. open kwenye same window
            rudisha action(filename)
        isipokua:
            edit = self.EditorWindow(self, filename, key)
            ikiwa edit.good_load:
                rudisha edit
            isipokua:
                edit._close()
                rudisha Tupu

    eleza gotofileline(self, filename, lineno=Tupu):
        edit = self.open(filename)
        ikiwa edit ni sio Tupu na lineno ni sio Tupu:
            edit.gotoline(lineno)

    eleza new(self, filename=Tupu):
        rudisha self.EditorWindow(self, filename)

    eleza close_all_callback(self, *args, **kwds):
        kila edit kwenye list(self.inversedict):
            reply = edit.close()
            ikiwa reply == "cancel":
                koma
        rudisha "koma"

    eleza unregister_maybe_terminate(self, edit):
        jaribu:
            key = self.inversedict[edit]
        tatizo KeyError:
            andika("Don't know this EditorWindow object.  (close)")
            rudisha
        ikiwa key:
            toa self.dict[key]
        toa self.inversedict[edit]
        ikiwa sio self.inversedict:
            self.root.quit()

    eleza filename_changed_edit(self, edit):
        edit.saved_change_hook()
        jaribu:
            key = self.inversedict[edit]
        tatizo KeyError:
            andika("Don't know this EditorWindow object.  (rename)")
            rudisha
        filename = edit.io.filename
        ikiwa sio filename:
            ikiwa key:
                toa self.dict[key]
            self.inversedict[edit] = Tupu
            rudisha
        filename = self.canonize(filename)
        newkey = os.path.normcase(filename)
        ikiwa newkey == key:
            rudisha
        ikiwa newkey kwenye self.dict:
            conflict = self.dict[newkey]
            self.inversedict[conflict] = Tupu
            tkMessageBox.showerror(
                "Name Conflict",
                "You now have multiple edit windows open kila %r" % (filename,),
                master=self.root)
        self.dict[newkey] = edit
        self.inversedict[edit] = newkey
        ikiwa key:
            jaribu:
                toa self.dict[key]
            tatizo KeyError:
                pita

    eleza canonize(self, filename):
        ikiwa sio os.path.isabs(filename):
            jaribu:
                pwd = os.getcwd()
            tatizo OSError:
                pita
            isipokua:
                filename = os.path.join(pwd, filename)
        rudisha os.path.normpath(filename)


eleza _test():  # TODO check na convert to htest
    kutoka tkinter agiza Tk
    kutoka idlelib.editor agiza fixwordkomas
    kutoka idlelib.run agiza fix_scaling
    root = Tk()
    fix_scaling(root)
    fixwordkomas(root)
    root.withdraw()
    flist = FileList(root)
    flist.new()
    ikiwa flist.inversedict:
        root.mainloop()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_filelist', verbosity=2)

#    _test()
