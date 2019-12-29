"""
Optional fixer to transform set() calls to set literals.
"""

# Author: Benjamin Peterson

kutoka lib2to3 agiza fixer_base, pytree
kutoka lib2to3.fixer_util agiza token, syms



kundi FixSetLiteral(fixer_base.BaseFix):

    BM_compatible = Kweli
    explicit = Kweli

    PATTERN = """power< 'set' trailer< '('
                     (atom=atom< '[' (items=listmaker< any ((',' any)* [',']) >
                                |
                                single=any) ']' >
                     |
                     atom< '(' items=testlist_gexp< any ((',' any)* [',']) > ')' >
                     )
                     ')' > >
              """

    eleza transform(self, node, results):
        single = results.get("single")
        ikiwa single:
            # Make a fake listmaker
            fake = pytree.Node(syms.listmaker, [single.clone()])
            single.replace(fake)
            items = fake
        isipokua:
            items = results["items"]

        # Build the contents of the literal
        literal = [pytree.Leaf(token.LBRACE, "{")]
        literal.extend(n.clone() kila n kwenye items.children)
        literal.append(pytree.Leaf(token.RBRACE, "}"))
        # Set the prefix of the right brace to that of the ')' ama ']'
        literal[-1].prefix = items.next_sibling.prefix
        maker = pytree.Node(syms.dictsetmaker, literal)
        maker.prefix = node.prefix

        # If the original was a one tuple, we need to remove the extra comma.
        ikiwa len(maker.children) == 4:
            n = maker.children[2]
            n.remove()
            maker.children[-1].prefix = n.prefix

        # Finally, replace the set call ukijumuisha our shiny new literal.
        rudisha maker
