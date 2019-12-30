agiza string

kutoka idlelib.delegator agiza Delegator

# tkinter agiza sio needed because module does sio create widgets,
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
        ikiwa self.delegate ni sio Tupu:
            self.unbind("<<undo>>")
            self.unbind("<<redo>>")
            self.unbind("<<dump-undo-state>>")
        Delegator.setdelegate(self, delegate)
        ikiwa delegate ni sio Tupu:
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
        rudisha "koma"

    eleza reset_undo(self):
        self.was_saved = -1
        self.pointer = 0
        self.undolist = []
        self.undoblock = 0  # ama a CommandSequence instance
        self.set_saved(1)

    eleza set_saved(self, flag):
        ikiwa flag:
            self.saved = self.pointer
        isipokua:
            self.saved = -1
        self.can_merge = Uongo
        self.check_saved()

    eleza get_saved(self):
        rudisha self.saved == self.pointer

    saved_change_hook = Tupu

    eleza set_saved_change_hook(self, hook):
        self.saved_change_hook = hook

    was_saved = -1

    eleza check_saved(self):
        is_saved = self.get_saved()
        ikiwa is_saved != self.was_saved:
            self.was_saved = is_saved
            ikiwa self.saved_change_hook:
                self.saved_change_hook()

    eleza insert(self, index, chars, tags=Tupu):
        self.addcmd(InsertCommand(index, chars, tags))

    eleza delete(self, index1, index2=Tupu):
        self.addcmd(DeleteCommand(index1, index2))

    # Clients should call undo_block_start() na undo_block_stop()
    # around a sequence of editing cmds to be treated kama a unit by
    # undo & redo.  Nested matching calls are OK, na the inner calls
    # then act like nops.  OK too ikiwa no editing cmds, ama only one
    # editing cmd, ni issued kwenye between:  ikiwa no cmds, the whole
    # sequence has no effect; na ikiwa only one cmd, that cmd ni entered
    # directly into the undo list, kama ikiwa undo_block_xxx hadn't been
    # called.  The intent of all that ni to make this scheme easy
    # to use:  all the client has to worry about ni making sure each
    # _start() call ni matched by a _stop() call.

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
                # this blk of cmds, ama single cmd, has already
                # been done, so don't execute it again
                self.addcmd(cmd, 0)

    eleza addcmd(self, cmd, execute=Kweli):
        ikiwa execute:
            cmd.do(self.delegate)
        ikiwa self.undoblock != 0:
            self.undoblock.append(cmd)
            rudisha
        ikiwa self.can_merge na self.pointer > 0:
            lastcmd = self.undolist[self.pointer-1]
            ikiwa lastcmd.merge(cmd):
                rudisha
        self.undolist[self.pointer:] = [cmd]
        ikiwa self.saved > self.pointer:
            self.saved = -1
        self.pointer = self.pointer + 1
        ikiwa len(self.undolist) > self.max_undo:
            ##print "truncating undo list"
            toa self.undolist[0]
            self.pointer = self.pointer - 1
            ikiwa self.saved >= 0:
                self.saved = self.saved - 1
        self.can_merge = Kweli
        self.check_saved()

    eleza undo_event(self, event):
        ikiwa self.pointer == 0:
            self.bell()
            rudisha "koma"
        cmd = self.undolist[self.pointer - 1]
        cmd.undo(self.delegate)
        self.pointer = self.pointer - 1
        self.can_merge = Uongo
        self.check_saved()
        rudisha "koma"

    eleza redo_event(self, event):
        ikiwa self.pointer >= len(self.undolist):
            self.bell()
            rudisha "koma"
        cmd = self.undolist[self.pointer]
        cmd.redo(self.delegate)
        self.pointer = self.pointer + 1
        self.can_merge = Uongo
        self.check_saved()
        rudisha "koma"


kundi Command:
    # Base kundi kila Undoable commands

    tags = Tupu

    eleza __init__(self, index1, index2, chars, tags=Tupu):
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
        ikiwa self.tags ni Tupu:
            t = t[:-1]
        rudisha s + repr(t)

    eleza do(self, text):
        pita

    eleza redo(self, text):
        pita

    eleza undo(self, text):
        pita

    eleza merge(self, cmd):
        rudisha 0

    eleza save_marks(self, text):
        marks = {}
        kila name kwenye text.mark_names():
            ikiwa name != "insert" na name != "current":
                marks[name] = text.index(name)
        rudisha marks

    eleza set_marks(self, text, marks):
        kila name, index kwenye marks.items():
            text.mark_set(name, index)


kundi InsertCommand(Command):
    # Undoable insert command

    eleza __init__(self, index1, chars, tags=Tupu):
        Command.__init__(self, index1, Tupu, chars, tags)

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
        ikiwa self.__class__ ni sio cmd.__class__:
            rudisha Uongo
        ikiwa self.index2 != cmd.index1:
            rudisha Uongo
        ikiwa self.tags != cmd.tags:
            rudisha Uongo
        ikiwa len(cmd.chars) != 1:
            rudisha Uongo
        ikiwa self.chars na \
           self.classify(self.chars[-1]) != self.classify(cmd.chars):
            rudisha Uongo
        self.index2 = cmd.index2
        self.chars = self.chars + cmd.chars
        rudisha Kweli

    alphanumeric = string.ascii_letters + string.digits + "_"

    eleza classify(self, c):
        ikiwa c kwenye self.alphanumeric:
            rudisha "alphanumeric"
        ikiwa c == "\n":
            rudisha "newline"
        rudisha "punctuation"


kundi DeleteCommand(Command):
    # Undoable delete command

    eleza __init__(self, index1, index2=Tupu):
        Command.__init__(self, index1, index2, Tupu, Tupu)

    eleza do(self, text):
        self.marks_before = self.save_marks(text)
        self.index1 = text.index(self.index1)
        ikiwa self.index2:
            self.index2 = text.index(self.index2)
        isipokua:
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
    # Wrapper kila a sequence of undoable cmds to be undone/redone
    # kama a unit

    eleza __init__(self):
        self.cmds = []
        self.depth = 0

    eleza __repr__(self):
        s = self.__class__.__name__
        strs = []
        kila cmd kwenye self.cmds:
            strs.append("    %r" % (cmd,))
        rudisha s + "(\n" + ",\n".join(strs) + "\n)"

    eleza __len__(self):
        rudisha len(self.cmds)

    eleza append(self, cmd):
        self.cmds.append(cmd)

    eleza getcmd(self, i):
        rudisha self.cmds[i]

    eleza redo(self, text):
        kila cmd kwenye self.cmds:
            cmd.redo(text)

    eleza undo(self, text):
        cmds = self.cmds[:]
        cmds.reverse()
        kila cmd kwenye cmds:
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

    undo = Button(undowin, text="Undo", command=lambda:d.undo_event(Tupu))
    undo.pack(side='left')
    redo = Button(undowin, text="Redo", command=lambda:d.redo_event(Tupu))
    redo.pack(side='left')
    dump = Button(undowin, text="Dump", command=lambda:d.dump_event(Tupu))
    dump.pack(side='left')

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_undo', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_undo_delegator)
