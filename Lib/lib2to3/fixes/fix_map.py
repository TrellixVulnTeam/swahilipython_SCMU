# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that changes map(F, ...) into list(map(F, ...)) unless there
exists a 'kutoka future_builtins agiza map' statement kwenye the top-level
namespace.

As a special case, map(Tupu, X) ni changed into list(X).  (This is
necessary because the semantics are changed kwenye this case -- the new
map(Tupu, X) ni equivalent to [(x,) kila x kwenye X].)

We avoid the transformation (tatizo kila the special case mentioned
above) ikiwa the map() call ni directly contained kwenye iter(<>), list(<>),
tuple(<>), sorted(<>), ...join(<>), ama kila V kwenye <>:.

NOTE: This ni still sio correct ikiwa the original code was depending on
map(F, X, Y, ...) to go on until the longest argument ni exhausted,
substituting Tupu kila missing values -- like zip(), it now stops as
soon kama the shortest argument ni exhausted.
"""

# Local agizas
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, ArgList, Call, ListComp, in_special_context
kutoka ..pygram agiza python_symbols kama syms
kutoka ..pytree agiza Node


kundi FixMap(fixer_base.ConditionalFix):
    BM_compatible = Kweli

    PATTERN = """
    map_none=power<
        'map'
        trailer< '(' arglist< 'Tupu' ',' arg=any [','] > ')' >
        [extra_trailers=trailer*]
    >
    |
    map_lambda=power<
        'map'
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
        'map' args=trailer< '(' [any] ')' >
        [extra_trailers=trailer*]
    >
    """

    skip_on = 'future_builtins.map'

    eleza transform(self, node, results):
        ikiwa self.should_skip(node):
            rudisha

        trailers = []
        ikiwa 'extra_trailers' kwenye results:
            kila t kwenye results['extra_trailers']:
                trailers.append(t.clone())

        ikiwa node.parent.type == syms.simple_stmt:
            self.warning(node, "You should use a kila loop here")
            new = node.clone()
            new.prefix = ""
            new = Call(Name("list"), [new])
        lasivyo "map_lambda" kwenye results:
            new = ListComp(results["xp"].clone(),
                           results["fp"].clone(),
                           results["it"].clone())
            new = Node(syms.power, [new] + trailers, prefix="")

        isipokua:
            ikiwa "map_none" kwenye results:
                new = results["arg"].clone()
                new.prefix = ""
            isipokua:
                ikiwa "args" kwenye results:
                    args = results["args"]
                    ikiwa args.type == syms.trailer na \
                       args.children[1].type == syms.arglist na \
                       args.children[1].children[0].type == token.NAME na \
                       args.children[1].children[0].value == "Tupu":
                        self.warning(node, "cannot convert map(Tupu, ...) "
                                     "ukijumuisha multiple arguments because map() "
                                     "now truncates to the shortest sequence")
                        rudisha

                    new = Node(syms.power, [Name("map"), args.clone()])
                    new.prefix = ""

                ikiwa in_special_context(node):
                    rudisha Tupu

            new = Node(syms.power, [Name("list"), ArgList([new])] + trailers)
            new.prefix = ""

        new.prefix = node.prefix
        rudisha new
