"""
MultiCall - a kundi which inherits its methods kutoka a Tkinter widget (Text, for
example), but enables multiple calls of functions per virtual event - all
matching events will be called, not only the most specific one. This is done
by wrapping the event functions - event_add, event_delete and event_info.
MultiCall recognizes only a subset of legal event sequences. Sequences which
are not recognized are treated by the original Tk handling mechanism. A
more-specific event will be called before a less-specific event.

The recognized sequences are complete one-event sequences (no emacs-style
Ctrl-X Ctrl-C, no shortcuts like <3>), for all types of events.
Key/Button Press/Release events can have modifiers.
The recognized modifiers are Shift, Control, Option and Command for Mac, and
Control, Alt, Shift, Meta/M for other platforms.

For all events which were handled by MultiCall, a new member is added to the
event instance passed to the binded functions - mc_type. This is one of the
event type constants defined in this module (such as MC_KEYPRESS).
For Key/Button events (which are handled by MultiCall and may receive
modifiers), another member is added - mc_state. This member gives the state
of the recognized modifiers, as a combination of the modifier constants
also defined in this module (for example, MC_SHIFT).
Using these members is absolutely portable.

The order by which events are called is defined by these rules:
1. A more-specific event will be called before a less-specific event.
2. A recently-binded event will be called before a previously-binded event,
   unless this conflicts with the first rule.
Each function will be called at most once for each event.
"""
agiza re
agiza sys

agiza tkinter

# the event type constants, which define the meaning of mc_type
MC_KEYPRESS=0; MC_KEYRELEASE=1; MC_BUTTONPRESS=2; MC_BUTTONRELEASE=3;
MC_ACTIVATE=4; MC_CIRCULATE=5; MC_COLORMAP=6; MC_CONFIGURE=7;
MC_DEACTIVATE=8; MC_DESTROY=9; MC_ENTER=10; MC_EXPOSE=11; MC_FOCUSIN=12;
MC_FOCUSOUT=13; MC_GRAVITY=14; MC_LEAVE=15; MC_MAP=16; MC_MOTION=17;
MC_MOUSEWHEEL=18; MC_PROPERTY=19; MC_REPARENT=20; MC_UNMAP=21; MC_VISIBILITY=22;
# the modifier state constants, which define the meaning of mc_state
MC_SHIFT = 1<<0; MC_CONTROL = 1<<2; MC_ALT = 1<<3; MC_META = 1<<5
MC_OPTION = 1<<6; MC_COMMAND = 1<<7

# define the list of modifiers, to be used in complex event types.
ikiwa sys.platform == "darwin":
    _modifiers = (("Shift",), ("Control",), ("Option",), ("Command",))
    _modifier_masks = (MC_SHIFT, MC_CONTROL, MC_OPTION, MC_COMMAND)
else:
    _modifiers = (("Control",), ("Alt",), ("Shift",), ("Meta", "M"))
    _modifier_masks = (MC_CONTROL, MC_ALT, MC_SHIFT, MC_META)

# a dictionary to map a modifier name into its number
_modifier_names = dict([(name, number)
                         for number in range(len(_modifiers))
                         for name in _modifiers[number]])

# In 3.4, ikiwa no shell window is ever open, the underlying Tk widget is
# destroyed before .__del__ methods here are called.  The following
# is used to selectively ignore shutdown exceptions to avoid
# 'Exception ignored' messages.  See http://bugs.python.org/issue20167
APPLICATION_GONE = "application has been destroyed"

# A binder is a kundi which binds functions to one type of event. It has two
# methods: bind and unbind, which get a function and a parsed sequence, as
# returned by _parse_sequence(). There are two types of binders:
# _SimpleBinder handles event types with no modifiers and no detail.
# No Python functions are called when no events are binded.
# _ComplexBinder handles event types with modifiers and a detail.
# A Python function is called each time an event is generated.

kundi _SimpleBinder:
    eleza __init__(self, type, widget, widgetinst):
        self.type = type
        self.sequence = '<'+_types[type][0]+'>'
        self.widget = widget
        self.widgetinst = widgetinst
        self.bindedfuncs = []
        self.handlerid = None

    eleza bind(self, triplet, func):
        ikiwa not self.handlerid:
            eleza handler(event, l = self.bindedfuncs, mc_type = self.type):
                event.mc_type = mc_type
                wascalled = {}
                for i in range(len(l)-1, -1, -1):
                    func = l[i]
                    ikiwa func not in wascalled:
                        wascalled[func] = True
                        r = func(event)
                        ikiwa r:
                            rudisha r
            self.handlerid = self.widget.bind(self.widgetinst,
                                              self.sequence, handler)
        self.bindedfuncs.append(func)

    eleza unbind(self, triplet, func):
        self.bindedfuncs.remove(func)
        ikiwa not self.bindedfuncs:
            self.widget.unbind(self.widgetinst, self.sequence, self.handlerid)
            self.handlerid = None

    eleza __del__(self):
        ikiwa self.handlerid:
            try:
                self.widget.unbind(self.widgetinst, self.sequence,
                        self.handlerid)
            except tkinter.TclError as e:
                ikiwa not APPLICATION_GONE in e.args[0]:
                    raise

# An int in range(1 << len(_modifiers)) represents a combination of modifiers
# (ikiwa the least significant bit is on, _modifiers[0] is on, and so on).
# _state_subsets gives for each combination of modifiers, or *state*,
# a list of the states which are a subset of it. This list is ordered by the
# number of modifiers is the state - the most specific state comes first.
_states = range(1 << len(_modifiers))
_state_names = [''.join(m[0]+'-'
                        for i, m in enumerate(_modifiers)
                        ikiwa (1 << i) & s)
                for s in _states]

eleza expand_substates(states):
    '''For each item of states rudisha a list containing all combinations of
    that item with individual bits reset, sorted by the number of set bits.
    '''
    eleza nbits(n):
        "number of bits set in n base 2"
        nb = 0
        while n:
            n, rem = divmod(n, 2)
            nb += rem
        rudisha nb
    statelist = []
    for state in states:
        substates = list(set(state & x for x in states))
        substates.sort(key=nbits, reverse=True)
        statelist.append(substates)
    rudisha statelist

_state_subsets = expand_substates(_states)

# _state_codes gives for each state, the portable code to be passed as mc_state
_state_codes = []
for s in _states:
    r = 0
    for i in range(len(_modifiers)):
        ikiwa (1 << i) & s:
            r |= _modifier_masks[i]
    _state_codes.append(r)

kundi _ComplexBinder:
    # This kundi binds many functions, and only unbinds them when it is deleted.
    # self.handlerids is the list of seqs and ids of binded handler functions.
    # The binded functions sit in a dictionary of lists of lists, which maps
    # a detail (or None) and a state into a list of functions.
    # When a new detail is discovered, handlers for all the possible states
    # are binded.

    eleza __create_handler(self, lists, mc_type, mc_state):
        eleza handler(event, lists = lists,
                    mc_type = mc_type, mc_state = mc_state,
                    ishandlerrunning = self.ishandlerrunning,
                    doafterhandler = self.doafterhandler):
            ishandlerrunning[:] = [True]
            event.mc_type = mc_type
            event.mc_state = mc_state
            wascalled = {}
            r = None
            for l in lists:
                for i in range(len(l)-1, -1, -1):
                    func = l[i]
                    ikiwa func not in wascalled:
                        wascalled[func] = True
                        r = l[i](event)
                        ikiwa r:
                            break
                ikiwa r:
                    break
            ishandlerrunning[:] = []
            # Call all functions in doafterhandler and remove them kutoka list
            for f in doafterhandler:
                f()
            doafterhandler[:] = []
            ikiwa r:
                rudisha r
        rudisha handler

    eleza __init__(self, type, widget, widgetinst):
        self.type = type
        self.typename = _types[type][0]
        self.widget = widget
        self.widgetinst = widgetinst
        self.bindedfuncs = {None: [[] for s in _states]}
        self.handlerids = []
        # we don't want to change the lists of functions while a handler is
        # running - it will mess up the loop and anyway, we usually want the
        # change to happen kutoka the next event. So we have a list of functions
        # for the handler to run after it finishes calling the binded functions.
        # It calls them only once.
        # ishandlerrunning is a list. An empty one means no, otherwise - yes.
        # this is done so that it would be mutable.
        self.ishandlerrunning = []
        self.doafterhandler = []
        for s in _states:
            lists = [self.bindedfuncs[None][i] for i in _state_subsets[s]]
            handler = self.__create_handler(lists, type, _state_codes[s])
            seq = '<'+_state_names[s]+self.typename+'>'
            self.handlerids.append((seq, self.widget.bind(self.widgetinst,
                                                          seq, handler)))

    eleza bind(self, triplet, func):
        ikiwa triplet[2] not in self.bindedfuncs:
            self.bindedfuncs[triplet[2]] = [[] for s in _states]
            for s in _states:
                lists = [ self.bindedfuncs[detail][i]
                          for detail in (triplet[2], None)
                          for i in _state_subsets[s]       ]
                handler = self.__create_handler(lists, self.type,
                                                _state_codes[s])
                seq = "<%s%s-%s>"% (_state_names[s], self.typename, triplet[2])
                self.handlerids.append((seq, self.widget.bind(self.widgetinst,
                                                              seq, handler)))
        doit = lambda: self.bindedfuncs[triplet[2]][triplet[0]].append(func)
        ikiwa not self.ishandlerrunning:
            doit()
        else:
            self.doafterhandler.append(doit)

    eleza unbind(self, triplet, func):
        doit = lambda: self.bindedfuncs[triplet[2]][triplet[0]].remove(func)
        ikiwa not self.ishandlerrunning:
            doit()
        else:
            self.doafterhandler.append(doit)

    eleza __del__(self):
        for seq, id in self.handlerids:
            try:
                self.widget.unbind(self.widgetinst, seq, id)
            except tkinter.TclError as e:
                ikiwa not APPLICATION_GONE in e.args[0]:
                    raise

# define the list of event types to be handled by MultiEvent. the order is
# compatible with the definition of event type constants.
_types = (
    ("KeyPress", "Key"), ("KeyRelease",), ("ButtonPress", "Button"),
    ("ButtonRelease",), ("Activate",), ("Circulate",), ("Colormap",),
    ("Configure",), ("Deactivate",), ("Destroy",), ("Enter",), ("Expose",),
    ("FocusIn",), ("FocusOut",), ("Gravity",), ("Leave",), ("Map",),
    ("Motion",), ("MouseWheel",), ("Property",), ("Reparent",), ("Unmap",),
    ("Visibility",),
)

# which binder should be used for every event type?
_binder_classes = (_ComplexBinder,) * 4 + (_SimpleBinder,) * (len(_types)-4)

# A dictionary to map a type name into its number
_type_names = dict([(name, number)
                     for number in range(len(_types))
                     for name in _types[number]])

_keysym_re = re.compile(r"^\w+$")
_button_re = re.compile(r"^[1-5]$")
eleza _parse_sequence(sequence):
    """Get a string which should describe an event sequence. If it is
    successfully parsed as one, rudisha a tuple containing the state (as an int),
    the event type (as an index of _types), and the detail - None ikiwa none, or a
    string ikiwa there is one. If the parsing is unsuccessful, rudisha None.
    """
    ikiwa not sequence or sequence[0] != '<' or sequence[-1] != '>':
        rudisha None
    words = sequence[1:-1].split('-')
    modifiers = 0
    while words and words[0] in _modifier_names:
        modifiers |= 1 << _modifier_names[words[0]]
        del words[0]
    ikiwa words and words[0] in _type_names:
        type = _type_names[words[0]]
        del words[0]
    else:
        rudisha None
    ikiwa _binder_classes[type] is _SimpleBinder:
        ikiwa modifiers or words:
            rudisha None
        else:
            detail = None
    else:
        # _ComplexBinder
        ikiwa type in [_type_names[s] for s in ("KeyPress", "KeyRelease")]:
            type_re = _keysym_re
        else:
            type_re = _button_re

        ikiwa not words:
            detail = None
        elikiwa len(words) == 1 and type_re.match(words[0]):
            detail = words[0]
        else:
            rudisha None

    rudisha modifiers, type, detail

eleza _triplet_to_sequence(triplet):
    ikiwa triplet[2]:
        rudisha '<'+_state_names[triplet[0]]+_types[triplet[1]][0]+'-'+ \
               triplet[2]+'>'
    else:
        rudisha '<'+_state_names[triplet[0]]+_types[triplet[1]][0]+'>'

_multicall_dict = {}
eleza MultiCallCreator(widget):
    """Return a MultiCall kundi which inherits its methods kutoka the
    given widget kundi (for example, Tkinter.Text). This is used
    instead of a templating mechanism.
    """
    ikiwa widget in _multicall_dict:
        rudisha _multicall_dict[widget]

    kundi MultiCall (widget):
        assert issubclass(widget, tkinter.Misc)

        eleza __init__(self, *args, **kwargs):
            widget.__init__(self, *args, **kwargs)
            # a dictionary which maps a virtual event to a tuple with:
            #  0. the function binded
            #  1. a list of triplets - the sequences it is binded to
            self.__eventinfo = {}
            self.__binders = [_binder_classes[i](i, widget, self)
                              for i in range(len(_types))]

        eleza bind(self, sequence=None, func=None, add=None):
            #andika("bind(%s, %s, %s)" % (sequence, func, add),
            #      file=sys.__stderr__)
            ikiwa type(sequence) is str and len(sequence) > 2 and \
               sequence[:2] == "<<" and sequence[-2:] == ">>":
                ikiwa sequence in self.__eventinfo:
                    ei = self.__eventinfo[sequence]
                    ikiwa ei[0] is not None:
                        for triplet in ei[1]:
                            self.__binders[triplet[1]].unbind(triplet, ei[0])
                    ei[0] = func
                    ikiwa ei[0] is not None:
                        for triplet in ei[1]:
                            self.__binders[triplet[1]].bind(triplet, func)
                else:
                    self.__eventinfo[sequence] = [func, []]
            rudisha widget.bind(self, sequence, func, add)

        eleza unbind(self, sequence, funcid=None):
            ikiwa type(sequence) is str and len(sequence) > 2 and \
               sequence[:2] == "<<" and sequence[-2:] == ">>" and \
               sequence in self.__eventinfo:
                func, triplets = self.__eventinfo[sequence]
                ikiwa func is not None:
                    for triplet in triplets:
                        self.__binders[triplet[1]].unbind(triplet, func)
                    self.__eventinfo[sequence][0] = None
            rudisha widget.unbind(self, sequence, funcid)

        eleza event_add(self, virtual, *sequences):
            #andika("event_add(%s, %s)" % (repr(virtual), repr(sequences)),
            #      file=sys.__stderr__)
            ikiwa virtual not in self.__eventinfo:
                self.__eventinfo[virtual] = [None, []]

            func, triplets = self.__eventinfo[virtual]
            for seq in sequences:
                triplet = _parse_sequence(seq)
                ikiwa triplet is None:
                    #andika("Tkinter event_add(%s)" % seq, file=sys.__stderr__)
                    widget.event_add(self, virtual, seq)
                else:
                    ikiwa func is not None:
                        self.__binders[triplet[1]].bind(triplet, func)
                    triplets.append(triplet)

        eleza event_delete(self, virtual, *sequences):
            ikiwa virtual not in self.__eventinfo:
                return
            func, triplets = self.__eventinfo[virtual]
            for seq in sequences:
                triplet = _parse_sequence(seq)
                ikiwa triplet is None:
                    #andika("Tkinter event_delete: %s" % seq, file=sys.__stderr__)
                    widget.event_delete(self, virtual, seq)
                else:
                    ikiwa func is not None:
                        self.__binders[triplet[1]].unbind(triplet, func)
                    triplets.remove(triplet)

        eleza event_info(self, virtual=None):
            ikiwa virtual is None or virtual not in self.__eventinfo:
                rudisha widget.event_info(self, virtual)
            else:
                rudisha tuple(map(_triplet_to_sequence,
                                 self.__eventinfo[virtual][1])) + \
                       widget.event_info(self, virtual)

        eleza __del__(self):
            for virtual in self.__eventinfo:
                func, triplets = self.__eventinfo[virtual]
                ikiwa func:
                    for triplet in triplets:
                        try:
                            self.__binders[triplet[1]].unbind(triplet, func)
                        except tkinter.TclError as e:
                            ikiwa not APPLICATION_GONE in e.args[0]:
                                raise

    _multicall_dict[widget] = MultiCall
    rudisha MultiCall


eleza _multi_call(parent):  # htest #
    top = tkinter.Toplevel(parent)
    top.title("Test MultiCall")
    x, y = map(int, parent.geometry().split('+')[1:])
    top.geometry("+%d+%d" % (x, y + 175))
    text = MultiCallCreator(tkinter.Text)(top)
    text.pack()
    eleza bindseq(seq, n=[0]):
        eleza handler(event):
            andika(seq)
        text.bind("<<handler%d>>"%n[0], handler)
        text.event_add("<<handler%d>>"%n[0], seq)
        n[0] += 1
    bindseq("<Key>")
    bindseq("<Control-Key>")
    bindseq("<Alt-Key-a>")
    bindseq("<Control-Key-a>")
    bindseq("<Alt-Control-Key-a>")
    bindseq("<Key-b>")
    bindseq("<Control-Button-1>")
    bindseq("<Button-2>")
    bindseq("<Alt-Button-1>")
    bindseq("<FocusOut>")
    bindseq("<Enter>")
    bindseq("<Leave>")

ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_mainmenu', verbosity=2, exit=False)

    kutoka idlelib.idle_test.htest agiza run
    run(_multi_call)
