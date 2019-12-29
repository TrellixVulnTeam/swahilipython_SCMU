"""Fixer kila __nonzero__ -> __bool__ methods."""
# Author: Collin Winter

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name

kundi FixNonzero(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = """
    classdef< 'class' any+ ':'
              suite< any*
                     funcdef< 'def' name='__nonzero__'
                              parameters< '(' NAME ')' > any+ >
                     any* > >
    """

    eleza transform(self, node, results):
        name = results["name"]
        new = Name("__bool__", prefix=name.prefix)
        name.replace(new)
