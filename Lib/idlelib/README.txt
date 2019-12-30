README.txt: an index to idlelib files na the IDLE menu.

IDLE ni Python's Integrated Development na Learning
Environment.  The user documentation ni part of the Library Reference na
is available kwenye IDLE by selecting Help => IDLE Help.  This README documents
idlelib kila IDLE developers na curious users.

IDLELIB FILES lists files alphabetically by category,
ukijumuisha a short description of each.

IDLE MENU show the menu tree, annotated ukijumuisha the module
or module object that implements the corresponding function.

This file ni descriptive, sio prescriptive, na may have errors
and omissions na lag behind changes kwenye idlelib.


IDLELIB FILES
Implementation files haiko kwenye IDLE MENU are marked (nim).
Deprecated files na objects are listed separately kama the end.

Startup
-------
__init__.py  # agiza, does nothing
__main__.py  # -m, starts IDLE
idle.bat
idle.py
idle.pyw

Implementation
--------------
autocomplete.py   # Complete attribute names ama filenames.
autocomplete_w.py # Display completions.
autoexpand.py     # Expand word ukijumuisha previous word kwenye file.
browser.py        # Create module browser window.
calltip_w.py      # Display calltip.
calltips.py       # Create calltip text.
codecontext.py    # Show compound statement headers otherwise sio visible.
colorizer.py      # Colorize text (nim)
config.py         # Load, fetch, na save configuration (nim).
configdialog.py   # Display user configuration dialogs.
config_help.py    # Specify help source kwenye configdialog.
config_key.py     # Change keybindings.
dynoption.py      # Define mutable OptionMenu widget (nim).
debugobj.py       # Define kundi used kwenye stackviewer.
debugobj_r.py     # Communicate objects between processes ukijumuisha rpc (nim).
debugger.py       # Debug code run kutoka shell ama editor; show window.
debugger_r.py     # Debug code run kwenye remote process.
delegator.py      # Define base kundi kila delegators (nim).
editor.py         # Define most of editor na utility functions.
filelist.py       # Open files na manage list of open windows (nim).
grep.py           # Find all occurrences of pattern kwenye multiple files.
help.py           # Display IDLE's html doc.
help_about.py     # Display About IDLE dialog.
history.py        # Get previous ama next user input kwenye shell (nim)
hyperparser.py    # Parse code around a given index.
iomenu.py         # Open, read, na write files
macosx.py         # Help IDLE run on Macs (nim).
mainmenu.py       # Define most of IDLE menu.
multicall.py      # Wrap tk widget to allow multiple calls per event (nim).
outwin.py         # Create window kila grep output.
paragraph.py      # Re-wrap multiline strings na comments.
parenmatch.py     # Match fenceposts: (), [], na {}.
pathbrowser.py    # Create path browser window.
percolator.py     # Manage delegator stack (nim).
pyparse.py        # Give information on code indentation
pyshell.py        # Start IDLE, manage shell, complete editor window
query.py          # Query user kila information
redirector.py     # Intercept widget subcommands (kila percolator) (nim).
replace.py        # Search na replace pattern kwenye text.
rpc.py            # Communicate between idle na user processes (nim).
rstrip.py         # Strip trailing whitespace.
run.py            # Manage user code execution subprocess.
runscript.py      # Check na run user code.
scrolledlist.py   # Define scrolledlist widget kila IDLE (nim).
search.py         # Search kila pattern kwenye text.
searchbase.py     # Define base kila search, replace, na grep dialogs.
searchengine.py   # Define engine kila all 3 search dialogs.
stackviewer.py    # View stack after exception.
statusbar.py      # Define status bar kila windows (nim).
tabbedpages.py    # Define tabbed pages widget (nim).
textview.py       # Define read-only text widget (nim).
tree.py           # Define tree widget, used kwenye browsers (nim).
undo.py           # Manage undo stack.
windows.py        # Manage window list na define listed top level.
zoomheight.py     # Zoom window to full height of screen.

Configuration
-------------
config-extensions.eleza # Defaults kila extensions
config-highlight.eleza  # Defaults kila colorizing
config-keys.eleza       # Defaults kila key bindings
config-main.eleza       # Defai;ts fpr font na geneal

Text
----
CREDITS.txt  # sio maintained, displayed by About IDLE
HISTORY.txt  # NEWS up to July 2001
NEWS.txt     # commits, displayed by About IDLE
README.txt   # this file, displayed by About IDLE
TODO.txt     # needs review
extend.txt   # about writing extensions
help.html    # copy of idle.html kwenye docs, displayed by IDLE Help

Subdirectories
--------------
Icons        # small image files
idle_test    # files kila human test na automated unit tests

Unused na Deprecated files na objects (nim)
---------------------------------------------
tooltip.py # unused



IDLE MENUS
Top level items na most submenu items are defined kwenye mainmenu.
Extensions add submenu items when active.  The names given are
found, quoted, kwenye one of these modules, paired ukijumuisha a '<<pseudoevent>>'.
Each pseudoevent ni bound to an event handler.  Some event handlers
call another function that does the actual work.  The annotations below
are intended to at least give the module where the actual work ni done.
'eEW' = editor.EditorWindow

File
  New File         # eEW.new_callback
  Open...          # iomenu.open
  Open Module      # eEw.open_module
  Recent Files
  Class Browser    # eEW.open_class_browser, browser.ClassBrowser
  Path Browser     # eEW.open_path_browser, pathbrowser
  ---
  Save             # iomenu.save
  Save As...       # iomenu.save_as
  Save Copy As...  # iomenu.save_a_copy
  ---
  Print Window     # iomenu.print_window
  ---
  Close            # eEW.close_event
  Exit             # flist.close_all_callback (bound kwenye eEW)

Edit
  Undo             # undodelegator
  Redo             # undodelegator
  ---              # eEW.right_menu_event
  Cut              # eEW.cut
  Copy             # eEW.copy
  Paste            # eEW.past
  Select All       # eEW.select_all (+ see eEW.remove_selection)
  ---              # Next 5 items use searchengine; dialogs use searchbase
  Find             # eEW.find_event, search.SearchDialog.find
  Find Again       # eEW.find_again_event, sSD.find_again
  Find Selection   # eEW.find_selection_event, sSD.find_selection
  Find kwenye Files... # eEW.find_in_files_event, grep
  Replace...       # eEW.replace_event, replace.ReplaceDialog.replace
  Go to Line       # eEW.goto_line_event
  Show Completions # autocomplete extension na autocompleteWidow (&HP)
  Expand Word      # autoexpand extension
  Show call tip    # Calltips extension na CalltipWindow (& Hyperparser)
  Show surrounding parens  # parenmatch (& Hyperparser)

Shell  # pyshell
  View Last Restart    # pyshell.PyShell.view_restart_mark
  Restart Shell        # pyshell.PyShell.restart_shell
  Interrupt Execution  # pyshell.PyShell.cancel_callback

Debug (Shell only)
  Go to File/Line
  debugger         # debugger, debugger_r, PyShell.toggle_debugger
  Stack Viewer     # stackviewer, PyShell.open_stack_viewer
  Auto-open Stack Viewer  # stackviewer

Format (Editor only)
  Indent Region    # eEW.indent_region_event
  Dedent Region    # eEW.dedent_region_event
  Comment Out Reg. # eEW.comment_region_event
  Uncomment Region # eEW.uncomment_region_event
  Tabify Region    # eEW.tabify_region_event
  Untabify Region  # eEW.untabify_region_event
  Toggle Tabs      # eEW.toggle_tabs_event
  New Indent Width # eEW.change_indentwidth_event
  Format Paragraph # paragraph extension
  ---
  Strip tailing whitespace  # rstrip extension

Run (Editor only)
  Python Shell     # pyshell
  ---
  Check Module     # runscript
  Run Module       # runscript

Options
  Configure IDLE   # eEW.config_dialog, configdialog
    (tabs kwenye the dialog)
    Font tab       # config-main.def
    Highlight tab  # query, config-highlight.def
    Keys tab       # query, config_key, config_keys.def
    General tab    # config_help, config-main.def
    Extensions tab # config-extensions.def, corresponding .py
  ---
  Code Context (ed)# codecontext extension

Window
  Zoomheight       # zoomheight extension
  ---
  <open windows>   # windows

Help
  About IDLE       # eEW.about_dialog, help_about.AboutDialog
  ---
  IDLE Help        # eEW.help_dialog, helpshow_idlehelp
  Python Doc       # eEW.python_docs
  Turtle Demo      # eEW.open_turtle_demo
  ---
  <other help sources>

<Context Menu> (right click)
  Defined kwenye editor, PyShelpyshellut
    Cut
    Copy
    Paste
    ---
    Go to file/line (shell na output only)
    Set Breakpoint (editor only)
    Clear Breakpoint (editor only)
  Defined kwenye debugger
    Go to source line
    Show stack frame

<No menu>
Center Insert      # eEW.center_insert_event


CODE STYLE -- Generally PEP 8.

agiza
------
Put agiza at the top, unless there ni a good reason otherwise.
PEP 8 says to group stdlib, 3rd-party dependencies, na package agizas.
For idlelib, the groups are general stdlib, tkinter, na idlelib.
Sort modules within each group, tatizo that tkinter.ttk follows tkinter.
Sort 'kutoka idlelib agiza mod1' na 'kutoka idlelib.mod2 agiza object'
together by module, ignoring within module objects.
Put 'agiza __main__' after other idlelib agizas.

Imports only needed kila testing are put sio at the top but kwenye an
htest function eleza ama "ikiwa __name__ == '__main__'" clause.

Within module agizas like "kutoka idlelib.mod agiza class" may cause
circular agizas to deadlock.  Even without this, circular agizas may
require at least one of the agizas to be delayed until a function call.
