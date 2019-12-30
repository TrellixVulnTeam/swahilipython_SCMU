# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer kila apply().

This converts apply(func, v, k) into (func)(*v, **k)."""

# Local imports
kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Call, Comma, parenthesize

kundi FixApply(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """
    power< 'apply'
        trailer<
            '('
            arglist<
                (sio argument<NAME '=' any>) func=any ','
                (sio argument<NAME '=' any>) args=any [','
                (sio argument<NAME '=' any>) kwds=any] [',']
            >
            ')'
        >
    >
    """

    eleza transform(self, node, results):
        syms = self.syms
        assert results
        func = results["func"]
        args = results["args"]
        kwds = results.get("kwds")
        # I feel like we should be able to express this logic kwenye the
        # PATTERN above but I don't know how to do it so...
        ikiwa args:
            ikiwa args.type == self.syms.star_expr:
                rudisha  # Make no change.
            ikiwa (args.type == self.syms.argument na
                args.children[0].value == '**'):
                rudisha  # Make no change.
        ikiwa kwds na (kwds.type == self.syms.argument na
                     kwds.children[0].value == '**'):
            rudisha  # Make no change.
        prefix = node.prefix
        func = func.clone()
        ikiwa (func.type haiko kwenye (token.NAME, syms.atom) na
            (func.type != syms.power ama
             func.children[-2].type == token.DOUBLESTAR)):
            # Need to parenthesize
            func = parenthesize(func)
        func.prefix = ""
        args = args.clone()
        args.prefix = ""
        ikiwa kwds ni sio Tupu:
            kwds = kwds.clone()
            kwds.prefix = ""
        l_newargs = [pytree.Leaf(token.STAR, "*"), args]
        ikiwa kwds ni sio Tupu:
            l_newargs.extend([Comma(),
                              pytree.Leaf(token.DOUBLESTAR, "**"),
                              kwds])
            l_newargs[-2].prefix = " " # that's the ** token
        # XXX Sometimes we could be cleverer, e.g. apply(f, (x, y) + t)
        # can be translated into f(x, y, *t) instead of f(*(x, y) + t)
        #new = pytree.Node(syms.power, (func, ArgList(l_newargs)))
        rudisha Call(func, l_newargs, prefix=prefix)
