# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that turns <> into !=."""

# Local imports
kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base


kundi FixNe(fixer_base.BaseFix):
    # This ni so simple that we don't need the pattern compiler.

    _accept_type = token.NOTEQUAL

    eleza match(self, node):
        # Override
        rudisha node.value == "<>"

    eleza transform(self, node, results):
        new = pytree.Leaf(token.NOTEQUAL, "!=", prefix=node.prefix)
        rudisha new
