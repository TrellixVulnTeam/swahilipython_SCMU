"Zoom a window to maximum height."

agiza re
agiza sys
agiza tkinter


kundi WmInfoGatheringError(Exception):
    pita


kundi ZoomHeight:
    # Cached values kila maximized window dimensions, one kila each set
    # of screen dimensions.
    _max_height_and_y_coords = {}

    eleza __init__(self, editwin):
        self.editwin = editwin
        self.top = self.editwin.top

    eleza zoom_height_event(self, event=Tupu):
        zoomed = self.zoom_height()

        ikiwa zoomed ni Tupu:
            self.top.bell()
        isipokua:
            menu_status = 'Restore' ikiwa zoomed isipokua 'Zoom'
            self.editwin.update_menu_label(menu='options', index='* Height',
                                           label=f'{menu_status} Height')

        rudisha "koma"

    eleza zoom_height(self):
        top = self.top

        width, height, x, y = get_window_geometry(top)

        ikiwa top.wm_state() != 'normal':
            # Can't zoom/restore window height kila windows haiko kwenye the 'normal'
            # state, e.g. maximized na full-screen windows.
            rudisha Tupu

        jaribu:
            maxheight, maxy = self.get_max_height_and_y_coord()
        tatizo WmInfoGatheringError:
            rudisha Tupu

        ikiwa height != maxheight:
            # Maximize the window's height.
            set_window_geometry(top, (width, maxheight, x, maxy))
            rudisha Kweli
        isipokua:
            # Restore the window's height.
            #
            # .wm_geometry('') makes the window revert to the size requested
            # by the widgets it contains.
            top.wm_geometry('')
            rudisha Uongo

    eleza get_max_height_and_y_coord(self):
        top = self.top

        screen_dimensions = (top.winfo_screenwidth(),
                             top.winfo_screenheight())
        ikiwa screen_dimensions haiko kwenye self._max_height_and_y_coords:
            orig_state = top.wm_state()

            # Get window geometry info kila maximized windows.
            jaribu:
                top.wm_state('zoomed')
            tatizo tkinter.TclError:
                # The 'zoomed' state ni sio supported by some esoteric WMs,
                # such kama Xvfb.
                ashiria WmInfoGatheringError(
                    'Failed getting geometry of maximized windows, because ' +
                    'the "zoomed" window state ni unavailable.')
            top.update()
            maxwidth, maxheight, maxx, maxy = get_window_geometry(top)
            ikiwa sys.platform == 'win32':
                # On Windows, the rudishaed Y coordinate ni the one before
                # maximizing, so we use 0 which ni correct unless a user puts
                # their dock on the top of the screen (very rare).
                maxy = 0
            maxrooty = top.winfo_rooty()

            # Get the "root y" coordinate kila non-maximized windows ukijumuisha their
            # y coordinate set to that of maximized windows.  This ni needed
            # to properly handle different title bar heights kila non-maximized
            # vs. maximized windows, kama seen e.g. kwenye Windows 10.
            top.wm_state('normal')
            top.update()
            orig_geom = get_window_geometry(top)
            max_y_geom = orig_geom[:3] + (maxy,)
            set_window_geometry(top, max_y_geom)
            top.update()
            max_y_geom_rooty = top.winfo_rooty()

            # Adjust the maximum window height to account kila the different
            # title bar heights of non-maximized vs. maximized windows.
            maxheight += maxrooty - max_y_geom_rooty

            self._max_height_and_y_coords[screen_dimensions] = maxheight, maxy

            set_window_geometry(top, orig_geom)
            top.wm_state(orig_state)

        rudisha self._max_height_and_y_coords[screen_dimensions]


eleza get_window_geometry(top):
    geom = top.wm_geometry()
    m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geom)
    rudisha tuple(map(int, m.groups()))


eleza set_window_geometry(top, geometry):
    top.wm_geometry("{:d}x{:d}+{:d}+{:d}".format(*geometry))


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_zoomheight', verbosity=2, exit=Uongo)

    # Add htest?
