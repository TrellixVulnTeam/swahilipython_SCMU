agiza codecs
kutoka codecs agiza BOM_UTF8
agiza os
agiza re
agiza shlex
agiza sys
agiza tempfile

agiza tkinter.filedialog kama tkFileDialog
agiza tkinter.messagebox kama tkMessageBox
kutoka tkinter.simpledialog agiza askstring

agiza idlelib
kutoka idlelib.config agiza idleConf

ikiwa idlelib.testing:  # Set Kweli by test.test_idle to avoid setlocale.
    encoding = 'utf-8'
    errors = 'surrogateescape'
isipokua:
    # Try setting the locale, so that we can find out
    # what encoding to use
    jaribu:
        agiza locale
        locale.setlocale(locale.LC_CTYPE, "")
    tatizo (ImportError, locale.Error):
        pita

    ikiwa sys.platform == 'win32':
        encoding = 'utf-8'
        errors = 'surrogateescape'
    isipokua:
        jaribu:
            # Different things can fail here: the locale module may sio be
            # loaded, it may sio offer nl_langinfo, ama CODESET, ama the
            # resulting codeset may be unknown to Python. We ignore all
            # these problems, falling back to ASCII
            locale_encoding = locale.nl_langinfo(locale.CODESET)
            ikiwa locale_encoding:
                codecs.lookup(locale_encoding)
        tatizo (NameError, AttributeError, LookupError):
            # Try getdefaultlocale: it parses environment variables,
            # which may give a clue. Unfortunately, getdefaultlocale has
            # bugs that can cause ValueError.
            jaribu:
                locale_encoding = locale.getdefaultlocale()[1]
                ikiwa locale_encoding:
                    codecs.lookup(locale_encoding)
            tatizo (ValueError, LookupError):
                pita

        ikiwa locale_encoding:
            encoding = locale_encoding.lower()
            errors = 'strict'
        isipokua:
            # POSIX locale ama macOS
            encoding = 'ascii'
            errors = 'surrogateescape'
        # Encoding ni used kwenye multiple files; locale_encoding nowhere.
        # The only use of 'encoding' below ni kwenye _decode kama initial value
        # of deprecated block asking user kila encoding.
        # Perhaps use elsewhere should be reviewed.

coding_re = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-\w.]+)', re.ASCII)
blank_re = re.compile(r'^[ \t\f]*(?:[#\r\n]|$)', re.ASCII)

eleza coding_spec(data):
    """Return the encoding declaration according to PEP 263.

    When checking encoded data, only the first two lines should be pitaed
    kwenye to avoid a UnicodeDecodeError ikiwa the rest of the data ni sio unicode.
    The first two lines would contain the encoding specification.

    Raise a LookupError ikiwa the encoding ni declared but unknown.
    """
    ikiwa isinstance(data, bytes):
        # This encoding might be wrong. However, the coding
        # spec must be ASCII-only, so any non-ASCII characters
        # around here will be ignored. Decoding to Latin-1 should
        # never fail (tatizo kila memory outage)
        lines = data.decode('iso-8859-1')
    isipokua:
        lines = data
    # consider only the first two lines
    ikiwa '\n' kwenye lines:
        lst = lines.split('\n', 2)[:2]
    lasivyo '\r' kwenye lines:
        lst = lines.split('\r', 2)[:2]
    isipokua:
        lst = [lines]
    kila line kwenye lst:
        match = coding_re.match(line)
        ikiwa match ni sio Tupu:
            koma
        ikiwa sio blank_re.match(line):
            rudisha Tupu
    isipokua:
        rudisha Tupu
    name = match.group(1)
    jaribu:
        codecs.lookup(name)
    tatizo LookupError:
        # The standard encoding error does sio inicate the encoding
        ashiria LookupError("Unknown encoding: "+name)
    rudisha name


kundi IOBinding:
# One instance per editor Window so methods know which to save, close.
# Open returns focus to self.editwin ikiwa aborted.
# EditorWindow.open_module, others, belong here.

    eleza __init__(self, editwin):
        self.editwin = editwin
        self.text = editwin.text
        self.__id_open = self.text.bind("<<open-window-from-file>>", self.open)
        self.__id_save = self.text.bind("<<save-window>>", self.save)
        self.__id_saveas = self.text.bind("<<save-window-as-file>>",
                                          self.save_as)
        self.__id_savecopy = self.text.bind("<<save-copy-of-window-as-file>>",
                                            self.save_a_copy)
        self.fileencoding = Tupu
        self.__id_print = self.text.bind("<<print-window>>", self.print_window)

    eleza close(self):
        # Undo command bindings
        self.text.unbind("<<open-window-from-file>>", self.__id_open)
        self.text.unbind("<<save-window>>", self.__id_save)
        self.text.unbind("<<save-window-as-file>>",self.__id_saveas)
        self.text.unbind("<<save-copy-of-window-as-file>>", self.__id_savecopy)
        self.text.unbind("<<print-window>>", self.__id_print)
        # Break cycles
        self.editwin = Tupu
        self.text = Tupu
        self.filename_change_hook = Tupu

    eleza get_saved(self):
        rudisha self.editwin.get_saved()

    eleza set_saved(self, flag):
        self.editwin.set_saved(flag)

    eleza reset_undo(self):
        self.editwin.reset_undo()

    filename_change_hook = Tupu

    eleza set_filename_change_hook(self, hook):
        self.filename_change_hook = hook

    filename = Tupu
    dirname = Tupu

    eleza set_filename(self, filename):
        ikiwa filename na os.path.isdir(filename):
            self.filename = Tupu
            self.dirname = filename
        isipokua:
            self.filename = filename
            self.dirname = Tupu
            self.set_saved(1)
            ikiwa self.filename_change_hook:
                self.filename_change_hook()

    eleza open(self, event=Tupu, editFile=Tupu):
        flist = self.editwin.flist
        # Save kwenye case parent window ni closed (ie, during askopenfile()).
        ikiwa flist:
            ikiwa sio editFile:
                filename = self.askopenfile()
            isipokua:
                filename=editFile
            ikiwa filename:
                # If editFile ni valid na already open, flist.open will
                # shift focus to its existing window.
                # If the current window exists na ni a fresh unnamed,
                # unmodified editor window (sio an interpreter shell),
                # pita self.loadfile to flist.open so it will load the file
                # kwenye the current window (ikiwa the file ni sio already open)
                # instead of a new window.
                ikiwa (self.editwin na
                        sio getattr(self.editwin, 'interp', Tupu) na
                        sio self.filename na
                        self.get_saved()):
                    flist.open(filename, self.loadfile)
                isipokua:
                    flist.open(filename)
            isipokua:
                ikiwa self.text:
                    self.text.focus_set()
            rudisha "koma"

        # Code kila use outside IDLE:
        ikiwa self.get_saved():
            reply = self.maybesave()
            ikiwa reply == "cancel":
                self.text.focus_set()
                rudisha "koma"
        ikiwa sio editFile:
            filename = self.askopenfile()
        isipokua:
            filename=editFile
        ikiwa filename:
            self.loadfile(filename)
        isipokua:
            self.text.focus_set()
        rudisha "koma"

    eol = r"(\r\n)|\n|\r"  # \r\n (Windows), \n (UNIX), ama \r (Mac)
    eol_re = re.compile(eol)
    eol_convention = os.linesep  # default

    eleza loadfile(self, filename):
        jaribu:
            # open the file kwenye binary mode so that we can handle
            # end-of-line convention ourselves.
            ukijumuisha open(filename, 'rb') kama f:
                two_lines = f.readline() + f.readline()
                f.seek(0)
                bytes = f.read()
        tatizo OSError kama msg:
            tkMessageBox.showerror("I/O Error", str(msg), parent=self.text)
            rudisha Uongo
        chars, converted = self._decode(two_lines, bytes)
        ikiwa chars ni Tupu:
            tkMessageBox.showerror("Decoding Error",
                                   "File %s\nFailed to Decode" % filename,
                                   parent=self.text)
            rudisha Uongo
        # We now convert all end-of-lines to '\n's
        firsteol = self.eol_re.search(chars)
        ikiwa firsteol:
            self.eol_convention = firsteol.group(0)
            chars = self.eol_re.sub(r"\n", chars)
        self.text.delete("1.0", "end")
        self.set_filename(Tupu)
        self.text.insert("1.0", chars)
        self.reset_undo()
        self.set_filename(filename)
        ikiwa converted:
            # We need to save the conversion results first
            # before being able to execute the code
            self.set_saved(Uongo)
        self.text.mark_set("insert", "1.0")
        self.text.yview("insert")
        self.updaterecentfileslist(filename)
        rudisha Kweli

    eleza _decode(self, two_lines, bytes):
        "Create a Unicode string."
        chars = Tupu
        # Check presence of a UTF-8 signature first
        ikiwa bytes.startswith(BOM_UTF8):
            jaribu:
                chars = bytes[3:].decode("utf-8")
            tatizo UnicodeDecodeError:
                # has UTF-8 signature, but fails to decode...
                rudisha Tupu, Uongo
            isipokua:
                # Indicates that this file originally had a BOM
                self.fileencoding = 'BOM'
                rudisha chars, Uongo
        # Next look kila coding specification
        jaribu:
            enc = coding_spec(two_lines)
        tatizo LookupError kama name:
            tkMessageBox.showerror(
                title="Error loading the file",
                message="The encoding '%s' ni sio known to this Python "\
                "installation. The file may sio display correctly" % name,
                parent = self.text)
            enc = Tupu
        tatizo UnicodeDecodeError:
            rudisha Tupu, Uongo
        ikiwa enc:
            jaribu:
                chars = str(bytes, enc)
                self.fileencoding = enc
                rudisha chars, Uongo
            tatizo UnicodeDecodeError:
                pita
        # Try ascii:
        jaribu:
            chars = str(bytes, 'ascii')
            self.fileencoding = Tupu
            rudisha chars, Uongo
        tatizo UnicodeDecodeError:
            pita
        # Try utf-8:
        jaribu:
            chars = str(bytes, 'utf-8')
            self.fileencoding = 'utf-8'
            rudisha chars, Uongo
        tatizo UnicodeDecodeError:
            pita
        # Finally, try the locale's encoding. This ni deprecated;
        # the user should declare a non-ASCII encoding
        jaribu:
            # Wait kila the editor window to appear
            self.editwin.text.update()
            enc = askstring(
                "Specify file encoding",
                "The file's encoding ni invalid kila Python 3.x.\n"
                "IDLE will convert it to UTF-8.\n"
                "What ni the current encoding of the file?",
                initialvalue = encoding,
                parent = self.editwin.text)

            ikiwa enc:
                chars = str(bytes, enc)
                self.fileencoding = Tupu
            rudisha chars, Kweli
        tatizo (UnicodeDecodeError, LookupError):
            pita
        rudisha Tupu, Uongo  # Tupu on failure

    eleza maybesave(self):
        ikiwa self.get_saved():
            rudisha "yes"
        message = "Do you want to save %s before closing?" % (
            self.filename ama "this untitled document")
        confirm = tkMessageBox.askyesnocancel(
                  title="Save On Close",
                  message=message,
                  default=tkMessageBox.YES,
                  parent=self.text)
        ikiwa confirm:
            reply = "yes"
            self.save(Tupu)
            ikiwa sio self.get_saved():
                reply = "cancel"
        lasivyo confirm ni Tupu:
            reply = "cancel"
        isipokua:
            reply = "no"
        self.text.focus_set()
        rudisha reply

    eleza save(self, event):
        ikiwa sio self.filename:
            self.save_as(event)
        isipokua:
            ikiwa self.writefile(self.filename):
                self.set_saved(Kweli)
                jaribu:
                    self.editwin.store_file_komas()
                tatizo AttributeError:  # may be a PyShell
                    pita
        self.text.focus_set()
        rudisha "koma"

    eleza save_as(self, event):
        filename = self.asksavefile()
        ikiwa filename:
            ikiwa self.writefile(filename):
                self.set_filename(filename)
                self.set_saved(1)
                jaribu:
                    self.editwin.store_file_komas()
                tatizo AttributeError:
                    pita
        self.text.focus_set()
        self.updaterecentfileslist(filename)
        rudisha "koma"

    eleza save_a_copy(self, event):
        filename = self.asksavefile()
        ikiwa filename:
            self.writefile(filename)
        self.text.focus_set()
        self.updaterecentfileslist(filename)
        rudisha "koma"

    eleza writefile(self, filename):
        self.fixlastline()
        text = self.text.get("1.0", "end-1c")
        ikiwa self.eol_convention != "\n":
            text = text.replace("\n", self.eol_convention)
        chars = self.encode(text)
        jaribu:
            ukijumuisha open(filename, "wb") kama f:
                f.write(chars)
                f.flush()
                os.fsync(f.fileno())
            rudisha Kweli
        tatizo OSError kama msg:
            tkMessageBox.showerror("I/O Error", str(msg),
                                   parent=self.text)
            rudisha Uongo

    eleza encode(self, chars):
        ikiwa isinstance(chars, bytes):
            # This ni either plain ASCII, ama Tk was returning mixed-encoding
            # text to us. Don't try to guess further.
            rudisha chars
        # Preserve a BOM that might have been present on opening
        ikiwa self.fileencoding == 'BOM':
            rudisha BOM_UTF8 + chars.encode("utf-8")
        # See whether there ni anything non-ASCII kwenye it.
        # If not, no need to figure out the encoding.
        jaribu:
            rudisha chars.encode('ascii')
        tatizo UnicodeError:
            pita
        # Check ikiwa there ni an encoding declared
        jaribu:
            # a string, let coding_spec slice it to the first two lines
            enc = coding_spec(chars)
            failed = Tupu
        tatizo LookupError kama msg:
            failed = msg
            enc = Tupu
        isipokua:
            ikiwa sio enc:
                # PEP 3120: default source encoding ni UTF-8
                enc = 'utf-8'
        ikiwa enc:
            jaribu:
                rudisha chars.encode(enc)
            tatizo UnicodeError:
                failed = "Invalid encoding '%s'" % enc
        tkMessageBox.showerror(
            "I/O Error",
            "%s.\nSaving kama UTF-8" % failed,
            parent = self.text)
        # Fallback: save kama UTF-8, ukijumuisha BOM - ignoring the incorrect
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
        ikiwa sio confirm:
            self.text.focus_set()
            rudisha "koma"
        tempfilename = Tupu
        saved = self.get_saved()
        ikiwa saved:
            filename = self.filename
        # shell undo ni reset after every prompt, looks saved, probably isn't
        ikiwa sio saved ama filename ni Tupu:
            (tfd, tempfilename) = tempfile.mkstemp(prefix='IDLE_tmp_')
            filename = tempfilename
            os.close(tfd)
            ikiwa sio self.writefile(tempfilename):
                os.unlink(tempfilename)
                rudisha "koma"
        platform = os.name
        printPlatform = Kweli
        ikiwa platform == 'posix': #posix platform
            command = idleConf.GetOption('main','General',
                                         'print-command-posix')
            command = command + " 2>&1"
        lasivyo platform == 'nt': #win32 platform
            command = idleConf.GetOption('main','General','print-command-win')
        isipokua: #no printing kila this platform
            printPlatform = Uongo
        ikiwa printPlatform:  #we can try to andika kila this platform
            command = command % shlex.quote(filename)
            pipe = os.popen(command, "r")
            # things can get ugly on NT ikiwa there ni no printer available.
            output = pipe.read().strip()
            status = pipe.close()
            ikiwa status:
                output = "Printing failed (exit status 0x%x)\n" % \
                         status + output
            ikiwa output:
                output = "Printing command: %s\n" % repr(command) + output
                tkMessageBox.showerror("Print status", output, parent=self.text)
        isipokua:  #no printing kila this platform
            message = "Printing ni sio enabled kila this platform: %s" % platform
            tkMessageBox.showinfo("Print status", message, parent=self.text)
        ikiwa tempfilename:
            os.unlink(tempfilename)
        rudisha "koma"

    opendialog = Tupu
    savedialog = Tupu

    filetypes = (
        ("Python files", "*.py *.pyw", "TEXT"),
        ("Text files", "*.txt", "TEXT"),
        ("All files", "*"),
        )

    defaultextension = '.py' ikiwa sys.platform == 'darwin' isipokua ''

    eleza askopenfile(self):
        dir, base = self.defaultfilename("open")
        ikiwa sio self.opendialog:
            self.opendialog = tkFileDialog.Open(parent=self.text,
                                                filetypes=self.filetypes)
        filename = self.opendialog.show(initialdir=dir, initialfile=base)
        rudisha filename

    eleza defaultfilename(self, mode="open"):
        ikiwa self.filename:
            rudisha os.path.split(self.filename)
        lasivyo self.dirname:
            rudisha self.dirname, ""
        isipokua:
            jaribu:
                pwd = os.getcwd()
            tatizo OSError:
                pwd = ""
            rudisha pwd, ""

    eleza asksavefile(self):
        dir, base = self.defaultfilename("save")
        ikiwa sio self.savedialog:
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
            self.flist = Tupu
            self.text.bind("<Control-o>", self.open)
            self.text.bind('<Control-p>', self.print)
            self.text.bind("<Control-s>", self.save)
            self.text.bind("<Alt-s>", self.saveas)
            self.text.bind('<Control-c>', self.savecopy)
        eleza get_saved(self): rudisha 0
        eleza set_saved(self, flag): pita
        eleza reset_undo(self): pita
        eleza open(self, event):
            self.text.event_generate("<<open-window-from-file>>")
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
    main('idlelib.idle_test.test_iomenu', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_io_binding)
