"""
MultiCall - a kundi which inherits its methods kutoka a Tkinter widget (Text, for
example), but enables multiple calls of functions per virtual event - all
matching events will be called, sio only the most specific one. This ni done
by wrapping the event functions - event_add, event_delete na event_info.
MultiCall recognizes only a subset of legal event sequences. Sequences which
are sio recognized are treated by the original Tk handling mechanism. A
more-specific event will be called before a less-specific event.

The recognized sequences are complete one-event sequences (no emacs-style
Ctrl-X Ctrl-C, no shortcuts like <3>), kila all types of events.
Key/Button Press/Release events can have modifiers.
The recognized modifiers are Shift, Control, Option na Command kila Mac, and
Control, Alt, Shift, Meta/M kila other platforms.

For all events which were handled by MultiCall, a new member ni added to the
event instance pitaed to the binded functions - mc_type. This ni one of the
event type constants defined kwenye this module (such kama MC_KEYPRESS).
For Key/Button events (which are handled by MultiCall na may receive
modifiers), another member ni added - mc_state. This member gives the state
of the recognized modifiers, kama a combination of the modifier constants
also defined kwenye this module (kila example, MC_SHIFT).
Using these members ni absolutely portable.

The order by which events are called ni defined by these rules:
1. A more-specific event will be called before a less-specific event.
2. A recently-binded event will be called before a previously-binded event,
   unless this conflicts ukijumuisha the first rule.
Each function will be called at most once kila each event.
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

# define the list of modifiers, to be used kwenye complex event types.
ikiwa sys.platform == "darwin":
    _modifiers = (("Shift",), ("Control",), ("Option",), ("Command",))
    _modifier_masks = (MC_SHIFT, MC_CONTROL, MC_OPTION, MC_COMMAND)
isipokua:
    _modifiers = (("Control",), ("Alt",), ("Shift",), ("Meta", "M"))
    _modifier_masks = (MC_CONTROL, MC_ALT, MC_SHIFT, MC_META)

# a dictionary to map a modifier name into its number
_modifier_names = dict([(name, number)
                         kila number kwenye range(len(_modifiers))
                         kila name kwenye _modifiers[number]])

# In 3.4, ikiwa no shell window ni ever open, the underlying Tk widget is
# destroyed before .__del__ methods here are called.  The following
# ni used to selectively ignore shutdown exceptions to avoid
# 'Exception ignored' messages.  See http://bugs.python.org/issue20167
APPLICATION_GONE = "application has been destroyed"

# A binder ni a kundi which binds functions to one type of event. It has two
# methods: bind na unbind, which get a function na a parsed sequence, as
# rudishaed by _parse_sequence(). There are two types of binders:
# _SimpleBinder handles event types ukijumuisha no modifiers na no detail.
# No Python functions are called when no events are binded.
# _ComplexBinder handles event types ukijumuisha modifiers na a detail.
# A Python function ni called each time an event ni generated.

kundi _SimpleBinder:
    eleza __init__(self, type, widget, widgetinst):
        self.type = type
        self.sequence = '<'+_types[type][0]+'>'
        self.widget = widget
        self.widgetinst = widgetinst
        self.bindedfuncs = []
        self.handlerid = Tupu

    eleza bind(self, triplet, func):
        ikiwa sio self.handlerid:
            eleza handler(event, l = self.bindedfuncs, mc_type = self.type):
                event.mc_type = mc_type
                wascalled = {}
                kila i kwenye range(len(l)-1, -1, -1):
                    func = l[i]
                    ikiwa func haiko kwenye wascalled:
                        wascalled[func] = Kweli
                        r = func(event)
                        ikiwa r:
                            rudisha r
            self.handlerid = self.widget.bind(self.widgetinst,
                                              self.sequence, handler)
        self.bindedfuncs.append(func)

    eleza unbind(self, triplet, func):
        self.bindedfuncs.remove(func)
        ikiwa sio self.bindedfuncs:
            self.widget.unbind(self.widgetinst, self.sequence, self.handlerid)
            self.handlerid = Tupu

    eleza __del__(self):
        ikiwa self.handlerid:
            jaribu:
                self.widget.unbind(self.widgetinst, self.sequence,
                        self.handlerid)
            tatizo tkinter.TclError kama e:
                ikiwa sio APPLICATION_GONE kwenye e.args[0]:
                    ashiria

# An int kwenye range(1 << len(_modifiers)) represents a combination of modifiers
# (ikiwa the least significant bit ni on, _modifiers[0] ni on, na so on).
# _state_subsets gives kila each combination of modifiers, ama *state*,
# a list of the states which are a subset of it. This list ni ordered by the
# number of modifiers ni the state - the most specific state comes first.
_states = range(1 << len(_modifiers))
_state_names = [''.join(m[0]+'-'
                        kila i, m kwenye enumerate(_modifiers)
                        ikiwa (1 << i) & s)
                kila s kwenye _states]

eleza expand_substates(states):
    '''For each item of states rudisha a list containing all combinations of
    that item ukijumuisha individual bits reset, sorted by the number of set bits.
    '''
    eleza nbits(n):
        "number of bits set kwenye n base 2"
        nb = 0
        wakati n:
            n, rem = divmod(n, 2)
            nb += rem
        rudisha nb
    statelist = []
    kila state kwenye states:
        substates = list(set(state & x kila x kwenye states))
        substates.sort(key=nbits, reverse=Kweli)
        statelist.append(substates)
    rudisha statelist

_state_subsets = expand_substates(_states)

# _state_codes gives kila each state, the portable code to be pitaed kama mc_state
_state_codes = []
kila s kwenye _states:
    r = 0
    kila i kwenye range(len(_modifiers)):
        ikiwa (1 << i) & s:
            r |= _modifier_masks[i]
    _state_codes.append(r)

kundi _ComplexBinder:
    # This kundi binds many functions, na only unbinds them when it ni deleted.
    # self.handlerids ni the list of seqs na ids of binded handler functions.
    # The binded functions sit kwenye a dictionary of lists of lists, which maps
    # a detail (or Tupu) na a state into a list of functions.
    # When a new detail ni discovered, handlers kila all the possible states
    # are binded.

    eleza __create_handler(self, lists, mc_type, mc_state):
        eleza handler(event, lists = lists,
                    mc_type = mc_type, mc_state = mc_state,
                    ishandlerrunning = self.ishandlerrunning,
                    doafterhandler = self.doafterhandler):
            ishandlerrunning[:] = [Kweli]
            event.mc_type = mc_type
            event.mc_state = mc_state
            wascalled = {}
            r = Tupu
            kila l kwenye lists:
                kila i kwenye range(len(l)-1, -1, -1):
                    func = l[i]
                    ikiwa func haiko kwenye wascalled:
                        wascalled[func] = Kweli
                        r = l[i](event)
                        ikiwa r:
                            koma
                ikiwa r:
                    koma
            ishandlerrunning[:] = []
            # Call all functions kwenye doafterhandler na remove them kutoka list
            kila f kwenye doafterhandler:
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
        self.bindedfuncs = {Tupu: [[] kila s kwenye _states]}
        self.handlerids = []
        # we don't want to change the lists of functions wakati a handler is
        # running - it will mess up the loop na anyway, we usually want the
        # change to happen kutoka the next event. So we have a list of functions
        # kila the handler to run after it finishes calling the binded functions.
        # It calls them only once.
        # ishandlerrunning ni a list. An empty one means no, otherwise - yes.
        # this ni done so that it would be mutable.
        self.ishandlerrunning = []
        self.doafterhandler = []
        kila s kwenye _states:
            lists = [self.bindedfuncs[Tupu][i] kila i kwenye _state_subsets[s]]
            handler = self.__create_handler(lists, type, _state_codes[s])
            seq = '<'+_state_names[s]+self.typename+'>'
            self.handlerids.append((seq, self.widget.bind(self.widgetinst,
                                                          seq, handler)))

    eleza bind(self, triplet, func):
        ikiwa triplet[2] haiko kwenye self.bindedfuncs:
            self.bindedfuncs[triplet[2]] = [[] kila s kwenye _states]
            kila s kwenye _states:
                lists = [ self.bindedfuncs[detail][i]
                          kila detail kwenye (triplet[2], Tupu)
                          kila i kwenye _state_subsets[s]       ]
                handler = self.__create_handler(lists, self.type,
                                                _state_codes[s])
                seq = "<%s%s-%s>"% (_state_names[s], self.typename, triplet[2])
                self.handlerids.append((seq, self.widget.bind(self.widgetinst,
                                                              seq, handler)))
        doit = lambda: self.bindedfuncs[triplet[2]][triplet[0]].append(func)
        ikiwa sio self.ishandlerrunning:
            doit()
        isipokua:
            self.doafterhandler.append(doit)

    eleza unbind(self, triplet, func):
        doit = lambda: self.bindedfuncs[triplet[2]][triplet[0]].remove(func)
        ikiwa sio self.ishandlerrunning:
            doit()
        isipokua:
            self.doafterhandler.append(doit)

    eleza __del__(self):
        kila seq, id kwenye self.handlerids:
            jaribu:
                self.widget.unbind(self.widgetinst, seq, id)
            tatizo tkinter.TclError kama e:
                ikiwa sio APPLICATION_GONE kwenye e.args[0]:
                    ashiria

# define the list of event types to be handled by MultiEvent. the order is
# compatible ukijumuisha the definition of event type constants.
_types = (
    ("KeyPress", "Key"), ("KeyRelease",), ("ButtonPress", "Button"),
    ("ButtonRelease",), ("Activate",), ("Circulate",), ("Colormap",),
    ("Configure",), ("Deactivate",), ("Destroy",), ("Enter",), ("Expose",),
    ("FocusIn",), ("FocusOut",), ("Gravity",), ("Leave",), ("Map",),
    ("Motion",), ("MouseWheel",), ("Property",), ("Reparent",), ("Unmap",),
    ("Visibility",),
)

# which binder should be used kila every event type?
_binder_classes = (_ComplexBinder,) * 4 + (_SimpleBinder,) * (len(_types)-4)

# A dictionary to map a type name into its number
_type_names = dict([(name, number)
                     kila number kwenye range(len(_types))
                     kila name kwenye _types[number]])

_keysym_re = re.compile(r"^\w+$")
_button_re = re.compile(r"^[1-5]$")
eleza _parse_sequence(sequence):
    """Get a string which should describe an event sequence. If it is
    successfully parsed kama one, rudisha a tuple containing the state (as an int),
    the event type (as an index of _types), na the detail - Tupu ikiwa none, ama a
    string ikiwa there ni one. If the parsing ni unsuccessful, rudisha Tupu.
    """
    ikiwa sio sequence ama sequence[0] != '<' ama sequence[-1] != '>':
        rudisha Tupu
    words = sequence[1:-1].split('-')
    modifiers = 0
    wakati words na words[0] kwenye _modifier_names:
        modifiers |= 1 << _modifier_names[words[0]]
        toa words[0]
    ikiwa words na words[0] kwenye _type_names:
        type = _type_names[words[0]]
        toa words[0]
    isipokua:
        rudisha Tupu
    ikiwa _binder_classes[type] ni _SimpleBinder:
        ikiwa modifiers ama words:
            rudisha Tupu
        isipokua:
            detail = Tupu
    isipokua:
        # _ComplexBinder
        ikiwa type kwenye [_type_names[s] kila s kwenye ("KeyPress", "KeyRelease")]:
            type_re = _keysym_re
        isipokua:
            type_re = _button_re

        ikiwa sio words:
            detail = Tupu
        lasivyo len(words) == 1 na type_re.match(words[0]):
            detail = words[0]
        isipokua:
            rudisha Tupu

    rudisha modifiers, type, detail

eleza _triplet_to_sequence(triplet):
    ikiwa triplet[2]:
        rudisha '<'+_state_names[triplet[0]]+_types[triplet[1]][0]+'-'+ \
               triplet[2]+'>'
    isipokua:
        rudisha '<'+_state_names[triplet[0]]+_types[triplet[1]][0]+'>'

_multicall_dict = {}
eleza MultiCallCreator(widget):
    """Return a MultiCall kundi which inherits its methods kutoka the
    given widget kundi (kila example, Tkinter.Text). This ni used
    instead of a templating mechanism.
    """
    ikiwa widget kwenye _multicall_dict:
        rudisha _multicall_dict[widget]

    kundi MultiCall (widget):
        assert issubclass(widget, tkinter.Misc)

        eleza __init__(self, *args, **kwargs):
            widget.__init__(self, *args, **kwargs)
            # a dictionary which maps a virtual event to a tuple with:
            #  0. the function binded
            #  1. a list of triplets - the sequences it ni binded to
            self.__eventinfo = {}
            self.__binders = [_binder_classes[i](i, widget, self)
                              kila i kwenye range(len(_types))]

        eleza bind(self, sequence=Tupu, func=Tupu, add=Tupu):
            #andika("bind(%s, %s, %s)" % (sequence, func, add),
            #      file=sys.__stderr__)
            ikiwa type(sequence) ni str na len(sequence) > 2 na \
               sequence[:2] == "<<" na sequence[-2:] == ">>":
                ikiwa sequence kwenye self.__eventinfo:
                    ei = self.__eventinfo[sequence]
                    ikiwa ei[0] ni sio Tupu:
                        kila triplet kwenye ei[1]:
                            self.__binders[triplet[1]].unbind(triplet, ei[0])
                    ei[0] = func
                    ikiwa ei[0] ni sio Tupu:
                        kila triplet kwenye ei[1]:
                            self.__binders[triplet[1]].bind(triplet, func)
                isipokua:
                    self.__eventinfo[sequence] = [func, []]
            rudisha widget.bind(self, sequence, func, add)

        eleza unbind(self, sequence, funcid=Tupu):
            ikiwa type(sequence) ni str na len(sequence) > 2 na \
               sequence[:2] == "<<" na sequence[-2:] == ">>" na \
               sequence kwenye self.__eventinfo:
                func, triplets = self.__eventinfo[sequence]
                ikiwa func ni sio Tupu:
                    kila triplet kwenye triplets:
                        self.__binders[triplet[1]].unbind(triplet, func)
                    self.__eventinfo[sequence][0] = Tupu
            rudisha widget.unbind(self, sequence, funcid)

        eleza event_add(self, virtual, *sequences):
            #andika("event_add(%s, %s)" % (repr(virtual), repr(sequences)),
            #      file=sys.__stderr__)
            ikiwa virtual haiko kwenye self.__eventinfo:
                self.__eventinfo[virtual] = [Tupu, []]

            func, triplets = self.__eventinfo[virtual]
            kila seq kwenye sequences:
                triplet = _parse_sequence(seq)
                ikiwa triplet ni Tupu:
                    #andika("Tkinter event_add(%s)" % seq, file=sys.__stderr__)
                    widget.event_add(self, virtual, seq)
                isipokua:
                    ikiwa func ni sio Tupu:
                        self.__binders[triplet[1]].bind(triplet, func)
                    triplets.append(triplet)

        eleza event_delete(self, virtual, *sequences):
            ikiwa virtual haiko kwenye self.__eventinfo:
                rudisha
            func, triplets = self.__eventinfo[virtual]
            kila seq kwenye sequences:
                triplet = _parse_sequence(seq)
                ikiwa triplet ni Tupu:
                    #andika("Tkinter event_delete: %s" % seq, file=sys.__stderr__)
                    widget.event_delete(self, virtual, seq)
                isipokua:
                    ikiwa func ni sio Tupu:
                        self.__binders[triplet[1]].unbind(triplet, func)
                    triplets.remove(triplet)

        eleza event_info(self, virtual=Tupu):
            ikiwa virtual ni Tupu ama virtual haiko kwenye self.__eventinfo:
                rudisha widget.event_info(self, virtual)
            isipokua:
                rudisha tuple(map(_triplet_to_sequence,
                                 self.__eventinfo[virtual][1])) + \
                       widget.event_info(self, virtual)

        eleza __del__(self):
            kila virtual kwenye self.__eventinfo:
                func, triplets = self.__eventinfo[virtual]
                ikiwa func:
                    kila triplet kwenye triplets:
                        jaribu:
                            self.__binders[triplet[1]].unbind(triplet, func)
                        tatizo tkinter.TclError kama e:
                            ikiwa sio APPLICATION_GONE kwenye e.args[0]:
                                ashiria

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
    main('idlelib.idle_test.test_mainmenu', verbosity=2, exit=Uongo)

    kutoka idlelib.idle_test.htest agiza run
    run(_multi_call)
