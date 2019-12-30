"""File selection dialog classes.

Classes:

- FileDialog
- LoadFileDialog
- SaveFileDialog

This module also presents tk common file dialogues, it provides interfaces
to the native file dialogues available kwenye Tk 4.2 na newer, na the
directory dialogue available kwenye Tk 8.3 na newer.
These interfaces were written by Fredrik Lundh, May 1997.
"""

kutoka tkinter agiza *
kutoka tkinter.dialog agiza Dialog
kutoka tkinter agiza commondialog

agiza os
agiza fnmatch


dialogstates = {}


kundi FileDialog:

    """Standard file selection dialog -- no checks on selected file.

    Usage:

        d = FileDialog(master)
        fname = d.go(dir_or_file, pattern, default, key)
        ikiwa fname ni Tupu: ...canceled...
        isipokua: ...open file...

    All arguments to go() are optional.

    The 'key' argument specifies a key kwenye the global dictionary
    'dialogstates', which keeps track of the values kila the directory
    na pattern arguments, overriding the values pitaed kwenye (it does
    sio keep track of the default argument!).  If no key ni specified,
    the dialog keeps no memory of previous state.  Note that memory is
    kept even when the dialog ni canceled.  (All this emulates the
    behavior of the Macintosh file selection dialogs.)

    """

    title = "File Selection Dialog"

    eleza __init__(self, master, title=Tupu):
        ikiwa title ni Tupu: title = self.title
        self.master = master
        self.directory = Tupu

        self.top = Toplevel(master)
        self.top.title(title)
        self.top.iconname(title)

        self.botframe = Frame(self.top)
        self.botframe.pack(side=BOTTOM, fill=X)

        self.selection = Entry(self.top)
        self.selection.pack(side=BOTTOM, fill=X)
        self.selection.bind('<Return>', self.ok_event)

        self.filter = Entry(self.top)
        self.filter.pack(side=TOP, fill=X)
        self.filter.bind('<Return>', self.filter_command)

        self.midframe = Frame(self.top)
        self.midframe.pack(expand=YES, fill=BOTH)

        self.filesbar = Scrollbar(self.midframe)
        self.filesbar.pack(side=RIGHT, fill=Y)
        self.files = Listbox(self.midframe, exportselection=0,
                             yscrollcommand=(self.filesbar, 'set'))
        self.files.pack(side=RIGHT, expand=YES, fill=BOTH)
        btags = self.files.bindtags()
        self.files.bindtags(btags[1:] + btags[:1])
        self.files.bind('<ButtonRelease-1>', self.files_select_event)
        self.files.bind('<Double-ButtonRelease-1>', self.files_double_event)
        self.filesbar.config(command=(self.files, 'yview'))

        self.dirsbar = Scrollbar(self.midframe)
        self.dirsbar.pack(side=LEFT, fill=Y)
        self.dirs = Listbox(self.midframe, exportselection=0,
                            yscrollcommand=(self.dirsbar, 'set'))
        self.dirs.pack(side=LEFT, expand=YES, fill=BOTH)
        self.dirsbar.config(command=(self.dirs, 'yview'))
        btags = self.dirs.bindtags()
        self.dirs.bindtags(btags[1:] + btags[:1])
        self.dirs.bind('<ButtonRelease-1>', self.dirs_select_event)
        self.dirs.bind('<Double-ButtonRelease-1>', self.dirs_double_event)

        self.ok_button = Button(self.botframe,
                                 text="OK",
                                 command=self.ok_command)
        self.ok_button.pack(side=LEFT)
        self.filter_button = Button(self.botframe,
                                    text="Filter",
                                    command=self.filter_command)
        self.filter_button.pack(side=LEFT, expand=YES)
        self.cancel_button = Button(self.botframe,
                                    text="Cancel",
                                    command=self.cancel_command)
        self.cancel_button.pack(side=RIGHT)

        self.top.protocol('WM_DELETE_WINDOW', self.cancel_command)
        # XXX Are the following okay kila a general audience?
        self.top.bind('<Alt-w>', self.cancel_command)
        self.top.bind('<Alt-W>', self.cancel_command)

    eleza go(self, dir_or_file=os.curdir, pattern="*", default="", key=Tupu):
        ikiwa key na key kwenye dialogstates:
            self.directory, pattern = dialogstates[key]
        isipokua:
            dir_or_file = os.path.expanduser(dir_or_file)
            ikiwa os.path.isdir(dir_or_file):
                self.directory = dir_or_file
            isipokua:
                self.directory, default = os.path.split(dir_or_file)
        self.set_filter(self.directory, pattern)
        self.set_selection(default)
        self.filter_command()
        self.selection.focus_set()
        self.top.wait_visibility() # window needs to be visible kila the grab
        self.top.grab_set()
        self.how = Tupu
        self.master.mainloop()          # Exited by self.quit(how)
        ikiwa key:
            directory, pattern = self.get_filter()
            ikiwa self.how:
                directory = os.path.dirname(self.how)
            dialogstates[key] = directory, pattern
        self.top.destroy()
        rudisha self.how

    eleza quit(self, how=Tupu):
        self.how = how
        self.master.quit()              # Exit mainloop()

    eleza dirs_double_event(self, event):
        self.filter_command()

    eleza dirs_select_event(self, event):
        dir, pat = self.get_filter()
        subdir = self.dirs.get('active')
        dir = os.path.normpath(os.path.join(self.directory, subdir))
        self.set_filter(dir, pat)

    eleza files_double_event(self, event):
        self.ok_command()

    eleza files_select_event(self, event):
        file = self.files.get('active')
        self.set_selection(file)

    eleza ok_event(self, event):
        self.ok_command()

    eleza ok_command(self):
        self.quit(self.get_selection())

    eleza filter_command(self, event=Tupu):
        dir, pat = self.get_filter()
        jaribu:
            names = os.listdir(dir)
        tatizo OSError:
            self.master.bell()
            return
        self.directory = dir
        self.set_filter(dir, pat)
        names.sort()
        subdirs = [os.pardir]
        matchingfiles = []
        kila name kwenye names:
            fullname = os.path.join(dir, name)
            ikiwa os.path.isdir(fullname):
                subdirs.append(name)
            lasivyo fnmatch.fnmatch(name, pat):
                matchingfiles.append(name)
        self.dirs.delete(0, END)
        kila name kwenye subdirs:
            self.dirs.insert(END, name)
        self.files.delete(0, END)
        kila name kwenye matchingfiles:
            self.files.insert(END, name)
        head, tail = os.path.split(self.get_selection())
        ikiwa tail == os.curdir: tail = ''
        self.set_selection(tail)

    eleza get_filter(self):
        filter = self.filter.get()
        filter = os.path.expanduser(filter)
        ikiwa filter[-1:] == os.sep ama os.path.isdir(filter):
            filter = os.path.join(filter, "*")
        rudisha os.path.split(filter)

    eleza get_selection(self):
        file = self.selection.get()
        file = os.path.expanduser(file)
        rudisha file

    eleza cancel_command(self, event=Tupu):
        self.quit()

    eleza set_filter(self, dir, pat):
        ikiwa sio os.path.isabs(dir):
            jaribu:
                pwd = os.getcwd()
            tatizo OSError:
                pwd = Tupu
            ikiwa pwd:
                dir = os.path.join(pwd, dir)
                dir = os.path.normpath(dir)
        self.filter.delete(0, END)
        self.filter.insert(END, os.path.join(dir ama os.curdir, pat ama "*"))

    eleza set_selection(self, file):
        self.selection.delete(0, END)
        self.selection.insert(END, os.path.join(self.directory, file))


kundi LoadFileDialog(FileDialog):

    """File selection dialog which checks that the file exists."""

    title = "Load File Selection Dialog"

    eleza ok_command(self):
        file = self.get_selection()
        ikiwa sio os.path.isfile(file):
            self.master.bell()
        isipokua:
            self.quit(file)


kundi SaveFileDialog(FileDialog):

    """File selection dialog which checks that the file may be created."""

    title = "Save File Selection Dialog"

    eleza ok_command(self):
        file = self.get_selection()
        ikiwa os.path.exists(file):
            ikiwa os.path.isdir(file):
                self.master.bell()
                return
            d = Dialog(self.top,
                       title="Overwrite Existing File Question",
                       text="Overwrite existing file %r?" % (file,),
                       bitmap='questhead',
                       default=1,
                       strings=("Yes", "Cancel"))
            ikiwa d.num != 0:
                return
        isipokua:
            head, tail = os.path.split(file)
            ikiwa sio os.path.isdir(head):
                self.master.bell()
                return
        self.quit(file)


# For the following classes na modules:
#
# options (all have default values):
#
# - defaultextension: added to filename ikiwa sio explicitly given
#
# - filetypes: sequence of (label, pattern) tuples.  the same pattern
#   may occur ukijumuisha several patterns.  use "*" kama pattern to indicate
#   all files.
#
# - initialdir: initial directory.  preserved by dialog instance.
#
# - initialfile: initial file (ignored by the open dialog).  preserved
#   by dialog instance.
#
# - parent: which window to place the dialog on top of
#
# - title: dialog title
#
# - multiple: ikiwa true user may select more than one file
#
# options kila the directory chooser:
#
# - initialdir, parent, title: see above
#
# - mustexist: ikiwa true, user must pick an existing directory
#


kundi _Dialog(commondialog.Dialog):

    eleza _fixoptions(self):
        jaribu:
            # make sure "filetypes" ni a tuple
            self.options["filetypes"] = tuple(self.options["filetypes"])
        tatizo KeyError:
            pita

    eleza _fixresult(self, widget, result):
        ikiwa result:
            # keep directory na filename until next time
            # convert Tcl path objects to strings
            jaribu:
                result = result.string
            tatizo AttributeError:
                # it already ni a string
                pita
            path, file = os.path.split(result)
            self.options["initialdir"] = path
            self.options["initialfile"] = file
        self.filename = result # compatibility
        rudisha result


#
# file dialogs

kundi Open(_Dialog):
    "Ask kila a filename to open"

    command = "tk_getOpenFile"

    eleza _fixresult(self, widget, result):
        ikiwa isinstance(result, tuple):
            # multiple results:
            result = tuple([getattr(r, "string", r) kila r kwenye result])
            ikiwa result:
                path, file = os.path.split(result[0])
                self.options["initialdir"] = path
                # don't set initialfile ama filename, kama we have multiple of these
            rudisha result
        ikiwa sio widget.tk.wantobjects() na "multiple" kwenye self.options:
            # Need to split result explicitly
            rudisha self._fixresult(widget, widget.tk.splitlist(result))
        rudisha _Dialog._fixresult(self, widget, result)


kundi SaveAs(_Dialog):
    "Ask kila a filename to save as"

    command = "tk_getSaveFile"


# the directory dialog has its own _fix routines.
kundi Directory(commondialog.Dialog):
    "Ask kila a directory"

    command = "tk_chooseDirectory"

    eleza _fixresult(self, widget, result):
        ikiwa result:
            # convert Tcl path objects to strings
            jaribu:
                result = result.string
            tatizo AttributeError:
                # it already ni a string
                pita
            # keep directory until next time
            self.options["initialdir"] = result
        self.directory = result # compatibility
        rudisha result

#
# convenience stuff


eleza askopenfilename(**options):
    "Ask kila a filename to open"

    rudisha Open(**options).show()


eleza asksaveasfilename(**options):
    "Ask kila a filename to save as"

    rudisha SaveAs(**options).show()


eleza askopenfilenames(**options):
    """Ask kila multiple filenames to open

    Returns a list of filenames ama empty list if
    cancel button selected
    """
    options["multiple"]=1
    rudisha Open(**options).show()

# FIXME: are the following  perhaps a bit too convenient?


eleza askopenfile(mode = "r", **options):
    "Ask kila a filename to open, na returned the opened file"

    filename = Open(**options).show()
    ikiwa filename:
        rudisha open(filename, mode)
    rudisha Tupu


eleza askopenfiles(mode = "r", **options):
    """Ask kila multiple filenames na rudisha the open file
    objects

    returns a list of open file objects ama an empty list if
    cancel selected
    """

    files = askopenfilenames(**options)
    ikiwa files:
        ofiles=[]
        kila filename kwenye files:
            ofiles.append(open(filename, mode))
        files=ofiles
    rudisha files


eleza asksaveasfile(mode = "w", **options):
    "Ask kila a filename to save as, na returned the opened file"

    filename = SaveAs(**options).show()
    ikiwa filename:
        rudisha open(filename, mode)
    rudisha Tupu


eleza askdirectory (**options):
    "Ask kila a directory, na rudisha the file name"
    rudisha Directory(**options).show()


# --------------------------------------------------------------------
# test stuff

eleza test():
    """Simple test program."""
    root = Tk()
    root.withdraw()
    fd = LoadFileDialog(root)
    loadfile = fd.go(key="test")
    fd = SaveFileDialog(root)
    savefile = fd.go(key="test")
    andika(loadfile, savefile)

    # Since the file name may contain non-ASCII characters, we need
    # to find an encoding that likely supports the file name, na
    # displays correctly on the terminal.

    # Start off ukijumuisha UTF-8
    enc = "utf-8"
    agiza sys

    # See whether CODESET ni defined
    jaribu:
        agiza locale
        locale.setlocale(locale.LC_ALL,'')
        enc = locale.nl_langinfo(locale.CODESET)
    tatizo (ImportError, AttributeError):
        pita

    # dialog kila opening files

    openfilename=askopenfilename(filetypes=[("all files", "*")])
    jaribu:
        fp=open(openfilename,"r")
        fp.close()
    tatizo:
        andika("Could sio open File: ")
        andika(sys.exc_info()[1])

    andika("open", openfilename.encode(enc))

    # dialog kila saving files

    saveasfilename=asksaveasfilename()
    andika("saveas", saveasfilename.encode(enc))


ikiwa __name__ == '__main__':
    test()
