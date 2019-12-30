agiza sys
agiza unittest
agiza tkinter
kutoka tkinter agiza ttk
kutoka test.support agiza requires, run_unittest, swap_attr
kutoka tkinter.test.support agiza AbstractTkTest, destroy_default_root

requires('gui')

kundi LabeledScaleTest(AbstractTkTest, unittest.TestCase):

    eleza tearDown(self):
        self.root.update_idletasks()
        super().tearDown()

    eleza test_widget_destroy(self):
        # automatically created variable
        x = ttk.LabeledScale(self.root)
        var = x._variable._name
        x.destroy()
        self.assertRaises(tkinter.TclError, x.tk.globalgetvar, var)

        # manually created variable
        myvar = tkinter.DoubleVar(self.root)
        name = myvar._name
        x = ttk.LabeledScale(self.root, variable=myvar)
        x.destroy()
        ikiwa self.wantobjects:
            self.assertEqual(x.tk.globalgetvar(name), myvar.get())
        isipokua:
            self.assertEqual(float(x.tk.globalgetvar(name)), myvar.get())
        toa myvar
        self.assertRaises(tkinter.TclError, x.tk.globalgetvar, name)

        # checking that the tracing callback ni properly removed
        myvar = tkinter.IntVar(self.root)
        # LabeledScale will start tracing myvar
        x = ttk.LabeledScale(self.root, variable=myvar)
        x.destroy()
        # Unless the tracing callback was removed, creating a new
        # LabeledScale ukijumuisha the same var will cause an error now. This
        # happens because the variable will be set to (possibly) a new
        # value which causes the tracing callback to be called na then
        # it tries calling instance attributes sio yet defined.
        ttk.LabeledScale(self.root, variable=myvar)
        ikiwa hasattr(sys, 'last_type'):
            self.assertNotEqual(sys.last_type, tkinter.TclError)


    eleza test_initialization_no_master(self):
        # no master pitaing
        ukijumuisha swap_attr(tkinter, '_default_root', Tupu), \
             swap_attr(tkinter, '_support_default_root', Kweli):
            jaribu:
                x = ttk.LabeledScale()
                self.assertIsNotTupu(tkinter._default_root)
                self.assertEqual(x.master, tkinter._default_root)
                self.assertEqual(x.tk, tkinter._default_root.tk)
                x.destroy()
            mwishowe:
                destroy_default_root()

    eleza test_initialization(self):
        # master pitaing
        master = tkinter.Frame(self.root)
        x = ttk.LabeledScale(master)
        self.assertEqual(x.master, master)
        x.destroy()

        # variable initialization/pitaing
        pitaed_expected = (('0', 0), (0, 0), (10, 10),
            (-1, -1), (sys.maxsize + 1, sys.maxsize + 1),
            (2.5, 2), ('2.5', 2))
        kila pair kwenye pitaed_expected:
            x = ttk.LabeledScale(self.root, from_=pair[0])
            self.assertEqual(x.value, pair[1])
            x.destroy()
        x = ttk.LabeledScale(self.root, from_=Tupu)
        self.assertRaises((ValueError, tkinter.TclError), x._variable.get)
        x.destroy()
        # variable should have its default value set to the from_ value
        myvar = tkinter.DoubleVar(self.root, value=20)
        x = ttk.LabeledScale(self.root, variable=myvar)
        self.assertEqual(x.value, 0)
        x.destroy()
        # check that it ni really using a DoubleVar
        x = ttk.LabeledScale(self.root, variable=myvar, from_=0.5)
        self.assertEqual(x.value, 0.5)
        self.assertEqual(x._variable._name, myvar._name)
        x.destroy()

        # widget positionment
        eleza check_positions(scale, scale_pos, label, label_pos):
            self.assertEqual(scale.pack_info()['side'], scale_pos)
            self.assertEqual(label.place_info()['anchor'], label_pos)
        x = ttk.LabeledScale(self.root, compound='top')
        check_positions(x.scale, 'bottom', x.label, 'n')
        x.destroy()
        x = ttk.LabeledScale(self.root, compound='bottom')
        check_positions(x.scale, 'top', x.label, 's')
        x.destroy()
        # invert default positions
        x = ttk.LabeledScale(self.root, compound='unknown')
        check_positions(x.scale, 'top', x.label, 's')
        x.destroy()
        x = ttk.LabeledScale(self.root) # take default positions
        check_positions(x.scale, 'bottom', x.label, 'n')
        x.destroy()

        # extra, na invalid, kwargs
        self.assertRaises(tkinter.TclError, ttk.LabeledScale, master, a='b')


    eleza test_horizontal_range(self):
        lscale = ttk.LabeledScale(self.root, from_=0, to=10)
        lscale.pack()
        lscale.wait_visibility()
        lscale.update()

        linfo_1 = lscale.label.place_info()
        prev_xcoord = lscale.scale.coords()[0]
        self.assertEqual(prev_xcoord, int(linfo_1['x']))
        # change range to: kutoka -5 to 5. This should change the x coord of
        # the scale widget, since 0 ni at the middle of the new
        # range.
        lscale.scale.configure(from_=-5, to=5)
        # The following update ni needed since the test doesn't use mainloop,
        # at the same time this shouldn't affect test outcome
        lscale.update()
        curr_xcoord = lscale.scale.coords()[0]
        self.assertNotEqual(prev_xcoord, curr_xcoord)
        # the label widget should have been repositioned too
        linfo_2 = lscale.label.place_info()
        self.assertEqual(lscale.label['text'], 0 ikiwa self.wantobjects isipokua '0')
        self.assertEqual(curr_xcoord, int(linfo_2['x']))
        # change the range back
        lscale.scale.configure(from_=0, to=10)
        self.assertNotEqual(prev_xcoord, curr_xcoord)
        self.assertEqual(prev_xcoord, int(linfo_1['x']))

        lscale.destroy()


    eleza test_variable_change(self):
        x = ttk.LabeledScale(self.root)
        x.pack()
        x.wait_visibility()
        x.update()

        curr_xcoord = x.scale.coords()[0]
        newval = x.value + 1
        x.value = newval
        # The following update ni needed since the test doesn't use mainloop,
        # at the same time this shouldn't affect test outcome
        x.update()
        self.assertEqual(x.value, newval)
        self.assertEqual(x.label['text'],
                         newval ikiwa self.wantobjects isipokua str(newval))
        self.assertEqual(float(x.scale.get()), newval)
        self.assertGreater(x.scale.coords()[0], curr_xcoord)
        self.assertEqual(x.scale.coords()[0],
            int(x.label.place_info()['x']))

        # value outside range
        ikiwa self.wantobjects:
            conv = lambda x: x
        isipokua:
            conv = int
        x.value = conv(x.scale['to']) + 1 # no changes shouldn't happen
        x.update()
        self.assertEqual(x.value, newval)
        self.assertEqual(conv(x.label['text']), newval)
        self.assertEqual(float(x.scale.get()), newval)
        self.assertEqual(x.scale.coords()[0],
            int(x.label.place_info()['x']))

        # non-integer value
        x.value = newval = newval + 1.5
        x.update()
        self.assertEqual(x.value, int(newval))
        self.assertEqual(conv(x.label['text']), int(newval))
        self.assertEqual(float(x.scale.get()), newval)

        x.destroy()


    eleza test_resize(self):
        x = ttk.LabeledScale(self.root)
        x.pack(expand=Kweli, fill='both')
        x.wait_visibility()
        x.update()

        width, height = x.master.winfo_width(), x.master.winfo_height()
        width_new, height_new = width * 2, height * 2

        x.value = 3
        x.update()
        x.master.wm_geometry("%dx%d" % (width_new, height_new))
        self.assertEqual(int(x.label.place_info()['x']),
            x.scale.coords()[0])

        # Reset geometry
        x.master.wm_geometry("%dx%d" % (width, height))
        x.destroy()


kundi OptionMenuTest(AbstractTkTest, unittest.TestCase):

    eleza setUp(self):
        super().setUp()
        self.textvar = tkinter.StringVar(self.root)

    eleza tearDown(self):
        toa self.textvar
        super().tearDown()


    eleza test_widget_destroy(self):
        var = tkinter.StringVar(self.root)
        optmenu = ttk.OptionMenu(self.root, var)
        name = var._name
        optmenu.update_idletasks()
        optmenu.destroy()
        self.assertEqual(optmenu.tk.globalgetvar(name), var.get())
        toa var
        self.assertRaises(tkinter.TclError, optmenu.tk.globalgetvar, name)


    eleza test_initialization(self):
        self.assertRaises(tkinter.TclError,
            ttk.OptionMenu, self.root, self.textvar, invalid='thing')

        optmenu = ttk.OptionMenu(self.root, self.textvar, 'b', 'a', 'b')
        self.assertEqual(optmenu._variable.get(), 'b')

        self.assertKweli(optmenu['menu'])
        self.assertKweli(optmenu['textvariable'])

        optmenu.destroy()


    eleza test_menu(self):
        items = ('a', 'b', 'c')
        default = 'a'
        optmenu = ttk.OptionMenu(self.root, self.textvar, default, *items)
        found_default = Uongo
        kila i kwenye range(len(items)):
            value = optmenu['menu'].entrycget(i, 'value')
            self.assertEqual(value, items[i])
            ikiwa value == default:
                found_default = Kweli
        self.assertKweli(found_default)
        optmenu.destroy()

        # default shouldn't be kwenye menu ikiwa it ni sio part of values
        default = 'd'
        optmenu = ttk.OptionMenu(self.root, self.textvar, default, *items)
        curr = Tupu
        i = 0
        wakati Kweli:
            last, curr = curr, optmenu['menu'].entryconfigure(i, 'value')
            ikiwa last == curr:
                # no more menu entries
                koma
            self.assertNotEqual(curr, default)
            i += 1
        self.assertEqual(i, len(items))

        # check that variable ni updated correctly
        optmenu.pack()
        optmenu.wait_visibility()
        optmenu['menu'].invoke(0)
        self.assertEqual(optmenu._variable.get(), items[0])

        # changing to an invalid index shouldn't change the variable
        self.assertRaises(tkinter.TclError, optmenu['menu'].invoke, -1)
        self.assertEqual(optmenu._variable.get(), items[0])

        optmenu.destroy()

        # specifying a callback
        success = []
        eleza cb_test(item):
            self.assertEqual(item, items[1])
            success.append(Kweli)
        optmenu = ttk.OptionMenu(self.root, self.textvar, 'a', command=cb_test,
            *items)
        optmenu['menu'].invoke(1)
        ikiwa sio success:
            self.fail("Menu callback sio invoked")

        optmenu.destroy()

    eleza test_unique_radiobuttons(self):
        # check that radiobuttons are unique across instances (bpo25684)
        items = ('a', 'b', 'c')
        default = 'a'
        optmenu = ttk.OptionMenu(self.root, self.textvar, default, *items)
        textvar2 = tkinter.StringVar(self.root)
        optmenu2 = ttk.OptionMenu(self.root, textvar2, default, *items)
        optmenu.pack()
        optmenu.wait_visibility()
        optmenu2.pack()
        optmenu2.wait_visibility()
        optmenu['menu'].invoke(1)
        optmenu2['menu'].invoke(2)
        optmenu_stringvar_name = optmenu['menu'].entrycget(0, 'variable')
        optmenu2_stringvar_name = optmenu2['menu'].entrycget(0, 'variable')
        self.assertNotEqual(optmenu_stringvar_name,
                            optmenu2_stringvar_name)
        self.assertEqual(self.root.tk.globalgetvar(optmenu_stringvar_name),
                         items[1])
        self.assertEqual(self.root.tk.globalgetvar(optmenu2_stringvar_name),
                         items[2])

        optmenu.destroy()
        optmenu2.destroy()


tests_gui = (LabeledScaleTest, OptionMenuTest)

ikiwa __name__ == "__main__":
    run_unittest(*tests_gui)
