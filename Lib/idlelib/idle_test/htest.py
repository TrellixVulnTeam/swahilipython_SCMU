'''Run human tests of Idle's window, dialog, na popup widgets.

run(*tests)
Create a master Tk window.  Within that, run each callable kwenye tests
after finding the matching test spec kwenye this file.  If tests ni empty,
run an htest kila each spec dict kwenye this file after finding the matching
callable kwenye the module named kwenye the spec.  Close the window to skip ama
end the test.

In a tested module, let X be a global name bound to a callable (class
or function) whose .__name__ attribute ni also X (the usual situation).
The first parameter of X must be 'parent'.  When called, the parent
argument will be the root window.  X must create a child Toplevel
window (or subkundi thereof).  The Toplevel may be a test widget ama
dialog, kwenye which case the callable ni the corresponding class.  Or the
Toplevel may contain the widget to be tested ama set up a context in
which a test widget ni invoked.  In this latter case, the callable ni a
wrapper function that sets up the Toplevel na other objects.  Wrapper
function names, such kama _editor_window', should start ukijumuisha '_'.


End the module with

ikiwa __name__ == '__main__':
    <unittest, ikiwa there ni one>
    kutoka idlelib.idle_test.htest agiza run
    run(X)

To have wrapper functions na test invocation code ignored by coveragepy
reports, put '# htest #' on the eleza statement header line.

eleza _wrapper(parent):  # htest #

Also make sure that the 'ikiwa __name__' line matches the above.  Then have
make sure that .coveragerc includes the following.

[report]
exclude_lines =
    .*# htest #
    ikiwa __name__ == .__main__.:

(The "." instead of "'" ni intentional na necessary.)


To run any X, this file must contain a matching instance of the
following template, ukijumuisha X.__name__ prepended to '_spec'.
When all tests are run, the prefix ni use to get X.

_spec = {
    'file': '',
    'kwds': {'title': ''},
    'msg': ""
    }

file (no .py): run() agizas file.py.
kwds: augmented ukijumuisha {'parent':root} na pitaed to X kama **kwds.
title: an example kwd; some widgets need this, delete ikiwa not.
msg: master window hints about testing the widget.


Modules na classes sio being tested at the moment:
pyshell.PyShellEditorWindow
debugger.Debugger
autocomplete_w.AutoCompleteWindow
outwin.OutputWindow (indirectly being tested ukijumuisha grep test)
'''

agiza idlelib.pyshell  # Set Windows DPI awareness before Tk().
kutoka importlib agiza import_module
agiza textwrap
agiza tkinter kama tk
kutoka tkinter.ttk agiza Scrollbar
tk.NoDefaultRoot()

AboutDialog_spec = {
    'file': 'help_about',
    'kwds': {'title': 'help_about test',
             '_htest': Kweli,
             },
    'msg': "Test every button. Ensure Python, TK na IDLE versions "
           "are correctly displayed.\n [Close] to exit.",
    }

# TODO implement ^\; adding '<Control-Key-\\>' to function does sio work.
_calltip_window_spec = {
    'file': 'calltip_w',
    'kwds': {},
    'msg': "Typing '(' should display a calltip.\n"
           "Typing ') should hide the calltip.\n"
           "So should moving cursor out of argument area.\n"
           "Force-open-calltip does sio work here.\n"
    }

_module_browser_spec = {
    'file': 'browser',
    'kwds': {},
    'msg': "Inspect names of module, class(ukijumuisha superkundi ikiwa "
           "applicable), methods na functions.\nToggle nested items.\n"
           "Double clicking on items prints a traceback kila an exception "
           "that ni ignored."
    }

_color_delegator_spec = {
    'file': 'colorizer',
    'kwds': {},
    'msg': "The text ni sample Python code.\n"
           "Ensure components like comments, keywords, builtins,\n"
           "string, definitions, na koma are correctly colored.\n"
           "The default color scheme ni kwenye idlelib/config-highlight.def"
    }

CustomRun_spec = {
    'file': 'query',
    'kwds': {'title': 'Customize query.py Run',
             '_htest': Kweli},
    'msg': "Enter ukijumuisha <Return> ama [Run].  Print valid entry to Shell\n"
           "Arguments are parsed into a list\n"
           "Mode ni currently restart Kweli ama Uongo\n"
           "Close dialog ukijumuisha valid entry, <Escape>, [Cancel], [X]"
    }

ConfigDialog_spec = {
    'file': 'configdialog',
    'kwds': {'title': 'ConfigDialogTest',
             '_htest': Kweli,},
    'msg': "IDLE preferences dialog.\n"
           "In the 'Fonts/Tabs' tab, changing font face, should update the "
           "font face of the text kwenye the area below it.\nIn the "
           "'Highlighting' tab, try different color schemes. Clicking "
           "items kwenye the sample program should update the choices above it."
           "\nIn the 'Keys', 'General' na 'Extensions' tabs, test settings "
           "of interest."
           "\n[Ok] to close the dialog.[Apply] to apply the settings na "
           "and [Cancel] to revert all changes.\nRe-run the test to ensure "
           "changes made have persisted."
    }

# TODO Improve message
_dyn_option_menu_spec = {
    'file': 'dynoption',
    'kwds': {},
    'msg': "Select one of the many options kwenye the 'old option set'.\n"
           "Click the button to change the option set.\n"
           "Select one of the many options kwenye the 'new option set'."
    }

# TODO edit wrapper
_editor_window_spec = {
   'file': 'editor',
    'kwds': {},
    'msg': "Test editor functions of interest.\n"
           "Best to close editor first."
    }

GetKeysDialog_spec = {
    'file': 'config_key',
    'kwds': {'title': 'Test keybindings',
             'action': 'find-again',
             'current_key_sequences': [['<Control-Key-g>', '<Key-F3>', '<Control-Key-G>']],
             '_htest': Kweli,
             },
    'msg': "Test kila different key modifier sequences.\n"
           "<nothing> ni invalid.\n"
           "No modifier key ni invalid.\n"
           "Shift key ukijumuisha [a-z],[0-9], function key, move key, tab, space "
           "is invalid.\nNo validity checking ikiwa advanced key binding "
           "entry ni used."
    }

_grep_dialog_spec = {
    'file': 'grep',
    'kwds': {},
    'msg': "Click the 'Show GrepDialog' button.\n"
           "Test the various 'Find-in-files' functions.\n"
           "The results should be displayed kwenye a new '*Output*' window.\n"
           "'Right-click'->'Go to file/line' anywhere kwenye the search results "
           "should open that file \nin a new EditorWindow."
    }

HelpSource_spec = {
    'file': 'query',
    'kwds': {'title': 'Help name na source',
             'menuitem': 'test',
             'filepath': __file__,
             'used_names': {'abc'},
             '_htest': Kweli},
    'msg': "Enter menu item name na help file path\n"
           "'', > than 30 chars, na 'abc' are invalid menu item names.\n"
           "'' na file does sio exist are invalid path items.\n"
           "Any url ('www...', 'http...') ni accepted.\n"
           "Test Browse ukijumuisha na without path, kama cannot unittest.\n"
           "[Ok] ama <Return> prints valid entry to shell\n"
           "[Cancel] ama <Escape> prints Tupu to shell"
    }

_io_binding_spec = {
    'file': 'iomenu',
    'kwds': {},
    'msg': "Test the following bindings.\n"
           "<Control-o> to open file kutoka dialog.\n"
           "Edit the file.\n"
           "<Control-p> to print the file.\n"
           "<Control-s> to save the file.\n"
           "<Alt-s> to save-as another file.\n"
           "<Control-c> to save-copy-as another file.\n"
           "Check that changes were saved by opening the file elsewhere."
    }

_linenumbers_drag_scrolling_spec = {
    'file': 'sidebar',
    'kwds': {},
    'msg': textwrap.dedent("""\
        1. Click on the line numbers na drag down below the edge of the
        window, moving the mouse a bit na then leaving it there kila a while.
        The text na line numbers should gradually scroll down, ukijumuisha the
        selection updated continuously.

        2. With the lines still selected, click on a line number above the
        selected lines. Only the line whose number was clicked should be
        selected.

        3. Repeat step #1, dragging to above the window. The text na line
        numbers should gradually scroll up, ukijumuisha the selection updated
        continuously.

        4. Repeat step #2, clicking a line number below the selection."""),
    }

_multi_call_spec = {
    'file': 'multicall',
    'kwds': {},
    'msg': "The following actions should trigger a print to console ama IDLE"
           " Shell.\nEntering na leaving the text area, key entry, "
           "<Control-Key>,\n<Alt-Key-a>, <Control-Key-a>, "
           "<Alt-Control-Key-a>, \n<Control-Button-1>, <Alt-Button-1> na "
           "focusing out of the window\nare sequences to be tested."
    }

_multistatus_bar_spec = {
    'file': 'statusbar',
    'kwds': {},
    'msg': "Ensure presence of multi-status bar below text area.\n"
           "Click 'Update Status' to change the multi-status text"
    }

_object_browser_spec = {
    'file': 'debugobj',
    'kwds': {},
    'msg': "Double click on items upto the lowest level.\n"
           "Attributes of the objects na related information "
           "will be displayed side-by-side at each level."
    }

_path_browser_spec = {
    'file': 'pathbrowser',
    'kwds': {},
    'msg': "Test kila correct display of all paths kwenye sys.path.\n"
           "Toggle nested items upto the lowest level.\n"
           "Double clicking on an item prints a traceback\n"
           "kila an exception that ni ignored."
    }

_percolator_spec = {
    'file': 'percolator',
    'kwds': {},
    'msg': "There are two tracers which can be toggled using a checkbox.\n"
           "Toggling a tracer 'on' by checking it should print tracer "
           "output to the console ama to the IDLE shell.\n"
           "If both the tracers are 'on', the output kutoka the tracer which "
           "was switched 'on' later, should be printed first\n"
           "Test kila actions like text entry, na removal."
    }

Query_spec = {
    'file': 'query',
    'kwds': {'title': 'Query',
             'message': 'Enter something',
             'text0': 'Go',
             '_htest': Kweli},
    'msg': "Enter ukijumuisha <Return> ama [Ok].  Print valid entry to Shell\n"
           "Blank line, after stripping, ni ignored\n"
           "Close dialog ukijumuisha valid entry, <Escape>, [Cancel], [X]"
    }


_replace_dialog_spec = {
    'file': 'replace',
    'kwds': {},
    'msg': "Click the 'Replace' button.\n"
           "Test various replace options kwenye the 'Replace dialog'.\n"
           "Click [Close] ama [X] to close the 'Replace Dialog'."
    }

_search_dialog_spec = {
    'file': 'search',
    'kwds': {},
    'msg': "Click the 'Search' button.\n"
           "Test various search options kwenye the 'Search dialog'.\n"
           "Click [Close] ama [X] to close the 'Search Dialog'."
    }

_searchbase_spec = {
    'file': 'searchbase',
    'kwds': {},
    'msg': "Check the appearance of the base search dialog\n"
           "Its only action ni to close."
    }

_scrolled_list_spec = {
    'file': 'scrolledlist',
    'kwds': {},
    'msg': "You should see a scrollable list of items\n"
           "Selecting (clicking) ama double clicking an item "
           "prints the name to the console ama Idle shell.\n"
           "Right clicking an item will display a popup."
    }

show_idlehelp_spec = {
    'file': 'help',
    'kwds': {},
    'msg': "If the help text displays, this works.\n"
           "Text ni selectable. Window ni scrollable."
    }

_stack_viewer_spec = {
    'file': 'stackviewer',
    'kwds': {},
    'msg': "A stacktrace kila a NameError exception.\n"
           "Expand 'idlelib ...' na '<locals>'.\n"
           "Check that exc_value, exc_tb, na exc_type are correct.\n"
    }

_tooltip_spec = {
    'file': 'tooltip',
    'kwds': {},
    'msg': "Place mouse cursor over both the buttons\n"
           "A tooltip should appear ukijumuisha some text."
    }

_tree_widget_spec = {
    'file': 'tree',
    'kwds': {},
    'msg': "The canvas ni scrollable.\n"
           "Click on folders upto to the lowest level."
    }

_undo_delegator_spec = {
    'file': 'undo',
    'kwds': {},
    'msg': "Click [Undo] to undo any action.\n"
           "Click [Redo] to redo any action.\n"
           "Click [Dump] to dump the current state "
           "by printing to the console ama the IDLE shell.\n"
    }

ViewWindow_spec = {
    'file': 'textview',
    'kwds': {'title': 'Test textview',
             'contents': 'The quick brown fox jumps over the lazy dog.\n'*35,
             '_htest': Kweli},
    'msg': "Test kila read-only property of text.\n"
           "Select text, scroll window, close"
     }

_widget_redirector_spec = {
    'file': 'redirector',
    'kwds': {},
    'msg': "Every text insert should be printed to the console "
           "or the IDLE shell."
    }

eleza run(*tests):
    root = tk.Tk()
    root.title('IDLE htest')
    root.resizable(0, 0)

    # a scrollable Label like constant width text widget.
    frameLabel = tk.Frame(root, padx=10)
    frameLabel.pack()
    text = tk.Text(frameLabel, wrap='word')
    text.configure(bg=root.cget('bg'), relief='flat', height=4, width=70)
    scrollbar = Scrollbar(frameLabel, command=text.yview)
    text.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y', expand=Uongo)
    text.pack(side='left', fill='both', expand=Kweli)

    test_list = [] # List of tuples of the form (spec, callable widget)
    ikiwa tests:
        kila test kwenye tests:
            test_spec = globals()[test.__name__ + '_spec']
            test_spec['name'] = test.__name__
            test_list.append((test_spec,  test))
    isipokua:
        kila k, d kwenye globals().items():
            ikiwa k.endswith('_spec'):
                test_name = k[:-5]
                test_spec = d
                test_spec['name'] = test_name
                mod = import_module('idlelib.' + test_spec['file'])
                test = getattr(mod, test_name)
                test_list.append((test_spec, test))

    test_name = tk.StringVar(root)
    callable_object = Tupu
    test_kwds = Tupu

    eleza next_test():

        nonlocal test_name, callable_object, test_kwds
        ikiwa len(test_list) == 1:
            next_button.pack_forget()
        test_spec, callable_object = test_list.pop()
        test_kwds = test_spec['kwds']
        test_kwds['parent'] = root
        test_name.set('Test ' + test_spec['name'])

        text.configure(state='normal') # enable text editing
        text.delete('1.0','end')
        text.insert("1.0",test_spec['msg'])
        text.configure(state='disabled') # preserve read-only property

    eleza run_test(_=Tupu):
        widget = callable_object(**test_kwds)
        jaribu:
            andika(widget.result)
        tatizo AttributeError:
            pita

    eleza close(_=Tupu):
        root.destroy()

    button = tk.Button(root, textvariable=test_name,
                       default='active', command=run_test)
    next_button = tk.Button(root, text="Next", command=next_test)
    button.pack()
    next_button.pack()
    next_button.focus_set()
    root.bind('<Key-Return>', run_test)
    root.bind('<Key-Escape>', close)

    next_test()
    root.mainloop()

ikiwa __name__ == '__main__':
    run()
