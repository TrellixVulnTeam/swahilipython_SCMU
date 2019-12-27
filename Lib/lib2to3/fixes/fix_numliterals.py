"""Fixer that turns 1L into 1, 0755 into 0o755.
"""
# Copyright 2007 Georg Brandl.
# Licensed to PSF under a Contributor Agreement.

# Local agizas
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Number


kundi FixNumliterals(fixer_base.BaseFix):
    # This is so simple that we don't need the pattern compiler.

    _accept_type = token.NUMBER

    eleza match(self, node):
        # Override
        rudisha (node.value.startswith("0") or node.value[-1] in "Ll")

    eleza transform(self, node, results):
        val = node.value
        ikiwa val[-1] in 'Ll':
            val = val[:-1]
        elikiwa val.startswith('0') and val.isdigit() and len(set(val)) > 1:
            val = "0o" + val[1:]

        rudisha Number(val, prefix=node.prefix)
