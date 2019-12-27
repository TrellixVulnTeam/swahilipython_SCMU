# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that changes map(F, ...) into list(map(F, ...)) unless there
exists a 'kutoka future_builtins agiza map' statement in the top-level
namespace.

As a special case, map(None, X) is changed into list(X).  (This is
necessary because the semantics are changed in this case -- the new
map(None, X) is equivalent to [(x,) for x in X].)

We avoid the transformation (except for the special case mentioned
above) ikiwa the map() call is directly contained in iter(<>), list(<>),
tuple(<>), sorted(<>), ...join(<>), or for V in <>:.

NOTE: This is still not correct ikiwa the original code was depending on
map(F, X, Y, ...) to go on until the longest argument is exhausted,
substituting None for missing values -- like zip(), it now stops as
soon as the shortest argument is exhausted.
"""

# Local agizas
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, ArgList, Call, ListComp, in_special_context
kutoka ..pygram agiza python_symbols as syms
kutoka ..pytree agiza Node


kundi FixMap(fixer_base.ConditionalFix):
    BM_compatible = True

    PATTERN = """
    map_none=power<
        'map'
        trailer< '(' arglist< 'None' ',' arg=any [','] > ')' >
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
            return

        trailers = []
        ikiwa 'extra_trailers' in results:
            for t in results['extra_trailers']:
                trailers.append(t.clone())

        ikiwa node.parent.type == syms.simple_stmt:
            self.warning(node, "You should use a for loop here")
            new = node.clone()
            new.prefix = ""
            new = Call(Name("list"), [new])
        elikiwa "map_lambda" in results:
            new = ListComp(results["xp"].clone(),
                           results["fp"].clone(),
                           results["it"].clone())
            new = Node(syms.power, [new] + trailers, prefix="")

        else:
            ikiwa "map_none" in results:
                new = results["arg"].clone()
                new.prefix = ""
            else:
                ikiwa "args" in results:
                    args = results["args"]
                    ikiwa args.type == syms.trailer and \
                       args.children[1].type == syms.arglist and \
                       args.children[1].children[0].type == token.NAME and \
                       args.children[1].children[0].value == "None":
                        self.warning(node, "cannot convert map(None, ...) "
                                     "with multiple arguments because map() "
                                     "now truncates to the shortest sequence")
                        return

                    new = Node(syms.power, [Name("map"), args.clone()])
                    new.prefix = ""

                ikiwa in_special_context(node):
                    rudisha None

            new = Node(syms.power, [Name("list"), ArgList([new])] + trailers)
            new.prefix = ""

        new.prefix = node.prefix
        rudisha new
