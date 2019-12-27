"idlelib.filelist"

agiza os
kutoka tkinter agiza messagebox as tkMessageBox


kundi FileList:

    # N.B. this agiza overridden in PyShellFileList.
    kutoka idlelib.editor agiza EditorWindow

    eleza __init__(self, root):
        self.root = root
        self.dict = {}
        self.inversedict = {}
        self.vars = {} # For EditorWindow.getrawvar (shared Tcl variables)

    eleza open(self, filename, action=None):
        assert filename
        filename = self.canonize(filename)
        ikiwa os.path.isdir(filename):
            # This can happen when bad filename is passed on command line:
            tkMessageBox.showerror(
                "File Error",
                "%r is a directory." % (filename,),
                master=self.root)
            rudisha None
        key = os.path.normcase(filename)
        ikiwa key in self.dict:
            edit = self.dict[key]
            edit.top.wakeup()
            rudisha edit
        ikiwa action:
            # Don't create window, perform 'action', e.g. open in same window
            rudisha action(filename)
        else:
            edit = self.EditorWindow(self, filename, key)
            ikiwa edit.good_load:
                rudisha edit
            else:
                edit._close()
                rudisha None

    eleza gotofileline(self, filename, lineno=None):
        edit = self.open(filename)
        ikiwa edit is not None and lineno is not None:
            edit.gotoline(lineno)

    eleza new(self, filename=None):
        rudisha self.EditorWindow(self, filename)

    eleza close_all_callback(self, *args, **kwds):
        for edit in list(self.inversedict):
            reply = edit.close()
            ikiwa reply == "cancel":
                break
        rudisha "break"

    eleza unregister_maybe_terminate(self, edit):
        try:
            key = self.inversedict[edit]
        except KeyError:
            andika("Don't know this EditorWindow object.  (close)")
            return
        ikiwa key:
            del self.dict[key]
        del self.inversedict[edit]
        ikiwa not self.inversedict:
            self.root.quit()

    eleza filename_changed_edit(self, edit):
        edit.saved_change_hook()
        try:
            key = self.inversedict[edit]
        except KeyError:
            andika("Don't know this EditorWindow object.  (rename)")
            return
        filename = edit.io.filename
        ikiwa not filename:
            ikiwa key:
                del self.dict[key]
            self.inversedict[edit] = None
            return
        filename = self.canonize(filename)
        newkey = os.path.normcase(filename)
        ikiwa newkey == key:
            return
        ikiwa newkey in self.dict:
            conflict = self.dict[newkey]
            self.inversedict[conflict] = None
            tkMessageBox.showerror(
                "Name Conflict",
                "You now have multiple edit windows open for %r" % (filename,),
                master=self.root)
        self.dict[newkey] = edit
        self.inversedict[edit] = newkey
        ikiwa key:
            try:
                del self.dict[key]
            except KeyError:
                pass

    eleza canonize(self, filename):
        ikiwa not os.path.isabs(filename):
            try:
                pwd = os.getcwd()
            except OSError:
                pass
            else:
                filename = os.path.join(pwd, filename)
        rudisha os.path.normpath(filename)


eleza _test():  # TODO check and convert to htest
    kutoka tkinter agiza Tk
    kutoka idlelib.editor agiza fixwordbreaks
    kutoka idlelib.run agiza fix_scaling
    root = Tk()
    fix_scaling(root)
    fixwordbreaks(root)
    root.withdraw()
    flist = FileList(root)
    flist.new()
    ikiwa flist.inversedict:
        root.mainloop()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_filelist', verbosity=2)

#    _test()
