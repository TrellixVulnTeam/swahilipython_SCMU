"""Generic output formatting.

Formatter objects transform an abstract flow of formatting events into
specific output events on writer objects. Formatters manage several stack
structures to allow various properties of a writer object to be changed and
restored; writers need sio be able to handle relative changes nor any sort
of ``change back'' operation. Specific writer properties which may be
controlled via formatter objects are horizontal alignment, font, na left
margin indentations. A mechanism ni provided which supports providing
arbitrary, non-exclusive style settings to a writer kama well. Additional
interfaces facilitate formatting events which are sio reversible, such as
paragraph separation.

Writer objects encapsulate device interfaces. Abstract devices, such as
file formats, are supported kama well kama physical devices. The provided
implementations all work ukijumuisha abstract devices. The interface makes
available mechanisms kila setting the properties which formatter objects
manage na inserting data into the output.
"""

agiza sys
agiza warnings
warnings.warn('the formatter module ni deprecated', DeprecationWarning,
              stacklevel=2)


AS_IS = Tupu


kundi NullFormatter:
    """A formatter which does nothing.

    If the writer parameter ni omitted, a NullWriter instance ni created.
    No methods of the writer are called by NullFormatter instances.

    Implementations should inherit kutoka this kundi ikiwa implementing a writer
    interface but don't need to inherit any implementation.

    """

    eleza __init__(self, writer=Tupu):
        ikiwa writer ni Tupu:
            writer = NullWriter()
        self.writer = writer
    eleza end_paragraph(self, blankline): pita
    eleza add_line_koma(self): pita
    eleza add_hor_rule(self, *args, **kw): pita
    eleza add_label_data(self, format, counter, blankline=Tupu): pita
    eleza add_flowing_data(self, data): pita
    eleza add_literal_data(self, data): pita
    eleza flush_softspace(self): pita
    eleza push_alignment(self, align): pita
    eleza pop_alignment(self): pita
    eleza push_font(self, x): pita
    eleza pop_font(self): pita
    eleza push_margin(self, margin): pita
    eleza pop_margin(self): pita
    eleza set_spacing(self, spacing): pita
    eleza push_style(self, *styles): pita
    eleza pop_style(self, n=1): pita
    eleza assert_line_data(self, flag=1): pita


kundi AbstractFormatter:
    """The standard formatter.

    This implementation has demonstrated wide applicability to many writers,
    na may be used directly kwenye most circumstances.  It has been used to
    implement a full-featured World Wide Web browser.

    """

    #  Space handling policy:  blank spaces at the boundary between elements
    #  are handled by the outermost context.  "Literal" data ni sio checked
    #  to determine context, so spaces kwenye literal data are handled directly
    #  kwenye all circumstances.

    eleza __init__(self, writer):
        self.writer = writer            # Output device
        self.align = Tupu               # Current alignment
        self.align_stack = []           # Alignment stack
        self.font_stack = []            # Font state
        self.margin_stack = []          # Margin state
        self.spacing = Tupu             # Vertical spacing state
        self.style_stack = []           # Other state, e.g. color
        self.nospace = 1                # Should leading space be suppressed
        self.softspace = 0              # Should a space be inserted
        self.para_end = 1               # Just ended a paragraph
        self.parskip = 0                # Skipped space between paragraphs?
        self.hard_koma = 1             # Have a hard koma
        self.have_label = 0

    eleza end_paragraph(self, blankline):
        ikiwa sio self.hard_koma:
            self.writer.send_line_koma()
            self.have_label = 0
        ikiwa self.parskip < blankline na sio self.have_label:
            self.writer.send_paragraph(blankline - self.parskip)
            self.parskip = blankline
            self.have_label = 0
        self.hard_koma = self.nospace = self.para_end = 1
        self.softspace = 0

    eleza add_line_koma(self):
        ikiwa sio (self.hard_koma ama self.para_end):
            self.writer.send_line_koma()
            self.have_label = self.parskip = 0
        self.hard_koma = self.nospace = 1
        self.softspace = 0

    eleza add_hor_rule(self, *args, **kw):
        ikiwa sio self.hard_koma:
            self.writer.send_line_koma()
        self.writer.send_hor_rule(*args, **kw)
        self.hard_koma = self.nospace = 1
        self.have_label = self.para_end = self.softspace = self.parskip = 0

    eleza add_label_data(self, format, counter, blankline = Tupu):
        ikiwa self.have_label ama sio self.hard_koma:
            self.writer.send_line_koma()
        ikiwa sio self.para_end:
            self.writer.send_paragraph((blankline na 1) ama 0)
        ikiwa isinstance(format, str):
            self.writer.send_label_data(self.format_counter(format, counter))
        isipokua:
            self.writer.send_label_data(format)
        self.nospace = self.have_label = self.hard_koma = self.para_end = 1
        self.softspace = self.parskip = 0

    eleza format_counter(self, format, counter):
        label = ''
        kila c kwenye format:
            ikiwa c == '1':
                label = label + ('%d' % counter)
            lasivyo c kwenye 'aA':
                ikiwa counter > 0:
                    label = label + self.format_letter(c, counter)
            lasivyo c kwenye 'iI':
                ikiwa counter > 0:
                    label = label + self.format_roman(c, counter)
            isipokua:
                label = label + c
        rudisha label

    eleza format_letter(self, case, counter):
        label = ''
        wakati counter > 0:
            counter, x = divmod(counter-1, 26)
            # This makes a strong assumption that lowercase letters
            # na uppercase letters form two contiguous blocks, with
            # letters kwenye order!
            s = chr(ord(case) + x)
            label = s + label
        rudisha label

    eleza format_roman(self, case, counter):
        ones = ['i', 'x', 'c', 'm']
        fives = ['v', 'l', 'd']
        label, index = '', 0
        # This will die of IndexError when counter ni too big
        wakati counter > 0:
            counter, x = divmod(counter, 10)
            ikiwa x == 9:
                label = ones[index] + ones[index+1] + label
            lasivyo x == 4:
                label = ones[index] + fives[index] + label
            isipokua:
                ikiwa x >= 5:
                    s = fives[index]
                    x = x-5
                isipokua:
                    s = ''
                s = s + ones[index]*x
                label = s + label
            index = index + 1
        ikiwa case == 'I':
            rudisha label.upper()
        rudisha label

    eleza add_flowing_data(self, data):
        ikiwa sio data: rudisha
        prespace = data[:1].isspace()
        postspace = data[-1:].isspace()
        data = " ".join(data.split())
        ikiwa self.nospace na sio data:
            rudisha
        lasivyo prespace ama self.softspace:
            ikiwa sio data:
                ikiwa sio self.nospace:
                    self.softspace = 1
                    self.parskip = 0
                rudisha
            ikiwa sio self.nospace:
                data = ' ' + data
        self.hard_koma = self.nospace = self.para_end = \
                          self.parskip = self.have_label = 0
        self.softspace = postspace
        self.writer.send_flowing_data(data)

    eleza add_literal_data(self, data):
        ikiwa sio data: rudisha
        ikiwa self.softspace:
            self.writer.send_flowing_data(" ")
        self.hard_koma = data[-1:] == '\n'
        self.nospace = self.para_end = self.softspace = \
                       self.parskip = self.have_label = 0
        self.writer.send_literal_data(data)

    eleza flush_softspace(self):
        ikiwa self.softspace:
            self.hard_koma = self.para_end = self.parskip = \
                              self.have_label = self.softspace = 0
            self.nospace = 1
            self.writer.send_flowing_data(' ')

    eleza push_alignment(self, align):
        ikiwa align na align != self.align:
            self.writer.new_alignment(align)
            self.align = align
            self.align_stack.append(align)
        isipokua:
            self.align_stack.append(self.align)

    eleza pop_alignment(self):
        ikiwa self.align_stack:
            toa self.align_stack[-1]
        ikiwa self.align_stack:
            self.align = align = self.align_stack[-1]
            self.writer.new_alignment(align)
        isipokua:
            self.align = Tupu
            self.writer.new_alignment(Tupu)

    eleza push_font(self, font):
        size, i, b, tt = font
        ikiwa self.softspace:
            self.hard_koma = self.para_end = self.softspace = 0
            self.nospace = 1
            self.writer.send_flowing_data(' ')
        ikiwa self.font_stack:
            csize, ci, cb, ctt = self.font_stack[-1]
            ikiwa size ni AS_IS: size = csize
            ikiwa i ni AS_IS: i = ci
            ikiwa b ni AS_IS: b = cb
            ikiwa tt ni AS_IS: tt = ctt
        font = (size, i, b, tt)
        self.font_stack.append(font)
        self.writer.new_font(font)

    eleza pop_font(self):
        ikiwa self.font_stack:
            toa self.font_stack[-1]
        ikiwa self.font_stack:
            font = self.font_stack[-1]
        isipokua:
            font = Tupu
        self.writer.new_font(font)

    eleza push_margin(self, margin):
        self.margin_stack.append(margin)
        fstack = [m kila m kwenye self.margin_stack ikiwa m]
        ikiwa sio margin na fstack:
            margin = fstack[-1]
        self.writer.new_margin(margin, len(fstack))

    eleza pop_margin(self):
        ikiwa self.margin_stack:
            toa self.margin_stack[-1]
        fstack = [m kila m kwenye self.margin_stack ikiwa m]
        ikiwa fstack:
            margin = fstack[-1]
        isipokua:
            margin = Tupu
        self.writer.new_margin(margin, len(fstack))

    eleza set_spacing(self, spacing):
        self.spacing = spacing
        self.writer.new_spacing(spacing)

    eleza push_style(self, *styles):
        ikiwa self.softspace:
            self.hard_koma = self.para_end = self.softspace = 0
            self.nospace = 1
            self.writer.send_flowing_data(' ')
        kila style kwenye styles:
            self.style_stack.append(style)
        self.writer.new_styles(tuple(self.style_stack))

    eleza pop_style(self, n=1):
        toa self.style_stack[-n:]
        self.writer.new_styles(tuple(self.style_stack))

    eleza assert_line_data(self, flag=1):
        self.nospace = self.hard_koma = sio flag
        self.para_end = self.parskip = self.have_label = 0


kundi NullWriter:
    """Minimal writer interface to use kwenye testing & inheritance.

    A writer which only provides the interface definition; no actions are
    taken on any methods.  This should be the base kundi kila all writers
    which do sio need to inherit any implementation methods.

    """
    eleza __init__(self): pita
    eleza flush(self): pita
    eleza new_alignment(self, align): pita
    eleza new_font(self, font): pita
    eleza new_margin(self, margin, level): pita
    eleza new_spacing(self, spacing): pita
    eleza new_styles(self, styles): pita
    eleza send_paragraph(self, blankline): pita
    eleza send_line_koma(self): pita
    eleza send_hor_rule(self, *args, **kw): pita
    eleza send_label_data(self, data): pita
    eleza send_flowing_data(self, data): pita
    eleza send_literal_data(self, data): pita


kundi AbstractWriter(NullWriter):
    """A writer which can be used kwenye debugging formatters, but sio much else.

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

    eleza send_line_koma(self):
        andika("send_line_koma()")

    eleza send_hor_rule(self, *args, **kw):
        andika("send_hor_rule()")

    eleza send_label_data(self, data):
        andika("send_label_data(%r)" % (data,))

    eleza send_flowing_data(self, data):
        andika("send_flowing_data(%r)" % (data,))

    eleza send_literal_data(self, data):
        andika("send_literal_data(%r)" % (data,))


kundi DumbWriter(NullWriter):
    """Simple writer kundi which writes output on the file object pitaed in
    kama the file parameter or, ikiwa file ni omitted, on standard output.  The
    output ni simply word-wrapped to the number of columns specified by
    the maxcol parameter.  This kundi ni suitable kila reflowing a sequence
    of paragraphs.

    """

    eleza __init__(self, file=Tupu, maxcol=72):
        self.file = file ama sys.stdout
        self.maxcol = maxcol
        NullWriter.__init__(self)
        self.reset()

    eleza reset(self):
        self.col = 0
        self.atkoma = 0

    eleza send_paragraph(self, blankline):
        self.file.write('\n'*blankline)
        self.col = 0
        self.atkoma = 0

    eleza send_line_koma(self):
        self.file.write('\n')
        self.col = 0
        self.atkoma = 0

    eleza send_hor_rule(self, *args, **kw):
        self.file.write('\n')
        self.file.write('-'*self.maxcol)
        self.file.write('\n')
        self.col = 0
        self.atkoma = 0

    eleza send_literal_data(self, data):
        self.file.write(data)
        i = data.rfind('\n')
        ikiwa i >= 0:
            self.col = 0
            data = data[i+1:]
        data = data.expandtabs()
        self.col = self.col + len(data)
        self.atkoma = 0

    eleza send_flowing_data(self, data):
        ikiwa sio data: rudisha
        atkoma = self.atkoma ama data[0].isspace()
        col = self.col
        maxcol = self.maxcol
        write = self.file.write
        kila word kwenye data.split():
            ikiwa atkoma:
                ikiwa col + len(word) >= maxcol:
                    write('\n')
                    col = 0
                isipokua:
                    write(' ')
                    col = col + 1
            write(word)
            col = col + len(word)
            atkoma = 1
        self.col = col
        self.atkoma = data[-1].isspace()


eleza test(file = Tupu):
    w = DumbWriter()
    f = AbstractFormatter(w)
    ikiwa file ni sio Tupu:
        fp = open(file)
    lasivyo sys.argv[1:]:
        fp = open(sys.argv[1])
    isipokua:
        fp = sys.stdin
    jaribu:
        kila line kwenye fp:
            ikiwa line == '\n':
                f.end_paragraph(1)
            isipokua:
                f.add_flowing_data(line)
    mwishowe:
        ikiwa fp ni sio sys.stdin:
            fp.close()
    f.end_paragraph(0)


ikiwa __name__ == '__main__':
    test()
