"""Fixer kila basestring -> str."""
# Author: Christian Heimes

# Local imports
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name

kundi FixBasestring(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = "'basestring'"

    eleza transform(self, node, results):
        rudisha Name("str", prefix=node.prefix)
