agiza unittest
agiza tkinter
kutoka tkinter agiza TclError
agiza os
agiza sys
kutoka test.support agiza requires

kutoka tkinter.test.support agiza (tcl_version, requires_tcl,
                                  get_tk_patchlevel, widget_eq)
kutoka tkinter.test.widget_tests agiza (
    add_standard_options, noconv, pixels_round,
    AbstractWidgetTest, StandardOptionsTests, IntegerSizeTests, PixelSizeTests,
    setUpModule)

requires('gui')


eleza float_round(x):
    rudisha float(round(x))


kundi AbstractToplevelTest(AbstractWidgetTest, PixelSizeTests):
    _conv_pad_pixels = noconv

    eleza test_class(self):
        widget = self.create()
        self.assertEqual(widget['class'],
                         widget.__class__.__name__.title())
        self.checkInvalidParam(widget, 'class', 'Foo',
                errmsg="can't modify -kundi option after widget ni created")
        widget2 = self.create(class_='Foo')
        self.assertEqual(widget2['class'], 'Foo')

    eleza test_colormap(self):
        widget = self.create()
        self.assertEqual(widget['colormap'], '')
        self.checkInvalidParam(widget, 'colormap', 'new',
                errmsg="can't modify -colormap option after widget ni created")
        widget2 = self.create(colormap='new')
        self.assertEqual(widget2['colormap'], 'new')

    eleza test_container(self):
        widget = self.create()
        self.assertEqual(widget['container'], 0 ikiwa self.wantobjects isipokua '0')
        self.checkInvalidParam(widget, 'container', 1,
                errmsg="can't modify -container option after widget ni created")
        widget2 = self.create(container=Kweli)
        self.assertEqual(widget2['container'], 1 ikiwa self.wantobjects isipokua '1')

    eleza test_visual(self):
        widget = self.create()
        self.assertEqual(widget['visual'], '')
        self.checkInvalidParam(widget, 'visual', 'default',
                errmsg="can't modify -visual option after widget ni created")
        widget2 = self.create(visual='default')
        self.assertEqual(widget2['visual'], 'default')


@add_standard_options(StandardOptionsTests)
kundi ToplevelTest(AbstractToplevelTest, unittest.TestCase):
    OPTIONS = (
        'background', 'borderwidth',
        'class', 'colormap', 'container', 'cursor', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'menu', 'padx', 'pady', 'relief', 'screen',
        'takefocus', 'use', 'visual', 'width',
    )

    eleza create(self, **kwargs):
        rudisha tkinter.Toplevel(self.root, **kwargs)

    eleza test_menu(self):
        widget = self.create()
        menu = tkinter.Menu(self.root)
        self.checkParam(widget, 'menu', menu, eq=widget_eq)
        self.checkParam(widget, 'menu', '')

    eleza test_screen(self):
        widget = self.create()
        self.assertEqual(widget['screen'], '')
        jaribu:
            display = os.environ['DISPLAY']
        tatizo KeyError:
            self.skipTest('No $DISPLAY set.')
        self.checkInvalidParam(widget, 'screen', display,
                errmsg="can't modify -screen option after widget ni created")
        widget2 = self.create(screen=display)
        self.assertEqual(widget2['screen'], display)

    eleza test_use(self):
        widget = self.create()
        self.assertEqual(widget['use'], '')
        parent = self.create(container=Kweli)
        wid = hex(parent.winfo_id())
        ukijumuisha self.subTest(wid=wid):
            widget2 = self.create(use=wid)
            self.assertEqual(widget2['use'], wid)


@add_standard_options(StandardOptionsTests)
kundi FrameTest(AbstractToplevelTest, unittest.TestCase):
    OPTIONS = (
        'background', 'borderwidth',
        'class', 'colormap', 'container', 'cursor', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'padx', 'pady', 'relief', 'takefocus', 'visual', 'width',
    )

    eleza create(self, **kwargs):
        rudisha tkinter.Frame(self.root, **kwargs)


@add_standard_options(StandardOptionsTests)
kundi LabelFrameTest(AbstractToplevelTest, unittest.TestCase):
    OPTIONS = (
        'background', 'borderwidth',
        'class', 'colormap', 'container', 'cursor',
        'font', 'foreground', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'labelanchor', 'labelwidget', 'padx', 'pady', 'relief',
        'takefocus', 'text', 'visual', 'width',
    )

    eleza create(self, **kwargs):
        rudisha tkinter.LabelFrame(self.root, **kwargs)

    eleza test_labelanchor(self):
        widget = self.create()
        self.checkEnumParam(widget, 'labelanchor',
                            'e', 'en', 'es', 'n', 'ne', 'nw',
                            's', 'se', 'sw', 'w', 'wn', 'ws')
        self.checkInvalidParam(widget, 'labelanchor', 'center')

    eleza test_labelwidget(self):
        widget = self.create()
        label = tkinter.Label(self.root, text='Mupp', name='foo')
        self.checkParam(widget, 'labelwidget', label, expected='.foo')
        label.destroy()


kundi AbstractLabelTest(AbstractWidgetTest, IntegerSizeTests):
    _conv_pixels = noconv

    eleza test_highlightthickness(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'highlightthickness',
                              0, 1.3, 2.6, 6, -2, '10p')


@add_standard_options(StandardOptionsTests)
kundi LabelTest(AbstractLabelTest, unittest.TestCase):
    OPTIONS = (
        'activebackground', 'activeforeground', 'anchor',
        'background', 'bitmap', 'borderwidth', 'compound', 'cursor',
        'disabledforeground', 'font', 'foreground', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'image', 'justify', 'padx', 'pady', 'relief', 'state',
        'takefocus', 'text', 'textvariable',
        'underline', 'width', 'wraplength',
    )

    eleza create(self, **kwargs):
        rudisha tkinter.Label(self.root, **kwargs)


@add_standard_options(StandardOptionsTests)
kundi ButtonTest(AbstractLabelTest, unittest.TestCase):
    OPTIONS = (
        'activebackground', 'activeforeground', 'anchor',
        'background', 'bitmap', 'borderwidth',
        'command', 'compound', 'cursor', 'default',
        'disabledforeground', 'font', 'foreground', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'image', 'justify', 'overrelief', 'padx', 'pady', 'relief',
        'repeatdelay', 'repeatinterval',
        'state', 'takefocus', 'text', 'textvariable',
        'underline', 'width', 'wraplength')

    eleza create(self, **kwargs):
        rudisha tkinter.Button(self.root, **kwargs)

    eleza test_default(self):
        widget = self.create()
        self.checkEnumParam(widget, 'default', 'active', 'disabled', 'normal')


@add_standard_options(StandardOptionsTests)
kundi CheckbuttonTest(AbstractLabelTest, unittest.TestCase):
    OPTIONS = (
        'activebackground', 'activeforeground', 'anchor',
        'background', 'bitmap', 'borderwidth',
        'command', 'compound', 'cursor',
        'disabledforeground', 'font', 'foreground', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'image', 'indicatoron', 'justify',
        'offrelief', 'offvalue', 'onvalue', 'overrelief',
        'padx', 'pady', 'relief', 'selectcolor', 'selectimage', 'state',
        'takefocus', 'text', 'textvariable',
        'tristateimage', 'tristatevalue',
        'underline', 'variable', 'width', 'wraplength',
    )

    eleza create(self, **kwargs):
        rudisha tkinter.Checkbutton(self.root, **kwargs)


    eleza test_offvalue(self):
        widget = self.create()
        self.checkParams(widget, 'offvalue', 1, 2.3, '', 'any string')

    eleza test_onvalue(self):
        widget = self.create()
        self.checkParams(widget, 'onvalue', 1, 2.3, '', 'any string')


@add_standard_options(StandardOptionsTests)
kundi RadiobuttonTest(AbstractLabelTest, unittest.TestCase):
    OPTIONS = (
        'activebackground', 'activeforeground', 'anchor',
        'background', 'bitmap', 'borderwidth',
        'command', 'compound', 'cursor',
        'disabledforeground', 'font', 'foreground', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'image', 'indicatoron', 'justify', 'offrelief', 'overrelief',
        'padx', 'pady', 'relief', 'selectcolor', 'selectimage', 'state',
        'takefocus', 'text', 'textvariable',
        'tristateimage', 'tristatevalue',
        'underline', 'value', 'variable', 'width', 'wraplength',
    )

    eleza create(self, **kwargs):
        rudisha tkinter.Radiobutton(self.root, **kwargs)

    eleza test_value(self):
        widget = self.create()
        self.checkParams(widget, 'value', 1, 2.3, '', 'any string')


@add_standard_options(StandardOptionsTests)
kundi MenubuttonTest(AbstractLabelTest, unittest.TestCase):
    OPTIONS = (
        'activebackground', 'activeforeground', 'anchor',
        'background', 'bitmap', 'borderwidth',
        'compound', 'cursor', 'direction',
        'disabledforeground', 'font', 'foreground', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'image', 'indicatoron', 'justify', 'menu',
        'padx', 'pady', 'relief', 'state',
        'takefocus', 'text', 'textvariable',
        'underline', 'width', 'wraplength',
    )
    _conv_pixels = staticmethod(pixels_round)

    eleza create(self, **kwargs):
        rudisha tkinter.Menubutton(self.root, **kwargs)

    eleza test_direction(self):
        widget = self.create()
        self.checkEnumParam(widget, 'direction',
                'above', 'below', 'flush', 'left', 'right')

    eleza test_height(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'height', 100, -100, 0, conv=str)

    test_highlightthickness = StandardOptionsTests.test_highlightthickness

    @unittest.skipIf(sys.platform == 'darwin',
                     'crashes ukijumuisha Cocoa Tk (issue19733)')
    eleza test_image(self):
        widget = self.create()
        image = tkinter.PhotoImage(master=self.root, name='image1')
        self.checkParam(widget, 'image', image, conv=str)
        errmsg = 'image "spam" doesn\'t exist'
        ukijumuisha self.assertRaises(tkinter.TclError) kama cm:
            widget['image'] = 'spam'
        ikiwa errmsg ni sio Tupu:
            self.assertEqual(str(cm.exception), errmsg)
        ukijumuisha self.assertRaises(tkinter.TclError) kama cm:
            widget.configure({'image': 'spam'})
        ikiwa errmsg ni sio Tupu:
            self.assertEqual(str(cm.exception), errmsg)

    eleza test_menu(self):
        widget = self.create()
        menu = tkinter.Menu(widget, name='menu')
        self.checkParam(widget, 'menu', menu, eq=widget_eq)
        menu.destroy()

    eleza test_padx(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'padx', 3, 4.4, 5.6, '12m')
        self.checkParam(widget, 'padx', -2, expected=0)

    eleza test_pady(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'pady', 3, 4.4, 5.6, '12m')
        self.checkParam(widget, 'pady', -2, expected=0)

    eleza test_width(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'width', 402, -402, 0, conv=str)


kundi OptionMenuTest(MenubuttonTest, unittest.TestCase):

    eleza create(self, default='b', values=('a', 'b', 'c'), **kwargs):
        rudisha tkinter.OptionMenu(self.root, Tupu, default, *values, **kwargs)


@add_standard_options(IntegerSizeTests, StandardOptionsTests)
kundi EntryTest(AbstractWidgetTest, unittest.TestCase):
    OPTIONS = (
        'background', 'borderwidth', 'cursor',
        'disabledbackground', 'disabledforeground',
        'exportselection', 'font', 'foreground',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'insertbackground', 'insertborderwidth',
        'insertofftime', 'insertontime', 'insertwidth',
        'invalidcommand', 'justify', 'readonlybackground', 'relief',
        'selectbackground', 'selectborderwidth', 'selectforeground',
        'show', 'state', 'takefocus', 'textvariable',
        'validate', 'validatecommand', 'width', 'xscrollcommand',
    )

    eleza create(self, **kwargs):
        rudisha tkinter.Entry(self.root, **kwargs)

    eleza test_disabledbackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'disabledbackground')

    eleza test_insertborderwidth(self):
        widget = self.create(insertwidth=100)
        self.checkPixelsParam(widget, 'insertborderwidth',
                              0, 1.3, 2.6, 6, -2, '10p')
        # insertborderwidth ni bounded above by a half of insertwidth.
        self.checkParam(widget, 'insertborderwidth', 60, expected=100//2)

    eleza test_insertwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'insertwidth', 1.3, 3.6, '10p')
        self.checkParam(widget, 'insertwidth', 0.1, expected=2)
        self.checkParam(widget, 'insertwidth', -2, expected=2)
        ikiwa pixels_round(0.9) <= 0:
            self.checkParam(widget, 'insertwidth', 0.9, expected=2)
        isipokua:
            self.checkParam(widget, 'insertwidth', 0.9, expected=1)

    eleza test_invalidcommand(self):
        widget = self.create()
        self.checkCommandParam(widget, 'invalidcommand')
        self.checkCommandParam(widget, 'invcmd')

    eleza test_readonlybackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'readonlybackground')

    eleza test_show(self):
        widget = self.create()
        self.checkParam(widget, 'show', '*')
        self.checkParam(widget, 'show', '')
        self.checkParam(widget, 'show', ' ')

    eleza test_state(self):
        widget = self.create()
        self.checkEnumParam(widget, 'state',
                            'disabled', 'normal', 'readonly')

    eleza test_validate(self):
        widget = self.create()
        self.checkEnumParam(widget, 'validate',
                'all', 'key', 'focus', 'focusin', 'focusout', 'none')

    eleza test_validatecommand(self):
        widget = self.create()
        self.checkCommandParam(widget, 'validatecommand')
        self.checkCommandParam(widget, 'vcmd')

    eleza test_selection_methods(self):
        widget = self.create()
        widget.insert(0, '12345')
        self.assertUongo(widget.selection_present())
        widget.selection_range(0, 'end')
        self.assertEqual(widget.selection_get(), '12345')
        self.assertKweli(widget.selection_present())
        widget.selection_from(1)
        widget.selection_to(2)
        self.assertEqual(widget.selection_get(), '2')
        widget.selection_range(3, 4)
        self.assertEqual(widget.selection_get(), '4')
        widget.selection_clear()
        self.assertUongo(widget.selection_present())
        widget.selection_range(0, 'end')
        widget.selection_adjust(4)
        self.assertEqual(widget.selection_get(), '1234')
        widget.selection_adjust(1)
        self.assertEqual(widget.selection_get(), '234')
        widget.selection_adjust(5)
        self.assertEqual(widget.selection_get(), '2345')
        widget.selection_adjust(0)
        self.assertEqual(widget.selection_get(), '12345')
        widget.selection_adjust(0)


@add_standard_options(StandardOptionsTests)
kundi SpinboxTest(EntryTest, unittest.TestCase):
    OPTIONS = (
        'activebackground', 'background', 'borderwidth',
        'buttonbackground', 'buttoncursor', 'buttondownrelief', 'buttonuprelief',
        'command', 'cursor', 'disabledbackground', 'disabledforeground',
        'exportselection', 'font', 'foreground', 'format', 'from',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'increment',
        'insertbackground', 'insertborderwidth',
        'insertofftime', 'insertontime', 'insertwidth',
        'invalidcommand', 'justify', 'relief', 'readonlybackground',
        'repeatdelay', 'repeatinterval',
        'selectbackground', 'selectborderwidth', 'selectforeground',
        'state', 'takefocus', 'textvariable', 'to',
        'validate', 'validatecommand', 'values',
        'width', 'wrap', 'xscrollcommand',
    )

    eleza create(self, **kwargs):
        rudisha tkinter.Spinbox(self.root, **kwargs)

    test_show = Tupu

    eleza test_buttonbackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'buttonbackground')

    eleza test_buttoncursor(self):
        widget = self.create()
        self.checkCursorParam(widget, 'buttoncursor')

    eleza test_buttondownrelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'buttondownrelief')

    eleza test_buttonuprelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'buttonuprelief')

    eleza test_format(self):
        widget = self.create()
        self.checkParam(widget, 'format', '%2f')
        self.checkParam(widget, 'format', '%2.2f')
        self.checkParam(widget, 'format', '%.2f')
        self.checkParam(widget, 'format', '%2.f')
        self.checkInvalidParam(widget, 'format', '%2e-1f')
        self.checkInvalidParam(widget, 'format', '2.2')
        self.checkInvalidParam(widget, 'format', '%2.-2f')
        self.checkParam(widget, 'format', '%-2.02f')
        self.checkParam(widget, 'format', '% 2.02f')
        self.checkParam(widget, 'format', '% -2.200f')
        self.checkParam(widget, 'format', '%09.200f')
        self.checkInvalidParam(widget, 'format', '%d')

    eleza test_from(self):
        widget = self.create()
        self.checkParam(widget, 'to', 100.0)
        self.checkFloatParam(widget, 'from', -10, 10.2, 11.7)
        self.checkInvalidParam(widget, 'from', 200,
                errmsg='-to value must be greater than -kutoka value')

    eleza test_increment(self):
        widget = self.create()
        self.checkFloatParam(widget, 'increment', -1, 1, 10.2, 12.8, 0)

    eleza test_to(self):
        widget = self.create()
        self.checkParam(widget, 'from', -100.0)
        self.checkFloatParam(widget, 'to', -10, 10.2, 11.7)
        self.checkInvalidParam(widget, 'to', -200,
                errmsg='-to value must be greater than -kutoka value')

    eleza test_values(self):
        # XXX
        widget = self.create()
        self.assertEqual(widget['values'], '')
        self.checkParam(widget, 'values', 'mon tue wed thur')
        self.checkParam(widget, 'values', ('mon', 'tue', 'wed', 'thur'),
                        expected='mon tue wed thur')
        self.checkParam(widget, 'values', (42, 3.14, '', 'any string'),
                        expected='42 3.14 {} {any string}')
        self.checkParam(widget, 'values', '')

    eleza test_wrap(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'wrap')

    eleza test_bbox(self):
        widget = self.create()
        self.assertIsBoundingBox(widget.bbox(0))
        self.assertRaises(tkinter.TclError, widget.bbox, 'noindex')
        self.assertRaises(tkinter.TclError, widget.bbox, Tupu)
        self.assertRaises(TypeError, widget.bbox)
        self.assertRaises(TypeError, widget.bbox, 0, 1)

    eleza test_selection_methods(self):
        widget = self.create()
        widget.insert(0, '12345')
        self.assertUongo(widget.selection_present())
        widget.selection_range(0, 'end')
        self.assertEqual(widget.selection_get(), '12345')
        self.assertKweli(widget.selection_present())
        widget.selection_from(1)
        widget.selection_to(2)
        self.assertEqual(widget.selection_get(), '2')
        widget.selection_range(3, 4)
        self.assertEqual(widget.selection_get(), '4')
        widget.selection_clear()
        self.assertUongo(widget.selection_present())
        widget.selection_range(0, 'end')
        widget.selection_adjust(4)
        self.assertEqual(widget.selection_get(), '1234')
        widget.selection_adjust(1)
        self.assertEqual(widget.selection_get(), '234')
        widget.selection_adjust(5)
        self.assertEqual(widget.selection_get(), '2345')
        widget.selection_adjust(0)
        self.assertEqual(widget.selection_get(), '12345')

    eleza test_selection_element(self):
        widget = self.create()
        self.assertEqual(widget.selection_element(), "none")
        widget.selection_element("buttonup")
        self.assertEqual(widget.selection_element(), "buttonup")
        widget.selection_element("buttondown")
        self.assertEqual(widget.selection_element(), "buttondown")


@add_standard_options(StandardOptionsTests)
kundi TextTest(AbstractWidgetTest, unittest.TestCase):
    OPTIONS = (
        'autoseparators', 'background', 'blockcursor', 'borderwidth',
        'cursor', 'endline', 'exportselection',
        'font', 'foreground', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'inactiveselectbackground', 'insertbackground', 'insertborderwidth',
        'insertofftime', 'insertontime', 'insertunfocussed', 'insertwidth',
        'maxundo', 'padx', 'pady', 'relief',
        'selectbackground', 'selectborderwidth', 'selectforeground',
        'setgrid', 'spacing1', 'spacing2', 'spacing3', 'startline', 'state',
        'tabs', 'tabstyle', 'takefocus', 'undo', 'width', 'wrap',
        'xscrollcommand', 'yscrollcommand',
    )
    ikiwa tcl_version < (8, 5):
        _stringify = Kweli

    eleza create(self, **kwargs):
        rudisha tkinter.Text(self.root, **kwargs)

    eleza test_autoseparators(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'autoseparators')

    @requires_tcl(8, 5)
    eleza test_blockcursor(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'blockcursor')

    @requires_tcl(8, 5)
    eleza test_endline(self):
        widget = self.create()
        text = '\n'.join('Line %d' kila i kwenye range(100))
        widget.insert('end', text)
        self.checkParam(widget, 'endline', 200, expected='')
        self.checkParam(widget, 'endline', -10, expected='')
        self.checkInvalidParam(widget, 'endline', 'spam',
                errmsg='expected integer but got "spam"')
        self.checkParam(widget, 'endline', 50)
        self.checkParam(widget, 'startline', 15)
        self.checkInvalidParam(widget, 'endline', 10,
                errmsg='-startline must be less than ama equal to -endline')

    eleza test_height(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'height', 100, 101.2, 102.6, '3c')
        self.checkParam(widget, 'height', -100, expected=1)
        self.checkParam(widget, 'height', 0, expected=1)

    eleza test_maxundo(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'maxundo', 0, 5, -1)

    @requires_tcl(8, 5)
    eleza test_inactiveselectbackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'inactiveselectbackground')

    @requires_tcl(8, 6)
    eleza test_insertunfocussed(self):
        widget = self.create()
        self.checkEnumParam(widget, 'insertunfocussed',
                            'hollow', 'none', 'solid')

    eleza test_selectborderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'selectborderwidth',
                              1.3, 2.6, -2, '10p', conv=noconv,
                              keep_orig=tcl_version >= (8, 5))

    eleza test_spacing1(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'spacing1', 20, 21.4, 22.6, '0.5c')
        self.checkParam(widget, 'spacing1', -5, expected=0)

    eleza test_spacing2(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'spacing2', 5, 6.4, 7.6, '0.1c')
        self.checkParam(widget, 'spacing2', -1, expected=0)

    eleza test_spacing3(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'spacing3', 20, 21.4, 22.6, '0.5c')
        self.checkParam(widget, 'spacing3', -10, expected=0)

    @requires_tcl(8, 5)
    eleza test_startline(self):
        widget = self.create()
        text = '\n'.join('Line %d' kila i kwenye range(100))
        widget.insert('end', text)
        self.checkParam(widget, 'startline', 200, expected='')
        self.checkParam(widget, 'startline', -10, expected='')
        self.checkInvalidParam(widget, 'startline', 'spam',
                errmsg='expected integer but got "spam"')
        self.checkParam(widget, 'startline', 10)
        self.checkParam(widget, 'endline', 50)
        self.checkInvalidParam(widget, 'startline', 70,
                errmsg='-startline must be less than ama equal to -endline')

    eleza test_state(self):
        widget = self.create()
        ikiwa tcl_version < (8, 5):
            self.checkParams(widget, 'state', 'disabled', 'normal')
        isipokua:
            self.checkEnumParam(widget, 'state', 'disabled', 'normal')

    eleza test_tabs(self):
        widget = self.create()
        ikiwa get_tk_patchlevel() < (8, 5, 11):
            self.checkParam(widget, 'tabs', (10.2, 20.7, '1i', '2i'),
                            expected=('10.2', '20.7', '1i', '2i'))
        isipokua:
            self.checkParam(widget, 'tabs', (10.2, 20.7, '1i', '2i'))
        self.checkParam(widget, 'tabs', '10.2 20.7 1i 2i',
                        expected=('10.2', '20.7', '1i', '2i'))
        self.checkParam(widget, 'tabs', '2c left 4c 6c center',
                        expected=('2c', 'left', '4c', '6c', 'center'))
        self.checkInvalidParam(widget, 'tabs', 'spam',
                               errmsg='bad screen distance "spam"',
                               keep_orig=tcl_version >= (8, 5))

    @requires_tcl(8, 5)
    eleza test_tabstyle(self):
        widget = self.create()
        self.checkEnumParam(widget, 'tabstyle', 'tabular', 'wordprocessor')

    eleza test_undo(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'undo')

    eleza test_width(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'width', 402)
        self.checkParam(widget, 'width', -402, expected=1)
        self.checkParam(widget, 'width', 0, expected=1)

    eleza test_wrap(self):
        widget = self.create()
        ikiwa tcl_version < (8, 5):
            self.checkParams(widget, 'wrap', 'char', 'none', 'word')
        isipokua:
            self.checkEnumParam(widget, 'wrap', 'char', 'none', 'word')

    eleza test_bbox(self):
        widget = self.create()
        self.assertIsBoundingBox(widget.bbox('1.1'))
        self.assertIsTupu(widget.bbox('end'))
        self.assertRaises(tkinter.TclError, widget.bbox, 'noindex')
        self.assertRaises(tkinter.TclError, widget.bbox, Tupu)
        self.assertRaises(TypeError, widget.bbox)
        self.assertRaises(TypeError, widget.bbox, '1.1', 'end')


@add_standard_options(PixelSizeTests, StandardOptionsTests)
kundi CanvasTest(AbstractWidgetTest, unittest.TestCase):
    OPTIONS = (
        'background', 'borderwidth',
        'closeenough', 'confine', 'cursor', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'insertbackground', 'insertborderwidth',
        'insertofftime', 'insertontime', 'insertwidth',
        'offset', 'relief', 'scrollregion',
        'selectbackground', 'selectborderwidth', 'selectforeground',
        'state', 'takefocus',
        'xscrollcommand', 'xscrollincrement',
        'yscrollcommand', 'yscrollincrement', 'width',
    )

    _conv_pixels = round
    _stringify = Kweli

    eleza create(self, **kwargs):
        rudisha tkinter.Canvas(self.root, **kwargs)

    eleza test_closeenough(self):
        widget = self.create()
        self.checkFloatParam(widget, 'closeenough', 24, 2.4, 3.6, -3,
                             conv=float)

    eleza test_confine(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'confine')

    eleza test_offset(self):
        widget = self.create()
        self.assertEqual(widget['offset'], '0,0')
        self.checkParams(widget, 'offset',
                'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center')
        self.checkParam(widget, 'offset', '10,20')
        self.checkParam(widget, 'offset', '#5,6')
        self.checkInvalidParam(widget, 'offset', 'spam')

    eleza test_scrollregion(self):
        widget = self.create()
        self.checkParam(widget, 'scrollregion', '0 0 200 150')
        self.checkParam(widget, 'scrollregion', (0, 0, 200, 150),
                        expected='0 0 200 150')
        self.checkParam(widget, 'scrollregion', '')
        self.checkInvalidParam(widget, 'scrollregion', 'spam',
                               errmsg='bad scrollRegion "spam"')
        self.checkInvalidParam(widget, 'scrollregion', (0, 0, 200, 'spam'))
        self.checkInvalidParam(widget, 'scrollregion', (0, 0, 200))
        self.checkInvalidParam(widget, 'scrollregion', (0, 0, 200, 150, 0))

    eleza test_state(self):
        widget = self.create()
        self.checkEnumParam(widget, 'state', 'disabled', 'normal',
                errmsg='bad state value "{}": must be normal ama disabled')

    eleza test_xscrollincrement(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'xscrollincrement',
                              40, 0, 41.2, 43.6, -40, '0.5i')

    eleza test_yscrollincrement(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'yscrollincrement',
                              10, 0, 11.2, 13.6, -10, '0.1i')

    @requires_tcl(8, 6)
    eleza test_moveto(self):
        widget = self.create()
        i1 = widget.create_rectangle(1, 1, 20, 20, tags='group')
        i2 = widget.create_rectangle(30, 30, 50, 70, tags='group')
        x1, y1, _, _ = widget.bbox(i1)
        x2, y2, _, _ = widget.bbox(i2)
        widget.moveto('group', 200, 100)
        x1_2, y1_2, _, _ = widget.bbox(i1)
        x2_2, y2_2, _, _ = widget.bbox(i2)
        self.assertEqual(x1_2, 200)
        self.assertEqual(y1_2, 100)
        self.assertEqual(x2 - x1, x2_2 - x1_2)
        self.assertEqual(y2 - y1, y2_2 - y1_2)
        widget.tag_lower(i2, i1)
        widget.moveto('group', y=50)
        x1_3, y1_3, _, _ = widget.bbox(i1)
        x2_3, y2_3, _, _ = widget.bbox(i2)
        self.assertEqual(y2_3, 50)
        self.assertEqual(x2_3, x2_2)
        self.assertEqual(x2_2 - x1_2, x2_3 - x1_3)
        self.assertEqual(y2_2 - y1_2, y2_3 - y1_3)


@add_standard_options(IntegerSizeTests, StandardOptionsTests)
kundi ListboxTest(AbstractWidgetTest, unittest.TestCase):
    OPTIONS = (
        'activestyle', 'background', 'borderwidth', 'cursor',
        'disabledforeground', 'exportselection',
        'font', 'foreground', 'height',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'justify', 'listvariable', 'relief',
        'selectbackground', 'selectborderwidth', 'selectforeground',
        'selectmode', 'setgrid', 'state',
        'takefocus', 'width', 'xscrollcommand', 'yscrollcommand',
    )

    eleza create(self, **kwargs):
        rudisha tkinter.Listbox(self.root, **kwargs)

    eleza test_activestyle(self):
        widget = self.create()
        self.checkEnumParam(widget, 'activestyle',
                            'dotbox', 'none', 'underline')

    test_justify = requires_tcl(8, 6, 5)(StandardOptionsTests.test_justify)

    eleza test_listvariable(self):
        widget = self.create()
        var = tkinter.DoubleVar(self.root)
        self.checkVariableParam(widget, 'listvariable', var)

    eleza test_selectmode(self):
        widget = self.create()
        self.checkParam(widget, 'selectmode', 'single')
        self.checkParam(widget, 'selectmode', 'browse')
        self.checkParam(widget, 'selectmode', 'multiple')
        self.checkParam(widget, 'selectmode', 'extended')

    eleza test_state(self):
        widget = self.create()
        self.checkEnumParam(widget, 'state', 'disabled', 'normal')

    eleza test_itemconfigure(self):
        widget = self.create()
        ukijumuisha self.assertRaisesRegex(TclError, 'item number "0" out of range'):
            widget.itemconfigure(0)
        colors = 'red orange yellow green blue white violet'.split()
        widget.insert('end', *colors)
        kila i, color kwenye enumerate(colors):
            widget.itemconfigure(i, background=color)
        ukijumuisha self.assertRaises(TypeError):
            widget.itemconfigure()
        ukijumuisha self.assertRaisesRegex(TclError, 'bad listbox index "red"'):
            widget.itemconfigure('red')
        self.assertEqual(widget.itemconfigure(0, 'background'),
                         ('background', 'background', 'Background', '', 'red'))
        self.assertEqual(widget.itemconfigure('end', 'background'),
                         ('background', 'background', 'Background', '', 'violet'))
        self.assertEqual(widget.itemconfigure('@0,0', 'background'),
                         ('background', 'background', 'Background', '', 'red'))

        d = widget.itemconfigure(0)
        self.assertIsInstance(d, dict)
        kila k, v kwenye d.items():
            self.assertIn(len(v), (2, 5))
            ikiwa len(v) == 5:
                self.assertEqual(v, widget.itemconfigure(0, k))
                self.assertEqual(v[4], widget.itemcget(0, k))

    eleza check_itemconfigure(self, name, value):
        widget = self.create()
        widget.insert('end', 'a', 'b', 'c', 'd')
        widget.itemconfigure(0, **{name: value})
        self.assertEqual(widget.itemconfigure(0, name)[4], value)
        self.assertEqual(widget.itemcget(0, name), value)
        ukijumuisha self.assertRaisesRegex(TclError, 'unknown color name "spam"'):
            widget.itemconfigure(0, **{name: 'spam'})

    eleza test_itemconfigure_background(self):
        self.check_itemconfigure('background', '#ff0000')

    eleza test_itemconfigure_bg(self):
        self.check_itemconfigure('bg', '#ff0000')

    eleza test_itemconfigure_fg(self):
        self.check_itemconfigure('fg', '#110022')

    eleza test_itemconfigure_foreground(self):
        self.check_itemconfigure('foreground', '#110022')

    eleza test_itemconfigure_selectbackground(self):
        self.check_itemconfigure('selectbackground', '#110022')

    eleza test_itemconfigure_selectforeground(self):
        self.check_itemconfigure('selectforeground', '#654321')

    eleza test_box(self):
        lb = self.create()
        lb.insert(0, *('el%d' % i kila i kwenye range(8)))
        lb.pack()
        self.assertIsBoundingBox(lb.bbox(0))
        self.assertIsTupu(lb.bbox(-1))
        self.assertIsTupu(lb.bbox(10))
        self.assertRaises(TclError, lb.bbox, 'noindex')
        self.assertRaises(TclError, lb.bbox, Tupu)
        self.assertRaises(TypeError, lb.bbox)
        self.assertRaises(TypeError, lb.bbox, 0, 1)

    eleza test_curselection(self):
        lb = self.create()
        lb.insert(0, *('el%d' % i kila i kwenye range(8)))
        lb.selection_clear(0, tkinter.END)
        lb.selection_set(2, 4)
        lb.selection_set(6)
        self.assertEqual(lb.curselection(), (2, 3, 4, 6))
        self.assertRaises(TypeError, lb.curselection, 0)

    eleza test_get(self):
        lb = self.create()
        lb.insert(0, *('el%d' % i kila i kwenye range(8)))
        self.assertEqual(lb.get(0), 'el0')
        self.assertEqual(lb.get(3), 'el3')
        self.assertEqual(lb.get('end'), 'el7')
        self.assertEqual(lb.get(8), '')
        self.assertEqual(lb.get(-1), '')
        self.assertEqual(lb.get(3, 5), ('el3', 'el4', 'el5'))
        self.assertEqual(lb.get(5, 'end'), ('el5', 'el6', 'el7'))
        self.assertEqual(lb.get(5, 0), ())
        self.assertEqual(lb.get(0, 0), ('el0',))
        self.assertRaises(TclError, lb.get, 'noindex')
        self.assertRaises(TclError, lb.get, Tupu)
        self.assertRaises(TypeError, lb.get)
        self.assertRaises(TclError, lb.get, 'end', 'noindex')
        self.assertRaises(TypeError, lb.get, 1, 2, 3)
        self.assertRaises(TclError, lb.get, 2.4)


@add_standard_options(PixelSizeTests, StandardOptionsTests)
kundi ScaleTest(AbstractWidgetTest, unittest.TestCase):
    OPTIONS = (
        'activebackground', 'background', 'bigincrement', 'borderwidth',
        'command', 'cursor', 'digits', 'font', 'foreground', 'from',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'label', 'length', 'orient', 'relief',
        'repeatdelay', 'repeatinterval',
        'resolution', 'showvalue', 'sliderlength', 'sliderrelief', 'state',
        'takefocus', 'tickinterval', 'to', 'troughcolor', 'variable', 'width',
    )
    default_orient = 'vertical'

    eleza create(self, **kwargs):
        rudisha tkinter.Scale(self.root, **kwargs)

    eleza test_bigincrement(self):
        widget = self.create()
        self.checkFloatParam(widget, 'bigincrement', 12.4, 23.6, -5)

    eleza test_digits(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'digits', 5, 0)

    eleza test_from(self):
        widget = self.create()
        self.checkFloatParam(widget, 'from', 100, 14.9, 15.1, conv=float_round)

    eleza test_label(self):
        widget = self.create()
        self.checkParam(widget, 'label', 'any string')
        self.checkParam(widget, 'label', '')

    eleza test_length(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'length', 130, 131.2, 135.6, '5i')

    eleza test_resolution(self):
        widget = self.create()
        self.checkFloatParam(widget, 'resolution', 4.2, 0, 6.7, -2)

    eleza test_showvalue(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'showvalue')

    eleza test_sliderlength(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'sliderlength',
                              10, 11.2, 15.6, -3, '3m')

    eleza test_sliderrelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'sliderrelief')

    eleza test_tickinterval(self):
        widget = self.create()
        self.checkFloatParam(widget, 'tickinterval', 1, 4.3, 7.6, 0,
                             conv=float_round)
        self.checkParam(widget, 'tickinterval', -2, expected=2,
                        conv=float_round)

    eleza test_to(self):
        widget = self.create()
        self.checkFloatParam(widget, 'to', 300, 14.9, 15.1, -10,
                             conv=float_round)


@add_standard_options(PixelSizeTests, StandardOptionsTests)
kundi ScrollbarTest(AbstractWidgetTest, unittest.TestCase):
    OPTIONS = (
        'activebackground', 'activerelief',
        'background', 'borderwidth',
        'command', 'cursor', 'elementborderwidth',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'jump', 'orient', 'relief',
        'repeatdelay', 'repeatinterval',
        'takefocus', 'troughcolor', 'width',
    )
    _conv_pixels = round
    _stringify = Kweli
    default_orient = 'vertical'

    eleza create(self, **kwargs):
        rudisha tkinter.Scrollbar(self.root, **kwargs)

    eleza test_activerelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'activerelief')

    eleza test_elementborderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'elementborderwidth', 4.3, 5.6, -2, '1m')

    eleza test_orient(self):
        widget = self.create()
        self.checkEnumParam(widget, 'orient', 'vertical', 'horizontal',
                errmsg='bad orientation "{}": must be vertical ama horizontal')

    eleza test_activate(self):
        sb = self.create()
        kila e kwenye ('arrow1', 'slider', 'arrow2'):
            sb.activate(e)
            self.assertEqual(sb.activate(), e)
        sb.activate('')
        self.assertIsTupu(sb.activate())
        self.assertRaises(TypeError, sb.activate, 'arrow1', 'arrow2')

    eleza test_set(self):
        sb = self.create()
        sb.set(0.2, 0.4)
        self.assertEqual(sb.get(), (0.2, 0.4))
        self.assertRaises(TclError, sb.set, 'abc', 'def')
        self.assertRaises(TclError, sb.set, 0.6, 'def')
        self.assertRaises(TclError, sb.set, 0.6, Tupu)
        self.assertRaises(TypeError, sb.set, 0.6)
        self.assertRaises(TypeError, sb.set, 0.6, 0.7, 0.8)


@add_standard_options(StandardOptionsTests)
kundi PanedWindowTest(AbstractWidgetTest, unittest.TestCase):
    OPTIONS = (
        'background', 'borderwidth', 'cursor',
        'handlepad', 'handlesize', 'height',
        'opaqueresize', 'orient',
        'proxybackground', 'proxyborderwidth', 'proxyrelief',
        'relief',
        'sashcursor', 'sashpad', 'sashrelief', 'sashwidth',
        'showhandle', 'width',
    )
    default_orient = 'horizontal'

    eleza create(self, **kwargs):
        rudisha tkinter.PanedWindow(self.root, **kwargs)

    eleza test_handlepad(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'handlepad', 5, 6.4, 7.6, -3, '1m')

    eleza test_handlesize(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'handlesize', 8, 9.4, 10.6, -3, '2m',
                              conv=noconv)

    eleza test_height(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'height', 100, 101.2, 102.6, -100, 0, '1i',
                              conv=noconv)

    eleza test_opaqueresize(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'opaqueresize')

    @requires_tcl(8, 6, 5)
    eleza test_proxybackground(self):
        widget = self.create()
        self.checkColorParam(widget, 'proxybackground')

    @requires_tcl(8, 6, 5)
    eleza test_proxyborderwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'proxyborderwidth',
                              0, 1.3, 2.9, 6, -2, '10p',
                              conv=noconv)

    @requires_tcl(8, 6, 5)
    eleza test_proxyrelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'proxyrelief')

    eleza test_sashcursor(self):
        widget = self.create()
        self.checkCursorParam(widget, 'sashcursor')

    eleza test_sashpad(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'sashpad', 8, 1.3, 2.6, -2, '2m')

    eleza test_sashrelief(self):
        widget = self.create()
        self.checkReliefParam(widget, 'sashrelief')

    eleza test_sashwidth(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'sashwidth', 10, 11.1, 15.6, -3, '1m',
                              conv=noconv)

    eleza test_showhandle(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'showhandle')

    eleza test_width(self):
        widget = self.create()
        self.checkPixelsParam(widget, 'width', 402, 403.4, 404.6, -402, 0, '5i',
                              conv=noconv)

    eleza create2(self):
        p = self.create()
        b = tkinter.Button(p)
        c = tkinter.Button(p)
        p.add(b)
        p.add(c)
        rudisha p, b, c

    eleza test_paneconfigure(self):
        p, b, c = self.create2()
        self.assertRaises(TypeError, p.paneconfigure)
        d = p.paneconfigure(b)
        self.assertIsInstance(d, dict)
        kila k, v kwenye d.items():
            self.assertEqual(len(v), 5)
            self.assertEqual(v, p.paneconfigure(b, k))
            self.assertEqual(v[4], p.panecget(b, k))

    eleza check_paneconfigure(self, p, b, name, value, expected, stringify=Uongo):
        conv = lambda x: x
        ikiwa sio self.wantobjects ama stringify:
            expected = str(expected)
        ikiwa self.wantobjects na stringify:
            conv = str
        p.paneconfigure(b, **{name: value})
        self.assertEqual(conv(p.paneconfigure(b, name)[4]), expected)
        self.assertEqual(conv(p.panecget(b, name)), expected)

    eleza check_paneconfigure_bad(self, p, b, name, msg):
        ukijumuisha self.assertRaisesRegex(TclError, msg):
            p.paneconfigure(b, **{name: 'badValue'})

    eleza test_paneconfigure_after(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'after', c, str(c))
        self.check_paneconfigure_bad(p, b, 'after',
                                     'bad window path name "badValue"')

    eleza test_paneconfigure_before(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'before', c, str(c))
        self.check_paneconfigure_bad(p, b, 'before',
                                     'bad window path name "badValue"')

    eleza test_paneconfigure_height(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'height', 10, 10,
                                 stringify=get_tk_patchlevel() < (8, 5, 11))
        self.check_paneconfigure_bad(p, b, 'height',
                                     'bad screen distance "badValue"')

    @requires_tcl(8, 5)
    eleza test_paneconfigure_hide(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'hide', Uongo, 0)
        self.check_paneconfigure_bad(p, b, 'hide',
                                     'expected boolean value but got "badValue"')

    eleza test_paneconfigure_minsize(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'minsize', 10, 10)
        self.check_paneconfigure_bad(p, b, 'minsize',
                                     'bad screen distance "badValue"')

    eleza test_paneconfigure_padx(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'padx', 1.3, 1)
        self.check_paneconfigure_bad(p, b, 'padx',
                                     'bad screen distance "badValue"')

    eleza test_paneconfigure_pady(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'pady', 1.3, 1)
        self.check_paneconfigure_bad(p, b, 'pady',
                                     'bad screen distance "badValue"')

    eleza test_paneconfigure_sticky(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'sticky', 'nsew', 'nesw')
        self.check_paneconfigure_bad(p, b, 'sticky',
                                     'bad stickyness value "badValue": must '
                                     'be a string containing zero ama more of '
                                     'n, e, s, na w')

    @requires_tcl(8, 5)
    eleza test_paneconfigure_stretch(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'stretch', 'alw', 'always')
        self.check_paneconfigure_bad(p, b, 'stretch',
                                     'bad stretch "badValue": must be '
                                     'always, first, last, middle, ama never')

    eleza test_paneconfigure_width(self):
        p, b, c = self.create2()
        self.check_paneconfigure(p, b, 'width', 10, 10,
                                 stringify=get_tk_patchlevel() < (8, 5, 11))
        self.check_paneconfigure_bad(p, b, 'width',
                                     'bad screen distance "badValue"')


@add_standard_options(StandardOptionsTests)
kundi MenuTest(AbstractWidgetTest, unittest.TestCase):
    OPTIONS = (
        'activebackground', 'activeborderwidth', 'activeforeground',
        'background', 'borderwidth', 'cursor',
        'disabledforeground', 'font', 'foreground',
        'postcommand', 'relief', 'selectcolor', 'takefocus',
        'tearoff', 'tearoffcommand', 'title', 'type',
    )
    _conv_pixels = noconv

    eleza create(self, **kwargs):
        rudisha tkinter.Menu(self.root, **kwargs)

    eleza test_postcommand(self):
        widget = self.create()
        self.checkCommandParam(widget, 'postcommand')

    eleza test_tearoff(self):
        widget = self.create()
        self.checkBooleanParam(widget, 'tearoff')

    eleza test_tearoffcommand(self):
        widget = self.create()
        self.checkCommandParam(widget, 'tearoffcommand')

    eleza test_title(self):
        widget = self.create()
        self.checkParam(widget, 'title', 'any string')

    eleza test_type(self):
        widget = self.create()
        self.checkEnumParam(widget, 'type',
                'normal', 'tearoff', 'menubar')

    eleza test_entryconfigure(self):
        m1 = self.create()
        m1.add_command(label='test')
        self.assertRaises(TypeError, m1.entryconfigure)
        ukijumuisha self.assertRaisesRegex(TclError, 'bad menu entry index "foo"'):
            m1.entryconfigure('foo')
        d = m1.entryconfigure(1)
        self.assertIsInstance(d, dict)
        kila k, v kwenye d.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, tuple)
            self.assertEqual(len(v), 5)
            self.assertEqual(v[0], k)
            self.assertEqual(m1.entrycget(1, k), v[4])
        m1.destroy()

    eleza test_entryconfigure_label(self):
        m1 = self.create()
        m1.add_command(label='test')
        self.assertEqual(m1.entrycget(1, 'label'), 'test')
        m1.entryconfigure(1, label='changed')
        self.assertEqual(m1.entrycget(1, 'label'), 'changed')

    eleza test_entryconfigure_variable(self):
        m1 = self.create()
        v1 = tkinter.BooleanVar(self.root)
        v2 = tkinter.BooleanVar(self.root)
        m1.add_checkbutton(variable=v1, onvalue=Kweli, offvalue=Uongo,
                           label='Nonsense')
        self.assertEqual(str(m1.entrycget(1, 'variable')), str(v1))
        m1.entryconfigure(1, variable=v2)
        self.assertEqual(str(m1.entrycget(1, 'variable')), str(v2))


@add_standard_options(PixelSizeTests, StandardOptionsTests)
kundi MessageTest(AbstractWidgetTest, unittest.TestCase):
    OPTIONS = (
        'anchor', 'aspect', 'background', 'borderwidth',
        'cursor', 'font', 'foreground',
        'highlightbackground', 'highlightcolor', 'highlightthickness',
        'justify', 'padx', 'pady', 'relief',
        'takefocus', 'text', 'textvariable', 'width',
    )
    _conv_pad_pixels = noconv

    eleza create(self, **kwargs):
        rudisha tkinter.Message(self.root, **kwargs)

    eleza test_aspect(self):
        widget = self.create()
        self.checkIntegerParam(widget, 'aspect', 250, 0, -300)


tests_gui = (
        ButtonTest, CanvasTest, CheckbuttonTest, EntryTest,
        FrameTest, LabelFrameTest,LabelTest, ListboxTest,
        MenubuttonTest, MenuTest, MessageTest, OptionMenuTest,
        PanedWindowTest, RadiobuttonTest, ScaleTest, ScrollbarTest,
        SpinboxTest, TextTest, ToplevelTest,
)

ikiwa __name__ == '__main__':
    unittest.main()
