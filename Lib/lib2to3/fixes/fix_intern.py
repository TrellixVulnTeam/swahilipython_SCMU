# Copyright 2006 Georg Brandl.
# Licensed to PSF under a Contributor Agreement.

"""Fixer kila intern().

intern(s) -> sys.intern(s)"""

# Local imports
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza ImportAndCall, touch_import


kundi FixIntern(fixer_base.BaseFix):
    BM_compatible = Kweli
    order = "pre"

    PATTERN = """
    power< 'intern'
           trailer< lpar='('
                    ( not(arglist | argument<any '=' any>) obj=any
                      | obj=arglist<(sio argument<any '=' any>) any ','> )
                    rpar=')' >
           after=any*
    >
    """

    eleza transform(self, node, results):
        ikiwa results:
            # I feel like we should be able to express this logic kwenye the
            # PATTERN above but I don't know how to do it so...
            obj = results['obj']
            ikiwa obj:
                ikiwa obj.type == self.syms.star_expr:
                    rudisha  # Make no change.
                ikiwa (obj.type == self.syms.argument na
                    obj.children[0].value == '**'):
                    rudisha  # Make no change.
        names = ('sys', 'intern')
        new = ImportAndCall(node, results, names)
        touch_import(Tupu, 'sys', node)
        rudisha new
