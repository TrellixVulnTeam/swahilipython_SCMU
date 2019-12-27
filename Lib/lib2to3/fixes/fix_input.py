"""Fixer that changes input(...) into eval(input(...))."""
# Author: Andre Roberge

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Call, Name
kutoka .. agiza patcomp


context = patcomp.compile_pattern("power< 'eval' trailer< '(' any ')' > >")


kundi FixInput(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = """
              power< 'input' args=trailer< '(' [any] ')' > >
              """

    eleza transform(self, node, results):
        # If we're already wrapped in an eval() call, we're done.
        ikiwa context.match(node.parent.parent):
            return

        new = node.clone()
        new.prefix = ""
        rudisha Call(Name("eval"), [new], prefix=node.prefix)
