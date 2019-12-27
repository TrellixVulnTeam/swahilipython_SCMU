"""Remove __future__ agizas

kutoka __future__ agiza foo is replaced with an empty line.
"""
# Author: Christian Heimes

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza BlankLine

class FixFuture(fixer_base.BaseFix):
    BM_compatible = True

    PATTERN = """import_from< 'from' module_name="__future__" 'agiza' any >"""

    # This should be run last -- some things check for the agiza
    run_order = 10

    def transform(self, node, results):
        new = BlankLine()
        new.prefix = node.prefix
        return new
