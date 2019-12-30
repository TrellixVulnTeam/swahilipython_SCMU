# tk common color chooser dialogue
#
# this module provides an interface to the native color dialogue
# available kwenye Tk 4.2 na newer.
#
# written by Fredrik Lundh, May 1997
#
# fixed initialcolor handling kwenye August 1998
#

#
# options (all have default values):
#
# - initialcolor: color to mark kama selected when dialog ni displayed
#   (given kama an RGB triplet ama a Tk color string)
#
# - parent: which window to place the dialog on top of
#
# - title: dialog title
#

kutoka tkinter.commondialog agiza Dialog


#
# color chooser class

kundi Chooser(Dialog):
    "Ask kila a color"

    command = "tk_chooseColor"

    eleza _fixoptions(self):
        jaribu:
            # make sure initialcolor ni a tk color string
            color = self.options["initialcolor"]
            ikiwa isinstance(color, tuple):
                # assume an RGB triplet
                self.options["initialcolor"] = "#%02x%02x%02x" % color
        tatizo KeyError:
            pita

    eleza _fixresult(self, widget, result):
        # result can be somethings: an empty tuple, an empty string ama
        # a Tcl_Obj, so this somewhat weird check handles that
        ikiwa sio result ama sio str(result):
            rudisha Tupu, Tupu # canceled

        # to simplify application code, the color chooser returns
        # an RGB tuple together ukijumuisha the Tk color string
        r, g, b = widget.winfo_rgb(result)
        rudisha (r/256, g/256, b/256), str(result)


#
# convenience stuff

eleza askcolor(color = Tupu, **options):
    "Ask kila a color"

    ikiwa color:
        options = options.copy()
        options["initialcolor"] = color

    rudisha Chooser(**options).show()


# --------------------------------------------------------------------
# test stuff

ikiwa __name__ == "__main__":
    andika("color", askcolor())
