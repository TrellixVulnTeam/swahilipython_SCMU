agiza importlib.abc
agiza importlib.util
agiza os
agiza platform
agiza re
agiza string
agiza sys
agiza tokenize
agiza traceback
agiza webbrowser

kutoka tkinter agiza *
kutoka tkinter.font agiza Font
kutoka tkinter.ttk agiza Scrollbar
agiza tkinter.simpledialog as tkSimpleDialog
agiza tkinter.messagebox as tkMessageBox

kutoka idlelib.config agiza idleConf
kutoka idlelib agiza configdialog
kutoka idlelib agiza grep
kutoka idlelib agiza help
kutoka idlelib agiza help_about
kutoka idlelib agiza macosx
kutoka idlelib.multicall agiza MultiCallCreator
kutoka idlelib agiza pyparse
kutoka idlelib agiza query
kutoka idlelib agiza replace
kutoka idlelib agiza search
kutoka idlelib.tree agiza wheel_event
kutoka idlelib agiza window

# The default tab setting for a Text widget, in average-width characters.
TK_TABWIDTH_DEFAULT = 8
_py_version = ' (%s)' % platform.python_version()
darwin = sys.platform == 'darwin'

eleza _sphinx_version():
    "Format sys.version_info to produce the Sphinx version string used to install the chm docs"
    major, minor, micro, level, serial = sys.version_info
    release = '%s%s' % (major, minor)
    release += '%s' % (micro,)
    ikiwa level == 'candidate':
        release += 'rc%s' % (serial,)
    elikiwa level != 'final':
        release += '%s%s' % (level[0], serial)
    rudisha release


kundi EditorWindow(object):
    kutoka idlelib.percolator agiza Percolator
    kutoka idlelib.colorizer agiza ColorDelegator, color_config
    kutoka idlelib.undo agiza UndoDelegator
    kutoka idlelib.iomenu agiza IOBinding, encoding
    kutoka idlelib agiza mainmenu
    kutoka idlelib.statusbar agiza MultiStatusBar
    kutoka idlelib.autocomplete agiza AutoComplete
    kutoka idlelib.autoexpand agiza AutoExpand
    kutoka idlelib.calltip agiza Calltip
    kutoka idlelib.codecontext agiza CodeContext
    kutoka idlelib.sidebar agiza LineNumbers
    kutoka idlelib.format agiza FormatParagraph, FormatRegion, Indents, Rstrip
    kutoka idlelib.parenmatch agiza ParenMatch
    kutoka idlelib.squeezer agiza Squeezer
    kutoka idlelib.zoomheight agiza ZoomHeight

    filesystemencoding = sys.getfilesystemencoding()  # for file names
    help_url = None

    allow_code_context = True
    allow_line_numbers = True

    eleza __init__(self, flist=None, filename=None, key=None, root=None):
        # Delay agiza: runscript agizas pyshell agizas EditorWindow.
        kutoka idlelib.runscript agiza ScriptBinding

        ikiwa EditorWindow.help_url is None:
            dochome =  os.path.join(sys.base_prefix, 'Doc', 'index.html')
            ikiwa sys.platform.count('linux'):
                # look for html docs in a couple of standard places
                pyver = 'python-docs-' + '%s.%s.%s' % sys.version_info[:3]
                ikiwa os.path.isdir('/var/www/html/python/'):  # "python2" rpm
                    dochome = '/var/www/html/python/index.html'
                else:
                    basepath = '/usr/share/doc/'  # standard location
                    dochome = os.path.join(basepath, pyver,
                                           'Doc', 'index.html')
            elikiwa sys.platform[:3] == 'win':
                chmfile = os.path.join(sys.base_prefix, 'Doc',
                                       'Python%s.chm' % _sphinx_version())
                ikiwa os.path.isfile(chmfile):
                    dochome = chmfile
            elikiwa sys.platform == 'darwin':
                # documentation may be stored inside a python framework
                dochome = os.path.join(sys.base_prefix,
                        'Resources/English.lproj/Documentation/index.html')
            dochome = os.path.normpath(dochome)
            ikiwa os.path.isfile(dochome):
                EditorWindow.help_url = dochome
                ikiwa sys.platform == 'darwin':
                    # Safari requires real file:-URLs
                    EditorWindow.help_url = 'file://' + EditorWindow.help_url
            else:
                EditorWindow.help_url = ("https://docs.python.org/%d.%d/"
                                         % sys.version_info[:2])
        self.flist = flist
        root = root or flist.root
        self.root = root
        self.menubar = Menu(root)
        self.top = top = window.ListedToplevel(root, menu=self.menubar)
        ikiwa flist:
            self.tkinter_vars = flist.vars
            #self.top.instance_dict makes flist.inversedict available to
            #configdialog.py so it can access all EditorWindow instances
            self.top.instance_dict = flist.inversedict
        else:
            self.tkinter_vars = {}  # keys: Tkinter event names
                                    # values: Tkinter variable instances
            self.top.instance_dict = {}
        self.recent_files_path = idleConf.userdir and os.path.join(
                idleConf.userdir, 'recent-files.lst')

        self.prompt_last_line = ''  # Override in PyShell
        self.text_frame = text_frame = Frame(top)
        self.vbar = vbar = Scrollbar(text_frame, name='vbar')
        width = idleConf.GetOption('main', 'EditorWindow', 'width', type='int')
        text_options = {
                'name': 'text',
                'padx': 5,
                'wrap': 'none',
                'highlightthickness': 0,
                'width': width,
                'tabstyle': 'wordprocessor',  # new in 8.5
                'height': idleConf.GetOption(
                        'main', 'EditorWindow', 'height', type='int'),
                }
        self.text = text = MultiCallCreator(Text)(text_frame, **text_options)
        self.top.focused_widget = self.text

        self.createmenubar()
        self.apply_bindings()

        self.top.protocol("WM_DELETE_WINDOW", self.close)
        self.top.bind("<<close-window>>", self.close_event)
        ikiwa macosx.isAquaTk():
            # Command-W on editor windows doesn't work without this.
            text.bind('<<close-window>>', self.close_event)
            # Some OS X systems have only one mouse button, so use
            # control-click for popup context menus there. For two
            # buttons, AquaTk defines <2> as the right button, not <3>.
            text.bind("<Control-Button-1>",self.right_menu_event)
            text.bind("<2>", self.right_menu_event)
        else:
            # Elsewhere, use right-click for popup menus.
            text.bind("<3>",self.right_menu_event)

        text.bind('<MouseWheel>', wheel_event)
        text.bind('<Button-4>', wheel_event)
        text.bind('<Button-5>', wheel_event)
        text.bind('<Configure>', self.handle_winconfig)
        text.bind("<<cut>>", self.cut)
        text.bind("<<copy>>", self.copy)
        text.bind("<<paste>>", self.paste)
        text.bind("<<center-insert>>", self.center_insert_event)
        text.bind("<<help>>", self.help_dialog)
        text.bind("<<python-docs>>", self.python_docs)
        text.bind("<<about-idle>>", self.about_dialog)
        text.bind("<<open-config-dialog>>", self.config_dialog)
        text.bind("<<open-module>>", self.open_module_event)
        text.bind("<<do-nothing>>", lambda event: "break")
        text.bind("<<select-all>>", self.select_all)
        text.bind("<<remove-selection>>", self.remove_selection)
        text.bind("<<find>>", self.find_event)
        text.bind("<<find-again>>", self.find_again_event)
        text.bind("<<find-in-files>>", self.find_in_files_event)
        text.bind("<<find-selection>>", self.find_selection_event)
        text.bind("<<replace>>", self.replace_event)
        text.bind("<<goto-line>>", self.goto_line_event)
        text.bind("<<smart-backspace>>",self.smart_backspace_event)
        text.bind("<<newline-and-indent>>",self.newline_and_indent_event)
        text.bind("<<smart-indent>>",self.smart_indent_event)
        self.fregion = fregion = self.FormatRegion(self)
        # self.fregion used in smart_indent_event to access indent_region.
        text.bind("<<indent-region>>", fregion.indent_region_event)
        text.bind("<<dedent-region>>", fregion.dedent_region_event)
        text.bind("<<comment-region>>", fregion.comment_region_event)
        text.bind("<<uncomment-region>>", fregion.uncomment_region_event)
        text.bind("<<tabify-region>>", fregion.tabify_region_event)
        text.bind("<<untabify-region>>", fregion.untabify_region_event)
        text.bind("<<toggle-tabs>>", self.Indents.toggle_tabs_event)
        text.bind("<<change-indentwidth>>", self.Indents.change_indentwidth_event)
        text.bind("<Left>", self.move_at_edge_if_selection(0))
        text.bind("<Right>", self.move_at_edge_if_selection(1))
        text.bind("<<del-word-left>>", self.del_word_left)
        text.bind("<<del-word-right>>", self.del_word_right)
        text.bind("<<beginning-of-line>>", self.home_callback)

        ikiwa flist:
            flist.inversedict[self] = key
            ikiwa key:
                flist.dict[key] = self
            text.bind("<<open-new-window>>", self.new_callback)
            text.bind("<<close-all-windows>>", self.flist.close_all_callback)
            text.bind("<<open-class-browser>>", self.open_module_browser)
            text.bind("<<open-path-browser>>", self.open_path_browser)
            text.bind("<<open-turtle-demo>>", self.open_turtle_demo)

        self.set_status_bar()
        text_frame.pack(side=LEFT, fill=BOTH, expand=1)
        text_frame.rowconfigure(1, weight=1)
        text_frame.columnconfigure(1, weight=1)
        vbar['command'] = self.handle_yview
        vbar.grid(row=1, column=2, sticky=NSEW)
        text['yscrollcommand'] = vbar.set
        text['font'] = idleConf.GetFont(self.root, 'main', 'EditorWindow')
        text.grid(row=1, column=1, sticky=NSEW)
        text.focus_set()
        self.set_width()

        # usetabs true  -> literal tab characters are used by indent and
        #                  dedent cmds, possibly mixed with spaces if
        #                  indentwidth is not a multiple of tabwidth,
        #                  which will cause Tabnanny to nag!
        #         false -> tab characters are converted to spaces by indent
        #                  and dedent cmds, and ditto TAB keystrokes
        # Although use-spaces=0 can be configured manually in config-main.def,
        # configuration of tabs v. spaces is not supported in the configuration
        # dialog.  IDLE promotes the preferred Python indentation: use spaces!
        usespaces = idleConf.GetOption('main', 'Indent',
                                       'use-spaces', type='bool')
        self.usetabs = not usespaces

        # tabwidth is the display width of a literal tab character.
        # CAUTION:  telling Tk to use anything other than its default
        # tab setting causes it to use an entirely different tabbing algorithm,
        # treating tab stops as fixed distances kutoka the left margin.
        # Nobody expects this, so for now tabwidth should never be changed.
        self.tabwidth = 8    # must remain 8 until Tk is fixed.

        # indentwidth is the number of screen characters per indent level.
        # The recommended Python indentation is four spaces.
        self.indentwidth = self.tabwidth
        self.set_notabs_indentwidth()

        # When searching backwards for a reliable place to begin parsing,
        # first start num_context_lines[0] lines back, then
        # num_context_lines[1] lines back ikiwa that didn't work, and so on.
        # The last value should be huge (larger than the # of lines in a
        # conceivable file).
        # Making the initial values larger slows things down more often.
        self.num_context_lines = 50, 500, 5000000
        self.per = per = self.Percolator(text)
        self.undo = undo = self.UndoDelegator()
        per.insertfilter(undo)
        text.undo_block_start = undo.undo_block_start
        text.undo_block_stop = undo.undo_block_stop
        undo.set_saved_change_hook(self.saved_change_hook)
        # IOBinding implements file I/O and printing functionality
        self.io = io = self.IOBinding(self)
        io.set_filename_change_hook(self.filename_change_hook)
        self.good_load = False
        self.set_indentation_params(False)
        self.color = None # initialized below in self.ResetColorizer
        self.code_context = None # optionally initialized later below
        self.line_numbers = None # optionally initialized later below
        ikiwa filename:
            ikiwa os.path.exists(filename) and not os.path.isdir(filename):
                ikiwa io.loadfile(filename):
                    self.good_load = True
                    is_py_src = self.ispythonsource(filename)
                    self.set_indentation_params(is_py_src)
            else:
                io.set_filename(filename)
                self.good_load = True

        self.ResetColorizer()
        self.saved_change_hook()
        self.update_recent_files_list()
        self.load_extensions()
        menu = self.menudict.get('window')
        ikiwa menu:
            end = menu.index("end")
            ikiwa end is None:
                end = -1
            ikiwa end >= 0:
                menu.add_separator()
                end = end + 1
            self.wmenu_end = end
            window.register_callback(self.postwindowsmenu)

        # Some abstractions so IDLE extensions are cross-IDE
        self.askyesno = tkMessageBox.askyesno
        self.askinteger = tkSimpleDialog.askinteger
        self.showerror = tkMessageBox.showerror

        # Add pseudoevents for former extension fixed keys.
        # (This probably needs to be done once in the process.)
        text.event_add('<<autocomplete>>', '<Key-Tab>')
        text.event_add('<<try-open-completions>>', '<KeyRelease-period>',
                       '<KeyRelease-slash>', '<KeyRelease-backslash>')
        text.event_add('<<try-open-calltip>>', '<KeyRelease-parenleft>')
        text.event_add('<<refresh-calltip>>', '<KeyRelease-parenright>')
        text.event_add('<<paren-closed>>', '<KeyRelease-parenright>',
                       '<KeyRelease-bracketright>', '<KeyRelease-braceright>')

        # Former extension bindings depends on frame.text being packed
        # (called kutoka self.ResetColorizer()).
        autocomplete = self.AutoComplete(self)
        text.bind("<<autocomplete>>", autocomplete.autocomplete_event)
        text.bind("<<try-open-completions>>",
                  autocomplete.try_open_completions_event)
        text.bind("<<force-open-completions>>",
                  autocomplete.force_open_completions_event)
        text.bind("<<expand-word>>", self.AutoExpand(self).expand_word_event)
        text.bind("<<format-paragraph>>",
                  self.FormatParagraph(self).format_paragraph_event)
        parenmatch = self.ParenMatch(self)
        text.bind("<<flash-paren>>", parenmatch.flash_paren_event)
        text.bind("<<paren-closed>>", parenmatch.paren_closed_event)
        scriptbinding = ScriptBinding(self)
        text.bind("<<check-module>>", scriptbinding.check_module_event)
        text.bind("<<run-module>>", scriptbinding.run_module_event)
        text.bind("<<run-custom>>", scriptbinding.run_custom_event)
        text.bind("<<do-rstrip>>", self.Rstrip(self).do_rstrip)
        ctip = self.Calltip(self)
        text.bind("<<try-open-calltip>>", ctip.try_open_calltip_event)
        #refresh-calltip must come after paren-closed to work right
        text.bind("<<refresh-calltip>>", ctip.refresh_calltip_event)
        text.bind("<<force-open-calltip>>", ctip.force_open_calltip_event)
        text.bind("<<zoom-height>>", self.ZoomHeight(self).zoom_height_event)
        ikiwa self.allow_code_context:
            self.code_context = self.CodeContext(self)
            text.bind("<<toggle-code-context>>",
                      self.code_context.toggle_code_context_event)
        else:
            self.update_menu_state('options', '*Code Context', 'disabled')
        ikiwa self.allow_line_numbers:
            self.line_numbers = self.LineNumbers(self)
            ikiwa idleConf.GetOption('main', 'EditorWindow',
                                  'line-numbers-default', type='bool'):
                self.toggle_line_numbers_event()
            text.bind("<<toggle-line-numbers>>", self.toggle_line_numbers_event)
        else:
            self.update_menu_state('options', '*Line Numbers', 'disabled')

    eleza handle_winconfig(self, event=None):
        self.set_width()

    eleza set_width(self):
        text = self.text
        inner_padding = sum(map(text.tk.getint, [text.cget('border'),
                                                 text.cget('padx')]))
        pixel_width = text.winfo_width() - 2 * inner_padding

        # Divide the width of the Text widget by the font width,
        # which is taken to be the width of '0' (zero).
        # http://www.tcl.tk/man/tcl8.6/TkCmd/text.htm#M21
        zero_char_width = \
            Font(text, font=text.cget('font')).measure('0')
        self.width = pixel_width // zero_char_width

    eleza new_callback(self, event):
        dirname, basename = self.io.defaultfilename()
        self.flist.new(dirname)
        rudisha "break"

    eleza home_callback(self, event):
        ikiwa (event.state & 4) != 0 and event.keysym == "Home":
            # state&4==Control. If <Control-Home>, use the Tk binding.
            rudisha None
        ikiwa self.text.index("iomark") and \
           self.text.compare("iomark", "<=", "insert lineend") and \
           self.text.compare("insert linestart", "<=", "iomark"):
            # In Shell on input line, go to just after prompt
            insertpt = int(self.text.index("iomark").split(".")[1])
        else:
            line = self.text.get("insert linestart", "insert lineend")
            for insertpt in range(len(line)):
                ikiwa line[insertpt] not in (' ','\t'):
                    break
            else:
                insertpt=len(line)
        lineat = int(self.text.index("insert").split('.')[1])
        ikiwa insertpt == lineat:
            insertpt = 0
        dest = "insert linestart+"+str(insertpt)+"c"
        ikiwa (event.state&1) == 0:
            # shift was not pressed
            self.text.tag_remove("sel", "1.0", "end")
        else:
            ikiwa not self.text.index("sel.first"):
                # there was no previous selection
                self.text.mark_set("my_anchor", "insert")
            else:
                ikiwa self.text.compare(self.text.index("sel.first"), "<",
                                     self.text.index("insert")):
                    self.text.mark_set("my_anchor", "sel.first") # extend back
                else:
                    self.text.mark_set("my_anchor", "sel.last") # extend forward
            first = self.text.index(dest)
            last = self.text.index("my_anchor")
            ikiwa self.text.compare(first,">",last):
                first,last = last,first
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", first, last)
        self.text.mark_set("insert", dest)
        self.text.see("insert")
        rudisha "break"

    eleza set_status_bar(self):
        self.status_bar = self.MultiStatusBar(self.top)
        sep = Frame(self.top, height=1, borderwidth=1, background='grey75')
        ikiwa sys.platform == "darwin":
            # Insert some padding to avoid obscuring some of the statusbar
            # by the resize widget.
            self.status_bar.set_label('_padding1', '    ', side=RIGHT)
        self.status_bar.set_label('column', 'Col: ?', side=RIGHT)
        self.status_bar.set_label('line', 'Ln: ?', side=RIGHT)
        self.status_bar.pack(side=BOTTOM, fill=X)
        sep.pack(side=BOTTOM, fill=X)
        self.text.bind("<<set-line-and-column>>", self.set_line_and_column)
        self.text.event_add("<<set-line-and-column>>",
                            "<KeyRelease>", "<ButtonRelease>")
        self.text.after_idle(self.set_line_and_column)

    eleza set_line_and_column(self, event=None):
        line, column = self.text.index(INSERT).split('.')
        self.status_bar.set_label('column', 'Col: %s' % column)
        self.status_bar.set_label('line', 'Ln: %s' % line)

    menu_specs = [
        ("file", "_File"),
        ("edit", "_Edit"),
        ("format", "F_ormat"),
        ("run", "_Run"),
        ("options", "_Options"),
        ("window", "_Window"),
        ("help", "_Help"),
    ]


    eleza createmenubar(self):
        mbar = self.menubar
        self.menudict = menudict = {}
        for name, label in self.menu_specs:
            underline, label = prepstr(label)
            menudict[name] = menu = Menu(mbar, name=name, tearoff=0)
            mbar.add_cascade(label=label, menu=menu, underline=underline)
        ikiwa macosx.isCarbonTk():
            # Insert the application menu
            menudict['application'] = menu = Menu(mbar, name='apple',
                                                  tearoff=0)
            mbar.add_cascade(label='IDLE', menu=menu)
        self.fill_menus()
        self.recent_files_menu = Menu(self.menubar, tearoff=0)
        self.menudict['file'].insert_cascade(3, label='Recent Files',
                                             underline=0,
                                             menu=self.recent_files_menu)
        self.base_helpmenu_length = self.menudict['help'].index(END)
        self.reset_help_menu_entries()

    eleza postwindowsmenu(self):
        # Only called when Window menu exists
        menu = self.menudict['window']
        end = menu.index("end")
        ikiwa end is None:
            end = -1
        ikiwa end > self.wmenu_end:
            menu.delete(self.wmenu_end+1, end)
        window.add_windows_to_menu(menu)

    eleza update_menu_label(self, menu, index, label):
        "Update label for menu item at index."
        menuitem = self.menudict[menu]
        menuitem.entryconfig(index, label=label)

    eleza update_menu_state(self, menu, index, state):
        "Update state for menu item at index."
        menuitem = self.menudict[menu]
        menuitem.entryconfig(index, state=state)

    eleza handle_yview(self, event, *args):
        "Handle scrollbar."
        ikiwa event == 'moveto':
            fraction = float(args[0])
            lines = (round(self.getlineno('end') * fraction) -
                     self.getlineno('@0,0'))
            event = 'scroll'
            args = (lines, 'units')
        self.text.yview(event, *args)
        rudisha 'break'

    rmenu = None

    eleza right_menu_event(self, event):
        self.text.mark_set("insert", "@%d,%d" % (event.x, event.y))
        ikiwa not self.rmenu:
            self.make_rmenu()
        rmenu = self.rmenu
        self.event = event
        iswin = sys.platform[:3] == 'win'
        ikiwa iswin:
            self.text.config(cursor="arrow")

        for item in self.rmenu_specs:
            try:
                label, eventname, verify_state = item
            except ValueError: # see issue1207589
                continue

            ikiwa verify_state is None:
                continue
            state = getattr(self, verify_state)()
            rmenu.entryconfigure(label, state=state)


        rmenu.tk_popup(event.x_root, event.y_root)
        ikiwa iswin:
            self.text.config(cursor="ibeam")
        rudisha "break"

    rmenu_specs = [
        # ("Label", "<<virtual-event>>", "statefuncname"), ...
        ("Close", "<<close-window>>", None), # Example
    ]

    eleza make_rmenu(self):
        rmenu = Menu(self.text, tearoff=0)
        for item in self.rmenu_specs:
            label, eventname = item[0], item[1]
            ikiwa label is not None:
                eleza command(text=self.text, eventname=eventname):
                    text.event_generate(eventname)
                rmenu.add_command(label=label, command=command)
            else:
                rmenu.add_separator()
        self.rmenu = rmenu

    eleza rmenu_check_cut(self):
        rudisha self.rmenu_check_copy()

    eleza rmenu_check_copy(self):
        try:
            indx = self.text.index('sel.first')
        except TclError:
            rudisha 'disabled'
        else:
            rudisha 'normal' ikiwa indx else 'disabled'

    eleza rmenu_check_paste(self):
        try:
            self.text.tk.call('tk::GetSelection', self.text, 'CLIPBOARD')
        except TclError:
            rudisha 'disabled'
        else:
            rudisha 'normal'

    eleza about_dialog(self, event=None):
        "Handle Help 'About IDLE' event."
        # Synchronize with macosx.overrideRootMenu.about_dialog.
        help_about.AboutDialog(self.top)
        rudisha "break"

    eleza config_dialog(self, event=None):
        "Handle Options 'Configure IDLE' event."
        # Synchronize with macosx.overrideRootMenu.config_dialog.
        configdialog.ConfigDialog(self.top,'Settings')
        rudisha "break"

    eleza help_dialog(self, event=None):
        "Handle Help 'IDLE Help' event."
        # Synchronize with macosx.overrideRootMenu.help_dialog.
        ikiwa self.root:
            parent = self.root
        else:
            parent = self.top
        help.show_idlehelp(parent)
        rudisha "break"

    eleza python_docs(self, event=None):
        ikiwa sys.platform[:3] == 'win':
            try:
                os.startfile(self.help_url)
            except OSError as why:
                tkMessageBox.showerror(title='Document Start Failure',
                    message=str(why), parent=self.text)
        else:
            webbrowser.open(self.help_url)
        rudisha "break"

    eleza cut(self,event):
        self.text.event_generate("<<Cut>>")
        rudisha "break"

    eleza copy(self,event):
        ikiwa not self.text.tag_ranges("sel"):
            # There is no selection, so do nothing and maybe interrupt.
            rudisha None
        self.text.event_generate("<<Copy>>")
        rudisha "break"

    eleza paste(self,event):
        self.text.event_generate("<<Paste>>")
        self.text.see("insert")
        rudisha "break"

    eleza select_all(self, event=None):
        self.text.tag_add("sel", "1.0", "end-1c")
        self.text.mark_set("insert", "1.0")
        self.text.see("insert")
        rudisha "break"

    eleza remove_selection(self, event=None):
        self.text.tag_remove("sel", "1.0", "end")
        self.text.see("insert")
        rudisha "break"

    eleza move_at_edge_if_selection(self, edge_index):
        """Cursor move begins at start or end of selection

        When a left/right cursor key is pressed create and rudisha to Tkinter a
        function which causes a cursor move kutoka the associated edge of the
        selection.

        """
        self_text_index = self.text.index
        self_text_mark_set = self.text.mark_set
        edges_table = ("sel.first+1c", "sel.last-1c")
        eleza move_at_edge(event):
            ikiwa (event.state & 5) == 0: # no shift(==1) or control(==4) pressed
                try:
                    self_text_index("sel.first")
                    self_text_mark_set("insert", edges_table[edge_index])
                except TclError:
                    pass
        rudisha move_at_edge

    eleza del_word_left(self, event):
        self.text.event_generate('<Meta-Delete>')
        rudisha "break"

    eleza del_word_right(self, event):
        self.text.event_generate('<Meta-d>')
        rudisha "break"

    eleza find_event(self, event):
        search.find(self.text)
        rudisha "break"

    eleza find_again_event(self, event):
        search.find_again(self.text)
        rudisha "break"

    eleza find_selection_event(self, event):
        search.find_selection(self.text)
        rudisha "break"

    eleza find_in_files_event(self, event):
        grep.grep(self.text, self.io, self.flist)
        rudisha "break"

    eleza replace_event(self, event):
        replace.replace(self.text)
        rudisha "break"

    eleza goto_line_event(self, event):
        text = self.text
        lineno = tkSimpleDialog.askinteger("Goto",
                "Go to line number:",parent=text)
        ikiwa lineno is None:
            rudisha "break"
        ikiwa lineno <= 0:
            text.bell()
            rudisha "break"
        text.mark_set("insert", "%d.0" % lineno)
        text.see("insert")
        rudisha "break"

    eleza open_module(self):
        """Get module name kutoka user and open it.

        Return module path or None for calls by open_module_browser
        when latter is not invoked in named editor window.
        """
        # XXX This, open_module_browser, and open_path_browser
        # would fit better in iomenu.IOBinding.
        try:
            name = self.text.get("sel.first", "sel.last").strip()
        except TclError:
            name = ''
        file_path = query.ModuleName(
                self.text, "Open Module",
                "Enter the name of a Python module\n"
                "to search on sys.path and open:",
                name).result
        ikiwa file_path is not None:
            ikiwa self.flist:
                self.flist.open(file_path)
            else:
                self.io.loadfile(file_path)
        rudisha file_path

    eleza open_module_event(self, event):
        self.open_module()
        rudisha "break"

    eleza open_module_browser(self, event=None):
        filename = self.io.filename
        ikiwa not (self.__class__.__name__ == 'PyShellEditorWindow'
                and filename):
            filename = self.open_module()
            ikiwa filename is None:
                rudisha "break"
        kutoka idlelib agiza browser
        browser.ModuleBrowser(self.root, filename)
        rudisha "break"

    eleza open_path_browser(self, event=None):
        kutoka idlelib agiza pathbrowser
        pathbrowser.PathBrowser(self.root)
        rudisha "break"

    eleza open_turtle_demo(self, event = None):
        agiza subprocess

        cmd = [sys.executable,
               '-c',
               'kutoka turtledemo.__main__ agiza main; main()']
        subprocess.Popen(cmd, shell=False)
        rudisha "break"

    eleza gotoline(self, lineno):
        ikiwa lineno is not None and lineno > 0:
            self.text.mark_set("insert", "%d.0" % lineno)
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", "insert", "insert +1l")
            self.center()

    eleza ispythonsource(self, filename):
        ikiwa not filename or os.path.isdir(filename):
            rudisha True
        base, ext = os.path.splitext(os.path.basename(filename))
        ikiwa os.path.normcase(ext) in (".py", ".pyw"):
            rudisha True
        line = self.text.get('1.0', '1.0 lineend')
        rudisha line.startswith('#!') and 'python' in line

    eleza close_hook(self):
        ikiwa self.flist:
            self.flist.unregister_maybe_terminate(self)
            self.flist = None

    eleza set_close_hook(self, close_hook):
        self.close_hook = close_hook

    eleza filename_change_hook(self):
        ikiwa self.flist:
            self.flist.filename_changed_edit(self)
        self.saved_change_hook()
        self.top.update_windowlist_registry(self)
        self.ResetColorizer()

    eleza _addcolorizer(self):
        ikiwa self.color:
            return
        ikiwa self.ispythonsource(self.io.filename):
            self.color = self.ColorDelegator()
        # can add more colorizers here...
        ikiwa self.color:
            self.per.removefilter(self.undo)
            self.per.insertfilter(self.color)
            self.per.insertfilter(self.undo)

    eleza _rmcolorizer(self):
        ikiwa not self.color:
            return
        self.color.removecolors()
        self.per.removefilter(self.color)
        self.color = None

    eleza ResetColorizer(self):
        "Update the color theme"
        # Called kutoka self.filename_change_hook and kutoka configdialog.py
        self._rmcolorizer()
        self._addcolorizer()
        EditorWindow.color_config(self.text)

        ikiwa self.code_context is not None:
            self.code_context.update_highlight_colors()

        ikiwa self.line_numbers is not None:
            self.line_numbers.update_colors()

    IDENTCHARS = string.ascii_letters + string.digits + "_"

    eleza colorize_syntax_error(self, text, pos):
        text.tag_add("ERROR", pos)
        char = text.get(pos)
        ikiwa char and char in self.IDENTCHARS:
            text.tag_add("ERROR", pos + " wordstart", pos)
        ikiwa '\n' == text.get(pos):   # error at line end
            text.mark_set("insert", pos)
        else:
            text.mark_set("insert", pos + "+1c")
        text.see(pos)

    eleza ResetFont(self):
        "Update the text widgets' font ikiwa it is changed"
        # Called kutoka configdialog.py

        # Update the code context widget first, since its height affects
        # the height of the text widget.  This avoids double re-rendering.
        ikiwa self.code_context is not None:
            self.code_context.update_font()
        # Next, update the line numbers widget, since its width affects
        # the width of the text widget.
        ikiwa self.line_numbers is not None:
            self.line_numbers.update_font()
        # Finally, update the main text widget.
        new_font = idleConf.GetFont(self.root, 'main', 'EditorWindow')
        self.text['font'] = new_font
        self.set_width()

    eleza RemoveKeybindings(self):
        "Remove the keybindings before they are changed."
        # Called kutoka configdialog.py
        self.mainmenu.default_keydefs = keydefs = idleConf.GetCurrentKeySet()
        for event, keylist in keydefs.items():
            self.text.event_delete(event, *keylist)
        for extensionName in self.get_standard_extension_names():
            xkeydefs = idleConf.GetExtensionBindings(extensionName)
            ikiwa xkeydefs:
                for event, keylist in xkeydefs.items():
                    self.text.event_delete(event, *keylist)

    eleza ApplyKeybindings(self):
        "Update the keybindings after they are changed"
        # Called kutoka configdialog.py
        self.mainmenu.default_keydefs = keydefs = idleConf.GetCurrentKeySet()
        self.apply_bindings()
        for extensionName in self.get_standard_extension_names():
            xkeydefs = idleConf.GetExtensionBindings(extensionName)
            ikiwa xkeydefs:
                self.apply_bindings(xkeydefs)
        #update menu accelerators
        menuEventDict = {}
        for menu in self.mainmenu.menudefs:
            menuEventDict[menu[0]] = {}
            for item in menu[1]:
                ikiwa item:
                    menuEventDict[menu[0]][prepstr(item[0])[1]] = item[1]
        for menubarItem in self.menudict:
            menu = self.menudict[menubarItem]
            end = menu.index(END)
            ikiwa end is None:
                # Skip empty menus
                continue
            end += 1
            for index in range(0, end):
                ikiwa menu.type(index) == 'command':
                    accel = menu.entrycget(index, 'accelerator')
                    ikiwa accel:
                        itemName = menu.entrycget(index, 'label')
                        event = ''
                        ikiwa menubarItem in menuEventDict:
                            ikiwa itemName in menuEventDict[menubarItem]:
                                event = menuEventDict[menubarItem][itemName]
                        ikiwa event:
                            accel = get_accelerator(keydefs, event)
                            menu.entryconfig(index, accelerator=accel)

    eleza set_notabs_indentwidth(self):
        "Update the indentwidth ikiwa changed and not using tabs in this window"
        # Called kutoka configdialog.py
        ikiwa not self.usetabs:
            self.indentwidth = idleConf.GetOption('main', 'Indent','num-spaces',
                                                  type='int')

    eleza reset_help_menu_entries(self):
        "Update the additional help entries on the Help menu"
        help_list = idleConf.GetAllExtraHelpSourcesList()
        helpmenu = self.menudict['help']
        # first delete the extra help entries, ikiwa any
        helpmenu_length = helpmenu.index(END)
        ikiwa helpmenu_length > self.base_helpmenu_length:
            helpmenu.delete((self.base_helpmenu_length + 1), helpmenu_length)
        # then rebuild them
        ikiwa help_list:
            helpmenu.add_separator()
            for entry in help_list:
                cmd = self.__extra_help_callback(entry[1])
                helpmenu.add_command(label=entry[0], command=cmd)
        # and update the menu dictionary
        self.menudict['help'] = helpmenu

    eleza __extra_help_callback(self, helpfile):
        "Create a callback with the helpfile value frozen at definition time"
        eleza display_extra_help(helpfile=helpfile):
            ikiwa not helpfile.startswith(('www', 'http')):
                helpfile = os.path.normpath(helpfile)
            ikiwa sys.platform[:3] == 'win':
                try:
                    os.startfile(helpfile)
                except OSError as why:
                    tkMessageBox.showerror(title='Document Start Failure',
                        message=str(why), parent=self.text)
            else:
                webbrowser.open(helpfile)
        rudisha display_extra_help

    eleza update_recent_files_list(self, new_file=None):
        "Load and update the recent files list and menus"
        # TODO: move to iomenu.
        rf_list = []
        file_path = self.recent_files_path
        ikiwa file_path and os.path.exists(file_path):
            with open(file_path, 'r',
                      encoding='utf_8', errors='replace') as rf_list_file:
                rf_list = rf_list_file.readlines()
        ikiwa new_file:
            new_file = os.path.abspath(new_file) + '\n'
            ikiwa new_file in rf_list:
                rf_list.remove(new_file)  # move to top
            rf_list.insert(0, new_file)
        # clean and save the recent files list
        bad_paths = []
        for path in rf_list:
            ikiwa '\0' in path or not os.path.exists(path[0:-1]):
                bad_paths.append(path)
        rf_list = [path for path in rf_list ikiwa path not in bad_paths]
        ulchars = "1234567890ABCDEFGHIJK"
        rf_list = rf_list[0:len(ulchars)]
        ikiwa file_path:
            try:
                with open(file_path, 'w',
                          encoding='utf_8', errors='replace') as rf_file:
                    rf_file.writelines(rf_list)
            except OSError as err:
                ikiwa not getattr(self.root, "recentfiles_message", False):
                    self.root.recentfiles_message = True
                    tkMessageBox.showwarning(title='IDLE Warning',
                        message="Cannot save Recent Files list to disk.\n"
                                f"  {err}\n"
                                "Select OK to continue.",
                        parent=self.text)
        # for each edit window instance, construct the recent files menu
        for instance in self.top.instance_dict:
            menu = instance.recent_files_menu
            menu.delete(0, END)  # clear, and rebuild:
            for i, file_name in enumerate(rf_list):
                file_name = file_name.rstrip()  # zap \n
                callback = instance.__recent_file_callback(file_name)
                menu.add_command(label=ulchars[i] + " " + file_name,
                                 command=callback,
                                 underline=0)

    eleza __recent_file_callback(self, file_name):
        eleza open_recent_file(fn_closure=file_name):
            self.io.open(editFile=fn_closure)
        rudisha open_recent_file

    eleza saved_change_hook(self):
        short = self.short_title()
        long = self.long_title()
        ikiwa short and long:
            title = short + " - " + long + _py_version
        elikiwa short:
            title = short
        elikiwa long:
            title = long
        else:
            title = "untitled"
        icon = short or long or title
        ikiwa not self.get_saved():
            title = "*%s*" % title
            icon = "*%s" % icon
        self.top.wm_title(title)
        self.top.wm_iconname(icon)

    eleza get_saved(self):
        rudisha self.undo.get_saved()

    eleza set_saved(self, flag):
        self.undo.set_saved(flag)

    eleza reset_undo(self):
        self.undo.reset_undo()

    eleza short_title(self):
        filename = self.io.filename
        rudisha os.path.basename(filename) ikiwa filename else "untitled"

    eleza long_title(self):
        rudisha self.io.filename or ""

    eleza center_insert_event(self, event):
        self.center()
        rudisha "break"

    eleza center(self, mark="insert"):
        text = self.text
        top, bot = self.getwindowlines()
        lineno = self.getlineno(mark)
        height = bot - top
        newtop = max(1, lineno - height//2)
        text.yview(float(newtop))

    eleza getwindowlines(self):
        text = self.text
        top = self.getlineno("@0,0")
        bot = self.getlineno("@0,65535")
        ikiwa top == bot and text.winfo_height() == 1:
            # Geometry manager hasn't run yet
            height = int(text['height'])
            bot = top + height - 1
        rudisha top, bot

    eleza getlineno(self, mark="insert"):
        text = self.text
        rudisha int(float(text.index(mark)))

    eleza get_geometry(self):
        "Return (width, height, x, y)"
        geom = self.top.wm_geometry()
        m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geom)
        rudisha list(map(int, m.groups()))

    eleza close_event(self, event):
        self.close()
        rudisha "break"

    eleza maybesave(self):
        ikiwa self.io:
            ikiwa not self.get_saved():
                ikiwa self.top.state()!='normal':
                    self.top.deiconify()
                self.top.lower()
                self.top.lift()
            rudisha self.io.maybesave()

    eleza close(self):
        try:
            reply = self.maybesave()
            ikiwa str(reply) != "cancel":
                self._close()
            rudisha reply
        except AttributeError:  # bpo-35379: close called twice
            pass

    eleza _close(self):
        ikiwa self.io.filename:
            self.update_recent_files_list(new_file=self.io.filename)
        window.unregister_callback(self.postwindowsmenu)
        self.unload_extensions()
        self.io.close()
        self.io = None
        self.undo = None
        ikiwa self.color:
            self.color.close()
            self.color = None
        self.text = None
        self.tkinter_vars = None
        self.per.close()
        self.per = None
        self.top.destroy()
        ikiwa self.close_hook:
            # unless override: unregister kutoka flist, terminate ikiwa last window
            self.close_hook()

    eleza load_extensions(self):
        self.extensions = {}
        self.load_standard_extensions()

    eleza unload_extensions(self):
        for ins in list(self.extensions.values()):
            ikiwa hasattr(ins, "close"):
                ins.close()
        self.extensions = {}

    eleza load_standard_extensions(self):
        for name in self.get_standard_extension_names():
            try:
                self.load_extension(name)
            except:
                andika("Failed to load extension", repr(name))
                traceback.print_exc()

    eleza get_standard_extension_names(self):
        rudisha idleConf.GetExtensions(editor_only=True)

    extfiles = {  # Map built-in config-extension section names to file names.
        'ZzDummy': 'zzdummy',
        }

    eleza load_extension(self, name):
        fname = self.extfiles.get(name, name)
        try:
            try:
                mod = importlib.import_module('.' + fname, package=__package__)
            except (ImportError, TypeError):
                mod = importlib.import_module(fname)
        except ImportError:
            andika("\nFailed to agiza extension: ", name)
            raise
        cls = getattr(mod, name)
        keydefs = idleConf.GetExtensionBindings(name)
        ikiwa hasattr(cls, "menudefs"):
            self.fill_menus(cls.menudefs, keydefs)
        ins = cls(self)
        self.extensions[name] = ins
        ikiwa keydefs:
            self.apply_bindings(keydefs)
            for vevent in keydefs:
                methodname = vevent.replace("-", "_")
                while methodname[:1] == '<':
                    methodname = methodname[1:]
                while methodname[-1:] == '>':
                    methodname = methodname[:-1]
                methodname = methodname + "_event"
                ikiwa hasattr(ins, methodname):
                    self.text.bind(vevent, getattr(ins, methodname))

    eleza apply_bindings(self, keydefs=None):
        ikiwa keydefs is None:
            keydefs = self.mainmenu.default_keydefs
        text = self.text
        text.keydefs = keydefs
        for event, keylist in keydefs.items():
            ikiwa keylist:
                text.event_add(event, *keylist)

    eleza fill_menus(self, menudefs=None, keydefs=None):
        """Add appropriate entries to the menus and submenus

        Menus that are absent or None in self.menudict are ignored.
        """
        ikiwa menudefs is None:
            menudefs = self.mainmenu.menudefs
        ikiwa keydefs is None:
            keydefs = self.mainmenu.default_keydefs
        menudict = self.menudict
        text = self.text
        for mname, entrylist in menudefs:
            menu = menudict.get(mname)
            ikiwa not menu:
                continue
            for entry in entrylist:
                ikiwa not entry:
                    menu.add_separator()
                else:
                    label, eventname = entry
                    checkbutton = (label[:1] == '!')
                    ikiwa checkbutton:
                        label = label[1:]
                    underline, label = prepstr(label)
                    accelerator = get_accelerator(keydefs, eventname)
                    eleza command(text=text, eventname=eventname):
                        text.event_generate(eventname)
                    ikiwa checkbutton:
                        var = self.get_var_obj(eventname, BooleanVar)
                        menu.add_checkbutton(label=label, underline=underline,
                            command=command, accelerator=accelerator,
                            variable=var)
                    else:
                        menu.add_command(label=label, underline=underline,
                                         command=command,
                                         accelerator=accelerator)

    eleza getvar(self, name):
        var = self.get_var_obj(name)
        ikiwa var:
            value = var.get()
            rudisha value
        else:
            raise NameError(name)

    eleza setvar(self, name, value, vartype=None):
        var = self.get_var_obj(name, vartype)
        ikiwa var:
            var.set(value)
        else:
            raise NameError(name)

    eleza get_var_obj(self, name, vartype=None):
        var = self.tkinter_vars.get(name)
        ikiwa not var and vartype:
            # create a Tkinter variable object with self.text as master:
            self.tkinter_vars[name] = var = vartype(self.text)
        rudisha var

    # Tk implementations of "virtual text methods" -- each platform
    # reusing IDLE's support code needs to define these for its GUI's
    # flavor of widget.

    # Is character at text_index in a Python string?  Return 0 for
    # "guaranteed no", true for anything else.  This info is expensive
    # to compute ab initio, but is probably already known by the
    # platform's colorizer.

    eleza is_char_in_string(self, text_index):
        ikiwa self.color:
            # Return true iff colorizer hasn't (re)gotten this far
            # yet, or the character is tagged as being in a string
            rudisha self.text.tag_prevrange("TODO", text_index) or \
                   "STRING" in self.text.tag_names(text_index)
        else:
            # The colorizer is missing: assume the worst
            rudisha 1

    # If a selection is defined in the text widget, rudisha (start,
    # end) as Tkinter text indices, otherwise rudisha (None, None)
    eleza get_selection_indices(self):
        try:
            first = self.text.index("sel.first")
            last = self.text.index("sel.last")
            rudisha first, last
        except TclError:
            rudisha None, None

    # Return the text widget's current view of what a tab stop means
    # (equivalent width in spaces).

    eleza get_tk_tabwidth(self):
        current = self.text['tabs'] or TK_TABWIDTH_DEFAULT
        rudisha int(current)

    # Set the text widget's current view of what a tab stop means.

    eleza set_tk_tabwidth(self, newtabwidth):
        text = self.text
        ikiwa self.get_tk_tabwidth() != newtabwidth:
            # Set text widget tab width
            pixels = text.tk.call("font", "measure", text["font"],
                                  "-displayof", text.master,
                                  "n" * newtabwidth)
            text.configure(tabs=pixels)

### begin autoindent code ###  (configuration was moved to beginning of class)

    eleza set_indentation_params(self, is_py_src, guess=True):
        ikiwa is_py_src and guess:
            i = self.guess_indent()
            ikiwa 2 <= i <= 8:
                self.indentwidth = i
            ikiwa self.indentwidth != self.tabwidth:
                self.usetabs = False
        self.set_tk_tabwidth(self.tabwidth)

    eleza smart_backspace_event(self, event):
        text = self.text
        first, last = self.get_selection_indices()
        ikiwa first and last:
            text.delete(first, last)
            text.mark_set("insert", first)
            rudisha "break"
        # Delete whitespace left, until hitting a real char or closest
        # preceding virtual tab stop.
        chars = text.get("insert linestart", "insert")
        ikiwa chars == '':
            ikiwa text.compare("insert", ">", "1.0"):
                # easy: delete preceding newline
                text.delete("insert-1c")
            else:
                text.bell()     # at start of buffer
            rudisha "break"
        ikiwa  chars[-1] not in " \t":
            # easy: delete preceding real char
            text.delete("insert-1c")
            rudisha "break"
        # Ick.  It may require *inserting* spaces ikiwa we back up over a
        # tab character!  This is written to be clear, not fast.
        tabwidth = self.tabwidth
        have = len(chars.expandtabs(tabwidth))
        assert have > 0
        want = ((have - 1) // self.indentwidth) * self.indentwidth
        # Debug prompt is multilined....
        ncharsdeleted = 0
        while 1:
            ikiwa chars == self.prompt_last_line:  # '' unless PyShell
                break
            chars = chars[:-1]
            ncharsdeleted = ncharsdeleted + 1
            have = len(chars.expandtabs(tabwidth))
            ikiwa have <= want or chars[-1] not in " \t":
                break
        text.undo_block_start()
        text.delete("insert-%dc" % ncharsdeleted, "insert")
        ikiwa have < want:
            text.insert("insert", ' ' * (want - have))
        text.undo_block_stop()
        rudisha "break"

    eleza smart_indent_event(self, event):
        # ikiwa intraline selection:
        #     delete it
        # elikiwa multiline selection:
        #     do indent-region
        # else:
        #     indent one level
        text = self.text
        first, last = self.get_selection_indices()
        text.undo_block_start()
        try:
            ikiwa first and last:
                ikiwa index2line(first) != index2line(last):
                    rudisha self.fregion.indent_region_event(event)
                text.delete(first, last)
                text.mark_set("insert", first)
            prefix = text.get("insert linestart", "insert")
            raw, effective = get_line_indent(prefix, self.tabwidth)
            ikiwa raw == len(prefix):
                # only whitespace to the left
                self.reindent_to(effective + self.indentwidth)
            else:
                # tab to the next 'stop' within or to right of line's text:
                ikiwa self.usetabs:
                    pad = '\t'
                else:
                    effective = len(prefix.expandtabs(self.tabwidth))
                    n = self.indentwidth
                    pad = ' ' * (n - effective % n)
                text.insert("insert", pad)
            text.see("insert")
            rudisha "break"
        finally:
            text.undo_block_stop()

    eleza newline_and_indent_event(self, event):
        text = self.text
        first, last = self.get_selection_indices()
        text.undo_block_start()
        try:
            ikiwa first and last:
                text.delete(first, last)
                text.mark_set("insert", first)
            line = text.get("insert linestart", "insert")
            i, n = 0, len(line)
            while i < n and line[i] in " \t":
                i = i+1
            ikiwa i == n:
                # the cursor is in or at leading indentation in a continuation
                # line; just inject an empty line at the start
                text.insert("insert linestart", '\n')
                rudisha "break"
            indent = line[:i]
            # strip whitespace before insert point unless it's in the prompt
            i = 0
            while line and line[-1] in " \t" and line != self.prompt_last_line:
                line = line[:-1]
                i = i+1
            ikiwa i:
                text.delete("insert - %d chars" % i, "insert")
            # strip whitespace after insert point
            while text.get("insert") in " \t":
                text.delete("insert")
            # start new line
            text.insert("insert", '\n')

            # adjust indentation for continuations and block
            # open/close first need to find the last stmt
            lno = index2line(text.index('insert'))
            y = pyparse.Parser(self.indentwidth, self.tabwidth)
            ikiwa not self.prompt_last_line:
                for context in self.num_context_lines:
                    startat = max(lno - context, 1)
                    startatindex = repr(startat) + ".0"
                    rawtext = text.get(startatindex, "insert")
                    y.set_code(rawtext)
                    bod = y.find_good_parse_start(
                              self._build_char_in_string_func(startatindex))
                    ikiwa bod is not None or startat == 1:
                        break
                y.set_lo(bod or 0)
            else:
                r = text.tag_prevrange("console", "insert")
                ikiwa r:
                    startatindex = r[1]
                else:
                    startatindex = "1.0"
                rawtext = text.get(startatindex, "insert")
                y.set_code(rawtext)
                y.set_lo(0)

            c = y.get_continuation_type()
            ikiwa c != pyparse.C_NONE:
                # The current stmt hasn't ended yet.
                ikiwa c == pyparse.C_STRING_FIRST_LINE:
                    # after the first line of a string; do not indent at all
                    pass
                elikiwa c == pyparse.C_STRING_NEXT_LINES:
                    # inside a string which started before this line;
                    # just mimic the current indent
                    text.insert("insert", indent)
                elikiwa c == pyparse.C_BRACKET:
                    # line up with the first (ikiwa any) element of the
                    # last open bracket structure; else indent one
                    # level beyond the indent of the line with the
                    # last open bracket
                    self.reindent_to(y.compute_bracket_indent())
                elikiwa c == pyparse.C_BACKSLASH:
                    # ikiwa more than one line in this stmt already, just
                    # mimic the current indent; else ikiwa initial line
                    # has a start on an assignment stmt, indent to
                    # beyond leftmost =; else to beyond first chunk of
                    # non-whitespace on initial line
                    ikiwa y.get_num_lines_in_stmt() > 1:
                        text.insert("insert", indent)
                    else:
                        self.reindent_to(y.compute_backslash_indent())
                else:
                    assert 0, "bogus continuation type %r" % (c,)
                rudisha "break"

            # This line starts a brand new stmt; indent relative to
            # indentation of initial line of closest preceding
            # interesting stmt.
            indent = y.get_base_indent_string()
            text.insert("insert", indent)
            ikiwa y.is_block_opener():
                self.smart_indent_event(event)
            elikiwa indent and y.is_block_closer():
                self.smart_backspace_event(event)
            rudisha "break"
        finally:
            text.see("insert")
            text.undo_block_stop()

    # Our editwin provides an is_char_in_string function that works
    # with a Tk text index, but PyParse only knows about offsets into
    # a string. This builds a function for PyParse that accepts an
    # offset.

    eleza _build_char_in_string_func(self, startindex):
        eleza inner(offset, _startindex=startindex,
                  _icis=self.is_char_in_string):
            rudisha _icis(_startindex + "+%dc" % offset)
        rudisha inner

    # XXX this isn't bound to anything -- see tabwidth comments
##     eleza change_tabwidth_event(self, event):
##         new = self._asktabwidth()
##         ikiwa new != self.tabwidth:
##             self.tabwidth = new
##             self.set_indentation_params(0, guess=0)
##         rudisha "break"

    # Make string that displays as n leading blanks.

    eleza _make_blanks(self, n):
        ikiwa self.usetabs:
            ntabs, nspaces = divmod(n, self.tabwidth)
            rudisha '\t' * ntabs + ' ' * nspaces
        else:
            rudisha ' ' * n

    # Delete kutoka beginning of line to insert point, then reinsert
    # column logical (meaning use tabs ikiwa appropriate) spaces.

    eleza reindent_to(self, column):
        text = self.text
        text.undo_block_start()
        ikiwa text.compare("insert linestart", "!=", "insert"):
            text.delete("insert linestart", "insert")
        ikiwa column:
            text.insert("insert", self._make_blanks(column))
        text.undo_block_stop()

    # Guess indentwidth kutoka text content.
    # Return guessed indentwidth.  This should not be believed unless
    # it's in a reasonable range (e.g., it will be 0 ikiwa no indented
    # blocks are found).

    eleza guess_indent(self):
        opener, indented = IndentSearcher(self.text, self.tabwidth).run()
        ikiwa opener and indented:
            raw, indentsmall = get_line_indent(opener, self.tabwidth)
            raw, indentlarge = get_line_indent(indented, self.tabwidth)
        else:
            indentsmall = indentlarge = 0
        rudisha indentlarge - indentsmall

    eleza toggle_line_numbers_event(self, event=None):
        ikiwa self.line_numbers is None:
            return

        ikiwa self.line_numbers.is_shown:
            self.line_numbers.hide_sidebar()
            menu_label = "Show"
        else:
            self.line_numbers.show_sidebar()
            menu_label = "Hide"
        self.update_menu_label(menu='options', index='*Line Numbers',
                               label=f'{menu_label} Line Numbers')

# "line.col" -> line, as an int
eleza index2line(index):
    rudisha int(float(index))


_line_indent_re = re.compile(r'[ \t]*')
eleza get_line_indent(line, tabwidth):
    """Return a line's indentation as (# chars, effective # of spaces).

    The effective # of spaces is the length after properly "expanding"
    the tabs into spaces, as done by str.expandtabs(tabwidth).
    """
    m = _line_indent_re.match(line)
    rudisha m.end(), len(m.group().expandtabs(tabwidth))


kundi IndentSearcher(object):

    # .run() chews over the Text widget, looking for a block opener
    # and the stmt following it.  Returns a pair,
    #     (line containing block opener, line containing stmt)
    # Either or both may be None.

    eleza __init__(self, text, tabwidth):
        self.text = text
        self.tabwidth = tabwidth
        self.i = self.finished = 0
        self.blkopenline = self.indentedline = None

    eleza readline(self):
        ikiwa self.finished:
            rudisha ""
        i = self.i = self.i + 1
        mark = repr(i) + ".0"
        ikiwa self.text.compare(mark, ">=", "end"):
            rudisha ""
        rudisha self.text.get(mark, mark + " lineend+1c")

    eleza tokeneater(self, type, token, start, end, line,
                   INDENT=tokenize.INDENT,
                   NAME=tokenize.NAME,
                   OPENERS=('class', 'def', 'for', 'if', 'try', 'while')):
        ikiwa self.finished:
            pass
        elikiwa type == NAME and token in OPENERS:
            self.blkopenline = line
        elikiwa type == INDENT and self.blkopenline:
            self.indentedline = line
            self.finished = 1

    eleza run(self):
        save_tabsize = tokenize.tabsize
        tokenize.tabsize = self.tabwidth
        try:
            try:
                tokens = tokenize.generate_tokens(self.readline)
                for token in tokens:
                    self.tokeneater(*token)
            except (tokenize.TokenError, SyntaxError):
                # since we cut off the tokenizer early, we can trigger
                # spurious errors
                pass
        finally:
            tokenize.tabsize = save_tabsize
        rudisha self.blkopenline, self.indentedline

### end autoindent code ###

eleza prepstr(s):
    # Helper to extract the underscore kutoka a string, e.g.
    # prepstr("Co_py") returns (2, "Copy").
    i = s.find('_')
    ikiwa i >= 0:
        s = s[:i] + s[i+1:]
    rudisha i, s


keynames = {
 'bracketleft': '[',
 'bracketright': ']',
 'slash': '/',
}

eleza get_accelerator(keydefs, eventname):
    keylist = keydefs.get(eventname)
    # issue10940: temporary workaround to prevent hang with OS X Cocoa Tk 8.5
    # ikiwa not keylist:
    ikiwa (not keylist) or (macosx.isCocoaTk() and eventname in {
                            "<<open-module>>",
                            "<<goto-line>>",
                            "<<change-indentwidth>>"}):
        rudisha ""
    s = keylist[0]
    s = re.sub(r"-[a-z]\b", lambda m: m.group().upper(), s)
    s = re.sub(r"\b\w+\b", lambda m: keynames.get(m.group(), m.group()), s)
    s = re.sub("Key-", "", s)
    s = re.sub("Cancel","Ctrl-Break",s)   # dscherer@cmu.edu
    s = re.sub("Control-", "Ctrl-", s)
    s = re.sub("-", "+", s)
    s = re.sub("><", " ", s)
    s = re.sub("<", "", s)
    s = re.sub(">", "", s)
    rudisha s


eleza fixwordbreaks(root):
    # On Windows, tcl/tk breaks 'words' only on spaces, as in Command Prompt.
    # We want Motikiwa style everywhere. See #21474, msg218992 and followup.
    tk = root.tk
    tk.call('tcl_wordBreakAfter', 'a b', 0) # make sure word.tcl is loaded
    tk.call('set', 'tcl_wordchars', r'\w')
    tk.call('set', 'tcl_nonwordchars', r'\W')


eleza _editor_window(parent):  # htest #
    # error ikiwa close master window first - timer event, after script
    root = parent
    fixwordbreaks(root)
    ikiwa sys.argv[1:]:
        filename = sys.argv[1]
    else:
        filename = None
    macosx.setupApp(root, None)
    edit = EditorWindow(root=root, filename=filename)
    text = edit.text
    text['height'] = 10
    for i in range(20):
        text.insert('insert', '  '*i + str(i) + '\n')
    # text.bind("<<close-all-windows>>", edit.close_event)
    # Does not stop error, neither does following
    # edit.text.bind("<<close-window>>", edit.close_event)

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_editor', verbosity=2, exit=False)

    kutoka idlelib.idle_test.htest agiza run
    run(_editor_window)
