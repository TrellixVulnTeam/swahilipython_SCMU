"""Generic output formatting.

Formatter objects transform an abstract flow of formatting events into
specific output events on writer objects. Formatters manage several stack
structures to allow various properties of a writer object to be changed and
restored; writers need not be able to handle relative changes nor any sort
of ``change back'' operation. Specific writer properties which may be
controlled via formatter objects are horizontal alignment, font, and left
margin indentations. A mechanism is provided which supports providing
arbitrary, non-exclusive style settings to a writer as well. Additional
interfaces facilitate formatting events which are not reversible, such as
paragraph separation.

Writer objects encapsulate device interfaces. Abstract devices, such as
file formats, are supported as well as physical devices. The provided
implementations all work with abstract devices. The interface makes
available mechanisms for setting the properties which formatter objects
manage and inserting data into the output.
"""

agiza sys
agiza warnings
warnings.warn('the formatter module is deprecated', DeprecationWarning,
              stacklevel=2)


AS_IS = None


kundi NullFormatter:
    """A formatter which does nothing.

    If the writer parameter is omitted, a NullWriter instance is created.
    No methods of the writer are called by NullFormatter instances.

    Implementations should inherit kutoka this kundi ikiwa implementing a writer
    interface but don't need to inherit any implementation.

    """

    eleza __init__(self, writer=None):
        ikiwa writer is None:
            writer = NullWriter()
        self.writer = writer
    eleza end_paragraph(self, blankline): pass
    eleza add_line_break(self): pass
    eleza add_hor_rule(self, *args, **kw): pass
    eleza add_label_data(self, format, counter, blankline=None): pass
    eleza add_flowing_data(self, data): pass
    eleza add_literal_data(self, data): pass
    eleza flush_softspace(self): pass
    eleza push_alignment(self, align): pass
    eleza pop_alignment(self): pass
    eleza push_font(self, x): pass
    eleza pop_font(self): pass
    eleza push_margin(self, margin): pass
    eleza pop_margin(self): pass
    eleza set_spacing(self, spacing): pass
    eleza push_style(self, *styles): pass
    eleza pop_style(self, n=1): pass
    eleza assert_line_data(self, flag=1): pass


kundi AbstractFormatter:
    """The standard formatter.

    This implementation has demonstrated wide applicability to many writers,
    and may be used directly in most circumstances.  It has been used to
    implement a full-featured World Wide Web browser.

    """

    #  Space handling policy:  blank spaces at the boundary between elements
    #  are handled by the outermost context.  "Literal" data is not checked
    #  to determine context, so spaces in literal data are handled directly
    #  in all circumstances.

    eleza __init__(self, writer):
        self.writer = writer            # Output device
        self.align = None               # Current alignment
        self.align_stack = []           # Alignment stack
        self.font_stack = []            # Font state
        self.margin_stack = []          # Margin state
        self.spacing = None             # Vertical spacing state
        self.style_stack = []           # Other state, e.g. color
        self.nospace = 1                # Should leading space be suppressed
        self.softspace = 0              # Should a space be inserted
        self.para_end = 1               # Just ended a paragraph
        self.parskip = 0                # Skipped space between paragraphs?
        self.hard_break = 1             # Have a hard break
        self.have_label = 0

    eleza end_paragraph(self, blankline):
        ikiwa not self.hard_break:
            self.writer.send_line_break()
            self.have_label = 0
        ikiwa self.parskip < blankline and not self.have_label:
            self.writer.send_paragraph(blankline - self.parskip)
            self.parskip = blankline
            self.have_label = 0
        self.hard_break = self.nospace = self.para_end = 1
        self.softspace = 0

    eleza add_line_break(self):
        ikiwa not (self.hard_break or self.para_end):
            self.writer.send_line_break()
            self.have_label = self.parskip = 0
        self.hard_break = self.nospace = 1
        self.softspace = 0

    eleza add_hor_rule(self, *args, **kw):
        ikiwa not self.hard_break:
            self.writer.send_line_break()
        self.writer.send_hor_rule(*args, **kw)
        self.hard_break = self.nospace = 1
        self.have_label = self.para_end = self.softspace = self.parskip = 0

    eleza add_label_data(self, format, counter, blankline = None):
        ikiwa self.have_label or not self.hard_break:
            self.writer.send_line_break()
        ikiwa not self.para_end:
            self.writer.send_paragraph((blankline and 1) or 0)
        ikiwa isinstance(format, str):
            self.writer.send_label_data(self.format_counter(format, counter))
        else:
            self.writer.send_label_data(format)
        self.nospace = self.have_label = self.hard_break = self.para_end = 1
        self.softspace = self.parskip = 0

    eleza format_counter(self, format, counter):
        label = ''
        for c in format:
            ikiwa c == '1':
                label = label + ('%d' % counter)
            elikiwa c in 'aA':
                ikiwa counter > 0:
                    label = label + self.format_letter(c, counter)
            elikiwa c in 'iI':
                ikiwa counter > 0:
                    label = label + self.format_roman(c, counter)
            else:
                label = label + c
        rudisha label

    eleza format_letter(self, case, counter):
        label = ''
        while counter > 0:
            counter, x = divmod(counter-1, 26)
            # This makes a strong assumption that lowercase letters
            # and uppercase letters form two contiguous blocks, with
            # letters in order!
            s = chr(ord(case) + x)
            label = s + label
        rudisha label

    eleza format_roman(self, case, counter):
        ones = ['i', 'x', 'c', 'm']
        fives = ['v', 'l', 'd']
        label, index = '', 0
        # This will die of IndexError when counter is too big
        while counter > 0:
            counter, x = divmod(counter, 10)
            ikiwa x == 9:
                label = ones[index] + ones[index+1] + label
            elikiwa x == 4:
                label = ones[index] + fives[index] + label
            else:
                ikiwa x >= 5:
                    s = fives[index]
                    x = x-5
                else:
                    s = ''
                s = s + ones[index]*x
                label = s + label
            index = index + 1
        ikiwa case == 'I':
            rudisha label.upper()
        rudisha label

    eleza add_flowing_data(self, data):
        ikiwa not data: return
        prespace = data[:1].isspace()
        postspace = data[-1:].isspace()
        data = " ".join(data.split())
        ikiwa self.nospace and not data:
            return
        elikiwa prespace or self.softspace:
            ikiwa not data:
                ikiwa not self.nospace:
                    self.softspace = 1
                    self.parskip = 0
                return
            ikiwa not self.nospace:
                data = ' ' + data
        self.hard_break = self.nospace = self.para_end = \
                          self.parskip = self.have_label = 0
        self.softspace = postspace
        self.writer.send_flowing_data(data)

    eleza add_literal_data(self, data):
        ikiwa not data: return
        ikiwa self.softspace:
            self.writer.send_flowing_data(" ")
        self.hard_break = data[-1:] == '\n'
        self.nospace = self.para_end = self.softspace = \
                       self.parskip = self.have_label = 0
        self.writer.send_literal_data(data)

    eleza flush_softspace(self):
        ikiwa self.softspace:
            self.hard_break = self.para_end = self.parskip = \
                              self.have_label = self.softspace = 0
            self.nospace = 1
            self.writer.send_flowing_data(' ')

    eleza push_alignment(self, align):
        ikiwa align and align != self.align:
            self.writer.new_alignment(align)
            self.align = align
            self.align_stack.append(align)
        else:
            self.align_stack.append(self.align)

    eleza pop_alignment(self):
        ikiwa self.align_stack:
            del self.align_stack[-1]
        ikiwa self.align_stack:
            self.align = align = self.align_stack[-1]
            self.writer.new_alignment(align)
        else:
            self.align = None
            self.writer.new_alignment(None)

    eleza push_font(self, font):
        size, i, b, tt = font
        ikiwa self.softspace:
            self.hard_break = self.para_end = self.softspace = 0
            self.nospace = 1
            self.writer.send_flowing_data(' ')
        ikiwa self.font_stack:
            csize, ci, cb, ctt = self.font_stack[-1]
            ikiwa size is AS_IS: size = csize
            ikiwa i is AS_IS: i = ci
            ikiwa b is AS_IS: b = cb
            ikiwa tt is AS_IS: tt = ctt
        font = (size, i, b, tt)
        self.font_stack.append(font)
        self.writer.new_font(font)

    eleza pop_font(self):
        ikiwa self.font_stack:
            del self.font_stack[-1]
        ikiwa self.font_stack:
            font = self.font_stack[-1]
        else:
            font = None
        self.writer.new_font(font)

    eleza push_margin(self, margin):
        self.margin_stack.append(margin)
        fstack = [m for m in self.margin_stack ikiwa m]
        ikiwa not margin and fstack:
            margin = fstack[-1]
        self.writer.new_margin(margin, len(fstack))

    eleza pop_margin(self):
        ikiwa self.margin_stack:
            del self.margin_stack[-1]
        fstack = [m for m in self.margin_stack ikiwa m]
        ikiwa fstack:
            margin = fstack[-1]
        else:
            margin = None
        self.writer.new_margin(margin, len(fstack))

    eleza set_spacing(self, spacing):
        self.spacing = spacing
        self.writer.new_spacing(spacing)

    eleza push_style(self, *styles):
        ikiwa self.softspace:
            self.hard_break = self.para_end = self.softspace = 0
            self.nospace = 1
            self.writer.send_flowing_data(' ')
        for style in styles:
            self.style_stack.append(style)
        self.writer.new_styles(tuple(self.style_stack))

    eleza pop_style(self, n=1):
        del self.style_stack[-n:]
        self.writer.new_styles(tuple(self.style_stack))

    eleza assert_line_data(self, flag=1):
        self.nospace = self.hard_break = not flag
        self.para_end = self.parskip = self.have_label = 0


kundi NullWriter:
    """Minimal writer interface to use in testing & inheritance.

    A writer which only provides the interface definition; no actions are
    taken on any methods.  This should be the base kundi for all writers
    which do not need to inherit any implementation methods.

    """
    eleza __init__(self): pass
    eleza flush(self): pass
    eleza new_alignment(self, align): pass
    eleza new_font(self, font): pass
    eleza new_margin(self, margin, level): pass
    eleza new_spacing(self, spacing): pass
    eleza new_styles(self, styles): pass
    eleza send_paragraph(self, blankline): pass
    eleza send_line_break(self): pass
    eleza send_hor_rule(self, *args, **kw): pass
    eleza send_label_data(self, data): pass
    eleza send_flowing_data(self, data): pass
    eleza send_literal_data(self, data): pass


kundi AbstractWriter(NullWriter):
    """A writer which can be used in debugging formatters, but not much else.

    Each method simply announces itself by printing its name and
    arguments on standard output.

    """

    eleza new_alignment(self, align):
        andika("new_alignment(%r)" % (align,))

    eleza new_font(self, font):
        andika("new_font(%r)" % (font,))

    eleza new_margin(self, margin, level):
        andika("new_margin(%r, %d)" % (margin, level))

    eleza new_spacing(self, spacing):
        andika("new_spacing(%r)" % (spacing,))

    eleza new_styles(self, styles):
        andika("new_styles(%r)" % (styles,))

    eleza send_paragraph(self, blankline):
        andika("send_paragraph(%r)" % (blankline,))

    eleza send_line_break(self):
        andika("send_line_break()")

    eleza send_hor_rule(self, *args, **kw):
        andika("send_hor_rule()")

    eleza send_label_data(self, data):
        andika("send_label_data(%r)" % (data,))

    eleza send_flowing_data(self, data):
        andika("send_flowing_data(%r)" % (data,))

    eleza send_literal_data(self, data):
        andika("send_literal_data(%r)" % (data,))


kundi DumbWriter(NullWriter):
    """Simple writer kundi which writes output on the file object passed in
    as the file parameter or, ikiwa file is omitted, on standard output.  The
    output is simply word-wrapped to the number of columns specified by
    the maxcol parameter.  This kundi is suitable for reflowing a sequence
    of paragraphs.

    """

    eleza __init__(self, file=None, maxcol=72):
        self.file = file or sys.stdout
        self.maxcol = maxcol
        NullWriter.__init__(self)
        self.reset()

    eleza reset(self):
        self.col = 0
        self.atbreak = 0

    eleza send_paragraph(self, blankline):
        self.file.write('\n'*blankline)
        self.col = 0
        self.atbreak = 0

    eleza send_line_break(self):
        self.file.write('\n')
        self.col = 0
        self.atbreak = 0

    eleza send_hor_rule(self, *args, **kw):
        self.file.write('\n')
        self.file.write('-'*self.maxcol)
        self.file.write('\n')
        self.col = 0
        self.atbreak = 0

    eleza send_literal_data(self, data):
        self.file.write(data)
        i = data.rfind('\n')
        ikiwa i >= 0:
            self.col = 0
            data = data[i+1:]
        data = data.expandtabs()
        self.col = self.col + len(data)
        self.atbreak = 0

    eleza send_flowing_data(self, data):
        ikiwa not data: return
        atbreak = self.atbreak or data[0].isspace()
        col = self.col
        maxcol = self.maxcol
        write = self.file.write
        for word in data.split():
            ikiwa atbreak:
                ikiwa col + len(word) >= maxcol:
                    write('\n')
                    col = 0
                else:
                    write(' ')
                    col = col + 1
            write(word)
            col = col + len(word)
            atbreak = 1
        self.col = col
        self.atbreak = data[-1].isspace()


eleza test(file = None):
    w = DumbWriter()
    f = AbstractFormatter(w)
    ikiwa file is not None:
        fp = open(file)
    elikiwa sys.argv[1:]:
        fp = open(sys.argv[1])
    else:
        fp = sys.stdin
    try:
        for line in fp:
            ikiwa line == '\n':
                f.end_paragraph(1)
            else:
                f.add_flowing_data(line)
    finally:
        ikiwa fp is not sys.stdin:
            fp.close()
    f.end_paragraph(0)


ikiwa __name__ == '__main__':
    test()
