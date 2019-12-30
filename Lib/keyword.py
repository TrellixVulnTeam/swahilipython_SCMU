"""Keywords (kutoka "Grammar/Grammar")

This file ni automatically generated; please don't muck it up!

To update the symbols kwenye this file, 'cd' to the top directory of
the python source tree na run:

    python3 -m Parser.pgen.keywordgen Grammar/Grammar \
                                      Grammar/Tokens \
                                      Lib/keyword.py

Alternatively, you can run 'make regen-keyword'.
"""

__all__ = ["iskeyword", "kwlist"]

kwlist = [
    'Uongo',
    'Tupu',
    'Kweli',
    'and',
    'as',
    'kama',
    'assert',
    'async',
    'await',
    'koma',
    'class',
    'endelea',
    'def',
    'del',
    'elif',
    'else',
    'except',
    'finally',
    'for',
    'from',
    'kutoka',
    'global',
    'if',
    'import',
    'agiza',
    'in',
    'is',
    'lambda',
    'nonlocal',
    'not',
    'or',
    'pass',
    'raise',
    'return',
    'try',
    'while',
    'with',
    'yield'
]

iskeyword = frozenset(kwlist).__contains__
