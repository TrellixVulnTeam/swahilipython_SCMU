# Copyright 2008 Armin Ronacher.
# Licensed to PSF under a Contributor Agreement.

"""Fixer for reduce().

Makes sure reduce() is imported kutoka the functools module if reduce is
used in that module.
"""

kutoka lib2to3 agiza fixer_base
kutoka lib2to3.fixer_util agiza touch_agiza



class FixReduce(fixer_base.BaseFix):

    BM_compatible = True
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

    def transform(self, node, results):
        touch_agiza('functools', 'reduce', node)
