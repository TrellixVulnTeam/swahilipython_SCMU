# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that changes filter(F, X) into list(filter(F, X)).

We avoid the transformation ikiwa the filter() call ni directly contained
in iter(<>), list(<>), tuple(<>), sorted(<>), ...join(<>), or
kila V kwenye <>:.

NOTE: This ni still sio correct ikiwa the original code was depending on
filter(F, X) to rudisha a string ikiwa X ni a string na a tuple ikiwa X ni a
tuple.  That would require type inference, which we don't do.  Let
Python 2.6 figure it out.
"""

# Local imports
kutoka .. agiza fixer_base
kutoka ..pytree agiza Node
kutoka ..pygram agiza python_symbols as syms
kutoka ..fixer_util agiza Name, ArgList, ListComp, in_special_context


kundi FixFilter(fixer_base.ConditionalFix):
    BM_compatible = Kweli

    PATTERN = """
    filter_lambda=power<
        'filter'
        trailer<
            '('
            arglist<
                lambdef< 'lambda'
                         (fp=NAME | vfpdef< '(' fp=NAME ')'> ) ':' xp=any
                >
                ','
                it=any
            >
            ')'
        >
        [extra_trailers=trailer*]
    >
    |
    power<
        'filter'
        trailer< '(' arglist< none='Tupu' ',' seq=any > ')' >
        [extra_trailers=trailer*]
    >
    |
    power<
        'filter'
        args=trailer< '(' [any] ')' >
        [extra_trailers=trailer*]
    >
    """

    skip_on = "future_builtins.filter"

    eleza transform(self, node, results):
        ikiwa self.should_skip(node):
            return

        trailers = []
        ikiwa 'extra_trailers' kwenye results:
            kila t kwenye results['extra_trailers']:
                trailers.append(t.clone())

        ikiwa "filter_lambda" kwenye results:
            new = ListComp(results.get("fp").clone(),
                           results.get("fp").clone(),
                           results.get("it").clone(),
                           results.get("xp").clone())
            new = Node(syms.power, [new] + trailers, prefix="")

        elikiwa "none" kwenye results:
            new = ListComp(Name("_f"),
                           Name("_f"),
                           results["seq"].clone(),
                           Name("_f"))
            new = Node(syms.power, [new] + trailers, prefix="")

        isipokua:
            ikiwa in_special_context(node):
                rudisha Tupu

            args = results['args'].clone()
            new = Node(syms.power, [Name("filter"), args], prefix="")
            new = Node(syms.power, [Name("list"), ArgList([new])] + trailers)
            new.prefix = ""
        new.prefix = node.prefix
        rudisha new
