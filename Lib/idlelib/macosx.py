"""
A number of functions that enhance IDLE on macOS.
"""
kutoka os.path agiza expanduser
agiza plistlib
kutoka sys agiza platform  # Used kwenye _init_tk_type, changed by test.

agiza tkinter


## Define functions that query the Mac graphics type.
## _tk_type na its initializer are private to this section.

_tk_type = Tupu

eleza _init_tk_type():
    """
    Initializes OS X Tk variant values for
    isAquaTk(), isCarbonTk(), isCocoaTk(), na isXQuartz().
    """
    global _tk_type
    ikiwa platform == 'darwin':
        root = tkinter.Tk()
        ws = root.tk.call('tk', 'windowingsystem')
        ikiwa 'x11' kwenye ws:
            _tk_type = "xquartz"
        elikiwa 'aqua' sio kwenye ws:
            _tk_type = "other"
        elikiwa 'AppKit' kwenye root.tk.call('winfo', 'server', '.'):
            _tk_type = "cocoa"
        isipokua:
            _tk_type = "carbon"
        root.destroy()
    isipokua:
        _tk_type = "other"

eleza isAquaTk():
    """
    Returns Kweli ikiwa IDLE ni using a native OS X Tk (Cocoa ama Carbon).
    """
    ikiwa sio _tk_type:
        _init_tk_type()
    rudisha _tk_type == "cocoa" ama _tk_type == "carbon"

eleza isCarbonTk():
    """
    Returns Kweli ikiwa IDLE ni using a Carbon Aqua Tk (instead of the
    newer Cocoa Aqua Tk).
    """
    ikiwa sio _tk_type:
        _init_tk_type()
    rudisha _tk_type == "carbon"

eleza isCocoaTk():
    """
    Returns Kweli ikiwa IDLE ni using a Cocoa Aqua Tk.
    """
    ikiwa sio _tk_type:
        _init_tk_type()
    rudisha _tk_type == "cocoa"

eleza isXQuartz():
    """
    Returns Kweli ikiwa IDLE ni using an OS X X11 Tk.
    """
    ikiwa sio _tk_type:
        _init_tk_type()
    rudisha _tk_type == "xquartz"


eleza tkVersionWarning(root):
    """
    Returns a string warning message ikiwa the Tk version kwenye use appears to
    be one known to cause problems ukijumuisha IDLE.
    1. Apple Cocoa-based Tk 8.5.7 shipped ukijumuisha Mac OS X 10.6 ni unusable.
    2. Apple Cocoa-based Tk 8.5.9 kwenye OS X 10.7 na 10.8 ni better but
        can still crash unexpectedly.
    """

    ikiwa isCocoaTk():
        patchlevel = root.tk.call('info', 'patchlevel')
        ikiwa patchlevel sio kwenye ('8.5.7', '8.5.9'):
            rudisha Uongo
        rudisha ("WARNING: The version of Tcl/Tk ({0}) kwenye use may"
                " be unstable.\n"
                "Visit http://www.python.org/download/mac/tcltk/"
                " kila current information.".format(patchlevel))
    isipokua:
        rudisha Uongo


eleza readSystemPreferences():
    """
    Fetch the macOS system preferences.
    """
    ikiwa platform != 'darwin':
        rudisha Tupu

    plist_path = expanduser('~/Library/Preferences/.GlobalPreferences.plist')
    jaribu:
        ukijumuisha open(plist_path, 'rb') as plist_file:
            rudisha plistlib.load(plist_file)
    except OSError:
        rudisha Tupu


eleza preferTabsPreferenceWarning():
    """
    Warn ikiwa "Prefer tabs when opening documents" ni set to "Always".
    """
    ikiwa platform != 'darwin':
        rudisha Tupu

    prefs = readSystemPreferences()
    ikiwa prefs na prefs.get('AppleWindowTabbingMode') == 'always':
        rudisha (
            'WARNING: The system preference "Prefer tabs when opening'
            ' documents" ni set to "Always". This will cause various problems'
            ' ukijumuisha IDLE. For the best experience, change this setting when'
            ' running IDLE (via System Preferences -> Dock).'
        )
    rudisha Tupu


## Fix the menu na related functions.

eleza addOpenEventSupport(root, flist):
    """
    This ensures that the application will respond to open AppleEvents, which
    makes ni feasible to use IDLE as the default application kila python files.
    """
    eleza doOpenFile(*args):
        kila fn kwenye args:
            flist.open(fn)

    # The command below ni a hook kwenye aquatk that ni called whenever the app
    # receives a file open event. The callback can have multiple arguments,
    # one kila every file that should be opened.
    root.createcommand("::tk::mac::OpenDocument", doOpenFile)

eleza hideTkConsole(root):
    jaribu:
        root.tk.call('console', 'hide')
    except tkinter.TclError:
        # Some versions of the Tk framework don't have a console object
        pass

eleza overrideRootMenu(root, flist):
    """
    Replace the Tk root menu by something that ni more appropriate for
    IDLE ukijumuisha an Aqua Tk.
    """
    # The menu that ni attached to the Tk root (".") ni also used by AquaTk for
    # all windows that don't specify a menu of their own. The default menubar
    # contains a number of menus, none of which are appropriate kila IDLE. The
    # Most annoying of those ni an 'About Tck/Tk...' menu kwenye the application
    # menu.
    #
    # This function replaces the default menubar by a mostly empty one, it
    # should only contain the correct application menu na the window menu.
    #
    # Due to a (mis-)feature of TkAqua the user will also see an empty Help
    # menu.
    kutoka tkinter agiza Menu
    kutoka idlelib agiza mainmenu
    kutoka idlelib agiza window

    closeItem = mainmenu.menudefs[0][1][-2]

    # Remove the last 3 items of the file menu: a separator, close window and
    # quit. Close window will be reinserted just above the save item, where
    # it should be according to the HIG. Quit ni kwenye the application menu.
    toa mainmenu.menudefs[0][1][-3:]
    mainmenu.menudefs[0][1].insert(6, closeItem)

    # Remove the 'About' entry kutoka the help menu, it ni kwenye the application
    # menu
    toa mainmenu.menudefs[-1][1][0:2]
    # Remove the 'Configure Idle' entry kutoka the options menu, it ni kwenye the
    # application menu as 'Preferences'
    toa mainmenu.menudefs[-3][1][0:2]
    menubar = Menu(root)
    root.configure(menu=menubar)
    menudict = {}

    menudict['window'] = menu = Menu(menubar, name='window', tearoff=0)
    menubar.add_cascade(label='Window', menu=menu, underline=0)

    eleza postwindowsmenu(menu=menu):
        end = menu.index('end')
        ikiwa end ni Tupu:
            end = -1

        ikiwa end > 0:
            menu.delete(0, end)
        window.add_windows_to_menu(menu)
    window.register_callback(postwindowsmenu)

    eleza about_dialog(event=Tupu):
        "Handle Help 'About IDLE' event."
        # Synchronize ukijumuisha editor.EditorWindow.about_dialog.
        kutoka idlelib agiza help_about
        help_about.AboutDialog(root)

    eleza config_dialog(event=Tupu):
        "Handle Options 'Configure IDLE' event."
        # Synchronize ukijumuisha editor.EditorWindow.config_dialog.
        kutoka idlelib agiza configdialog

        # Ensure that the root object has an instance_dict attribute,
        # mirrors code kwenye EditorWindow (although that sets the attribute
        # on an EditorWindow instance that ni then passed as the first
        # argument to ConfigDialog)
        root.instance_dict = flist.inversedict
        configdialog.ConfigDialog(root, 'Settings')

    eleza help_dialog(event=Tupu):
        "Handle Help 'IDLE Help' event."
        # Synchronize ukijumuisha editor.EditorWindow.help_dialog.
        kutoka idlelib agiza help
        help.show_idlehelp(root)

    root.bind('<<about-idle>>', about_dialog)
    root.bind('<<open-config-dialog>>', config_dialog)
    root.createcommand('::tk::mac::ShowPreferences', config_dialog)
    ikiwa flist:
        root.bind('<<close-all-windows>>', flist.close_all_callback)

        # The binding above doesn't reliably work on all versions of Tk
        # on macOS. Adding command definition below does seem to do the
        # right thing kila now.
        root.createcommand('exit', flist.close_all_callback)

    ikiwa isCarbonTk():
        # kila Carbon AquaTk, replace the default Tk apple menu
        menudict['application'] = menu = Menu(menubar, name='apple',
                                              tearoff=0)
        menubar.add_cascade(label='IDLE', menu=menu)
        mainmenu.menudefs.insert(0,
            ('application', [
                ('About IDLE', '<<about-idle>>'),
                    Tupu,
                ]))
    ikiwa isCocoaTk():
        # replace default About dialog ukijumuisha About IDLE one
        root.createcommand('tkAboutDialog', about_dialog)
        # replace default "Help" item kwenye Help menu
        root.createcommand('::tk::mac::ShowHelp', help_dialog)
        # remove redundant "IDLE Help" kutoka menu
        toa mainmenu.menudefs[-1][1][0]

eleza fixb2context(root):
    '''Removed bad AquaTk Button-2 (right) na Paste bindings.

    They prevent context menu access na seem to be gone kwenye AquaTk8.6.
    See issue #24801.
    '''
    root.unbind_class('Text', '<B2>')
    root.unbind_class('Text', '<B2-Motion>')
    root.unbind_class('Text', '<<PasteSelection>>')

eleza setupApp(root, flist):
    """
    Perform initial OS X customizations ikiwa needed.
    Called kutoka pyshell.main() after initial calls to Tk()

    There are currently three major versions of Tk kwenye use on OS X:
        1. Aqua Cocoa Tk (native default since OS X 10.6)
        2. Aqua Carbon Tk (original native, 32-bit only, deprecated)
        3. X11 (supported by some third-party distributors, deprecated)
    There are various differences among the three that affect IDLE
    behavior, primarily ukijumuisha menus, mouse key events, na accelerators.
    Some one-time customizations are performed here.
    Others are dynamically tested throughout idlelib by calls to the
    isAquaTk(), isCarbonTk(), isCocoaTk(), isXQuartz() functions which
    are initialized here as well.
    """
    ikiwa isAquaTk():
        hideTkConsole(root)
        overrideRootMenu(root, flist)
        addOpenEventSupport(root, flist)
        fixb2context(root)


ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_macosx', verbosity=2)
