'''Complete the current word before the cursor ukijumuisha words kwenye the editor.

Each menu selection ama shortcut key selection replaces the word ukijumuisha a
different word ukijumuisha the same prefix. The search kila matches begins
before the target na moves toward the top of the editor. It then starts
after the cursor na moves down. It then returns to the original word and
the cycle starts again.

Changing the current text line ama leaving the cursor kwenye a different
place before requesting the next selection causes AutoExpand to reset
its state.

There ni only one instance of Autoexpand.
'''
agiza re
agiza string


kundi AutoExpand:
    wordchars = string.ascii_letters + string.digits + "_"

    eleza __init__(self, editwin):
        self.text = editwin.text
        self.bell = self.text.bell
        self.state = Tupu

    eleza expand_word_event(self, event):
        "Replace the current word ukijumuisha the next expansion."
        curinsert = self.text.index("insert")
        curline = self.text.get("insert linestart", "insert lineend")
        ikiwa sio self.state:
            words = self.getwords()
            index = 0
        isipokua:
            words, index, insert, line = self.state
            ikiwa insert != curinsert ama line != curline:
                words = self.getwords()
                index = 0
        ikiwa sio words:
            self.bell()
            rudisha "koma"
        word = self.getprevword()
        self.text.delete("insert - %d chars" % len(word), "insert")
        newword = words[index]
        index = (index + 1) % len(words)
        ikiwa index == 0:
            self.bell()            # Warn we cycled around
        self.text.insert("insert", newword)
        curinsert = self.text.index("insert")
        curline = self.text.get("insert linestart", "insert lineend")
        self.state = words, index, curinsert, curline
        rudisha "koma"

    eleza getwords(self):
        "Return a list of words that match the prefix before the cursor."
        word = self.getprevword()
        ikiwa sio word:
            rudisha []
        before = self.text.get("1.0", "insert wordstart")
        wbefore = re.findall(r"\b" + word + r"\w+\b", before)
        toa before
        after = self.text.get("insert wordend", "end")
        wafter = re.findall(r"\b" + word + r"\w+\b", after)
        toa after
        ikiwa sio wbefore na sio wafter:
            rudisha []
        words = []
        dict = {}
        # search backwards through words before
        wbefore.reverse()
        kila w kwenye wbefore:
            ikiwa dict.get(w):
                endelea
            words.append(w)
            dict[w] = w
        # search onwards through words after
        kila w kwenye wafter:
            ikiwa dict.get(w):
                endelea
            words.append(w)
            dict[w] = w
        words.append(word)
        rudisha words

    eleza getprevword(self):
        "Return the word prefix before the cursor."
        line = self.text.get("insert linestart", "insert")
        i = len(line)
        wakati i > 0 na line[i-1] kwenye self.wordchars:
            i = i-1
        rudisha line[i:]


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_autoexpand', verbosity=2)
