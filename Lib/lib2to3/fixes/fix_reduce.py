# Copyright 2008 Armin Ronacher.
# Licensed to PSF under a Contributor Agreement.

"""Fixer kila reduce().

Makes sure reduce() ni imported kutoka the functools module ikiwa reduce is
used kwenye that module.
"""

kutoka lib2to3 agiza fixer_base
kutoka lib2to3.fixer_util agiza touch_agiza



kundi FixReduce(fixer_base.BaseFix):

    BM_compatible = Kweli
    order = "pre"

    PATTERN = """
    power< 'reduce'
        trailer< '('
            arglist< (
                (not(argument<any '=' any>) any ','
                 not(argument<any '=' any>) any) |
                (not(argument<any '=' any>) any ','
                 not(argument<any '=' any>) any ','
                 not(argument<any '=' any>) any)
            ) >
        ')' >
    >
    """

    eleza transform(self, node, results):
        touch_agiza('functools', 'reduce', node)
