# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer kila StandardError -> Exception."""

# Local imports
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name


kundi FixStandarderror(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = """
              'StandardError'
              """

    eleza transform(self, node, results):
        rudisha Name("Exception", prefix=node.prefix)
