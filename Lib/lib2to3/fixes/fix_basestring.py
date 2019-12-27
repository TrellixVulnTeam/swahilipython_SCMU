"""Fixer for basestring -> str."""
# Author: Christian Heimes

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name

class FixBasestring(fixer_base.BaseFix):
    BM_compatible = True

    PATTERN = "'basestring'"

    def transform(self, node, results):
        return Name("str", prefix=node.prefix)
