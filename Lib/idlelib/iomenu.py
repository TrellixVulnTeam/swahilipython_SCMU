agiza codecs
kutoka codecs agiza BOM_UTF8
agiza os
agiza re
agiza shlex
agiza sys
agiza tempfile

agiza tkinter.filedialog as tkFileDialog
agiza tkinter.messagebox as tkMessageBox
kutoka tkinter.simpledialog agiza askstring

agiza idlelib
kutoka idlelib.config agiza idleConf

ikiwa idlelib.testing:  # Set True by test.test_idle to avoid setlocale.
    encoding = 'utf-8'
    errors = 'surrogateescape'
else:
    # Try setting the locale, so that we can find out
    # what encoding to use
    try:
        agiza locale
        locale.setlocale(locale.LC_CTYPE, "")
    except (ImportError, locale.Error):
        pass

    ikiwa sys.platform == 'win32':
        encoding = 'utf-8'
        errors = 'surrogateescape'
    else:
        try:
            # Different things can fail here: the locale module may not be
            # loaded, it may not offer nl_langinfo, or CODESET, or the
            # resulting codeset may be unknown to Python. We ignore all
            # these problems, falling back to ASCII
            locale_encoding = locale.nl_langinfo(locale.CODESET)
            ikiwa locale_encoding:
                codecs.lookup(locale_encoding)
        except (NameError, AttributeError, LookupError):
            # Try getdefaultlocale: it parses environment variables,
            # which may give a clue. Unfortunately, getdefaultlocale has
            # bugs that can cause ValueError.
            try:
                locale_encoding = locale.getdefaultlocale()[1]
                ikiwa locale_encoding:
                    codecs.lookup(locale_encoding)
            except (ValueError, LookupError):
                pass

        ikiwa locale_encoding:
            encoding = locale_encoding.lower()
            errors = 'strict'
        else:
            # POSIX locale or macOS
            encoding = 'ascii'
            errors = 'surrogateescape'
        # Encoding is used in multiple files; locale_encoding nowhere.
        # The only use of 'encoding' below is in _decode as initial value
        # of deprecated block asking user for encoding.
        # Perhaps use elsewhere should be reviewed.

coding_re = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)', re.ASCII)
blank_re = re.compile(r'^[ \t\f]*(?:[#\r\n]|$)', re.ASCII)

eleza coding_spec(data):
    """Return the encoding declaration according to PEP 263.

    When checking encoded data, only the first two lines should be passed
    in to avoid a UnicodeDecodeError ikiwa the rest of the data is not unicode.
    The first two lines would contain the encoding specification.

    Raise a LookupError ikiwa the encoding is declared but unknown.
    """
    ikiwa isinstance(data, bytes):
        # This encoding might be wrong. However, the coding
        # spec must be ASCII-only, so any non-ASCII characters
        # around here will be ignored. Decoding to Latin-1 should
        # never fail (except for memory outage)
        lines = data.decode('iso-8859-1')
    else:
        lines = data
    # consider only the first two lines
    ikiwa '\n' in lines:
        lst = lines.split('\n', 2)[:2]
    elikiwa '\r' in lines:
        lst = lines.split('\r', 2)[:2]
    else:
        lst = [lines]
    for line in lst:
        match = coding_re.match(line)
        ikiwa match is not None:
            break
        ikiwa not blank_re.match(line):
            rudisha None
    else:
        rudisha None
    name = match.group(1)
    try:
        codecs.lookup(name)
    except LookupError:
        # The standard encoding error does not indicate the encoding
        raise LookupError("Unknown encoding: "+name)
    rudisha name


kundi IOBinding:
# One instance per editor Window so methods know which to save, close.
# Open returns focus to self.editwin ikiwa aborted.
# EditorWindow.open_module, others, belong here.

    eleza __init__(self, editwin):
        self.editwin = editwin
        self.text = editwin.text
        self.__id_open = self.text.bind("<<open-window-kutoka-file>>", self.open)
        self.__id_save = self.text.bind("<<save-window>>", self.save)
        self.__id_saveas = self.text.bind("<<save-window-as-file>>",
                                          self.save_as)
        self.__id_savecopy = self.text.bind("<<save-copy-of-window-as-file>>",
                                            self.save_a_copy)
        self.fileencoding = None
        self.__id_print = self.text.bind("<<print-window>>", self.print_window)

    eleza close(self):
        # Undo command bindings
        self.text.unbind("<<open-window-kutoka-file>>", self.__id_open)
        self.text.unbind("<<save-window>>", self.__id_save)
        self.text.unbind("<<save-window-as-file>>",self.__id_saveas)
        self.text.unbind("<<save-copy-of-window-as-file>>", self.__id_savecopy)
        self.text.unbind("<<print-window>>", self.__id_print)
        # Break cycles
        self.editwin = None
        self.text = None
        self.filename_change_hook = None

    eleza get_saved(self):
        rudisha self.editwin.get_saved()

    eleza set_saved(self, flag):
        self.editwin.set_saved(flag)

    eleza reset_undo(self):
        self.editwin.reset_undo()

    filename_change_hook = None

    eleza set_filename_change_hook(self, hook):
        self.filename_change_hook = hook

    filename = None
    dirname = None

    eleza set_filename(self, filename):
        ikiwa filename and os.path.isdir(filename):
            self.filename = None
            self.dirname = filename
        else:
            self.filename = filename
            self.dirname = None
            self.set_saved(1)
            ikiwa self.filename_change_hook:
                self.filename_change_hook()

    eleza open(self, event=None, editFile=None):
        flist = self.editwin.flist
        # Save in case parent window is closed (ie, during askopenfile()).
        ikiwa flist:
            ikiwa not editFile:
                filename = self.askopenfile()
            else:
                filename=editFile
            ikiwa filename:
                # If editFile is valid and already open, flist.open will
                # shift focus to its existing window.
                # If the current window exists and is a fresh unnamed,
                # unmodified editor window (not an interpreter shell),
                # pass self.loadfile to flist.open so it will load the file
                # in the current window (ikiwa the file is not already open)
                # instead of a new window.
                ikiwa (self.editwin and
                        not getattr(self.editwin, 'interp', None) and
                        not self.filename and
                        self.get_saved()):
                    flist.open(filename, self.loadfile)
                else:
                    flist.open(filename)
            else:
                ikiwa self.text:
                    self.text.focus_set()
            rudisha "break"

        # Code for use outside IDLE:
        ikiwa self.get_saved():
            reply = self.maybesave()
            ikiwa reply == "cancel":
                self.text.focus_set()
                rudisha "break"
        ikiwa not editFile:
            filename = self.askopenfile()
        else:
            filename=editFile
        ikiwa filename:
            self.loadfile(filename)
        else:
            self.text.focus_set()
        rudisha "break"

    eol = r"(\r\n)|\n|\r"  # \r\n (Windows), \n (UNIX), or \r (Mac)
    eol_re = re.compile(eol)
    eol_convention = os.linesep  # default

    eleza loadfile(self, filename):
        try:
            # open the file in binary mode so that we can handle
            # end-of-line convention ourselves.
            with open(filename, 'rb') as f:
                two_lines = f.readline() + f.readline()
                f.seek(0)
                bytes = f.read()
        except OSError as msg:
            tkMessageBox.showerror("I/O Error", str(msg), parent=self.text)
            rudisha False
        chars, converted = self._decode(two_lines, bytes)
        ikiwa chars is None:
            tkMessageBox.showerror("Decoding Error",
                                   "File %s\nFailed to Decode" % filename,
                                   parent=self.text)
            rudisha False
        # We now convert all end-of-lines to '\n's
        firsteol = self.eol_re.search(chars)
        ikiwa firsteol:
            self.eol_convention = firsteol.group(0)
            chars = self.eol_re.sub(r"\n", chars)
        self.text.delete("1.0", "end")
        self.set_filename(None)
        self.text.insert("1.0", chars)
        self.reset_undo()
        self.set_filename(filename)
        ikiwa converted:
            # We need to save the conversion results first
            # before being able to execute the code
            self.set_saved(False)
        self.text.mark_set("insert", "1.0")
        self.text.yview("insert")
        self.updaterecentfileslist(filename)
        rudisha True

    eleza _decode(self, two_lines, bytes):
        "Create a Unicode string."
        chars = None
        # Check presence of a UTF-8 signature first
        ikiwa bytes.startswith(BOM_UTF8):
            try:
                chars = bytes[3:].decode("utf-8")
            except UnicodeDecodeError:
                # has UTF-8 signature, but fails to decode...
                rudisha None, False
            else:
                # Indicates that this file originally had a BOM
                self.fileencoding = 'BOM'
                rudisha chars, False
        # Next look for coding specification
        try:
            enc = coding_spec(two_lines)
        except LookupError as name:
            tkMessageBox.showerror(
                title="Error loading the file",
                message="The encoding '%s' is not known to this Python "\
                "installation. The file may not display correctly" % name,
                parent = self.text)
            enc = None
        except UnicodeDecodeError:
            rudisha None, False
        ikiwa enc:
            try:
                chars = str(bytes, enc)
                self.fileencoding = enc
                rudisha chars, False
            except UnicodeDecodeError:
                pass
        # Try ascii:
        try:
            chars = str(bytes, 'ascii')
            self.fileencoding = None
            rudisha chars, False
        except UnicodeDecodeError:
            pass
        # Try utf-8:
        try:
            chars = str(bytes, 'utf-8')
            self.fileencoding = 'utf-8'
            rudisha chars, False
        except UnicodeDecodeError:
            pass
        # Finally, try the locale's encoding. This is deprecated;
        # the user should declare a non-ASCII encoding
        try:
            # Wait for the editor window to appear
            self.editwin.text.update()
            enc = askstring(
                "Specify file encoding",
                "The file's encoding is invalid for Python 3.x.\n"
                "IDLE will convert it to UTF-8.\n"
                "What is the current encoding of the file?",
                initialvalue = encoding,
                parent = self.editwin.text)

            ikiwa enc:
                chars = str(bytes, enc)
                self.fileencoding = None
            rudisha chars, True
        except (UnicodeDecodeError, LookupError):
            pass
        rudisha None, False  # None on failure

    eleza maybesave(self):
        ikiwa self.get_saved():
            rudisha "yes"
        message = "Do you want to save %s before closing?" % (
            self.filename or "this untitled document")
        confirm = tkMessageBox.askyesnocancel(
                  title="Save On Close",
                  message=message,
                  default=tkMessageBox.YES,
                  parent=self.text)
        ikiwa confirm:
            reply = "yes"
            self.save(None)
            ikiwa not self.get_saved():
                reply = "cancel"
        elikiwa confirm is None:
            reply = "cancel"
        else:
            reply = "no"
        self.text.focus_set()
        rudisha reply

    eleza save(self, event):
        ikiwa not self.filename:
            self.save_as(event)
        else:
            ikiwa self.writefile(self.filename):
                self.set_saved(True)
                try:
                    self.editwin.store_file_breaks()
                except AttributeError:  # may be a PyShell
                    pass
        self.text.focus_set()
        rudisha "break"

    eleza save_as(self, event):
        filename = self.asksavefile()
        ikiwa filename:
            ikiwa self.writefile(filename):
                self.set_filename(filename)
                self.set_saved(1)
                try:
                    self.editwin.store_file_breaks()
                except AttributeError:
                    pass
        self.text.focus_set()
        self.updaterecentfileslist(filename)
        rudisha "break"

    eleza save_a_copy(self, event):
        filename = self.asksavefile()
        ikiwa filename:
            self.writefile(filename)
        self.text.focus_set()
        self.updaterecentfileslist(filename)
        rudisha "break"

    eleza writefile(self, filename):
        self.fixlastline()
        text = self.text.get("1.0", "end-1c")
        ikiwa self.eol_convention != "\n":
            text = text.replace("\n", self.eol_convention)
        chars = self.encode(text)
        try:
            with open(filename, "wb") as f:
                f.write(chars)
                f.flush()
                os.fsync(f.fileno())
            rudisha True
        except OSError as msg:
            tkMessageBox.showerror("I/O Error", str(msg),
                                   parent=self.text)
            rudisha False

    eleza encode(self, chars):
        ikiwa isinstance(chars, bytes):
            # This is either plain ASCII, or Tk was returning mixed-encoding
            # text to us. Don't try to guess further.
            rudisha chars
        # Preserve a BOM that might have been present on opening
        ikiwa self.fileencoding == 'BOM':
            rudisha BOM_UTF8 + chars.encode("utf-8")
        # See whether there is anything non-ASCII in it.
        # If not, no need to figure out the encoding.
        try:
            rudisha chars.encode('ascii')
        except UnicodeError:
            pass
        # Check ikiwa there is an encoding declared
        try:
            # a string, let coding_spec slice it to the first two lines
            enc = coding_spec(chars)
            failed = None
        except LookupError as msg:
            failed = msg
            enc = None
        else:
            ikiwa not enc:
                # PEP 3120: default source encoding is UTF-8
                enc = 'utf-8'
        ikiwa enc:
            try:
                rudisha chars.encode(enc)
            except UnicodeError:
                failed = "Invalid encoding '%s'" % enc
        tkMessageBox.showerror(
            "I/O Error",
            "%s.\nSaving as UTF-8" % failed,
            parent = self.text)
        # Fallback: save as UTF-8, with BOM - ignoring the incorrect
        # declared encoding
        rudisha BOM_UTF8 + chars.encode("utf-8")

    eleza fixlastline(self):
        c = self.text.get("end-2c")
        ikiwa c != '\n':
            self.text.insert("end-1c", "\n")

    eleza print_window(self, event):
        confirm = tkMessageBox.askokcancel(
                  title="Print",
                  message="Print to Default Printer",
                  default=tkMessageBox.OK,
                  parent=self.text)
        ikiwa not confirm:
            self.text.focus_set()
            rudisha "break"
        tempfilename = None
        saved = self.get_saved()
        ikiwa saved:
            filename = self.filename
        # shell undo is reset after every prompt, looks saved, probably isn't
        ikiwa not saved or filename is None:
            (tfd, tempfilename) = tempfile.mkstemp(prefix='IDLE_tmp_')
            filename = tempfilename
            os.close(tfd)
            ikiwa not self.writefile(tempfilename):
                os.unlink(tempfilename)
                rudisha "break"
        platform = os.name
        printPlatform = True
        ikiwa platform == 'posix': #posix platform
            command = idleConf.GetOption('main','General',
                                         'print-command-posix')
            command = command + " 2>&1"
        elikiwa platform == 'nt': #win32 platform
            command = idleConf.GetOption('main','General','print-command-win')
        else: #no printing for this platform
            printPlatform = False
        ikiwa printPlatform:  #we can try to print for this platform
            command = command % shlex.quote(filename)
            pipe = os.popen(command, "r")
            # things can get ugly on NT ikiwa there is no printer available.
            output = pipe.read().strip()
            status = pipe.close()
            ikiwa status:
                output = "Printing failed (exit status 0x%x)\n" % \
                         status + output
            ikiwa output:
                output = "Printing command: %s\n" % repr(command) + output
                tkMessageBox.showerror("Print status", output, parent=self.text)
        else:  #no printing for this platform
            message = "Printing is not enabled for this platform: %s" % platform
            tkMessageBox.showinfo("Print status", message, parent=self.text)
        ikiwa tempfilename:
            os.unlink(tempfilename)
        rudisha "break"

    opendialog = None
    savedialog = None

    filetypes = (
        ("Python files", "*.py *.pyw", "TEXT"),
        ("Text files", "*.txt", "TEXT"),
        ("All files", "*"),
        )

    defaultextension = '.py' ikiwa sys.platform == 'darwin' else ''

    eleza askopenfile(self):
        dir, base = self.defaultfilename("open")
        ikiwa not self.opendialog:
            self.opendialog = tkFileDialog.Open(parent=self.text,
                                                filetypes=self.filetypes)
        filename = self.opendialog.show(initialdir=dir, initialfile=base)
        rudisha filename

    eleza defaultfilename(self, mode="open"):
        ikiwa self.filename:
            rudisha os.path.split(self.filename)
        elikiwa self.dirname:
            rudisha self.dirname, ""
        else:
            try:
                pwd = os.getcwd()
            except OSError:
                pwd = ""
            rudisha pwd, ""

    eleza asksavefile(self):
        dir, base = self.defaultfilename("save")
        ikiwa not self.savedialog:
            self.savedialog = tkFileDialog.SaveAs(
                    parent=self.text,
                    filetypes=self.filetypes,
                    defaultextension=self.defaultextension)
        filename = self.savedialog.show(initialdir=dir, initialfile=base)
        rudisha filename

    eleza updaterecentfileslist(self,filename):
        "Update recent file list on all editor windows"
        ikiwa self.editwin.flist:
            self.editwin.update_recent_files_list(filename)

eleza _io_binding(parent):  # htest #
    kutoka tkinter agiza Toplevel, Text

    root = Toplevel(parent)
    root.title("Test IOBinding")
    x, y = map(int, parent.geometry().split('+')[1:])
    root.geometry("+%d+%d" % (x, y + 175))
    kundi MyEditWin:
        eleza __init__(self, text):
            self.text = text
            self.flist = None
            self.text.bind("<Control-o>", self.open)
            self.text.bind('<Control-p>', self.print)
            self.text.bind("<Control-s>", self.save)
            self.text.bind("<Alt-s>", self.saveas)
            self.text.bind('<Control-c>', self.savecopy)
        eleza get_saved(self): rudisha 0
        eleza set_saved(self, flag): pass
        eleza reset_undo(self): pass
        eleza open(self, event):
            self.text.event_generate("<<open-window-kutoka-file>>")
        eleza andika(self, event):
            self.text.event_generate("<<print-window>>")
        eleza save(self, event):
            self.text.event_generate("<<save-window>>")
        eleza saveas(self, event):
            self.text.event_generate("<<save-window-as-file>>")
        eleza savecopy(self, event):
            self.text.event_generate("<<save-copy-of-window-as-file>>")

    text = Text(root)
    text.pack()
    text.focus_set()
    editwin = MyEditWin(text)
    IOBinding(editwin)

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_iomenu', verbosity=2, exit=False)

    kutoka idlelib.idle_test.htest agiza run
    run(_io_binding)
