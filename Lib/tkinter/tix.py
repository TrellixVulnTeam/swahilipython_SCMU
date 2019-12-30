# Tix.py -- Tix widget wrappers.
#
#       For Tix, see http://tix.sourceforge.net
#
#       - Sudhir Shenoy (sshenoy@gol.com), Dec. 1995.
#         based on an idea of Jean-Marc Lugrin (lugrin@ms.com)
#
# NOTE: In order to minimize changes to Tkinter.py, some of the code here
#       (TixWidget.__init__) has been taken kutoka Tkinter (Widget.__init__)
#       na will koma ikiwa there are major changes kwenye Tkinter.
#
# The Tix widgets are represented by a kundi hierarchy kwenye python ukijumuisha proper
# inheritance of base classes.
#
# As a result after creating a 'w = StdButtonBox', I can write
#              w.ok['text'] = 'Who Cares'
#    ama              w.ok['bg'] = w['bg']
# ama even       w.ok.invoke()
# etc.
#
# Compare the demo tixwidgets.py to the original Tcl program na you will
# appreciate the advantages.
#

agiza os
agiza tkinter
kutoka tkinter agiza *
kutoka tkinter agiza _cnfmerge

agiza _tkinter # If this fails your Python may sio be configured kila Tk

# Some more constants (kila consistency ukijumuisha Tkinter)
WINDOW = 'window'
TEXT = 'text'
STATUS = 'status'
IMMEDIATE = 'immediate'
IMAGE = 'image'
IMAGETEXT = 'imagetext'
BALLOON = 'balloon'
AUTO = 'auto'
ACROSSTOP = 'acrosstop'

# A few useful constants kila the Grid widget
ASCII = 'ascii'
CELL = 'cell'
COLUMN = 'column'
DECREASING = 'decreasing'
INCREASING = 'increasing'
INTEGER = 'integer'
MAIN = 'main'
MAX = 'max'
REAL = 'real'
ROW = 'row'
S_REGION = 's-region'
X_REGION = 'x-region'
Y_REGION = 'y-region'

# Some constants used by Tkinter dooneevent()
TCL_DONT_WAIT     = 1 << 1
TCL_WINDOW_EVENTS = 1 << 2
TCL_FILE_EVENTS   = 1 << 3
TCL_TIMER_EVENTS  = 1 << 4
TCL_IDLE_EVENTS   = 1 << 5
TCL_ALL_EVENTS    = 0

# BEWARE - this ni implemented by copying some code kutoka the Widget class
#          kwenye Tkinter (to override Widget initialization) na ni therefore
#          liable to koma.

# Could probably add this to Tkinter.Misc
kundi tixCommand:
    """The tix commands provide access to miscellaneous  elements
    of  Tix's  internal state na the Tix application context.
    Most of the information manipulated by these  commands pertains
    to  the  application  kama a whole, ama to a screen ama
    display, rather than to a particular window.

    This ni a mixin class, assumed to be mixed to Tkinter.Tk
    that supports the self.tk.call method.
    """

    eleza tix_addbitmapdir(self, directory):
        """Tix maintains a list of directories under which
        the  tix_getimage  na tix_getbitmap commands will
        search kila image files. The standard bitmap  directory
        ni $TIX_LIBRARY/bitmaps. The addbitmapdir command
        adds directory into this list. By  using  this
        command, the  image  files  of an applications can
        also be located using the tix_getimage ama tix_getbitmap
        command.
        """
        rudisha self.tk.call('tix', 'addbitmapdir', directory)

    eleza tix_cget(self, option):
        """Returns  the  current  value  of the configuration
        option given by option. Option may be  any  of  the
        options described kwenye the CONFIGURATION OPTIONS section.
        """
        rudisha self.tk.call('tix', 'cget', option)

    eleza tix_configure(self, cnf=Tupu, **kw):
        """Query ama modify the configuration options of the Tix application
        context. If no option ni specified, returns a dictionary all of the
        available options.  If option ni specified ukijumuisha no value, then the
        command returns a list describing the one named option (this list
        will be identical to the corresponding sublist of the value
        returned ikiwa no option ni specified).  If one ama more option-value
        pairs are specified, then the command modifies the given option(s)
        to have the given value(s); kwenye this case the command returns an
        empty string. Option may be any of the configuration options.
        """
        # Copied kutoka Tkinter.py
        ikiwa kw:
            cnf = _cnfmerge((cnf, kw))
        lasivyo cnf:
            cnf = _cnfmerge(cnf)
        ikiwa cnf ni Tupu:
            rudisha self._getconfigure('tix', 'configure')
        ikiwa isinstance(cnf, str):
            rudisha self._getconfigure1('tix', 'configure', '-'+cnf)
        rudisha self.tk.call(('tix', 'configure') + self._options(cnf))

    eleza tix_filedialog(self, dlgclass=Tupu):
        """Returns the file selection dialog that may be shared among
        different calls kutoka this application.  This command will create a
        file selection dialog widget when it ni called the first time. This
        dialog will be returned by all subsequent calls to tix_filedialog.
        An optional dlgkundi parameter can be pitaed to specified what type
        of file selection dialog widget ni desired. Possible options are
        tix FileSelectDialog ama tixExFileSelectDialog.
        """
        ikiwa dlgkundi ni sio Tupu:
            rudisha self.tk.call('tix', 'filedialog', dlgclass)
        isipokua:
            rudisha self.tk.call('tix', 'filedialog')

    eleza tix_getbitmap(self, name):
        """Locates a bitmap file of the name name.xpm ama name kwenye one of the
        bitmap directories (see the tix_addbitmapdir command above).  By
        using tix_getbitmap, you can avoid hard coding the pathnames of the
        bitmap files kwenye your application. When successful, it returns the
        complete pathname of the bitmap file, prefixed ukijumuisha the character
        '@'.  The returned value can be used to configure the -bitmap
        option of the TK na Tix widgets.
        """
        rudisha self.tk.call('tix', 'getbitmap', name)

    eleza tix_getimage(self, name):
        """Locates an image file of the name name.xpm, name.xbm ama name.ppm
        kwenye one of the bitmap directories (see the addbitmapdir command
        above). If more than one file ukijumuisha the same name (but different
        extensions) exist, then the image type ni chosen according to the
        depth of the X display: xbm images are chosen on monochrome
        displays na color images are chosen on color displays. By using
        tix_ getimage, you can avoid hard coding the pathnames of the
        image files kwenye your application. When successful, this command
        returns the name of the newly created image, which can be used to
        configure the -image option of the Tk na Tix widgets.
        """
        rudisha self.tk.call('tix', 'getimage', name)

    eleza tix_option_get(self, name):
        """Gets  the options  maintained  by  the  Tix
        scheme mechanism. Available options include:

            active_bg       active_fg      bg
            bold_font       dark1_bg       dark1_fg
            dark2_bg        dark2_fg       disabled_fg
            fg              fixed_font     font
            inactive_bg     inactive_fg    input1_bg
            input2_bg       italic_font    light1_bg
            light1_fg       light2_bg      light2_fg
            menu_font       output1_bg     output2_bg
            select_bg       select_fg      selector
            """
        # could use self.tk.globalgetvar('tixOption', name)
        rudisha self.tk.call('tix', 'option', 'get', name)

    eleza tix_resetoptions(self, newScheme, newFontSet, newScmPrio=Tupu):
        """Resets the scheme na fontset of the Tix application to
        newScheme na newFontSet, respectively.  This affects only those
        widgets created after this call. Therefore, it ni best to call the
        resetoptions command before the creation of any widgets kwenye a Tix
        application.

        The optional parameter newScmPrio can be given to reset the
        priority level of the Tk options set by the Tix schemes.

        Because of the way Tk handles the X option database, after Tix has
        been has imported na inited, it ni sio possible to reset the color
        schemes na font sets using the tix config command.  Instead, the
        tix_resetoptions command must be used.
        """
        ikiwa newScmPrio ni sio Tupu:
            rudisha self.tk.call('tix', 'resetoptions', newScheme, newFontSet, newScmPrio)
        isipokua:
            rudisha self.tk.call('tix', 'resetoptions', newScheme, newFontSet)

kundi Tk(tkinter.Tk, tixCommand):
    """Toplevel widget of Tix which represents mostly the main window
    of an application. It has an associated Tcl interpreter."""
    eleza __init__(self, screenName=Tupu, baseName=Tupu, className='Tix'):
        tkinter.Tk.__init__(self, screenName, baseName, className)
        tixlib = os.environ.get('TIX_LIBRARY')
        self.tk.eval('global auto_path; lappend auto_path [file dir [info nameof]]')
        ikiwa tixlib ni sio Tupu:
            self.tk.eval('global auto_path; lappend auto_path {%s}' % tixlib)
            self.tk.eval('global tcl_pkgPath; lappend tcl_pkgPath {%s}' % tixlib)
        # Load Tix - this should work dynamically ama statically
        # If it's static, tcl/tix8.1/pkgIndex.tcl should have
        #               'load {} Tix'
        # If it's dynamic under Unix, tcl/tix8.1/pkgIndex.tcl should have
        #               'load libtix8.1.8.3.so Tix'
        self.tk.eval('package require Tix')

    eleza destroy(self):
        # For safety, remove the delete_window binding before destroy
        self.protocol("WM_DELETE_WINDOW", "")
        tkinter.Tk.destroy(self)

# The Tix 'tixForm' geometry manager
kundi Form:
    """The Tix Form geometry manager

    Widgets can be arranged by specifying attachments to other widgets.
    See Tix documentation kila complete details"""

    eleza config(self, cnf={}, **kw):
        self.tk.call('tixForm', self._w, *self._options(cnf, kw))

    form = config

    eleza __setitem__(self, key, value):
        Form.form(self, {key: value})

    eleza check(self):
        rudisha self.tk.call('tixForm', 'check', self._w)

    eleza forget(self):
        self.tk.call('tixForm', 'forget', self._w)

    eleza grid(self, xsize=0, ysize=0):
        ikiwa (sio xsize) na (sio ysize):
            x = self.tk.call('tixForm', 'grid', self._w)
            y = self.tk.splitlist(x)
            z = ()
            kila x kwenye y:
                z = z + (self.tk.getint(x),)
            rudisha z
        rudisha self.tk.call('tixForm', 'grid', self._w, xsize, ysize)

    eleza info(self, option=Tupu):
        ikiwa sio option:
            rudisha self.tk.call('tixForm', 'info', self._w)
        ikiwa option[0] != '-':
            option = '-' + option
        rudisha self.tk.call('tixForm', 'info', self._w, option)

    eleza slaves(self):
        rudisha [self._nametowidget(x) kila x in
                self.tk.splitlist(
                       self.tk.call(
                       'tixForm', 'slaves', self._w))]



tkinter.Widget.__bases__ = tkinter.Widget.__bases__ + (Form,)

kundi TixWidget(tkinter.Widget):
    """A TixWidget kundi ni used to package all (or most) Tix widgets.

    Widget initialization ni extended kwenye two ways:
       1) It ni possible to give a list of options which must be part of
       the creation command (so called Tix 'static' options). These cannot be
       given kama a 'config' command later.
       2) It ni possible to give the name of an existing TK widget. These are
       child widgets created automatically by a Tix mega-widget. The Tk call
       to create these widgets ni therefore bypitaed kwenye TixWidget.__init__

    Both options are kila use by subclasses only.
    """
    eleza __init__ (self, master=Tupu, widgetName=Tupu,
                static_options=Tupu, cnf={}, kw={}):
        # Merge keywords na dictionary arguments
        ikiwa kw:
            cnf = _cnfmerge((cnf, kw))
        isipokua:
            cnf = _cnfmerge(cnf)

        # Move static options into extra. static_options must be
        # a list of keywords (or Tupu).
        extra=()

        # 'options' ni always a static option
        ikiwa static_options:
            static_options.append('options')
        isipokua:
            static_options = ['options']

        kila k,v kwenye list(cnf.items()):
            ikiwa k kwenye static_options:
                extra = extra + ('-' + k, v)
                toa cnf[k]

        self.widgetName = widgetName
        Widget._setup(self, master, cnf)

        # If widgetName ni Tupu, this ni a dummy creation call where the
        # corresponding Tk widget has already been created by Tix
        ikiwa widgetName:
            self.tk.call(widgetName, self._w, *extra)

        # Non-static options - to be done via a 'config' command
        ikiwa cnf:
            Widget.config(self, cnf)

        # Dictionary to hold subwidget names kila easier access. We can't
        # use the children list because the public Tix names may sio be the
        # same kama the pathname component
        self.subwidget_list = {}

    # We set up an attribute access function so that it ni possible to
    # do w.ok['text'] = 'Hello' rather than w.subwidget('ok')['text'] = 'Hello'
    # when w ni a StdButtonBox.
    # We can even do w.ok.invoke() because w.ok ni subclassed kutoka the
    # Button kundi ikiwa you go through the proper constructors
    eleza __getattr__(self, name):
        ikiwa name kwenye self.subwidget_list:
            rudisha self.subwidget_list[name]
        ashiria AttributeError(name)

    eleza set_silent(self, value):
        """Set a variable without calling its action routine"""
        self.tk.call('tixSetSilent', self._w, value)

    eleza subwidget(self, name):
        """Return the named subwidget (which must have been created by
        the sub-class)."""
        n = self._subwidget_name(name)
        ikiwa sio n:
            ashiria TclError("Subwidget " + name + " sio child of " + self._name)
        # Remove header of name na leading dot
        n = n[len(self._w)+1:]
        rudisha self._nametowidget(n)

    eleza subwidgets_all(self):
        """Return all subwidgets."""
        names = self._subwidget_names()
        ikiwa sio names:
            rudisha []
        retlist = []
        kila name kwenye names:
            name = name[len(self._w)+1:]
            jaribu:
                retlist.append(self._nametowidget(name))
            tatizo:
                # some of the widgets are unknown e.g. border kwenye LabelFrame
                pita
        rudisha retlist

    eleza _subwidget_name(self,name):
        """Get a subwidget name (returns a String, sio a Widget !)"""
        jaribu:
            rudisha self.tk.call(self._w, 'subwidget', name)
        tatizo TclError:
            rudisha Tupu

    eleza _subwidget_names(self):
        """Return the name of all subwidgets."""
        jaribu:
            x = self.tk.call(self._w, 'subwidgets', '-all')
            rudisha self.tk.splitlist(x)
        tatizo TclError:
            rudisha Tupu

    eleza config_all(self, option, value):
        """Set configuration options kila all subwidgets (and self)."""
        ikiwa option == '':
            return
        lasivyo sio isinstance(option, str):
            option = repr(option)
        ikiwa sio isinstance(value, str):
            value = repr(value)
        names = self._subwidget_names()
        kila name kwenye names:
            self.tk.call(name, 'configure', '-' + option, value)
    # These are missing kutoka Tkinter
    eleza image_create(self, imgtype, cnf={}, master=Tupu, **kw):
        ikiwa sio master:
            master = tkinter._default_root
            ikiwa sio master:
                ashiria RuntimeError('Too early to create image')
        ikiwa kw na cnf: cnf = _cnfmerge((cnf, kw))
        lasivyo kw: cnf = kw
        options = ()
        kila k, v kwenye cnf.items():
            ikiwa callable(v):
                v = self._register(v)
            options = options + ('-'+k, v)
        rudisha master.tk.call(('image', 'create', imgtype,) + options)
    eleza image_delete(self, imgname):
        jaribu:
            self.tk.call('image', 'delete', imgname)
        tatizo TclError:
            # May happen ikiwa the root was destroyed
            pita

# Subwidgets are child widgets created automatically by mega-widgets.
# In python, we have to create these subwidgets manually to mirror their
# existence kwenye Tk/Tix.
kundi TixSubWidget(TixWidget):
    """Subwidget class.

    This ni used to mirror child widgets automatically created
    by Tix/Tk kama part of a mega-widget kwenye Python (which ni sio informed
    of this)"""

    eleza __init__(self, master, name,
               destroy_physically=1, check_intermediate=1):
        ikiwa check_intermediate:
            path = master._subwidget_name(name)
            jaribu:
                path = path[len(master._w)+1:]
                plist = path.split('.')
            tatizo:
                plist = []

        ikiwa sio check_intermediate:
            # immediate descendant
            TixWidget.__init__(self, master, Tupu, Tupu, {'name' : name})
        isipokua:
            # Ensure that the intermediate widgets exist
            parent = master
            kila i kwenye range(len(plist) - 1):
                n = '.'.join(plist[:i+1])
                jaribu:
                    w = master._nametowidget(n)
                    parent = w
                tatizo KeyError:
                    # Create the intermediate widget
                    parent = TixSubWidget(parent, plist[i],
                                          destroy_physically=0,
                                          check_intermediate=0)
            # The Tk widget name ni kwenye plist, haiko kwenye name
            ikiwa plist:
                name = plist[-1]
            TixWidget.__init__(self, parent, Tupu, Tupu, {'name' : name})
        self.destroy_physically = destroy_physically

    eleza destroy(self):
        # For some widgets e.g., a NoteBook, when we call destructors,
        # we must be careful sio to destroy the frame widget since this
        # also destroys the parent NoteBook thus leading to an exception
        # kwenye Tkinter when it finally calls Tcl to destroy the NoteBook
        kila c kwenye list(self.children.values()): c.destroy()
        ikiwa self._name kwenye self.master.children:
            toa self.master.children[self._name]
        ikiwa self._name kwenye self.master.subwidget_list:
            toa self.master.subwidget_list[self._name]
        ikiwa self.destroy_physically:
            # This ni bypitaed only kila a few widgets
            self.tk.call('destroy', self._w)


# Useful kundi to create a display style - later shared by many items.
# Contributed by Steffen Kremser
kundi DisplayStyle:
    """DisplayStyle - handle configuration options shared by
    (multiple) Display Items"""

    eleza __init__(self, itemtype, cnf={}, *, master=Tupu, **kw):
        ikiwa sio master:
            ikiwa 'refwindow' kwenye kw:
                master = kw['refwindow']
            lasivyo 'refwindow' kwenye cnf:
                master = cnf['refwindow']
            isipokua:
                master = tkinter._default_root
                ikiwa sio master:
                    ashiria RuntimeError("Too early to create display style: "
                                       "no root window")
        self.tk = master.tk
        self.stylename = self.tk.call('tixDisplayStyle', itemtype,
                            *self._options(cnf,kw) )

    eleza __str__(self):
        rudisha self.stylename

    eleza _options(self, cnf, kw):
        ikiwa kw na cnf:
            cnf = _cnfmerge((cnf, kw))
        lasivyo kw:
            cnf = kw
        opts = ()
        kila k, v kwenye cnf.items():
            opts = opts + ('-'+k, v)
        rudisha opts

    eleza delete(self):
        self.tk.call(self.stylename, 'delete')

    eleza __setitem__(self,key,value):
        self.tk.call(self.stylename, 'configure', '-%s'%key, value)

    eleza config(self, cnf={}, **kw):
        rudisha self._getconfigure(
            self.stylename, 'configure', *self._options(cnf,kw))

    eleza __getitem__(self,key):
        rudisha self.tk.call(self.stylename, 'cget', '-%s'%key)


######################################################
### The Tix Widget classes - kwenye alphabetical order ###
######################################################

kundi Balloon(TixWidget):
    """Balloon help widget.

    Subwidget       Class
    ---------       -----
    label           Label
    message         Message"""

    # FIXME: It should inherit -superkundi tixShell
    eleza __init__(self, master=Tupu, cnf={}, **kw):
        # static seem to be -installcolormap -initwait -statusbar -cursor
        static = ['options', 'installcolormap', 'initwait', 'statusbar',
                  'cursor']
        TixWidget.__init__(self, master, 'tixBalloon', static, cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label',
                                                   destroy_physically=0)
        self.subwidget_list['message'] = _dummyLabel(self, 'message',
                                                     destroy_physically=0)

    eleza bind_widget(self, widget, cnf={}, **kw):
        """Bind balloon widget to another.
        One balloon widget may be bound to several widgets at the same time"""
        self.tk.call(self._w, 'bind', widget._w, *self._options(cnf, kw))

    eleza unbind_widget(self, widget):
        self.tk.call(self._w, 'unbind', widget._w)

kundi ButtonBox(TixWidget):
    """ButtonBox - A container kila pushbuttons.
    Subwidgets are the buttons added ukijumuisha the add method.
    """
    eleza __init__(self, master=Tupu, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixButtonBox',
                           ['orientation', 'options'], cnf, kw)

    eleza add(self, name, cnf={}, **kw):
        """Add a button ukijumuisha given name to box."""

        btn = self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = _dummyButton(self, name)
        rudisha btn

    eleza invoke(self, name):
        ikiwa name kwenye self.subwidget_list:
            self.tk.call(self._w, 'invoke', name)

kundi ComboBox(TixWidget):
    """ComboBox - an Entry field ukijumuisha a dropdown menu. The user can select a
    choice by either typing kwenye the entry subwidget ama selecting kutoka the
    listbox subwidget.

    Subwidget       Class
    ---------       -----
    entry       Entry
    arrow       Button
    slistbox    ScrolledListBox
    tick        Button
    cross       Button : present ikiwa created ukijumuisha the fancy option"""

    # FIXME: It should inherit -superkundi tixLabelWidget
    eleza __init__ (self, master=Tupu, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixComboBox',
                           ['editable', 'dropdown', 'fancy', 'options'],
                           cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')
        self.subwidget_list['arrow'] = _dummyButton(self, 'arrow')
        self.subwidget_list['slistbox'] = _dummyScrolledListBox(self,
                                                                'slistbox')
        jaribu:
            self.subwidget_list['tick'] = _dummyButton(self, 'tick')
            self.subwidget_list['cross'] = _dummyButton(self, 'cross')
        tatizo TypeError:
            # unavailable when -fancy sio specified
            pita

    # align

    eleza add_history(self, str):
        self.tk.call(self._w, 'addhistory', str)

    eleza append_history(self, str):
        self.tk.call(self._w, 'appendhistory', str)

    eleza insert(self, index, str):
        self.tk.call(self._w, 'insert', index, str)

    eleza pick(self, index):
        self.tk.call(self._w, 'pick', index)

kundi Control(TixWidget):
    """Control - An entry field ukijumuisha value change arrows.  The user can
    adjust the value by pressing the two arrow buttons ama by entering
    the value directly into the entry. The new value will be checked
    against the user-defined upper na lower limits.

    Subwidget       Class
    ---------       -----
    incr       Button
    decr       Button
    entry       Entry
    label       Label"""

    # FIXME: It should inherit -superkundi tixLabelWidget
    eleza __init__ (self, master=Tupu, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixControl', ['options'], cnf, kw)
        self.subwidget_list['incr'] = _dummyButton(self, 'incr')
        self.subwidget_list['decr'] = _dummyButton(self, 'decr')
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')

    eleza decrement(self):
        self.tk.call(self._w, 'decr')

    eleza increment(self):
        self.tk.call(self._w, 'incr')

    eleza invoke(self):
        self.tk.call(self._w, 'invoke')

    eleza update(self):
        self.tk.call(self._w, 'update')

kundi DirList(TixWidget):
    """DirList - displays a list view of a directory, its previous
    directories na its sub-directories. The user can choose one of
    the directories displayed kwenye the list ama change to another directory.

    Subwidget       Class
    ---------       -----
    hlist       HList
    hsb              Scrollbar
    vsb              Scrollbar"""

    # FIXME: It should inherit -superkundi tixScrolledHList
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirList', ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    eleza chdir(self, dir):
        self.tk.call(self._w, 'chdir', dir)

kundi DirTree(TixWidget):
    """DirTree - Directory Listing kwenye a hierarchical view.
    Displays a tree view of a directory, its previous directories na its
    sub-directories. The user can choose one of the directories displayed
    kwenye the list ama change to another directory.

    Subwidget       Class
    ---------       -----
    hlist           HList
    hsb             Scrollbar
    vsb             Scrollbar"""

    # FIXME: It should inherit -superkundi tixScrolledHList
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirTree', ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    eleza chdir(self, dir):
        self.tk.call(self._w, 'chdir', dir)

kundi DirSelectBox(TixWidget):
    """DirSelectBox - Motikiwa style file select box.
    It ni generally used for
    the user to choose a file. FileSelectBox stores the files mostly
    recently selected into a ComboBox widget so that they can be quickly
    selected again.

    Subwidget       Class
    ---------       -----
    selection       ComboBox
    filter          ComboBox
    dirlist         ScrolledListBox
    filelist        ScrolledListBox"""

    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirSelectBox', ['options'], cnf, kw)
        self.subwidget_list['dirlist'] = _dummyDirList(self, 'dirlist')
        self.subwidget_list['dircbx'] = _dummyFileComboBox(self, 'dircbx')

kundi ExFileSelectBox(TixWidget):
    """ExFileSelectBox - MS Windows style file select box.
    It provides a convenient method kila the user to select files.

    Subwidget       Class
    ---------       -----
    cancel       Button
    ok              Button
    hidden       Checkbutton
    types       ComboBox
    dir              ComboBox
    file       ComboBox
    dirlist       ScrolledListBox
    filelist       ScrolledListBox"""

    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixExFileSelectBox', ['options'], cnf, kw)
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['hidden'] = _dummyCheckbutton(self, 'hidden')
        self.subwidget_list['types'] = _dummyComboBox(self, 'types')
        self.subwidget_list['dir'] = _dummyComboBox(self, 'dir')
        self.subwidget_list['dirlist'] = _dummyDirList(self, 'dirlist')
        self.subwidget_list['file'] = _dummyComboBox(self, 'file')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')

    eleza filter(self):
        self.tk.call(self._w, 'filter')

    eleza invoke(self):
        self.tk.call(self._w, 'invoke')


# Should inherit kutoka a Dialog class
kundi DirSelectDialog(TixWidget):
    """The DirSelectDialog widget presents the directories kwenye the file
    system kwenye a dialog window. The user can use this dialog window to
    navigate through the file system to select the desired directory.

    Subwidgets       Class
    ----------       -----
    dirbox       DirSelectDialog"""

    # FIXME: It should inherit -superkundi tixDialogShell
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixDirSelectDialog',
                           ['options'], cnf, kw)
        self.subwidget_list['dirbox'] = _dummyDirSelectBox(self, 'dirbox')
        # cancel na ok buttons are missing

    eleza popup(self):
        self.tk.call(self._w, 'popup')

    eleza popdown(self):
        self.tk.call(self._w, 'popdown')


# Should inherit kutoka a Dialog class
kundi ExFileSelectDialog(TixWidget):
    """ExFileSelectDialog - MS Windows style file select dialog.
    It provides a convenient method kila the user to select files.

    Subwidgets       Class
    ----------       -----
    fsbox       ExFileSelectBox"""

    # FIXME: It should inherit -superkundi tixDialogShell
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixExFileSelectDialog',
                           ['options'], cnf, kw)
        self.subwidget_list['fsbox'] = _dummyExFileSelectBox(self, 'fsbox')

    eleza popup(self):
        self.tk.call(self._w, 'popup')

    eleza popdown(self):
        self.tk.call(self._w, 'popdown')

kundi FileSelectBox(TixWidget):
    """ExFileSelectBox - Motikiwa style file select box.
    It ni generally used for
    the user to choose a file. FileSelectBox stores the files mostly
    recently selected into a ComboBox widget so that they can be quickly
    selected again.

    Subwidget       Class
    ---------       -----
    selection       ComboBox
    filter          ComboBox
    dirlist         ScrolledListBox
    filelist        ScrolledListBox"""

    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixFileSelectBox', ['options'], cnf, kw)
        self.subwidget_list['dirlist'] = _dummyScrolledListBox(self, 'dirlist')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')
        self.subwidget_list['filter'] = _dummyComboBox(self, 'filter')
        self.subwidget_list['selection'] = _dummyComboBox(self, 'selection')

    eleza apply_filter(self):              # name of subwidget ni same kama command
        self.tk.call(self._w, 'filter')

    eleza invoke(self):
        self.tk.call(self._w, 'invoke')

# Should inherit kutoka a Dialog class
kundi FileSelectDialog(TixWidget):
    """FileSelectDialog - Motikiwa style file select dialog.

    Subwidgets       Class
    ----------       -----
    btns       StdButtonBox
    fsbox       FileSelectBox"""

    # FIXME: It should inherit -superkundi tixStdDialogShell
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixFileSelectDialog',
                           ['options'], cnf, kw)
        self.subwidget_list['btns'] = _dummyStdButtonBox(self, 'btns')
        self.subwidget_list['fsbox'] = _dummyFileSelectBox(self, 'fsbox')

    eleza popup(self):
        self.tk.call(self._w, 'popup')

    eleza popdown(self):
        self.tk.call(self._w, 'popdown')

kundi FileEntry(TixWidget):
    """FileEntry - Entry field ukijumuisha button that invokes a FileSelectDialog.
    The user can type kwenye the filename manually. Alternatively, the user can
    press the button widget that sits next to the entry, which will bring
    up a file selection dialog.

    Subwidgets       Class
    ----------       -----
    button       Button
    entry       Entry"""

    # FIXME: It should inherit -superkundi tixLabelWidget
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixFileEntry',
                           ['dialogtype', 'options'], cnf, kw)
        self.subwidget_list['button'] = _dummyButton(self, 'button')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')

    eleza invoke(self):
        self.tk.call(self._w, 'invoke')

    eleza file_dialog(self):
        # FIXME: rudisha python object
        pita

kundi HList(TixWidget, XView, YView):
    """HList - Hierarchy display  widget can be used to display any data
    that have a hierarchical structure, kila example, file system directory
    trees. The list entries are indented na connected by branch lines
    according to their places kwenye the hierarchy.

    Subwidgets - Tupu"""

    eleza __init__ (self,master=Tupu,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixHList',
                           ['columns', 'options'], cnf, kw)

    eleza add(self, entry, cnf={}, **kw):
        rudisha self.tk.call(self._w, 'add', entry, *self._options(cnf, kw))

    eleza add_child(self, parent=Tupu, cnf={}, **kw):
        ikiwa sio parent:
            parent = ''
        rudisha self.tk.call(
                     self._w, 'addchild', parent, *self._options(cnf, kw))

    eleza anchor_set(self, entry):
        self.tk.call(self._w, 'anchor', 'set', entry)

    eleza anchor_clear(self):
        self.tk.call(self._w, 'anchor', 'clear')

    eleza column_width(self, col=0, width=Tupu, chars=Tupu):
        ikiwa sio chars:
            rudisha self.tk.call(self._w, 'column', 'width', col, width)
        isipokua:
            rudisha self.tk.call(self._w, 'column', 'width', col,
                                '-char', chars)

    eleza delete_all(self):
        self.tk.call(self._w, 'delete', 'all')

    eleza delete_entry(self, entry):
        self.tk.call(self._w, 'delete', 'entry', entry)

    eleza delete_offsprings(self, entry):
        self.tk.call(self._w, 'delete', 'offsprings', entry)

    eleza delete_siblings(self, entry):
        self.tk.call(self._w, 'delete', 'siblings', entry)

    eleza dragsite_set(self, index):
        self.tk.call(self._w, 'dragsite', 'set', index)

    eleza dragsite_clear(self):
        self.tk.call(self._w, 'dragsite', 'clear')

    eleza dropsite_set(self, index):
        self.tk.call(self._w, 'dropsite', 'set', index)

    eleza dropsite_clear(self):
        self.tk.call(self._w, 'dropsite', 'clear')

    eleza header_create(self, col, cnf={}, **kw):
        self.tk.call(self._w, 'header', 'create', col, *self._options(cnf, kw))

    eleza header_configure(self, col, cnf={}, **kw):
        ikiwa cnf ni Tupu:
            rudisha self._getconfigure(self._w, 'header', 'configure', col)
        self.tk.call(self._w, 'header', 'configure', col,
                     *self._options(cnf, kw))

    eleza header_cget(self,  col, opt):
        rudisha self.tk.call(self._w, 'header', 'cget', col, opt)

    eleza header_exists(self,  col):
        # A workaround to Tix library bug (issue #25464).
        # The documented command ni "exists", but only erroneous "exist" is
        # accepted.
        rudisha self.tk.getboolean(self.tk.call(self._w, 'header', 'exist', col))
    header_exist = header_exists

    eleza header_delete(self, col):
        self.tk.call(self._w, 'header', 'delete', col)

    eleza header_size(self, col):
        rudisha self.tk.call(self._w, 'header', 'size', col)

    eleza hide_entry(self, entry):
        self.tk.call(self._w, 'hide', 'entry', entry)

    eleza indicator_create(self, entry, cnf={}, **kw):
        self.tk.call(
              self._w, 'indicator', 'create', entry, *self._options(cnf, kw))

    eleza indicator_configure(self, entry, cnf={}, **kw):
        ikiwa cnf ni Tupu:
            rudisha self._getconfigure(
                self._w, 'indicator', 'configure', entry)
        self.tk.call(
              self._w, 'indicator', 'configure', entry, *self._options(cnf, kw))

    eleza indicator_cget(self,  entry, opt):
        rudisha self.tk.call(self._w, 'indicator', 'cget', entry, opt)

    eleza indicator_exists(self,  entry):
        rudisha self.tk.call (self._w, 'indicator', 'exists', entry)

    eleza indicator_delete(self, entry):
        self.tk.call(self._w, 'indicator', 'delete', entry)

    eleza indicator_size(self, entry):
        rudisha self.tk.call(self._w, 'indicator', 'size', entry)

    eleza info_anchor(self):
        rudisha self.tk.call(self._w, 'info', 'anchor')

    eleza info_bbox(self, entry):
        rudisha self._getints(
                self.tk.call(self._w, 'info', 'bbox', entry)) ama Tupu

    eleza info_children(self, entry=Tupu):
        c = self.tk.call(self._w, 'info', 'children', entry)
        rudisha self.tk.splitlist(c)

    eleza info_data(self, entry):
        rudisha self.tk.call(self._w, 'info', 'data', entry)

    eleza info_dragsite(self):
        rudisha self.tk.call(self._w, 'info', 'dragsite')

    eleza info_dropsite(self):
        rudisha self.tk.call(self._w, 'info', 'dropsite')

    eleza info_exists(self, entry):
        rudisha self.tk.call(self._w, 'info', 'exists', entry)

    eleza info_hidden(self, entry):
        rudisha self.tk.call(self._w, 'info', 'hidden', entry)

    eleza info_next(self, entry):
        rudisha self.tk.call(self._w, 'info', 'next', entry)

    eleza info_parent(self, entry):
        rudisha self.tk.call(self._w, 'info', 'parent', entry)

    eleza info_prev(self, entry):
        rudisha self.tk.call(self._w, 'info', 'prev', entry)

    eleza info_selection(self):
        c = self.tk.call(self._w, 'info', 'selection')
        rudisha self.tk.splitlist(c)

    eleza item_cget(self, entry, col, opt):
        rudisha self.tk.call(self._w, 'item', 'cget', entry, col, opt)

    eleza item_configure(self, entry, col, cnf={}, **kw):
        ikiwa cnf ni Tupu:
            rudisha self._getconfigure(self._w, 'item', 'configure', entry, col)
        self.tk.call(self._w, 'item', 'configure', entry, col,
              *self._options(cnf, kw))

    eleza item_create(self, entry, col, cnf={}, **kw):
        self.tk.call(
              self._w, 'item', 'create', entry, col, *self._options(cnf, kw))

    eleza item_exists(self, entry, col):
        rudisha self.tk.call(self._w, 'item', 'exists', entry, col)

    eleza item_delete(self, entry, col):
        self.tk.call(self._w, 'item', 'delete', entry, col)

    eleza entrycget(self, entry, opt):
        rudisha self.tk.call(self._w, 'entrycget', entry, opt)

    eleza entryconfigure(self, entry, cnf={}, **kw):
        ikiwa cnf ni Tupu:
            rudisha self._getconfigure(self._w, 'entryconfigure', entry)
        self.tk.call(self._w, 'entryconfigure', entry,
              *self._options(cnf, kw))

    eleza nearest(self, y):
        rudisha self.tk.call(self._w, 'nearest', y)

    eleza see(self, entry):
        self.tk.call(self._w, 'see', entry)

    eleza selection_clear(self, cnf={}, **kw):
        self.tk.call(self._w, 'selection', 'clear', *self._options(cnf, kw))

    eleza selection_includes(self, entry):
        rudisha self.tk.call(self._w, 'selection', 'includes', entry)

    eleza selection_set(self, first, last=Tupu):
        self.tk.call(self._w, 'selection', 'set', first, last)

    eleza show_entry(self, entry):
        rudisha self.tk.call(self._w, 'show', 'entry', entry)

kundi InputOnly(TixWidget):
    """InputOnly - Invisible widget. Unix only.

    Subwidgets - Tupu"""

    eleza __init__ (self,master=Tupu,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixInputOnly', Tupu, cnf, kw)

kundi LabelEntry(TixWidget):
    """LabelEntry - Entry field ukijumuisha label. Packages an entry widget
    na a label into one mega widget. It can be used to simplify the creation
    of ``entry-form'' type of interface.

    Subwidgets       Class
    ----------       -----
    label       Label
    entry       Entry"""

    eleza __init__ (self,master=Tupu,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixLabelEntry',
                           ['labelside','options'], cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')

kundi LabelFrame(TixWidget):
    """LabelFrame - Labelled Frame container. Packages a frame widget
    na a label into one mega widget. To create widgets inside a
    LabelFrame widget, one creates the new widgets relative to the
    frame subwidget na manage them inside the frame subwidget.

    Subwidgets       Class
    ----------       -----
    label       Label
    frame       Frame"""

    eleza __init__ (self,master=Tupu,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixLabelFrame',
                           ['labelside','options'], cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['frame'] = _dummyFrame(self, 'frame')


kundi ListNoteBook(TixWidget):
    """A ListNoteBook widget ni very similar to the TixNoteBook widget:
    it can be used to display many windows kwenye a limited space using a
    notebook metaphor. The notebook ni divided into a stack of pages
    (windows). At one time only one of these pages can be shown.
    The user can navigate through these pages by
    choosing the name of the desired page kwenye the hlist subwidget."""

    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixListNoteBook', ['options'], cnf, kw)
        # Is this necessary? It's sio an exposed subwidget kwenye Tix.
        self.subwidget_list['pane'] = _dummyPanedWindow(self, 'pane',
                                                        destroy_physically=0)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['shlist'] = _dummyScrolledHList(self, 'shlist')

    eleza add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = TixSubWidget(self, name)
        rudisha self.subwidget_list[name]

    eleza page(self, name):
        rudisha self.subwidget(name)

    eleza pages(self):
        # Can't call subwidgets_all directly because we don't want .nbframe
        names = self.tk.splitlist(self.tk.call(self._w, 'pages'))
        ret = []
        kila x kwenye names:
            ret.append(self.subwidget(x))
        rudisha ret

    eleza raise_page(self, name):              # ashiria ni a python keyword
        self.tk.call(self._w, 'raise', name)

kundi Meter(TixWidget):
    """The Meter widget can be used to show the progress of a background
    job which may take a long time to execute.
    """

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixMeter',
                           ['options'], cnf, kw)

kundi NoteBook(TixWidget):
    """NoteBook - Multi-page container widget (tabbed notebook metaphor).

    Subwidgets       Class
    ----------       -----
    nbframe       NoteBookFrame
    <pages>       page widgets added dynamically ukijumuisha the add method"""

    eleza __init__ (self,master=Tupu,cnf={}, **kw):
        TixWidget.__init__(self,master,'tixNoteBook', ['options'], cnf, kw)
        self.subwidget_list['nbframe'] = TixSubWidget(self, 'nbframe',
                                                      destroy_physically=0)

    eleza add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = TixSubWidget(self, name)
        rudisha self.subwidget_list[name]

    eleza delete(self, name):
        self.tk.call(self._w, 'delete', name)
        self.subwidget_list[name].destroy()
        toa self.subwidget_list[name]

    eleza page(self, name):
        rudisha self.subwidget(name)

    eleza pages(self):
        # Can't call subwidgets_all directly because we don't want .nbframe
        names = self.tk.splitlist(self.tk.call(self._w, 'pages'))
        ret = []
        kila x kwenye names:
            ret.append(self.subwidget(x))
        rudisha ret

    eleza raise_page(self, name):              # ashiria ni a python keyword
        self.tk.call(self._w, 'raise', name)

    eleza raised(self):
        rudisha self.tk.call(self._w, 'raised')

kundi NoteBookFrame(TixWidget):
    # FIXME: This ni dangerous to expose to be called on its own.
    pita

kundi OptionMenu(TixWidget):
    """OptionMenu - creates a menu button of options.

    Subwidget       Class
    ---------       -----
    menubutton      Menubutton
    menu            Menu"""

    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixOptionMenu', ['options'], cnf, kw)
        self.subwidget_list['menubutton'] = _dummyMenubutton(self, 'menubutton')
        self.subwidget_list['menu'] = _dummyMenu(self, 'menu')

    eleza add_command(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', 'command', name, *self._options(cnf, kw))

    eleza add_separator(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', 'separator', name, *self._options(cnf, kw))

    eleza delete(self, name):
        self.tk.call(self._w, 'delete', name)

    eleza disable(self, name):
        self.tk.call(self._w, 'disable', name)

    eleza enable(self, name):
        self.tk.call(self._w, 'enable', name)

kundi PanedWindow(TixWidget):
    """PanedWindow - Multi-pane container widget
    allows the user to interactively manipulate the sizes of several
    panes. The panes can be arranged either vertically ama horizontally.The
    user changes the sizes of the panes by dragging the resize handle
    between two panes.

    Subwidgets       Class
    ----------       -----
    <panes>       g/p widgets added dynamically ukijumuisha the add method."""

    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixPanedWindow', ['orientation', 'options'], cnf, kw)

    # add delete forget panecget paneconfigure panes setsize
    eleza add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = TixSubWidget(self, name,
                                                 check_intermediate=0)
        rudisha self.subwidget_list[name]

    eleza delete(self, name):
        self.tk.call(self._w, 'delete', name)
        self.subwidget_list[name].destroy()
        toa self.subwidget_list[name]

    eleza forget(self, name):
        self.tk.call(self._w, 'forget', name)

    eleza panecget(self,  entry, opt):
        rudisha self.tk.call(self._w, 'panecget', entry, opt)

    eleza paneconfigure(self, entry, cnf={}, **kw):
        ikiwa cnf ni Tupu:
            rudisha self._getconfigure(self._w, 'paneconfigure', entry)
        self.tk.call(self._w, 'paneconfigure', entry, *self._options(cnf, kw))

    eleza panes(self):
        names = self.tk.splitlist(self.tk.call(self._w, 'panes'))
        rudisha [self.subwidget(x) kila x kwenye names]

kundi PopupMenu(TixWidget):
    """PopupMenu widget can be used kama a replacement of the tk_popup command.
    The advantage of the Tix PopupMenu widget ni it requires less application
    code to manipulate.


    Subwidgets       Class
    ----------       -----
    menubutton       Menubutton
    menu       Menu"""

    # FIXME: It should inherit -superkundi tixShell
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixPopupMenu', ['options'], cnf, kw)
        self.subwidget_list['menubutton'] = _dummyMenubutton(self, 'menubutton')
        self.subwidget_list['menu'] = _dummyMenu(self, 'menu')

    eleza bind_widget(self, widget):
        self.tk.call(self._w, 'bind', widget._w)

    eleza unbind_widget(self, widget):
        self.tk.call(self._w, 'unbind', widget._w)

    eleza post_widget(self, widget, x, y):
        self.tk.call(self._w, 'post', widget._w, x, y)

kundi ResizeHandle(TixWidget):
    """Internal widget to draw resize handles on Scrolled widgets."""
    eleza __init__(self, master, cnf={}, **kw):
        # There seems to be a Tix bug rejecting the configure method
        # Let's try making the flags -static
        flags = ['options', 'command', 'cursorfg', 'cursorbg',
                 'handlesize', 'hintcolor', 'hintwidth',
                 'x', 'y']
        # In fact, x y height width are configurable
        TixWidget.__init__(self, master, 'tixResizeHandle',
                           flags, cnf, kw)

    eleza attach_widget(self, widget):
        self.tk.call(self._w, 'attachwidget', widget._w)

    eleza detach_widget(self, widget):
        self.tk.call(self._w, 'detachwidget', widget._w)

    eleza hide(self, widget):
        self.tk.call(self._w, 'hide', widget._w)

    eleza show(self, widget):
        self.tk.call(self._w, 'show', widget._w)

kundi ScrolledHList(TixWidget):
    """ScrolledHList - HList ukijumuisha automatic scrollbars."""

    # FIXME: It should inherit -superkundi tixScrolledWidget
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledHList', ['options'],
                           cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

kundi ScrolledListBox(TixWidget):
    """ScrolledListBox - Listbox ukijumuisha automatic scrollbars."""

    # FIXME: It should inherit -superkundi tixScrolledWidget
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledListBox', ['options'], cnf, kw)
        self.subwidget_list['listbox'] = _dummyListbox(self, 'listbox')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

kundi ScrolledText(TixWidget):
    """ScrolledText - Text ukijumuisha automatic scrollbars."""

    # FIXME: It should inherit -superkundi tixScrolledWidget
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledText', ['options'], cnf, kw)
        self.subwidget_list['text'] = _dummyText(self, 'text')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

kundi ScrolledTList(TixWidget):
    """ScrolledTList - TList ukijumuisha automatic scrollbars."""

    # FIXME: It should inherit -superkundi tixScrolledWidget
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledTList', ['options'],
                           cnf, kw)
        self.subwidget_list['tlist'] = _dummyTList(self, 'tlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

kundi ScrolledWindow(TixWidget):
    """ScrolledWindow - Window ukijumuisha automatic scrollbars."""

    # FIXME: It should inherit -superkundi tixScrolledWidget
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixScrolledWindow', ['options'], cnf, kw)
        self.subwidget_list['window'] = _dummyFrame(self, 'window')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

kundi Select(TixWidget):
    """Select - Container of button subwidgets. It can be used to provide
    radio-box ama check-box style of selection options kila the user.

    Subwidgets are buttons added dynamically using the add method."""

    # FIXME: It should inherit -superkundi tixLabelWidget
    eleza __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixSelect',
                           ['allowzero', 'radio', 'orientation', 'labelside',
                            'options'],
                           cnf, kw)
        self.subwidget_list['label'] = _dummyLabel(self, 'label')

    eleza add(self, name, cnf={}, **kw):
        self.tk.call(self._w, 'add', name, *self._options(cnf, kw))
        self.subwidget_list[name] = _dummyButton(self, name)
        rudisha self.subwidget_list[name]

    eleza invoke(self, name):
        self.tk.call(self._w, 'invoke', name)

kundi Shell(TixWidget):
    """Toplevel window.

    Subwidgets - Tupu"""

    eleza __init__ (self,master=Tupu,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixShell', ['options', 'title'], cnf, kw)

kundi DialogShell(TixWidget):
    """Toplevel window, ukijumuisha popup popdown na center methods.
    It tells the window manager that it ni a dialog window na should be
    treated specially. The exact treatment depends on the treatment of
    the window manager.

    Subwidgets - Tupu"""

    # FIXME: It should inherit kutoka  Shell
    eleza __init__ (self,master=Tupu,cnf={}, **kw):
        TixWidget.__init__(self, master,
                           'tixDialogShell',
                           ['options', 'title', 'mapped',
                            'minheight', 'minwidth',
                            'parent', 'transient'], cnf, kw)

    eleza popdown(self):
        self.tk.call(self._w, 'popdown')

    eleza popup(self):
        self.tk.call(self._w, 'popup')

    eleza center(self):
        self.tk.call(self._w, 'center')

kundi StdButtonBox(TixWidget):
    """StdButtonBox - Standard Button Box (OK, Apply, Cancel na Help) """

    eleza __init__(self, master=Tupu, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixStdButtonBox',
                           ['orientation', 'options'], cnf, kw)
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['apply'] = _dummyButton(self, 'apply')
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['help'] = _dummyButton(self, 'help')

    eleza invoke(self, name):
        ikiwa name kwenye self.subwidget_list:
            self.tk.call(self._w, 'invoke', name)

kundi TList(TixWidget, XView, YView):
    """TList - Hierarchy display widget which can be
    used to display data kwenye a tabular format. The list entries of a TList
    widget are similar to the entries kwenye the Tk listbox widget. The main
    differences are (1) the TList widget can display the list entries kwenye a
    two dimensional format na (2) you can use graphical images kama well as
    multiple colors na fonts kila the list entries.

    Subwidgets - Tupu"""

    eleza __init__ (self,master=Tupu,cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixTList', ['options'], cnf, kw)

    eleza active_set(self, index):
        self.tk.call(self._w, 'active', 'set', index)

    eleza active_clear(self):
        self.tk.call(self._w, 'active', 'clear')

    eleza anchor_set(self, index):
        self.tk.call(self._w, 'anchor', 'set', index)

    eleza anchor_clear(self):
        self.tk.call(self._w, 'anchor', 'clear')

    eleza delete(self, from_, to=Tupu):
        self.tk.call(self._w, 'delete', from_, to)

    eleza dragsite_set(self, index):
        self.tk.call(self._w, 'dragsite', 'set', index)

    eleza dragsite_clear(self):
        self.tk.call(self._w, 'dragsite', 'clear')

    eleza dropsite_set(self, index):
        self.tk.call(self._w, 'dropsite', 'set', index)

    eleza dropsite_clear(self):
        self.tk.call(self._w, 'dropsite', 'clear')

    eleza insert(self, index, cnf={}, **kw):
        self.tk.call(self._w, 'insert', index, *self._options(cnf, kw))

    eleza info_active(self):
        rudisha self.tk.call(self._w, 'info', 'active')

    eleza info_anchor(self):
        rudisha self.tk.call(self._w, 'info', 'anchor')

    eleza info_down(self, index):
        rudisha self.tk.call(self._w, 'info', 'down', index)

    eleza info_left(self, index):
        rudisha self.tk.call(self._w, 'info', 'left', index)

    eleza info_right(self, index):
        rudisha self.tk.call(self._w, 'info', 'right', index)

    eleza info_selection(self):
        c = self.tk.call(self._w, 'info', 'selection')
        rudisha self.tk.splitlist(c)

    eleza info_size(self):
        rudisha self.tk.call(self._w, 'info', 'size')

    eleza info_up(self, index):
        rudisha self.tk.call(self._w, 'info', 'up', index)

    eleza nearest(self, x, y):
        rudisha self.tk.call(self._w, 'nearest', x, y)

    eleza see(self, index):
        self.tk.call(self._w, 'see', index)

    eleza selection_clear(self, cnf={}, **kw):
        self.tk.call(self._w, 'selection', 'clear', *self._options(cnf, kw))

    eleza selection_includes(self, index):
        rudisha self.tk.call(self._w, 'selection', 'includes', index)

    eleza selection_set(self, first, last=Tupu):
        self.tk.call(self._w, 'selection', 'set', first, last)

kundi Tree(TixWidget):
    """Tree - The tixTree widget can be used to display hierarchical
    data kwenye a tree form. The user can adjust
    the view of the tree by opening ama closing parts of the tree."""

    # FIXME: It should inherit -superkundi tixScrolledWidget
    eleza __init__(self, master=Tupu, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixTree',
                           ['options'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    eleza autosetmode(self):
        '''This command calls the setmode method kila all the entries kwenye this
     Tree widget: ikiwa an entry has no child entries, its mode ni set to
     none. Otherwise, ikiwa the entry has any hidden child entries, its mode is
     set to open; otherwise its mode ni set to close.'''
        self.tk.call(self._w, 'autosetmode')

    eleza close(self, entrypath):
        '''Close the entry given by entryPath ikiwa its mode ni close.'''
        self.tk.call(self._w, 'close', entrypath)

    eleza getmode(self, entrypath):
        '''Returns the current mode of the entry given by entryPath.'''
        rudisha self.tk.call(self._w, 'getmode', entrypath)

    eleza open(self, entrypath):
        '''Open the entry given by entryPath ikiwa its mode ni open.'''
        self.tk.call(self._w, 'open', entrypath)

    eleza setmode(self, entrypath, mode='none'):
        '''This command ni used to indicate whether the entry given by
     entryPath has children entries na whether the children are visible. mode
     must be one of open, close ama none. If mode ni set to open, a (+)
     indicator ni drawn next the entry. If mode ni set to close, a (-)
     indicator ni drawn next the entry. If mode ni set to none, no
     indicators will be drawn kila this entry. The default mode ni none. The
     open mode indicates the entry has hidden children na this entry can be
     opened by the user. The close mode indicates that all the children of the
     entry are now visible na the entry can be closed by the user.'''
        self.tk.call(self._w, 'setmode', entrypath, mode)


# Could try subclassing Tree kila CheckList - would need another arg to init
kundi CheckList(TixWidget):
    """The CheckList widget
    displays a list of items to be selected by the user. CheckList acts
    similarly to the Tk checkbutton ama radiobutton widgets, tatizo it is
    capable of handling many more items than checkbuttons ama radiobuttons.
    """
    # FIXME: It should inherit -superkundi tixTree
    eleza __init__(self, master=Tupu, cnf={}, **kw):
        TixWidget.__init__(self, master, 'tixCheckList',
                           ['options', 'radio'], cnf, kw)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

    eleza autosetmode(self):
        '''This command calls the setmode method kila all the entries kwenye this
     Tree widget: ikiwa an entry has no child entries, its mode ni set to
     none. Otherwise, ikiwa the entry has any hidden child entries, its mode is
     set to open; otherwise its mode ni set to close.'''
        self.tk.call(self._w, 'autosetmode')

    eleza close(self, entrypath):
        '''Close the entry given by entryPath ikiwa its mode ni close.'''
        self.tk.call(self._w, 'close', entrypath)

    eleza getmode(self, entrypath):
        '''Returns the current mode of the entry given by entryPath.'''
        rudisha self.tk.call(self._w, 'getmode', entrypath)

    eleza open(self, entrypath):
        '''Open the entry given by entryPath ikiwa its mode ni open.'''
        self.tk.call(self._w, 'open', entrypath)

    eleza getselection(self, mode='on'):
        '''Returns a list of items whose status matches status. If status is
     sio specified, the list of items kwenye the "on" status will be returned.
     Mode can be on, off, default'''
        rudisha self.tk.splitlist(self.tk.call(self._w, 'getselection', mode))

    eleza getstatus(self, entrypath):
        '''Returns the current status of entryPath.'''
        rudisha self.tk.call(self._w, 'getstatus', entrypath)

    eleza setstatus(self, entrypath, mode='on'):
        '''Sets the status of entryPath to be status. A bitmap will be
     displayed next to the entry its status ni on, off ama default.'''
        self.tk.call(self._w, 'setstatus', entrypath, mode)


###########################################################################
### The subclassing below ni used to instantiate the subwidgets kwenye each ###
### mega widget. This allows us to access their methods directly.       ###
###########################################################################

kundi _dummyButton(Button, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyCheckbutton(Checkbutton, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyEntry(Entry, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyFrame(Frame, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyLabel(Label, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyListbox(Listbox, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyMenu(Menu, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyMenubutton(Menubutton, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyScrollbar(Scrollbar, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyText(Text, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyScrolledListBox(ScrolledListBox, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['listbox'] = _dummyListbox(self, 'listbox')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

kundi _dummyHList(HList, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyScrolledHList(ScrolledHList, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

kundi _dummyTList(TList, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyComboBox(ComboBox, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, ['fancy',destroy_physically])
        self.subwidget_list['label'] = _dummyLabel(self, 'label')
        self.subwidget_list['entry'] = _dummyEntry(self, 'entry')
        self.subwidget_list['arrow'] = _dummyButton(self, 'arrow')

        self.subwidget_list['slistbox'] = _dummyScrolledListBox(self,
                                                                'slistbox')
        jaribu:
            self.subwidget_list['tick'] = _dummyButton(self, 'tick')
            #cross Button : present ikiwa created ukijumuisha the fancy option
            self.subwidget_list['cross'] = _dummyButton(self, 'cross')
        tatizo TypeError:
            # unavailable when -fancy sio specified
            pita

kundi _dummyDirList(DirList, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['hlist'] = _dummyHList(self, 'hlist')
        self.subwidget_list['vsb'] = _dummyScrollbar(self, 'vsb')
        self.subwidget_list['hsb'] = _dummyScrollbar(self, 'hsb')

kundi _dummyDirSelectBox(DirSelectBox, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['dirlist'] = _dummyDirList(self, 'dirlist')
        self.subwidget_list['dircbx'] = _dummyFileComboBox(self, 'dircbx')

kundi _dummyExFileSelectBox(ExFileSelectBox, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['hidden'] = _dummyCheckbutton(self, 'hidden')
        self.subwidget_list['types'] = _dummyComboBox(self, 'types')
        self.subwidget_list['dir'] = _dummyComboBox(self, 'dir')
        self.subwidget_list['dirlist'] = _dummyScrolledListBox(self, 'dirlist')
        self.subwidget_list['file'] = _dummyComboBox(self, 'file')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')

kundi _dummyFileSelectBox(FileSelectBox, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['dirlist'] = _dummyScrolledListBox(self, 'dirlist')
        self.subwidget_list['filelist'] = _dummyScrolledListBox(self, 'filelist')
        self.subwidget_list['filter'] = _dummyComboBox(self, 'filter')
        self.subwidget_list['selection'] = _dummyComboBox(self, 'selection')

kundi _dummyFileComboBox(ComboBox, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['dircbx'] = _dummyComboBox(self, 'dircbx')

kundi _dummyStdButtonBox(StdButtonBox, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)
        self.subwidget_list['ok'] = _dummyButton(self, 'ok')
        self.subwidget_list['apply'] = _dummyButton(self, 'apply')
        self.subwidget_list['cancel'] = _dummyButton(self, 'cancel')
        self.subwidget_list['help'] = _dummyButton(self, 'help')

kundi _dummyNoteBookFrame(NoteBookFrame, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=0):
        TixSubWidget.__init__(self, master, name, destroy_physically)

kundi _dummyPanedWindow(PanedWindow, TixSubWidget):
    eleza __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

########################
### Utility Routines ###
########################

#mike Should tixDestroy be exposed kama a wrapper? - but sio kila widgets.

eleza OptionName(widget):
    '''Returns the qualified path name kila the widget. Normally used to set
    default options kila subwidgets. See tixwidgets.py'''
    rudisha widget.tk.call('tixOptionName', widget._w)

# Called ukijumuisha a dictionary argument of the form
# {'*.c':'C source files', '*.txt':'Text Files', '*':'All files'}
# returns a string which can be used to configure the fsbox file types
# kwenye an ExFileSelectBox. i.e.,
# '{{*} {* - All files}} {{*.c} {*.c - C source files}} {{*.txt} {*.txt - Text Files}}'
eleza FileTypeList(dict):
    s = ''
    kila type kwenye dict.keys():
        s = s + '{{' + type + '} {' + type + ' - ' + dict[type] + '}} '
    rudisha s

# Still to be done:
# tixIconView
kundi CObjView(TixWidget):
    """This file implements the Canvas Object View widget. This ni a base
    kundi of IconView. It implements automatic placement/adjustment of the
    scrollbars according to the canvas objects inside the canvas subwidget.
    The scrollbars are adjusted so that the canvas ni just large enough
    to see all the objects.
    """
    # FIXME: It should inherit -superkundi tixScrolledWidget
    pita


kundi Grid(TixWidget, XView, YView):
    '''The Tix Grid command creates a new window  na makes it into a
    tixGrid widget. Additional options, may be specified on the command
    line ama kwenye the option database to configure aspects such kama its cursor
    na relief.

    A Grid widget displays its contents kwenye a two dimensional grid of cells.
    Each cell may contain one Tix display item, which may be kwenye text,
    graphics ama other formats. See the DisplayStyle kundi kila more information
    about Tix display items. Individual cells, ama groups of cells, can be
    formatted ukijumuisha a wide range of attributes, such kama its color, relief na
    border.

    Subwidgets - Tupu'''
    # valid specific resources kama of Tk 8.4
    # editdonecmd, editnotifycmd, floatingcols, floatingrows, formatcmd,
    # highlightbackground, highlightcolor, leftmargin, itemtype, selectmode,
    # selectunit, topmargin,
    eleza __init__(self, master=Tupu, cnf={}, **kw):
        static= []
        self.cnf= cnf
        TixWidget.__init__(self, master, 'tixGrid', static, cnf, kw)

    # valid options kama of Tk 8.4
    # anchor, bdtype, cget, configure, delete, dragsite, dropsite, entrycget,
    # edit, entryconfigure, format, geometryinfo, info, index, move, nearest,
    # selection, set, size, unset, xview, yview
    eleza anchor_clear(self):
        """Removes the selection anchor."""
        self.tk.call(self, 'anchor', 'clear')

    eleza anchor_get(self):
        "Get the (x,y) coordinate of the current anchor cell"
        rudisha self._getints(self.tk.call(self, 'anchor', 'get'))

    eleza anchor_set(self, x, y):
        """Set the selection anchor to the cell at (x, y)."""
        self.tk.call(self, 'anchor', 'set', x, y)

    eleza delete_row(self, from_, to=Tupu):
        """Delete rows between from_ na to inclusive.
        If to ni sio provided,  delete only row at from_"""
        ikiwa to ni Tupu:
            self.tk.call(self, 'delete', 'row', from_)
        isipokua:
            self.tk.call(self, 'delete', 'row', from_, to)

    eleza delete_column(self, from_, to=Tupu):
        """Delete columns between from_ na to inclusive.
        If to ni sio provided,  delete only column at from_"""
        ikiwa to ni Tupu:
            self.tk.call(self, 'delete', 'column', from_)
        isipokua:
            self.tk.call(self, 'delete', 'column', from_, to)

    eleza edit_apply(self):
        """If any cell ni being edited, de-highlight the cell  na  applies
        the changes."""
        self.tk.call(self, 'edit', 'apply')

    eleza edit_set(self, x, y):
        """Highlights  the  cell  at  (x, y) kila editing, ikiwa the -editnotify
        command returns Kweli kila this cell."""
        self.tk.call(self, 'edit', 'set', x, y)

    eleza entrycget(self, x, y, option):
        "Get the option value kila cell at (x,y)"
        ikiwa option na option[0] != '-':
            option = '-' + option
        rudisha self.tk.call(self, 'entrycget', x, y, option)

    eleza entryconfigure(self, x, y, cnf=Tupu, **kw):
        rudisha self._configure(('entryconfigure', x, y), cnf, kw)

    # eleza format
    # eleza index

    eleza info_exists(self, x, y):
        "Return Kweli ikiwa display item exists at (x,y)"
        rudisha self._getboolean(self.tk.call(self, 'info', 'exists', x, y))

    eleza info_bbox(self, x, y):
        # This seems to always rudisha '', at least kila 'text' displayitems
        rudisha self.tk.call(self, 'info', 'bbox', x, y)

    eleza move_column(self, from_, to, offset):
        """Moves the range of columns kutoka position FROM through TO by
        the distance indicated by OFFSET. For example, move_column(2, 4, 1)
        moves the columns 2,3,4 to columns 3,4,5."""
        self.tk.call(self, 'move', 'column', from_, to, offset)

    eleza move_row(self, from_, to, offset):
        """Moves the range of rows kutoka position FROM through TO by
        the distance indicated by OFFSET.
        For example, move_row(2, 4, 1) moves the rows 2,3,4 to rows 3,4,5."""
        self.tk.call(self, 'move', 'row', from_, to, offset)

    eleza nearest(self, x, y):
        "Return coordinate of cell nearest pixel coordinate (x,y)"
        rudisha self._getints(self.tk.call(self, 'nearest', x, y))

    # eleza selection adjust
    # eleza selection clear
    # eleza selection includes
    # eleza selection set
    # eleza selection toggle

    eleza set(self, x, y, itemtype=Tupu, **kw):
        args= self._options(self.cnf, kw)
        ikiwa itemtype ni sio Tupu:
            args= ('-itemtype', itemtype) + args
        self.tk.call(self, 'set', x, y, *args)

    eleza size_column(self, index, **kw):
        """Queries ama sets the size of the column given by
        INDEX.  INDEX may be any non-negative
        integer that gives the position of a given column.
        INDEX can also be the string "default"; kwenye this case, this command
        queries ama sets the default size of all columns.
        When no option-value pair ni given, this command returns a tuple
        containing the current size setting of the given column.  When
        option-value pairs are given, the corresponding options of the
        size setting of the given column are changed. Options may be one
        of the follwing:
              pad0 pixels
                     Specifies the paddings to the left of a column.
              pad1 pixels
                     Specifies the paddings to the right of a column.
              size val
                     Specifies the width of a column.  Val may be:
                     "auto" -- the width of the column ni set to the
                     width of the widest cell kwenye the column;
                     a valid Tk screen distance unit;
                     ama a real number following by the word chars
                     (e.g. 3.4chars) that sets the width of the column to the
                     given number of characters."""
        rudisha self.tk.splitlist(self.tk.call(self._w, 'size', 'column', index,
                             *self._options({}, kw)))

    eleza size_row(self, index, **kw):
        """Queries ama sets the size of the row given by
        INDEX. INDEX may be any non-negative
        integer that gives the position of a given row .
        INDEX can also be the string "default"; kwenye this case, this command
        queries ama sets the default size of all rows.
        When no option-value pair ni given, this command returns a list con-
        taining the current size setting of the given row . When option-value
        pairs are given, the corresponding options of the size setting of the
        given row are changed. Options may be one of the follwing:
              pad0 pixels
                     Specifies the paddings to the top of a row.
              pad1 pixels
                     Specifies the paddings to the bottom of a row.
              size val
                     Specifies the height of a row.  Val may be:
                     "auto" -- the height of the row ni set to the
                     height of the highest cell kwenye the row;
                     a valid Tk screen distance unit;
                     ama a real number following by the word chars
                     (e.g. 3.4chars) that sets the height of the row to the
                     given number of characters."""
        rudisha self.tk.splitlist(self.tk.call(
                    self, 'size', 'row', index, *self._options({}, kw)))

    eleza unset(self, x, y):
        """Clears the cell at (x, y) by removing its display item."""
        self.tk.call(self._w, 'unset', x, y)


kundi ScrolledGrid(Grid):
    '''Scrolled Grid widgets'''

    # FIXME: It should inherit -superkundi tixScrolledWidget
    eleza __init__(self, master=Tupu, cnf={}, **kw):
        static= []
        self.cnf= cnf
        TixWidget.__init__(self, master, 'tixScrolledGrid', static, cnf, kw)
