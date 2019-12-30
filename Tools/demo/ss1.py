#!/usr/bin/env python3

"""
SS1 -- a spreadsheet-like application.
"""

agiza os
agiza re
agiza sys
kutoka xml.parsers agiza expat
kutoka xml.sax.saxutils agiza escape

LEFT, CENTER, RIGHT = "LEFT", "CENTER", "RIGHT"

eleza ljust(x, n):
    rudisha x.ljust(n)
eleza center(x, n):
    rudisha x.center(n)
eleza rjust(x, n):
    rudisha x.rjust(n)
align2action = {LEFT: ljust, CENTER: center, RIGHT: rjust}

align2xml = {LEFT: "left", CENTER: "center", RIGHT: "right"}
xml2align = {"left": LEFT, "center": CENTER, "right": RIGHT}

align2anchor = {LEFT: "w", CENTER: "center", RIGHT: "e"}

eleza sum(seq):
    total = 0
    kila x kwenye seq:
        ikiwa x ni sio Tupu:
            total += x
    rudisha total

kundi Sheet:

    eleza __init__(self):
        self.cells = {} # {(x, y): cell, ...}
        self.ns = dict(
            cell = self.cellvalue,
            cells = self.multicellvalue,
            sum = sum,
        )

    eleza cellvalue(self, x, y):
        cell = self.getcell(x, y)
        ikiwa hasattr(cell, 'recalc'):
            rudisha cell.recalc(self.ns)
        isipokua:
            rudisha cell

    eleza multicellvalue(self, x1, y1, x2, y2):
        ikiwa x1 > x2:
            x1, x2 = x2, x1
        ikiwa y1 > y2:
            y1, y2 = y2, y1
        seq = []
        kila y kwenye range(y1, y2+1):
            kila x kwenye range(x1, x2+1):
                seq.append(self.cellvalue(x, y))
        rudisha seq

    eleza getcell(self, x, y):
        rudisha self.cells.get((x, y))

    eleza setcell(self, x, y, cell):
        assert x > 0 na y > 0
        assert isinstance(cell, BaseCell)
        self.cells[x, y] = cell

    eleza clearcell(self, x, y):
        jaribu:
            toa self.cells[x, y]
        tatizo KeyError:
            pita

    eleza clearcells(self, x1, y1, x2, y2):
        kila xy kwenye self.selectcells(x1, y1, x2, y2):
            toa self.cells[xy]

    eleza clearrows(self, y1, y2):
        self.clearcells(0, y1, sys.maxsize, y2)

    eleza clearcolumns(self, x1, x2):
        self.clearcells(x1, 0, x2, sys.maxsize)

    eleza selectcells(self, x1, y1, x2, y2):
        ikiwa x1 > x2:
            x1, x2 = x2, x1
        ikiwa y1 > y2:
            y1, y2 = y2, y1
        rudisha [(x, y) kila x, y kwenye self.cells
                ikiwa x1 <= x <= x2 na y1 <= y <= y2]

    eleza movecells(self, x1, y1, x2, y2, dx, dy):
        ikiwa dx == 0 na dy == 0:
            rudisha
        ikiwa x1 > x2:
            x1, x2 = x2, x1
        ikiwa y1 > y2:
            y1, y2 = y2, y1
        assert x1+dx > 0 na y1+dy > 0
        new = {}
        kila x, y kwenye self.cells:
            cell = self.cells[x, y]
            ikiwa hasattr(cell, 'renumber'):
                cell = cell.renumber(x1, y1, x2, y2, dx, dy)
            ikiwa x1 <= x <= x2 na y1 <= y <= y2:
                x += dx
                y += dy
            new[x, y] = cell
        self.cells = new

    eleza insertrows(self, y, n):
        assert n > 0
        self.movecells(0, y, sys.maxsize, sys.maxsize, 0, n)

    eleza deleterows(self, y1, y2):
        ikiwa y1 > y2:
            y1, y2 = y2, y1
        self.clearrows(y1, y2)
        self.movecells(0, y2+1, sys.maxsize, sys.maxsize, 0, y1-y2-1)

    eleza insertcolumns(self, x, n):
        assert n > 0
        self.movecells(x, 0, sys.maxsize, sys.maxsize, n, 0)

    eleza deletecolumns(self, x1, x2):
        ikiwa x1 > x2:
            x1, x2 = x2, x1
        self.clearcells(x1, x2)
        self.movecells(x2+1, 0, sys.maxsize, sys.maxsize, x1-x2-1, 0)

    eleza getsize(self):
        maxx = maxy = 0
        kila x, y kwenye self.cells:
            maxx = max(maxx, x)
            maxy = max(maxy, y)
        rudisha maxx, maxy

    eleza reset(self):
        kila cell kwenye self.cells.values():
            ikiwa hasattr(cell, 'reset'):
                cell.reset()

    eleza recalc(self):
        self.reset()
        kila cell kwenye self.cells.values():
            ikiwa hasattr(cell, 'recalc'):
                cell.recalc(self.ns)

    eleza display(self):
        maxx, maxy = self.getsize()
        width, height = maxx+1, maxy+1
        colwidth = [1] * width
        full = {}
        # Add column heading labels kwenye row 0
        kila x kwenye range(1, width):
            full[x, 0] = text, alignment = colnum2name(x), RIGHT
            colwidth[x] = max(colwidth[x], len(text))
        # Add row labels kwenye column 0
        kila y kwenye range(1, height):
            full[0, y] = text, alignment = str(y), RIGHT
            colwidth[0] = max(colwidth[0], len(text))
        # Add sheet cells kwenye columns ukijumuisha x>0 na y>0
        kila (x, y), cell kwenye self.cells.items():
            ikiwa x <= 0 ama y <= 0:
                endelea
            ikiwa hasattr(cell, 'recalc'):
                cell.recalc(self.ns)
            ikiwa hasattr(cell, 'format'):
                text, alignment = cell.format()
                assert isinstance(text, str)
                assert alignment kwenye (LEFT, CENTER, RIGHT)
            isipokua:
                text = str(cell)
                ikiwa isinstance(cell, str):
                    alignment = LEFT
                isipokua:
                    alignment = RIGHT
            full[x, y] = (text, alignment)
            colwidth[x] = max(colwidth[x], len(text))
        # Calculate the horizontal separator line (dashes na dots)
        sep = ""
        kila x kwenye range(width):
            ikiwa sep:
                sep += "+"
            sep += "-"*colwidth[x]
        # Now andika The full grid
        kila y kwenye range(height):
            line = ""
            kila x kwenye range(width):
                text, alignment = full.get((x, y)) ama ("", LEFT)
                text = align2action[alignment](text, colwidth[x])
                ikiwa line:
                    line += '|'
                line += text
            andika(line)
            ikiwa y == 0:
                andika(sep)

    eleza xml(self):
        out = ['<spreadsheet>']
        kila (x, y), cell kwenye self.cells.items():
            ikiwa hasattr(cell, 'xml'):
                cellxml = cell.xml()
            isipokua:
                cellxml = '<value>%s</value>' % escape(cell)
            out.append('<cell row="%s" col="%s">\n  %s\n</cell>' %
                       (y, x, cellxml))
        out.append('</spreadsheet>')
        rudisha '\n'.join(out)

    eleza save(self, filename):
        text = self.xml()
        ukijumuisha open(filename, "w", encoding='utf-8') kama f:
            f.write(text)
            ikiwa text na sio text.endswith('\n'):
                f.write('\n')

    eleza load(self, filename):
        ukijumuisha open(filename, 'rb') kama f:
            SheetParser(self).parsefile(f)

kundi SheetParser:

    eleza __init__(self, sheet):
        self.sheet = sheet

    eleza parsefile(self, f):
        parser = expat.ParserCreate()
        parser.StartElementHandler = self.startelement
        parser.EndElementHandler = self.endelement
        parser.CharacterDataHandler = self.data
        parser.ParseFile(f)

    eleza startelement(self, tag, attrs):
        method = getattr(self, 'start_'+tag, Tupu)
        ikiwa method:
            method(attrs)
        self.texts = []

    eleza data(self, text):
        self.texts.append(text)

    eleza endelement(self, tag):
        method = getattr(self, 'end_'+tag, Tupu)
        ikiwa method:
            method("".join(self.texts))

    eleza start_cell(self, attrs):
        self.y = int(attrs.get("row"))
        self.x = int(attrs.get("col"))

    eleza start_value(self, attrs):
        self.fmt = attrs.get('format')
        self.alignment = xml2align.get(attrs.get('align'))

    start_formula = start_value

    eleza end_int(self, text):
        jaribu:
            self.value = int(text)
        tatizo (TypeError, ValueError):
            self.value = Tupu

    end_long = end_int

    eleza end_double(self, text):
        jaribu:
            self.value = float(text)
        tatizo (TypeError, ValueError):
            self.value = Tupu

    eleza end_complex(self, text):
        jaribu:
            self.value = complex(text)
        tatizo (TypeError, ValueError):
            self.value = Tupu

    eleza end_string(self, text):
        self.value = text

    eleza end_value(self, text):
        ikiwa isinstance(self.value, BaseCell):
            self.cell = self.value
        lasivyo isinstance(self.value, str):
            self.cell = StringCell(self.value,
                                   self.fmt ama "%s",
                                   self.alignment ama LEFT)
        isipokua:
            self.cell = NumericCell(self.value,
                                    self.fmt ama "%s",
                                    self.alignment ama RIGHT)

    eleza end_formula(self, text):
        self.cell = FormulaCell(text,
                                self.fmt ama "%s",
                                self.alignment ama RIGHT)

    eleza end_cell(self, text):
        self.sheet.setcell(self.x, self.y, self.cell)

kundi BaseCell:
    __init__ = Tupu # Must provide
    """Abstract base kundi kila sheet cells.

    Subclasses may but needn't provide the following APIs:

    cell.reset() -- prepare kila recalculation
    cell.recalc(ns) -> value -- recalculate formula
    cell.format() -> (value, alignment) -- rudisha formatted value
    cell.xml() -> string -- rudisha XML
    """

kundi NumericCell(BaseCell):

    eleza __init__(self, value, fmt="%s", alignment=RIGHT):
        assert isinstance(value, (int, float, complex))
        assert alignment kwenye (LEFT, CENTER, RIGHT)
        self.value = value
        self.fmt = fmt
        self.alignment = alignment

    eleza recalc(self, ns):
        rudisha self.value

    eleza format(self):
        jaribu:
            text = self.fmt % self.value
        tatizo:
            text = str(self.value)
        rudisha text, self.alignment

    eleza xml(self):
        method = getattr(self, '_xml_' + type(self.value).__name__)
        rudisha '<value align="%s" format="%s">%s</value>' % (
                align2xml[self.alignment],
                self.fmt,
                method())

    eleza _xml_int(self):
        ikiwa -2**31 <= self.value < 2**31:
            rudisha '<int>%s</int>' % self.value
        isipokua:
            rudisha '<long>%s</long>' % self.value

    eleza _xml_float(self):
        rudisha '<double>%r</double>' % self.value

    eleza _xml_complex(self):
        rudisha '<complex>%r</complex>' % self.value

kundi StringCell(BaseCell):

    eleza __init__(self, text, fmt="%s", alignment=LEFT):
        assert isinstance(text, str)
        assert alignment kwenye (LEFT, CENTER, RIGHT)
        self.text = text
        self.fmt = fmt
        self.alignment = alignment

    eleza recalc(self, ns):
        rudisha self.text

    eleza format(self):
        rudisha self.text, self.alignment

    eleza xml(self):
        s = '<value align="%s" format="%s"><string>%s</string></value>'
        rudisha s % (
            align2xml[self.alignment],
            self.fmt,
            escape(self.text))

kundi FormulaCell(BaseCell):

    eleza __init__(self, formula, fmt="%s", alignment=RIGHT):
        assert alignment kwenye (LEFT, CENTER, RIGHT)
        self.formula = formula
        self.translated = translate(self.formula)
        self.fmt = fmt
        self.alignment = alignment
        self.reset()

    eleza reset(self):
        self.value = Tupu

    eleza recalc(self, ns):
        ikiwa self.value ni Tupu:
            jaribu:
                self.value = eval(self.translated, ns)
            tatizo:
                exc = sys.exc_info()[0]
                ikiwa hasattr(exc, "__name__"):
                    self.value = exc.__name__
                isipokua:
                    self.value = str(exc)
        rudisha self.value

    eleza format(self):
        jaribu:
            text = self.fmt % self.value
        tatizo:
            text = str(self.value)
        rudisha text, self.alignment

    eleza xml(self):
        rudisha '<formula align="%s" format="%s">%s</formula>' % (
            align2xml[self.alignment],
            self.fmt,
            escape(self.formula))

    eleza renumber(self, x1, y1, x2, y2, dx, dy):
        out = []
        kila part kwenye re.split(r'(\w+)', self.formula):
            m = re.match('^([A-Z]+)([1-9][0-9]*)$', part)
            ikiwa m ni sio Tupu:
                sx, sy = m.groups()
                x = colname2num(sx)
                y = int(sy)
                ikiwa x1 <= x <= x2 na y1 <= y <= y2:
                    part = cellname(x+dx, y+dy)
            out.append(part)
        rudisha FormulaCell("".join(out), self.fmt, self.alignment)

eleza translate(formula):
    """Translate a formula containing fancy cell names to valid Python code.

    Examples:
        B4 -> cell(2, 4)
        B4:Z100 -> cells(2, 4, 26, 100)
    """
    out = []
    kila part kwenye re.split(r"(\w+(?::\w+)?)", formula):
        m = re.match(r"^([A-Z]+)([1-9][0-9]*)(?::([A-Z]+)([1-9][0-9]*))?$", part)
        ikiwa m ni Tupu:
            out.append(part)
        isipokua:
            x1, y1, x2, y2 = m.groups()
            x1 = colname2num(x1)
            ikiwa x2 ni Tupu:
                s = "cell(%s, %s)" % (x1, y1)
            isipokua:
                x2 = colname2num(x2)
                s = "cells(%s, %s, %s, %s)" % (x1, y1, x2, y2)
            out.append(s)
    rudisha "".join(out)

eleza cellname(x, y):
    "Translate a cell coordinate to a fancy cell name (e.g. (1, 1)->'A1')."
    assert x > 0 # Column 0 has an empty name, so can't use that
    rudisha colnum2name(x) + str(y)

eleza colname2num(s):
    "Translate a column name to number (e.g. 'A'->1, 'Z'->26, 'AA'->27)."
    s = s.upper()
    n = 0
    kila c kwenye s:
        assert 'A' <= c <= 'Z'
        n = n*26 + ord(c) - ord('A') + 1
    rudisha n

eleza colnum2name(n):
    "Translate a column number to name (e.g. 1->'A', etc.)."
    assert n > 0
    s = ""
    wakati n:
        n, m = divmod(n-1, 26)
        s = chr(m+ord('A')) + s
    rudisha s

agiza tkinter kama Tk

kundi SheetGUI:

    """Beginnings of a GUI kila a spreadsheet.

    TO DO:
    - clear multiple cells
    - Insert, clear, remove rows ama columns
    - Show new contents wakati typing
    - Scroll bars
    - Grow grid when window ni grown
    - Proper menus
    - Undo, redo
    - Cut, copy na paste
    - Formatting na alignment
    """

    eleza __init__(self, filename="sheet1.xml", rows=10, columns=5):
        """Constructor.

        Load the sheet kutoka the filename argument.
        Set up the Tk widget tree.
        """
        # Create na load the sheet
        self.filename = filename
        self.sheet = Sheet()
        ikiwa os.path.isfile(filename):
            self.sheet.load(filename)
        # Calculate the needed grid size
        maxx, maxy = self.sheet.getsize()
        rows = max(rows, maxy)
        columns = max(columns, maxx)
        # Create the widgets
        self.root = Tk.Tk()
        self.root.wm_title("Spreadsheet: %s" % self.filename)
        self.beacon = Tk.Label(self.root, text="A1",
                               font=('helvetica', 16, 'bold'))
        self.entry = Tk.Entry(self.root)
        self.savebutton = Tk.Button(self.root, text="Save",
                                    command=self.save)
        self.cellgrid = Tk.Frame(self.root)
        # Configure the widget lay-out
        self.cellgrid.pack(side="bottom", expand=1, fill="both")
        self.beacon.pack(side="left")
        self.savebutton.pack(side="right")
        self.entry.pack(side="left", expand=1, fill="x")
        # Bind some events
        self.entry.bind("<Return>", self.return_event)
        self.entry.bind("<Shift-Return>", self.shift_return_event)
        self.entry.bind("<Tab>", self.tab_event)
        self.entry.bind("<Shift-Tab>", self.shift_tab_event)
        self.entry.bind("<Delete>", self.delete_event)
        self.entry.bind("<Escape>", self.escape_event)
        # Now create the cell grid
        self.makegrid(rows, columns)
        # Select the top-left cell
        self.currentxy = Tupu
        self.cornerxy = Tupu
        self.setcurrent(1, 1)
        # Copy the sheet cells to the GUI cells
        self.sync()

    eleza delete_event(self, event):
        ikiwa self.cornerxy != self.currentxy na self.cornerxy ni sio Tupu:
            self.sheet.clearcells(*(self.currentxy + self.cornerxy))
        isipokua:
            self.sheet.clearcell(*self.currentxy)
        self.sync()
        self.entry.delete(0, 'end')
        rudisha "koma"

    eleza escape_event(self, event):
        x, y = self.currentxy
        self.load_entry(x, y)

    eleza load_entry(self, x, y):
        cell = self.sheet.getcell(x, y)
        ikiwa cell ni Tupu:
            text = ""
        lasivyo isinstance(cell, FormulaCell):
            text = '=' + cell.formula
        isipokua:
            text, alignment = cell.format()
        self.entry.delete(0, 'end')
        self.entry.insert(0, text)
        self.entry.selection_range(0, 'end')

    eleza makegrid(self, rows, columns):
        """Helper to create the grid of GUI cells.

        The edge (x==0 ama y==0) ni filled ukijumuisha labels; the rest ni real cells.
        """
        self.rows = rows
        self.columns = columns
        self.gridcells = {}
        # Create the top left corner cell (which selects all)
        cell = Tk.Label(self.cellgrid, relief='raised')
        cell.grid_configure(column=0, row=0, sticky='NSWE')
        cell.bind("<ButtonPress-1>", self.selectall)
        # Create the top row of labels, na configure the grid columns
        kila x kwenye range(1, columns+1):
            self.cellgrid.grid_columnconfigure(x, minsize=64)
            cell = Tk.Label(self.cellgrid, text=colnum2name(x), relief='raised')
            cell.grid_configure(column=x, row=0, sticky='WE')
            self.gridcells[x, 0] = cell
            cell.__x = x
            cell.__y = 0
            cell.bind("<ButtonPress-1>", self.selectcolumn)
            cell.bind("<B1-Motion>", self.extendcolumn)
            cell.bind("<ButtonRelease-1>", self.extendcolumn)
            cell.bind("<Shift-Button-1>", self.extendcolumn)
        # Create the leftmost column of labels
        kila y kwenye range(1, rows+1):
            cell = Tk.Label(self.cellgrid, text=str(y), relief='raised')
            cell.grid_configure(column=0, row=y, sticky='WE')
            self.gridcells[0, y] = cell
            cell.__x = 0
            cell.__y = y
            cell.bind("<ButtonPress-1>", self.selectrow)
            cell.bind("<B1-Motion>", self.extendrow)
            cell.bind("<ButtonRelease-1>", self.extendrow)
            cell.bind("<Shift-Button-1>", self.extendrow)
        # Create the real cells
        kila x kwenye range(1, columns+1):
            kila y kwenye range(1, rows+1):
                cell = Tk.Label(self.cellgrid, relief='sunken',
                                bg='white', fg='black')
                cell.grid_configure(column=x, row=y, sticky='NSWE')
                self.gridcells[x, y] = cell
                cell.__x = x
                cell.__y = y
                # Bind mouse events
                cell.bind("<ButtonPress-1>", self.press)
                cell.bind("<B1-Motion>", self.motion)
                cell.bind("<ButtonRelease-1>", self.release)
                cell.bind("<Shift-Button-1>", self.release)

    eleza selectall(self, event):
        self.setcurrent(1, 1)
        self.setcorner(sys.maxsize, sys.maxsize)

    eleza selectcolumn(self, event):
        x, y = self.whichxy(event)
        self.setcurrent(x, 1)
        self.setcorner(x, sys.maxsize)

    eleza extendcolumn(self, event):
        x, y = self.whichxy(event)
        ikiwa x > 0:
            self.setcurrent(self.currentxy[0], 1)
            self.setcorner(x, sys.maxsize)

    eleza selectrow(self, event):
        x, y = self.whichxy(event)
        self.setcurrent(1, y)
        self.setcorner(sys.maxsize, y)

    eleza extendrow(self, event):
        x, y = self.whichxy(event)
        ikiwa y > 0:
            self.setcurrent(1, self.currentxy[1])
            self.setcorner(sys.maxsize, y)

    eleza press(self, event):
        x, y = self.whichxy(event)
        ikiwa x > 0 na y > 0:
            self.setcurrent(x, y)

    eleza motion(self, event):
        x, y = self.whichxy(event)
        ikiwa x > 0 na y > 0:
            self.setcorner(x, y)

    release = motion

    eleza whichxy(self, event):
        w = self.cellgrid.winfo_containing(event.x_root, event.y_root)
        ikiwa w ni sio Tupu na isinstance(w, Tk.Label):
            jaribu:
                rudisha w.__x, w.__y
            tatizo AttributeError:
                pita
        rudisha 0, 0

    eleza save(self):
        self.sheet.save(self.filename)

    eleza setcurrent(self, x, y):
        "Make (x, y) the current cell."
        ikiwa self.currentxy ni sio Tupu:
            self.change_cell()
        self.clearfocus()
        self.beacon['text'] = cellname(x, y)
        self.load_entry(x, y)
        self.entry.focus_set()
        self.currentxy = x, y
        self.cornerxy = Tupu
        gridcell = self.gridcells.get(self.currentxy)
        ikiwa gridcell ni sio Tupu:
            gridcell['bg'] = 'yellow'

    eleza setcorner(self, x, y):
        ikiwa self.currentxy ni Tupu ama self.currentxy == (x, y):
            self.setcurrent(x, y)
            rudisha
        self.clearfocus()
        self.cornerxy = x, y
        x1, y1 = self.currentxy
        x2, y2 = self.cornerxy ama self.currentxy
        ikiwa x1 > x2:
            x1, x2 = x2, x1
        ikiwa y1 > y2:
            y1, y2 = y2, y1
        kila (x, y), cell kwenye self.gridcells.items():
            ikiwa x1 <= x <= x2 na y1 <= y <= y2:
                cell['bg'] = 'lightBlue'
        gridcell = self.gridcells.get(self.currentxy)
        ikiwa gridcell ni sio Tupu:
            gridcell['bg'] = 'yellow'
        self.setbeacon(x1, y1, x2, y2)

    eleza setbeacon(self, x1, y1, x2, y2):
        ikiwa x1 == y1 == 1 na x2 == y2 == sys.maxsize:
            name = ":"
        lasivyo (x1, x2) == (1, sys.maxsize):
            ikiwa y1 == y2:
                name = "%d" % y1
            isipokua:
                name = "%d:%d" % (y1, y2)
        lasivyo (y1, y2) == (1, sys.maxsize):
            ikiwa x1 == x2:
                name = "%s" % colnum2name(x1)
            isipokua:
                name = "%s:%s" % (colnum2name(x1), colnum2name(x2))
        isipokua:
            name1 = cellname(*self.currentxy)
            name2 = cellname(*self.cornerxy)
            name = "%s:%s" % (name1, name2)
        self.beacon['text'] = name


    eleza clearfocus(self):
        ikiwa self.currentxy ni sio Tupu:
            x1, y1 = self.currentxy
            x2, y2 = self.cornerxy ama self.currentxy
            ikiwa x1 > x2:
                x1, x2 = x2, x1
            ikiwa y1 > y2:
                y1, y2 = y2, y1
            kila (x, y), cell kwenye self.gridcells.items():
                ikiwa x1 <= x <= x2 na y1 <= y <= y2:
                    cell['bg'] = 'white'

    eleza return_event(self, event):
        "Callback kila the Return key."
        self.change_cell()
        x, y = self.currentxy
        self.setcurrent(x, y+1)
        rudisha "koma"

    eleza shift_return_event(self, event):
        "Callback kila the Return key ukijumuisha Shift modifier."
        self.change_cell()
        x, y = self.currentxy
        self.setcurrent(x, max(1, y-1))
        rudisha "koma"

    eleza tab_event(self, event):
        "Callback kila the Tab key."
        self.change_cell()
        x, y = self.currentxy
        self.setcurrent(x+1, y)
        rudisha "koma"

    eleza shift_tab_event(self, event):
        "Callback kila the Tab key ukijumuisha Shift modifier."
        self.change_cell()
        x, y = self.currentxy
        self.setcurrent(max(1, x-1), y)
        rudisha "koma"

    eleza change_cell(self):
        "Set the current cell kutoka the entry widget."
        x, y = self.currentxy
        text = self.entry.get()
        cell = Tupu
        ikiwa text.startswith('='):
            cell = FormulaCell(text[1:])
        isipokua:
            kila cls kwenye int, float, complex:
                jaribu:
                    value = cls(text)
                tatizo (TypeError, ValueError):
                    endelea
                isipokua:
                    cell = NumericCell(value)
                    koma
        ikiwa cell ni Tupu na text:
            cell = StringCell(text)
        ikiwa cell ni Tupu:
            self.sheet.clearcell(x, y)
        isipokua:
            self.sheet.setcell(x, y, cell)
        self.sync()

    eleza sync(self):
        "Fill the GUI cells kutoka the sheet cells."
        self.sheet.recalc()
        kila (x, y), gridcell kwenye self.gridcells.items():
            ikiwa x == 0 ama y == 0:
                endelea
            cell = self.sheet.getcell(x, y)
            ikiwa cell ni Tupu:
                gridcell['text'] = ""
            isipokua:
                ikiwa hasattr(cell, 'format'):
                    text, alignment = cell.format()
                isipokua:
                    text, alignment = str(cell), LEFT
                gridcell['text'] = text
                gridcell['anchor'] = align2anchor[alignment]


eleza test_basic():
    "Basic non-gui self-test."
    a = Sheet()
    kila x kwenye range(1, 11):
        kila y kwenye range(1, 11):
            ikiwa x == 1:
                cell = NumericCell(y)
            lasivyo y == 1:
                cell = NumericCell(x)
            isipokua:
                c1 = cellname(x, 1)
                c2 = cellname(1, y)
                formula = "%s*%s" % (c1, c2)
                cell = FormulaCell(formula)
            a.setcell(x, y, cell)
##    ikiwa os.path.isfile("sheet1.xml"):
##        andika "Loading kutoka sheet1.xml"
##        a.load("sheet1.xml")
    a.display()
    a.save("sheet1.xml")

eleza test_gui():
    "GUI test."
    ikiwa sys.argv[1:]:
        filename = sys.argv[1]
    isipokua:
        filename = "sheet1.xml"
    g = SheetGUI(filename)
    g.root.mainloop()

ikiwa __name__ == '__main__':
    #test_basic()
    test_gui()
