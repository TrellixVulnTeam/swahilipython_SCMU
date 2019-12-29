"""Fix "kila x kwenye f.xreadlines()" -> "kila x kwenye f".

This fixer will also convert g(f.xreadlines) into g(f.__iter__)."""
# Author: Collin Winter

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name


kundi FixXreadlines(fixer_base.BaseFix):
    BM_compatible = Kweli
    PATTERN = """
    power< call=any+ trailer< '.' 'xreadlines' > trailer< '(' ')' > >
    |
    power< any+ trailer< '.' no_call='xreadlines' > >
    """

    eleza transform(self, node, results):
        no_call = results.get("no_call")

        ikiwa no_call:
            no_call.replace(Name("__iter__", prefix=no_call.prefix))
        isipokua:
            node.replace([x.clone() kila x kwenye results["call"]])
