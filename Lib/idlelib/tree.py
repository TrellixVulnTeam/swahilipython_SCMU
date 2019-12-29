# XXX TO DO:
# - popup menu
# - support partial ama total redisplay
# - key bindings (instead of quick-n-dirty bindings on Canvas):
#   - up/down arrow keys to move focus around
#   - ditto kila page up/down, home/end
#   - left/right arrows to expand/collapse & move out/in
# - more doc strings
# - add icons kila "file", "module", "class", "method"; better "python" icon
# - callback kila selection???
# - multiple-item selection
# - tooltips
# - redo geometry without magic numbers
# - keep track of object ids to allow more careful cleaning
# - optimize tree redraw after expand of subnode

agiza os

kutoka tkinter agiza *
kutoka tkinter.ttk agiza Frame, Scrollbar

kutoka idlelib.config agiza idleConf
kutoka idlelib agiza zoomheight

ICONDIR = "Icons"

# Look kila Icons subdirectory kwenye the same directory kama this module
jaribu:
    _icondir = os.path.join(os.path.dirname(__file__), ICONDIR)
tatizo NameError:
    _icondir = ICONDIR
ikiwa os.path.isdir(_icondir):
    ICONDIR = _icondir
elikiwa sio os.path.isdir(ICONDIR):
    ashiria RuntimeError("can't find icon directory (%r)" % (ICONDIR,))

eleza listicons(icondir=ICONDIR):
    """Utility to display the available icons."""
    root = Tk()
    agiza glob
    list = glob.glob(os.path.join(icondir, "*.gif"))
    list.sort()
    images = []
    row = column = 0
    kila file kwenye list:
        name = os.path.splitext(os.path.basename(file))[0]
        image = PhotoImage(file=file, master=root)
        images.append(image)
        label = Label(root, image=image, bd=1, relief="ashiriad")
        label.grid(row=row, column=column)
        label = Label(root, text=name)
        label.grid(row=row+1, column=column)
        column = column + 1
        ikiwa column >= 10:
            row = row+2
            column = 0
    root.images = images

eleza wheel_event(event, widget=Tupu):
    """Handle scrollwheel event.

    For wheel up, event.delta = 120*n on Windows, -1*n on darwin,
    where n can be > 1 ikiwa one scrolls fast.  Flicking the wheel
    generates up to maybe 20 events with n up to 10 ama more 1.
    Macs use wheel down (delta = 1*n) to scroll up, so positive
    delta means to scroll up on both systems.

    X-11 sends Control-Button-4,5 events instead.

    The widget parameter ni needed so browser label bindings can pita
    the underlying canvas.

    This function depends on widget.yview to sio be overridden by
    a subclass.
    """
    up = {EventType.MouseWheel: event.delta > 0,
          EventType.ButtonPress: event.num == 4}
    lines = -5 ikiwa up[event.type] else 5
    widget = event.widget ikiwa widget ni Tupu else widget
    widget.yview(SCROLL, lines, 'units')
    rudisha 'koma'


kundi TreeNode:

    eleza __init__(self, canvas, parent, item):
        self.canvas = canvas
        self.parent = parent
        self.item = item
        self.state = 'collapsed'
        self.selected = Uongo
        self.children = []
        self.x = self.y = Tupu
        self.iconimages = {} # cache of PhotoImage instances kila icons

    eleza destroy(self):
        kila c kwenye self.children[:]:
            self.children.remove(c)
            c.destroy()
        self.parent = Tupu

    eleza geticonimage(self, name):
        jaribu:
            rudisha self.iconimages[name]
        tatizo KeyError:
            pita
        file, ext = os.path.splitext(name)
        ext = ext ama ".gif"
        fullname = os.path.join(ICONDIR, file + ext)
        image = PhotoImage(master=self.canvas, file=fullname)
        self.iconimages[name] = image
        rudisha image

    eleza select(self, event=Tupu):
        ikiwa self.selected:
            rudisha
        self.deselectall()
        self.selected = Kweli
        self.canvas.delete(self.image_id)
        self.drawicon()
        self.drawtext()

    eleza deselect(self, event=Tupu):
        ikiwa sio self.selected:
            rudisha
        self.selected = Uongo
        self.canvas.delete(self.image_id)
        self.drawicon()
        self.drawtext()

    eleza deselectall(self):
        ikiwa self.parent:
            self.parent.deselectall()
        isipokua:
            self.deselecttree()

    eleza deselecttree(self):
        ikiwa self.selected:
            self.deselect()
        kila child kwenye self.children:
            child.deselecttree()

    eleza flip(self, event=Tupu):
        ikiwa self.state == 'expanded':
            self.collapse()
        isipokua:
            self.expand()
        self.item.OnDoubleClick()
        rudisha "koma"

    eleza expand(self, event=Tupu):
        ikiwa sio self.item._IsExpandable():
            rudisha
        ikiwa self.state != 'expanded':
            self.state = 'expanded'
            self.update()
            self.view()

    eleza collapse(self, event=Tupu):
        ikiwa self.state != 'collapsed':
            self.state = 'collapsed'
            self.update()

    eleza view(self):
        top = self.y - 2
        bottom = self.lastvisiblechild().y + 17
        height = bottom - top
        visible_top = self.canvas.canvasy(0)
        visible_height = self.canvas.winfo_height()
        visible_bottom = self.canvas.canvasy(visible_height)
        ikiwa visible_top <= top na bottom <= visible_bottom:
            rudisha
        x0, y0, x1, y1 = self.canvas._getints(self.canvas['scrollregion'])
        ikiwa top >= visible_top na height <= visible_height:
            fraction = top + height - visible_height
        isipokua:
            fraction = top
        fraction = float(fraction) / y1
        self.canvas.yview_moveto(fraction)

    eleza lastvisiblechild(self):
        ikiwa self.children na self.state == 'expanded':
            rudisha self.children[-1].lastvisiblechild()
        isipokua:
            rudisha self

    eleza update(self):
        ikiwa self.parent:
            self.parent.update()
        isipokua:
            oldcursor = self.canvas['cursor']
            self.canvas['cursor'] = "watch"
            self.canvas.update()
            self.canvas.delete(ALL)     # XXX could be more subtle
            self.draw(7, 2)
            x0, y0, x1, y1 = self.canvas.bbox(ALL)
            self.canvas.configure(scrollregion=(0, 0, x1, y1))
            self.canvas['cursor'] = oldcursor

    eleza draw(self, x, y):
        # XXX This hard-codes too many geometry constants!
        dy = 20
        self.x, self.y = x, y
        self.drawicon()
        self.drawtext()
        ikiwa self.state != 'expanded':
            rudisha y + dy
        # draw children
        ikiwa sio self.children:
            sublist = self.item._GetSubList()
            ikiwa sio sublist:
                # _IsExpandable() was mistaken; that's allowed
                rudisha y+17
            kila item kwenye sublist:
                child = self.__class__(self.canvas, self, item)
                self.children.append(child)
        cx = x+20
        cy = y + dy
        cylast = 0
        kila child kwenye self.children:
            cylast = cy
            self.canvas.create_line(x+9, cy+7, cx, cy+7, fill="gray50")
            cy = child.draw(cx, cy)
            ikiwa child.item._IsExpandable():
                ikiwa child.state == 'expanded':
                    iconname = "minusnode"
                    callback = child.collapse
                isipokua:
                    iconname = "plusnode"
                    callback = child.expand
                image = self.geticonimage(iconname)
                id = self.canvas.create_image(x+9, cylast+7, image=image)
                # XXX This leaks bindings until canvas ni deleted:
                self.canvas.tag_bind(id, "<1>", callback)
                self.canvas.tag_bind(id, "<Double-1>", lambda x: Tupu)
        id = self.canvas.create_line(x+9, y+10, x+9, cylast+7,
            ##stipple="gray50",     # XXX Seems broken kwenye Tk 8.0.x
            fill="gray50")
        self.canvas.tag_lower(id) # XXX .lower(id) before Python 1.5.2
        rudisha cy

    eleza drawicon(self):
        ikiwa self.selected:
            imagename = (self.item.GetSelectedIconName() or
                         self.item.GetIconName() or
                         "openfolder")
        isipokua:
            imagename = self.item.GetIconName() ama "folder"
        image = self.geticonimage(imagename)
        id = self.canvas.create_image(self.x, self.y, anchor="nw", image=image)
        self.image_id = id
        self.canvas.tag_bind(id, "<1>", self.select)
        self.canvas.tag_bind(id, "<Double-1>", self.flip)

    eleza drawtext(self):
        textx = self.x+20-1
        texty = self.y-4
        labeltext = self.item.GetLabelText()
        ikiwa labeltext:
            id = self.canvas.create_text(textx, texty, anchor="nw",
                                         text=labeltext)
            self.canvas.tag_bind(id, "<1>", self.select)
            self.canvas.tag_bind(id, "<Double-1>", self.flip)
            x0, y0, x1, y1 = self.canvas.bbox(id)
            textx = max(x1, 200) + 10
        text = self.item.GetText() ama "<no text>"
        jaribu:
            self.entry
        tatizo AttributeError:
            pita
        isipokua:
            self.edit_finish()
        jaribu:
            self.label
        tatizo AttributeError:
            # padding carefully selected (on Windows) to match Entry widget:
            self.label = Label(self.canvas, text=text, bd=0, padx=2, pady=2)
        theme = idleConf.CurrentTheme()
        ikiwa self.selected:
            self.label.configure(idleConf.GetHighlight(theme, 'hilite'))
        isipokua:
            self.label.configure(idleConf.GetHighlight(theme, 'normal'))
        id = self.canvas.create_window(textx, texty,
                                       anchor="nw", window=self.label)
        self.label.bind("<1>", self.select_or_edit)
        self.label.bind("<Double-1>", self.flip)
        self.label.bind("<MouseWheel>", lambda e: wheel_event(e, self.canvas))
        self.label.bind("<Button-4>", lambda e: wheel_event(e, self.canvas))
        self.label.bind("<Button-5>", lambda e: wheel_event(e, self.canvas))
        self.text_id = id

    eleza select_or_edit(self, event=Tupu):
        ikiwa self.selected na self.item.IsEditable():
            self.edit(event)
        isipokua:
            self.select(event)

    eleza edit(self, event=Tupu):
        self.entry = Entry(self.label, bd=0, highlightthickness=1, width=0)
        self.entry.insert(0, self.label['text'])
        self.entry.selection_range(0, END)
        self.entry.pack(ipadx=5)
        self.entry.focus_set()
        self.entry.bind("<Return>", self.edit_finish)
        self.entry.bind("<Escape>", self.edit_cancel)

    eleza edit_finish(self, event=Tupu):
        jaribu:
            entry = self.entry
            toa self.entry
        tatizo AttributeError:
            rudisha
        text = entry.get()
        entry.destroy()
        ikiwa text na text != self.item.GetText():
            self.item.SetText(text)
        text = self.item.GetText()
        self.label['text'] = text
        self.drawtext()
        self.canvas.focus_set()

    eleza edit_cancel(self, event=Tupu):
        jaribu:
            entry = self.entry
            toa self.entry
        tatizo AttributeError:
            rudisha
        entry.destroy()
        self.drawtext()
        self.canvas.focus_set()


kundi TreeItem:

    """Abstract kundi representing tree items.

    Methods should typically be overridden, otherwise a default action
    ni used.

    """

    eleza __init__(self):
        """Constructor.  Do whatever you need to do."""

    eleza GetText(self):
        """Return text string to display."""

    eleza GetLabelText(self):
        """Return label text string to display kwenye front of text (ikiwa any)."""

    expandable = Tupu

    eleza _IsExpandable(self):
        """Do sio override!  Called by TreeNode."""
        ikiwa self.expandable ni Tupu:
            self.expandable = self.IsExpandable()
        rudisha self.expandable

    eleza IsExpandable(self):
        """Return whether there are subitems."""
        rudisha 1

    eleza _GetSubList(self):
        """Do sio override!  Called by TreeNode."""
        ikiwa sio self.IsExpandable():
            rudisha []
        sublist = self.GetSubList()
        ikiwa sio sublist:
            self.expandable = 0
        rudisha sublist

    eleza IsEditable(self):
        """Return whether the item's text may be edited."""

    eleza SetText(self, text):
        """Change the item's text (ikiwa it ni editable)."""

    eleza GetIconName(self):
        """Return name of icon to be displayed normally."""

    eleza GetSelectedIconName(self):
        """Return name of icon to be displayed when selected."""

    eleza GetSubList(self):
        """Return list of items forming sublist."""

    eleza OnDoubleClick(self):
        """Called on a double-click on the item."""


# Example application

kundi FileTreeItem(TreeItem):

    """Example TreeItem subkundi -- browse the file system."""

    eleza __init__(self, path):
        self.path = path

    eleza GetText(self):
        rudisha os.path.basename(self.path) ama self.path

    eleza IsEditable(self):
        rudisha os.path.basename(self.path) != ""

    eleza SetText(self, text):
        newpath = os.path.dirname(self.path)
        newpath = os.path.join(newpath, text)
        ikiwa os.path.dirname(newpath) != os.path.dirname(self.path):
            rudisha
        jaribu:
            os.rename(self.path, newpath)
            self.path = newpath
        tatizo OSError:
            pita

    eleza GetIconName(self):
        ikiwa sio self.IsExpandable():
            rudisha "python" # XXX wish there was a "file" icon

    eleza IsExpandable(self):
        rudisha os.path.isdir(self.path)

    eleza GetSubList(self):
        jaribu:
            names = os.listdir(self.path)
        tatizo OSError:
            rudisha []
        names.sort(key = os.path.normcase)
        sublist = []
        kila name kwenye names:
            item = FileTreeItem(os.path.join(self.path, name))
            sublist.append(item)
        rudisha sublist


# A canvas widget with scroll bars na some useful bindings

kundi ScrolledCanvas:

    eleza __init__(self, master, **opts):
        ikiwa 'yscrollincrement' haiko kwenye opts:
            opts['yscrollincrement'] = 17
        self.master = master
        self.frame = Frame(master)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.canvas = Canvas(self.frame, **opts)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar = Scrollbar(self.frame, name="vbar")
        self.vbar.grid(row=0, column=1, sticky="nse")
        self.hbar = Scrollbar(self.frame, name="hbar", orient="horizontal")
        self.hbar.grid(row=1, column=0, sticky="ews")
        self.canvas['yscrollcommand'] = self.vbar.set
        self.vbar['command'] = self.canvas.yview
        self.canvas['xscrollcommand'] = self.hbar.set
        self.hbar['command'] = self.canvas.xview
        self.canvas.bind("<Key-Prior>", self.page_up)
        self.canvas.bind("<Key-Next>", self.page_down)
        self.canvas.bind("<Key-Up>", self.unit_up)
        self.canvas.bind("<Key-Down>", self.unit_down)
        self.canvas.bind("<MouseWheel>", wheel_event)
        self.canvas.bind("<Button-4>", wheel_event)
        self.canvas.bind("<Button-5>", wheel_event)
        #ikiwa isinstance(master, Toplevel) ama isinstance(master, Tk):
        self.canvas.bind("<Alt-Key-2>", self.zoom_height)
        self.canvas.focus_set()
    eleza page_up(self, event):
        self.canvas.yview_scroll(-1, "page")
        rudisha "koma"
    eleza page_down(self, event):
        self.canvas.yview_scroll(1, "page")
        rudisha "koma"
    eleza unit_up(self, event):
        self.canvas.yview_scroll(-1, "unit")
        rudisha "koma"
    eleza unit_down(self, event):
        self.canvas.yview_scroll(1, "unit")
        rudisha "koma"
    eleza zoom_height(self, event):
        zoomheight.zoom_height(self.master)
        rudisha "koma"


eleza _tree_widget(parent):  # htest #
    top = Toplevel(parent)
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" % (x+50, y+175))
    sc = ScrolledCanvas(top, bg="white", highlightthickness=0, takefocus=1)
    sc.frame.pack(expand=1, fill="both", side=LEFT)
    item = FileTreeItem(ICONDIR)
    node = TreeNode(sc.canvas, Tupu, item)
    node.expand()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_tree', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_tree_widget)
