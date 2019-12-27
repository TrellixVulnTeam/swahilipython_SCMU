agiza string

kutoka idlelib.delegator agiza Delegator

# tkinter agiza not needed because module does not create widgets,
# although many methods operate on text widget arguments.

#$ event <<redo>>
#$ win <Control-y>
#$ unix <Alt-z>

#$ event <<undo>>
#$ win <Control-z>
#$ unix <Control-z>

#$ event <<dump-undo-state>>
#$ win <Control-backslash>
#$ unix <Control-backslash>


kundi UndoDelegator(Delegator):

    max_undo = 1000

    eleza __init__(self):
        Delegator.__init__(self)
        self.reset_undo()

    eleza setdelegate(self, delegate):
        ikiwa self.delegate is not None:
            self.unbind("<<undo>>")
            self.unbind("<<redo>>")
            self.unbind("<<dump-undo-state>>")
        Delegator.setdelegate(self, delegate)
        ikiwa delegate is not None:
            self.bind("<<undo>>", self.undo_event)
            self.bind("<<redo>>", self.redo_event)
            self.bind("<<dump-undo-state>>", self.dump_event)

    eleza dump_event(self, event):
        kutoka pprint agiza pprint
        pandika(self.undolist[:self.pointer])
        andika("pointer:", self.pointer, end=' ')
        andika("saved:", self.saved, end=' ')
        andika("can_merge:", self.can_merge, end=' ')
        andika("get_saved():", self.get_saved())
        pandika(self.undolist[self.pointer:])
        rudisha "break"

    eleza reset_undo(self):
        self.was_saved = -1
        self.pointer = 0
        self.undolist = []
        self.undoblock = 0  # or a CommandSequence instance
        self.set_saved(1)

    eleza set_saved(self, flag):
        ikiwa flag:
            self.saved = self.pointer
        else:
            self.saved = -1
        self.can_merge = False
        self.check_saved()

    eleza get_saved(self):
        rudisha self.saved == self.pointer

    saved_change_hook = None

    eleza set_saved_change_hook(self, hook):
        self.saved_change_hook = hook

    was_saved = -1

    eleza check_saved(self):
        is_saved = self.get_saved()
        ikiwa is_saved != self.was_saved:
            self.was_saved = is_saved
            ikiwa self.saved_change_hook:
                self.saved_change_hook()

    eleza insert(self, index, chars, tags=None):
        self.addcmd(InsertCommand(index, chars, tags))

    eleza delete(self, index1, index2=None):
        self.addcmd(DeleteCommand(index1, index2))

    # Clients should call undo_block_start() and undo_block_stop()
    # around a sequence of editing cmds to be treated as a unit by
    # undo & redo.  Nested matching calls are OK, and the inner calls
    # then act like nops.  OK too ikiwa no editing cmds, or only one
    # editing cmd, is issued in between:  ikiwa no cmds, the whole
    # sequence has no effect; and ikiwa only one cmd, that cmd is entered
    # directly into the undo list, as ikiwa undo_block_xxx hadn't been
    # called.  The intent of all that is to make this scheme easy
    # to use:  all the client has to worry about is making sure each
    # _start() call is matched by a _stop() call.

    eleza undo_block_start(self):
        ikiwa self.undoblock == 0:
            self.undoblock = CommandSequence()
        self.undoblock.bump_depth()

    eleza undo_block_stop(self):
        ikiwa self.undoblock.bump_depth(-1) == 0:
            cmd = self.undoblock
            self.undoblock = 0
            ikiwa len(cmd) > 0:
                ikiwa len(cmd) == 1:
                    # no need to wrap a single cmd
                    cmd = cmd.getcmd(0)
                # this blk of cmds, or single cmd, has already
                # been done, so don't execute it again
                self.addcmd(cmd, 0)

    eleza addcmd(self, cmd, execute=True):
        ikiwa execute:
            cmd.do(self.delegate)
        ikiwa self.undoblock != 0:
            self.undoblock.append(cmd)
            return
        ikiwa self.can_merge and self.pointer > 0:
            lastcmd = self.undolist[self.pointer-1]
            ikiwa lastcmd.merge(cmd):
                return
        self.undolist[self.pointer:] = [cmd]
        ikiwa self.saved > self.pointer:
            self.saved = -1
        self.pointer = self.pointer + 1
        ikiwa len(self.undolist) > self.max_undo:
            ##print "truncating undo list"
            del self.undolist[0]
            self.pointer = self.pointer - 1
            ikiwa self.saved >= 0:
                self.saved = self.saved - 1
        self.can_merge = True
        self.check_saved()

    eleza undo_event(self, event):
        ikiwa self.pointer == 0:
            self.bell()
            rudisha "break"
        cmd = self.undolist[self.pointer - 1]
        cmd.undo(self.delegate)
        self.pointer = self.pointer - 1
        self.can_merge = False
        self.check_saved()
        rudisha "break"

    eleza redo_event(self, event):
        ikiwa self.pointer >= len(self.undolist):
            self.bell()
            rudisha "break"
        cmd = self.undolist[self.pointer]
        cmd.redo(self.delegate)
        self.pointer = self.pointer + 1
        self.can_merge = False
        self.check_saved()
        rudisha "break"


kundi Command:
    # Base kundi for Undoable commands

    tags = None

    eleza __init__(self, index1, index2, chars, tags=None):
        self.marks_before = {}
        self.marks_after = {}
        self.index1 = index1
        self.index2 = index2
        self.chars = chars
        ikiwa tags:
            self.tags = tags

    eleza __repr__(self):
        s = self.__class__.__name__
        t = (self.index1, self.index2, self.chars, self.tags)
        ikiwa self.tags is None:
            t = t[:-1]
        rudisha s + repr(t)

    eleza do(self, text):
        pass

    eleza redo(self, text):
        pass

    eleza undo(self, text):
        pass

    eleza merge(self, cmd):
        rudisha 0

    eleza save_marks(self, text):
        marks = {}
        for name in text.mark_names():
            ikiwa name != "insert" and name != "current":
                marks[name] = text.index(name)
        rudisha marks

    eleza set_marks(self, text, marks):
        for name, index in marks.items():
            text.mark_set(name, index)


kundi InsertCommand(Command):
    # Undoable insert command

    eleza __init__(self, index1, chars, tags=None):
        Command.__init__(self, index1, None, chars, tags)

    eleza do(self, text):
        self.marks_before = self.save_marks(text)
        self.index1 = text.index(self.index1)
        ikiwa text.compare(self.index1, ">", "end-1c"):
            # Insert before the final newline
            self.index1 = text.index("end-1c")
        text.insert(self.index1, self.chars, self.tags)
        self.index2 = text.index("%s+%dc" % (self.index1, len(self.chars)))
        self.marks_after = self.save_marks(text)
        ##sys.__stderr__.write("do: %s\n" % self)

    eleza redo(self, text):
        text.mark_set('insert', self.index1)
        text.insert(self.index1, self.chars, self.tags)
        self.set_marks(text, self.marks_after)
        text.see('insert')
        ##sys.__stderr__.write("redo: %s\n" % self)

    eleza undo(self, text):
        text.mark_set('insert', self.index1)
        text.delete(self.index1, self.index2)
        self.set_marks(text, self.marks_before)
        text.see('insert')
        ##sys.__stderr__.write("undo: %s\n" % self)

    eleza merge(self, cmd):
        ikiwa self.__class__ is not cmd.__class__:
            rudisha False
        ikiwa self.index2 != cmd.index1:
            rudisha False
        ikiwa self.tags != cmd.tags:
            rudisha False
        ikiwa len(cmd.chars) != 1:
            rudisha False
        ikiwa self.chars and \
           self.classify(self.chars[-1]) != self.classify(cmd.chars):
            rudisha False
        self.index2 = cmd.index2
        self.chars = self.chars + cmd.chars
        rudisha True

    alphanumeric = string.ascii_letters + string.digits + "_"

    eleza classify(self, c):
        ikiwa c in self.alphanumeric:
            rudisha "alphanumeric"
        ikiwa c == "\n":
            rudisha "newline"
        rudisha "punctuation"


kundi DeleteCommand(Command):
    # Undoable delete command

    eleza __init__(self, index1, index2=None):
        Command.__init__(self, index1, index2, None, None)

    eleza do(self, text):
        self.marks_before = self.save_marks(text)
        self.index1 = text.index(self.index1)
        ikiwa self.index2:
            self.index2 = text.index(self.index2)
        else:
            self.index2 = text.index(self.index1 + " +1c")
        ikiwa text.compare(self.index2, ">", "end-1c"):
            # Don't delete the final newline
            self.index2 = text.index("end-1c")
        self.chars = text.get(self.index1, self.index2)
        text.delete(self.index1, self.index2)
        self.marks_after = self.save_marks(text)
        ##sys.__stderr__.write("do: %s\n" % self)

    eleza redo(self, text):
        text.mark_set('insert', self.index1)
        text.delete(self.index1, self.index2)
        self.set_marks(text, self.marks_after)
        text.see('insert')
        ##sys.__stderr__.write("redo: %s\n" % self)

    eleza undo(self, text):
        text.mark_set('insert', self.index1)
        text.insert(self.index1, self.chars)
        self.set_marks(text, self.marks_before)
        text.see('insert')
        ##sys.__stderr__.write("undo: %s\n" % self)


kundi CommandSequence(Command):
    # Wrapper for a sequence of undoable cmds to be undone/redone
    # as a unit

    eleza __init__(self):
        self.cmds = []
        self.depth = 0

    eleza __repr__(self):
        s = self.__class__.__name__
        strs = []
        for cmd in self.cmds:
            strs.append("    %r" % (cmd,))
        rudisha s + "(\n" + ",\n".join(strs) + "\n)"

    eleza __len__(self):
        rudisha len(self.cmds)

    eleza append(self, cmd):
        self.cmds.append(cmd)

    eleza getcmd(self, i):
        rudisha self.cmds[i]

    eleza redo(self, text):
        for cmd in self.cmds:
            cmd.redo(text)

    eleza undo(self, text):
        cmds = self.cmds[:]
        cmds.reverse()
        for cmd in cmds:
            cmd.undo(text)

    eleza bump_depth(self, incr=1):
        self.depth = self.depth + incr
        rudisha self.depth


eleza _undo_delegator(parent):  # htest #
    kutoka tkinter agiza Toplevel, Text, Button
    kutoka idlelib.percolator agiza Percolator
    undowin = Toplevel(parent)
    undowin.title("Test UndoDelegator")
    x, y = map(int, parent.geometry().split('+')[1:])
    undowin.geometry("+%d+%d" % (x, y + 175))

    text = Text(undowin, height=10)
    text.pack()
    text.focus_set()
    p = Percolator(text)
    d = UndoDelegator()
    p.insertfilter(d)

    undo = Button(undowin, text="Undo", command=lambda:d.undo_event(None))
    undo.pack(side='left')
    redo = Button(undowin, text="Redo", command=lambda:d.redo_event(None))
    redo.pack(side='left')
    dump = Button(undowin, text="Dump", command=lambda:d.dump_event(None))
    dump.pack(side='left')

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_undo', verbosity=2, exit=False)

    kutoka idlelib.idle_test.htest agiza run
    run(_undo_delegator)
