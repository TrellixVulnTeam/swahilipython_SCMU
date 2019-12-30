agiza collections
agiza tokenize  # kutoka stdlib

kutoka . agiza grammar, token


kundi ParserGenerator(object):

    eleza __init__(self, grammar_file, token_file, stream=Tupu, verbose=Uongo):
        close_stream = Tupu
        ikiwa stream ni Tupu:
            stream = open(grammar_file)
            close_stream = stream.close
        ukijumuisha open(token_file) kama tok_file:
            token_lines = tok_file.readlines()
        self.tokens = dict(token.generate_tokens(token_lines))
        self.opmap = dict(token.generate_opmap(token_lines))
        # Manually add <> so it does sio collide ukijumuisha !=
        self.opmap['<>'] = "NOTEQUAL"
        self.verbose = verbose
        self.filename = grammar_file
        self.stream = stream
        self.generator = tokenize.generate_tokens(stream.readline)
        self.gettoken() # Initialize lookahead
        self.dfas, self.startsymbol = self.parse()
        ikiwa close_stream ni sio Tupu:
            close_stream()
        self.first = {} # map kutoka symbol name to set of tokens
        self.addfirstsets()

    eleza make_grammar(self):
        c = grammar.Grammar()
        names = list(self.dfas.keys())
        names.remove(self.startsymbol)
        names.insert(0, self.startsymbol)
        kila name kwenye names:
            i = 256 + len(c.symbol2number)
            c.symbol2number[name] = i
            c.number2symbol[i] = name
        kila name kwenye names:
            self.make_label(c, name)
            dfa = self.dfas[name]
            states = []
            kila state kwenye dfa:
                arcs = []
                kila label, next kwenye sorted(state.arcs.items()):
                    arcs.append((self.make_label(c, label), dfa.index(next)))
                ikiwa state.isfinal:
                    arcs.append((0, dfa.index(state)))
                states.append(arcs)
            c.states.append(states)
            c.dfas[c.symbol2number[name]] = (states, self.make_first(c, name))
        c.start = c.symbol2number[self.startsymbol]

        ikiwa self.verbose:
            andika("")
            andika("Grammar summary")
            andika("===============")

            andika("- {n_labels} labels".format(n_labels=len(c.labels)))
            andika("- {n_dfas} dfas".format(n_dfas=len(c.dfas)))
            andika("- {n_tokens} tokens".format(n_tokens=len(c.tokens)))
            andika("- {n_keywords} keywords".format(n_keywords=len(c.keywords)))
            andika(
                "- Start symbol: {start_symbol}".format(
                    start_symbol=c.number2symbol[c.start]
                )
            )
        rudisha c

    eleza make_first(self, c, name):
        rawfirst = self.first[name]
        first = set()
        kila label kwenye sorted(rawfirst):
            ilabel = self.make_label(c, label)
            ##assert ilabel haiko kwenye first # XXX failed on <> ... !=
            first.add(ilabel)
        rudisha first

    eleza make_label(self, c, label):
        # XXX Maybe this should be a method on a subkundi of converter?
        ilabel = len(c.labels)
        ikiwa label[0].isalpha():
            # Either a symbol name ama a named token
            ikiwa label kwenye c.symbol2number:
                # A symbol name (a non-terminal)
                ikiwa label kwenye c.symbol2label:
                    rudisha c.symbol2label[label]
                isipokua:
                    c.labels.append((c.symbol2number[label], Tupu))
                    c.symbol2label[label] = ilabel
                    rudisha ilabel
            isipokua:
                # A named token (NAME, NUMBER, STRING)
                itoken = self.tokens.get(label, Tupu)
                assert isinstance(itoken, int), label
                assert itoken kwenye self.tokens.values(), label
                ikiwa itoken kwenye c.tokens:
                    rudisha c.tokens[itoken]
                isipokua:
                    c.labels.append((itoken, Tupu))
                    c.tokens[itoken] = ilabel
                    rudisha ilabel
        isipokua:
            # Either a keyword ama an operator
            assert label[0] kwenye ('"', "'"), label
            value = eval(label)
            ikiwa value[0].isalpha():
                # A keyword
                ikiwa value kwenye c.keywords:
                    rudisha c.keywords[value]
                isipokua:
                    c.labels.append((self.tokens["NAME"], value))
                    c.keywords[value] = ilabel
                    rudisha ilabel
            isipokua:
                # An operator (any non-numeric token)
                tok_name = self.opmap[value] # Fails ikiwa unknown token
                itoken = self.tokens[tok_name]
                ikiwa itoken kwenye c.tokens:
                    rudisha c.tokens[itoken]
                isipokua:
                    c.labels.append((itoken, Tupu))
                    c.tokens[itoken] = ilabel
                    rudisha ilabel

    eleza addfirstsets(self):
        names = list(self.dfas.keys())
        kila name kwenye names:
            ikiwa name haiko kwenye self.first:
                self.calcfirst(name)

            ikiwa self.verbose:
                andika("First set kila {dfa_name}".format(dfa_name=name))
                kila item kwenye self.first[name]:
                    andika("    - {terminal}".format(terminal=item))

    eleza calcfirst(self, name):
        dfa = self.dfas[name]
        self.first[name] = Tupu # dummy to detect left recursion
        state = dfa[0]
        totalset = set()
        overlapcheck = {}
        kila label, next kwenye state.arcs.items():
            ikiwa label kwenye self.dfas:
                ikiwa label kwenye self.first:
                    fset = self.first[label]
                    ikiwa fset ni Tupu:
                        ashiria ValueError("recursion kila rule %r" % name)
                isipokua:
                    self.calcfirst(label)
                    fset = self.first[label]
                totalset.update(fset)
                overlapcheck[label] = fset
            isipokua:
                totalset.add(label)
                overlapcheck[label] = {label}
        inverse = {}
        kila label, itsfirst kwenye overlapcheck.items():
            kila symbol kwenye itsfirst:
                ikiwa symbol kwenye inverse:
                    ashiria ValueError("rule %s ni ambiguous; %s ni kwenye the"
                                     " first sets of %s kama well kama %s" %
                                     (name, symbol, label, inverse[symbol]))
                inverse[symbol] = label
        self.first[name] = totalset

    eleza parse(self):
        dfas = collections.OrderedDict()
        startsymbol = Tupu
        # MSTART: (NEWLINE | RULE)* ENDMARKER
        wakati self.type != tokenize.ENDMARKER:
            wakati self.type == tokenize.NEWLINE:
                self.gettoken()
            # RULE: NAME ':' RHS NEWLINE
            name = self.expect(tokenize.NAME)
            ikiwa self.verbose:
                andika("Processing rule {dfa_name}".format(dfa_name=name))
            self.expect(tokenize.OP, ":")
            a, z = self.parse_rhs()
            self.expect(tokenize.NEWLINE)
            ikiwa self.verbose:
                self.dump_nfa(name, a, z)
            dfa = self.make_dfa(a, z)
            ikiwa self.verbose:
                self.dump_dfa(name, dfa)
            self.simplify_dfa(dfa)
            dfas[name] = dfa
            ikiwa startsymbol ni Tupu:
                startsymbol = name
        rudisha dfas, startsymbol

    eleza make_dfa(self, start, finish):
        # To turn an NFA into a DFA, we define the states of the DFA
        # to correspond to *sets* of states of the NFA.  Then do some
        # state reduction.  Let's represent sets kama dicts ukijumuisha 1 for
        # values.
        assert isinstance(start, NFAState)
        assert isinstance(finish, NFAState)
        eleza closure(state):
            base = set()
            addclosure(state, base)
            rudisha base
        eleza addclosure(state, base):
            assert isinstance(state, NFAState)
            ikiwa state kwenye base:
                rudisha
            base.add(state)
            kila label, next kwenye state.arcs:
                ikiwa label ni Tupu:
                    addclosure(next, base)
        states = [DFAState(closure(start), finish)]
        kila state kwenye states: # NB states grows wakati we're iterating
            arcs = {}
            kila nfastate kwenye state.nfaset:
                kila label, next kwenye nfastate.arcs:
                    ikiwa label ni sio Tupu:
                        addclosure(next, arcs.setdefault(label, set()))
            kila label, nfaset kwenye sorted(arcs.items()):
                kila st kwenye states:
                    ikiwa st.nfaset == nfaset:
                        koma
                isipokua:
                    st = DFAState(nfaset, finish)
                    states.append(st)
                state.addarc(st, label)
        rudisha states # List of DFAState instances; first one ni start

    eleza dump_nfa(self, name, start, finish):
        andika("Dump of NFA for", name)
        todo = [start]
        kila i, state kwenye enumerate(todo):
            andika("  State", i, state ni finish na "(final)" ama "")
            kila label, next kwenye state.arcs:
                ikiwa next kwenye todo:
                    j = todo.index(next)
                isipokua:
                    j = len(todo)
                    todo.append(next)
                ikiwa label ni Tupu:
                    andika("    -> %d" % j)
                isipokua:
                    andika("    %s -> %d" % (label, j))

    eleza dump_dfa(self, name, dfa):
        andika("Dump of DFA for", name)
        kila i, state kwenye enumerate(dfa):
            andika("  State", i, state.isfinal na "(final)" ama "")
            kila label, next kwenye sorted(state.arcs.items()):
                andika("    %s -> %d" % (label, dfa.index(next)))

    eleza simplify_dfa(self, dfa):
        # This ni sio theoretically optimal, but works well enough.
        # Algorithm: repeatedly look kila two states that have the same
        # set of arcs (same labels pointing to the same nodes) na
        # unify them, until things stop changing.

        # dfa ni a list of DFAState instances
        changes = Kweli
        wakati changes:
            changes = Uongo
            kila i, state_i kwenye enumerate(dfa):
                kila j kwenye range(i+1, len(dfa)):
                    state_j = dfa[j]
                    ikiwa state_i == state_j:
                        #print "  unify", i, j
                        toa dfa[j]
                        kila state kwenye dfa:
                            state.unifystate(state_j, state_i)
                        changes = Kweli
                        koma

    eleza parse_rhs(self):
        # RHS: ALT ('|' ALT)*
        a, z = self.parse_alt()
        ikiwa self.value != "|":
            rudisha a, z
        isipokua:
            aa = NFAState()
            zz = NFAState()
            aa.addarc(a)
            z.addarc(zz)
            wakati self.value == "|":
                self.gettoken()
                a, z = self.parse_alt()
                aa.addarc(a)
                z.addarc(zz)
            rudisha aa, zz

    eleza parse_alt(self):
        # ALT: ITEM+
        a, b = self.parse_item()
        wakati (self.value kwenye ("(", "[") ama
               self.type kwenye (tokenize.NAME, tokenize.STRING)):
            c, d = self.parse_item()
            b.addarc(c)
            b = d
        rudisha a, b

    eleza parse_item(self):
        # ITEM: '[' RHS ']' | ATOM ['+' | '*']
        ikiwa self.value == "[":
            self.gettoken()
            a, z = self.parse_rhs()
            self.expect(tokenize.OP, "]")
            a.addarc(z)
            rudisha a, z
        isipokua:
            a, z = self.parse_atom()
            value = self.value
            ikiwa value haiko kwenye ("+", "*"):
                rudisha a, z
            self.gettoken()
            z.addarc(a)
            ikiwa value == "+":
                rudisha a, z
            isipokua:
                rudisha a, a

    eleza parse_atom(self):
        # ATOM: '(' RHS ')' | NAME | STRING
        ikiwa self.value == "(":
            self.gettoken()
            a, z = self.parse_rhs()
            self.expect(tokenize.OP, ")")
            rudisha a, z
        lasivyo self.type kwenye (tokenize.NAME, tokenize.STRING):
            a = NFAState()
            z = NFAState()
            a.addarc(z, self.value)
            self.gettoken()
            rudisha a, z
        isipokua:
            self.raise_error("expected (...) ama NAME ama STRING, got %s/%s",
                             self.type, self.value)

    eleza expect(self, type, value=Tupu):
        ikiwa self.type != type ama (value ni sio Tupu na self.value != value):
            self.raise_error("expected %s/%s, got %s/%s",
                             type, value, self.type, self.value)
        value = self.value
        self.gettoken()
        rudisha value

    eleza gettoken(self):
        tup = next(self.generator)
        wakati tup[0] kwenye (tokenize.COMMENT, tokenize.NL):
            tup = next(self.generator)
        self.type, self.value, self.begin, self.end, self.line = tup
        # andika(getattr(tokenize, 'tok_name')[self.type], repr(self.value))

    eleza raise_error(self, msg, *args):
        ikiwa args:
            jaribu:
                msg = msg % args
            tatizo Exception:
                msg = " ".join([msg] + list(map(str, args)))
        ashiria SyntaxError(msg, (self.filename, self.end[0],
                                self.end[1], self.line))

kundi NFAState(object):

    eleza __init__(self):
        self.arcs = [] # list of (label, NFAState) pairs

    eleza addarc(self, next, label=Tupu):
        assert label ni Tupu ama isinstance(label, str)
        assert isinstance(next, NFAState)
        self.arcs.append((label, next))

kundi DFAState(object):

    eleza __init__(self, nfaset, final):
        assert isinstance(nfaset, set)
        assert isinstance(next(iter(nfaset)), NFAState)
        assert isinstance(final, NFAState)
        self.nfaset = nfaset
        self.isfinal = final kwenye nfaset
        self.arcs = {} # map kutoka label to DFAState

    eleza addarc(self, next, label):
        assert isinstance(label, str)
        assert label haiko kwenye self.arcs
        assert isinstance(next, DFAState)
        self.arcs[label] = next

    eleza unifystate(self, old, new):
        kila label, next kwenye self.arcs.items():
            ikiwa next ni old:
                self.arcs[label] = new

    eleza __eq__(self, other):
        # Equality test -- ignore the nfaset instance variable
        assert isinstance(other, DFAState)
        ikiwa self.isfinal != other.isfinal:
            rudisha Uongo
        # Can't just rudisha self.arcs == other.arcs, because that
        # would invoke this method recursively, ukijumuisha cycles...
        ikiwa len(self.arcs) != len(other.arcs):
            rudisha Uongo
        kila label, next kwenye self.arcs.items():
            ikiwa next ni sio other.arcs.get(label):
                rudisha Uongo
        rudisha Kweli

    __hash__ = Tupu # For Py3 compatibility.
