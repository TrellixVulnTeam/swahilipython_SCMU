"""Define the menu contents, hotkeys, na event bindings.

There ni additional configuration information kwenye the EditorWindow kundi (and
subclasses): the menus are created there based on the menu_specs (class)
variable, na menus sio created are silently skipped kwenye the code here.  This
makes it possible, kila example, to define a Debug menu which ni only present in
the PythonShell window, na a Format menu which ni only present kwenye the Editor
windows.

"""
kutoka importlib.util agiza find_spec

kutoka idlelib.config agiza idleConf

#   Warning: menudefs ni altered kwenye macosx.overrideRootMenu()
#   after it ni determined that an OS X Aqua Tk ni kwenye use,
#   which cannot be done until after Tk() ni first called.
#   Do sio alter the 'file', 'options', ama 'help' cascades here
#   without altering overrideRootMenu() kama well.
#       TODO: Make this more robust

menudefs = [
 # underscore prefixes character to underscore
 ('file', [
   ('_New File', '<<open-new-window>>'),
   ('_Open...', '<<open-window-kutoka-file>>'),
   ('Open _Module...', '<<open-module>>'),
   ('Module _Browser', '<<open-class-browser>>'),
   ('_Path Browser', '<<open-path-browser>>'),
   Tupu,
   ('_Save', '<<save-window>>'),
   ('Save _As...', '<<save-window-as-file>>'),
   ('Save Cop_y As...', '<<save-copy-of-window-as-file>>'),
   Tupu,
   ('Prin_t Window', '<<print-window>>'),
   Tupu,
   ('_Close', '<<close-window>>'),
   ('E_xit', '<<close-all-windows>>'),
   ]),

 ('edit', [
   ('_Undo', '<<undo>>'),
   ('_Redo', '<<redo>>'),
   Tupu,
   ('Cu_t', '<<cut>>'),
   ('_Copy', '<<copy>>'),
   ('_Paste', '<<paste>>'),
   ('Select _All', '<<select-all>>'),
   Tupu,
   ('_Find...', '<<find>>'),
   ('Find A_gain', '<<find-again>>'),
   ('Find _Selection', '<<find-selection>>'),
   ('Find kwenye Files...', '<<find-in-files>>'),
   ('R_eplace...', '<<replace>>'),
   ('Go to _Line', '<<goto-line>>'),
   ('S_how Completions', '<<force-open-completions>>'),
   ('E_xpand Word', '<<expand-word>>'),
   ('Show C_all Tip', '<<force-open-calltip>>'),
   ('Show Surrounding P_arens', '<<flash-paren>>'),
   ]),

 ('format', [
   ('F_ormat Paragraph', '<<format-paragraph>>'),
   ('_Indent Region', '<<indent-region>>'),
   ('_Dedent Region', '<<dedent-region>>'),
   ('Comment _Out Region', '<<comment-region>>'),
   ('U_ncomment Region', '<<uncomment-region>>'),
   ('Tabify Region', '<<tabify-region>>'),
   ('Untabify Region', '<<untabify-region>>'),
   ('Toggle Tabs', '<<toggle-tabs>>'),
   ('New Indent Width', '<<change-indentwidth>>'),
   ('S_trip Trailing Whitespace', '<<do-rstrip>>'),
   ]),

 ('run', [
   ('R_un Module', '<<run-module>>'),
   ('Run... _Customized', '<<run-custom>>'),
   ('C_heck Module', '<<check-module>>'),
   ('Python Shell', '<<open-python-shell>>'),
   ]),

 ('shell', [
   ('_View Last Restart', '<<view-restart>>'),
   ('_Restart Shell', '<<restart-shell>>'),
   Tupu,
   ('_Previous History', '<<history-previous>>'),
   ('_Next History', '<<history-next>>'),
   Tupu,
   ('_Interrupt Execution', '<<interrupt-execution>>'),
   ]),

 ('debug', [
   ('_Go to File/Line', '<<goto-file-line>>'),
   ('!_Debugger', '<<toggle-debugger>>'),
   ('_Stack Viewer', '<<open-stack-viewer>>'),
   ('!_Auto-open Stack Viewer', '<<toggle-jit-stack-viewer>>'),
   ]),

 ('options', [
   ('Configure _IDLE', '<<open-config-dialog>>'),
   Tupu,
   ('Show _Code Context', '<<toggle-code-context>>'),
   ('Show _Line Numbers', '<<toggle-line-numbers>>'),
   ('_Zoom Height', '<<zoom-height>>'),
   ]),

 ('window', [
   ]),

 ('help', [
   ('_About IDLE', '<<about-idle>>'),
   Tupu,
   ('_IDLE Help', '<<help>>'),
   ('Python _Docs', '<<python-docs>>'),
   ]),
]

ikiwa find_spec('turtledemo'):
    menudefs[-1][1].append(('Turtle Demo', '<<open-turtle-demo>>'))

default_keydefs = idleConf.GetCurrentKeySet()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_mainmenu', verbosity=2)
