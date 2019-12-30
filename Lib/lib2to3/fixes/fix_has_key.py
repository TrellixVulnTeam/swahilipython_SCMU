# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer kila has_key().

Calls to .has_key() methods are expressed kwenye terms of the 'in'
operator:

    d.has_key(k) -> k kwenye d

CAVEATS:
1) While the primary target of this fixer ni dict.has_key(), the
   fixer will change any has_key() method call, regardless of its
   class.

2) Cases like this will sio be converted:

    m = d.has_key
    ikiwa m(k):
        ...

   Only *calls* to has_key() are converted. While it ni possible to
   convert the above to something like

    m = d.__contains__
    ikiwa m(k):
        ...

   this ni currently sio done.
"""

# Local imports
kutoka .. agiza pytree
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, parenthesize


kundi FixHasKey(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """
    anchor=power<
        before=any+
        trailer< '.' 'has_key' >
        trailer<
            '('
            ( not(arglist | argument<any '=' any>) arg=any
            | arglist<(not argument<any '=' any>) arg=any ','>
            )
            ')'
        >
        after=any*
    >
    |
    negation=not_test<
        'not'
        anchor=power<
            before=any+
            trailer< '.' 'has_key' >
            trailer<
                '('
                ( not(arglist | argument<any '=' any>) arg=any
                | arglist<(not argument<any '=' any>) arg=any ','>
                )
                ')'
            >
        >
    >
    """

    eleza transform(self, node, results):
        assert results
        syms = self.syms
        ikiwa (node.parent.type == syms.not_test and
            self.pattern.match(node.parent)):
            # Don't transform a node matching the first alternative of the
            # pattern when its parent matches the second alternative
            rudisha Tupu
        negation = results.get("negation")
        anchor = results["anchor"]
        prefix = node.prefix
        before = [n.clone() kila n kwenye results["before"]]
        arg = results["arg"].clone()
        after = results.get("after")
        ikiwa after:
            after = [n.clone() kila n kwenye after]
        ikiwa arg.type kwenye (syms.comparison, syms.not_test, syms.and_test,
                        syms.or_test, syms.test, syms.lambdef, syms.argument):
            arg = parenthesize(arg)
        ikiwa len(before) == 1:
            before = before[0]
        isipokua:
            before = pytree.Node(syms.power, before)
        before.prefix = " "
        n_op = Name("in", prefix=" ")
        ikiwa negation:
            n_not = Name("not", prefix=" ")
            n_op = pytree.Node(syms.comp_op, (n_not, n_op))
        new = pytree.Node(syms.comparison, (arg, n_op, before))
        ikiwa after:
            new = parenthesize(new)
            new = pytree.Node(syms.power, (new,) + tuple(after))
        ikiwa node.parent.type kwenye (syms.comparison, syms.expr, syms.xor_expr,
                                syms.and_expr, syms.shift_expr,
                                syms.arith_expr, syms.term,
                                syms.factor, syms.power):
            new = parenthesize(new)
        new.prefix = prefix
        rudisha new
