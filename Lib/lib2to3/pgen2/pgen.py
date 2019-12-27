# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

# Pgen agizas
kutoka . agiza grammar, token, tokenize

kundi PgenGrammar(grammar.Grammar):
    pass

kundi ParserGenerator(object):

    eleza __init__(self, filename, stream=None):
        close_stream = None
        ikiwa stream is None:
            stream = open(filename)
            close_stream = stream.close
        self.filename = filename
        self.stream = stream
        self.generator = tokenize.generate_tokens(stream.readline)
        self.gettoken() # Initialize lookahead
        self.dfas, self.startsymbol = self.parse()
        ikiwa close_stream is not None:
            close_stream()
        self.first = {} # map kutoka symbol name to set of tokens
        self.addfirstsets()

    eleza make_grammar(self):
        c = PgenGrammar()
        names = list(self.dfas.keys())
        names.sort()
        names.remove(self.startsymbol)
        names.insert(0, self.startsymbol)
        for name in names:
            i = 256 + len(c.symbol2number)
            c.symbol2number[name] = i
            c.number2symbol[i] = name
        for name in names:
            dfa = self.dfas[name]
            states = []
            for state in dfa:
                arcs = []
                for label, next in sorted(state.arcs.items()):
                    arcs.append((self.make_label(c, label), dfa.index(next)))
                ikiwa state.isfinal:
                    arcs.append((0, dfa.index(state)))
                states.append(arcs)
            c.states.append(states)
            c.dfas[c.symbol2number[name]] = (states, self.make_first(c, name))
        c.start = c.symbol2number[self.startsymbol]
        rudisha c

    eleza make_first(self, c, name):
        rawfirst = self.first[name]
        first = {}
        for label in sorted(rawfirst):
            ilabel = self.make_label(c, label)
            ##assert ilabel not in first # XXX failed on <> ... !=
            first[ilabel] = 1
        rudisha first

    eleza make_label(self, c, label):
        # XXX Maybe this should be a method on a subkundi of converter?
        ilabel = len(c.labels)
        ikiwa label[0].isalpha():
            # Either a symbol name or a named token
            ikiwa label in c.symbol2number:
                # A symbol name (a non-terminal)
                ikiwa label in c.symbol2label:
                    rudisha c.symbol2label[label]
                else:
                    c.labels.append((c.symbol2number[label], None))
                    c.symbol2label[label] = ilabel
                    rudisha ilabel
            else:
                # A named token (NAME, NUMBER, STRING)
                itoken = getattr(token, label, None)
                assert isinstance(itoken, int), label
                assert itoken in token.tok_name, label
                ikiwa itoken in c.tokens:
                    rudisha c.tokens[itoken]
                else:
                    c.labels.append((itoken, None))
                    c.tokens[itoken] = ilabel
                    rudisha ilabel
        else:
            # Either a keyword or an operator
            assert label[0] in ('"', "'"), label
            value = eval(label)
            ikiwa value[0].isalpha():
                # A keyword
                ikiwa value in c.keywords:
                    rudisha c.keywords[value]
                else:
                    c.labels.append((token.NAME, value))
                    c.keywords[value] = ilabel
                    rudisha ilabel
            else:
                # An operator (any non-numeric token)
                itoken = grammar.opmap[value] # Fails ikiwa unknown token
                ikiwa itoken in c.tokens:
                    rudisha c.tokens[itoken]
                else:
                    c.labels.append((itoken, None))
                    c.tokens[itoken] = ilabel
                    rudisha ilabel

    eleza addfirstsets(self):
        names = list(self.dfas.keys())
        names.sort()
        for name in names:
            ikiwa name not in self.first:
                self.calcfirst(name)
            #print name, self.first[name].keys()

    eleza calcfirst(self, name):
        dfa = self.dfas[name]
        self.first[name] = None # dummy to detect left recursion
        state = dfa[0]
        totalset = {}
        overlapcheck = {}
        for label, next in state.arcs.items():
            ikiwa label in self.dfas:
                ikiwa label in self.first:
                    fset = self.first[label]
                    ikiwa fset is None:
                        raise ValueError("recursion for rule %r" % name)
                else:
                    self.calcfirst(label)
                    fset = self.first[label]
                totalset.update(fset)
                overlapcheck[label] = fset
            else:
                totalset[label] = 1
                overlapcheck[label] = {label: 1}
        inverse = {}
        for label, itsfirst in overlapcheck.items():
            for symbol in itsfirst:
                ikiwa symbol in inverse:
                    raise ValueError("rule %s is ambiguous; %s is in the"
                                     " first sets of %s as well as %s" %
                                     (name, symbol, label, inverse[symbol]))
                inverse[symbol] = label
        self.first[name] = totalset

    eleza parse(self):
        dfas = {}
        startsymbol = None
        # MSTART: (NEWLINE | RULE)* ENDMARKER
        while self.type != token.ENDMARKER:
            while self.type == token.NEWLINE:
                self.gettoken()
            # RULE: NAME ':' RHS NEWLINE
            name = self.expect(token.NAME)
            self.expect(token.OP, ":")
            a, z = self.parse_rhs()
            self.expect(token.NEWLINE)
            #self.dump_nfa(name, a, z)
            dfa = self.make_dfa(a, z)
            #self.dump_dfa(name, dfa)
            oldlen = len(dfa)
            self.simplify_dfa(dfa)
            newlen = len(dfa)
            dfas[name] = dfa
            #print name, oldlen, newlen
            ikiwa startsymbol is None:
                startsymbol = name
        rudisha dfas, startsymbol

    eleza make_dfa(self, start, finish):
        # To turn an NFA into a DFA, we define the states of the DFA
        # to correspond to *sets* of states of the NFA.  Then do some
        # state reduction.  Let's represent sets as dicts with 1 for
        # values.
        assert isinstance(start, NFAState)
        assert isinstance(finish, NFAState)
        eleza closure(state):
            base = {}
            addclosure(state, base)
            rudisha base
        eleza addclosure(state, base):
            assert isinstance(state, NFAState)
            ikiwa state in base:
                return
            base[state] = 1
            for label, next in state.arcs:
                ikiwa label is None:
                    addclosure(next, base)
        states = [DFAState(closure(start), finish)]
        for state in states: # NB states grows while we're iterating
            arcs = {}
            for nfastate in state.nfaset:
                for label, next in nfastate.arcs:
                    ikiwa label is not None:
                        addclosure(next, arcs.setdefault(label, {}))
            for label, nfaset in sorted(arcs.items()):
                for st in states:
                    ikiwa st.nfaset == nfaset:
                        break
                else:
                    st = DFAState(nfaset, finish)
                    states.append(st)
                state.addarc(st, label)
        rudisha states # List of DFAState instances; first one is start

    eleza dump_nfa(self, name, start, finish):
        andika("Dump of NFA for", name)
        todo = [start]
        for i, state in enumerate(todo):
            andika("  State", i, state is finish and "(final)" or "")
            for label, next in state.arcs:
                ikiwa next in todo:
                    j = todo.index(next)
                else:
                    j = len(todo)
                    todo.append(next)
                ikiwa label is None:
                    andika("    -> %d" % j)
                else:
                    andika("    %s -> %d" % (label, j))

    eleza dump_dfa(self, name, dfa):
        andika("Dump of DFA for", name)
        for i, state in enumerate(dfa):
            andika("  State", i, state.isfinal and "(final)" or "")
            for label, next in sorted(state.arcs.items()):
                andika("    %s -> %d" % (label, dfa.index(next)))

    eleza simplify_dfa(self, dfa):
        # This is not theoretically optimal, but works well enough.
        # Algorithm: repeatedly look for two states that have the same
        # set of arcs (same labels pointing to the same nodes) and
        # unify them, until things stop changing.

        # dfa is a list of DFAState instances
        changes = True
        while changes:
            changes = False
            for i, state_i in enumerate(dfa):
                for j in range(i+1, len(dfa)):
                    state_j = dfa[j]
                    ikiwa state_i == state_j:
                        #print "  unify", i, j
                        del dfa[j]
                        for state in dfa:
                            state.unifystate(state_j, state_i)
                        changes = True
                        break

    eleza parse_rhs(self):
        # RHS: ALT ('|' ALT)*
        a, z = self.parse_alt()
        ikiwa self.value != "|":
            rudisha a, z
        else:
            aa = NFAState()
            zz = NFAState()
            aa.addarc(a)
            z.addarc(zz)
            while self.value == "|":
                self.gettoken()
                a, z = self.parse_alt()
                aa.addarc(a)
                z.addarc(zz)
            rudisha aa, zz

    eleza parse_alt(self):
        # ALT: ITEM+
        a, b = self.parse_item()
        while (self.value in ("(", "[") or
               self.type in (token.NAME, token.STRING)):
            c, d = self.parse_item()
            b.addarc(c)
            b = d
        rudisha a, b

    eleza parse_item(self):
        # ITEM: '[' RHS ']' | ATOM ['+' | '*']
        ikiwa self.value == "[":
            self.gettoken()
            a, z = self.parse_rhs()
            self.expect(token.OP, "]")
            a.addarc(z)
            rudisha a, z
        else:
            a, z = self.parse_atom()
            value = self.value
            ikiwa value not in ("+", "*"):
                rudisha a, z
            self.gettoken()
            z.addarc(a)
            ikiwa value == "+":
                rudisha a, z
            else:
                rudisha a, a

    eleza parse_atom(self):
        # ATOM: '(' RHS ')' | NAME | STRING
        ikiwa self.value == "(":
            self.gettoken()
            a, z = self.parse_rhs()
            self.expect(token.OP, ")")
            rudisha a, z
        elikiwa self.type in (token.NAME, token.STRING):
            a = NFAState()
            z = NFAState()
            a.addarc(z, self.value)
            self.gettoken()
            rudisha a, z
        else:
            self.raise_error("expected (...) or NAME or STRING, got %s/%s",
                             self.type, self.value)

    eleza expect(self, type, value=None):
        ikiwa self.type != type or (value is not None and self.value != value):
            self.raise_error("expected %s/%s, got %s/%s",
                             type, value, self.type, self.value)
        value = self.value
        self.gettoken()
        rudisha value

    eleza gettoken(self):
        tup = next(self.generator)
        while tup[0] in (tokenize.COMMENT, tokenize.NL):
            tup = next(self.generator)
        self.type, self.value, self.begin, self.end, self.line = tup
        #print token.tok_name[self.type], repr(self.value)

    eleza raise_error(self, msg, *args):
        ikiwa args:
            try:
                msg = msg % args
            except:
                msg = " ".join([msg] + list(map(str, args)))
        raise SyntaxError(msg, (self.filename, self.end[0],
                                self.end[1], self.line))

kundi NFAState(object):

    eleza __init__(self):
        self.arcs = [] # list of (label, NFAState) pairs

    eleza addarc(self, next, label=None):
        assert label is None or isinstance(label, str)
        assert isinstance(next, NFAState)
        self.arcs.append((label, next))

kundi DFAState(object):

    eleza __init__(self, nfaset, final):
        assert isinstance(nfaset, dict)
        assert isinstance(next(iter(nfaset)), NFAState)
        assert isinstance(final, NFAState)
        self.nfaset = nfaset
        self.isfinal = final in nfaset
        self.arcs = {} # map kutoka label to DFAState

    eleza addarc(self, next, label):
        assert isinstance(label, str)
        assert label not in self.arcs
        assert isinstance(next, DFAState)
        self.arcs[label] = next

    eleza unifystate(self, old, new):
        for label, next in self.arcs.items():
            ikiwa next is old:
                self.arcs[label] = new

    eleza __eq__(self, other):
        # Equality test -- ignore the nfaset instance variable
        assert isinstance(other, DFAState)
        ikiwa self.isfinal != other.isfinal:
            rudisha False
        # Can't just rudisha self.arcs == other.arcs, because that
        # would invoke this method recursively, with cycles...
        ikiwa len(self.arcs) != len(other.arcs):
            rudisha False
        for label, next in self.arcs.items():
            ikiwa next is not other.arcs.get(label):
                rudisha False
        rudisha True

    __hash__ = None # For Py3 compatibility.

eleza generate_grammar(filename="Grammar.txt"):
    p = ParserGenerator(filename)
    rudisha p.make_grammar()
