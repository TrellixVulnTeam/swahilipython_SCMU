# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that turns 'long' into 'int' everywhere.
"""

# Local agizas
kutoka lib2to3 agiza fixer_base
kutoka lib2to3.fixer_util agiza is_probably_builtin


kundi FixLong(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = "'long'"

    eleza transform(self, node, results):
        ikiwa is_probably_builtin(node):
            node.value = "int"
            node.changed()
