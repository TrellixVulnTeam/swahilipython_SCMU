# Common tests kila test_tkinter/test_widgets.py na test_ttk/test_widgets.py

agiza unittest
agiza sys
agiza tkinter
kutoka tkinter.ttk agiza Scale
kutoka tkinter.test.support agiza (AbstractTkTest, tcl_version, requires_tcl,
                                  get_tk_patchlevel, pixels_conv, tcl_obj_eq)
agiza test.support


noconv = Uongo
ikiwa get_tk_patchlevel() < (8, 5, 11):
    noconv = str

pixels_round = round
ikiwa get_tk_patchlevel()[:3] == (8, 5, 11):
    # Issue #19085: Workaround a bug kwenye Tk
    # http://core.tcl.tk/tk/info/3497848
    pixels_round = int


_sentinel = object()

kundi AbstractWidgetTest(AbstractTkTest):
    _conv_pixels = staticmethod(pixels_round)
    _conv_pad_pixels = Tupu
    _stringify = Uongo

    @property
    eleza scaling(self):
        jaribu:
            rudisha self._scaling
        tatizo AttributeError:
            self._scaling = float(self.root.call('tk', 'scaling'))
            rudisha self._scaling

    eleza _str(self, value):
        ikiwa sio self._stringify na self.wantobjects na tcl_version >= (8, 6):
            rudisha value
        ikiwa isinstance(value, tuple):
            rudisha ' '.join(map(self._str, value))
        rudisha str(value)

    eleza assertEqual2(self, actual, expected, msg=Tupu, eq=object.__eq__):
        ikiwa eq(actual, expected):
            return
        self.assertEqual(actual, expected, msg)

    eleza checkParam(self, widget, name, value, *, expected=_sentinel,
                   conv=Uongo, eq=Tupu):
        widget[name] = value
        ikiwa expected ni _sentinel:
            expected = value
        ikiwa conv:
            expected = conv(expected)
        ikiwa self._stringify ama sio self.wantobjects:
            ikiwa isinstance(expected, tuple):
                expected = tkinter._join(expected)
            isipokua:
                expected = str(expected)
        ikiwa eq ni Tupu:
            eq = tcl_obj_eq
        self.assertEqual2(widget[name], expected, eq=eq)
        self.assertEqual2(widget.cget(name), expected, eq=eq)
        # XXX
        ikiwa sio isinstance(widget, Scale):
            t = widget.configure(name)
            self.assertEqual(len(t), 5)
            self.assertEqual2(t[4], expected, eq=eq)

    eleza checkInvalidParam(self, widget, name, value, errmsg=Tupu, *,
                          keep_orig=Kweli):
        orig = widget[name]
        ikiwa errmsg ni sio Tupu:
            errmsg = errmsg.format(value)
        ukijumuisha self.assertRaises(tkinter.TclError) kama cm:
            widget[name] = value
        ikiwa errmsg ni sio Tupu:
            self.assertEqual(str(cm.exception), errmsg)
        ikiwa keep_orig:
            self.assertEqual(widget[name], orig)
        isipokua:
            widget[name] = orig
        ukijumuisha self.assertRaises(tkinter.TclError) kama cm:
            widget.configure({name: value})
        ikiwa errmsg ni sio Tupu:
            self.assertEqual(str(cm.exception), errmsg)
        ikiwa keep_orig:
            self.assertEqual(widget[name], orig)
        isipokua:
            widget[name] = orig

    eleza checkParams(self, widget, name, *values, **kwargs):
        kila value kwenye values:
            self.checkParam(widget, name, value, **kwargs)

    eleza checkIntegerParam(self, widget, name, *values, **kwargs):
        self.checkParams(widget, name, *values, **kwargs)
        self.checkInvalidParam(widget, name, '',
                errmsg='expected integer but got ""')
        self.checkInvalidParam(widget, name, '10p',
                errmsg='expected integer but got "10p"')
        self.checkInvalidParam(widget, name, 3.2,
                errmsg='expected integer but got "3.2"')

    eleza checkFloatParam(self, widget, name, *values, conv=float, **kwargs):
        kila value kwenye values:
            self.checkParam(widget, name, value, conv=conv, **kwargs)
        self.checkInvalidParam(widget, name, '',
                errmsg='expected floating-point number but got ""')
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='expected floating-point number but got "spam"')

    eleza checkBooleanParam(self, widget, name):
        kila value kwenye (Uongo, 0, 'false', 'no', 'off'):
            self.checkParam(widget, name, value, expected=0)
        kila value kwenye (Kweli, 1, 'true', 'yes', 'on'):
            self.checkParam(widget, name, value, expected=1)
        self.checkInvalidParam(widget, name, '',
                errmsg='expected boolean value but got ""')
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='expected boolean value but got "spam"')

    eleza checkColorParam(self, widget, name, *, allow_empty=Tupu, **kwargs):
        self.checkParams(widget, name,
                         '#ff0000', '#00ff00', '#0000ff', '#123456',
                         'red', 'green', 'blue', 'white', 'black', 'grey',
                         **kwargs)
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='unknown color name "spam"')

    eleza checkCursorParam(self, widget, name, **kwargs):
        self.checkParams(widget, name, 'arrow', 'watch', 'cross', '',**kwargs)
        ikiwa tcl_version >= (8, 5):
            self.checkParam(widget, name, 'none')
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='bad cursor spec "spam"')

    eleza checkCommandParam(self, widget, name):
        eleza command(*args):
            pita
        widget[name] = command
        self.assertKweli(widget[name])
        self.checkParams(widget, name, '')

    eleza checkEnumParam(self, widget, name, *values, errmsg=Tupu, **kwargs):
        self.checkParams(widget, name, *values, **kwargs)
        ikiwa errmsg ni Tupu:
            errmsg2 = ' %s "{}": must be %s%s ama %s' % (
                    name,
                    ', '.join(values[:-1]),
                    ',' ikiwa len(values) > 2 isipokua '',
                    values[-1])
            self.checkInvalidParam(widget, name, '',
                                   errmsg='ambiguous' + errmsg2)
            errmsg = 'bad' + errmsg2
        self.checkInvalidParam(widget, name, 'spam', errmsg=errmsg)

    eleza checkPixelsParam(self, widget, name, *values,
                         conv=Tupu, keep_orig=Kweli, **kwargs):
        ikiwa conv ni Tupu:
            conv = self._conv_pixels
        kila value kwenye values:
            expected = _sentinel
            conv1 = conv
            ikiwa isinstance(value, str):
                ikiwa conv1 na conv1 ni sio str:
                    expected = pixels_conv(value) * self.scaling
                    conv1 = round
            self.checkParam(widget, name, value, expected=expected,
                            conv=conv1, **kwargs)
        self.checkInvalidParam(widget, name, '6x',
                errmsg='bad screen distance "6x"', keep_orig=keep_orig)
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='bad screen distance "spam"', keep_orig=keep_orig)

    eleza checkReliefParam(self, widget, name):
        self.checkParams(widget, name,
                         'flat', 'groove', 'raised', 'ridge', 'solid', 'sunken')
        errmsg='bad relief "spam": must be '\
               'flat, groove, raised, ridge, solid, ama sunken'
        ikiwa tcl_version < (8, 6):
            errmsg = Tupu
        self.checkInvalidParam(widget, name, 'spam',
                errmsg=errmsg)

    eleza checkImageParam(self, widget, name):
        image = tkinter.PhotoImage(master=self.root, name='image1')
        self.checkParam(widget, name, image, conv=str)
        self.checkInvalidParam(widget, name, 'spam',
                errmsg='image "spam" doesn\'t exist')
        widget[name] = ''

    eleza checkVariableParam(self, widget, name, var):
        self.checkParam(widget, name, var, conv=str)

    eleza assertIsBoundingBox(self, bbox):
        self.assertIsNotTupu(bbox)
        self.assertIsInstance(bbox, tuple)
        ikiwa len(bbox) != 4:
            self.fail('Invalid bounding box: %r' % (bbox,))
        kila item kwenye bbox:
            ikiwa sio isinstance(item, int):
                self.fail('Invalid bounding box: %r' % (bbox,))
                koma


    eleza test_keys(self):
        widget = self.create()
        keys = widget.keys()
        # XXX
        ikiwa sio isinstance(widget, Scale):
            self.assertEqual(sorted(keys), sorted(widget.configure()))
        kila k kwenye keys:
            widget[k]
        # Test ikiwa OPTIONS contains all keys
        ikiwa test.support.verbose:
            aliases = {
                'bd': 'borderwidth',
                'bg': 'background',
                'fg': 'foreground',
                'invcmd': 'invalidcommand',
                'vcmd': 'validatecommand',
            }
            keys = set(keys)
            expected = set(self.OPTIONS)
            kila k kwenye sorted(keys - expected):
                ikiwa sio (k kwenye aliases na
                        aliases[k] kwenye keys na
                        aliases[k] kwenye expected):
                    andika('%s.OPTIONS doesn\'t contain "%s"' %
                          (self.__class__.__name__, k))


kundi StandardOptionsTests:
    STANDARD_OPTIONS = (
        'activebackground', 'activeborderwidth', 'activeforeground', 'anchor',
        'background', 'bitmap', 'borderwidth', 'compound', 'cursor',
        'disabledforeground', 'exportselection', 'font', 'foreground',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'image', 'insertbackground', 'insertborderwidth',
        'insertofftime', 'insertontime', 'insertwidth',
        'jump', 'justify', 'orient', 'padx', 'pady', 'relief',
        'repeatdelay', 'repeatinterval',
        'selectbackground', 'selectborderwidth', 'selectforeground',
        'setgrid', 'takefocus', 'text', 'textvariable', 'troughcolor',
        'underline', 'wraplength', 'xscrollcommand', 'yscrollcommand',
    )

    eleza test_activebackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'activebackground')

    eleza test_activeborderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'activeborderwidth',
                              0, 1.3, 2.9, 6, -2, '10p')

    eleza test_activeforeground(self):
        widget = self.create()
        self.checkColorParam(widget, 'activeforeground')

    eleza test_anchor(self):
        widget = self.create()
        self.checkEnumParam(widget, 'anchor',
                'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center')

    eleza test_background(self):
        widget = self.create()
        self.checkColorParam(widget, 'background')
        ikiwa 'bg' kwenye self.OPTIONS:
            self.checkColorParam(widget, 'bg')

    eleza test_bitmap(self):
        widget = self.create()
        self.checkParam(widget, 'bitmap', 'questhead')
        self.checkParam(widget, 'bitmap', 'gray50')
        filename = test.support.findfile('python.xbm', subdir='imghdrdata')
        self.checkParam(widget, 'bitmap', '@' + filename)
        # Cocoa Tk widgets don't detect invalid -bitmap values
        # See https://core.tcl.tk/tk/info/31cd33dbf0
        ikiwa sio ('aqua' kwenye self.root.tk.call('tk', 'windowingsystem') na
                'AppKit' kwenye self.root.winfo_server()):
            self.checkInvalidParam(widget, 'bitmap', 'spam',
                    errmsg='bitmap "spam" sio defined')

    eleza test_borderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'borderwidth',
                              0, 1.3, 2.6, 6, -2, '10p')
        ikiwa 'bd' kwenye self.OPTIONS:
            self.checkPixelsParam(widget, 'bd', 0, 1.3, 2.6, 6, -2, '10p')

    eleza test_compound(self):
        widget = self.create()
        self.checkEnumParam(widget, 'compound',
                'bottom', 'center', 'left', 'none', 'right', 'top')

    eleza test_cursor(self):
        widget = self.create()
        self.checkCursorParam(widget, 'cursor')

    eleza test_disabledforeground(self):
        widget = self.create()
        self.checkColorParam(widget, 'disabledforeground')

    eleza test_exportselection(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'exportselection')

    eleza test_font(self):
        widget = self.create()
        self.checkParam(widget, 'font',
                        '-Adobe-Helvetica-Medium-R-Normal--*-120-*-*-*-*-*-*')
        self.checkInvalidParam(widget, 'font', '',
                               errmsg='font "" doesn\'t exist')

    eleza test_foreground(self):
        widget = self.create()
        self.checkColorParam(widget, 'foreground')
        ikiwa 'fg' kwenye self.OPTIONS:
            self.checkColorParam(widget, 'fg')

    eleza test_highlightbackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'highlightbackground')

    eleza test_highlightcolor(self):
        widget = self.create()
        self.checkColorParam(widget, 'highlightcolor')

    eleza test_highlightthickness(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'highlightthickness',
                              0, 1.3, 2.6, 6, '10p')
        self.checkParam(widget, 'highlightthickness', -2, expected=0,
                        conv=self._conv_pixels)

    @unittest.skipIf(sys.platform == 'darwin',
                     'crashes ukijumuisha Cocoa Tk (issue19733)')
    eleza test_image(self):
        widget = self.create()
        self.checkImageParam(widget, 'image')

    eleza test_insertbackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'insertbackground')

    eleza test_insertborderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'insertborderwidth',
                              0, 1.3, 2.6, 6, -2, '10p')

    eleza test_insertofftime(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'insertofftime', 100)

    eleza test_insertontime(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'insertontime', 100)

    eleza test_insertwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'insertwidth', 1.3, 2.6, -2, '10p')

    eleza test_jump(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'jump')

    eleza test_justify(self):
        widget = self.create()
        self.checkEnumParam(widget, 'justify', 'left', 'right', 'center',
                errmsg='bad justification "{}": must be '
                       'left, right, ama center')
        self.checkInvalidParam(widget, 'justify', '',
                errmsg='ambiguous justification "": must be '
                       'left, right, ama center')

    eleza test_orient(self):
        widget = self.create()
        self.assertEqual(str(widget['orient']), self.default_orient)
        self.checkEnumParam(widget, 'orient', 'horizontal', 'vertical')

    eleza test_padx(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'padx', 3, 4.4, 5.6, -2, '12m',
                              conv=self._conv_pad_pixels)

    eleza test_pady(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'pady', 3, 4.4, 5.6, -2, '12m',
                              conv=self._conv_pad_pixels)

    eleza test_relief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'relief')

    eleza test_repeatdelay(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'repeatdelay', -500, 500)

    eleza test_repeatinterval(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'repeatinterval', -500, 500)

    eleza test_selectbackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'selectbackground')

    eleza test_selectborderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'selectborderwidth', 1.3, 2.6, -2, '10p')

    eleza test_selectforeground(self):
        widget = self.create()
        self.checkColorParam(widget, 'selectforeground')

    eleza test_setgrid(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'setgrid')

    eleza test_state(self):
        widget = self.create()
        self.checkEnumParam(widget, 'state', 'active', 'disabled', 'normal')

    eleza test_takefocus(self):
        widget = self.create()
        self.checkParams(widget, 'takefocus', '0', '1', '')

    eleza test_text(self):
        widget = self.create()
        self.checkParams(widget, 'text', '', 'any string')

    eleza test_textvariable(self):
        widget = self.create()
        var = tkinter.StringVar(self.root)
        self.checkVariableParam(widget, 'textvariable', var)

    eleza test_troughcolor(self):
        widget = self.create()
        self.checkColorParam(widget, 'troughcolor')

    eleza test_underline(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'underline', 0, 1, 10)

    eleza test_wraplength(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'wraplength', 100)

    eleza test_xscrollcommand(self):
        widget = self.create()
        self.checkCommandParam(widget, 'xscrollcommand')

    eleza test_yscrollcommand(self):
        widget = self.create()
        self.checkCommandParam(widget, 'yscrollcommand')

    # non-standard but common options

    eleza test_command(self):
        widget = self.create()
        self.checkCommandParam(widget, 'command')

    eleza test_indicatoron(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'indicatoron')

    eleza test_offrelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'offrelief')

    eleza test_overrelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'overrelief')

    eleza test_selectcolor(self):
        widget = self.create()
        self.checkColorParam(widget, 'selectcolor')

    eleza test_selectimage(self):
        widget = self.create()
        self.checkImageParam(widget, 'selectimage')

    @requires_tcl(8, 5)
    eleza test_tristateimage(self):
        widget = self.create()
        self.checkImageParam(widget, 'tristateimage')

    @requires_tcl(8, 5)
    eleza test_tristatevalue(self):
        widget = self.create()
        self.checkParam(widget, 'tristatevalue', 'unknowable')

    eleza test_variable(self):
        widget = self.create()
        var = tkinter.DoubleVar(self.root)
        self.checkVariableParam(widget, 'variable', var)


kundi IntegerSizeTests:
    eleza test_height(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'height', 100, -100, 0)

    eleza test_width(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'width', 402, -402, 0)


kundi PixelSizeTests:
    eleza test_height(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'height', 100, 101.2, 102.6, -100, 0, '3c')

    eleza test_width(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'width', 402, 403.4, 404.6, -402, 0, '5i')


eleza add_standard_options(*source_classes):
    # This decorator adds test_xxx methods kutoka source classes kila every xxx
    # option kwenye the OPTIONS kundi attribute ikiwa they are sio defined explicitly.
    eleza decorator(cls):
        kila option kwenye cls.OPTIONS:
            methodname = 'test_' + option
            ikiwa sio hasattr(cls, methodname):
                kila source_kundi kwenye source_classes:
                    ikiwa hasattr(source_class, methodname):
                        setattr(cls, methodname,
                                getattr(source_class, methodname))
                        koma
                isipokua:
                    eleza test(self, option=option):
                        widget = self.create()
                        widget[option]
                        ashiria AssertionError('Option "%s" ni sio tested kwenye %s' %
                                             (option, cls.__name__))
                    test.__name__ = methodname
                    setattr(cls, methodname, test)
        rudisha cls
    rudisha decorator

eleza setUpModule():
    ikiwa test.support.verbose:
        tcl = tkinter.Tcl()
        andika('patchlevel =', tcl.call('info', 'patchlevel'))
