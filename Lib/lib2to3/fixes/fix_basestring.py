"""Fixer for basestring -> str."""
# Author: Christian Heimes

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name

kundi FixBasestring(fixer_base.BaseFix):
    BM_compatible = True

    PATTERN = "'basestring'"

    eleza transform(self, node, results):
        rudisha Name("str", prefix=node.prefix)
