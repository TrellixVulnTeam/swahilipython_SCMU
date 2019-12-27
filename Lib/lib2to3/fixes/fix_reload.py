"""Fixer for reload().

reload(s) -> importlib.reload(s)"""

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza ImportAndCall, touch_agiza


kundi FixReload(fixer_base.BaseFix):
    BM_compatible = True
    order = "pre"

    PATTERN = """
    power< 'reload'
           trailer< lpar='('
                    ( not(arglist | argument<any '=' any>) obj=any
                      | obj=arglist<(not argument<any '=' any>) any ','> )
                    rpar=')' >
           after=any*
    >
    """

    eleza transform(self, node, results):
        ikiwa results:
            # I feel like we should be able to express this logic in the
            # PATTERN above but I don't know how to do it so...
            obj = results['obj']
            ikiwa obj:
                ikiwa obj.type == self.syms.star_expr:
                    rudisha  # Make no change.
                ikiwa (obj.type == self.syms.argument and
                    obj.children[0].value == '**'):
                    rudisha  # Make no change.
        names = ('importlib', 'reload')
        new = ImportAndCall(node, results, names)
        touch_agiza(None, 'importlib', node)
        rudisha new
