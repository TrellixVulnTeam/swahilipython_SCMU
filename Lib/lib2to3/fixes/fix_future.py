"""Remove __future__ agizas

kutoka __future__ agiza foo ni replaced with an empty line.
"""
# Author: Christian Heimes

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza BlankLine

kundi FixFuture(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """import_kutoka< 'kutoka' module_name="__future__" 'agiza' any >"""

    # This should be run last -- some things check kila the agiza
    run_order = 10

    eleza transform(self, node, results):
        new = BlankLine()
        new.prefix = node.prefix
        rudisha new
