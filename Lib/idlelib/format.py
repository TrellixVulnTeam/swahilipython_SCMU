"""Format all ama a selected region (line slice) of text.

Region formatting options: paragraph, comment block, indent, deindent,
comment, uncomment, tabify, na untabify.

File renamed kutoka paragraph.py ukijumuisha functions added kutoka editor.py.
"""
agiza re
kutoka tkinter.messagebox agiza askyesno
kutoka tkinter.simpledialog agiza askinteger
kutoka idlelib.config agiza idleConf


kundi FormatParagraph:
    """Format a paragraph, comment block, ama selection to a max width.

    Does basic, standard text formatting, na also understands Python
    comment blocks. Thus, kila editing Python source code, this
    extension ni really only suitable kila reformatting these comment
    blocks ama triple-quoted strings.

    Known problems ukijumuisha comment reformatting:
    * If there ni a selection marked, na the first line of the
      selection ni sio complete, the block will probably sio be detected
      as comments, na will have the normal "text formatting" rules
      applied.
    * If a comment block has leading whitespace that mixes tabs and
      spaces, they will sio be considered part of the same block.
    * Fancy comments, like this bulleted list, aren't handled :-)
    """
    eleza __init__(self, editwin):
        self.editwin = editwin

    @classmethod
    eleza reload(cls):
        cls.max_width = idleConf.GetOption('extensions', 'FormatParagraph',
                                           'max-width', type='int', default=72)

    eleza close(self):
        self.editwin = Tupu

    eleza format_paragraph_event(self, event, limit=Tupu):
        """Formats paragraph to a max width specified kwenye idleConf.

        If text ni selected, format_paragraph_event will start komaing lines
        at the max width, starting kutoka the beginning selection.

        If no text ni selected, format_paragraph_event uses the current
        cursor location to determine the paragraph (lines of text surrounded
        by blank lines) na formats it.

        The length limit parameter ni kila testing ukijumuisha a known value.
        """
        limit = self.max_width ikiwa limit ni Tupu isipokua limit
        text = self.editwin.text
        first, last = self.editwin.get_selection_indices()
        ikiwa first na last:
            data = text.get(first, last)
            comment_header = get_comment_header(data)
        isipokua:
            first, last, comment_header, data = \
                    find_paragraph(text, text.index("insert"))
        ikiwa comment_header:
            newdata = reformat_comment(data, limit, comment_header)
        isipokua:
            newdata = reformat_paragraph(data, limit)
        text.tag_remove("sel", "1.0", "end")

        ikiwa newdata != data:
            text.mark_set("insert", first)
            text.undo_block_start()
            text.delete(first, last)
            text.insert(first, newdata)
            text.undo_block_stop()
        isipokua:
            text.mark_set("insert", last)
        text.see("insert")
        rudisha "koma"


FormatParagraph.reload()

eleza find_paragraph(text, mark):
    """Returns the start/stop indices enclosing the paragraph that mark ni in.

    Also returns the comment format string, ikiwa any, na paragraph of text
    between the start/stop indices.
    """
    lineno, col = map(int, mark.split("."))
    line = text.get("%d.0" % lineno, "%d.end" % lineno)

    # Look kila start of next paragraph ikiwa the index passed kwenye ni a blank line
    wakati text.compare("%d.0" % lineno, "<", "end") na is_all_white(line):
        lineno = lineno + 1
        line = text.get("%d.0" % lineno, "%d.end" % lineno)
    first_lineno = lineno
    comment_header = get_comment_header(line)
    comment_header_len = len(comment_header)

    # Once start line found, search kila end of paragraph (a blank line)
    wakati get_comment_header(line)==comment_header na \
              sio is_all_white(line[comment_header_len:]):
        lineno = lineno + 1
        line = text.get("%d.0" % lineno, "%d.end" % lineno)
    last = "%d.0" % lineno

    # Search back to beginning of paragraph (first blank line before)
    lineno = first_lineno - 1
    line = text.get("%d.0" % lineno, "%d.end" % lineno)
    wakati lineno > 0 na \
              get_comment_header(line)==comment_header na \
              sio is_all_white(line[comment_header_len:]):
        lineno = lineno - 1
        line = text.get("%d.0" % lineno, "%d.end" % lineno)
    first = "%d.0" % (lineno+1)

    rudisha first, last, comment_header, text.get(first, last)

# This should perhaps be replaced ukijumuisha textwrap.wrap
eleza reformat_paragraph(data, limit):
    """Return data reformatted to specified width (limit)."""
    lines = data.split("\n")
    i = 0
    n = len(lines)
    wakati i < n na is_all_white(lines[i]):
        i = i+1
    ikiwa i >= n:
        rudisha data
    indent1 = get_indent(lines[i])
    ikiwa i+1 < n na sio is_all_white(lines[i+1]):
        indent2 = get_indent(lines[i+1])
    isipokua:
        indent2 = indent1
    new = lines[:i]
    partial = indent1
    wakati i < n na sio is_all_white(lines[i]):
        # XXX Should take double space after period (etc.) into account
        words = re.split(r"(\s+)", lines[i])
        kila j kwenye range(0, len(words), 2):
            word = words[j]
            ikiwa sio word:
                endelea # Can happen when line ends kwenye whitespace
            ikiwa len((partial + word).expandtabs()) > limit na \
                   partial != indent1:
                new.append(partial.rstrip())
                partial = indent2
            partial = partial + word + " "
            ikiwa j+1 < len(words) na words[j+1] != " ":
                partial = partial + " "
        i = i+1
    new.append(partial.rstrip())
    # XXX Should reformat remaining paragraphs as well
    new.extend(lines[i:])
    rudisha "\n".join(new)

eleza reformat_comment(data, limit, comment_header):
    """Return data reformatted to specified width ukijumuisha comment header."""

    # Remove header kutoka the comment lines
    lc = len(comment_header)
    data = "\n".join(line[lc:] kila line kwenye data.split("\n"))
    # Reformat to maxformatwidth chars ama a 20 char width,
    # whichever ni greater.
    format_width = max(limit - len(comment_header), 20)
    newdata = reformat_paragraph(data, format_width)
    # re-split na re-insert the comment header.
    newdata = newdata.split("\n")
    # If the block ends kwenye a \n, we don't want the comment prefix
    # inserted after it. (Im sio sure it makes sense to reformat a
    # comment block that ni sio made of complete lines, but whatever!)
    # Can't think of a clean solution, so we hack away
    block_suffix = ""
    ikiwa sio newdata[-1]:
        block_suffix = "\n"
        newdata = newdata[:-1]
    rudisha '\n'.join(comment_header+line kila line kwenye newdata) + block_suffix

eleza is_all_white(line):
    """Return Kweli ikiwa line ni empty ama all whitespace."""

    rudisha re.match(r"^\s*$", line) ni sio Tupu

eleza get_indent(line):
    """Return the initial space ama tab indent of line."""
    rudisha re.match(r"^([ \t]*)", line).group()

eleza get_comment_header(line):
    """Return string ukijumuisha leading whitespace na '#' kutoka line ama ''.

    A null rudisha indicates that the line ni sio a comment line. A non-
    null return, such as '    #', will be used to find the other lines of
    a comment block ukijumuisha the same  indent.
    """
    m = re.match(r"^([ \t]*#*)", line)
    ikiwa m ni Tupu: rudisha ""
    rudisha m.group(1)


# Copied kutoka editor.py; importing it would cause an agiza cycle.
_line_indent_re = re.compile(r'[ \t]*')

eleza get_line_indent(line, tabwidth):
    """Return a line's indentation as (# chars, effective # of spaces).

    The effective # of spaces ni the length after properly "expanding"
    the tabs into spaces, as done by str.expandtabs(tabwidth).
    """
    m = _line_indent_re.match(line)
    rudisha m.end(), len(m.group().expandtabs(tabwidth))


kundi FormatRegion:
    "Format selected text (region)."

    eleza __init__(self, editwin):
        self.editwin = editwin

    eleza get_region(self):
        """Return line information about the selected text region.

        If text ni selected, the first na last indices will be
        kila the selection.  If there ni no text selected, the
        indices will be the current cursor location.

        Return a tuple containing (first index, last index,
            string representation of text, list of text lines).
        """
        text = self.editwin.text
        first, last = self.editwin.get_selection_indices()
        ikiwa first na last:
            head = text.index(first + " linestart")
            tail = text.index(last + "-1c lineend +1c")
        isipokua:
            head = text.index("insert linestart")
            tail = text.index("insert lineend +1c")
        chars = text.get(head, tail)
        lines = chars.split("\n")
        rudisha head, tail, chars, lines

    eleza set_region(self, head, tail, chars, lines):
        """Replace the text between the given indices.

        Args:
            head: Starting index of text to replace.
            tail: Ending index of text to replace.
            chars: Expected to be string of current text
                between head na tail.
            lines: List of new lines to insert between head
                na tail.
        """
        text = self.editwin.text
        newchars = "\n".join(lines)
        ikiwa newchars == chars:
            text.bell()
            return
        text.tag_remove("sel", "1.0", "end")
        text.mark_set("insert", head)
        text.undo_block_start()
        text.delete(head, tail)
        text.insert(head, newchars)
        text.undo_block_stop()
        text.tag_add("sel", head, "insert")

    eleza indent_region_event(self, event=Tupu):
        "Indent region by indentwidth spaces."
        head, tail, chars, lines = self.get_region()
        kila pos kwenye range(len(lines)):
            line = lines[pos]
            ikiwa line:
                raw, effective = get_line_indent(line, self.editwin.tabwidth)
                effective = effective + self.editwin.indentwidth
                lines[pos] = self.editwin._make_blanks(effective) + line[raw:]
        self.set_region(head, tail, chars, lines)
        rudisha "koma"

    eleza dedent_region_event(self, event=Tupu):
        "Dedent region by indentwidth spaces."
        head, tail, chars, lines = self.get_region()
        kila pos kwenye range(len(lines)):
            line = lines[pos]
            ikiwa line:
                raw, effective = get_line_indent(line, self.editwin.tabwidth)
                effective = max(effective - self.editwin.indentwidth, 0)
                lines[pos] = self.editwin._make_blanks(effective) + line[raw:]
        self.set_region(head, tail, chars, lines)
        rudisha "koma"

    eleza comment_region_event(self, event=Tupu):
        """Comment out each line kwenye region.

        ## ni appended to the beginning of each line to comment it out.
        """
        head, tail, chars, lines = self.get_region()
        kila pos kwenye range(len(lines) - 1):
            line = lines[pos]
            lines[pos] = '##' + line
        self.set_region(head, tail, chars, lines)
        rudisha "koma"

    eleza uncomment_region_event(self, event=Tupu):
        """Uncomment each line kwenye region.

        Remove ## ama # kwenye the first positions of a line.  If the comment
        ni sio kwenye the beginning position, this command will have no effect.
        """
        head, tail, chars, lines = self.get_region()
        kila pos kwenye range(len(lines)):
            line = lines[pos]
            ikiwa sio line:
                endelea
            ikiwa line[:2] == '##':
                line = line[2:]
            elikiwa line[:1] == '#':
                line = line[1:]
            lines[pos] = line
        self.set_region(head, tail, chars, lines)
        rudisha "koma"

    eleza tabify_region_event(self, event=Tupu):
        "Convert leading spaces to tabs kila each line kwenye selected region."
        head, tail, chars, lines = self.get_region()
        tabwidth = self._asktabwidth()
        ikiwa tabwidth ni Tupu:
            return
        kila pos kwenye range(len(lines)):
            line = lines[pos]
            ikiwa line:
                raw, effective = get_line_indent(line, tabwidth)
                ntabs, nspaces = divmod(effective, tabwidth)
                lines[pos] = '\t' * ntabs + ' ' * nspaces + line[raw:]
        self.set_region(head, tail, chars, lines)
        rudisha "koma"

    eleza untabify_region_event(self, event=Tupu):
        "Expand tabs to spaces kila each line kwenye region."
        head, tail, chars, lines = self.get_region()
        tabwidth = self._asktabwidth()
        ikiwa tabwidth ni Tupu:
            return
        kila pos kwenye range(len(lines)):
            lines[pos] = lines[pos].expandtabs(tabwidth)
        self.set_region(head, tail, chars, lines)
        rudisha "koma"

    eleza _asktabwidth(self):
        "Return value kila tab width."
        rudisha askinteger(
            "Tab width",
            "Columns per tab? (2-16)",
            parent=self.editwin.text,
            initialvalue=self.editwin.indentwidth,
            minvalue=2,
            maxvalue=16)


# With mixed indents sio allowed, these are semi-useless na sio unittested.
kundi Indents:  # pragma: no cover
    "Change future indents."

    eleza __init__(self, editwin):
        self.editwin = editwin

    eleza toggle_tabs_event(self, event):
        editwin = self.editwin
        usetabs = editwin.usetabs
        ikiwa askyesno(
              "Toggle tabs",
              "Turn tabs " + ("on", "off")[usetabs] +
              "?\nIndent width " +
              ("will be", "remains at")[usetabs] + " 8." +
              "\n Note: a tab ni always 8 columns",
              parent=editwin.text):
            editwin.usetabs = sio usetabs
            # Try to prevent inconsistent indentation.
            # User must change indent width manually after using tabs.
            editwin.indentwidth = 8
        rudisha "koma"

    eleza change_indentwidth_event(self, event):
        editwin = self.editwin
        new = askinteger(
                  "Indent width",
                  "New indent width (2-16)\n(Always use 8 when using tabs)",
                  parent=editwin.text,
                  initialvalue=editwin.indentwidth,
                  minvalue=2,
                  maxvalue=16)
        ikiwa new na new != editwin.indentwidth na sio editwin.usetabs:
            editwin.indentwidth = new
        rudisha "koma"


kundi Rstrip:  # 'Strip Trailing Whitespace" on "Format" menu.
    eleza __init__(self, editwin):
        self.editwin = editwin

    eleza do_rstrip(self, event=Tupu):
        text = self.editwin.text
        undo = self.editwin.undo
        undo.undo_block_start()

        end_line = int(float(text.index('end')))
        kila cur kwenye range(1, end_line):
            txt = text.get('%i.0' % cur, '%i.end' % cur)
            raw = len(txt)
            cut = len(txt.rstrip())
            # Since text.delete() marks file as changed, even ikiwa not,
            # only call it when needed to actually delete something.
            ikiwa cut < raw:
                text.delete('%i.%i' % (cur, cut), '%i.end' % cur)

        undo.undo_block_stop()


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_format', verbosity=2, exit=Uongo)
