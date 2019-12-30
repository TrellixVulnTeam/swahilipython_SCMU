# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that transforms `xyzzy` into repr(xyzzy)."""

# Local imports
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Call, Name, parenthesize


kundi FixRepr(fixer_base.BaseFix):

    BM_compatible = Kweli
    PATTERN = """
              atom < '`' expr=any '`' >
              """

    eleza transform(self, node, results):
        expr = results["expr"].clone()

        ikiwa expr.type == self.syms.testlist1:
            expr = parenthesize(expr)
        rudisha Call(Name("repr"), [expr], prefix=node.prefix)
