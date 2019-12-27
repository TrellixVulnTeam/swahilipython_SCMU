'''Complete the current word before the cursor with words in the editor.

Each menu selection or shortcut key selection replaces the word with a
different word with the same prefix. The search for matches begins
before the target and moves toward the top of the editor. It then starts
after the cursor and moves down. It then returns to the original word and
the cycle starts again.

Changing the current text line or leaving the cursor in a different
place before requesting the next selection causes AutoExpand to reset
its state.

There is only one instance of Autoexpand.
'''
agiza re
agiza string


kundi AutoExpand:
    wordchars = string.ascii_letters + string.digits + "_"

    eleza __init__(self, editwin):
        self.text = editwin.text
        self.bell = self.text.bell
        self.state = None

    eleza expand_word_event(self, event):
        "Replace the current word with the next expansion."
        curinsert = self.text.index("insert")
        curline = self.text.get("insert linestart", "insert lineend")
        ikiwa not self.state:
            words = self.getwords()
            index = 0
        else:
            words, index, insert, line = self.state
            ikiwa insert != curinsert or line != curline:
                words = self.getwords()
                index = 0
        ikiwa not words:
            self.bell()
            rudisha "break"
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
        rudisha "break"

    eleza getwords(self):
        "Return a list of words that match the prefix before the cursor."
        word = self.getprevword()
        ikiwa not word:
            rudisha []
        before = self.text.get("1.0", "insert wordstart")
        wbefore = re.findall(r"\b" + word + r"\w+\b", before)
        del before
        after = self.text.get("insert wordend", "end")
        wafter = re.findall(r"\b" + word + r"\w+\b", after)
        del after
        ikiwa not wbefore and not wafter:
            rudisha []
        words = []
        dict = {}
        # search backwards through words before
        wbefore.reverse()
        for w in wbefore:
            ikiwa dict.get(w):
                continue
            words.append(w)
            dict[w] = w
        # search onwards through words after
        for w in wafter:
            ikiwa dict.get(w):
                continue
            words.append(w)
            dict[w] = w
        words.append(word)
        rudisha words

    eleza getprevword(self):
        "Return the word prefix before the cursor."
        line = self.text.get("insert linestart", "insert")
        i = len(line)
        while i > 0 and line[i-1] in self.wordchars:
            i = i-1
        rudisha line[i:]


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_autoexpand', verbosity=2)
