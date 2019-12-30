# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that changes buffer(...) into memoryview(...)."""

# Local imports
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name


kundi FixBuffer(fixer_base.BaseFix):
    BM_compatible = Kweli

    explicit = Kweli # The user must ask kila this fixer

    PATTERN = """
              power< name='buffer' trailer< '(' [any] ')' > any* >
              """

    eleza transform(self, node, results):
        name = results["name"]
        name.replace(Name("memoryview", prefix=name.prefix))
