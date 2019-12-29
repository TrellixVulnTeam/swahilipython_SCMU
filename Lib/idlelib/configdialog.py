"""IDLE Configuration Dialog: support user customization of IDLE by GUI

Customize font faces, sizes, na colorization attributes.  Set indentation
defaults.  Customize keybindings.  Colorization na keybindings can be
saved kama user defined sets.  Select startup options including shell/editor
and default window size.  Define additional help sources.

Note that tab width kwenye IDLE ni currently fixed at eight due to Tk issues.
Refer to comments kwenye EditorWindow autoindent code kila details.

"""
agiza re

kutoka tkinter agiza (Toplevel, Listbox, Text, Scale, Canvas,
                     StringVar, BooleanVar, IntVar, TRUE, FALSE,
                     TOP, BOTTOM, RIGHT, LEFT, SOLID, GROOVE,
                     NONE, BOTH, X, Y, W, E, EW, NS, NSEW, NW,
                     HORIZONTAL, VERTICAL, ANCHOR, ACTIVE, END)
kutoka tkinter.ttk agiza (Frame, LabelFrame, Button, Checkbutton, Entry, Label,
                         OptionMenu, Notebook, Radiobutton, Scrollbar, Style)
agiza tkinter.colorchooser kama tkColorChooser
agiza tkinter.font kama tkFont
kutoka tkinter agiza messagebox

kutoka idlelib.config agiza idleConf, ConfigChanges
kutoka idlelib.config_key agiza GetKeysDialog
kutoka idlelib.dynoption agiza DynOptionMenu
kutoka idlelib agiza macosx
kutoka idlelib.query agiza SectionName, HelpSource
kutoka idlelib.textview agiza view_text
kutoka idlelib.autocomplete agiza AutoComplete
kutoka idlelib.codecontext agiza CodeContext
kutoka idlelib.parenmatch agiza ParenMatch
kutoka idlelib.format agiza FormatParagraph
kutoka idlelib.squeezer agiza Squeezer
kutoka idlelib.textview agiza ScrollableTextFrame

changes = ConfigChanges()
# Reload changed options kwenye the following classes.
reloadables = (AutoComplete, CodeContext, ParenMatch, FormatParagraph,
               Squeezer)


kundi ConfigDialog(Toplevel):
    """Config dialog kila IDLE.
    """

    eleza __init__(self, parent, title='', *, _htest=Uongo, _utest=Uongo):
        """Show the tabbed dialog kila user configuration.

        Args:
            parent - parent of this dialog
            title - string which ni the title of this popup dialog
            _htest - bool, change box location when running htest
            _utest - bool, don't wait_window when running unittest

        Note: Focus set on font page fontlist.

        Methods:
            create_widgets
            cancel: Bound to DELETE_WINDOW protocol.
        """
        Toplevel.__init__(self, parent)
        self.parent = parent
        ikiwa _htest:
            parent.instance_dict = {}
        ikiwa sio _utest:
            self.withdraw()

        self.configure(borderwidth=5)
        self.title(title ama 'IDLE Preferences')
        x = parent.winfo_rootx() + 20
        y = parent.winfo_rooty() + (30 ikiwa sio _htest isipokua 150)
        self.geometry(f'+{x}+{y}')
        # Each theme element key ni its display name.
        # The first value of the tuple ni the sample area tag name.
        # The second value ni the display name list sort index.
        self.create_widgets()
        self.resizable(height=FALSE, width=FALSE)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.fontpage.fontlist.focus_set()
        # XXX Decide whether to keep ama delete these key bindings.
        # Key bindings kila this dialog.
        # self.bind('<Escape>', self.Cancel) #dismiss dialog, no save
        # self.bind('<Alt-a>', self.Apply) #apply changes, save
        # self.bind('<F1>', self.Help) #context help
        # Attach callbacks after loading config to avoid calling them.
        tracers.attach()

        ikiwa sio _utest:
            self.grab_set()
            self.wm_deiconify()
            self.wait_window()

    eleza create_widgets(self):
        """Create na place widgets kila tabbed dialog.

        Widgets Bound to self:
            note: Notebook
            highpage: HighPage
            fontpage: FontPage
            keyspage: KeysPage
            genpage: GenPage
            extpage: self.create_page_extensions

        Methods:
            create_action_buttons
            load_configs: Load pages tatizo kila extensions.
            activate_config_changes: Tell editors to reload.
        """
        self.note = note = Notebook(self)
        self.highpage = HighPage(note)
        self.fontpage = FontPage(note, self.highpage)
        self.keyspage = KeysPage(note)
        self.genpage = GenPage(note)
        self.extpage = self.create_page_extensions()
        note.add(self.fontpage, text='Fonts/Tabs')
        note.add(self.highpage, text='Highlights')
        note.add(self.keyspage, text=' Keys ')
        note.add(self.genpage, text=' General ')
        note.add(self.extpage, text='Extensions')
        note.enable_traversal()
        note.pack(side=TOP, expand=TRUE, fill=BOTH)
        self.create_action_buttons().pack(side=BOTTOM)

    eleza create_action_buttons(self):
        """Return frame of action buttons kila dialog.

        Methods:
            ok
            apply
            cancel
            help

        Widget Structure:
            outer: Frame
                buttons: Frame
                    (no assignment): Button (ok)
                    (no assignment): Button (apply)
                    (no assignment): Button (cancel)
                    (no assignment): Button (help)
                (no assignment): Frame
        """
        ikiwa macosx.isAquaTk():
            # Changing the default padding on OSX results kwenye unreadable
            # text kwenye the buttons.
            padding_args = {}
        isipokua:
            padding_args = {'padding': (6, 3)}
        outer = Frame(self, padding=2)
        buttons = Frame(outer, padding=2)
        kila txt, cmd kwenye (
            ('Ok', self.ok),
            ('Apply', self.apply),
            ('Cancel', self.cancel),
            ('Help', self.help)):
            Button(buttons, text=txt, command=cmd, takefocus=FALSE,
                   **padding_args).pack(side=LEFT, padx=5)
        # Add space above buttons.
        Frame(outer, height=2, borderwidth=0).pack(side=TOP)
        buttons.pack(side=BOTTOM)
        rudisha outer

    eleza ok(self):
        """Apply config changes, then dismiss dialog.

        Methods:
            apply
            destroy: inherited
        """
        self.apply()
        self.destroy()

    eleza apply(self):
        """Apply config changes na leave dialog open.

        Methods:
            deactivate_current_config
            save_all_changed_extensions
            activate_config_changes
        """
        self.deactivate_current_config()
        changes.save_all()
        self.save_all_changed_extensions()
        self.activate_config_changes()

    eleza cancel(self):
        """Dismiss config dialog.

        Methods:
            destroy: inherited
        """
        self.destroy()

    eleza destroy(self):
        global font_sample_text
        font_sample_text = self.fontpage.font_sample.get('1.0', 'end')
        self.grab_release()
        super().destroy()

    eleza help(self):
        """Create textview kila config dialog help.

        Attributes accessed:
            note

        Methods:
            view_text: Method kutoka textview module.
        """
        page = self.note.tab(self.note.select(), option='text').strip()
        view_text(self, title='Help kila IDLE preferences',
                 text=help_common+help_pages.get(page, ''))

    eleza deactivate_current_config(self):
        """Remove current key bindings.
        Iterate over window instances defined kwenye parent na remove
        the keybindings.
        """
        # Before a config ni saved, some cleanup of current
        # config must be done - remove the previous keybindings.
        win_instances = self.parent.instance_dict.keys()
        kila instance kwenye win_instances:
            instance.RemoveKeybindings()

    eleza activate_config_changes(self):
        """Apply configuration changes to current windows.

        Dynamically update the current parent window instances
        ukijumuisha some of the configuration changes.
        """
        win_instances = self.parent.instance_dict.keys()
        kila instance kwenye win_instances:
            instance.ResetColorizer()
            instance.ResetFont()
            instance.set_notabs_indentwidth()
            instance.ApplyKeybindings()
            instance.reset_help_menu_entries()
        kila klass kwenye reloadables:
            klass.reload()

    eleza create_page_extensions(self):
        """Part of the config dialog used kila configuring IDLE extensions.

        This code ni generic - it works kila any na all IDLE extensions.

        IDLE extensions save their configuration options using idleConf.
        This code reads the current configuration using idleConf, supplies a
        GUI interface to change the configuration values, na saves the
        changes using idleConf.

        Not all changes take effect immediately - some may require restarting IDLE.
        This depends on each extension's implementation.

        All values are treated kama text, na it ni up to the user to supply
        reasonable values. The only exception to this are the 'enable*' options,
        which are boolean, na can be toggled ukijumuisha a Kweli/Uongo button.

        Methods:
            load_extensions:
            extension_selected: Handle selection kutoka list.
            create_extension_frame: Hold widgets kila one extension.
            set_extension_value: Set kwenye userCfg['extensions'].
            save_all_changed_extensions: Call extension page Save().
        """
        parent = self.parent
        frame = Frame(self.note)
        self.ext_defaultCfg = idleConf.defaultCfg['extensions']
        self.ext_userCfg = idleConf.userCfg['extensions']
        self.is_int = self.register(is_int)
        self.load_extensions()
        # Create widgets - a listbox shows all available extensions, ukijumuisha the
        # controls kila the extension selected kwenye the listbox to the right.
        self.extension_names = StringVar(self)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(2, weight=1)
        self.extension_list = Listbox(frame, listvariable=self.extension_names,
                                      selectmode='browse')
        self.extension_list.bind('<<ListboxSelect>>', self.extension_selected)
        scroll = Scrollbar(frame, command=self.extension_list.yview)
        self.extension_list.yscrollcommand=scroll.set
        self.details_frame = LabelFrame(frame, width=250, height=250)
        self.extension_list.grid(column=0, row=0, sticky='nws')
        scroll.grid(column=1, row=0, sticky='ns')
        self.details_frame.grid(column=2, row=0, sticky='nsew', padx=[10, 0])
        frame.configure(padding=10)
        self.config_frame = {}
        self.current_extension = Tupu

        self.outerframe = self                      # TEMPORARY
        self.tabbed_page_set = self.extension_list  # TEMPORARY

        # Create the frame holding controls kila each extension.
        ext_names = ''
        kila ext_name kwenye sorted(self.extensions):
            self.create_extension_frame(ext_name)
            ext_names = ext_names + '{' + ext_name + '} '
        self.extension_names.set(ext_names)
        self.extension_list.selection_set(0)
        self.extension_selected(Tupu)

        rudisha frame

    eleza load_extensions(self):
        "Fill self.extensions ukijumuisha data kutoka the default na user configs."
        self.extensions = {}
        kila ext_name kwenye idleConf.GetExtensions(active_only=Uongo):
            # Former built-in extensions are already filtered out.
            self.extensions[ext_name] = []

        kila ext_name kwenye self.extensions:
            opt_list = sorted(self.ext_defaultCfg.GetOptionList(ext_name))

            # Bring 'enable' options to the beginning of the list.
            enables = [opt_name kila opt_name kwenye opt_list
                       ikiwa opt_name.startswith('enable')]
            kila opt_name kwenye enables:
                opt_list.remove(opt_name)
            opt_list = enables + opt_list

            kila opt_name kwenye opt_list:
                def_str = self.ext_defaultCfg.Get(
                        ext_name, opt_name, raw=Kweli)
                jaribu:
                    def_obj = {'Kweli':Kweli, 'Uongo':Uongo}[def_str]
                    opt_type = 'bool'
                tatizo KeyError:
                    jaribu:
                        def_obj = int(def_str)
                        opt_type = 'int'
                    tatizo ValueError:
                        def_obj = def_str
                        opt_type = Tupu
                jaribu:
                    value = self.ext_userCfg.Get(
                            ext_name, opt_name, type=opt_type, raw=Kweli,
                            default=def_obj)
                tatizo ValueError:  # Need this until .Get fixed.
                    value = def_obj  # Bad values overwritten by entry.
                var = StringVar(self)
                var.set(str(value))

                self.extensions[ext_name].append({'name': opt_name,
                                                  'type': opt_type,
                                                  'default': def_str,
                                                  'value': value,
                                                  'var': var,
                                                 })

    eleza extension_selected(self, event):
        "Handle selection of an extension kutoka the list."
        newsel = self.extension_list.curselection()
        ikiwa newsel:
            newsel = self.extension_list.get(newsel)
        ikiwa newsel ni Tupu ama newsel != self.current_extension:
            ikiwa self.current_extension:
                self.details_frame.config(text='')
                self.config_frame[self.current_extension].grid_forget()
                self.current_extension = Tupu
        ikiwa newsel:
            self.details_frame.config(text=newsel)
            self.config_frame[newsel].grid(column=0, row=0, sticky='nsew')
            self.current_extension = newsel

    eleza create_extension_frame(self, ext_name):
        """Create a frame holding the widgets to configure one extension"""
        f = VerticalScrolledFrame(self.details_frame, height=250, width=250)
        self.config_frame[ext_name] = f
        entry_area = f.interior
        # Create an entry kila each configuration option.
        kila row, opt kwenye enumerate(self.extensions[ext_name]):
            # Create a row ukijumuisha a label na entry/checkbutton.
            label = Label(entry_area, text=opt['name'])
            label.grid(row=row, column=0, sticky=NW)
            var = opt['var']
            ikiwa opt['type'] == 'bool':
                Checkbutton(entry_area, variable=var,
                            onvalue='Kweli', offvalue='Uongo', width=8
                            ).grid(row=row, column=1, sticky=W, padx=7)
            lasivyo opt['type'] == 'int':
                Entry(entry_area, textvariable=var, validate='key',
                      validatecommand=(self.is_int, '%P'), width=10
                      ).grid(row=row, column=1, sticky=NSEW, padx=7)

            isipokua:  # type == 'str'
                # Limit size to fit non-expanding space ukijumuisha larger font.
                Entry(entry_area, textvariable=var, width=15
                      ).grid(row=row, column=1, sticky=NSEW, padx=7)
        rudisha

    eleza set_extension_value(self, section, opt):
        """Return Kweli ikiwa the configuration was added ama changed.

        If the value ni the same kama the default, then remove it
        kutoka user config file.
        """
        name = opt['name']
        default = opt['default']
        value = opt['var'].get().strip() ama default
        opt['var'].set(value)
        # ikiwa self.defaultCfg.has_section(section):
        # Currently, always true; ikiwa not, indent to rudisha.
        ikiwa (value == default):
            rudisha self.ext_userCfg.RemoveOption(section, name)
        # Set the option.
        rudisha self.ext_userCfg.SetOption(section, name, value)

    eleza save_all_changed_extensions(self):
        """Save configuration changes to the user config file.

        Attributes accessed:
            extensions

        Methods:
            set_extension_value
        """
        has_changes = Uongo
        kila ext_name kwenye self.extensions:
            options = self.extensions[ext_name]
            kila opt kwenye options:
                ikiwa self.set_extension_value(ext_name, opt):
                    has_changes = Kweli
        ikiwa has_changes:
            self.ext_userCfg.Save()


# kundi TabPage(Frame):  # A template kila Page classes.
#     eleza __init__(self, master):
#         super().__init__(master)
#         self.create_page_tab()
#         self.load_tab_cfg()
#     eleza create_page_tab(self):
#         # Define tk vars na register var na callback ukijumuisha tracers.
#         # Create subframes na widgets.
#         # Pack widgets.
#     eleza load_tab_cfg(self):
#         # Initialize widgets ukijumuisha data kutoka idleConf.
#     eleza var_changed_var_name():
#         # For each tk var that needs other than default callback.
#     eleza other_methods():
#         # Define tab-specific behavior.

font_sample_text = (
    '<ASCII/Latin1>\n'
    'AaBbCcDdEeFfGgHhIiJj\n1234567890#:+=(){}[]\n'
    '\u00a2\u00a3\u00a5\u00a7\u00a9\u00ab\u00ae\u00b6\u00bd\u011e'
    '\u00c0\u00c1\u00c2\u00c3\u00c4\u00c5\u00c7\u00d0\u00d8\u00df\n'
    '\n<IPA,Greek,Cyrillic>\n'
    '\u0250\u0255\u0258\u025e\u025f\u0264\u026b\u026e\u0270\u0277'
    '\u027b\u0281\u0283\u0286\u028e\u029e\u02a2\u02ab\u02ad\u02af\n'
    '\u0391\u03b1\u0392\u03b2\u0393\u03b3\u0394\u03b4\u0395\u03b5'
    '\u0396\u03b6\u0397\u03b7\u0398\u03b8\u0399\u03b9\u039a\u03ba\n'
    '\u0411\u0431\u0414\u0434\u0416\u0436\u041f\u043f\u0424\u0444'
    '\u0427\u0447\u042a\u044a\u042d\u044d\u0460\u0464\u046c\u04dc\n'
    '\n<Hebrew, Arabic>\n'
    '\u05d0\u05d1\u05d2\u05d3\u05d4\u05d5\u05d6\u05d7\u05d8\u05d9'
    '\u05da\u05db\u05dc\u05dd\u05de\u05df\u05e0\u05e1\u05e2\u05e3\n'
    '\u0627\u0628\u062c\u062f\u0647\u0648\u0632\u062d\u0637\u064a'
    '\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669\n'
    '\n<Devanagari, Tamil>\n'
    '\u0966\u0967\u0968\u0969\u096a\u096b\u096c\u096d\u096e\u096f'
    '\u0905\u0906\u0907\u0908\u0909\u090a\u090f\u0910\u0913\u0914\n'
    '\u0be6\u0be7\u0be8\u0be9\u0bea\u0beb\u0bec\u0bed\u0bee\u0bef'
    '\u0b85\u0b87\u0b89\u0b8e\n'
    '\n<East Asian>\n'
    '\u3007\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\n'
    '\u6c49\u5b57\u6f22\u5b57\u4eba\u6728\u706b\u571f\u91d1\u6c34\n'
    '\uac00\ub0d0\ub354\ub824\ubaa8\ubd64\uc218\uc720\uc988\uce58\n'
    '\u3042\u3044\u3046\u3048\u304a\u30a2\u30a4\u30a6\u30a8\u30aa\n'
    )


kundi FontPage(Frame):

    eleza __init__(self, master, highpage):
        super().__init__(master)
        self.highlight_sample = highpage.highlight_sample
        self.create_page_font_tab()
        self.load_font_cfg()
        self.load_tab_cfg()

    eleza create_page_font_tab(self):
        """Return frame of widgets kila Font/Tabs tab.

        Fonts: Enable users to provisionally change font face, size, or
        boldness na to see the consequence of proposed choices.  Each
        action set 3 options kwenye changes structuree na changes the
        corresponding aspect of the font sample on this page and
        highlight sample on highlight page.

        Function load_font_cfg initializes font vars na widgets kutoka
        idleConf entries na tk.

        Fontlist: mouse button 1 click ama up ama down key invoke
        on_fontlist_select(), which sets var font_name.

        Sizelist: clicking the menubutton opens the dropdown menu. A
        mouse button 1 click ama rudisha key sets var font_size.

        Bold_toggle: clicking the box toggles var font_bold.

        Changing any of the font vars invokes var_changed_font, which
        adds all 3 font options to changes na calls set_samples.
        Set_samples applies a new font constructed kutoka the font vars to
        font_sample na to highlight_sample on the highlight page.

        Tabs: Enable users to change spaces entered kila indent tabs.
        Changing indent_scale value ukijumuisha the mouse sets Var space_num,
        which invokes the default callback to add an entry to
        changes.  Load_tab_cfg initializes space_num to default.

        Widgets kila FontPage(Frame):  (*) widgets bound to self
            frame_font: LabelFrame
                frame_font_name: Frame
                    font_name_title: Label
                    (*)fontlist: ListBox - font_name
                    scroll_font: Scrollbar
                frame_font_param: Frame
                    font_size_title: Label
                    (*)sizelist: DynOptionMenu - font_size
                    (*)bold_toggle: Checkbutton - font_bold
            frame_sample: LabelFrame
                (*)font_sample: Label
            frame_indent: LabelFrame
                    indent_title: Label
                    (*)indent_scale: Scale - space_num
        """
        self.font_name = tracers.add(StringVar(self), self.var_changed_font)
        self.font_size = tracers.add(StringVar(self), self.var_changed_font)
        self.font_bold = tracers.add(BooleanVar(self), self.var_changed_font)
        self.space_num = tracers.add(IntVar(self), ('main', 'Indent', 'num-spaces'))

        # Define frames na widgets.
        frame_font = LabelFrame(
                self, borderwidth=2, relief=GROOVE, text=' Shell/Editor Font ')
        frame_sample = LabelFrame(
                self, borderwidth=2, relief=GROOVE,
                text=' Font Sample (Editable) ')
        frame_indent = LabelFrame(
                self, borderwidth=2, relief=GROOVE, text=' Indentation Width ')
        # frame_font.
        frame_font_name = Frame(frame_font)
        frame_font_param = Frame(frame_font)
        font_name_title = Label(
                frame_font_name, justify=LEFT, text='Font Face :')
        self.fontlist = Listbox(frame_font_name, height=15,
                                takefocus=Kweli, exportselection=FALSE)
        self.fontlist.bind('<ButtonRelease-1>', self.on_fontlist_select)
        self.fontlist.bind('<KeyRelease-Up>', self.on_fontlist_select)
        self.fontlist.bind('<KeyRelease-Down>', self.on_fontlist_select)
        scroll_font = Scrollbar(frame_font_name)
        scroll_font.config(command=self.fontlist.yview)
        self.fontlist.config(yscrollcommand=scroll_font.set)
        font_size_title = Label(frame_font_param, text='Size :')
        self.sizelist = DynOptionMenu(frame_font_param, self.font_size, Tupu)
        self.bold_toggle = Checkbutton(
                frame_font_param, variable=self.font_bold,
                onvalue=1, offvalue=0, text='Bold')
        # frame_sample.
        font_sample_frame = ScrollableTextFrame(frame_sample)
        self.font_sample = font_sample_frame.text
        self.font_sample.config(wrap=NONE, width=1, height=1)
        self.font_sample.insert(END, font_sample_text)
        # frame_indent.
        indent_title = Label(
                frame_indent, justify=LEFT,
                text='Python Standard: 4 Spaces!')
        self.indent_scale = Scale(
                frame_indent, variable=self.space_num,
                orient='horizontal', tickinterval=2, kutoka_=2, to=16)

        # Grid na pack widgets:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        frame_font.grid(row=0, column=0, padx=5, pady=5)
        frame_sample.grid(row=0, column=1, rowspan=3, padx=5, pady=5,
                          sticky='nsew')
        frame_indent.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        # frame_font.
        frame_font_name.pack(side=TOP, padx=5, pady=5, fill=X)
        frame_font_param.pack(side=TOP, padx=5, pady=5, fill=X)
        font_name_title.pack(side=TOP, anchor=W)
        self.fontlist.pack(side=LEFT, expand=TRUE, fill=X)
        scroll_font.pack(side=LEFT, fill=Y)
        font_size_title.pack(side=LEFT, anchor=W)
        self.sizelist.pack(side=LEFT, anchor=W)
        self.bold_toggle.pack(side=LEFT, anchor=W, padx=20)
        # frame_sample.
        font_sample_frame.pack(expand=TRUE, fill=BOTH)
        # frame_indent.
        indent_title.pack(side=TOP, anchor=W, padx=5)
        self.indent_scale.pack(side=TOP, padx=5, fill=X)

    eleza load_font_cfg(self):
        """Load current configuration settings kila the font options.

        Retrieve current font ukijumuisha idleConf.GetFont na font families
        kutoka tk. Setup fontlist na set font_name.  Setup sizelist,
        which sets font_size.  Set font_bold.  Call set_samples.
        """
        configured_font = idleConf.GetFont(self, 'main', 'EditorWindow')
        font_name = configured_font[0].lower()
        font_size = configured_font[1]
        font_bold  = configured_font[2]=='bold'

        # Set editor font selection list na font_name.
        fonts = list(tkFont.families(self))
        fonts.sort()
        kila font kwenye fonts:
            self.fontlist.insert(END, font)
        self.font_name.set(font_name)
        lc_fonts = [s.lower() kila s kwenye fonts]
        jaribu:
            current_font_index = lc_fonts.index(font_name)
            self.fontlist.see(current_font_index)
            self.fontlist.select_set(current_font_index)
            self.fontlist.select_anchor(current_font_index)
            self.fontlist.activate(current_font_index)
        tatizo ValueError:
            pita
        # Set font size dropdown.
        self.sizelist.SetMenu(('7', '8', '9', '10', '11', '12', '13', '14',
                               '16', '18', '20', '22', '25', '29', '34', '40'),
                              font_size)
        # Set font weight.
        self.font_bold.set(font_bold)
        self.set_samples()

    eleza var_changed_font(self, *params):
        """Store changes to font attributes.

        When one font attribute changes, save them all, kama they are
        sio independent kutoka each other. In particular, when we are
        overriding the default font, we need to write out everything.
        """
        value = self.font_name.get()
        changes.add_option('main', 'EditorWindow', 'font', value)
        value = self.font_size.get()
        changes.add_option('main', 'EditorWindow', 'font-size', value)
        value = self.font_bold.get()
        changes.add_option('main', 'EditorWindow', 'font-bold', value)
        self.set_samples()

    eleza on_fontlist_select(self, event):
        """Handle selecting a font kutoka the list.

        Event can result kutoka either mouse click ama Up ama Down key.
        Set font_name na example displays to selection.
        """
        font = self.fontlist.get(
                ACTIVE ikiwa event.type.name == 'KeyRelease' isipokua ANCHOR)
        self.font_name.set(font.lower())

    eleza set_samples(self, event=Tupu):
        """Update update both screen samples ukijumuisha the font settings.

        Called on font initialization na change events.
        Accesses font_name, font_size, na font_bold Variables.
        Updates font_sample na highlight page highlight_sample.
        """
        font_name = self.font_name.get()
        font_weight = tkFont.BOLD ikiwa self.font_bold.get() isipokua tkFont.NORMAL
        new_font = (font_name, self.font_size.get(), font_weight)
        self.font_sample['font'] = new_font
        self.highlight_sample['font'] = new_font

    eleza load_tab_cfg(self):
        """Load current configuration settings kila the tab options.

        Attributes updated:
            space_num: Set to value kutoka idleConf.
        """
        # Set indent sizes.
        space_num = idleConf.GetOption(
            'main', 'Indent', 'num-spaces', default=4, type='int')
        self.space_num.set(space_num)

    eleza var_changed_space_num(self, *params):
        "Store change to indentation size."
        value = self.space_num.get()
        changes.add_option('main', 'Indent', 'num-spaces', value)


kundi HighPage(Frame):

    eleza __init__(self, master):
        super().__init__(master)
        self.cd = master.master
        self.style = Style(master)
        self.create_page_highlight()
        self.load_theme_cfg()

    eleza create_page_highlight(self):
        """Return frame of widgets kila Highlighting tab.

        Enable users to provisionally change foreground na background
        colors applied to textual tags.  Color mappings are stored in
        complete listings called themes.  Built-in themes in
        idlelib/config-highlight.eleza are fixed kama far kama the dialog is
        concerned. Any theme can be used kama the base kila a new custom
        theme, stored kwenye .idlerc/config-highlight.cfg.

        Function load_theme_cfg() initializes tk variables na theme
        lists na calls paint_theme_sample() na set_highlight_target()
        kila the current theme.  Radiobuttons builtin_theme_on and
        custom_theme_on toggle var theme_source, which controls ikiwa the
        current set of colors are kutoka a builtin ama custom theme.
        DynOptionMenus builtinlist na customlist contain lists of the
        builtin na custom themes, respectively, na the current item
        kutoka each list ni stored kwenye vars builtin_name na custom_name.

        Function paint_theme_sample() applies the colors kutoka the theme
        to the tags kwenye text widget highlight_sample na then invokes
        set_color_sample().  Function set_highlight_target() sets the state
        of the radiobuttons fg_on na bg_on based on the tag na it also
        invokes set_color_sample().

        Function set_color_sample() sets the background color kila the frame
        holding the color selector.  This provides a larger visual of the
        color kila the current tag na plane (foreground/background).

        Note: set_color_sample() ni called kutoka many places na ni often
        called more than once when a change ni made.  It ni invoked when
        foreground ama background ni selected (radiobuttons), kutoka
        paint_theme_sample() (theme ni changed ama load_cfg ni called), and
        kutoka set_highlight_target() (target tag ni changed ama load_cfg called).

        Button delete_custom invokes delete_custom() to delete
        a custom theme kutoka idleConf.userCfg['highlight'] na changes.
        Button save_custom invokes save_as_new_theme() which calls
        get_new_theme_name() na create_new() to save a custom theme
        na its colors to idleConf.userCfg['highlight'].

        Radiobuttons fg_on na bg_on toggle var fg_bg_toggle to control
        ikiwa the current selected color kila a tag ni kila the foreground or
        background.

        DynOptionMenu targetlist contains a readable description of the
        tags applied to Python source within IDLE.  Selecting one of the
        tags kutoka this list populates highlight_target, which has a callback
        function set_highlight_target().

        Text widget highlight_sample displays a block of text (which is
        mock Python code) kwenye which ni embedded the defined tags na reflects
        the color attributes of the current theme na changes kila those tags.
        Mouse button 1 allows kila selection of a tag na updates
        highlight_target ukijumuisha that tag value.

        Note: The font kwenye highlight_sample ni set through the config in
        the fonts tab.

        In other words, a tag can be selected either kutoka targetlist or
        by clicking on the sample text within highlight_sample.  The
        plane (foreground/background) ni selected via the radiobutton.
        Together, these two (tag na plane) control what color is
        shown kwenye set_color_sample() kila the current theme.  Button set_color
        invokes get_color() which displays a ColorChooser to change the
        color kila the selected tag/plane.  If a new color ni picked,
        it will be saved to changes na the highlight_sample and
        frame background will be updated.

        Tk Variables:
            color: Color of selected target.
            builtin_name: Menu variable kila built-in theme.
            custom_name: Menu variable kila custom theme.
            fg_bg_toggle: Toggle kila foreground/background color.
                Note: this has no callback.
            theme_source: Selector kila built-in ama custom theme.
            highlight_target: Menu variable kila the highlight tag target.

        Instance Data Attributes:
            theme_elements: Dictionary of tags kila text highlighting.
                The key ni the display name na the value ni a tuple of
                (tag name, display sort order).

        Methods [attachment]:
            load_theme_cfg: Load current highlight colors.
            get_color: Invoke colorchooser [button_set_color].
            set_color_sample_binding: Call set_color_sample [fg_bg_toggle].
            set_highlight_target: set fg_bg_toggle, set_color_sample().
            set_color_sample: Set frame background to target.
            on_new_color_set: Set new color na add option.
            paint_theme_sample: Recolor sample.
            get_new_theme_name: Get kutoka popup.
            create_new: Combine theme ukijumuisha changes na save.
            save_as_new_theme: Save [button_save_custom].
            set_theme_type: Command kila [theme_source].
            delete_custom: Activate default [button_delete_custom].
            save_new: Save to userCfg['theme'] (is function).

        Widgets of highlights page frame:  (*) widgets bound to self
            frame_custom: LabelFrame
                (*)highlight_sample: Text
                (*)frame_color_set: Frame
                    (*)button_set_color: Button
                    (*)targetlist: DynOptionMenu - highlight_target
                frame_fg_bg_toggle: Frame
                    (*)fg_on: Radiobutton - fg_bg_toggle
                    (*)bg_on: Radiobutton - fg_bg_toggle
                (*)button_save_custom: Button
            frame_theme: LabelFrame
                theme_type_title: Label
                (*)builtin_theme_on: Radiobutton - theme_source
                (*)custom_theme_on: Radiobutton - theme_source
                (*)builtinlist: DynOptionMenu - builtin_name
                (*)customlist: DynOptionMenu - custom_name
                (*)button_delete_custom: Button
                (*)theme_message: Label
        """
        self.theme_elements = {
            'Normal Code ama Text': ('normal', '00'),
            'Code Context': ('context', '01'),
            'Python Keywords': ('keyword', '02'),
            'Python Definitions': ('definition', '03'),
            'Python Builtins': ('builtin', '04'),
            'Python Comments': ('comment', '05'),
            'Python Strings': ('string', '06'),
            'Selected Text': ('hilite', '07'),
            'Found Text': ('hit', '08'),
            'Cursor': ('cursor', '09'),
            'Editor Breakpoint': ('koma', '10'),
            'Shell Prompt': ('console', '11'),
            'Error Text': ('error', '12'),
            'Shell User Output': ('stdout', '13'),
            'Shell User Exception': ('stderr', '14'),
            'Line Number': ('linenumber', '16'),
            }
        self.builtin_name = tracers.add(
                StringVar(self), self.var_changed_builtin_name)
        self.custom_name = tracers.add(
                StringVar(self), self.var_changed_custom_name)
        self.fg_bg_toggle = BooleanVar(self)
        self.color = tracers.add(
                StringVar(self), self.var_changed_color)
        self.theme_source = tracers.add(
                BooleanVar(self), self.var_changed_theme_source)
        self.highlight_target = tracers.add(
                StringVar(self), self.var_changed_highlight_target)

        # Create widgets:
        # body frame na section frames.
        frame_custom = LabelFrame(self, borderwidth=2, relief=GROOVE,
                                  text=' Custom Highlighting ')
        frame_theme = LabelFrame(self, borderwidth=2, relief=GROOVE,
                                 text=' Highlighting Theme ')
        # frame_custom.
        sample_frame = ScrollableTextFrame(
                frame_custom, relief=SOLID, borderwidth=1)
        text = self.highlight_sample = sample_frame.text
        text.configure(
                font=('courier', 12, ''), cursor='hand2', width=1, height=1,
                takefocus=FALSE, highlightthickness=0, wrap=NONE)
        text.bind('<Double-Button-1>', lambda e: 'koma')
        text.bind('<B1-Motion>', lambda e: 'koma')
        string_tags=(
            ('# Click selects item.', 'comment'), ('\n', 'normal'),
            ('code context section', 'context'), ('\n', 'normal'),
            ('| cursor', 'cursor'), ('\n', 'normal'),
            ('def', 'keyword'), (' ', 'normal'),
            ('func', 'definition'), ('(param):\n  ', 'normal'),
            ('"Return Tupu."', 'string'), ('\n  var0 = ', 'normal'),
            ("'string'", 'string'), ('\n  var1 = ', 'normal'),
            ("'selected'", 'hilite'), ('\n  var2 = ', 'normal'),
            ("'found'", 'hit'), ('\n  var3 = ', 'normal'),
            ('list', 'builtin'), ('(', 'normal'),
            ('Tupu', 'keyword'), (')\n', 'normal'),
            ('  komapoint("line")', 'koma'), ('\n\n', 'normal'),
            ('>>>', 'console'), (' 3.14**2\n', 'normal'),
            ('9.8596', 'stdout'), ('\n', 'normal'),
            ('>>>', 'console'), (' pri ', 'normal'),
            ('n', 'error'), ('t(\n', 'normal'),
            ('SyntaxError', 'stderr'), ('\n', 'normal'))
        kila string, tag kwenye string_tags:
            text.insert(END, string, tag)
        n_lines = len(text.get('1.0', END).splitlines())
        kila lineno kwenye range(1, n_lines):
            text.insert(f'{lineno}.0',
                        f'{lineno:{len(str(n_lines))}d} ',
                        'linenumber')
        kila element kwenye self.theme_elements:
            eleza tem(event, elem=element):
                # event.widget.winfo_top_level().highlight_target.set(elem)
                self.highlight_target.set(elem)
            text.tag_bind(
                    self.theme_elements[element][0], '<ButtonPress-1>', tem)
        text['state'] = 'disabled'
        self.style.configure('frame_color_set.TFrame', borderwidth=1,
                             relief='solid')
        self.frame_color_set = Frame(frame_custom, style='frame_color_set.TFrame')
        frame_fg_bg_toggle = Frame(frame_custom)
        self.button_set_color = Button(
                self.frame_color_set, text='Choose Color kila :',
                command=self.get_color)
        self.targetlist = DynOptionMenu(
                self.frame_color_set, self.highlight_target, Tupu,
                highlightthickness=0) #, command=self.set_highlight_targetBinding
        self.fg_on = Radiobutton(
                frame_fg_bg_toggle, variable=self.fg_bg_toggle, value=1,
                text='Foreground', command=self.set_color_sample_binding)
        self.bg_on = Radiobutton(
                frame_fg_bg_toggle, variable=self.fg_bg_toggle, value=0,
                text='Background', command=self.set_color_sample_binding)
        self.fg_bg_toggle.set(1)
        self.button_save_custom = Button(
                frame_custom, text='Save kama New Custom Theme',
                command=self.save_as_new_theme)
        # frame_theme.
        theme_type_title = Label(frame_theme, text='Select : ')
        self.builtin_theme_on = Radiobutton(
                frame_theme, variable=self.theme_source, value=1,
                command=self.set_theme_type, text='a Built-in Theme')
        self.custom_theme_on = Radiobutton(
                frame_theme, variable=self.theme_source, value=0,
                command=self.set_theme_type, text='a Custom Theme')
        self.builtinlist = DynOptionMenu(
                frame_theme, self.builtin_name, Tupu, command=Tupu)
        self.customlist = DynOptionMenu(
                frame_theme, self.custom_name, Tupu, command=Tupu)
        self.button_delete_custom = Button(
                frame_theme, text='Delete Custom Theme',
                command=self.delete_custom)
        self.theme_message = Label(frame_theme, borderwidth=2)
        # Pack widgets:
        # body.
        frame_custom.pack(side=LEFT, padx=5, pady=5, expand=TRUE, fill=BOTH)
        frame_theme.pack(side=TOP, padx=5, pady=5, fill=X)
        # frame_custom.
        self.frame_color_set.pack(side=TOP, padx=5, pady=5, fill=X)
        frame_fg_bg_toggle.pack(side=TOP, padx=5, pady=0)
        sample_frame.pack(
                side=TOP, padx=5, pady=5, expand=TRUE, fill=BOTH)
        self.button_set_color.pack(side=TOP, expand=TRUE, fill=X, padx=8, pady=4)
        self.targetlist.pack(side=TOP, expand=TRUE, fill=X, padx=8, pady=3)
        self.fg_on.pack(side=LEFT, anchor=E)
        self.bg_on.pack(side=RIGHT, anchor=W)
        self.button_save_custom.pack(side=BOTTOM, fill=X, padx=5, pady=5)
        # frame_theme.
        theme_type_title.pack(side=TOP, anchor=W, padx=5, pady=5)
        self.builtin_theme_on.pack(side=TOP, anchor=W, padx=5)
        self.custom_theme_on.pack(side=TOP, anchor=W, padx=5, pady=2)
        self.builtinlist.pack(side=TOP, fill=X, padx=5, pady=5)
        self.customlist.pack(side=TOP, fill=X, anchor=W, padx=5, pady=5)
        self.button_delete_custom.pack(side=TOP, fill=X, padx=5, pady=5)
        self.theme_message.pack(side=TOP, fill=X, pady=5)

    eleza load_theme_cfg(self):
        """Load current configuration settings kila the theme options.

        Based on the theme_source toggle, the theme ni set as
        either builtin ama custom na the initial widget values
        reflect the current settings kutoka idleConf.

        Attributes updated:
            theme_source: Set kutoka idleConf.
            builtinlist: List of default themes kutoka idleConf.
            customlist: List of custom themes kutoka idleConf.
            custom_theme_on: Disabled ikiwa there are no custom themes.
            custom_theme: Message ukijumuisha additional information.
            targetlist: Create menu kutoka self.theme_elements.

        Methods:
            set_theme_type
            paint_theme_sample
            set_highlight_target
        """
        # Set current theme type radiobutton.
        self.theme_source.set(idleConf.GetOption(
                'main', 'Theme', 'default', type='bool', default=1))
        # Set current theme.
        current_option = idleConf.CurrentTheme()
        # Load available theme option menus.
        ikiwa self.theme_source.get():  # Default theme selected.
            item_list = idleConf.GetSectionList('default', 'highlight')
            item_list.sort()
            self.builtinlist.SetMenu(item_list, current_option)
            item_list = idleConf.GetSectionList('user', 'highlight')
            item_list.sort()
            ikiwa sio item_list:
                self.custom_theme_on.state(('disabled',))
                self.custom_name.set('- no custom themes -')
            isipokua:
                self.customlist.SetMenu(item_list, item_list[0])
        isipokua:  # User theme selected.
            item_list = idleConf.GetSectionList('user', 'highlight')
            item_list.sort()
            self.customlist.SetMenu(item_list, current_option)
            item_list = idleConf.GetSectionList('default', 'highlight')
            item_list.sort()
            self.builtinlist.SetMenu(item_list, item_list[0])
        self.set_theme_type()
        # Load theme element option menu.
        theme_names = list(self.theme_elements.keys())
        theme_names.sort(key=lambda x: self.theme_elements[x][1])
        self.targetlist.SetMenu(theme_names, theme_names[0])
        self.paint_theme_sample()
        self.set_highlight_target()

    eleza var_changed_builtin_name(self, *params):
        """Process new builtin theme selection.

        Add the changed theme's name to the changed_items na recreate
        the sample ukijumuisha the values kutoka the selected theme.
        """
        old_themes = ('IDLE Classic', 'IDLE New')
        value = self.builtin_name.get()
        ikiwa value haiko kwenye old_themes:
            ikiwa idleConf.GetOption('main', 'Theme', 'name') haiko kwenye old_themes:
                changes.add_option('main', 'Theme', 'name', old_themes[0])
            changes.add_option('main', 'Theme', 'name2', value)
            self.theme_message['text'] = 'New theme, see Help'
        isipokua:
            changes.add_option('main', 'Theme', 'name', value)
            changes.add_option('main', 'Theme', 'name2', '')
            self.theme_message['text'] = ''
        self.paint_theme_sample()

    eleza var_changed_custom_name(self, *params):
        """Process new custom theme selection.

        If a new custom theme ni selected, add the name to the
        changed_items na apply the theme to the sample.
        """
        value = self.custom_name.get()
        ikiwa value != '- no custom themes -':
            changes.add_option('main', 'Theme', 'name', value)
            self.paint_theme_sample()

    eleza var_changed_theme_source(self, *params):
        """Process toggle between builtin na custom theme.

        Update the default toggle value na apply the newly
        selected theme type.
        """
        value = self.theme_source.get()
        changes.add_option('main', 'Theme', 'default', value)
        ikiwa value:
            self.var_changed_builtin_name()
        isipokua:
            self.var_changed_custom_name()

    eleza var_changed_color(self, *params):
        "Process change to color choice."
        self.on_new_color_set()

    eleza var_changed_highlight_target(self, *params):
        "Process selection of new target tag kila highlighting."
        self.set_highlight_target()

    eleza set_theme_type(self):
        """Set available screen options based on builtin ama custom theme.

        Attributes accessed:
            theme_source

        Attributes updated:
            builtinlist
            customlist
            button_delete_custom
            custom_theme_on

        Called kutoka:
            handler kila builtin_theme_on na custom_theme_on
            delete_custom
            create_new
            load_theme_cfg
        """
        ikiwa self.theme_source.get():
            self.builtinlist['state'] = 'normal'
            self.customlist['state'] = 'disabled'
            self.button_delete_custom.state(('disabled',))
        isipokua:
            self.builtinlist['state'] = 'disabled'
            self.custom_theme_on.state(('!disabled',))
            self.customlist['state'] = 'normal'
            self.button_delete_custom.state(('!disabled',))

    eleza get_color(self):
        """Handle button to select a new color kila the target tag.

        If a new color ni selected wakati using a builtin theme, a
        name must be supplied to create a custom theme.

        Attributes accessed:
            highlight_target
            frame_color_set
            theme_source

        Attributes updated:
            color

        Methods:
            get_new_theme_name
            create_new
        """
        target = self.highlight_target.get()
        prev_color = self.style.lookup(self.frame_color_set['style'],
                                       'background')
        rgbTuplet, color_string = tkColorChooser.askcolor(
                parent=self, title='Pick new color kila : '+target,
                initialcolor=prev_color)
        ikiwa color_string na (color_string != prev_color):
            # User didn't cancel na they chose a new color.
            ikiwa self.theme_source.get():  # Current theme ni a built-in.
                message = ('Your changes will be saved kama a new Custom Theme. '
                           'Enter a name kila your new Custom Theme below.')
                new_theme = self.get_new_theme_name(message)
                ikiwa sio new_theme:  # User cancelled custom theme creation.
                    rudisha
                isipokua:  # Create new custom theme based on previously active theme.
                    self.create_new(new_theme)
                    self.color.set(color_string)
            isipokua:  # Current theme ni user defined.
                self.color.set(color_string)

    eleza on_new_color_set(self):
        "Display sample of new color selection on the dialog."
        new_color = self.color.get()
        self.style.configure('frame_color_set.TFrame', background=new_color)
        plane = 'foreground' ikiwa self.fg_bg_toggle.get() isipokua 'background'
        sample_element = self.theme_elements[self.highlight_target.get()][0]
        self.highlight_sample.tag_config(sample_element, **{plane: new_color})
        theme = self.custom_name.get()
        theme_element = sample_element + '-' + plane
        changes.add_option('highlight', theme, theme_element, new_color)

    eleza get_new_theme_name(self, message):
        "Return name of new theme kutoka query popup."
        used_names = (idleConf.GetSectionList('user', 'highlight') +
                idleConf.GetSectionList('default', 'highlight'))
        new_theme = SectionName(
                self, 'New Custom Theme', message, used_names).result
        rudisha new_theme

    eleza save_as_new_theme(self):
        """Prompt kila new theme name na create the theme.

        Methods:
            get_new_theme_name
            create_new
        """
        new_theme_name = self.get_new_theme_name('New Theme Name:')
        ikiwa new_theme_name:
            self.create_new(new_theme_name)

    eleza create_new(self, new_theme_name):
        """Create a new custom theme ukijumuisha the given name.

        Create the new theme based on the previously active theme
        ukijumuisha the current changes applied.  Once it ni saved, then
        activate the new theme.

        Attributes accessed:
            builtin_name
            custom_name

        Attributes updated:
            customlist
            theme_source

        Method:
            save_new
            set_theme_type
        """
        ikiwa self.theme_source.get():
            theme_type = 'default'
            theme_name = self.builtin_name.get()
        isipokua:
            theme_type = 'user'
            theme_name = self.custom_name.get()
        new_theme = idleConf.GetThemeDict(theme_type, theme_name)
        # Apply any of the old theme's unsaved changes to the new theme.
        ikiwa theme_name kwenye changes['highlight']:
            theme_changes = changes['highlight'][theme_name]
            kila element kwenye theme_changes:
                new_theme[element] = theme_changes[element]
        # Save the new theme.
        self.save_new(new_theme_name, new_theme)
        # Change GUI over to the new theme.
        custom_theme_list = idleConf.GetSectionList('user', 'highlight')
        custom_theme_list.sort()
        self.customlist.SetMenu(custom_theme_list, new_theme_name)
        self.theme_source.set(0)
        self.set_theme_type()

    eleza set_highlight_target(self):
        """Set fg/bg toggle na color based on highlight tag target.

        Instance variables accessed:
            highlight_target

        Attributes updated:
            fg_on
            bg_on
            fg_bg_toggle

        Methods:
            set_color_sample

        Called kutoka:
            var_changed_highlight_target
            load_theme_cfg
        """
        ikiwa self.highlight_target.get() == 'Cursor':  # bg sio possible
            self.fg_on.state(('disabled',))
            self.bg_on.state(('disabled',))
            self.fg_bg_toggle.set(1)
        isipokua:  # Both fg na bg can be set.
            self.fg_on.state(('!disabled',))
            self.bg_on.state(('!disabled',))
            self.fg_bg_toggle.set(1)
        self.set_color_sample()

    eleza set_color_sample_binding(self, *args):
        """Change color sample based on foreground/background toggle.

        Methods:
            set_color_sample
        """
        self.set_color_sample()

    eleza set_color_sample(self):
        """Set the color of the frame background to reflect the selected target.

        Instance variables accessed:
            theme_elements
            highlight_target
            fg_bg_toggle
            highlight_sample

        Attributes updated:
            frame_color_set
        """
        # Set the color sample area.
        tag = self.theme_elements[self.highlight_target.get()][0]
        plane = 'foreground' ikiwa self.fg_bg_toggle.get() isipokua 'background'
        color = self.highlight_sample.tag_cget(tag, plane)
        self.style.configure('frame_color_set.TFrame', background=color)

    eleza paint_theme_sample(self):
        """Apply the theme colors to each element tag kwenye the sample text.

        Instance attributes accessed:
            theme_elements
            theme_source
            builtin_name
            custom_name

        Attributes updated:
            highlight_sample: Set the tag elements to the theme.

        Methods:
            set_color_sample

        Called kutoka:
            var_changed_builtin_name
            var_changed_custom_name
            load_theme_cfg
        """
        ikiwa self.theme_source.get():  # Default theme
            theme = self.builtin_name.get()
        isipokua:  # User theme
            theme = self.custom_name.get()
        kila element_title kwenye self.theme_elements:
            element = self.theme_elements[element_title][0]
            colors = idleConf.GetHighlight(theme, element)
            ikiwa element == 'cursor':  # Cursor sample needs special painting.
                colors['background'] = idleConf.GetHighlight(
                        theme, 'normal')['background']
            # Handle any unsaved changes to this theme.
            ikiwa theme kwenye changes['highlight']:
                theme_dict = changes['highlight'][theme]
                ikiwa element + '-foreground' kwenye theme_dict:
                    colors['foreground'] = theme_dict[element + '-foreground']
                ikiwa element + '-background' kwenye theme_dict:
                    colors['background'] = theme_dict[element + '-background']
            self.highlight_sample.tag_config(element, **colors)
        self.set_color_sample()

    eleza save_new(self, theme_name, theme):
        """Save a newly created theme to idleConf.

        theme_name - string, the name of the new theme
        theme - dictionary containing the new theme
        """
        ikiwa sio idleConf.userCfg['highlight'].has_section(theme_name):
            idleConf.userCfg['highlight'].add_section(theme_name)
        kila element kwenye theme:
            value = theme[element]
            idleConf.userCfg['highlight'].SetOption(theme_name, element, value)

    eleza askyesno(self, *args, **kwargs):
        # Make testing easier.  Could change implementation.
        rudisha messagebox.askyesno(*args, **kwargs)

    eleza delete_custom(self):
        """Handle event to delete custom theme.

        The current theme ni deactivated na the default theme is
        activated.  The custom theme ni permanently removed kutoka
        the config file.

        Attributes accessed:
            custom_name

        Attributes updated:
            custom_theme_on
            customlist
            theme_source
            builtin_name

        Methods:
            deactivate_current_config
            save_all_changed_extensions
            activate_config_changes
            set_theme_type
        """
        theme_name = self.custom_name.get()
        delmsg = 'Are you sure you wish to delete the theme %r ?'
        ikiwa sio self.askyesno(
                'Delete Theme',  delmsg % theme_name, parent=self):
            rudisha
        self.cd.deactivate_current_config()
        # Remove theme kutoka changes, config, na file.
        changes.delete_section('highlight', theme_name)
        # Reload user theme list.
        item_list = idleConf.GetSectionList('user', 'highlight')
        item_list.sort()
        ikiwa sio item_list:
            self.custom_theme_on.state(('disabled',))
            self.customlist.SetMenu(item_list, '- no custom themes -')
        isipokua:
            self.customlist.SetMenu(item_list, item_list[0])
        # Revert to default theme.
        self.theme_source.set(idleConf.defaultCfg['main'].Get('Theme', 'default'))
        self.builtin_name.set(idleConf.defaultCfg['main'].Get('Theme', 'name'))
        # User can't back out of these changes, they must be applied now.
        changes.save_all()
        self.cd.save_all_changed_extensions()
        self.cd.activate_config_changes()
        self.set_theme_type()


kundi KeysPage(Frame):

    eleza __init__(self, master):
        super().__init__(master)
        self.cd = master.master
        self.create_page_keys()
        self.load_key_cfg()

    eleza create_page_keys(self):
        """Return frame of widgets kila Keys tab.

        Enable users to provisionally change both individual na sets of
        keybindings (shortcut keys). Except kila features implemented as
        extensions, keybindings are stored kwenye complete sets called
        keysets. Built-in keysets kwenye idlelib/config-keys.eleza are fixed
        kama far kama the dialog ni concerned. Any keyset can be used kama the
        base kila a new custom keyset, stored kwenye .idlerc/config-keys.cfg.

        Function load_key_cfg() initializes tk variables na keyset
        lists na calls load_keys_list kila the current keyset.
        Radiobuttons builtin_keyset_on na custom_keyset_on toggle var
        keyset_source, which controls ikiwa the current set of keybindings
        are kutoka a builtin ama custom keyset. DynOptionMenus builtinlist
        na customlist contain lists of the builtin na custom keysets,
        respectively, na the current item kutoka each list ni stored in
        vars builtin_name na custom_name.

        Button delete_custom_keys invokes delete_custom_keys() to delete
        a custom keyset kutoka idleConf.userCfg['keys'] na changes.  Button
        save_custom_keys invokes save_as_new_key_set() which calls
        get_new_keys_name() na create_new_key_set() to save a custom keyset
        na its keybindings to idleConf.userCfg['keys'].

        Listbox bindingslist contains all of the keybindings kila the
        selected keyset.  The keybindings are loaded kwenye load_keys_list()
        na are pairs of (event, [keys]) where keys can be a list
        of one ama more key combinations to bind to the same event.
        Mouse button 1 click invokes on_bindingslist_select(), which
        allows button_new_keys to be clicked.

        So, an item ni selected kwenye listbindings, which activates
        button_new_keys, na clicking button_new_keys calls function
        get_new_keys().  Function get_new_keys() gets the key mappings kutoka the
        current keyset kila the binding event item that was selected.  The
        function then displays another dialog, GetKeysDialog, ukijumuisha the
        selected binding event na current keys na allows new key sequences
        to be entered kila that binding event.  If the keys aren't
        changed, nothing happens.  If the keys are changed na the keyset
        ni a builtin, function get_new_keys_name() will be called
        kila input of a custom keyset name.  If no name ni given, then the
        change to the keybinding will abort na no updates will be made.  If
        a custom name ni entered kwenye the prompt ama ikiwa the current keyset was
        already custom (and thus didn't require a prompt), then
        idleConf.userCfg['keys'] ni updated kwenye function create_new_key_set()
        ukijumuisha the change to the event binding.  The item listing kwenye bindingslist
        ni updated ukijumuisha the new keys.  Var keybinding ni also set which invokes
        the callback function, var_changed_keybinding, to add the change to
        the 'keys' ama 'extensions' changes tracker based on the binding type.

        Tk Variables:
            keybinding: Action/key bindings.

        Methods:
            load_keys_list: Reload active set.
            create_new_key_set: Combine active keyset na changes.
            set_keys_type: Command kila keyset_source.
            save_new_key_set: Save to idleConf.userCfg['keys'] (is function).
            deactivate_current_config: Remove keys bindings kwenye editors.

        Widgets kila KeysPage(frame):  (*) widgets bound to self
            frame_key_sets: LabelFrame
                frames[0]: Frame
                    (*)builtin_keyset_on: Radiobutton - var keyset_source
                    (*)custom_keyset_on: Radiobutton - var keyset_source
                    (*)builtinlist: DynOptionMenu - var builtin_name,
                            func keybinding_selected
                    (*)customlist: DynOptionMenu - var custom_name,
                            func keybinding_selected
                    (*)keys_message: Label
                frames[1]: Frame
                    (*)button_delete_custom_keys: Button - delete_custom_keys
                    (*)button_save_custom_keys: Button -  save_as_new_key_set
            frame_custom: LabelFrame
                frame_target: Frame
                    target_title: Label
                    scroll_target_y: Scrollbar
                    scroll_target_x: Scrollbar
                    (*)bindingslist: ListBox - on_bindingslist_select
                    (*)button_new_keys: Button - get_new_keys & ..._name
        """
        self.builtin_name = tracers.add(
                StringVar(self), self.var_changed_builtin_name)
        self.custom_name = tracers.add(
                StringVar(self), self.var_changed_custom_name)
        self.keyset_source = tracers.add(
                BooleanVar(self), self.var_changed_keyset_source)
        self.keybinding = tracers.add(
                StringVar(self), self.var_changed_keybinding)

        # Create widgets:
        # body na section frames.
        frame_custom = LabelFrame(
                self, borderwidth=2, relief=GROOVE,
                text=' Custom Key Bindings ')
        frame_key_sets = LabelFrame(
                self, borderwidth=2, relief=GROOVE, text=' Key Set ')
        # frame_custom.
        frame_target = Frame(frame_custom)
        target_title = Label(frame_target, text='Action - Key(s)')
        scroll_target_y = Scrollbar(frame_target)
        scroll_target_x = Scrollbar(frame_target, orient=HORIZONTAL)
        self.bindingslist = Listbox(
                frame_target, takefocus=FALSE, exportselection=FALSE)
        self.bindingslist.bind('<ButtonRelease-1>',
                               self.on_bindingslist_select)
        scroll_target_y['command'] = self.bindingslist.yview
        scroll_target_x['command'] = self.bindingslist.xview
        self.bindingslist['yscrollcommand'] = scroll_target_y.set
        self.bindingslist['xscrollcommand'] = scroll_target_x.set
        self.button_new_keys = Button(
                frame_custom, text='Get New Keys kila Selection',
                command=self.get_new_keys, state='disabled')
        # frame_key_sets.
        frames = [Frame(frame_key_sets, padding=2, borderwidth=0)
                  kila i kwenye range(2)]
        self.builtin_keyset_on = Radiobutton(
                frames[0], variable=self.keyset_source, value=1,
                command=self.set_keys_type, text='Use a Built-in Key Set')
        self.custom_keyset_on = Radiobutton(
                frames[0], variable=self.keyset_source, value=0,
                command=self.set_keys_type, text='Use a Custom Key Set')
        self.builtinlist = DynOptionMenu(
                frames[0], self.builtin_name, Tupu, command=Tupu)
        self.customlist = DynOptionMenu(
                frames[0], self.custom_name, Tupu, command=Tupu)
        self.button_delete_custom_keys = Button(
                frames[1], text='Delete Custom Key Set',
                command=self.delete_custom_keys)
        self.button_save_custom_keys = Button(
                frames[1], text='Save kama New Custom Key Set',
                command=self.save_as_new_key_set)
        self.keys_message = Label(frames[0], borderwidth=2)

        # Pack widgets:
        # body.
        frame_custom.pack(side=BOTTOM, padx=5, pady=5, expand=TRUE, fill=BOTH)
        frame_key_sets.pack(side=BOTTOM, padx=5, pady=5, fill=BOTH)
        # frame_custom.
        self.button_new_keys.pack(side=BOTTOM, fill=X, padx=5, pady=5)
        frame_target.pack(side=LEFT, padx=5, pady=5, expand=TRUE, fill=BOTH)
        # frame_target.
        frame_target.columnconfigure(0, weight=1)
        frame_target.rowconfigure(1, weight=1)
        target_title.grid(row=0, column=0, columnspan=2, sticky=W)
        self.bindingslist.grid(row=1, column=0, sticky=NSEW)
        scroll_target_y.grid(row=1, column=1, sticky=NS)
        scroll_target_x.grid(row=2, column=0, sticky=EW)
        # frame_key_sets.
        self.builtin_keyset_on.grid(row=0, column=0, sticky=W+NS)
        self.custom_keyset_on.grid(row=1, column=0, sticky=W+NS)
        self.builtinlist.grid(row=0, column=1, sticky=NSEW)
        self.customlist.grid(row=1, column=1, sticky=NSEW)
        self.keys_message.grid(row=0, column=2, sticky=NSEW, padx=5, pady=5)
        self.button_delete_custom_keys.pack(side=LEFT, fill=X, expand=Kweli, padx=2)
        self.button_save_custom_keys.pack(side=LEFT, fill=X, expand=Kweli, padx=2)
        frames[0].pack(side=TOP, fill=BOTH, expand=Kweli)
        frames[1].pack(side=TOP, fill=X, expand=Kweli, pady=2)

    eleza load_key_cfg(self):
        "Load current configuration settings kila the keybinding options."
        # Set current keys type radiobutton.
        self.keyset_source.set(idleConf.GetOption(
                'main', 'Keys', 'default', type='bool', default=1))
        # Set current keys.
        current_option = idleConf.CurrentKeys()
        # Load available keyset option menus.
        ikiwa self.keyset_source.get():  # Default theme selected.
            item_list = idleConf.GetSectionList('default', 'keys')
            item_list.sort()
            self.builtinlist.SetMenu(item_list, current_option)
            item_list = idleConf.GetSectionList('user', 'keys')
            item_list.sort()
            ikiwa sio item_list:
                self.custom_keyset_on.state(('disabled',))
                self.custom_name.set('- no custom keys -')
            isipokua:
                self.customlist.SetMenu(item_list, item_list[0])
        isipokua:  # User key set selected.
            item_list = idleConf.GetSectionList('user', 'keys')
            item_list.sort()
            self.customlist.SetMenu(item_list, current_option)
            item_list = idleConf.GetSectionList('default', 'keys')
            item_list.sort()
            self.builtinlist.SetMenu(item_list, idleConf.default_keys())
        self.set_keys_type()
        # Load keyset element list.
        keyset_name = idleConf.CurrentKeys()
        self.load_keys_list(keyset_name)

    eleza var_changed_builtin_name(self, *params):
        "Process selection of builtin key set."
        old_keys = (
            'IDLE Classic Windows',
            'IDLE Classic Unix',
            'IDLE Classic Mac',
            'IDLE Classic OSX',
        )
        value = self.builtin_name.get()
        ikiwa value haiko kwenye old_keys:
            ikiwa idleConf.GetOption('main', 'Keys', 'name') haiko kwenye old_keys:
                changes.add_option('main', 'Keys', 'name', old_keys[0])
            changes.add_option('main', 'Keys', 'name2', value)
            self.keys_message['text'] = 'New key set, see Help'
        isipokua:
            changes.add_option('main', 'Keys', 'name', value)
            changes.add_option('main', 'Keys', 'name2', '')
            self.keys_message['text'] = ''
        self.load_keys_list(value)

    eleza var_changed_custom_name(self, *params):
        "Process selection of custom key set."
        value = self.custom_name.get()
        ikiwa value != '- no custom keys -':
            changes.add_option('main', 'Keys', 'name', value)
            self.load_keys_list(value)

    eleza var_changed_keyset_source(self, *params):
        "Process toggle between builtin key set na custom key set."
        value = self.keyset_source.get()
        changes.add_option('main', 'Keys', 'default', value)
        ikiwa value:
            self.var_changed_builtin_name()
        isipokua:
            self.var_changed_custom_name()

    eleza var_changed_keybinding(self, *params):
        "Store change to a keybinding."
        value = self.keybinding.get()
        key_set = self.custom_name.get()
        event = self.bindingslist.get(ANCHOR).split()[0]
        ikiwa idleConf.IsCoreBinding(event):
            changes.add_option('keys', key_set, event, value)
        isipokua:  # Event ni an extension binding.
            ext_name = idleConf.GetExtnNameForEvent(event)
            ext_keybind_section = ext_name + '_cfgBindings'
            changes.add_option('extensions', ext_keybind_section, event, value)

    eleza set_keys_type(self):
        "Set available screen options based on builtin ama custom key set."
        ikiwa self.keyset_source.get():
            self.builtinlist['state'] = 'normal'
            self.customlist['state'] = 'disabled'
            self.button_delete_custom_keys.state(('disabled',))
        isipokua:
            self.builtinlist['state'] = 'disabled'
            self.custom_keyset_on.state(('!disabled',))
            self.customlist['state'] = 'normal'
            self.button_delete_custom_keys.state(('!disabled',))

    eleza get_new_keys(self):
        """Handle event to change key binding kila selected line.

        A selection of a key/binding kwenye the list of current
        bindings pops up a dialog to enter a new binding.  If
        the current key set ni builtin na a binding has
        changed, then a name kila a custom key set needs to be
        entered kila the change to be applied.
        """
        list_index = self.bindingslist.index(ANCHOR)
        binding = self.bindingslist.get(list_index)
        bind_name = binding.split()[0]
        ikiwa self.keyset_source.get():
            current_key_set_name = self.builtin_name.get()
        isipokua:
            current_key_set_name = self.custom_name.get()
        current_bindings = idleConf.GetCurrentKeySet()
        ikiwa current_key_set_name kwenye changes['keys']:  # unsaved changes
            key_set_changes = changes['keys'][current_key_set_name]
            kila event kwenye key_set_changes:
                current_bindings[event] = key_set_changes[event].split()
        current_key_sequences = list(current_bindings.values())
        new_keys = GetKeysDialog(self, 'Get New Keys', bind_name,
                current_key_sequences).result
        ikiwa new_keys:
            ikiwa self.keyset_source.get():  # Current key set ni a built-in.
                message = ('Your changes will be saved kama a new Custom Key Set.'
                           ' Enter a name kila your new Custom Key Set below.')
                new_keyset = self.get_new_keys_name(message)
                ikiwa sio new_keyset:  # User cancelled custom key set creation.
                    self.bindingslist.select_set(list_index)
                    self.bindingslist.select_anchor(list_index)
                    rudisha
                isipokua:  # Create new custom key set based on previously active key set.
                    self.create_new_key_set(new_keyset)
            self.bindingslist.delete(list_index)
            self.bindingslist.insert(list_index, bind_name+' - '+new_keys)
            self.bindingslist.select_set(list_index)
            self.bindingslist.select_anchor(list_index)
            self.keybinding.set(new_keys)
        isipokua:
            self.bindingslist.select_set(list_index)
            self.bindingslist.select_anchor(list_index)

    eleza get_new_keys_name(self, message):
        "Return new key set name kutoka query popup."
        used_names = (idleConf.GetSectionList('user', 'keys') +
                idleConf.GetSectionList('default', 'keys'))
        new_keyset = SectionName(
                self, 'New Custom Key Set', message, used_names).result
        rudisha new_keyset

    eleza save_as_new_key_set(self):
        "Prompt kila name of new key set na save changes using that name."
        new_keys_name = self.get_new_keys_name('New Key Set Name:')
        ikiwa new_keys_name:
            self.create_new_key_set(new_keys_name)

    eleza on_bindingslist_select(self, event):
        "Activate button to assign new keys to selected action."
        self.button_new_keys.state(('!disabled',))

    eleza create_new_key_set(self, new_key_set_name):
        """Create a new custom key set ukijumuisha the given name.

        Copy the bindings/keys kutoka the previously active keyset
        to the new keyset na activate the new custom keyset.
        """
        ikiwa self.keyset_source.get():
            prev_key_set_name = self.builtin_name.get()
        isipokua:
            prev_key_set_name = self.custom_name.get()
        prev_keys = idleConf.GetCoreKeys(prev_key_set_name)
        new_keys = {}
        kila event kwenye prev_keys:  # Add key set to changed items.
            event_name = event[2:-2]  # Trim off the angle brackets.
            binding = ' '.join(prev_keys[event])
            new_keys[event_name] = binding
        # Handle any unsaved changes to prev key set.
        ikiwa prev_key_set_name kwenye changes['keys']:
            key_set_changes = changes['keys'][prev_key_set_name]
            kila event kwenye key_set_changes:
                new_keys[event] = key_set_changes[event]
        # Save the new key set.
        self.save_new_key_set(new_key_set_name, new_keys)
        # Change GUI over to the new key set.
        custom_key_list = idleConf.GetSectionList('user', 'keys')
        custom_key_list.sort()
        self.customlist.SetMenu(custom_key_list, new_key_set_name)
        self.keyset_source.set(0)
        self.set_keys_type()

    eleza load_keys_list(self, keyset_name):
        """Reload the list of action/key binding pairs kila the active key set.

        An action/key binding can be selected to change the key binding.
        """
        reselect = Uongo
        ikiwa self.bindingslist.curselection():
            reselect = Kweli
            list_index = self.bindingslist.index(ANCHOR)
        keyset = idleConf.GetKeySet(keyset_name)
        bind_names = list(keyset.keys())
        bind_names.sort()
        self.bindingslist.delete(0, END)
        kila bind_name kwenye bind_names:
            key = ' '.join(keyset[bind_name])
            bind_name = bind_name[2:-2]  # Trim off the angle brackets.
            ikiwa keyset_name kwenye changes['keys']:
                # Handle any unsaved changes to this key set.
                ikiwa bind_name kwenye changes['keys'][keyset_name]:
                    key = changes['keys'][keyset_name][bind_name]
            self.bindingslist.insert(END, bind_name+' - '+key)
        ikiwa reselect:
            self.bindingslist.see(list_index)
            self.bindingslist.select_set(list_index)
            self.bindingslist.select_anchor(list_index)

    @staticmethod
    eleza save_new_key_set(keyset_name, keyset):
        """Save a newly created core key set.

        Add keyset to idleConf.userCfg['keys'], sio to disk.
        If the keyset doesn't exist, it ni created.  The
        binding/keys are taken kutoka the keyset argument.

        keyset_name - string, the name of the new key set
        keyset - dictionary containing the new keybindings
        """
        ikiwa sio idleConf.userCfg['keys'].has_section(keyset_name):
            idleConf.userCfg['keys'].add_section(keyset_name)
        kila event kwenye keyset:
            value = keyset[event]
            idleConf.userCfg['keys'].SetOption(keyset_name, event, value)

    eleza askyesno(self, *args, **kwargs):
        # Make testing easier.  Could change implementation.
        rudisha messagebox.askyesno(*args, **kwargs)

    eleza delete_custom_keys(self):
        """Handle event to delete a custom key set.

        Applying the delete deactivates the current configuration and
        reverts to the default.  The custom key set ni permanently
        deleted kutoka the config file.
        """
        keyset_name = self.custom_name.get()
        delmsg = 'Are you sure you wish to delete the key set %r ?'
        ikiwa sio self.askyesno(
                'Delete Key Set',  delmsg % keyset_name, parent=self):
            rudisha
        self.cd.deactivate_current_config()
        # Remove key set kutoka changes, config, na file.
        changes.delete_section('keys', keyset_name)
        # Reload user key set list.
        item_list = idleConf.GetSectionList('user', 'keys')
        item_list.sort()
        ikiwa sio item_list:
            self.custom_keyset_on.state(('disabled',))
            self.customlist.SetMenu(item_list, '- no custom keys -')
        isipokua:
            self.customlist.SetMenu(item_list, item_list[0])
        # Revert to default key set.
        self.keyset_source.set(idleConf.defaultCfg['main']
                               .Get('Keys', 'default'))
        self.builtin_name.set(idleConf.defaultCfg['main'].Get('Keys', 'name')
                              ama idleConf.default_keys())
        # User can't back out of these changes, they must be applied now.
        changes.save_all()
        self.cd.save_all_changed_extensions()
        self.cd.activate_config_changes()
        self.set_keys_type()


kundi GenPage(Frame):

    eleza __init__(self, master):
        super().__init__(master)

        self.init_validators()
        self.create_page_general()
        self.load_general_cfg()

    eleza init_validators(self):
        digits_or_empty_re = re.compile(r'[0-9]*')
        eleza is_digits_or_empty(s):
            "Return 's ni blank ama contains only digits'"
            rudisha digits_or_empty_re.fullmatch(s) ni sio Tupu
        self.digits_only = (self.register(is_digits_or_empty), '%P',)

    eleza create_page_general(self):
        """Return frame of widgets kila General tab.

        Enable users to provisionally change general options. Function
        load_general_cfg initializes tk variables na helplist using
        idleConf.  Radiobuttons startup_shell_on na startup_editor_on
        set var startup_edit. Radiobuttons save_ask_on na save_auto_on
        set var autosave. Entry boxes win_width_int na win_height_int
        set var win_width na win_height.  Setting var_name invokes the
        default callback that adds option to changes.

        Helplist: load_general_cfg loads list user_helplist with
        name, position pairs na copies names to listbox helplist.
        Clicking a name invokes help_source selected. Clicking
        button_helplist_name invokes helplist_item_name, which also
        changes user_helplist.  These functions all call
        set_add_delete_state. All but load call update_help_changes to
        rewrite changes['main']['HelpFiles'].

        Widgets kila GenPage(Frame):  (*) widgets bound to self
            frame_window: LabelFrame
                frame_run: Frame
                    startup_title: Label
                    (*)startup_editor_on: Radiobutton - startup_edit
                    (*)startup_shell_on: Radiobutton - startup_edit
                frame_win_size: Frame
                    win_size_title: Label
                    win_width_title: Label
                    (*)win_width_int: Entry - win_width
                    win_height_title: Label
                    (*)win_height_int: Entry - win_height
                frame_autocomplete: Frame
                    auto_wait_title: Label
                    (*)auto_wait_int: Entry - autocomplete_wait
                frame_paren1: Frame
                    paren_style_title: Label
                    (*)paren_style_type: OptionMenu - paren_style
                frame_paren2: Frame
                    paren_time_title: Label
                    (*)paren_flash_time: Entry - flash_delay
                    (*)bell_on: Checkbutton - paren_bell
            frame_editor: LabelFrame
                frame_save: Frame
                    run_save_title: Label
                    (*)save_ask_on: Radiobutton - autosave
                    (*)save_auto_on: Radiobutton - autosave
                frame_format: Frame
                    format_width_title: Label
                    (*)format_width_int: Entry - format_width
                frame_line_numbers_default: Frame
                    line_numbers_default_title: Label
                    (*)line_numbers_default_bool: Checkbutton - line_numbers_default
                frame_context: Frame
                    context_title: Label
                    (*)context_int: Entry - context_lines
            frame_shell: LabelFrame
                frame_auto_squeeze_min_lines: Frame
                    auto_squeeze_min_lines_title: Label
                    (*)auto_squeeze_min_lines_int: Entry - auto_squeeze_min_lines
            frame_help: LabelFrame
                frame_helplist: Frame
                    frame_helplist_buttons: Frame
                        (*)button_helplist_edit
                        (*)button_helplist_add
                        (*)button_helplist_remove
                    (*)helplist: ListBox
                    scroll_helplist: Scrollbar
        """
        # Integer values need StringVar because int('') ashirias.
        self.startup_edit = tracers.add(
                IntVar(self), ('main', 'General', 'editor-on-startup'))
        self.win_width = tracers.add(
                StringVar(self), ('main', 'EditorWindow', 'width'))
        self.win_height = tracers.add(
                StringVar(self), ('main', 'EditorWindow', 'height'))
        self.autocomplete_wait = tracers.add(
                StringVar(self), ('extensions', 'AutoComplete', 'popupwait'))
        self.paren_style = tracers.add(
                StringVar(self), ('extensions', 'ParenMatch', 'style'))
        self.flash_delay = tracers.add(
                StringVar(self), ('extensions', 'ParenMatch', 'flash-delay'))
        self.paren_bell = tracers.add(
                BooleanVar(self), ('extensions', 'ParenMatch', 'bell'))

        self.auto_squeeze_min_lines = tracers.add(
                StringVar(self), ('main', 'PyShell', 'auto-squeeze-min-lines'))

        self.autosave = tracers.add(
                IntVar(self), ('main', 'General', 'autosave'))
        self.format_width = tracers.add(
                StringVar(self), ('extensions', 'FormatParagraph', 'max-width'))
        self.line_numbers_default = tracers.add(
                BooleanVar(self),
                ('main', 'EditorWindow', 'line-numbers-default'))
        self.context_lines = tracers.add(
                StringVar(self), ('extensions', 'CodeContext', 'maxlines'))

        # Create widgets:
        # Section frames.
        frame_window = LabelFrame(self, borderwidth=2, relief=GROOVE,
                                  text=' Window Preferences')
        frame_editor = LabelFrame(self, borderwidth=2, relief=GROOVE,
                                  text=' Editor Preferences')
        frame_shell = LabelFrame(self, borderwidth=2, relief=GROOVE,
                                 text=' Shell Preferences')
        frame_help = LabelFrame(self, borderwidth=2, relief=GROOVE,
                                text=' Additional Help Sources ')
        # Frame_window.
        frame_run = Frame(frame_window, borderwidth=0)
        startup_title = Label(frame_run, text='At Startup')
        self.startup_editor_on = Radiobutton(
                frame_run, variable=self.startup_edit, value=1,
                text="Open Edit Window")
        self.startup_shell_on = Radiobutton(
                frame_run, variable=self.startup_edit, value=0,
                text='Open Shell Window')

        frame_win_size = Frame(frame_window, borderwidth=0)
        win_size_title = Label(
                frame_win_size, text='Initial Window Size  (in characters)')
        win_width_title = Label(frame_win_size, text='Width')
        self.win_width_int = Entry(
                frame_win_size, textvariable=self.win_width, width=3,
                validatecommand=self.digits_only, validate='key',
        )
        win_height_title = Label(frame_win_size, text='Height')
        self.win_height_int = Entry(
                frame_win_size, textvariable=self.win_height, width=3,
                validatecommand=self.digits_only, validate='key',
        )

        frame_autocomplete = Frame(frame_window, borderwidth=0,)
        auto_wait_title = Label(frame_autocomplete,
                               text='Completions Popup Wait (milliseconds)')
        self.auto_wait_int = Entry(frame_autocomplete, width=6,
                                   textvariable=self.autocomplete_wait,
                                   validatecommand=self.digits_only,
                                   validate='key',
                                   )

        frame_paren1 = Frame(frame_window, borderwidth=0)
        paren_style_title = Label(frame_paren1, text='Paren Match Style')
        self.paren_style_type = OptionMenu(
                frame_paren1, self.paren_style, 'expression',
                "opener","parens","expression")
        frame_paren2 = Frame(frame_window, borderwidth=0)
        paren_time_title = Label(
                frame_paren2, text='Time Match Displayed (milliseconds)\n'
                                  '(0 ni until next input)')
        self.paren_flash_time = Entry(
                frame_paren2, textvariable=self.flash_delay, width=6)
        self.bell_on = Checkbutton(
                frame_paren2, text="Bell on Mismatch", variable=self.paren_bell)

        # Frame_editor.
        frame_save = Frame(frame_editor, borderwidth=0)
        run_save_title = Label(frame_save, text='At Start of Run (F5)  ')
        self.save_ask_on = Radiobutton(
                frame_save, variable=self.autosave, value=0,
                text="Prompt to Save")
        self.save_auto_on = Radiobutton(
                frame_save, variable=self.autosave, value=1,
                text='No Prompt')

        frame_format = Frame(frame_editor, borderwidth=0)
        format_width_title = Label(frame_format,
                                   text='Format Paragraph Max Width')
        self.format_width_int = Entry(
                frame_format, textvariable=self.format_width, width=4,
                validatecommand=self.digits_only, validate='key',
        )

        frame_line_numbers_default = Frame(frame_editor, borderwidth=0)
        line_numbers_default_title = Label(
            frame_line_numbers_default, text='Show line numbers kwenye new windows')
        self.line_numbers_default_bool = Checkbutton(
                frame_line_numbers_default,
                variable=self.line_numbers_default,
                width=1)

        frame_context = Frame(frame_editor, borderwidth=0)
        context_title = Label(frame_context, text='Max Context Lines :')
        self.context_int = Entry(
                frame_context, textvariable=self.context_lines, width=3,
                validatecommand=self.digits_only, validate='key',
        )

        # Frame_shell.
        frame_auto_squeeze_min_lines = Frame(frame_shell, borderwidth=0)
        auto_squeeze_min_lines_title = Label(frame_auto_squeeze_min_lines,
                                             text='Auto-Squeeze Min. Lines:')
        self.auto_squeeze_min_lines_int = Entry(
                frame_auto_squeeze_min_lines, width=4,
                textvariable=self.auto_squeeze_min_lines,
                validatecommand=self.digits_only, validate='key',
        )

        # frame_help.
        frame_helplist = Frame(frame_help)
        frame_helplist_buttons = Frame(frame_helplist)
        self.helplist = Listbox(
                frame_helplist, height=5, takefocus=Kweli,
                exportselection=FALSE)
        scroll_helplist = Scrollbar(frame_helplist)
        scroll_helplist['command'] = self.helplist.yview
        self.helplist['yscrollcommand'] = scroll_helplist.set
        self.helplist.bind('<ButtonRelease-1>', self.help_source_selected)
        self.button_helplist_edit = Button(
                frame_helplist_buttons, text='Edit', state='disabled',
                width=8, command=self.helplist_item_edit)
        self.button_helplist_add = Button(
                frame_helplist_buttons, text='Add',
                width=8, command=self.helplist_item_add)
        self.button_helplist_remove = Button(
                frame_helplist_buttons, text='Remove', state='disabled',
                width=8, command=self.helplist_item_remove)

        # Pack widgets:
        # Body.
        frame_window.pack(side=TOP, padx=5, pady=5, expand=TRUE, fill=BOTH)
        frame_editor.pack(side=TOP, padx=5, pady=5, expand=TRUE, fill=BOTH)
        frame_shell.pack(side=TOP, padx=5, pady=5, expand=TRUE, fill=BOTH)
        frame_help.pack(side=TOP, padx=5, pady=5, expand=TRUE, fill=BOTH)
        # frame_run.
        frame_run.pack(side=TOP, padx=5, pady=0, fill=X)
        startup_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.startup_shell_on.pack(side=RIGHT, anchor=W, padx=5, pady=5)
        self.startup_editor_on.pack(side=RIGHT, anchor=W, padx=5, pady=5)
        # frame_win_size.
        frame_win_size.pack(side=TOP, padx=5, pady=0, fill=X)
        win_size_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.win_height_int.pack(side=RIGHT, anchor=E, padx=10, pady=5)
        win_height_title.pack(side=RIGHT, anchor=E, pady=5)
        self.win_width_int.pack(side=RIGHT, anchor=E, padx=10, pady=5)
        win_width_title.pack(side=RIGHT, anchor=E, pady=5)
        # frame_autocomplete.
        frame_autocomplete.pack(side=TOP, padx=5, pady=0, fill=X)
        auto_wait_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.auto_wait_int.pack(side=TOP, padx=10, pady=5)
        # frame_paren.
        frame_paren1.pack(side=TOP, padx=5, pady=0, fill=X)
        paren_style_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.paren_style_type.pack(side=TOP, padx=10, pady=5)
        frame_paren2.pack(side=TOP, padx=5, pady=0, fill=X)
        paren_time_title.pack(side=LEFT, anchor=W, padx=5)
        self.bell_on.pack(side=RIGHT, anchor=E, padx=15, pady=5)
        self.paren_flash_time.pack(side=TOP, anchor=W, padx=15, pady=5)

        # frame_save.
        frame_save.pack(side=TOP, padx=5, pady=0, fill=X)
        run_save_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.save_auto_on.pack(side=RIGHT, anchor=W, padx=5, pady=5)
        self.save_ask_on.pack(side=RIGHT, anchor=W, padx=5, pady=5)
        # frame_format.
        frame_format.pack(side=TOP, padx=5, pady=0, fill=X)
        format_width_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.format_width_int.pack(side=TOP, padx=10, pady=5)
        # frame_line_numbers_default.
        frame_line_numbers_default.pack(side=TOP, padx=5, pady=0, fill=X)
        line_numbers_default_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.line_numbers_default_bool.pack(side=LEFT, padx=5, pady=5)
        # frame_context.
        frame_context.pack(side=TOP, padx=5, pady=0, fill=X)
        context_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.context_int.pack(side=TOP, padx=5, pady=5)

        # frame_auto_squeeze_min_lines
        frame_auto_squeeze_min_lines.pack(side=TOP, padx=5, pady=0, fill=X)
        auto_squeeze_min_lines_title.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.auto_squeeze_min_lines_int.pack(side=TOP, padx=5, pady=5)

        # frame_help.
        frame_helplist_buttons.pack(side=RIGHT, padx=5, pady=5, fill=Y)
        frame_helplist.pack(side=TOP, padx=5, pady=5, expand=TRUE, fill=BOTH)
        scroll_helplist.pack(side=RIGHT, anchor=W, fill=Y)
        self.helplist.pack(side=LEFT, anchor=E, expand=TRUE, fill=BOTH)
        self.button_helplist_edit.pack(side=TOP, anchor=W, pady=5)
        self.button_helplist_add.pack(side=TOP, anchor=W)
        self.button_helplist_remove.pack(side=TOP, anchor=W, pady=5)

    eleza load_general_cfg(self):
        "Load current configuration settings kila the general options."
        # Set variables kila all windows.
        self.startup_edit.set(idleConf.GetOption(
                'main', 'General', 'editor-on-startup', type='bool'))
        self.win_width.set(idleConf.GetOption(
                'main', 'EditorWindow', 'width', type='int'))
        self.win_height.set(idleConf.GetOption(
                'main', 'EditorWindow', 'height', type='int'))
        self.autocomplete_wait.set(idleConf.GetOption(
                'extensions', 'AutoComplete', 'popupwait', type='int'))
        self.paren_style.set(idleConf.GetOption(
                'extensions', 'ParenMatch', 'style'))
        self.flash_delay.set(idleConf.GetOption(
                'extensions', 'ParenMatch', 'flash-delay', type='int'))
        self.paren_bell.set(idleConf.GetOption(
                'extensions', 'ParenMatch', 'bell'))

        # Set variables kila editor windows.
        self.autosave.set(idleConf.GetOption(
                'main', 'General', 'autosave', default=0, type='bool'))
        self.format_width.set(idleConf.GetOption(
                'extensions', 'FormatParagraph', 'max-width', type='int'))
        self.line_numbers_default.set(idleConf.GetOption(
                'main', 'EditorWindow', 'line-numbers-default', type='bool'))
        self.context_lines.set(idleConf.GetOption(
                'extensions', 'CodeContext', 'maxlines', type='int'))

        # Set variables kila shell windows.
        self.auto_squeeze_min_lines.set(idleConf.GetOption(
                'main', 'PyShell', 'auto-squeeze-min-lines', type='int'))

        # Set additional help sources.
        self.user_helplist = idleConf.GetAllExtraHelpSourcesList()
        self.helplist.delete(0, 'end')
        kila help_item kwenye self.user_helplist:
            self.helplist.insert(END, help_item[0])
        self.set_add_delete_state()

    eleza help_source_selected(self, event):
        "Handle event kila selecting additional help."
        self.set_add_delete_state()

    eleza set_add_delete_state(self):
        "Toggle the state kila the help list buttons based on list entries."
        ikiwa self.helplist.size() < 1:  # No entries kwenye list.
            self.button_helplist_edit.state(('disabled',))
            self.button_helplist_remove.state(('disabled',))
        isipokua:  # Some entries.
            ikiwa self.helplist.curselection():  # There currently ni a selection.
                self.button_helplist_edit.state(('!disabled',))
                self.button_helplist_remove.state(('!disabled',))
            isipokua:  # There currently ni sio a selection.
                self.button_helplist_edit.state(('disabled',))
                self.button_helplist_remove.state(('disabled',))

    eleza helplist_item_add(self):
        """Handle add button kila the help list.

        Query kila name na location of new help sources na add
        them to the list.
        """
        help_source = HelpSource(self, 'New Help Source').result
        ikiwa help_source:
            self.user_helplist.append(help_source)
            self.helplist.insert(END, help_source[0])
            self.update_help_changes()

    eleza helplist_item_edit(self):
        """Handle edit button kila the help list.

        Query ukijumuisha existing help source information na update
        config ikiwa the values are changed.
        """
        item_index = self.helplist.index(ANCHOR)
        help_source = self.user_helplist[item_index]
        new_help_source = HelpSource(
                self, 'Edit Help Source',
                menuitem=help_source[0],
                filepath=help_source[1],
                ).result
        ikiwa new_help_source na new_help_source != help_source:
            self.user_helplist[item_index] = new_help_source
            self.helplist.delete(item_index)
            self.helplist.insert(item_index, new_help_source[0])
            self.update_help_changes()
            self.set_add_delete_state()  # Selected will be un-selected

    eleza helplist_item_remove(self):
        """Handle remove button kila the help list.

        Delete the help list item kutoka config.
        """
        item_index = self.helplist.index(ANCHOR)
        del(self.user_helplist[item_index])
        self.helplist.delete(item_index)
        self.update_help_changes()
        self.set_add_delete_state()

    eleza update_help_changes(self):
        "Clear na rebuild the HelpFiles section kwenye changes"
        changes['main']['HelpFiles'] = {}
        kila num kwenye range(1, len(self.user_helplist) + 1):
            changes.add_option(
                    'main', 'HelpFiles', str(num),
                    ';'.join(self.user_helplist[num-1][:2]))


kundi VarTrace:
    """Maintain Tk variables trace state."""

    eleza __init__(self):
        """Store Tk variables na callbacks.

        untraced: List of tuples (var, callback)
            that do sio have the callback attached
            to the Tk var.
        traced: List of tuples (var, callback) where
            that callback has been attached to the var.
        """
        self.untraced = []
        self.traced = []

    eleza clear(self):
        "Clear lists (kila tests)."
        # Call after all tests kwenye a module to avoid memory leaks.
        self.untraced.clear()
        self.traced.clear()

    eleza add(self, var, callback):
        """Add (var, callback) tuple to untraced list.

        Args:
            var: Tk variable instance.
            callback: Either function name to be used kama a callback
                ama a tuple ukijumuisha IdleConf config-type, section, and
                option names used kwenye the default callback.

        Return:
            Tk variable instance.
        """
        ikiwa isinstance(callback, tuple):
            callback = self.make_callback(var, callback)
        self.untraced.append((var, callback))
        rudisha var

    @staticmethod
    eleza make_callback(var, config):
        "Return default callback function to add values to changes instance."
        eleza default_callback(*params):
            "Add config values to changes instance."
            changes.add_option(*config, var.get())
        rudisha default_callback

    eleza attach(self):
        "Attach callback to all vars that are sio traced."
        wakati self.untraced:
            var, callback = self.untraced.pop()
            var.trace_add('write', callback)
            self.traced.append((var, callback))

    eleza detach(self):
        "Remove callback kutoka traced vars."
        wakati self.traced:
            var, callback = self.traced.pop()
            var.trace_remove('write', var.trace_info()[0][1])
            self.untraced.append((var, callback))


tracers = VarTrace()

help_common = '''\
When you click either the Apply ama Ok buttons, settings kwenye this
dialog that are different kutoka IDLE's default are saved in
a .idlerc directory kwenye your home directory. Except kama noted,
these changes apply to all versions of IDLE installed on this
machine. [Cancel] only cancels changes made since the last save.
'''
help_pages = {
    'Fonts/Tabs':'''
Font sample: This shows what a selection of Basic Multilingual Plane
unicode characters look like kila the current font selection.  If the
selected font does sio define a character, Tk attempts to find another
font that does.  Substitute glyphs depend on what ni available on a
particular system na will sio necessarily have the same size kama the
font selected.  Line contains 20 characters up to Devanagari, 14 for
Tamil, na 10 kila East Asia.

Hebrew na Arabic letters should display right to left, starting with
alef, \u05d0 na \u0627.  Arabic digits display left to right.  The
Devanagari na Tamil lines start ukijumuisha digits.  The East Asian lines
are Chinese digits, Chinese Hanzi, Korean Hangul, na Japanese
Hiragana na Katakana.

You can edit the font sample. Changes remain until IDLE ni closed.
''',
    'Highlights': '''
Highlighting:
The IDLE Dark color theme ni new kwenye October 2015.  It can only
be used ukijumuisha older IDLE releases ikiwa it ni saved kama a custom
theme, ukijumuisha a different name.
''',
    'Keys': '''
Keys:
The IDLE Modern Unix key set ni new kwenye June 2016.  It can only
be used ukijumuisha older IDLE releases ikiwa it ni saved kama a custom
key set, ukijumuisha a different name.
''',
     'General': '''
General:

AutoComplete: Popupwait ni milliseconds to wait after key char, without
cursor movement, before popping up completion box.  Key char ni '.' after
identifier ama a '/' (or '\\' on Windows) within a string.

FormatParagraph: Max-width ni max chars kwenye lines after re-formatting.
Use ukijumuisha paragraphs kwenye both strings na comment blocks.

ParenMatch: Style indicates what ni highlighted when closer ni entered:
'opener' - opener '({[' corresponding to closer; 'parens' - both chars;
'expression' (default) - also everything kwenye between.  Flash-delay ni how
long to highlight ikiwa cursor ni sio moved (0 means forever).

CodeContext: Maxlines ni the maximum number of code context lines to
display when Code Context ni turned on kila an editor window.

Shell Preferences: Auto-Squeeze Min. Lines ni the minimum number of lines
of output to automatically "squeeze".
'''
}


eleza is_int(s):
    "Return 's ni blank ama represents an int'"
    ikiwa sio s:
        rudisha Kweli
    jaribu:
        int(s)
        rudisha Kweli
    tatizo ValueError:
        rudisha Uongo


kundi VerticalScrolledFrame(Frame):
    """A pure Tkinter vertically scrollable frame.

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct na pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    eleza __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object na a vertical scrollbar kila scrolling it.
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, borderwidth=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set, width=240)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view.
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled ukijumuisha it.
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)

        # Track changes to the canvas na frame width na sync them,
        # also updating the scrollbar.
        eleza _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
        interior.bind('<Configure>', _configure_interior)

        eleza _configure_canvas(event):
            ikiwa interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        rudisha


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_configdialog', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(ConfigDialog)
