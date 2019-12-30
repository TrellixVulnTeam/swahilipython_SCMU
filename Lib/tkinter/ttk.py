"""Ttk wrapper.

This module provides classes to allow using Tk themed widget set.

Ttk ni based on a revised na enhanced version of
TIP #48 (http://tip.tcl.tk/48) specified style engine.

Its basic idea ni to separate, to the extent possible, the code
implementing a widget's behavior kutoka the code implementing its
appearance. Widget kundi bindings are primarily responsible for
maintaining the widget state na invoking callbacks, all aspects
of the widgets appearance lies at Themes.
"""

__version__ = "0.3.1"

__author__ = "Guilherme Polo <ggpolo@gmail.com>"

__all__ = ["Button", "Checkbutton", "Combobox", "Entry", "Frame", "Label",
           "Labelframe", "LabelFrame", "Menubutton", "Notebook", "Panedwindow",
           "PanedWindow", "Progressbar", "Radiobutton", "Scale", "Scrollbar",
           "Separator", "Sizegrip", "Spinbox", "Style", "Treeview",
           # Extensions
           "LabeledScale", "OptionMenu",
           # functions
           "tclobjs_to_py", "setup_master"]

agiza tkinter
kutoka tkinter agiza _flatten, _join, _stringify, _splitdict

# Verify ikiwa Tk ni new enough to sio need the Tile package
_REQUIRE_TILE = Kweli ikiwa tkinter.TkVersion < 8.5 isipokua Uongo

eleza _load_tile(master):
    ikiwa _REQUIRE_TILE:
        agiza os
        tilelib = os.environ.get('TILE_LIBRARY')
        ikiwa tilelib:
            # append custom tile path to the list of directories that
            # Tcl uses when attempting to resolve packages ukijumuisha the package
            # command
            master.tk.eval(
                    'global auto_path; '
                    'lappend auto_path {%s}' % tilelib)

        master.tk.eval('package require tile') # TclError may be raised here
        master._tile_loaded = Kweli

eleza _format_optvalue(value, script=Uongo):
    """Internal function."""
    ikiwa script:
        # ikiwa caller pitaes a Tcl script to tk.call, all the values need to
        # be grouped into words (arguments to a command kwenye Tcl dialect)
        value = _stringify(value)
    lasivyo isinstance(value, (list, tuple)):
        value = _join(value)
    rudisha value

eleza _format_optdict(optdict, script=Uongo, ignore=Tupu):
    """Formats optdict to a tuple to pita it to tk.call.

    E.g. (script=Uongo):
      {'foreground': 'blue', 'padding': [1, 2, 3, 4]} returns:
      ('-foreground', 'blue', '-padding', '1 2 3 4')"""

    opts = []
    kila opt, value kwenye optdict.items():
        ikiwa sio ignore ama opt haiko kwenye ignore:
            opts.append("-%s" % opt)
            ikiwa value ni sio Tupu:
                opts.append(_format_optvalue(value, script))

    rudisha _flatten(opts)

eleza _mapdict_values(items):
    # each value kwenye mapdict ni expected to be a sequence, where each item
    # ni another sequence containing a state (or several) na a value
    # E.g. (script=Uongo):
    #   [('active', 'selected', 'grey'), ('focus', [1, 2, 3, 4])]
    #   returns:
    #   ['active selected', 'grey', 'focus', [1, 2, 3, 4]]
    opt_val = []
    kila *state, val kwenye items:
        # hacks kila backward compatibility
        state[0] # ashiria IndexError ikiwa empty
        ikiwa len(state) == 1:
            # ikiwa it ni empty (something that evaluates to Uongo), then
            # format it to Tcl code to denote the "normal" state
            state = state[0] ama ''
        isipokua:
            # group multiple states
            state = ' '.join(state) # ashiria TypeError ikiwa sio str
        opt_val.append(state)
        ikiwa val ni sio Tupu:
            opt_val.append(val)
    rudisha opt_val

eleza _format_mapdict(mapdict, script=Uongo):
    """Formats mapdict to pita it to tk.call.

    E.g. (script=Uongo):
      {'expand': [('active', 'selected', 'grey'), ('focus', [1, 2, 3, 4])]}

      returns:

      ('-expand', '{active selected} grey focus {1, 2, 3, 4}')"""

    opts = []
    kila opt, value kwenye mapdict.items():
        opts.extend(("-%s" % opt,
                     _format_optvalue(_mapdict_values(value), script)))

    rudisha _flatten(opts)

eleza _format_elemcreate(etype, script=Uongo, *args, **kw):
    """Formats args na kw according to the given element factory etype."""
    spec = Tupu
    opts = ()
    ikiwa etype kwenye ("image", "vsapi"):
        ikiwa etype == "image": # define an element based on an image
            # first arg should be the default image name
            iname = args[0]
            # next args, ikiwa any, are statespec/value pairs which ni almost
            # a mapdict, but we just need the value
            imagespec = _join(_mapdict_values(args[1:]))
            spec = "%s %s" % (iname, imagespec)

        isipokua:
            # define an element whose visual appearance ni drawn using the
            # Microsoft Visual Styles API which ni responsible kila the
            # themed styles on Windows XP na Vista.
            # Availability: Tk 8.6, Windows XP na Vista.
            class_name, part_id = args[:2]
            statemap = _join(_mapdict_values(args[2:]))
            spec = "%s %s %s" % (class_name, part_id, statemap)

        opts = _format_optdict(kw, script)

    lasivyo etype == "from": # clone an element
        # it expects a themename na optionally an element to clone from,
        # otherwise it will clone {} (empty element)
        spec = args[0] # theme name
        ikiwa len(args) > 1: # elementkutoka specified
            opts = (_format_optvalue(args[1], script),)

    ikiwa script:
        spec = '{%s}' % spec
        opts = ' '.join(opts)

    rudisha spec, opts

eleza _format_layoutlist(layout, indent=0, indent_size=2):
    """Formats a layout list so we can pita the result to ttk::style
    layout na ttk::style settings. Note that the layout doesn't have to
    be a list necessarily.

    E.g.:
      [("Menubutton.background", Tupu),
       ("Menubutton.button", {"children":
           [("Menubutton.focus", {"children":
               [("Menubutton.padding", {"children":
                [("Menubutton.label", {"side": "left", "expand": 1})]
               })]
           })]
       }),
       ("Menubutton.indicator", {"side": "right"})
      ]

      returns:

      Menubutton.background
      Menubutton.button -children {
        Menubutton.focus -children {
          Menubutton.padding -children {
            Menubutton.label -side left -expand 1
          }
        }
      }
      Menubutton.indicator -side right"""
    script = []

    kila layout_elem kwenye layout:
        elem, opts = layout_elem
        opts = opts ama {}
        fopts = ' '.join(_format_optdict(opts, Kweli, ("children",)))
        head = "%s%s%s" % (' ' * indent, elem, (" %s" % fopts) ikiwa fopts isipokua '')

        ikiwa "children" kwenye opts:
            script.append(head + " -children {")
            indent += indent_size
            newscript, indent = _format_layoutlist(opts['children'], indent,
                indent_size)
            script.append(newscript)
            indent -= indent_size
            script.append('%s}' % (' ' * indent))
        isipokua:
            script.append(head)

    rudisha '\n'.join(script), indent

eleza _script_from_settings(settings):
    """Returns an appropriate script, based on settings, according to
    theme_settings definition to be used by theme_settings na
    theme_create."""
    script = []
    # a script will be generated according to settings pitaed, which
    # will then be evaluated by Tcl
    kila name, opts kwenye settings.items():
        # will format specific keys according to Tcl code
        ikiwa opts.get('configure'): # format 'configure'
            s = ' '.join(_format_optdict(opts['configure'], Kweli))
            script.append("ttk::style configure %s %s;" % (name, s))

        ikiwa opts.get('map'): # format 'map'
            s = ' '.join(_format_mapdict(opts['map'], Kweli))
            script.append("ttk::style map %s %s;" % (name, s))

        ikiwa 'layout' kwenye opts: # format 'layout' which may be empty
            ikiwa sio opts['layout']:
                s = 'null' # could be any other word, but this one makes sense
            isipokua:
                s, _ = _format_layoutlist(opts['layout'])
            script.append("ttk::style layout %s {\n%s\n}" % (name, s))

        ikiwa opts.get('element create'): # format 'element create'
            eopts = opts['element create']
            etype = eopts[0]

            # find where args end, na where kwargs start
            argc = 1 # etype was the first one
            wakati argc < len(eopts) na sio hasattr(eopts[argc], 'items'):
                argc += 1

            elemargs = eopts[1:argc]
            elemkw = eopts[argc] ikiwa argc < len(eopts) na eopts[argc] isipokua {}
            spec, opts = _format_elemcreate(etype, Kweli, *elemargs, **elemkw)

            script.append("ttk::style element create %s %s %s %s" % (
                name, etype, spec, opts))

    rudisha '\n'.join(script)

eleza _list_from_statespec(stuple):
    """Construct a list kutoka the given statespec tuple according to the
    accepted statespec accepted by _format_mapdict."""
    nval = []
    kila val kwenye stuple:
        typename = getattr(val, 'typename', Tupu)
        ikiwa typename ni Tupu:
            nval.append(val)
        isipokua: # this ni a Tcl object
            val = str(val)
            ikiwa typename == 'StateSpec':
                val = val.split()
            nval.append(val)

    it = iter(nval)
    rudisha [_flatten(spec) kila spec kwenye zip(it, it)]

eleza _list_from_layouttuple(tk, ltuple):
    """Construct a list kutoka the tuple returned by ttk::layout, this is
    somewhat the reverse of _format_layoutlist."""
    ltuple = tk.splitlist(ltuple)
    res = []

    indx = 0
    wakati indx < len(ltuple):
        name = ltuple[indx]
        opts = {}
        res.append((name, opts))
        indx += 1

        wakati indx < len(ltuple): # grab name's options
            opt, val = ltuple[indx:indx + 2]
            ikiwa sio opt.startswith('-'): # found next name
                koma

            opt = opt[1:] # remove the '-' kutoka the option
            indx += 2

            ikiwa opt == 'children':
                val = _list_from_layouttuple(tk, val)

            opts[opt] = val

    rudisha res

eleza _val_or_dict(tk, options, *args):
    """Format options then call Tk command ukijumuisha args na options na return
    the appropriate result.

    If no option ni specified, a dict ni returned. If an option is
    specified ukijumuisha the Tupu value, the value kila that option ni returned.
    Otherwise, the function just sets the pitaed options na the caller
    shouldn't be expecting a rudisha value anyway."""
    options = _format_optdict(options)
    res = tk.call(*(args + options))

    ikiwa len(options) % 2: # option specified without a value, rudisha its value
        rudisha res

    rudisha _splitdict(tk, res, conv=_tclobj_to_py)

eleza _convert_stringval(value):
    """Converts a value to, hopefully, a more appropriate Python object."""
    value = str(value)
    jaribu:
        value = int(value)
    tatizo (ValueError, TypeError):
        pita

    rudisha value

eleza _to_number(x):
    ikiwa isinstance(x, str):
        ikiwa '.' kwenye x:
            x = float(x)
        isipokua:
            x = int(x)
    rudisha x

eleza _tclobj_to_py(val):
    """Return value converted kutoka Tcl object to Python object."""
    ikiwa val na hasattr(val, '__len__') na sio isinstance(val, str):
        ikiwa getattr(val[0], 'typename', Tupu) == 'StateSpec':
            val = _list_from_statespec(val)
        isipokua:
            val = list(map(_convert_stringval, val))

    lasivyo hasattr(val, 'typename'): # some other (single) Tcl object
        val = _convert_stringval(val)

    rudisha val

eleza tclobjs_to_py(adict):
    """Returns adict ukijumuisha its values converted kutoka Tcl objects to Python
    objects."""
    kila opt, val kwenye adict.items():
        adict[opt] = _tclobj_to_py(val)

    rudisha adict

eleza setup_master(master=Tupu):
    """If master ni sio Tupu, itself ni returned. If master ni Tupu,
    the default master ni returned ikiwa there ni one, otherwise a new
    master ni created na returned.

    If it ni sio allowed to use the default root na master ni Tupu,
    RuntimeError ni raised."""
    ikiwa master ni Tupu:
        ikiwa tkinter._support_default_root:
            master = tkinter._default_root ama tkinter.Tk()
        isipokua:
            ashiria RuntimeError(
                    "No master specified na tkinter ni "
                    "configured to sio support default root")
    rudisha master


kundi Style(object):
    """Manipulate style database."""

    _name = "ttk::style"

    eleza __init__(self, master=Tupu):
        master = setup_master(master)

        ikiwa sio getattr(master, '_tile_loaded', Uongo):
            # Load tile now, ikiwa needed
            _load_tile(master)

        self.master = master
        self.tk = self.master.tk


    eleza configure(self, style, query_opt=Tupu, **kw):
        """Query ama sets the default value of the specified option(s) in
        style.

        Each key kwenye kw ni an option na each value ni either a string ama
        a sequence identifying the value kila that option."""
        ikiwa query_opt ni sio Tupu:
            kw[query_opt] = Tupu
        result = _val_or_dict(self.tk, kw, self._name, "configure", style)
        ikiwa result ama query_opt:
            rudisha result


    eleza map(self, style, query_opt=Tupu, **kw):
        """Query ama sets dynamic values of the specified option(s) in
        style.

        Each key kwenye kw ni an option na each value should be a list ama a
        tuple (usually) containing statespecs grouped kwenye tuples, ama list,
        ama something isipokua of your preference. A statespec ni compound of
        one ama more states na then a value."""
        ikiwa query_opt ni sio Tupu:
            rudisha _list_from_statespec(self.tk.splitlist(
                self.tk.call(self._name, "map", style, '-%s' % query_opt)))

        rudisha _splitdict(
            self.tk,
            self.tk.call(self._name, "map", style, *_format_mapdict(kw)),
            conv=_tclobj_to_py)


    eleza lookup(self, style, option, state=Tupu, default=Tupu):
        """Returns the value specified kila option kwenye style.

        If state ni specified it ni expected to be a sequence of one
        ama more states. If the default argument ni set, it ni used as
        a fallback value kwenye case no specification kila option ni found."""
        state = ' '.join(state) ikiwa state isipokua ''

        rudisha self.tk.call(self._name, "lookup", style, '-%s' % option,
            state, default)


    eleza layout(self, style, layoutspec=Tupu):
        """Define the widget layout kila given style. If layoutspec is
        omitted, rudisha the layout specification kila given style.

        layoutspec ni expected to be a list ama an object different than
        Tupu that evaluates to Uongo ikiwa you want to "turn off" that style.
        If it ni a list (or tuple, ama something else), each item should be
        a tuple where the first item ni the layout name na the second item
        should have the format described below:

        LAYOUTS

            A layout can contain the value Tupu, ikiwa takes no options, ama
            a dict of options specifying how to arrange the element.
            The layout mechanism uses a simplified version of the pack
            geometry manager: given an initial cavity, each element is
            allocated a parcel. Valid options/values are:

                side: whichside
                    Specifies which side of the cavity to place the
                    element; one of top, right, bottom ama left. If
                    omitted, the element occupies the entire cavity.

                sticky: nswe
                    Specifies where the element ni placed inside its
                    allocated parcel.

                children: [sublayout... ]
                    Specifies a list of elements to place inside the
                    element. Each element ni a tuple (or other sequence)
                    where the first item ni the layout name, na the other
                    ni a LAYOUT."""
        lspec = Tupu
        ikiwa layoutspec:
            lspec = _format_layoutlist(layoutspec)[0]
        lasivyo layoutspec ni sio Tupu: # will disable the layout ({}, '', etc)
            lspec = "null" # could be any other word, but this may make sense
                           # when calling layout(style) later

        rudisha _list_from_layouttuple(self.tk,
            self.tk.call(self._name, "layout", style, lspec))


    eleza element_create(self, elementname, etype, *args, **kw):
        """Create a new element kwenye the current theme of given etype."""
        spec, opts = _format_elemcreate(etype, Uongo, *args, **kw)
        self.tk.call(self._name, "element", "create", elementname, etype,
            spec, *opts)


    eleza element_names(self):
        """Returns the list of elements defined kwenye the current theme."""
        rudisha tuple(n.lstrip('-') kila n kwenye self.tk.splitlist(
            self.tk.call(self._name, "element", "names")))


    eleza element_options(self, elementname):
        """Return the list of elementname's options."""
        rudisha tuple(o.lstrip('-') kila o kwenye self.tk.splitlist(
            self.tk.call(self._name, "element", "options", elementname)))


    eleza theme_create(self, themename, parent=Tupu, settings=Tupu):
        """Creates a new theme.

        It ni an error ikiwa themename already exists. If parent is
        specified, the new theme will inherit styles, elements na
        layouts kutoka the specified parent theme. If settings are present,
        they are expected to have the same syntax used kila theme_settings."""
        script = _script_from_settings(settings) ikiwa settings isipokua ''

        ikiwa parent:
            self.tk.call(self._name, "theme", "create", themename,
                "-parent", parent, "-settings", script)
        isipokua:
            self.tk.call(self._name, "theme", "create", themename,
                "-settings", script)


    eleza theme_settings(self, themename, settings):
        """Temporarily sets the current theme to themename, apply specified
        settings na then restore the previous theme.

        Each key kwenye settings ni a style na each value may contain the
        keys 'configure', 'map', 'layout' na 'element create' na they
        are expected to have the same format kama specified by the methods
        configure, map, layout na element_create respectively."""
        script = _script_from_settings(settings)
        self.tk.call(self._name, "theme", "settings", themename, script)


    eleza theme_names(self):
        """Returns a list of all known themes."""
        rudisha self.tk.splitlist(self.tk.call(self._name, "theme", "names"))


    eleza theme_use(self, themename=Tupu):
        """If themename ni Tupu, returns the theme kwenye use, otherwise, set
        the current theme to themename, refreshes all widgets na emits
        a <<ThemeChanged>> event."""
        ikiwa themename ni Tupu:
            # Starting on Tk 8.6, checking this global ni no longer needed
            # since it allows doing self.tk.call(self._name, "theme", "use")
            rudisha self.tk.eval("rudisha $ttk::currentTheme")

        # using "ttk::setTheme" instead of "ttk::style theme use" causes
        # the variable currentTheme to be updated, also, ttk::setTheme calls
        # "ttk::style theme use" kwenye order to change theme.
        self.tk.call("ttk::setTheme", themename)


kundi Widget(tkinter.Widget):
    """Base kundi kila Tk themed widgets."""

    eleza __init__(self, master, widgetname, kw=Tupu):
        """Constructs a Ttk Widget ukijumuisha the parent master.

        STANDARD OPTIONS

            class, cursor, takefocus, style

        SCROLLABLE WIDGET OPTIONS

            xscrollcommand, yscrollcommand

        LABEL WIDGET OPTIONS

            text, textvariable, underline, image, compound, width

        WIDGET STATES

            active, disabled, focus, pressed, selected, background,
            readonly, alternate, invalid
        """
        master = setup_master(master)
        ikiwa sio getattr(master, '_tile_loaded', Uongo):
            # Load tile now, ikiwa needed
            _load_tile(master)
        tkinter.Widget.__init__(self, master, widgetname, kw=kw)


    eleza identify(self, x, y):
        """Returns the name of the element at position x, y, ama the empty
        string ikiwa the point does sio lie within any element.

        x na y are pixel coordinates relative to the widget."""
        rudisha self.tk.call(self._w, "identify", x, y)


    eleza instate(self, statespec, callback=Tupu, *args, **kw):
        """Test the widget's state.

        If callback ni sio specified, returns Kweli ikiwa the widget state
        matches statespec na Uongo otherwise. If callback ni specified,
        then it will be invoked ukijumuisha *args, **kw ikiwa the widget state
        matches statespec. statespec ni expected to be a sequence."""
        ret = self.tk.getboolean(
                self.tk.call(self._w, "instate", ' '.join(statespec)))
        ikiwa ret na callback:
            rudisha callback(*args, **kw)

        rudisha ret


    eleza state(self, statespec=Tupu):
        """Modify ama inquire widget state.

        Widget state ni returned ikiwa statespec ni Tupu, otherwise it is
        set according to the statespec flags na then a new state spec
        ni returned indicating which flags were changed. statespec is
        expected to be a sequence."""
        ikiwa statespec ni sio Tupu:
            statespec = ' '.join(statespec)

        rudisha self.tk.splitlist(str(self.tk.call(self._w, "state", statespec)))


kundi Button(Widget):
    """Ttk Button widget, displays a textual label and/or image, na
    evaluates a command when pressed."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Button widget ukijumuisha the parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, state, style, takefocus,
            text, textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            command, default, width
        """
        Widget.__init__(self, master, "ttk::button", kw)


    eleza invoke(self):
        """Invokes the command associated ukijumuisha the button."""
        rudisha self.tk.call(self._w, "invoke")


kundi Checkbutton(Widget):
    """Ttk Checkbutton widget which ni either kwenye on- ama off-state."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Checkbutton widget ukijumuisha the parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, state, style, takefocus,
            text, textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            command, offvalue, onvalue, variable
        """
        Widget.__init__(self, master, "ttk::checkbutton", kw)


    eleza invoke(self):
        """Toggles between the selected na deselected states na
        invokes the associated command. If the widget ni currently
        selected, sets the option variable to the offvalue option
        na deselects the widget; otherwise, sets the option variable
        to the option onvalue.

        Returns the result of the associated command."""
        rudisha self.tk.call(self._w, "invoke")


kundi Entry(Widget, tkinter.Entry):
    """Ttk Entry widget displays a one-line text string na allows that
    string to be edited by the user."""

    eleza __init__(self, master=Tupu, widget=Tupu, **kw):
        """Constructs a Ttk Entry widget ukijumuisha the parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus, xscrollcommand

        WIDGET-SPECIFIC OPTIONS

            exportselection, invalidcommand, justify, show, state,
            textvariable, validate, validatecommand, width

        VALIDATION MODES

            none, key, focus, focusin, focusout, all
        """
        Widget.__init__(self, master, widget ama "ttk::entry", kw)


    eleza bbox(self, index):
        """Return a tuple of (x, y, width, height) which describes the
        bounding box of the character given by index."""
        rudisha self._getints(self.tk.call(self._w, "bbox", index))


    eleza identify(self, x, y):
        """Returns the name of the element at position x, y, ama the
        empty string ikiwa the coordinates are outside the window."""
        rudisha self.tk.call(self._w, "identify", x, y)


    eleza validate(self):
        """Force revalidation, independent of the conditions specified
        by the validate option. Returns Uongo ikiwa validation fails, Kweli
        ikiwa it succeeds. Sets ama clears the invalid state accordingly."""
        rudisha self.tk.getboolean(self.tk.call(self._w, "validate"))


kundi Combobox(Entry):
    """Ttk Combobox widget combines a text field ukijumuisha a pop-down list of
    values."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Combobox widget ukijumuisha the parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            exportselection, justify, height, postcommand, state,
            textvariable, values, width
        """
        Entry.__init__(self, master, "ttk::combobox", **kw)


    eleza current(self, newindex=Tupu):
        """If newindex ni supplied, sets the combobox value to the
        element at position newindex kwenye the list of values. Otherwise,
        returns the index of the current value kwenye the list of values
        ama -1 ikiwa the current value does sio appear kwenye the list."""
        ikiwa newindex ni Tupu:
            rudisha self.tk.getint(self.tk.call(self._w, "current"))
        rudisha self.tk.call(self._w, "current", newindex)


    eleza set(self, value):
        """Sets the value of the combobox to value."""
        self.tk.call(self._w, "set", value)


kundi Frame(Widget):
    """Ttk Frame widget ni a container, used to group other widgets
    together."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Frame ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            borderwidth, relief, padding, width, height
        """
        Widget.__init__(self, master, "ttk::frame", kw)


kundi Label(Widget):
    """Ttk Label widget displays a textual label and/or image."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Label ukijumuisha parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, style, takefocus, text,
            textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            anchor, background, font, foreground, justify, padding,
            relief, text, wraplength
        """
        Widget.__init__(self, master, "ttk::label", kw)


kundi Labelframe(Widget):
    """Ttk Labelframe widget ni a container used to group other widgets
    together. It has an optional label, which may be a plain text string
    ama another widget."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Labelframe ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS
            labelanchor, text, underline, padding, labelwidget, width,
            height
        """
        Widget.__init__(self, master, "ttk::labelframe", kw)

LabelFrame = Labelframe # tkinter name compatibility


kundi Menubutton(Widget):
    """Ttk Menubutton widget displays a textual label and/or image, na
    displays a menu when pressed."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Menubutton ukijumuisha parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, state, style, takefocus,
            text, textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            direction, menu
        """
        Widget.__init__(self, master, "ttk::menubutton", kw)


kundi Notebook(Widget):
    """Ttk Notebook widget manages a collection of windows na displays
    a single one at a time. Each child window ni associated ukijumuisha a tab,
    which the user may select to change the currently-displayed window."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Notebook ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            height, padding, width

        TAB OPTIONS

            state, sticky, padding, text, image, compound, underline

        TAB IDENTIFIERS (tab_id)

            The tab_id argument found kwenye several methods may take any of
            the following forms:

                * An integer between zero na the number of tabs
                * The name of a child window
                * A positional specification of the form "@x,y", which
                  defines the tab
                * The string "current", which identifies the
                  currently-selected tab
                * The string "end", which returns the number of tabs (only
                  valid kila method index)
        """
        Widget.__init__(self, master, "ttk::notebook", kw)


    eleza add(self, child, **kw):
        """Adds a new tab to the notebook.

        If window ni currently managed by the notebook but hidden, it is
        restored to its previous position."""
        self.tk.call(self._w, "add", child, *(_format_optdict(kw)))


    eleza forget(self, tab_id):
        """Removes the tab specified by tab_id, unmaps na unmanages the
        associated window."""
        self.tk.call(self._w, "forget", tab_id)


    eleza hide(self, tab_id):
        """Hides the tab specified by tab_id.

        The tab will sio be displayed, but the associated window remains
        managed by the notebook na its configuration remembered. Hidden
        tabs may be restored ukijumuisha the add command."""
        self.tk.call(self._w, "hide", tab_id)


    eleza identify(self, x, y):
        """Returns the name of the tab element at position x, y, ama the
        empty string ikiwa none."""
        rudisha self.tk.call(self._w, "identify", x, y)


    eleza index(self, tab_id):
        """Returns the numeric index of the tab specified by tab_id, ama
        the total number of tabs ikiwa tab_id ni the string "end"."""
        rudisha self.tk.getint(self.tk.call(self._w, "index", tab_id))


    eleza insert(self, pos, child, **kw):
        """Inserts a pane at the specified position.

        pos ni either the string end, an integer index, ama the name of
        a managed child. If child ni already managed by the notebook,
        moves it to the specified position."""
        self.tk.call(self._w, "insert", pos, child, *(_format_optdict(kw)))


    eleza select(self, tab_id=Tupu):
        """Selects the specified tab.

        The associated child window will be displayed, na the
        previously-selected window (ikiwa different) ni unmapped. If tab_id
        ni omitted, returns the widget name of the currently selected
        pane."""
        rudisha self.tk.call(self._w, "select", tab_id)


    eleza tab(self, tab_id, option=Tupu, **kw):
        """Query ama modify the options of the specific tab_id.

        If kw ni sio given, returns a dict of the tab option values. If option
        ni specified, returns the value of that option. Otherwise, sets the
        options to the corresponding values."""
        ikiwa option ni sio Tupu:
            kw[option] = Tupu
        rudisha _val_or_dict(self.tk, kw, self._w, "tab", tab_id)


    eleza tabs(self):
        """Returns a list of windows managed by the notebook."""
        rudisha self.tk.splitlist(self.tk.call(self._w, "tabs") ama ())


    eleza enable_traversal(self):
        """Enable keyboard traversal kila a toplevel window containing
        this notebook.

        This will extend the bindings kila the toplevel window containing
        this notebook kama follows:

            Control-Tab: selects the tab following the currently selected
                         one

            Shift-Control-Tab: selects the tab preceding the currently
                               selected one

            Alt-K: where K ni the mnemonic (underlined) character of any
                   tab, will select that tab.

        Multiple notebooks kwenye a single toplevel may be enabled for
        traversal, including nested notebooks. However, notebook traversal
        only works properly ikiwa all panes are direct children of the
        notebook."""
        # The only, na good, difference I see ni about mnemonics, which works
        # after calling this method. Control-Tab na Shift-Control-Tab always
        # works (here at least).
        self.tk.call("ttk::notebook::enableTraversal", self._w)


kundi Panedwindow(Widget, tkinter.PanedWindow):
    """Ttk Panedwindow widget displays a number of subwindows, stacked
    either vertically ama horizontally."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Panedwindow ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            orient, width, height

        PANE OPTIONS

            weight
        """
        Widget.__init__(self, master, "ttk::panedwindow", kw)


    forget = tkinter.PanedWindow.forget # overrides Pack.forget


    eleza insert(self, pos, child, **kw):
        """Inserts a pane at the specified positions.

        pos ni either the string end, na integer index, ama the name
        of a child. If child ni already managed by the paned window,
        moves it to the specified position."""
        self.tk.call(self._w, "insert", pos, child, *(_format_optdict(kw)))


    eleza pane(self, pane, option=Tupu, **kw):
        """Query ama modify the options of the specified pane.

        pane ni either an integer index ama the name of a managed subwindow.
        If kw ni sio given, returns a dict of the pane option values. If
        option ni specified then the value kila that option ni returned.
        Otherwise, sets the options to the corresponding values."""
        ikiwa option ni sio Tupu:
            kw[option] = Tupu
        rudisha _val_or_dict(self.tk, kw, self._w, "pane", pane)


    eleza sashpos(self, index, newpos=Tupu):
        """If newpos ni specified, sets the position of sash number index.

        May adjust the positions of adjacent sashes to ensure that
        positions are monotonically increasing. Sash positions are further
        constrained to be between 0 na the total size of the widget.

        Returns the new position of sash number index."""
        rudisha self.tk.getint(self.tk.call(self._w, "sashpos", index, newpos))

PanedWindow = Panedwindow # tkinter name compatibility


kundi Progressbar(Widget):
    """Ttk Progressbar widget shows the status of a long-running
    operation. They can operate kwenye two modes: determinate mode shows the
    amount completed relative to the total amount of work to be done, na
    indeterminate mode provides an animated display to let the user know
    that something ni happening."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Progressbar ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            orient, length, mode, maximum, value, variable, phase
        """
        Widget.__init__(self, master, "ttk::progressbar", kw)


    eleza start(self, interval=Tupu):
        """Begin autoincrement mode: schedules a recurring timer event
        that calls method step every interval milliseconds.

        interval defaults to 50 milliseconds (20 steps/second) ikiwa omitted."""
        self.tk.call(self._w, "start", interval)


    eleza step(self, amount=Tupu):
        """Increments the value option by amount.

        amount defaults to 1.0 ikiwa omitted."""
        self.tk.call(self._w, "step", amount)


    eleza stop(self):
        """Stop autoincrement mode: cancels any recurring timer event
        initiated by start."""
        self.tk.call(self._w, "stop")


kundi Radiobutton(Widget):
    """Ttk Radiobutton widgets are used kwenye groups to show ama change a
    set of mutually-exclusive options."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Radiobutton ukijumuisha parent master.

        STANDARD OPTIONS

            class, compound, cursor, image, state, style, takefocus,
            text, textvariable, underline, width

        WIDGET-SPECIFIC OPTIONS

            command, value, variable
        """
        Widget.__init__(self, master, "ttk::radiobutton", kw)


    eleza invoke(self):
        """Sets the option variable to the option value, selects the
        widget, na invokes the associated command.

        Returns the result of the command, ama an empty string if
        no command ni specified."""
        rudisha self.tk.call(self._w, "invoke")


kundi Scale(Widget, tkinter.Scale):
    """Ttk Scale widget ni typically used to control the numeric value of
    a linked variable that varies uniformly over some range."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Scale ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            command, from, length, orient, to, value, variable
        """
        Widget.__init__(self, master, "ttk::scale", kw)


    eleza configure(self, cnf=Tupu, **kw):
        """Modify ama query scale options.

        Setting a value kila any of the "from", "from_" ama "to" options
        generates a <<RangeChanged>> event."""
        ikiwa cnf:
            kw.update(cnf)
        Widget.configure(self, **kw)
        ikiwa any(['from' kwenye kw, 'from_' kwenye kw, 'to' kwenye kw]):
            self.event_generate('<<RangeChanged>>')


    eleza get(self, x=Tupu, y=Tupu):
        """Get the current value of the value option, ama the value
        corresponding to the coordinates x, y ikiwa they are specified.

        x na y are pixel coordinates relative to the scale widget
        origin."""
        rudisha self.tk.call(self._w, 'get', x, y)


kundi Scrollbar(Widget, tkinter.Scrollbar):
    """Ttk Scrollbar controls the viewport of a scrollable widget."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Scrollbar ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            command, orient
        """
        Widget.__init__(self, master, "ttk::scrollbar", kw)


kundi Separator(Widget):
    """Ttk Separator widget displays a horizontal ama vertical separator
    bar."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Separator ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus

        WIDGET-SPECIFIC OPTIONS

            orient
        """
        Widget.__init__(self, master, "ttk::separator", kw)


kundi Sizegrip(Widget):
    """Ttk Sizegrip allows the user to resize the containing toplevel
    window by pressing na dragging the grip."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Sizegrip ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, state, style, takefocus
        """
        Widget.__init__(self, master, "ttk::sizegrip", kw)


kundi Spinbox(Entry):
    """Ttk Spinbox ni an Entry ukijumuisha increment na decrement arrows

    It ni commonly used kila number entry ama to select kutoka a list of
    string values.
    """

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Spinbox widget ukijumuisha the parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus, validate,
            validatecommand, xscrollcommand, invalidcommand

        WIDGET-SPECIFIC OPTIONS

            to, from_, increment, values, wrap, format, command
        """
        Entry.__init__(self, master, "ttk::spinbox", **kw)


    eleza set(self, value):
        """Sets the value of the Spinbox to value."""
        self.tk.call(self._w, "set", value)


kundi Treeview(Widget, tkinter.XView, tkinter.YView):
    """Ttk Treeview widget displays a hierarchical collection of items.

    Each item has a textual label, an optional image, na an optional list
    of data values. The data values are displayed kwenye successive columns
    after the tree label."""

    eleza __init__(self, master=Tupu, **kw):
        """Construct a Ttk Treeview ukijumuisha parent master.

        STANDARD OPTIONS

            class, cursor, style, takefocus, xscrollcommand,
            yscrollcommand

        WIDGET-SPECIFIC OPTIONS

            columns, displaycolumns, height, padding, selectmode, show

        ITEM OPTIONS

            text, image, values, open, tags

        TAG OPTIONS

            foreground, background, font, image
        """
        Widget.__init__(self, master, "ttk::treeview", kw)


    eleza bbox(self, item, column=Tupu):
        """Returns the bounding box (relative to the treeview widget's
        window) of the specified item kwenye the form x y width height.

        If column ni specified, returns the bounding box of that cell.
        If the item ni sio visible (i.e., ikiwa it ni a descendant of a
        closed item ama ni scrolled offscreen), returns an empty string."""
        rudisha self._getints(self.tk.call(self._w, "bbox", item, column)) ama ''


    eleza get_children(self, item=Tupu):
        """Returns a tuple of children belonging to item.

        If item ni sio specified, returns root children."""
        rudisha self.tk.splitlist(
                self.tk.call(self._w, "children", item ama '') ama ())


    eleza set_children(self, item, *newchildren):
        """Replaces item's child ukijumuisha newchildren.

        Children present kwenye item that are sio present kwenye newchildren
        are detached kutoka tree. No items kwenye newchildren may be an
        ancestor of item."""
        self.tk.call(self._w, "children", item, newchildren)


    eleza column(self, column, option=Tupu, **kw):
        """Query ama modify the options kila the specified column.

        If kw ni sio given, returns a dict of the column option values. If
        option ni specified then the value kila that option ni returned.
        Otherwise, sets the options to the corresponding values."""
        ikiwa option ni sio Tupu:
            kw[option] = Tupu
        rudisha _val_or_dict(self.tk, kw, self._w, "column", column)


    eleza delete(self, *items):
        """Delete all specified items na all their descendants. The root
        item may sio be deleted."""
        self.tk.call(self._w, "delete", items)


    eleza detach(self, *items):
        """Unlinks all of the specified items kutoka the tree.

        The items na all of their descendants are still present, na may
        be reinserted at another point kwenye the tree, but will sio be
        displayed. The root item may sio be detached."""
        self.tk.call(self._w, "detach", items)


    eleza exists(self, item):
        """Returns Kweli ikiwa the specified item ni present kwenye the tree,
        Uongo otherwise."""
        rudisha self.tk.getboolean(self.tk.call(self._w, "exists", item))


    eleza focus(self, item=Tupu):
        """If item ni specified, sets the focus item to item. Otherwise,
        returns the current focus item, ama '' ikiwa there ni none."""
        rudisha self.tk.call(self._w, "focus", item)


    eleza heading(self, column, option=Tupu, **kw):
        """Query ama modify the heading options kila the specified column.

        If kw ni sio given, returns a dict of the heading option values. If
        option ni specified then the value kila that option ni returned.
        Otherwise, sets the options to the corresponding values.

        Valid options/values are:
            text: text
                The text to display kwenye the column heading
            image: image_name
                Specifies an image to display to the right of the column
                heading
            anchor: anchor
                Specifies how the heading text should be aligned. One of
                the standard Tk anchor values
            command: callback
                A callback to be invoked when the heading label is
                pressed.

        To configure the tree column heading, call this ukijumuisha column = "#0" """
        cmd = kw.get('command')
        ikiwa cmd na sio isinstance(cmd, str):
            # callback sio registered yet, do it now
            kw['command'] = self.master.register(cmd, self._substitute)

        ikiwa option ni sio Tupu:
            kw[option] = Tupu

        rudisha _val_or_dict(self.tk, kw, self._w, 'heading', column)


    eleza identify(self, component, x, y):
        """Returns a description of the specified component under the
        point given by x na y, ama the empty string ikiwa no such component
        ni present at that position."""
        rudisha self.tk.call(self._w, "identify", component, x, y)


    eleza identify_row(self, y):
        """Returns the item ID of the item at position y."""
        rudisha self.identify("row", 0, y)


    eleza identify_column(self, x):
        """Returns the data column identifier of the cell at position x.

        The tree column has ID #0."""
        rudisha self.identify("column", x, 0)


    eleza identify_region(self, x, y):
        """Returns one of:

        heading: Tree heading area.
        separator: Space between two columns headings;
        tree: The tree area.
        cell: A data cell.

        * Availability: Tk 8.6"""
        rudisha self.identify("region", x, y)


    eleza identify_element(self, x, y):
        """Returns the element at position x, y.

        * Availability: Tk 8.6"""
        rudisha self.identify("element", x, y)


    eleza index(self, item):
        """Returns the integer index of item within its parent's list
        of children."""
        rudisha self.tk.getint(self.tk.call(self._w, "index", item))


    eleza insert(self, parent, index, iid=Tupu, **kw):
        """Creates a new item na rudisha the item identifier of the newly
        created item.

        parent ni the item ID of the parent item, ama the empty string
        to create a new top-level item. index ni an integer, ama the value
        end, specifying where kwenye the list of parent's children to insert
        the new item. If index ni less than ama equal to zero, the new node
        ni inserted at the beginning, ikiwa index ni greater than ama equal to
        the current number of children, it ni inserted at the end. If iid
        ni specified, it ni used kama the item identifier, iid must not
        already exist kwenye the tree. Otherwise, a new unique identifier
        ni generated."""
        opts = _format_optdict(kw)
        ikiwa iid ni sio Tupu:
            res = self.tk.call(self._w, "insert", parent, index,
                "-id", iid, *opts)
        isipokua:
            res = self.tk.call(self._w, "insert", parent, index, *opts)

        rudisha res


    eleza item(self, item, option=Tupu, **kw):
        """Query ama modify the options kila the specified item.

        If no options are given, a dict ukijumuisha options/values kila the item
        ni returned. If option ni specified then the value kila that option
        ni returned. Otherwise, sets the options to the corresponding
        values kama given by kw."""
        ikiwa option ni sio Tupu:
            kw[option] = Tupu
        rudisha _val_or_dict(self.tk, kw, self._w, "item", item)


    eleza move(self, item, parent, index):
        """Moves item to position index kwenye parent's list of children.

        It ni illegal to move an item under one of its descendants. If
        index ni less than ama equal to zero, item ni moved to the
        beginning, ikiwa greater than ama equal to the number of children,
        it ni moved to the end. If item was detached it ni reattached."""
        self.tk.call(self._w, "move", item, parent, index)

    reattach = move # A sensible method name kila reattaching detached items


    eleza next(self, item):
        """Returns the identifier of item's next sibling, ama '' ikiwa item
        ni the last child of its parent."""
        rudisha self.tk.call(self._w, "next", item)


    eleza parent(self, item):
        """Returns the ID of the parent of item, ama '' ikiwa item ni at the
        top level of the hierarchy."""
        rudisha self.tk.call(self._w, "parent", item)


    eleza prev(self, item):
        """Returns the identifier of item's previous sibling, ama '' if
        item ni the first child of its parent."""
        rudisha self.tk.call(self._w, "prev", item)


    eleza see(self, item):
        """Ensure that item ni visible.

        Sets all of item's ancestors open option to Kweli, na scrolls
        the widget ikiwa necessary so that item ni within the visible
        portion of the tree."""
        self.tk.call(self._w, "see", item)


    eleza selection(self):
        """Returns the tuple of selected items."""
        rudisha self.tk.splitlist(self.tk.call(self._w, "selection"))


    eleza _selection(self, selop, items):
        ikiwa len(items) == 1 na isinstance(items[0], (tuple, list)):
            items = items[0]

        self.tk.call(self._w, "selection", selop, items)


    eleza selection_set(self, *items):
        """The specified items becomes the new selection."""
        self._selection("set", items)


    eleza selection_add(self, *items):
        """Add all of the specified items to the selection."""
        self._selection("add", items)


    eleza selection_remove(self, *items):
        """Remove all of the specified items kutoka the selection."""
        self._selection("remove", items)


    eleza selection_toggle(self, *items):
        """Toggle the selection state of each specified item."""
        self._selection("toggle", items)


    eleza set(self, item, column=Tupu, value=Tupu):
        """Query ama set the value of given item.

        With one argument, rudisha a dictionary of column/value pairs
        kila the specified item. With two arguments, rudisha the current
        value of the specified column. With three arguments, set the
        value of given column kwenye given item to the specified value."""
        res = self.tk.call(self._w, "set", item, column, value)
        ikiwa column ni Tupu na value ni Tupu:
            rudisha _splitdict(self.tk, res,
                              cut_minus=Uongo, conv=_tclobj_to_py)
        isipokua:
            rudisha res


    eleza tag_bind(self, tagname, sequence=Tupu, callback=Tupu):
        """Bind a callback kila the given event sequence to the tag tagname.
        When an event ni delivered to an item, the callbacks kila each
        of the item's tags option are called."""
        self._bind((self._w, "tag", "bind", tagname), sequence, callback, add=0)


    eleza tag_configure(self, tagname, option=Tupu, **kw):
        """Query ama modify the options kila the specified tagname.

        If kw ni sio given, returns a dict of the option settings kila tagname.
        If option ni specified, returns the value kila that option kila the
        specified tagname. Otherwise, sets the options to the corresponding
        values kila the given tagname."""
        ikiwa option ni sio Tupu:
            kw[option] = Tupu
        rudisha _val_or_dict(self.tk, kw, self._w, "tag", "configure",
            tagname)


    eleza tag_has(self, tagname, item=Tupu):
        """If item ni specified, returns 1 ama 0 depending on whether the
        specified item has the given tagname. Otherwise, returns a list of
        all items which have the specified tag.

        * Availability: Tk 8.6"""
        ikiwa item ni Tupu:
            rudisha self.tk.splitlist(
                self.tk.call(self._w, "tag", "has", tagname))
        isipokua:
            rudisha self.tk.getboolean(
                self.tk.call(self._w, "tag", "has", tagname, item))


# Extensions

kundi LabeledScale(Frame):
    """A Ttk Scale widget ukijumuisha a Ttk Label widget indicating its
    current value.

    The Ttk Scale can be accessed through instance.scale, na Ttk Label
    can be accessed through instance.label"""

    eleza __init__(self, master=Tupu, variable=Tupu, from_=0, to=10, **kw):
        """Construct a horizontal LabeledScale ukijumuisha parent master, a
        variable to be associated ukijumuisha the Ttk Scale widget na its range.
        If variable ni sio specified, a tkinter.IntVar ni created.

        WIDGET-SPECIFIC OPTIONS

            compound: 'top' ama 'bottom'
                Specifies how to display the label relative to the scale.
                Defaults to 'top'.
        """
        self._label_top = kw.pop('compound', 'top') == 'top'

        Frame.__init__(self, master, **kw)
        self._variable = variable ama tkinter.IntVar(master)
        self._variable.set(from_)
        self._last_valid = from_

        self.label = Label(self)
        self.scale = Scale(self, variable=self._variable, from_=from_, to=to)
        self.scale.bind('<<RangeChanged>>', self._adjust)

        # position scale na label according to the compound option
        scale_side = 'bottom' ikiwa self._label_top isipokua 'top'
        label_side = 'top' ikiwa scale_side == 'bottom' isipokua 'bottom'
        self.scale.pack(side=scale_side, fill='x')
        tmp = Label(self).pack(side=label_side) # place holder
        self.label.place(anchor='n' ikiwa label_side == 'top' isipokua 's')

        # update the label kama scale ama variable changes
        self.__tracecb = self._variable.trace_variable('w', self._adjust)
        self.bind('<Configure>', self._adjust)
        self.bind('<Map>', self._adjust)


    eleza destroy(self):
        """Destroy this widget na possibly its associated variable."""
        jaribu:
            self._variable.trace_vdelete('w', self.__tracecb)
        tatizo AttributeError:
            pita
        isipokua:
            toa self._variable
        super().destroy()
        self.label = Tupu
        self.scale = Tupu


    eleza _adjust(self, *args):
        """Adjust the label position according to the scale."""
        eleza adjust_label():
            self.update_idletasks() # "force" scale redraw

            x, y = self.scale.coords()
            ikiwa self._label_top:
                y = self.scale.winfo_y() - self.label.winfo_reqheight()
            isipokua:
                y = self.scale.winfo_reqheight() + self.label.winfo_reqheight()

            self.label.place_configure(x=x, y=y)

        from_ = _to_number(self.scale['from'])
        to = _to_number(self.scale['to'])
        ikiwa to < from_:
            from_, to = to, from_
        newval = self._variable.get()
        ikiwa sio from_ <= newval <= to:
            # value outside range, set value back to the last valid one
            self.value = self._last_valid
            return

        self._last_valid = newval
        self.label['text'] = newval
        self.after_idle(adjust_label)

    @property
    eleza value(self):
        """Return current scale value."""
        rudisha self._variable.get()

    @value.setter
    eleza value(self, val):
        """Set new scale value."""
        self._variable.set(val)


kundi OptionMenu(Menubutton):
    """Themed OptionMenu, based after tkinter's OptionMenu, which allows
    the user to select a value kutoka a menu."""

    eleza __init__(self, master, variable, default=Tupu, *values, **kwargs):
        """Construct a themed OptionMenu widget ukijumuisha master kama the parent,
        the resource textvariable set to variable, the initially selected
        value specified by the default parameter, the menu values given by
        *values na additional keywords.

        WIDGET-SPECIFIC OPTIONS

            style: stylename
                Menubutton style.
            direction: 'above', 'below', 'left', 'right', ama 'flush'
                Menubutton direction.
            command: callback
                A callback that will be invoked after selecting an item.
        """
        kw = {'textvariable': variable, 'style': kwargs.pop('style', Tupu),
              'direction': kwargs.pop('direction', Tupu)}
        Menubutton.__init__(self, master, **kw)
        self['menu'] = tkinter.Menu(self, tearoff=Uongo)

        self._variable = variable
        self._callback = kwargs.pop('command', Tupu)
        ikiwa kwargs:
            ashiria tkinter.TclError('unknown option -%s' % (
                next(iter(kwargs.keys()))))

        self.set_menu(default, *values)


    eleza __getitem__(self, item):
        ikiwa item == 'menu':
            rudisha self.nametowidget(Menubutton.__getitem__(self, item))

        rudisha Menubutton.__getitem__(self, item)


    eleza set_menu(self, default=Tupu, *values):
        """Build a new menu of radiobuttons ukijumuisha *values na optionally
        a default value."""
        menu = self['menu']
        menu.delete(0, 'end')
        kila val kwenye values:
            menu.add_radiobutton(label=val,
                command=tkinter._setit(self._variable, val, self._callback),
                variable=self._variable)

        ikiwa default:
            self._variable.set(default)


    eleza destroy(self):
        """Destroy this widget na its associated variable."""
        jaribu:
            toa self._variable
        tatizo AttributeError:
            pita
        super().destroy()
