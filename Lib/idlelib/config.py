"""idlelib.config -- Manage IDLE configuration information.

The comments at the beginning of config-main.eleza describe the
configuration files and the design implemented to update user
configuration information.  In particular, user configuration choices
which duplicate the defaults will be removed kutoka the user's
configuration files, and ikiwa a user file becomes empty, it will be
deleted.

The configuration database maps options to values.  Conceptually, the
database keys are tuples (config-type, section, item).  As implemented,
there are  separate dicts for default and user values.  Each has
config-type keys 'main', 'extensions', 'highlight', and 'keys'.  The
value for each key is a ConfigParser instance that maps section and item
to values.  For 'main' and 'extensions', user values override
default values.  For 'highlight' and 'keys', user sections augment the
default sections (and must, therefore, have distinct names).

Throughout this module there is an emphasis on returning useable defaults
when a problem occurs in returning a requested configuration value back to
idle. This is to allow IDLE to continue to function in spite of errors in
the retrieval of config information. When a default is returned instead of
a requested config value, a message is printed to stderr to aid in
configuration problem notification and resolution.
"""
# TODOs added Oct 2014, tjr

kutoka configparser agiza ConfigParser
agiza os
agiza sys

kutoka tkinter.font agiza Font
agiza idlelib

kundi InvalidConfigType(Exception): pass
kundi InvalidConfigSet(Exception): pass
kundi InvalidTheme(Exception): pass

kundi IdleConfParser(ConfigParser):
    """
    A ConfigParser specialised for idle configuration file handling
    """
    eleza __init__(self, cfgFile, cfgDefaults=None):
        """
        cfgFile - string, fully specified configuration file name
        """
        self.file = cfgFile  # This is currently '' when testing.
        ConfigParser.__init__(self, defaults=cfgDefaults, strict=False)

    eleza Get(self, section, option, type=None, default=None, raw=False):
        """
        Get an option value for given section/option or rudisha default.
        If type is specified, rudisha as type.
        """
        # TODO Use default as fallback, at least ikiwa not None
        # Should also print Warning(file, section, option).
        # Currently may raise ValueError
        ikiwa not self.has_option(section, option):
            rudisha default
        ikiwa type == 'bool':
            rudisha self.getboolean(section, option)
        elikiwa type == 'int':
            rudisha self.getint(section, option)
        else:
            rudisha self.get(section, option, raw=raw)

    eleza GetOptionList(self, section):
        "Return a list of options for given section, else []."
        ikiwa self.has_section(section):
            rudisha self.options(section)
        else:  #rudisha a default value
            rudisha []

    eleza Load(self):
        "Load the configuration file kutoka disk."
        ikiwa self.file:
            self.read(self.file)

kundi IdleUserConfParser(IdleConfParser):
    """
    IdleConfigParser specialised for user configuration handling.
    """

    eleza SetOption(self, section, option, value):
        """Return True ikiwa option is added or changed to value, else False.

        Add section ikiwa required.  False means option already had value.
        """
        ikiwa self.has_option(section, option):
            ikiwa self.get(section, option) == value:
                rudisha False
            else:
                self.set(section, option, value)
                rudisha True
        else:
            ikiwa not self.has_section(section):
                self.add_section(section)
            self.set(section, option, value)
            rudisha True

    eleza RemoveOption(self, section, option):
        """Return True ikiwa option is removed kutoka section, else False.

        False ikiwa either section does not exist or did not have option.
        """
        ikiwa self.has_section(section):
            rudisha self.remove_option(section, option)
        rudisha False

    eleza AddSection(self, section):
        "If section doesn't exist, add it."
        ikiwa not self.has_section(section):
            self.add_section(section)

    eleza RemoveEmptySections(self):
        "Remove any sections that have no options."
        for section in self.sections():
            ikiwa not self.GetOptionList(section):
                self.remove_section(section)

    eleza IsEmpty(self):
        "Return True ikiwa no sections after removing empty sections."
        self.RemoveEmptySections()
        rudisha not self.sections()

    eleza Save(self):
        """Update user configuration file.

        If self not empty after removing empty sections, write the file
        to disk. Otherwise, remove the file kutoka disk ikiwa it exists.
        """
        fname = self.file
        ikiwa fname and fname[0] != '#':
            ikiwa not self.IsEmpty():
                try:
                    cfgFile = open(fname, 'w')
                except OSError:
                    os.unlink(fname)
                    cfgFile = open(fname, 'w')
                with cfgFile:
                    self.write(cfgFile)
            elikiwa os.path.exists(self.file):
                os.remove(self.file)

kundi IdleConf:
    """Hold config parsers for all idle config files in singleton instance.

    Default config files, self.defaultCfg --
        for config_type in self.config_types:
            (idle install dir)/config-{config-type}.def

    User config files, self.userCfg --
        for config_type in self.config_types:
        (user home dir)/.idlerc/config-{config-type}.cfg
    """
    eleza __init__(self, _utest=False):
        self.config_types = ('main', 'highlight', 'keys', 'extensions')
        self.defaultCfg = {}
        self.userCfg = {}
        self.cfg = {}  # TODO use to select userCfg vs defaultCfg

        ikiwa not _utest:
            self.CreateConfigHandlers()
            self.LoadCfgFiles()

    eleza CreateConfigHandlers(self):
        "Populate default and user config parser dictionaries."
        idledir = os.path.dirname(__file__)
        self.userdir = userdir = '' ikiwa idlelib.testing else self.GetUserCfgDir()
        for cfg_type in self.config_types:
            self.defaultCfg[cfg_type] = IdleConfParser(
                os.path.join(idledir, f'config-{cfg_type}.def'))
            self.userCfg[cfg_type] = IdleUserConfParser(
                os.path.join(userdir or '#', f'config-{cfg_type}.cfg'))

    eleza GetUserCfgDir(self):
        """Return a filesystem directory for storing user config files.

        Creates it ikiwa required.
        """
        cfgDir = '.idlerc'
        userDir = os.path.expanduser('~')
        ikiwa userDir != '~': # expanduser() found user home dir
            ikiwa not os.path.exists(userDir):
                ikiwa not idlelib.testing:
                    warn = ('\n Warning: os.path.expanduser("~") points to\n ' +
                            userDir + ',\n but the path does not exist.')
                    try:
                        andika(warn, file=sys.stderr)
                    except OSError:
                        pass
                userDir = '~'
        ikiwa userDir == "~": # still no path to home!
            # traditionally IDLE has defaulted to os.getcwd(), is this adequate?
            userDir = os.getcwd()
        userDir = os.path.join(userDir, cfgDir)
        ikiwa not os.path.exists(userDir):
            try:
                os.mkdir(userDir)
            except OSError:
                ikiwa not idlelib.testing:
                    warn = ('\n Warning: unable to create user config directory\n' +
                            userDir + '\n Check path and permissions.\n Exiting!\n')
                    try:
                        andika(warn, file=sys.stderr)
                    except OSError:
                        pass
                raise SystemExit
        # TODO continue without userDIr instead of exit
        rudisha userDir

    eleza GetOption(self, configType, section, option, default=None, type=None,
                  warn_on_default=True, raw=False):
        """Return a value for configType section option, or default.

        If type is not None, rudisha a value of that type.  Also pass raw
        to the config parser.  First try to rudisha a valid value
        (including type) kutoka a user configuration. If that fails, try
        the default configuration. If that fails, rudisha default, with a
        default of None.

        Warn ikiwa either user or default configurations have an invalid value.
        Warn ikiwa default is returned and warn_on_default is True.
        """
        try:
            ikiwa self.userCfg[configType].has_option(section, option):
                rudisha self.userCfg[configType].Get(section, option,
                                                    type=type, raw=raw)
        except ValueError:
            warning = ('\n Warning: config.py - IdleConf.GetOption -\n'
                       ' invalid %r value for configuration option %r\n'
                       ' kutoka section %r: %r' %
                       (type, option, section,
                       self.userCfg[configType].Get(section, option, raw=raw)))
            _warn(warning, configType, section, option)
        try:
            ikiwa self.defaultCfg[configType].has_option(section,option):
                rudisha self.defaultCfg[configType].Get(
                        section, option, type=type, raw=raw)
        except ValueError:
            pass
        #returning default, print warning
        ikiwa warn_on_default:
            warning = ('\n Warning: config.py - IdleConf.GetOption -\n'
                       ' problem retrieving configuration option %r\n'
                       ' kutoka section %r.\n'
                       ' returning default value: %r' %
                       (option, section, default))
            _warn(warning, configType, section, option)
        rudisha default

    eleza SetOption(self, configType, section, option, value):
        """Set section option to value in user config file."""
        self.userCfg[configType].SetOption(section, option, value)

    eleza GetSectionList(self, configSet, configType):
        """Return sections for configSet configType configuration.

        configSet must be either 'user' or 'default'
        configType must be in self.config_types.
        """
        ikiwa not (configType in self.config_types):
            raise InvalidConfigType('Invalid configType specified')
        ikiwa configSet == 'user':
            cfgParser = self.userCfg[configType]
        elikiwa configSet == 'default':
            cfgParser=self.defaultCfg[configType]
        else:
            raise InvalidConfigSet('Invalid configSet specified')
        rudisha cfgParser.sections()

    eleza GetHighlight(self, theme, element):
        """Return dict of theme element highlight colors.

        The keys are 'foreground' and 'background'.  The values are
        tkinter color strings for configuring backgrounds and tags.
        """
        cfg = ('default' ikiwa self.defaultCfg['highlight'].has_section(theme)
               else 'user')
        theme_dict = self.GetThemeDict(cfg, theme)
        fore = theme_dict[element + '-foreground']
        ikiwa element == 'cursor':
            element = 'normal'
        back = theme_dict[element + '-background']
        rudisha {"foreground": fore, "background": back}

    eleza GetThemeDict(self, type, themeName):
        """Return {option:value} dict for elements in themeName.

        type - string, 'default' or 'user' theme type
        themeName - string, theme name
        Values are loaded over ultimate fallback defaults to guarantee
        that all theme elements are present in a newly created theme.
        """
        ikiwa type == 'user':
            cfgParser = self.userCfg['highlight']
        elikiwa type == 'default':
            cfgParser = self.defaultCfg['highlight']
        else:
            raise InvalidTheme('Invalid theme type specified')
        # Provide foreground and background colors for each theme
        # element (other than cursor) even though some values are not
        # yet used by idle, to allow for their use in the future.
        # Default values are generally black and white.
        # TODO copy theme kutoka a kundi attribute.
        theme ={'normal-foreground':'#000000',
                'normal-background':'#ffffff',
                'keyword-foreground':'#000000',
                'keyword-background':'#ffffff',
                'builtin-foreground':'#000000',
                'builtin-background':'#ffffff',
                'comment-foreground':'#000000',
                'comment-background':'#ffffff',
                'string-foreground':'#000000',
                'string-background':'#ffffff',
                'definition-foreground':'#000000',
                'definition-background':'#ffffff',
                'hilite-foreground':'#000000',
                'hilite-background':'gray',
                'break-foreground':'#ffffff',
                'break-background':'#000000',
                'hit-foreground':'#ffffff',
                'hit-background':'#000000',
                'error-foreground':'#ffffff',
                'error-background':'#000000',
                'context-foreground':'#000000',
                'context-background':'#ffffff',
                'linenumber-foreground':'#000000',
                'linenumber-background':'#ffffff',
                #cursor (only foreground can be set)
                'cursor-foreground':'#000000',
                #shell window
                'stdout-foreground':'#000000',
                'stdout-background':'#ffffff',
                'stderr-foreground':'#000000',
                'stderr-background':'#ffffff',
                'console-foreground':'#000000',
                'console-background':'#ffffff',
                }
        for element in theme:
            ikiwa not (cfgParser.has_option(themeName, element) or
                    # Skip warning for new elements.
                    element.startswith(('context-', 'linenumber-'))):
                # Print warning that will rudisha a default color
                warning = ('\n Warning: config.IdleConf.GetThemeDict'
                           ' -\n problem retrieving theme element %r'
                           '\n kutoka theme %r.\n'
                           ' returning default color: %r' %
                           (element, themeName, theme[element]))
                _warn(warning, 'highlight', themeName, element)
            theme[element] = cfgParser.Get(
                    themeName, element, default=theme[element])
        rudisha theme

    eleza CurrentTheme(self):
        "Return the name of the currently active text color theme."
        rudisha self.current_colors_and_keys('Theme')

    eleza CurrentKeys(self):
        """Return the name of the currently active key set."""
        rudisha self.current_colors_and_keys('Keys')

    eleza current_colors_and_keys(self, section):
        """Return the currently active name for Theme or Keys section.

        idlelib.config-main.eleza ('default') includes these sections

        [Theme]
        default= 1
        name= IDLE Classic
        name2=

        [Keys]
        default= 1
        name=
        name2=

        Item 'name2', is used for built-in ('default') themes and keys
        added after 2015 Oct 1 and 2016 July 1.  This kludge is needed
        because setting 'name' to a builtin not defined in older IDLEs
        to display multiple error messages or quit.
        See https://bugs.python.org/issue25313.
        When default = True, 'name2' takes precedence over 'name',
        while older IDLEs will just use name.  When default = False,
        'name2' may still be set, but it is ignored.
        """
        cfgname = 'highlight' ikiwa section == 'Theme' else 'keys'
        default = self.GetOption('main', section, 'default',
                                 type='bool', default=True)
        name = ''
        ikiwa default:
            name = self.GetOption('main', section, 'name2', default='')
        ikiwa not name:
            name = self.GetOption('main', section, 'name', default='')
        ikiwa name:
            source = self.defaultCfg ikiwa default else self.userCfg
            ikiwa source[cfgname].has_section(name):
                rudisha name
        rudisha "IDLE Classic" ikiwa section == 'Theme' else self.default_keys()

    @staticmethod
    eleza default_keys():
        ikiwa sys.platform[:3] == 'win':
            rudisha 'IDLE Classic Windows'
        elikiwa sys.platform == 'darwin':
            rudisha 'IDLE Classic OSX'
        else:
            rudisha 'IDLE Modern Unix'

    eleza GetExtensions(self, active_only=True,
                      editor_only=False, shell_only=False):
        """Return extensions in default and user config-extensions files.

        If active_only True, only rudisha active (enabled) extensions
        and optionally only editor or shell extensions.
        If active_only False, rudisha all extensions.
        """
        extns = self.RemoveKeyBindNames(
                self.GetSectionList('default', 'extensions'))
        userExtns = self.RemoveKeyBindNames(
                self.GetSectionList('user', 'extensions'))
        for extn in userExtns:
            ikiwa extn not in extns: #user has added own extension
                extns.append(extn)
        for extn in ('AutoComplete','CodeContext',
                     'FormatParagraph','ParenMatch'):
            extns.remove(extn)
            # specific exclusions because we are storing config for mainlined old
            # extensions in config-extensions.eleza for backward compatibility
        ikiwa active_only:
            activeExtns = []
            for extn in extns:
                ikiwa self.GetOption('extensions', extn, 'enable', default=True,
                                  type='bool'):
                    #the extension is enabled
                    ikiwa editor_only or shell_only:  # TODO both True contradict
                        ikiwa editor_only:
                            option = "enable_editor"
                        else:
                            option = "enable_shell"
                        ikiwa self.GetOption('extensions', extn,option,
                                          default=True, type='bool',
                                          warn_on_default=False):
                            activeExtns.append(extn)
                    else:
                        activeExtns.append(extn)
            rudisha activeExtns
        else:
            rudisha extns

    eleza RemoveKeyBindNames(self, extnNameList):
        "Return extnNameList with keybinding section names removed."
        rudisha [n for n in extnNameList ikiwa not n.endswith(('_bindings', '_cfgBindings'))]

    eleza GetExtnNameForEvent(self, virtualEvent):
        """Return the name of the extension binding virtualEvent, or None.

        virtualEvent - string, name of the virtual event to test for,
                       without the enclosing '<< >>'
        """
        extName = None
        vEvent = '<<' + virtualEvent + '>>'
        for extn in self.GetExtensions(active_only=0):
            for event in self.GetExtensionKeys(extn):
                ikiwa event == vEvent:
                    extName = extn  # TODO rudisha here?
        rudisha extName

    eleza GetExtensionKeys(self, extensionName):
        """Return dict: {configurable extensionName event : active keybinding}.

        Events come kutoka default config extension_cfgBindings section.
        Keybindings come kutoka GetCurrentKeySet() active key dict,
        where previously used bindings are disabled.
        """
        keysName = extensionName + '_cfgBindings'
        activeKeys = self.GetCurrentKeySet()
        extKeys = {}
        ikiwa self.defaultCfg['extensions'].has_section(keysName):
            eventNames = self.defaultCfg['extensions'].GetOptionList(keysName)
            for eventName in eventNames:
                event = '<<' + eventName + '>>'
                binding = activeKeys[event]
                extKeys[event] = binding
        rudisha extKeys

    eleza __GetRawExtensionKeys(self,extensionName):
        """Return dict {configurable extensionName event : keybinding list}.

        Events come kutoka default config extension_cfgBindings section.
        Keybindings list come kutoka the splitting of GetOption, which
        tries user config before default config.
        """
        keysName = extensionName+'_cfgBindings'
        extKeys = {}
        ikiwa self.defaultCfg['extensions'].has_section(keysName):
            eventNames = self.defaultCfg['extensions'].GetOptionList(keysName)
            for eventName in eventNames:
                binding = self.GetOption(
                        'extensions', keysName, eventName, default='').split()
                event = '<<' + eventName + '>>'
                extKeys[event] = binding
        rudisha extKeys

    eleza GetExtensionBindings(self, extensionName):
        """Return dict {extensionName event : active or defined keybinding}.

        Augment self.GetExtensionKeys(extensionName) with mapping of non-
        configurable events (kutoka default config) to GetOption splits,
        as in self.__GetRawExtensionKeys.
        """
        bindsName = extensionName + '_bindings'
        extBinds = self.GetExtensionKeys(extensionName)
        #add the non-configurable bindings
        ikiwa self.defaultCfg['extensions'].has_section(bindsName):
            eventNames = self.defaultCfg['extensions'].GetOptionList(bindsName)
            for eventName in eventNames:
                binding = self.GetOption(
                        'extensions', bindsName, eventName, default='').split()
                event = '<<' + eventName + '>>'
                extBinds[event] = binding

        rudisha extBinds

    eleza GetKeyBinding(self, keySetName, eventStr):
        """Return the keybinding list for keySetName eventStr.

        keySetName - name of key binding set (config-keys section).
        eventStr - virtual event, including brackets, as in '<<event>>'.
        """
        eventName = eventStr[2:-2] #trim off the angle brackets
        binding = self.GetOption('keys', keySetName, eventName, default='',
                                 warn_on_default=False).split()
        rudisha binding

    eleza GetCurrentKeySet(self):
        "Return CurrentKeys with 'darwin' modifications."
        result = self.GetKeySet(self.CurrentKeys())

        ikiwa sys.platform == "darwin":
            # macOS (OS X) Tk variants do not support the "Alt"
            # keyboard modifier.  Replace it with "Option".
            # TODO (Ned?): the "Option" modifier does not work properly
            #     for Cocoa Tk and XQuartz Tk so we should not use it
            #     in the default 'OSX' keyset.
            for k, v in result.items():
                v2 = [ x.replace('<Alt-', '<Option-') for x in v ]
                ikiwa v != v2:
                    result[k] = v2

        rudisha result

    eleza GetKeySet(self, keySetName):
        """Return event-key dict for keySetName core plus active extensions.

        If a binding defined in an extension is already in use, the
        extension binding is disabled by being set to ''
        """
        keySet = self.GetCoreKeys(keySetName)
        activeExtns = self.GetExtensions(active_only=1)
        for extn in activeExtns:
            extKeys = self.__GetRawExtensionKeys(extn)
            ikiwa extKeys: #the extension defines keybindings
                for event in extKeys:
                    ikiwa extKeys[event] in keySet.values():
                        #the binding is already in use
                        extKeys[event] = '' #disable this binding
                    keySet[event] = extKeys[event] #add binding
        rudisha keySet

    eleza IsCoreBinding(self, virtualEvent):
        """Return True ikiwa the virtual event is one of the core idle key events.

        virtualEvent - string, name of the virtual event to test for,
                       without the enclosing '<< >>'
        """
        rudisha ('<<'+virtualEvent+'>>') in self.GetCoreKeys()

# TODO make keyBindins a file or kundi attribute used for test above
# and copied in function below.

    former_extension_events = {  #  Those with user-configurable keys.
        '<<force-open-completions>>', '<<expand-word>>',
        '<<force-open-calltip>>', '<<flash-paren>>', '<<format-paragraph>>',
         '<<run-module>>', '<<check-module>>', '<<zoom-height>>',
         '<<run-custom>>',
         }

    eleza GetCoreKeys(self, keySetName=None):
        """Return dict of core virtual-key keybindings for keySetName.

        The default keySetName None corresponds to the keyBindings base
        dict. If keySetName is not None, bindings kutoka the config
        file(s) are loaded _over_ these defaults, so ikiwa there is a
        problem getting any core binding there will be an 'ultimate last
        resort fallback' to the CUA-ish bindings defined here.
        """
        keyBindings={
            '<<copy>>': ['<Control-c>', '<Control-C>'],
            '<<cut>>': ['<Control-x>', '<Control-X>'],
            '<<paste>>': ['<Control-v>', '<Control-V>'],
            '<<beginning-of-line>>': ['<Control-a>', '<Home>'],
            '<<center-insert>>': ['<Control-l>'],
            '<<close-all-windows>>': ['<Control-q>'],
            '<<close-window>>': ['<Alt-F4>'],
            '<<do-nothing>>': ['<Control-x>'],
            '<<end-of-file>>': ['<Control-d>'],
            '<<python-docs>>': ['<F1>'],
            '<<python-context-help>>': ['<Shift-F1>'],
            '<<history-next>>': ['<Alt-n>'],
            '<<history-previous>>': ['<Alt-p>'],
            '<<interrupt-execution>>': ['<Control-c>'],
            '<<view-restart>>': ['<F6>'],
            '<<restart-shell>>': ['<Control-F6>'],
            '<<open-class-browser>>': ['<Alt-c>'],
            '<<open-module>>': ['<Alt-m>'],
            '<<open-new-window>>': ['<Control-n>'],
            '<<open-window-kutoka-file>>': ['<Control-o>'],
            '<<plain-newline-and-indent>>': ['<Control-j>'],
            '<<print-window>>': ['<Control-p>'],
            '<<redo>>': ['<Control-y>'],
            '<<remove-selection>>': ['<Escape>'],
            '<<save-copy-of-window-as-file>>': ['<Alt-Shift-S>'],
            '<<save-window-as-file>>': ['<Alt-s>'],
            '<<save-window>>': ['<Control-s>'],
            '<<select-all>>': ['<Alt-a>'],
            '<<toggle-auto-coloring>>': ['<Control-slash>'],
            '<<undo>>': ['<Control-z>'],
            '<<find-again>>': ['<Control-g>', '<F3>'],
            '<<find-in-files>>': ['<Alt-F3>'],
            '<<find-selection>>': ['<Control-F3>'],
            '<<find>>': ['<Control-f>'],
            '<<replace>>': ['<Control-h>'],
            '<<goto-line>>': ['<Alt-g>'],
            '<<smart-backspace>>': ['<Key-BackSpace>'],
            '<<newline-and-indent>>': ['<Key-Return>', '<Key-KP_Enter>'],
            '<<smart-indent>>': ['<Key-Tab>'],
            '<<indent-region>>': ['<Control-Key-bracketright>'],
            '<<dedent-region>>': ['<Control-Key-bracketleft>'],
            '<<comment-region>>': ['<Alt-Key-3>'],
            '<<uncomment-region>>': ['<Alt-Key-4>'],
            '<<tabify-region>>': ['<Alt-Key-5>'],
            '<<untabify-region>>': ['<Alt-Key-6>'],
            '<<toggle-tabs>>': ['<Alt-Key-t>'],
            '<<change-indentwidth>>': ['<Alt-Key-u>'],
            '<<del-word-left>>': ['<Control-Key-BackSpace>'],
            '<<del-word-right>>': ['<Control-Key-Delete>'],
            '<<force-open-completions>>': ['<Control-Key-space>'],
            '<<expand-word>>': ['<Alt-Key-slash>'],
            '<<force-open-calltip>>': ['<Control-Key-backslash>'],
            '<<flash-paren>>': ['<Control-Key-0>'],
            '<<format-paragraph>>': ['<Alt-Key-q>'],
            '<<run-module>>': ['<Key-F5>'],
            '<<run-custom>>': ['<Shift-Key-F5>'],
            '<<check-module>>': ['<Alt-Key-x>'],
            '<<zoom-height>>': ['<Alt-Key-2>'],
            }

        ikiwa keySetName:
            ikiwa not (self.userCfg['keys'].has_section(keySetName) or
                    self.defaultCfg['keys'].has_section(keySetName)):
                warning = (
                    '\n Warning: config.py - IdleConf.GetCoreKeys -\n'
                    ' key set %r is not defined, using default bindings.' %
                    (keySetName,)
                )
                _warn(warning, 'keys', keySetName)
            else:
                for event in keyBindings:
                    binding = self.GetKeyBinding(keySetName, event)
                    ikiwa binding:
                        keyBindings[event] = binding
                    # Otherwise rudisha default in keyBindings.
                    elikiwa event not in self.former_extension_events:
                        warning = (
                            '\n Warning: config.py - IdleConf.GetCoreKeys -\n'
                            ' problem retrieving key binding for event %r\n'
                            ' kutoka key set %r.\n'
                            ' returning default value: %r' %
                            (event, keySetName, keyBindings[event])
                        )
                        _warn(warning, 'keys', keySetName, event)
        rudisha keyBindings

    eleza GetExtraHelpSourceList(self, configSet):
        """Return list of extra help sources kutoka a given configSet.

        Valid configSets are 'user' or 'default'.  Return a list of tuples of
        the form (menu_item , path_to_help_file , option), or rudisha the empty
        list.  'option' is the sequence number of the help resource.  'option'
        values determine the position of the menu items on the Help menu,
        therefore the returned list must be sorted by 'option'.

        """
        helpSources = []
        ikiwa configSet == 'user':
            cfgParser = self.userCfg['main']
        elikiwa configSet == 'default':
            cfgParser = self.defaultCfg['main']
        else:
            raise InvalidConfigSet('Invalid configSet specified')
        options=cfgParser.GetOptionList('HelpFiles')
        for option in options:
            value=cfgParser.Get('HelpFiles', option, default=';')
            ikiwa value.find(';') == -1: #malformed config entry with no ';'
                menuItem = '' #make these empty
                helpPath = '' #so value won't be added to list
            else: #config entry contains ';' as expected
                value=value.split(';')
                menuItem=value[0].strip()
                helpPath=value[1].strip()
            ikiwa menuItem and helpPath: #neither are empty strings
                helpSources.append( (menuItem,helpPath,option) )
        helpSources.sort(key=lambda x: x[2])
        rudisha helpSources

    eleza GetAllExtraHelpSourcesList(self):
        """Return a list of the details of all additional help sources.

        Tuples in the list are those of GetExtraHelpSourceList.
        """
        allHelpSources = (self.GetExtraHelpSourceList('default') +
                self.GetExtraHelpSourceList('user') )
        rudisha allHelpSources

    eleza GetFont(self, root, configType, section):
        """Retrieve a font kutoka configuration (font, font-size, font-bold)
        Intercept the special value 'TkFixedFont' and substitute
        the actual font, factoring in some tweaks ikiwa needed for
        appearance sakes.

        The 'root' parameter can normally be any valid Tkinter widget.

        Return a tuple (family, size, weight) suitable for passing
        to tkinter.Font
        """
        family = self.GetOption(configType, section, 'font', default='courier')
        size = self.GetOption(configType, section, 'font-size', type='int',
                              default='10')
        bold = self.GetOption(configType, section, 'font-bold', default=0,
                              type='bool')
        ikiwa (family == 'TkFixedFont'):
            f = Font(name='TkFixedFont', exists=True, root=root)
            actualFont = Font.actual(f)
            family = actualFont['family']
            size = actualFont['size']
            ikiwa size <= 0:
                size = 10  # ikiwa font in pixels, ignore actual size
            bold = actualFont['weight'] == 'bold'
        rudisha (family, size, 'bold' ikiwa bold else 'normal')

    eleza LoadCfgFiles(self):
        "Load all configuration files."
        for key in self.defaultCfg:
            self.defaultCfg[key].Load()
            self.userCfg[key].Load() #same keys

    eleza SaveUserCfgFiles(self):
        "Write all loaded user configuration files to disk."
        for key in self.userCfg:
            self.userCfg[key].Save()


idleConf = IdleConf()

_warned = set()
eleza _warn(msg, *key):
    key = (msg,) + key
    ikiwa key not in _warned:
        try:
            andika(msg, file=sys.stderr)
        except OSError:
            pass
        _warned.add(key)


kundi ConfigChanges(dict):
    """Manage a user's proposed configuration option changes.

    Names used across multiple methods:
        page -- one of the 4 top-level dicts representing a
                .idlerc/config-x.cfg file.
        config_type -- name of a page.
        section -- a section within a page/file.
        option -- name of an option within a section.
        value -- value for the option.

    Methods
        add_option: Add option and value to changes.
        save_option: Save option and value to config parser.
        save_all: Save all the changes to the config parser and file.
        delete_section: If section exists,
                        delete kutoka changes, userCfg, and file.
        clear: Clear all changes by clearing each page.
    """
    eleza __init__(self):
        "Create a page for each configuration file"
        self.pages = []  # List of unhashable dicts.
        for config_type in idleConf.config_types:
            self[config_type] = {}
            self.pages.append(self[config_type])

    eleza add_option(self, config_type, section, item, value):
        "Add item/value pair for config_type and section."
        page = self[config_type]
        value = str(value)  # Make sure we use a string.
        ikiwa section not in page:
            page[section] = {}
        page[section][item] = value

    @staticmethod
    eleza save_option(config_type, section, item, value):
        """Return True ikiwa the configuration value was added or changed.

        Helper for save_all.
        """
        ikiwa idleConf.defaultCfg[config_type].has_option(section, item):
            ikiwa idleConf.defaultCfg[config_type].Get(section, item) == value:
                # The setting equals a default setting, remove it kutoka user cfg.
                rudisha idleConf.userCfg[config_type].RemoveOption(section, item)
        # If we got here, set the option.
        rudisha idleConf.userCfg[config_type].SetOption(section, item, value)

    eleza save_all(self):
        """Save configuration changes to the user config file.

        Clear self in preparation for additional changes.
        Return changed for testing.
        """
        idleConf.userCfg['main'].Save()

        changed = False
        for config_type in self:
            cfg_type_changed = False
            page = self[config_type]
            for section in page:
                ikiwa section == 'HelpFiles':  # Remove it for replacement.
                    idleConf.userCfg['main'].remove_section('HelpFiles')
                    cfg_type_changed = True
                for item, value in page[section].items():
                    ikiwa self.save_option(config_type, section, item, value):
                        cfg_type_changed = True
            ikiwa cfg_type_changed:
                idleConf.userCfg[config_type].Save()
                changed = True
        for config_type in ['keys', 'highlight']:
            # Save these even ikiwa unchanged!
            idleConf.userCfg[config_type].Save()
        self.clear()
        # ConfigDialog caller must add the following call
        # self.save_all_changed_extensions()  # Uses a different mechanism.
        rudisha changed

    eleza delete_section(self, config_type, section):
        """Delete a section kutoka self, userCfg, and file.

        Used to delete custom themes and keysets.
        """
        ikiwa section in self[config_type]:
            del self[config_type][section]
        configpage = idleConf.userCfg[config_type]
        configpage.remove_section(section)
        configpage.Save()

    eleza clear(self):
        """Clear all 4 pages.

        Called in save_all after saving to idleConf.
        XXX Mark window *title* when there are changes; unmark here.
        """
        for page in self.pages:
            page.clear()


# TODO Revise test output, write expanded unittest
eleza _dump():  # htest # (not really, but ignore in coverage)
    kutoka zlib agiza crc32
    line, crc = 0, 0

    eleza sandika(obj):
        global line, crc
        txt = str(obj)
        line += 1
        crc = crc32(txt.encode(encoding='utf-8'), crc)
        andika(txt)
        #andika('***', line, crc, '***')  # Uncomment for diagnosis.

    eleza dumpCfg(cfg):
        andika('\n', cfg, '\n')  # Cfg has variable '0xnnnnnnnn' address.
        for key in sorted(cfg.keys()):
            sections = cfg[key].sections()
            sandika(key)
            sandika(sections)
            for section in sections:
                options = cfg[key].options(section)
                sandika(section)
                sandika(options)
                for option in options:
                    sandika(option + ' = ' + cfg[key].Get(section, option))

    dumpCfg(idleConf.defaultCfg)
    dumpCfg(idleConf.userCfg)
    andika('\nlines = ', line, ', crc = ', crc, sep='')

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_config', verbosity=2, exit=False)

    # Run revised _dump() as htest?
