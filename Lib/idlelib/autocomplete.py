"""Complete either attribute names or file names.

Either on demand or after a user-selected delay after a key character,
pop up a list of candidates.
"""
agiza __main__
agiza os
agiza string
agiza sys

# Two types of completions; defined here for autocomplete_w agiza below.
ATTRS, FILES = 0, 1
kutoka idlelib agiza autocomplete_w
kutoka idlelib.config agiza idleConf
kutoka idlelib.hyperparser agiza HyperParser

# Tuples passed to open_completions.
#       EvalFunc, Complete, WantWin, Mode
FORCE = True,     False,    True,    None   # Control-Space.
TAB   = False,    True,     True,    None   # Tab.
TRY_A = False,    False,    False,   ATTRS  # '.' for attributes.
TRY_F = False,    False,    False,   FILES  # '/' in quotes for file name.

# This string includes all chars that may be in an identifier.
# TODO Update this here and elsewhere.
ID_CHARS = string.ascii_letters + string.digits + "_"

SEPS = f"{os.sep}{os.altsep ikiwa os.altsep else ''}"
TRIGGERS = f".{SEPS}"

kundi AutoComplete:

    eleza __init__(self, editwin=None):
        self.editwin = editwin
        ikiwa editwin is not None:   # not in subprocess or no-gui test
            self.text = editwin.text
        self.autocompletewindow = None
        # id of delayed call, and the index of the text insert when
        # the delayed call was issued. If _delayed_completion_id is
        # None, there is no delayed call.
        self._delayed_completion_id = None
        self._delayed_completion_index = None

    @classmethod
    eleza reload(cls):
        cls.popupwait = idleConf.GetOption(
            "extensions", "AutoComplete", "popupwait", type="int", default=0)

    eleza _make_autocomplete_window(self):  # Makes mocking easier.
        rudisha autocomplete_w.AutoCompleteWindow(self.text)

    eleza _remove_autocomplete_window(self, event=None):
        ikiwa self.autocompletewindow:
            self.autocompletewindow.hide_window()
            self.autocompletewindow = None

    eleza force_open_completions_event(self, event):
        "(^space) Open completion list, even ikiwa a function call is needed."
        self.open_completions(FORCE)
        rudisha "break"

    eleza autocomplete_event(self, event):
        "(tab) Complete word or open list ikiwa multiple options."
        ikiwa hasattr(event, "mc_state") and event.mc_state or\
                not self.text.get("insert linestart", "insert").strip():
            # A modifier was pressed along with the tab or
            # there is only previous whitespace on this line, so tab.
            rudisha None
        ikiwa self.autocompletewindow and self.autocompletewindow.is_active():
            self.autocompletewindow.complete()
            rudisha "break"
        else:
            opened = self.open_completions(TAB)
            rudisha "break" ikiwa opened else None

    eleza try_open_completions_event(self, event=None):
        "(./) Open completion list after pause with no movement."
        lastchar = self.text.get("insert-1c")
        ikiwa lastchar in TRIGGERS:
            args = TRY_A ikiwa lastchar == "." else TRY_F
            self._delayed_completion_index = self.text.index("insert")
            ikiwa self._delayed_completion_id is not None:
                self.text.after_cancel(self._delayed_completion_id)
            self._delayed_completion_id = self.text.after(
                self.popupwait, self._delayed_open_completions, args)

    eleza _delayed_open_completions(self, args):
        "Call open_completions ikiwa index unchanged."
        self._delayed_completion_id = None
        ikiwa self.text.index("insert") == self._delayed_completion_index:
            self.open_completions(args)

    eleza open_completions(self, args):
        """Find the completions and create the AutoCompleteWindow.
        Return True ikiwa successful (no syntax error or so found).
        If complete is True, then ikiwa there's nothing to complete and no
        start of completion, won't open completions and rudisha False.
        If mode is given, will open a completion list only in this mode.
        """
        evalfuncs, complete, wantwin, mode = args
        # Cancel another delayed call, ikiwa it exists.
        ikiwa self._delayed_completion_id is not None:
            self.text.after_cancel(self._delayed_completion_id)
            self._delayed_completion_id = None

        hp = HyperParser(self.editwin, "insert")
        curline = self.text.get("insert linestart", "insert")
        i = j = len(curline)
        ikiwa hp.is_in_string() and (not mode or mode==FILES):
            # Find the beginning of the string.
            # fetch_completions will look at the file system to determine
            # whether the string value constitutes an actual file name
            # XXX could consider raw strings here and unescape the string
            # value ikiwa it's not raw.
            self._remove_autocomplete_window()
            mode = FILES
            # Find last separator or string start
            while i and curline[i-1] not in "'\"" + SEPS:
                i -= 1
            comp_start = curline[i:j]
            j = i
            # Find string start
            while i and curline[i-1] not in "'\"":
                i -= 1
            comp_what = curline[i:j]
        elikiwa hp.is_in_code() and (not mode or mode==ATTRS):
            self._remove_autocomplete_window()
            mode = ATTRS
            while i and (curline[i-1] in ID_CHARS or ord(curline[i-1]) > 127):
                i -= 1
            comp_start = curline[i:j]
            ikiwa i and curline[i-1] == '.':  # Need object with attributes.
                hp.set_index("insert-%dc" % (len(curline)-(i-1)))
                comp_what = hp.get_expression()
                ikiwa (not comp_what or
                   (not evalfuncs and comp_what.find('(') != -1)):
                    rudisha None
            else:
                comp_what = ""
        else:
            rudisha None

        ikiwa complete and not comp_what and not comp_start:
            rudisha None
        comp_lists = self.fetch_completions(comp_what, mode)
        ikiwa not comp_lists[0]:
            rudisha None
        self.autocompletewindow = self._make_autocomplete_window()
        rudisha not self.autocompletewindow.show_window(
                comp_lists, "insert-%dc" % len(comp_start),
                complete, mode, wantwin)

    eleza fetch_completions(self, what, mode):
        """Return a pair of lists of completions for something. The first list
        is a sublist of the second. Both are sorted.

        If there is a Python subprocess, get the comp. list there.  Otherwise,
        either fetch_completions() is running in the subprocess itself or it
        was called in an IDLE EditorWindow before any script had been run.

        The subprocess environment is that of the most recently run script.  If
        two unrelated modules are being edited some calltips in the current
        module may be inoperative ikiwa the module was not the last to run.
        """
        try:
            rpcclt = self.editwin.flist.pyshell.interp.rpcclt
        except:
            rpcclt = None
        ikiwa rpcclt:
            rudisha rpcclt.remotecall("exec", "get_the_completion_list",
                                     (what, mode), {})
        else:
            ikiwa mode == ATTRS:
                ikiwa what == "":
                    namespace = {**__main__.__builtins__.__dict__,
                                 **__main__.__dict__}
                    bigl = eval("dir()", namespace)
                    bigl.sort()
                    ikiwa "__all__" in bigl:
                        smalll = sorted(eval("__all__", namespace))
                    else:
                        smalll = [s for s in bigl ikiwa s[:1] != '_']
                else:
                    try:
                        entity = self.get_entity(what)
                        bigl = dir(entity)
                        bigl.sort()
                        ikiwa "__all__" in bigl:
                            smalll = sorted(entity.__all__)
                        else:
                            smalll = [s for s in bigl ikiwa s[:1] != '_']
                    except:
                        rudisha [], []

            elikiwa mode == FILES:
                ikiwa what == "":
                    what = "."
                try:
                    expandedpath = os.path.expanduser(what)
                    bigl = os.listdir(expandedpath)
                    bigl.sort()
                    smalll = [s for s in bigl ikiwa s[:1] != '.']
                except OSError:
                    rudisha [], []

            ikiwa not smalll:
                smalll = bigl
            rudisha smalll, bigl

    eleza get_entity(self, name):
        "Lookup name in a namespace spanning sys.modules and __main.dict__."
        rudisha eval(name, {**sys.modules, **__main__.__dict__})


AutoComplete.reload()

ikiwa __name__ == '__main__':
    kutoka unittest agiza main
    main('idlelib.idle_test.test_autocomplete', verbosity=2)
