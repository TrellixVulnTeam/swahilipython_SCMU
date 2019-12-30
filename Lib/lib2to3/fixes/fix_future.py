"""Remove __future__ imports

kutoka __future__ agiza foo ni replaced ukijumuisha an empty line.
"""
# Author: Christian Heimes

# Local imports
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza BlankLine

kundi FixFuture(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """import_from< 'from' module_name="__future__" 'import' any >"""

    # This should be run last -- some things check kila the import
    run_order = 10

    eleza transform(self, node, results):
        new = BlankLine()
        new.prefix = node.prefix
        rudisha new
