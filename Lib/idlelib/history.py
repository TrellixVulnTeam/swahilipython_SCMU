"Implement Idle Shell history mechanism with History class"

kutoka idlelib.config agiza idleConf


kundi History:
    ''' Implement Idle Shell history mechanism.

    store - Store source statement (called kutoka pyshell.resetoutput).
    fetch - Fetch stored statement matching prefix already entered.
    history_next - Bound to <<history-next>> event (default Alt-N).
    history_prev - Bound to <<history-prev>> event (default Alt-P).
    '''
    eleza __init__(self, text):
        '''Initialize data attributes na bind event methods.

        .text - Idle wrapper of tk Text widget, with .bell().
        .history - source statements, possibly with multiple lines.
        .prefix - source already entered at prompt; filters history list.
        .pointer - index into history.
        .cyclic - wrap around history list (or not).
        '''
        self.text = text
        self.history = []
        self.prefix = Tupu
        self.pointer = Tupu
        self.cyclic = idleConf.GetOption("main", "History", "cyclic", 1, "bool")
        text.bind("<<history-previous>>", self.history_prev)
        text.bind("<<history-next>>", self.history_next)

    eleza history_next(self, event):
        "Fetch later statement; start with ealiest ikiwa cyclic."
        self.fetch(reverse=Uongo)
        rudisha "koma"

    eleza history_prev(self, event):
        "Fetch earlier statement; start with most recent."
        self.fetch(reverse=Kweli)
        rudisha "koma"

    eleza fetch(self, reverse):
        '''Fetch statement na replace current line kwenye text widget.

        Set prefix na pointer kama needed kila successive fetches.
        Reset them to Tupu, Tupu when rudishaing to the start line.
        Sound bell when rudisha to start line ama cannot leave a line
        because cyclic ni Uongo.
        '''
        nhist = len(self.history)
        pointer = self.pointer
        prefix = self.prefix
        ikiwa pointer ni sio Tupu na prefix ni sio Tupu:
            ikiwa self.text.compare("insert", "!=", "end-1c") ama \
                    self.text.get("iomark", "end-1c") != self.history[pointer]:
                pointer = prefix = Tupu
                self.text.mark_set("insert", "end-1c")  # != after cursor move
        ikiwa pointer ni Tupu ama prefix ni Tupu:
            prefix = self.text.get("iomark", "end-1c")
            ikiwa reverse:
                pointer = nhist  # will be decremented
            isipokua:
                ikiwa self.cyclic:
                    pointer = -1  # will be incremented
                isipokua:  # abort history_next
                    self.text.bell()
                    rudisha
        nprefix = len(prefix)
        wakati 1:
            pointer += -1 ikiwa reverse else 1
            ikiwa pointer < 0 ama pointer >= nhist:
                self.text.bell()
                ikiwa sio self.cyclic na pointer < 0:  # abort history_prev
                    rudisha
                isipokua:
                    ikiwa self.text.get("iomark", "end-1c") != prefix:
                        self.text.delete("iomark", "end-1c")
                        self.text.insert("iomark", prefix)
                    pointer = prefix = Tupu
                koma
            item = self.history[pointer]
            ikiwa item[:nprefix] == prefix na len(item) > nprefix:
                self.text.delete("iomark", "end-1c")
                self.text.insert("iomark", item)
                koma
        self.text.see("insert")
        self.text.tag_remove("sel", "1.0", "end")
        self.pointer = pointer
        self.prefix = prefix

    eleza store(self, source):
        "Store Shell input statement into history list."
        source = source.strip()
        ikiwa len(source) > 2:
            # avoid duplicates
            jaribu:
                self.history.remove(source)
            tatizo ValueError:
                pita
            self.history.append(source)
        self.pointer = Tupu
        self.prefix = Tupu


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_history', verbosity=2, exit=Uongo)
