# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""This module defines the data structures used to represent a grammar.

These are a bit arcane because they are derived kutoka the data
structures used by Python's 'pgen' parser generator.

There's also a table here mapping operators to their names kwenye the
token module; the Python tokenize module reports all operators as the
fallback token code OP, but the parser needs the actual token code.

"""

# Python imports
agiza pickle

# Local imports
kutoka . agiza token


kundi Grammar(object):
    """Pgen parsing tables conversion class.

    Once initialized, this kundi supplies the grammar tables kila the
    parsing engine implemented by parse.py.  The parsing engine
    accesses the instance variables directly.  The kundi here does not
    provide initialization of the tables; several subclasses exist to
    do this (see the conv na pgen modules).

    The load() method reads the tables kutoka a pickle file, which is
    much faster than the other ways offered by subclasses.  The pickle
    file ni written by calling dump() (after loading the grammar
    tables using a subclass).  The report() method prints a readable
    representation of the tables to stdout, kila debugging.

    The instance variables are as follows:

    symbol2number -- a dict mapping symbol names to numbers.  Symbol
                     numbers are always 256 ama higher, to distinguish
                     them kutoka token numbers, which are between 0 and
                     255 (inclusive).

    number2symbol -- a dict mapping numbers to symbol names;
                     these two are each other's inverse.

    states        -- a list of DFAs, where each DFA ni a list of
                     states, each state ni a list of arcs, na each
                     arc ni a (i, j) pair where i ni a label na j is
                     a state number.  The DFA number ni the index into
                     this list.  (This name ni slightly confusing.)
                     Final states are represented by a special arc of
                     the form (0, j) where j ni its own state number.

    dfas          -- a dict mapping symbol numbers to (DFA, first)
                     pairs, where DFA ni an item kutoka the states list
                     above, na first ni a set of tokens that can
                     begin this grammar rule (represented by a dict
                     whose values are always 1).

    labels        -- a list of (x, y) pairs where x ni either a token
                     number ama a symbol number, na y ni either Tupu
                     ama a string; the strings are keywords.  The label
                     number ni the index kwenye this list; label numbers
                     are used to mark state transitions (arcs) kwenye the
                     DFAs.

    start         -- the number of the grammar's start symbol.

    keywords      -- a dict mapping keyword strings to arc labels.

    tokens        -- a dict mapping token numbers to arc labels.

    """

    eleza __init__(self):
        self.symbol2number = {}
        self.number2symbol = {}
        self.states = []
        self.dfas = {}
        self.labels = [(0, "EMPTY")]
        self.keywords = {}
        self.tokens = {}
        self.symbol2label = {}
        self.start = 256

    eleza dump(self, filename):
        """Dump the grammar tables to a pickle file."""
        ukijumuisha open(filename, "wb") as f:
            pickle.dump(self.__dict__, f, pickle.HIGHEST_PROTOCOL)

    eleza load(self, filename):
        """Load the grammar tables kutoka a pickle file."""
        ukijumuisha open(filename, "rb") as f:
            d = pickle.load(f)
        self.__dict__.update(d)

    eleza loads(self, pkl):
        """Load the grammar tables kutoka a pickle bytes object."""
        self.__dict__.update(pickle.loads(pkl))

    eleza copy(self):
        """
        Copy the grammar.
        """
        new = self.__class__()
        kila dict_attr kwenye ("symbol2number", "number2symbol", "dfas", "keywords",
                          "tokens", "symbol2label"):
            setattr(new, dict_attr, getattr(self, dict_attr).copy())
        new.labels = self.labels[:]
        new.states = self.states[:]
        new.start = self.start
        rudisha new

    eleza report(self):
        """Dump the grammar tables to standard output, kila debugging."""
        kutoka pprint agiza pprint
        andika("s2n")
        pandika(self.symbol2number)
        andika("n2s")
        pandika(self.number2symbol)
        andika("states")
        pandika(self.states)
        andika("dfas")
        pandika(self.dfas)
        andika("labels")
        pandika(self.labels)
        andika("start", self.start)


# Map kutoka operator to number (since tokenize doesn't do this)

opmap_raw = """
( LPAR
) RPAR
[ LSQB
] RSQB
: COLON
, COMMA
; SEMI
+ PLUS
- MINUS
* STAR
/ SLASH
| VBAR
& AMPER
< LESS
> GREATER
= EQUAL
. DOT
% PERCENT
` BACKQUOTE
{ LBRACE
} RBRACE
@ AT
@= ATEQUAL
== EQEQUAL
!= NOTEQUAL
<> NOTEQUAL
<= LESSEQUAL
>= GREATEREQUAL
~ TILDE
^ CIRCUMFLEX
<< LEFTSHIFT
>> RIGHTSHIFT
** DOUBLESTAR
+= PLUSEQUAL
-= MINEQUAL
*= STAREQUAL
/= SLASHEQUAL
%= PERCENTEQUAL
&= AMPEREQUAL
|= VBAREQUAL
^= CIRCUMFLEXEQUAL
<<= LEFTSHIFTEQUAL
>>= RIGHTSHIFTEQUAL
**= DOUBLESTAREQUAL
// DOUBLESLASH
//= DOUBLESLASHEQUAL
-> RARROW
"""

opmap = {}
kila line kwenye opmap_raw.splitlines():
    ikiwa line:
        op, name = line.split()
        opmap[op] = getattr(token, name)
