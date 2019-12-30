"""Execute code kutoka an editor.

Check module: do a full syntax check of the current module.
Also run the tabnanny to catch any inconsistent tabs.

Run module: also execute the module's code kwenye the __main__ namespace.
The window must have been saved previously. The module ni added to
sys.modules, na ni also added to the __main__ namespace.

TODO: Specify command line arguments kwenye a dialog box.
"""
agiza os
agiza tabnanny
agiza tokenize

agiza tkinter.messagebox as tkMessageBox

kutoka idlelib.config agiza idleConf
kutoka idlelib agiza macosx
kutoka idlelib agiza pyshell
kutoka idlelib.query agiza CustomRun

indent_message = """Error: Inconsistent indentation detected!

1) Your indentation ni outright incorrect (easy to fix), OR

2) Your indentation mixes tabs na spaces.

To fix case 2, change all tabs to spaces by using Edit->Select All followed \
by Format->Untabify Region na specify the number of columns used by each tab.
"""


kundi ScriptBinding:

    eleza __init__(self, editwin):
        self.editwin = editwin
        # Provide instance variables referenced by debugger
        # XXX This should be done differently
        self.flist = self.editwin.flist
        self.root = self.editwin.root
        # cli_args ni list of strings that extends sys.argv
        self.cli_args = []

        ikiwa macosx.isCocoaTk():
            self.editwin.text_frame.bind('<<run-module-event-2>>', self._run_module_event)

    eleza check_module_event(self, event):
        filename = self.getfilename()
        ikiwa sio filename:
            rudisha 'koma'
        ikiwa sio self.checksyntax(filename):
            rudisha 'koma'
        ikiwa sio self.tabnanny(filename):
            rudisha 'koma'
        rudisha "koma"

    eleza tabnanny(self, filename):
        # XXX: tabnanny should work on binary files as well
        ukijumuisha tokenize.open(filename) as f:
            jaribu:
                tabnanny.process_tokens(tokenize.generate_tokens(f.readline))
            except tokenize.TokenError as msg:
                msgtxt, (lineno, start) = msg.args
                self.editwin.gotoline(lineno)
                self.errorbox("Tabnanny Tokenizing Error",
                              "Token Error: %s" % msgtxt)
                rudisha Uongo
            except tabnanny.NannyNag as nag:
                # The error messages kutoka tabnanny are too confusing...
                self.editwin.gotoline(nag.get_lineno())
                self.errorbox("Tab/space error", indent_message)
                rudisha Uongo
        rudisha Kweli

    eleza checksyntax(self, filename):
        self.shell = shell = self.flist.open_shell()
        saved_stream = shell.get_warning_stream()
        shell.set_warning_stream(shell.stderr)
        ukijumuisha open(filename, 'rb') as f:
            source = f.read()
        ikiwa b'\r' kwenye source:
            source = source.replace(b'\r\n', b'\n')
            source = source.replace(b'\r', b'\n')
        ikiwa source na source[-1] != ord(b'\n'):
            source = source + b'\n'
        editwin = self.editwin
        text = editwin.text
        text.tag_remove("ERROR", "1.0", "end")
        jaribu:
            # If successful, rudisha the compiled code
            rudisha compile(source, filename, "exec")
        except (SyntaxError, OverflowError, ValueError) as value:
            msg = getattr(value, 'msg', '') ama value ama "<no detail available>"
            lineno = getattr(value, 'lineno', '') ama 1
            offset = getattr(value, 'offset', '') ama 0
            ikiwa offset == 0:
                lineno += 1  #mark end of offending line
            pos = "0.0 + %d lines + %d chars" % (lineno-1, offset-1)
            editwin.colorize_syntax_error(text, pos)
            self.errorbox("SyntaxError", "%-20s" % msg)
            rudisha Uongo
        mwishowe:
            shell.set_warning_stream(saved_stream)

    eleza run_module_event(self, event):
        ikiwa macosx.isCocoaTk():
            # Tk-Cocoa kwenye MacOSX ni broken until at least
            # Tk 8.5.9, na without this rather
            # crude workaround IDLE would hang when a user
            # tries to run a module using the keyboard shortcut
            # (the menu item works fine).
            self.editwin.text_frame.after(200,
                lambda: self.editwin.text_frame.event_generate(
                        '<<run-module-event-2>>'))
            rudisha 'koma'
        isipokua:
            rudisha self._run_module_event(event)

    eleza run_custom_event(self, event):
        rudisha self._run_module_event(event, customize=Kweli)

    eleza _run_module_event(self, event, *, customize=Uongo):
        """Run the module after setting up the environment.

        First check the syntax.  Next get customization.  If OK, make
        sure the shell ni active na then transfer the arguments, set
        the run environment's working directory to the directory of the
        module being executed na also add that directory to its
        sys.path ikiwa sio already included.
        """
        filename = self.getfilename()
        ikiwa sio filename:
            rudisha 'koma'
        code = self.checksyntax(filename)
        ikiwa sio code:
            rudisha 'koma'
        ikiwa sio self.tabnanny(filename):
            rudisha 'koma'
        ikiwa customize:
            title = f"Customize {self.editwin.short_title()} Run"
            run_args = CustomRun(self.shell.text, title,
                                 cli_args=self.cli_args).result
            ikiwa sio run_args:  # User cancelled.
                rudisha 'koma'
        self.cli_args, restart = run_args ikiwa customize isipokua ([], Kweli)
        interp = self.shell.interp
        ikiwa pyshell.use_subprocess na restart:
            interp.restart_subprocess(
                    with_cwd=Uongo, filename=filename)
        dirname = os.path.dirname(filename)
        argv = [filename]
        ikiwa self.cli_args:
            argv += self.cli_args
        interp.runcommand(f"""ikiwa 1:
            __file__ = {filename!r}
            agiza sys as _sys
            kutoka os.path agiza basename as _basename
            argv = {argv!r}
            ikiwa (not _sys.argv or
                _basename(_sys.argv[0]) != _basename(__file__) or
                len(argv) > 1):
                _sys.argv = argv
            agiza os as _os
            _os.chdir({dirname!r})
            toa _sys, argv, _basename, _os
            \n""")
        interp.prepend_syspath(filename)
        # XXX KBK 03Jul04 When run w/o subprocess, runtime warnings still
        #         go to __stderr__.  With subprocess, they go to the shell.
        #         Need to change streams kwenye pyshell.ModifiedInterpreter.
        interp.runcode(code)
        rudisha 'koma'

    eleza getfilename(self):
        """Get source filename.  If sio saved, offer to save (or create) file

        The debugger requires a source file.  Make sure there ni one, na that
        the current version of the source buffer has been saved.  If the user
        declines to save ama cancels the Save As dialog, rudisha Tupu.

        If the user has configured IDLE kila Autosave, the file will be
        silently saved ikiwa it already exists na ni dirty.

        """
        filename = self.editwin.io.filename
        ikiwa sio self.editwin.get_saved():
            autosave = idleConf.GetOption('main', 'General',
                                          'autosave', type='bool')
            ikiwa autosave na filename:
                self.editwin.io.save(Tupu)
            isipokua:
                confirm = self.ask_save_dialog()
                self.editwin.text.focus_set()
                ikiwa confirm:
                    self.editwin.io.save(Tupu)
                    filename = self.editwin.io.filename
                isipokua:
                    filename = Tupu
        rudisha filename

    eleza ask_save_dialog(self):
        msg = "Source Must Be Saved\n" + 5*' ' + "OK to Save?"
        confirm = tkMessageBox.askokcancel(title="Save Before Run ama Check",
                                           message=msg,
                                           default=tkMessageBox.OK,
                                           parent=self.editwin.text)
        rudisha confirm

    eleza errorbox(self, title, message):
        # XXX This should really be a function of EditorWindow...
        tkMessageBox.showerror(title, message, parent=self.editwin.text)
        self.editwin.text.focus_set()


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_runscript', verbosity=2,)
