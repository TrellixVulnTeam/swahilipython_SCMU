"""Fixer kila tatizo statements ukijumuisha named exceptions.

The following cases will be converted:

- "tatizo E, T:" where T ni a name:

    tatizo E kama T:

- "tatizo E, T:" where T ni sio a name, tuple ama list:

        tatizo E kama t:
            T = t

    This ni done because the target of an "except" clause must be a
    name.

- "tatizo E, T:" where T ni a tuple ama list literal:

        tatizo E kama t:
            T = t.args
"""
# Author: Collin Winter

# Local agizas
kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Assign, Attr, Name, is_tuple, is_list, syms

eleza find_excepts(nodes):
    kila i, n kwenye enumerate(nodes):
        ikiwa n.type == syms.except_clause:
            ikiwa n.children[0].value == 'except':
                tuma (n, nodes[i+2])

kundi FixExcept(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """
    try_stmt< 'try' ':' (simple_stmt | suite)
                  cleanup=(except_clause ':' (simple_stmt | suite))+
                  tail=(['except' ':' (simple_stmt | suite)]
                        ['else' ':' (simple_stmt | suite)]
                        ['finally' ':' (simple_stmt | suite)]) >
    """

    eleza transform(self, node, results):
        syms = self.syms

        tail = [n.clone() kila n kwenye results["tail"]]

        try_cleanup = [ch.clone() kila ch kwenye results["cleanup"]]
        kila except_clause, e_suite kwenye find_excepts(try_cleanup):
            ikiwa len(except_clause.children) == 4:
                (E, comma, N) = except_clause.children[1:4]
                comma.replace(Name("as", prefix=" "))

                ikiwa N.type != token.NAME:
                    # Generate a new N kila the tatizo clause
                    new_N = Name(self.new_name(), prefix=" ")
                    target = N.clone()
                    target.prefix = ""
                    N.replace(new_N)
                    new_N = new_N.clone()

                    # Insert "old_N = new_N" kama the first statement in
                    #  the tatizo body. This loop skips leading whitespace
                    #  na indents
                    #TODO(cwinter) suite-cleanup
                    suite_stmts = e_suite.children
                    kila i, stmt kwenye enumerate(suite_stmts):
                        ikiwa isinstance(stmt, pytree.Node):
                            koma

                    # The assignment ni different ikiwa old_N ni a tuple ama list
                    # In that case, the assignment ni old_N = new_N.args
                    ikiwa is_tuple(N) ama is_list(N):
                        assign = Assign(target, Attr(new_N, Name('args')))
                    isipokua:
                        assign = Assign(target, new_N)

                    #TODO(cwinter) stopgap until children becomes a smart list
                    kila child kwenye reversed(suite_stmts[:i]):
                        e_suite.insert_child(0, child)
                    e_suite.insert_child(i, assign)
                lasivyo N.prefix == "":
                    # No space after a comma ni legal; no space after "as",
                    # sio so much.
                    N.prefix = " "

        #TODO(cwinter) fix this when children becomes a smart list
        children = [c.clone() kila c kwenye node.children[:3]] + try_cleanup + tail
        rudisha pytree.Node(node.type, children)
