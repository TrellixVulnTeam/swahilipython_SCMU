"""
Dialog kila building Tkinter accelerator key bindings
"""
kutoka tkinter agiza Toplevel, Listbox, Text, StringVar, TclError
kutoka tkinter.ttk agiza Frame, Button, Checkbutton, Entry, Label, Scrollbar
kutoka tkinter agiza messagebox
agiza string
agiza sys


FUNCTION_KEYS = ('F1', 'F2' ,'F3' ,'F4' ,'F5' ,'F6',
                 'F7', 'F8' ,'F9' ,'F10' ,'F11' ,'F12')
ALPHANUM_KEYS = tuple(string.ascii_lowercase + string.digits)
PUNCTUATION_KEYS = tuple('~!@#%^&*()_-+={}[]|;:,.<>/?')
WHITESPACE_KEYS = ('Tab', 'Space', 'Return')
EDIT_KEYS = ('BackSpace', 'Delete', 'Insert')
MOVE_KEYS = ('Home', 'End', 'Page Up', 'Page Down', 'Left Arrow',
             'Right Arrow', 'Up Arrow', 'Down Arrow')
AVAILABLE_KEYS = (ALPHANUM_KEYS + PUNCTUATION_KEYS + FUNCTION_KEYS +
                  WHITESPACE_KEYS + EDIT_KEYS + MOVE_KEYS)


eleza translate_key(key, modifiers):
    "Translate kutoka keycap symbol to the Tkinter keysym."
    mapping = {'Space':'space',
            '~':'asciitilde', '!':'exclam', '@':'at', '#':'numbersign',
            '%':'percent', '^':'asciicircum', '&':'ampersand',
            '*':'asterisk', '(':'parenleft', ')':'parenright',
            '_':'underscore', '-':'minus', '+':'plus', '=':'equal',
            '{':'braceleft', '}':'braceright',
            '[':'bracketleft', ']':'bracketright', '|':'bar',
            ';':'semicolon', ':':'colon', ',':'comma', '.':'period',
            '<':'less', '>':'greater', '/':'slash', '?':'question',
            'Page Up':'Prior', 'Page Down':'Next',
            'Left Arrow':'Left', 'Right Arrow':'Right',
            'Up Arrow':'Up', 'Down Arrow': 'Down', 'Tab':'Tab'}
    key = mapping.get(key, key)
    ikiwa 'Shift' kwenye modifiers na key kwenye string.ascii_lowercase:
        key = key.upper()
    rudisha f'Key-{key}'


kundi GetKeysDialog(Toplevel):

    # Dialog title kila invalid key sequence
    keyerror_title = 'Key Sequence Error'

    eleza __init__(self, parent, title, action, current_key_sequences,
                 *, _htest=Uongo, _utest=Uongo):
        """
        parent - parent of this dialog
        title - string which ni the title of the popup dialog
        action - string, the name of the virtual event these keys will be
                 mapped to
        current_key_sequences - list, a list of all key sequence lists
                 currently mapped to virtual events, kila overlap checking
        _htest - bool, change box location when running htest
        _utest - bool, do sio wait when running unittest
        """
        Toplevel.__init__(self, parent)
        self.withdraw()  # Hide wakati setting geometry.
        self.configure(borderwidth=5)
        self.resizable(height=Uongo, width=Uongo)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.parent = parent
        self.action = action
        self.current_key_sequences = current_key_sequences
        self.result = ''
        self.key_string = StringVar(self)
        self.key_string.set('')
        # Set self.modifiers, self.modifier_label.
        self.set_modifiers_for_platform()
        self.modifier_vars = []
        kila modifier kwenye self.modifiers:
            variable = StringVar(self)
            variable.set('')
            self.modifier_vars.append(variable)
        self.advanced = Uongo
        self.create_widgets()
        self.update_idletasks()
        self.geometry(
                "+%d+%d" % (
                    parent.winfo_rootx() +
                    (parent.winfo_width()/2 - self.winfo_reqwidth()/2),
                    parent.winfo_rooty() +
                    ((parent.winfo_height()/2 - self.winfo_reqheight()/2)
                    ikiwa sio _htest isipokua 150)
                ) )  # Center dialog over parent (or below htest box).
        ikiwa sio _utest:
            self.deiconify()  # Geometry set, unhide.
            self.wait_window()

    eleza showerror(self, *args, **kwargs):
        # Make testing easier.  Replace kwenye #30751.
        messagebox.showerror(*args, **kwargs)

    eleza create_widgets(self):
        self.frame = frame = Frame(self, borderwidth=2, relief='sunken')
        frame.pack(side='top', expand=Kweli, fill='both')

        frame_buttons = Frame(self)
        frame_buttons.pack(side='bottom', fill='x')

        self.button_ok = Button(frame_buttons, text='OK',
                                width=8, command=self.ok)
        self.button_ok.grid(row=0, column=0, padx=5, pady=5)
        self.button_cancel = Button(frame_buttons, text='Cancel',
                                   width=8, command=self.cancel)
        self.button_cancel.grid(row=0, column=1, padx=5, pady=5)

        # Basic entry key sequence.
        self.frame_keyseq_basic = Frame(frame, name='keyseq_basic')
        self.frame_keyseq_basic.grid(row=0, column=0, sticky='nsew',
                                      padx=5, pady=5)
        basic_title = Label(self.frame_keyseq_basic,
                            text=f"New keys kila '{self.action}' :")
        basic_title.pack(anchor='w')

        basic_keys = Label(self.frame_keyseq_basic, justify='left',
                           textvariable=self.key_string, relief='groove',
                           borderwidth=2)
        basic_keys.pack(ipadx=5, ipady=5, fill='x')

        # Basic entry controls.
        self.frame_controls_basic = Frame(frame)
        self.frame_controls_basic.grid(row=1, column=0, sticky='nsew', padx=5)

        # Basic entry modifiers.
        self.modifier_checkbuttons = {}
        column = 0
        kila modifier, variable kwenye zip(self.modifiers, self.modifier_vars):
            label = self.modifier_label.get(modifier, modifier)
            check = Checkbutton(self.frame_controls_basic,
                                command=self.build_key_string, text=label,
                                variable=variable, onvalue=modifier, offvalue='')
            check.grid(row=0, column=column, padx=2, sticky='w')
            self.modifier_checkbuttons[modifier] = check
            column += 1

        # Basic entry help text.
        help_basic = Label(self.frame_controls_basic, justify='left',
                           text="Select the desired modifier keys\n"+
                                "above, na the final key kutoka the\n"+
                                "list on the right.\n\n" +
                                "Use upper case Symbols when using\n" +
                                "the Shift modifier.  (Letters will be\n" +
                                "converted automatically.)")
        help_basic.grid(row=1, column=0, columnspan=4, padx=2, sticky='w')

        # Basic entry key list.
        self.list_keys_final = Listbox(self.frame_controls_basic, width=15,
                                       height=10, selectmode='single')
        self.list_keys_final.insert('end', *AVAILABLE_KEYS)
        self.list_keys_final.bind('<ButtonRelease-1>', self.final_key_selected)
        self.list_keys_final.grid(row=0, column=4, rowspan=4, sticky='ns')
        scroll_keys_final = Scrollbar(self.frame_controls_basic,
                                      orient='vertical',
                                      command=self.list_keys_final.yview)
        self.list_keys_final.config(yscrollcommand=scroll_keys_final.set)
        scroll_keys_final.grid(row=0, column=5, rowspan=4, sticky='ns')
        self.button_clear = Button(self.frame_controls_basic,
                                   text='Clear Keys',
                                   command=self.clear_key_seq)
        self.button_clear.grid(row=2, column=0, columnspan=4)

        # Advanced entry key sequence.
        self.frame_keyseq_advanced = Frame(frame, name='keyseq_advanced')
        self.frame_keyseq_advanced.grid(row=0, column=0, sticky='nsew',
                                         padx=5, pady=5)
        advanced_title = Label(self.frame_keyseq_advanced, justify='left',
                               text=f"Enter new binding(s) kila '{self.action}' :\n" +
                                     "(These bindings will sio be checked kila validity!)")
        advanced_title.pack(anchor='w')
        self.advanced_keys = Entry(self.frame_keyseq_advanced,
                                   textvariable=self.key_string)
        self.advanced_keys.pack(fill='x')

        # Advanced entry help text.
        self.frame_help_advanced = Frame(frame)
        self.frame_help_advanced.grid(row=1, column=0, sticky='nsew', padx=5)
        help_advanced = Label(self.frame_help_advanced, justify='left',
            text="Key bindings are specified using Tkinter keysyms as\n"+
                 "in these samples: <Control-f>, <Shift-F2>, <F12>,\n"
                 "<Control-space>, <Meta-less>, <Control-Alt-Shift-X>.\n"
                 "Upper case ni used when the Shift modifier ni present!\n\n" +
                 "'Emacs style' multi-keystroke bindings are specified as\n" +
                 "follows: <Control-x><Control-y>, where the first key\n" +
                 "is the 'do-nothing' keybinding.\n\n" +
                 "Multiple separate bindings kila one action should be\n"+
                 "separated by a space, eg., <Alt-v> <Meta-v>." )
        help_advanced.grid(row=0, column=0, sticky='nsew')

        # Switch between basic na advanced.
        self.button_level = Button(frame, command=self.toggle_level,
                                  text='<< Basic Key Binding Entry')
        self.button_level.grid(row=2, column=0, stick='ew', padx=5, pady=5)
        self.toggle_level()

    eleza set_modifiers_for_platform(self):
        """Determine list of names of key modifiers kila this platform.

        The names are used to build Tk bindings -- it doesn't matter ikiwa the
        keyboard has these keys; it matters ikiwa Tk understands them.  The
        order ni also important: key binding equality depends on it, so
        config-keys.eleza must use the same ordering.
        """
        ikiwa sys.platform == "darwin":
            self.modifiers = ['Shift', 'Control', 'Option', 'Command']
        isipokua:
            self.modifiers = ['Control', 'Alt', 'Shift']
        self.modifier_label = {'Control': 'Ctrl'}  # Short name.

    eleza toggle_level(self):
        "Toggle between basic na advanced keys."
        ikiwa  self.button_level.cget('text').startswith('Advanced'):
            self.clear_key_seq()
            self.button_level.config(text='<< Basic Key Binding Entry')
            self.frame_keyseq_advanced.lift()
            self.frame_help_advanced.lift()
            self.advanced_keys.focus_set()
            self.advanced = Kweli
        isipokua:
            self.clear_key_seq()
            self.button_level.config(text='Advanced Key Binding Entry >>')
            self.frame_keyseq_basic.lift()
            self.frame_controls_basic.lift()
            self.advanced = Uongo

    eleza final_key_selected(self, event=Tupu):
        "Handler kila clicking on key kwenye basic settings list."
        self.build_key_string()

    eleza build_key_string(self):
        "Create formatted string of modifiers plus the key."
        keylist = modifiers = self.get_modifiers()
        final_key = self.list_keys_final.get('anchor')
        ikiwa final_key:
            final_key = translate_key(final_key, modifiers)
            keylist.append(final_key)
        self.key_string.set(f"<{'-'.join(keylist)}>")

    eleza get_modifiers(self):
        "Return ordered list of modifiers that have been selected."
        mod_list = [variable.get() kila variable kwenye self.modifier_vars]
        rudisha [mod kila mod kwenye mod_list ikiwa mod]

    eleza clear_key_seq(self):
        "Clear modifiers na keys selection."
        self.list_keys_final.select_clear(0, 'end')
        self.list_keys_final.yview('moveto', '0.0')
        kila variable kwenye self.modifier_vars:
            variable.set('')
        self.key_string.set('')

    eleza ok(self, event=Tupu):
        keys = self.key_string.get().strip()
        ikiwa sio keys:
            self.showerror(title=self.keyerror_title, parent=self,
                           message="No key specified.")
            rudisha
        ikiwa (self.advanced ama self.keys_ok(keys)) na self.bind_ok(keys):
            self.result = keys
        self.grab_release()
        self.destroy()

    eleza cancel(self, event=Tupu):
        self.result = ''
        self.grab_release()
        self.destroy()

    eleza keys_ok(self, keys):
        """Validity check on user's 'basic' keybinding selection.

        Doesn't check the string produced by the advanced dialog because
        'modifiers' isn't set.
        """
        final_key = self.list_keys_final.get('anchor')
        modifiers = self.get_modifiers()
        title = self.keyerror_title
        key_sequences = [key kila keylist kwenye self.current_key_sequences
                             kila key kwenye keylist]
        ikiwa sio keys.endswith('>'):
            self.showerror(title, parent=self,
                           message='Missing the final Key')
        lasivyo (sio modifiers
              na final_key haiko kwenye FUNCTION_KEYS + MOVE_KEYS):
            self.showerror(title=title, parent=self,
                           message='No modifier key(s) specified.')
        lasivyo (modifiers == ['Shift']) \
                 na (final_key haiko kwenye
                      FUNCTION_KEYS + MOVE_KEYS + ('Tab', 'Space')):
            msg = 'The shift modifier by itself may sio be used with'\
                  ' this key symbol.'
            self.showerror(title=title, parent=self, message=msg)
        lasivyo keys kwenye key_sequences:
            msg = 'This key combination ni already kwenye use.'
            self.showerror(title=title, parent=self, message=msg)
        isipokua:
            rudisha Kweli
        rudisha Uongo

    eleza bind_ok(self, keys):
        "Return Kweli ikiwa Tcl accepts the new keys isipokua show message."
        jaribu:
            binding = self.bind(keys, lambda: Tupu)
        tatizo TclError kama err:
            self.showerror(
                    title=self.keyerror_title, parent=self,
                    message=(f'The entered key sequence ni sio accepted.\n\n'
                             f'Error: {err}'))
            rudisha Uongo
        isipokua:
            self.unbind(keys, binding)
            rudisha Kweli


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_config_key', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(GetKeysDialog)
