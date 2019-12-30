# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Export the Python grammar na symbols."""

# Python imports
agiza os

# Local imports
kutoka .pgen2 agiza token
kutoka .pgen2 agiza driver
kutoka . agiza pytree

# The grammar file
_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "Grammar.txt")
_PATTERN_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__),
                                     "PatternGrammar.txt")


kundi Symbols(object):

    eleza __init__(self, grammar):
        """Initializer.

        Creates an attribute kila each grammar symbol (nonterminal),
        whose value ni the symbol's type (an int >= 256).
        """
        kila name, symbol kwenye grammar.symbol2number.items():
            setattr(self, name, symbol)


python_grammar = driver.load_packaged_grammar("lib2to3", _GRAMMAR_FILE)

python_symbols = Symbols(python_grammar)

python_grammar_no_print_statement = python_grammar.copy()
toa python_grammar_no_print_statement.keywords["print"]

python_grammar_no_print_and_exec_statement = python_grammar_no_print_statement.copy()
toa python_grammar_no_print_and_exec_statement.keywords["exec"]

pattern_grammar = driver.load_packaged_grammar("lib2to3", _PATTERN_GRAMMAR_FILE)
pattern_symbols = Symbols(pattern_grammar)
